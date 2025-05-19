from machine import I2C, Pin
import time

# Configuration I2C avec les pins qui fonctionnent
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100000)  # Fréquence réduite pour plus de stabilité

# Définition de l'adresse LCD détectée
LCD_ADDR = 0x27

# Classe LCD améliorée pour écrans LCD I2C avec PCF8574
class LCD:
    def __init__(self, i2c, addr):
        self.i2c = i2c
        self.addr = addr
        self.backlight = True
        
        # Constantes
        self.LCD_BACKLIGHT = 0x08
        self.LCD_NOBACKLIGHT = 0x00
        self.En = 0x04  # Enable bit
        self.Rw = 0x02  # Read/Write bit
        self.Rs = 0x01  # Register select bit
        
        # Initialisation plus robuste
        time.sleep_ms(50)
        
        # Mode 8-bit d'abord
        self._write4bits(0x30, False)
        time.sleep_ms(5)
        self._write4bits(0x30, False)
        time.sleep_ms(5)
        self._write4bits(0x30, False)
        time.sleep_ms(5)
        
        # Passer en mode 4-bit
        self._write4bits(0x20, False)
        time.sleep_ms(5)
        
        # Fonction set: mode 4-bit, 2 lignes, 5x8 points
        self.command(0x28)
        # Display control: display on, cursor off, blink off
        self.command(0x0C)
        # Entry mode set: increment, no shift
        self.command(0x06)
        
        self.clear()
    
    def clear(self):
        self.command(0x01)  # Clear display
        time.sleep_ms(2)
    
    def home(self):
        self.command(0x02)  # Return home
        time.sleep_ms(2)
    
    def move_to(self, col, row):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        self.command(0x80 | (col + row_offsets[row]))
    
    def command(self, cmd):
        self._send(cmd, False)
    
    def write(self, data):
        self._send(data, True)
    
    def _send(self, data, rs):
        # Envoie en mode 4 bits
        high = (data & 0xF0)
        low = ((data << 4) & 0xF0)
        
        self._write4bits(high, rs)
        self._write4bits(low, rs)
    
    def _write4bits(self, value, rs):
        s = value
        if rs:
            s |= self.Rs
        if self.backlight:
            s |= self.LCD_BACKLIGHT
            
        try:
            self.i2c.writeto(self.addr, bytes([s]))
            time.sleep_us(1)
            self.i2c.writeto(self.addr, bytes([s | self.En]))  # Pulse enable
            time.sleep_us(1)
            self.i2c.writeto(self.addr, bytes([s]))
            time.sleep_us(100)  # Temps d'attente plus long
        except Exception as e:
            print(f"Erreur d'écriture: {e}")
    
    def putchar(self, char):
        self.write(ord(char))
    
    def putstr(self, string):
        for char in string:
            self.putchar(char)

try:
    # Scan I2C pour confirmation
    devices = i2c.scan()
    if devices:
        print(f"Appareil détecté à l'adresse: 0x{devices[0]:x}")
        
        # Initialiser l'écran
        lcd = LCD(i2c, LCD_ADDR)
        
        # Afficher un message
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Bonjour!")
        lcd.move_to(0, 1)
        lcd.putstr("Ca marche!")
        
        print("Message affiché avec succès!")
    else:
        print("Aucun appareil I2C trouvé!")
        
except Exception as e:
    print(f"Erreur: {e}")