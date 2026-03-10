import smbus
import time

# I2Cの設定
bus = smbus.SMBus(1)
address = 0x36 # X1200のバッテリー管理チップのアドレス

def read_voltage():
    read = bus.read_word_data(address, 2)
    swapped = bytes([read & 0xFF, (read >> 8) & 0xFF]) # エンディアン変換
    voltage = int.from_bytes(swapped, 'big') * 1.25 / 1000 / 16
    return voltage

def read_capacity():
    read = bus.read_word_data(address, 4)
    swapped = bytes([read & 0xFF, (read >> 8) & 0xFF])
    capacity = int.from_bytes(swapped, 'big') / 256
    return capacity

print(f"電圧: {read_voltage():.2f} V")
print(f"残量: {read_capacity():.1f} %")