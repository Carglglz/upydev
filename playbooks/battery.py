from machine import ADC
bat = ADC(Pin(35))
bat.atten(ADC.ATTN_11DB)

class Battery:
    def __init__(self, bat=bat):
        self.bat = bat 

    def __repr__(self):
        volt =((self.bat.read()*2)/4095)*3.6
        percentage = round((volt - 3.3) / (4.23 - 3.3) * 100, 1)
        return f"Battery Voltage : {round(volt, 2)}, V; Level:{percentage} %"

battery = Battery()

