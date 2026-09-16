import time
import fc_core
import machine
import rp2
from BNO055 import BNO055

# ==========================================
# 0. 吊り下げテスト用パラメータ設定
# ==========================================
# 浮かび上がらず、かつ姿勢制御の推力が効くスロットル値 (1100〜1300程度)
TEST_THROTTLE = 15.0

# 1軸拘束のため、まずはD項を0にしてPゲインの限界を探る
# Pitchのテスト時は Kp_roll を 0 に、Rollのテスト時は Kp_pitch を 0 にするとより確実です
KP_ROLL = 0.03
KP_PITCH = 0.04 #0.04
KD_ROLL = 0.01  # BNO055差分によるノイズ・スパイク防止のため一旦0
KD_PITCH = 0.02 #0.02  # 0.2 / 同上

MAX_TILT_DEG = 45.0  # 吊り下げ時の非常停止角度

pin_scl = machine.Pin("I2C_SCL")
pin_sda = machine.Pin("I2C_SDA")

isStarted = False
exec_time_us = 0
interval_us = 0
t_last_irq = 0


def dma_rx_irq_handler(dma_obj):
    global isStarted, exec_time_us, interval_us, t_last_irq

    t_now = time.ticks_us()
    if t_last_irq > 0:
        interval_us = time.ticks_diff(t_now, t_last_irq)

    t_start = time.ticks_us()

    if dma_obj.channel == sensor.rx_dma_a.channel:
        raw = sensor.rx_buf_a
    else:
        raw = sensor.rx_buf_b

    fc_core.set_sensor_buffer(raw)
    dma_obj.write = raw
    dma_obj.count = len(raw)

    if isStarted:
        fc_core.process()

    if not sensor.dma_ch.active():
        sensor.dma_ch.read = sensor.tx_cmds
        sensor.dma_ch.count = len(sensor.tx_cmds)
        sensor.dma_ch.active(1)

    exec_time_us = time.ticks_diff(time.ticks_us(), t_start)
    t_last_irq = time.ticks_us()


# ==========================================
# 1. センサーおよびハードウェア初期化
# ==========================================
print("BNO055 初期化中...")
sensor = BNO055(0, pin_scl, pin_sda, address=0x29)
if not sensor.load_calibration_from_file():
    print("Warning: Running with default/raw offsets.")

sensor.configure(dma_rx_irq_handler)
fc_core.set_sensor_buffer(sensor.rx_buf_a)


@rp2.asm_pio(
    sideset_init=rp2.PIO.OUT_LOW,
    out_shiftdir=rp2.PIO.SHIFT_LEFT,
    autopull=False,
)
def dshot300():
    wrap_target()
    # 1. パケット取得（空なら X の値＝前回パケットが OSR に復帰）
    pull(noblock)
    # パケット全体を退避したいが、XとYしかないので ISR を一時退避場所にする
    mov(isr, osr)  # ISR にパケット全体をバックアップ
    set(y, 15)  # 16ビットカウンタ

    label("bit_loop")
    # OSRから1ビット取り出して X に格納 (ピンLOW)
    out(x, 1).side(0)

    # --- 前半: 全ビット共通 HIGH 15サイクル ---
    nop().side(1)[6]  # [7] HIGH
    nop().side(1)[6]  # [7] HIGH (計14サイクル)

    # --- 中盤: x の値（0か1か）で分岐 ---
    jmp(not_x, "bit0_mid").side(1)  # [1] 0ならbit0へ (15サイクル目完了)

    # --- Bit 1 のルート (HIGHを残り15サイクル維持) ---
    nop().side(1)[6]  # [7]
    jmp("tail").side(1)[7]  # [8] (15 + 7 + 8 = 30サイクル HIGH完了)

    # --- Bit 0 のルート (LOWを15サイクル維持) ---
    label("bit0_mid")
    nop().side(0)[6]  # [7]
    nop().side(0)[7]  # [8] (計15サイクル LOW)

    # --- 後半: 全ビット共通 LOW 10サイクル ---
    label("tail")
    nop().side(0)[6]  # [7] LOW維持
    # yをデクリメントして16回判定（OSRの空判定は使わない！）
    jmp(y_dec, "bit_loop").side(0)[
        1
    ]  # [2] LOW維持 (計 1 + 7 + 2 = 10サイクル LOW)

    # --------------------------------------------------
    # 2. 次回のための前回値復元 ＆ インターフレームギャップ
    # --------------------------------------------------
    mov(x, isr).side(0)  # バックアップしておいたパケットを X に戻す！

    # LOWギャップ待機 (約50us)
    set(y, 31)
    label("gap_loop")
    nop()[6]
    jmp(y_dec, "gap_loop")[7]

    wrap()


