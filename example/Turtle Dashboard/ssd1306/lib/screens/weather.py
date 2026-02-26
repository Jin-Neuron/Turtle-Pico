from img_lib import img_lib
from fdrawer import FontDrawer
import os, framebuf, requests
class weather:

    def __init__(self, display):
        
        self.display = display
        url = "https://www.jma.go.jp/bosai/forecast/data/forecast/270000.json"

        os.chdir('/fonts')
        self.font16 = FontDrawer( frame_buffer=self.display, font_name = '7SegmentDisplay_16' )
        self.font25 = FontDrawer( frame_buffer=self.display, font_name = 'Nixie_23' )
    
        self.menu_item_fb = [
            framebuf.FrameBuffer(img_lib.icon_back, 16, 16, framebuf.MONO_HLSB),
            framebuf.FrameBuffer(img_lib.icon_yesterday, 16, 16, framebuf.MONO_HLSB),
            framebuf.FrameBuffer(img_lib.icon_tomorrow, 16, 16, framebuf.MONO_HLSB),
        ]

        self.weahter_item_fb = [
            framebuf.FrameBuffer(img_lib.icon_sunny, 32, 32, framebuf.MONO_HLSB),
            framebuf.FrameBuffer(img_lib.icon_cloudy, 32, 32, framebuf.MONO_HLSB),
            framebuf.FrameBuffer(img_lib.icon_rainy, 32, 32, framebuf.MONO_HLSB),
            framebuf.FrameBuffer(img_lib.icon_snowy, 32, 32, framebuf.MONO_HLSB),
        ]

        self.weathers = ["Sunny", "Cloudy", "Rainy", "Snowy"]

        data = requests.get(url).json()
        self.weatherDates = data[0]['timeSeries'][0]['timeDefines']
        self.weatherCodes = data[0]['timeSeries'][0]['areas'][0]['weatherCodes']

        self.sel_item_box = framebuf.FrameBuffer(img_lib.item_sel_background_mini, 20, 20, framebuf.MONO_HLSB)
        
        self.weatherIdx = 0
        self.num_weathers = 3
        self.item_selected = 0
        self.num_items = 3

    def showDisplay(self):

        target = 'T'
        index = self.weatherDates[self.weatherIdx].find(target)
        dateStr = self.weatherDates[self.weatherIdx][5:index].split('-')

        weather_pos = (int)((int)(self.weatherCodes[self.weatherIdx]) / 100 - 1)

        self.display.fill(0)

        selbox_offsetX = 30 * self.item_selected
        if(self.item_selected > 0):
            selbox_offsetX = selbox_offsetX + 42
        self.display.blit(self.sel_item_box, 3 + selbox_offsetX, 43)

        self.display.blit(self.menu_item_fb[0], 5, 45)
        if(self.weatherIdx > 0):
            self.display.blit(self.menu_item_fb[1], 77, 45)
        if(self.weatherIdx < self.num_weathers - 1):
            self.display.blit(self.menu_item_fb[2], 107, 45)

        self.display.blit(self.weahter_item_fb[weather_pos], 3, 5)

        self.font16.print_str(dateStr[0] + "/" + dateStr[1], 88, 2)
        self.font25.print_str(self.weathers[weather_pos], 42, 17)

        self.display.show()
    
    def zfill(self, s, width):
        if len(s) < width:
            return ("0" * (width - len(s))) + s
        else:
            return s

    def upMenu(self):
        self.item_selected = self.item_selected + 1
        if(self.item_selected >= self.num_items):
            self.item_selected = 0
        if(self.weatherIdx == 0 and self.item_selected == 1):
            self.item_selected = self.num_weathers - 1
        if(self.weatherIdx == self.num_weathers - 1 and self.item_selected == 2):
            self.item_selected = 0

    def selMenu(self):
        if(self.item_selected == 0):
            return -1
        elif(self.item_selected == 1):
            if(self.weatherIdx > 0):
                self.weatherIdx -= 1
            else:
                self.weatherIdx = 0
            if(self.weatherIdx == 0):
                self.item_selected = self.num_weathers - 1
        elif(self.item_selected == 2):
            if(self.weatherIdx < self.num_weathers - 1):
                self.weatherIdx += 1
            else:
                self.weatherIdx = self.num_weathers - 1
            if(self.weatherIdx == self.num_weathers - 1):
                self.item_selected = 0
        else:
            raise Exception( "Invalid Menu Item!" )
        
        return 0