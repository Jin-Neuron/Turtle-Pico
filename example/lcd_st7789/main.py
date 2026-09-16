import st7789
import tft_config

tft = tft_config.config(rotation=0)
tft.init()

tft.jpg('/img/JinNeuron.jpg', 0, 0, st7789.SLOW)