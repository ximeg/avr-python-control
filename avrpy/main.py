import serial
from registers import *
from time import sleep

ms = 0.001
us = 0.001 * ms
kHz = 1000
MHz = 1000*kHz

class AVR(object):
    def __init__(self, port="COM6", baudrate = 2*MHz):
        self.serial = serial.Serial(port, baudrate=baudrate, timeout=4)
        if not self.serial.is_open:
            self.serial.open()

        # We wait for Arduino to startup
        startup_message = self.serial.readline().strip().decode()
        print(startup_message)
        assert startup_message == "Arduino is up!"
        self.serial.flush()
        self.serial.timeout = 20*ms
        sleep(0.08)
    
    def __del__(self):
        self.serial.close()

    def set_register(self, addr, value):
        self.serial.write(bytearray([ord("W"), addr, value]))

    def get_register(self, addr):
        self.serial.flush()
        self.serial.write(bytearray([ord("R"), addr, 0]))
        return ord(self.serial.read(1))

    def get_16bit_register(self, addrL):
        byte_L = self.get_register(addrL)
        byte_H = self.get_register(addrL + 1)
        return byte_H << 8 | byte_L

    def set_16bit_register(self, addrL, value):
        byte_L = value & 0xff
        byte_H = (value >> 8)
        self.set_register(addrL + 1, byte_H)
        self.set_register(addrL, byte_L)


    @property
    def OCR1A(self):
        return self.get_16bit_register(R16.OCR1A)
    @OCR1A.setter
    def OCR1A(self, value):
        self.set_16bit_register(R16.OCR1A, value)

    @property
    def OCR1B(self):
        return self.get_16bit_register(R16.OCR1B)
    @OCR1B.setter
    def OCR1B(self, value):
        self.set_16bit_register(R16.OCR1B, value)

    @property
    def TCNT1(self):
        return self.get_16bit_register(R16.TCNT1)
    @TCNT1.setter
    def TCNT1(self, value):
        self.set_16bit_register(R16.TCNT1, value)

    @property
    def ICR1(self):
        return self.get_16bit_register(R16.ICR1)
    @ICR1.setter
    def ICR1(self, value):
        self.set_16bit_register(R16.ICR1, value)

    @property
    def ADC(self):
        return self.get_16bit_register(R16.ADC)
    @ADC.setter
    def ADC(self, value):
        self.set_16bit_register(R16.ADC, value)


    @property
    def TCCR1A(self):
        return self.get_register(R8.TCCR1A)
    @TCCR1A.setter
    def TCCR1A(self, value):
        self.set_register(R8.TCCR1A, value)

    @property
    def TCCR1B(self):
        return self.get_register(R8.TCCR1B)
    @TCCR1B.setter
    def TCCR1B(self, value):
        self.set_register(R8.TCCR1B, value)

    @property
    def TCCR1C(self):
        return self.get_register(R8.TCCR1C)
    @TCCR1C.setter
    def TCCR1C(self, value):
        self.set_register(R8.TCCR1C, value)

# TODO: How to generate these properties dynamically for all registers??


if __name__ == "__main__":
    avr = AVR()

    # Enable outputs on port B
    avr.set_register(R8.DDRB, 0xff)

  # bit    : 7      6      5      4      3     2    1     0
  # TCCR1A : COM1A1 COM1A0 COM1B1 COM1B0 -     -    WGM10 WGM11
  # TCCR1B : ICNC1  ICES1  -      WGM13  WGM12 CS12 CS11  CS10
  # TCCR1C : FOC1A  FOC1B  -      -      -     -    -     -

    # Set output compare registers
    freq = (16*MHz / 1024)

    # Set period to 383 ms
    avr.ICR1 = int(383*ms*freq)
    # Output A (pin 10) stays high for 52.3 ms
    avr.OCR1A = int(52.3*ms*freq)
    # Output B (pin 9) stays low for 74.5 ms
    avr.OCR1B = int(74.5*ms*freq)

    # Reset timer
    avr.TCNT1 = 0

    # Set pin A on bottom, clear on match. B inverted
    avr.TCCR1A = COM1A1 | COM1B1 | COM1B0 | WGM11
    # Fast PWM mode, top=ICR1, prescaler 1024
    avr.TCCR1B = WGM13 | WGM12 | CS12 | CS10
