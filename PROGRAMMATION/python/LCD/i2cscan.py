import machine
sda = machine.Pin(2)
scl = machine.Pin(3)
i2c = machine.I2C(1,sda=sda,scl=scl, freq=400000)
a = i2c.scan()
print(i2c.scan(), hex(a[0]))