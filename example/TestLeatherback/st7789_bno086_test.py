import time
import st7789
import math
import tft_config
from machine import Pin, PWM
from lib.bno08x import *
from lib.bno08x_i2c import BNO08X_I2C
from machine import I2C, Pin
import time 
import vga1_8x8 as font
import vga2_bold_16x32 as font2

I2C_ADDR = 0x4a
i2c = I2C(1, scl=Pin("I2C_SCL"), sda=Pin("I2C_SDA"), freq=400_000)

bno = BNO08X_I2C(i2c, address=I2C_ADDR)

bno.acceleration.enable()
bno.magnetic.enable()
bno.gyro.enable()
bno.quaternion.enable()

tft = tft_config.config(rotation=3)
tft.init()# --- 設定 ---

WIDTH, HEIGHT = 240, 320
CX, CY = WIDTH // 2, HEIGHT // 2
SCALE = 50  # 立方体の大きさ
FOV = 200    # 遠近感

# 立方体の頂点 (x, y, z)
vertices = [
    [-1,-1, 1], [ 1,-1, 1], [ 1, 1, 1], [-1, 1, 1],
    [-1,-1,-1], [ 1,-1,-1], [ 1, 1,-1], [-1, 1,-1]
]
edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
old_points = None

def get_normalized_quat():
    """クォータニオンを取得し、確実に単位円内に収める"""
    qi, qj, qk, qr = bno.quaternion
    # もし値が1.0より極端に大きい場合（生データの可能性）、補正する
    mag = math.sqrt(qi**2 + qj**2 + qk**2 + qr**2)
    if mag == 0: return (0, 0, 0, 1)
    return (qr/mag, qi/mag, qk/mag, -qj/mag)

print("3D Start...")
tft.fill(st7789.BLACK)
tft.text(font, "BNO08x 3D FIX", 10, 10, st7789.WHITE)

while True:
    if bno.update_sensors():
        # 1. データの取得と正規化
        qi, qj, qk, qr = get_normalized_quat()
        
        # 2. 回転行列 R の計算
        # ※ 数式ミスを防ぐため、より標準的な表記に変更
        xx, xy, xz = 1-2*(qj**2+qk**2), 2*(qi*qj-qk*qr), 2*(qi*qk+qj*qr)
        yx, yy, yz = 2*(qi*qj+qk*qr), 1-2*(qi**2+qk**2), 2*(qj*qk-qi*qr)
        zx, zy, zz = 2*(qi*qk-qj*qr), 2*(qj*qk+qi*qr), 1-2*(qi**2+qj**2)

        # 3. 描画の準備
        points = []
        for x, y, z in vertices:
            # 回転適用
            nx = x * xx + y * xy + z * xz
            ny = x * yx + y * yy + z * yz
            nz = x * zx + y * zy + z * zz
            
            # 投影 ( nz+3 でカメラからの距離を固定 )
            pz = nz + 3
            factor = FOV / pz
            px = int(nx * factor) + CX
            py = int(ny * factor) + CY
            points.append((px, py))
            
        # A. 消去：前回の線があった場所だけを黒でなぞる
        if old_points:
            for s, e in edges:
                p1, p2 = old_points[s], old_points[e]
            
                # --- 座標のクランプ処理 ---
                # x座標を 0～239 の範囲に収める
                x1 = max(0, min(int(p1[0]), WIDTH-1))
                x2 = max(0, min(int(p2[0]), WIDTH-1))
                
                # y座標を 0(またはHEADER_H)～239 の範囲に収める
                # ※見出しを守るなら下限を HEADER_H にします
                y1 = max(0, min(int(p1[1]), HEIGHT-1))
                y2 = max(0, min(int(p2[1]), HEIGHT-1))

                # 前回の線がヘッダーより下にあった場合のみ消去（念のため）
                tft.line(x1, y1, x2, y2, st7789.BLACK)

        for s, e in edges:
            p1, p2 = points[s], points[e]
            
            # --- 座標のクランプ処理 ---
            # x座標を 0～239 の範囲に収める
            x1 = max(0, min(int(p1[0]), WIDTH-1))
            x2 = max(0, min(int(p2[0]), WIDTH-1))
            
            # y座標を 0(またはHEADER_H)～239 の範囲に収める
            # ※見出しを守るなら下限を HEADER_H にします
            y1 = max(0, min(int(p1[1]), HEIGHT-1))
            y2 = max(0, min(int(p2[1]), HEIGHT-1))
            
            tft.line(x1, y1, x2, y2, st7789.GREEN)
        
        old_points = points
        
    time.sleep_ms(5)