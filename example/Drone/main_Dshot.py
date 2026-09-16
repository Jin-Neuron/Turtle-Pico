import machine
import rp2
import time
import fc_core
from BNO055 import BNO055

pin_scl = machine.Pin("I2C_SCL")
pin_sda = machine.Pin("I2C_SDA")

KP_ROLL = 0.04
KP_PITCH = 0.04 #0.04
KD_ROLL = 0.01  # BNO055差分によるノイズ・スパイク防止のため一旦0
KD_PITCH = 0.02 #0.02  # 0.2 / 同上

isStarted = False
exec_time_us = 0
interval_us = 0
t_last_irq = 0

MAX_PITCH = 180
MAX_ROLL = 90

def dma_rx_irq_handler(dma_obj):
    global isStarted, exec_time_us, interval_us, t_last_irq
    global pitch, roll, sensor

    t_now = time.ticks_us()
    
    if t_last_irq > 0:
        interval_us = time.ticks_diff(t_now, t_last_irq)

    t_start = time.ticks_us()

    # 完了したチャンネルに応じてバッファを取得 & 次回周回用に再装填
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

    '''# 6バイトの受信完了！(CPUを介さずに rx_buf に直接入っている)
    heading, roll, pitch = struct.unpack("<hhh", raw)
    heading /= 16.0
    pitch /= 16.0
    roll /= 16.0

    print(f"heading: {heading:6.2f} | roll: {roll:6.2f} | pitch: {pitch:6.2f}", end="\r")'''



print("BNO055をIMUモード(6軸)で初期化しています...")

sensor = BNO055(0, pin_scl, pin_sda, address=0x29)

# ファイルが存在すれば読み込み、無ければスキップ
if not sensor.load_calibration_from_file():
    print("Warning: Running with default/raw offsets.")

sensor.configure(dma_rx_irq_handler)

fc_core.set_sensor_buffer(sensor.rx_buf_a)

print("rp2.DMA + pack_ctrl Ring Buffer Autonomous Stream Started.")

# ==========================================
# 1. モーター用PIOステートマシンの定義と起動
# ==========================================
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
    
# モーター出力用ピンの割り当て（ご自身の配線に合わせて変更してください）
pin_rr = machine.Pin("ESC_SERVO_RR", machine.Pin.OUT)
pin_fr = machine.Pin("ESC_SERVO_FR", machine.Pin.OUT)
pin_rl = machine.Pin("ESC_SERVO_RL", machine.Pin.OUT)
pin_fl = machine.Pin("ESC_SERVO_FL", machine.Pin.OUT)

freq = 12_000_000  # PIOクロック
sm_rr = rp2.StateMachine(0, dshot300, freq=freq, sideset_base=pin_rr)
sm_fr = rp2.StateMachine(1, dshot300, freq=freq, sideset_base=pin_fr)
sm_rl = rp2.StateMachine(2, dshot300, freq=freq, sideset_base=pin_rl)
sm_fl = rp2.StateMachine(3, dshot300, freq=freq, sideset_base=pin_fl)

# 各ステートマシンの初期化と起動（最大PWM周期：2000us）
for sm in (sm_rr, sm_fr, sm_rl, sm_fl):
    sm.put(0)
    sm.active(1)

print("Motor PIO State Machines Initialized.")

# 引数: PIOインスタンス(1), SM_RR(0), SM_FR(1), SM_RL(2), SM_FL(3)
fc_core.init_hardware(0, 0, 1, 2, 3)

# PIDパラメータと dt（割り込み周期）のセット
# 例: Kp_roll=0.5, Kp_pitch=0.5, Kd_roll=0.2, Kd_pitch=0.2, dt=0.001 (1000Hz)
#fc_core.set_pid(0.8, 0.3, 0.25, 0.18)
fc_core.set_pid(KP_ROLL, KP_PITCH, KD_ROLL, KD_PITCH)


# 現在の姿勢をキャリブレーション
fc_core.calibrate()
print("Zero point calibrated.")

MAX_TILT_DEG = 45.0

print("FC Core & Hardware Initialized. System ready.")

base_throttle_start = 37.0
base_throttle_mid = 41.0
base_throttle_max = 44.0

RAMP_UP_DURATION = 0.5  # 離陸時のランプアップ時間（秒）
HOVER_DURATION = 3.0
LANDING_DURATION = 1.0

try:
    print("ARMING MOTORS...")
    fc_core.set_armed(True)

    # ★ここでオペレーターの入力を確実に待機する
    input("Press ENTER to ARM and start takeoff sequence...")

    time.sleep(2)
    isStarted = True
    sensor.activate()
    start_time = time.ticks_ms()
    
    while True:
        elapsed = time.ticks_diff(time.ticks_ms(), start_time) / 1000.0
        
        # --- 離陸時のランプアップ制御 ---
        if elapsed < RAMP_UP_DURATION:
            # RAMP_UP_DURATION 秒かけてベーススロットルを1250から1400へ滑らかに引き上げる
            throttle = base_throttle_start + (base_throttle_max - base_throttle_start) * (elapsed / RAMP_UP_DURATION)
            fc_core.set_throttle(throttle)
        elif elapsed < (RAMP_UP_DURATION + HOVER_DURATION):
            # 2. ホバリング維持
            fc_core.set_throttle(base_throttle_mid)

        elif elapsed < (RAMP_UP_DURATION + HOVER_DURATION + LANDING_DURATION):
            # 3. 着地ランプダウン
            land_elapsed = elapsed - (RAMP_UP_DURATION + HOVER_DURATION)
            throttle = base_throttle_mid - (
                base_throttle_mid - base_throttle_start
            ) * (land_elapsed / LANDING_DURATION)
            fc_core.set_throttle(throttle)
        else:
            # 4. 着地完了・安全停止
            fc_core.set_throttle(0)
            fc_core.set_armed(False)
            isStarted = False
            print("\nFLIGHT COMPLETED: SAFELY DISARMED.")
            break

        # --- 安全監視（キルスイッチ） ---
        roll, pitch = fc_core.get_angles()
        if abs(roll) > MAX_TILT_DEG or abs(pitch) > MAX_TILT_DEG:
            raise RuntimeError(
                f"Excessive tilt detected (Roll: {roll:.1f}°, Pitch: {pitch:.1f}°)"
            )

        print(
            f"Elapsed: {elapsed:4.1f}s | Roll: {roll:5.1f}°, Pitch: {pitch:5.1f}° | "
        )

        time.sleep_ms(20)

except KeyboardInterrupt:
    print("\nUSER INTERRUPT: SAFELY DISARMED.")

except Exception as e:
    print(f"\nERROR OCCURRED: {e}. SAFELY DISARMED.")

finally:
    
    machine.reset()