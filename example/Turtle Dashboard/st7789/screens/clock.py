import os, time, math, ntptime, st7789
from machine import Timer

class clock:

    def __init__(self, font, font_bold, display):
        
        self.display = display
        ntptime.host = "time.cloudflare.com"
        
        self.isTimeset = False
        self.font = font
        self.font_bold = font_bold

        self.len_long = 40
        self.len_middle = 35
        self.len_short = 30

        self.angleLong = None
        self.angleMiddle = None
        self.angleShort = None

    def showDisplay(self):
        self.display.fill(0x0000) # 黒でクリア
        self.display.png('/img/clock_back.png', 0, 0, True)
        self.timer = Timer(period=1000, callback=lambda t: self.updateTime())
        self.display.png('/img/circle-left.png', 15, 320 - 37, True)
        self.display.rect(10, 320 - 42, 42, 42, 0x07E0)

    def updateTime(self):
        npttime = time.localtime(time.time() + 9 * 60 * 60)

        hour = str(npttime[3])
        minutes = str(npttime[4])
        seconds = str(npttime[5])
        timestr = '{}:{}:{}'.format(self.zfill(hour, 2), self.zfill(minutes, 2), self.zfill(seconds, 2))

        month = str(npttime[1])
        day = str(npttime[2])
        datestr = '{}/{}'.format(self.zfill(month, 2), self.zfill(day, 2))
        
        self.display.text(self.font_bold, timestr, 85-64, 200, 0xFFFF)
        self.display.text(self.font, datestr, 85-40, 235, 0xFFFF)

        #angle setting [deg]
        angleLongParSeconds = 6
        angleMiddleParMinutes = 6
        angleShortParMinutes = 0.5
        angleClockOffset = -90

        if self.angleLong is not None:
            self.draw_styled_hand(self.angleLong, self.len_long, 4, 0x1689)
            self.draw_styled_hand(self.angleMiddle, self.len_middle, 4, 0x1689)
            self.draw_styled_hand(self.angleShort, self.len_short, 4, 0x1689)

        self.angleLong = npttime[5] * angleLongParSeconds + angleClockOffset
        self.angleMiddle = npttime[4] * angleMiddleParMinutes + angleClockOffset
        self.angleShort = (npttime[3] % 12 * 60 + npttime[4]) * angleShortParMinutes + angleClockOffset

        self.draw_styled_hand(self.angleLong, self.len_long, 4, 0xFFFF)
        self.draw_styled_hand(self.angleMiddle, self.len_middle, 4, st7789.YELLOW) 
        self.draw_styled_hand(self.angleShort, self.len_short, 4, 0x9FD3)

        self.display.fill_circle(78, 100, 3, 0x0000) # 軸の穴を描画

    def draw_styled_hand(self, angle, length, width, color, offset_back=10):

        CX = 78
        CY = 100
        
        """
        angle: 角度(度)
        length: 針の長さ
        width: 根元の太さ
        color: RGB565色
        offset_back: 軸から後ろに突き出す長さ(隠し味)
        """
        rad = math.radians(angle)
        # 先端、右、後ろ、左の4点
        # 極座標から直交座標へ変換
        points = [
            (int(length * math.cos(rad)), int(length * math.sin(rad))), # 先端
            (int(width *  math.cos(rad + 1.8)), int(width *  math.sin(rad + 1.8))), # 右
            (int(- offset_back * math.cos(rad)), int(- offset_back * math.sin(rad))), # 後ろ
            (int(width * math.cos(rad - 1.8)), int(width *  math.sin(rad - 1.8))),  # 左
            (int(length * math.cos(rad)), int(length * math.sin(rad))) # 先端に戻る
        ]
        
        # 描画（ライブラリの仕様に合わせた形式に変換）
        # st7789_mpyのpolygonは通常頂点のリストを受け取ります
        self.display.fill_polygon(points, CX, CY, color)
    
    def zfill(self, s, width):
        if len(s) < width:
            return ("0" * (width - len(s))) + s
        else:
            return s
        
    def upMenu(self):
        pass

    def selMenu(self):
        self.timer.deinit() # タイマー停止
        if self.angleLong is not None:
            self.draw_styled_hand(self.angleLong, self.len_long, 4, 0x1689)
            self.draw_styled_hand(self.angleMiddle, self.len_middle, 4, 0x1689)
            self.draw_styled_hand(self.angleShort, self.len_short, 4, 0x1689)
        return -1

    def setTimeThread(self):
        cnt =  0
        while(True):
            # 時間の同期を試みる
            try:
                # NTPサーバーから取得した時刻でPico WのRTCを同期
                ntptime.settime()
                self.isTimeset = True
                return
            except:
                #タイムアウトの設定
                cnt = cnt + 1
                if(cnt > 15):
                    raise Exception('ntp timeout')
                #同期に失敗した場合は再度挑戦