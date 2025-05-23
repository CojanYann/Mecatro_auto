from micropyGPS import MicropyGPS
import machine
import utime

class GPS:
    def __init__(self, uart_id=0, baudrate=9600, tx_pin=0, rx_pin=1):
        self.uart = machine.UART(uart_id, baudrate=baudrate, rx=machine.Pin(rx_pin), tx=machine.Pin(tx_pin))
        self.gps = MicropyGPS()

    def convert_to_decimal(self, coord):
        degrees = coord[0]
        minutes = coord[1]
        direction = coord[2]
        decimal = degrees + (minutes / 60)
        if direction in ('S', 'W'):
            decimal *= -1
        return decimal

    def read(self, timeout=1, satellite_bool=1):
        start_time = utime.ticks_ms()
        while utime.ticks_diff(utime.ticks_ms(), start_time) < timeout * 1000:
            if self.uart.any():
                data = self.uart.read(32)
                for byte in data:
                    self.gps.update(chr(byte))
                if self.gps.valid:
                    latitude_decimal = self.convert_to_decimal(self.gps.latitude)
                    longitude_decimal = self.convert_to_decimal(self.gps.longitude)
                    return (latitude_decimal, longitude_decimal)
            utime.sleep_ms(100)
        if satellite_bool == 1:
            print("Satellites visibles:", self.gps.satellites_in_use)
        return None