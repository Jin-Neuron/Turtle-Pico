import machine
from machine import PWM
import network
import socket
import time
from wifi_config import wifi_config
 
#LEDのピンをPWM出力に設定
led_r=PWM(machine.Pin("LED_R", machine.Pin.OUT))
led_l = PWM(machine.Pin("LED_L", machine.Pin.OUT))

#周波数とデューティー比を設定
led_r.freq(1000)
led_r.duty_u16(0)
led_l.freq(1000)
led_l.duty_u16(0)

#自宅Wi-FiのSSIDとパスワードを入力
ssid = wifi_config.ssid
password = wifi_config.pw

#Wi-Fiに接続
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

#HTMLを定義
html = """<!DOCTYPE html><html>
<head><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}
.buttonGreen { background-color: #4CAF50; border: 2px solid #000000;; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; }
.buttonRed { background-color: #D11D53; border: 2px solid #000000;; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; }
.buttonBlue { background-color: #191970; border: 2px solid #000000;; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; }
text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
</style></head>
<body><center><h1>Turtle Pico LED Web Control</h1></center><br><br>
<form method="POST"><center>
<center> <button class="buttonBlue" name="led" value="blue" type="submit">Blue Toggle</button>
<center> <label>duty_blue<br><input type="range" name="duty_blue" value="%s" min="0" max="100"></label>
<br><br>
<center> <button class="buttonRed" name="led" value="red" type="submit">Red Toggle</button>
<center> <label>duty_red<br><input type="range" name="duty_red" value="%s"min="0" max="100"></label>
</form>
<br><br>
<br><br></body></html>
"""

#接続を待機
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

#接続できなかった場合はエラーを表示
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
#接続できた場合はIPアドレスを表示
else:
    print('Connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

#ソケットを作成
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print('listening on', addr)

duty_blue = 0
duty_red = 0

#クライアントからの接続を待機
while True:
    cl, addr = s.accept()
    try:
        #クライアントからのリクエストを解析
        print('client connected from', addr)
        request = cl.recv(1024)
        print("request:")
        print(request)
        request = str(request)
        red_toggle = request.find('led=red')
        blue_toggle = request.find('led=blue')
        
        #red_toggleの場合はduty_redを変更
        if red_toggle > -1:
            start = request.find('duty_red=')+len("duty_red=")
            end = request.find("'",start)
            duty_red = int(request[start:end])
            duty_red_u16 = duty_red / 100 * 65536

            print("red_value set",duty_red)
            led_l.duty_u16(int(duty_red_u16))
        
        #blue_toggleの場合はduty_blueを変更
        if blue_toggle > -1:
            start = request.find('duty_blue=')+len("duty_blue=")
            end = request.find("&",start)
            duty_blue = int(request[start:end])
            duty_blue_u16 = duty_blue / 100 * 65536
            
            print("blue_value set",duty_blue)
            led_r.duty_u16(int(duty_blue_u16))
        
        #HTMLをクライアントに送信
        response = html % (duty_blue, duty_red)
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()
        
    except Exception as e:
        cl.close()
        print(e)
