from machine import Timer

class menu:

    def __init__(self, font, font_bold, display):

        self.display = display
        self.font = font
        self.font_bold = font_bold

        self.menu_item_char = [
            'Weather',
            'Clock',
            'Timer',
            'Stopwatch',
            'Music'
        ]

        self.menu_item_icon = [
            '/img/cloud-sun.png',
            '/img/clock.png',
            '/img/alarm-clock.png',
            '/img/stopwatch.png',
            '/img/music.png'
        ]

        self.item_selected = 0
        self.num_items = len(self.menu_item_char)
        self.rect_height = int(64 / self.num_items)

    def showDisplay(self):

        item_sel_previous = self.item_selected - 1
        if(item_sel_previous < 0):
            item_sel_previous = self.num_items - 1

        item_sel_next = self.item_selected + 1
        if(item_sel_next >= self.num_items):
            item_sel_next = 0
        
        self.display.fill(0x0000) # 黒でクリア
        
        for i, item in enumerate(self.menu_item_char):
            y_pos = 42 + (i * 42) # 項目ごとの高さ
            self.display.png(self.menu_item_icon[i], 0, y_pos - 5) # アイコン
            if i == self.item_selected:
                self.display.text(self.font_bold, item, 37, y_pos, 0xFFFF) # 文字
                # 選択中の項目は枠を表示
                self.display.rect(0, y_pos - 5, 170, 42, 0x07E0) # 緑色のハイライト
            else:
                self.display.text(self.font, item, 32, y_pos, 0xFFFF) # 白文字

        self.tim_scroll = Timer(period=300, callback=lambda t: self.scrollMenu())
        self.scrolledText = self.menu_item_char[self.item_selected] + ' ' * (10 - len(self.menu_item_char[self.item_selected]))# スクロール用テキスト
        self.scrollingIdx = 0

    def scrollMenu(self):
        self.scrollingIdx += 1
        if self.scrollingIdx > 9:
            self.scrollingIdx = 0
        scrolledText = self.scrolledText[self.scrollingIdx:] + self.scrolledText[:self.scrollingIdx]
        y_pos = 42 + (self.item_selected * 42) # 項目ごとの高さ
        self.display.fill_rect(32, y_pos-5, 170, 42, 0x0000) # 黒でクリア
        self.display.text(self.font_bold, scrolledText, 32, y_pos, 0xFFFF) # 文字
        # 選択中の項目は枠を表示
        self.display.rect(0, y_pos - 5, 170, 42, 0x07E0) # 緑色のハイライト

    def upMenu(self):
        self.tim_scroll.deinit() # タイマー停止
        
        self.item_selected = self.item_selected + 1
        if(self.item_selected >= self.num_items):
            self.item_selected = 0
        self.scrollingIdx = 0
        self.showDisplay()