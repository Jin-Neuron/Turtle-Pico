from machine import PWM, Pin, SPI, reset
from lib.wavplayer import WavPlayer
import os
from lib.sdcard import SDCard
import time

# --- 1. 準備編：ピンと周辺機器の設定 ---

# 左右のLEDをPWM（明るさ調整できるモード）で準備します
orange = PWM(Pin("LED_R", Pin.OUT))
green = PWM(Pin("LED_L", Pin.OUT))
orange.freq(1000)
green.freq(1000)

# 左右のスイッチの設定
playSW = Pin("SW_R", Pin.IN, Pin.PULL_DOWN)
stopSW = Pin("SW_L", Pin.IN, Pin.PULL_DOWN)

# SDカード用のチップセレクトピン
sd_cs = Pin("SD_CS")

# I2S（高品質デジタルオーディオ通信）用のピン設定
sck_pin = Pin("I2S_BCLK")   
ws_pin = Pin("I2S_LRCLK")   
sd_pin = Pin("I2S_SDATA")   

# 超音波距離センサー用のピン設定
trig = Pin("TRIG_TX", Pin.OUT)
echo = Pin("ECHO_RX", Pin.IN)

# SDカードに使うSPI通信の設定
spi = SPI( 1,
           baudrate = 100000,
           sck  = Pin("SPI_SCK"),
           mosi = Pin("SPI_MOSI"),
           miso = Pin("SPI_MISO"))

# SDカードの操作係を作成します
sd = SDCard(spi, sd_cs)


# --- 2. メインの処理をまとめた関数 ---
def main():

    # SDカードを認識させ、中のファイル一覧を取得します
    os.mount(sd, '/sd')
    os.chdir('sd')
    list = os.listdir("/sd")

    try: 
        # ファイル一覧の数だけ順番に処理を繰り返します
        for i in range(0, len(list)):
            
            # 曲の開始時は緑LEDをON、オレンジLEDをOFF
            green.duty_u16(65535)
            orange.duty_u16(0)

            # ".wav" ファイル以外はスキップします
            if(list[i].find(".wav") == -1):
                continue
            
            # オーディオプレイヤーの準備
            wp = WavPlayer(
                id=0,
                sck_pin=sck_pin,
                ws_pin=ws_pin,
                sd_pin=sd_pin,
                ibuf=40000, 
            )
            
            # 画面の代わりに、パソコンのコンソールに曲名を表示
            print("Playing:", list[i])
            
            # 音楽を再生スタート
            wp.play(list[i], loop=False)
            
            # 音楽が再生されている間の監視ループ
            while wp.isplaying():
                
                # 距離センサーで手をかざしているか確認
                distance = messure_distance()
                
                # 手をかざして（5cm未満）スキップした時の処理
                if distance < 5:
                    print("skip")
                    wp.stop() 
                    
                    # LEDをオレンジに切り替えてお知らせ
                    green.duty_u16(0)
                    orange.duty_u16(65535)
                    time.sleep(0.5)
                    break 
                    
                # 右スイッチが押されたら音量アップ
                if stopSW.value() == 1:
                    wp.increase_volume()
                    
                # 左スイッチが押されたら音量ダウン
                if playSW.value() == 1:
                    wp.decrease_volume()
                    
                # センサー計測の間隔を少し空ける
                time.sleep(0.15)
                pass
                
            # 1曲終わるごとに0.5秒お休みして次の曲へ
            time.sleep(0.5)

    except KeyboardInterrupt:
        # プログラムを強制終了(Ctrl+C)した時の安全装置
        print("KeyboardInterrupt")
        reset()


# --- 3. 距離を測る専用の関数 ---
def messure_distance():
    trig.low()
    time.sleep_us(2)
    trig.high() 
    time.sleep_us(10)
    trig.low()
    
    signaloff, signalon = 0, 0
    while echo.value() == 0:
        signaloff = time.ticks_us()
    while echo.value() == 1:
        signalon = time.ticks_us()
        
    timepassed = signalon - signaloff
    dis = (timepassed * 0.0343) / 2
    return dis


# --- プログラムのスタート地点 ---
if __name__ == "__main__":
    main()
    print("end")
    reset()