pin_rr = machine.Pin("ESC_SERVO_RR", machine.Pin.OUT)
pin_fr = machine.Pin("ESC_SERVO_FR", machine.Pin.OUT)
pin_rl = machine.Pin("ESC_SERVO_RL", machine.Pin.OUT)
pin_fl = machine.Pin("ESC_SERVO_FL", machine.Pin.OUT)

freq = 12_000_000  # 12MHz
sm_rr = rp2.StateMachine(0, dshot300, freq=freq, sideset_base=pin_rr)
sm_fr = rp2.StateMachine(1, dshot300, freq=freq, sideset_base=pin_fr)
sm_rl = rp2.StateMachine(2, dshot300, freq=freq, sideset_base=pin_rl)
sm_fl = rp2.StateMachine(3, dshot300, freq=freq, sideset_base=pin_fl)

for sm in (sm_rr, sm_fr, sm_rl, sm_fl):
    sm.put(0)
    sm.active(1)

fc_core.init_hardware(0, 0, 1, 2, 3)

# PIDゲインセット (D=0)
fc_core.set_pid(KP_ROLL, KP_PITCH, KD_ROLL, KD_PITCH)

# 吊り下げて水平がつり合った状態で水平キャリブレーション
print("静止水平状態で水平キャリブレーションを実行します...")
time.sleep(1)
fc_core.calibrate()
print("キャリブレーション完了。")

# ==========================================
# 2. 吊り下げベンチテスト実行ループ
# ==========================================
try:
    print("\n--- 吊り下げテストモード ---")
    print(f"Base Throttle: {TEST_THROTTLE} us")
    print(
        f"PID -> Roll P:{KP_ROLL}, D:{KD_ROLL} | Pitch P:{KP_PITCH}, D:{KD_PITCH}"
    )
    input("Enterキーを押すとモーターが低速回転を開始します...")

    fc_core.set_throttle(TEST_THROTTLE)
    fc_core.set_armed(True)
    isStarted = True
    sensor.activate()

    print("動作中... (Ctrl+C で即座にディスアーム/停止)")

    while True:
        roll, pitch = fc_core.get_angles()

        # 安全装置: 糸が外れたり暴走して傾きすぎた場合は即停止
        if abs(roll) > MAX_TILT_DEG or abs(pitch) > MAX_TILT_DEG:
            raise RuntimeError(
                f"角度制限超過 (Roll: {roll:.1f}°, Pitch: {pitch:.1f}°)"
            )

        freq_hz = (1_000_000 / interval_us) if interval_us > 0 else 0
        print(
            f"Roll: {roll:6.1f}° | Pitch: {pitch:6.1f}° | Loop: {freq_hz:4.0f}Hz",
            end="\r",
        )

        time.sleep_ms(5)

except KeyboardInterrupt:
    print("\n[ユーザー停止] 安全にディスアームしました。")

except Exception as e:
    print(f"\n[エラー停止] {e}")

finally:
    # 確実なモーター全停止
    isStarted = False
    fc_core.set_throttle(0.0)
    fc_core.set_armed(False)
    for sm in (sm_rr, sm_fr, sm_rl, sm_fl):
        sm.put(0)
    print("全モーター出力を 1000us (OFF) に設定しました。")
    machine.reset()