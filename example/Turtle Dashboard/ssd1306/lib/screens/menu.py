from img_lib import img_lib
from fdrawer import FontDrawer
import os, framebuf

class menu:
    def __init__(self, display):

        self.display = display

        os.chdir('/fonts')
        self.po = FontDrawer( frame_buffer=display, font_name = 'PixelOperator' )
        self.po_b = FontDrawer( frame_buffer=display, font_name = 'PixelOperatorBold')
        
        self.fb1 = framebuf.FrameBuffer(img_lib.item_sel_background, 128, 21, framebuf.MONO_HLSB)
        self.fb2 = framebuf.FrameBuffer(img_lib.scrollbar_background, 3, 64, framebuf.MONO_HLSB)

        self.menu_item_fb = [
            framebuf.FrameBuffer(img_lib.icon_weather, 16, 16, framebuf.MONO_HLSB),
            framebuf.FrameBuffer(img_lib.icon_clock, 16, 16, framebuf.MONO_HLSB),
            framebuf.FrameBuffer(img_lib.icon_timer, 16, 16, framebuf.MONO_HLSB),
            framebuf.FrameBuffer(img_lib.icon_dashboard, 16, 16, framebuf.MONO_HLSB),
            framebuf.FrameBuffer(img_lib.icon_note, 16, 16, framebuf.MONO_HLSB),
        ]

        self.menu_item_char = [
            'Weather',
            'Clock',
            'Timer',
            'Stopwatch',
            'Music'
        ]

        self.item_selected = 0
        self.num_items = len(self.menu_item_fb)
        self.rect_height = int(64 / self.num_items)

    def showDisplay(self):

        item_sel_previous = self.item_selected - 1
        if(item_sel_previous < 0):
            item_sel_previous = self.num_items - 1

        item_sel_next = self.item_selected + 1
        if(item_sel_next >= self.num_items):
            item_sel_next = 0
        
        #backgroundを表示
        self.display.fill(0)

        self.display.blit(self.fb1, 0, 22)
        self.display.blit(self.fb2, 125, 0)
        #scroll barの表示
        self.display.fill_rect(125, self.item_selected * self.rect_height, 3, self.rect_height, 1)

        #previous item
        self.display.blit(self.menu_item_fb[item_sel_previous], 5, 2)
        #self.display.text(menu_item_char[item_sel_previous], 29, 7, 1)
        self.po.print_str(self.menu_item_char[item_sel_previous], 29, 5)

        #selected item
        self.display.blit(self.menu_item_fb[self.item_selected], 5, 24)
        #self.display.text(menu_item_char[item_selected], 29, 27, 1)
        self.po_b.print_str(self.menu_item_char[self.item_selected], 29, 25)

        #next item
        self.display.blit(self.menu_item_fb[item_sel_next], 5, 46)
        #self.display.text(menu_item_char[item_sel_next], 29, 50, 1)
        self.po.print_str(self.menu_item_char[item_sel_next], 29, 48)

        self.display.show()

    def upMenu(self):
        self.item_selected = self.item_selected + 1
        if(self.item_selected >= self.num_items):
            self.item_selected = 0