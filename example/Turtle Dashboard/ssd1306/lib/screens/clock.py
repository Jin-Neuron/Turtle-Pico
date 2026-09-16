from img_lib import img_lib
from fdrawer import FontDrawer
import os, framebuf, time, math, ntptime
class clock:

    def __init__(self, display):
        
        self.display = display
        ntptime.host = "time.cloudflare.com"

        os.chdir('/fonts')
        self.font16 = FontDrawer( frame_buffer=self.display, font_name = '7SegmentDisplay_16' )
        self.font25 = FontDrawer( frame_buffer=self.display, font_name = 'Nixie_23' )
    
        self.menu_item_fb = [
            framebuf.FrameBuffer(img_lib.icon_back, 16, 16, framebuf.MONO_HLSB),
            framebuf.FrameBuffer(img_lib.icon_24h, 16, 16, framebuf.MONO_HLSB),
            framebuf.FrameBuffer(img_lib.icon_clock, 16, 16, framebuf.MONO_HLSB),
            framebuf.FrameBuffer(img_lib.icon_digital, 16, 16, framebuf.MONO_HLSB),
        ]

        self.dial = framebuf.FrameBuffer(img_lib.analog_dial, 128, 43, framebuf.MONO_HLSB)
        self.sel_item_box = framebuf.FrameBuffer(img_lib.item_sel_background_mini, 20, 20, framebuf.MONO_HLSB)
        
        self.isAnalog = False
        self.is24H = False
        self.isTimeset = False
        self.item_selected = 0
        self.num_items = 4

    def showDisplay(self):
        
        npttime = time.localtime(time.time() + 9 * 60 * 60)
        
        self.display.fill(0)

        selbox_offsetX = 30 * self.item_selected
        if(self.item_selected > 1):
            selbox_offsetX = selbox_offsetX + 12
        self.display.blit(self.sel_item_box, 3 + selbox_offsetX, 43)

        #display setting
        if(not self.isAnalog): 
            
            self.display.blit(self.menu_item_fb[0], 5, 45)
            self.display.blit(self.menu_item_fb[1], 35, 45)
            self.display.blit(self.menu_item_fb[2], 77, 45)

            hour = str(npttime[3])
            minutes = str(npttime[4])
            seconds = str(npttime[5])

            ampmstr = ''

            if(not self.is24H):
                if(int(hour) >= 12):
                    ampmstr = 'PM'
                    hour = str(int(hour) - 12)
                else:
                    ampmstr = 'AM'
            
            timestr = '{}:{}:{}'.format(self.zfill(hour, 2), self.zfill(minutes, 2), self.zfill(seconds, 2))

            month = str(npttime[1])
            day = str(npttime[2])
            datestr = '{}/{}'.format(self.zfill(month, 2), self.zfill(day, 2))

            self.font16.print_str(datestr, 1, 1)
            self.font16.print_str(ampmstr, 108, 1)
            self.font25.print_str(timestr, 25, 19)
        
        else:
            self.display.blit(self.menu_item_fb[0], 5, 45)
            self.display.blit(self.menu_item_fb[3], 107, 45)

            startX = 64
            startY = 22

            len_long = 18
            len_middle = 15
            len_short = 10

            #angle setting [deg]
            angleLongParSeconds = -6
            angleMiddleParMinutes = -6
            angleShortParMinutes = -0.5
            angleClockOffset = 180

            angleLong = npttime[5] * angleLongParSeconds + angleClockOffset
            angleMiddle = npttime[4] * angleMiddleParMinutes + angleClockOffset
            angleShort = (npttime[3] % 12 * 60 + npttime[4]) * angleShortParMinutes + angleClockOffset
            
            longX = int(len_long * math.sin(math.radians(angleLong)))
            longY = int(len_long * math.cos(math.radians(angleLong)))
            middleX = int(len_middle * math.sin(math.radians(angleMiddle)))
            middleY = int(len_middle * math.cos(math.radians(angleMiddle)))
            shortX = int(len_short * math.sin(math.radians(angleShort)))
            shortY = int(len_short * math.cos(math.radians(angleShort)))

            self.display.blit(self.dial, 0, 0)

            self.display.line(startX, startY, startX + longX, startY + longY, 1)
            self.display.line(startX, startY, startX + middleX, startY + middleY, 1)
            self.display.line(startX, startY, startX + shortX, startY + shortY, 1)

        self.display.show()
    
    def zfill(self, s, width):
        if len(s) < width:
            return ("0" * (width - len(s))) + s
        else:
            return s

    def upMenu(self):
        self.item_selected = self.item_selected + 1
        if(self.isAnalog):
            if(self.item_selected >= self.num_items):
                self.item_selected = 0
            elif(self.item_selected > 0):
                self.item_selected = self.num_items - 1
        else:
            if(self.item_selected >= self.num_items - 1):
                self.item_selected = 0

    def selMenu(self):
        if(self.item_selected == 0):
            self.is24H = False
            self.menu_item_fb[1] = framebuf.FrameBuffer(img_lib.icon_24h, 16, 16, framebuf.MONO_HLSB)
            return -1
        elif(self.item_selected == 1):
            self.is24H = not self.is24H
            if(self.is24H):
                self.menu_item_fb[1] = framebuf.FrameBuffer(img_lib.icon_ampm, 16, 16, framebuf.MONO_HLSB)
            else:
                self.menu_item_fb[1] = framebuf.FrameBuffer(img_lib.icon_24h, 16, 16, framebuf.MONO_HLSB)
        elif(self.item_selected == 2):
            self.isAnalog = True
            self.item_selected = 0
        elif(self.item_selected == 3):
            self.isAnalog = False
            self.item_selected = 0
        else:
            raise Exception( "Invalid Menu Item!" )
        
        return 0

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