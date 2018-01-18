from __future__ import division, print_function, unicode_literals
import time
import wiringpi as w

PIN_IRQ = 29
PIN_WR = 28
PIN_IC = 25
PIN_CS0 = 27
PIN_RD = 26
PIN_A0 = 21
PIN_A1 = 22
PIN_A2 = 23
PIN_A3 = 24
PIN_D0 = 0
PIN_D1 = 1
PIN_D2 = 2
PIN_D3 = 3
PIN_D4 = 4
PIN_D5 = 5
PIN_D6 = 6
PIN_D7 = 7
PINS_A = [PIN_A0, PIN_A1, PIN_A2, PIN_A3]
PINS_D = [PIN_D0, PIN_D1, PIN_D2, PIN_D3, PIN_D4, PIN_D5, PIN_D6, PIN_D7]


class RPiReController:

    @classmethod
    def init(cls):
        w.wiringPiSetup()

        cls.__set_input_pin(PIN_IRQ, w.PUD_UP)
        cls.__set_output_pin(PIN_WR, 1)
        cls.__set_output_pin(PIN_IC, 0)
        cls.__set_output_pin(PIN_CS0, 1)
        cls.__set_output_pin(PIN_RD, 1)

        cls.__set_output_pin(PIN_A0, 0)
        cls.__set_output_pin(PIN_A1, 0)
        cls.__set_output_pin(PIN_A2, 0)
        cls.__set_output_pin(PIN_A3, 0)

        cls.__set_data_bus_mode(w.OUTPUT)

    @classmethod
    def reset(cls, microseconds=1):
        w.digitalWrite(PIN_IC, 0)
        time.sleep(microseconds/1000000.0)

        w.digitalWrite(PIN_IC, 1)
        time.sleep(microseconds/1000000.0)

    @classmethod
    def address(cls, address):
        for i in range(0, 4):
            w.digitalWrite(PINS_A[i], (address>>i) & 1)

    @classmethod
    def data(cls, data):
        w.digitalWriteByte(data)

    @classmethod
    def irq(cls):
        return w.digitalRead(PIN_IRQ)

    @classmethod
    def cs0(cls, b):
        w.digitalWrite(PIN_CS0, b)

    @classmethod
    def wr(cls, b):
        w.digitalWrite(PIN_WR, b)

    @classmethod
    def write(cls):
        cls.cs0(0)
        cls.wr(0)
        cls.wr(1)
        cls.cs0(1)

    @classmethod
    def read(cls):
        cls.__set_data_bus_mode(w.INPUT)
        data = 0
        for p in PINS_D:
            data |= w.digitalRead(p)
            data = data<<1
        cls.__set_data_bus_mode(w.OUTPUT)
        return data

    @classmethod
    def __set_input_pin(cls, pin, pud):
        w.pinMode(pin, w.INPUT)
        w.pullUpDnControl(pin, pud)

    @classmethod
    def __set_output_pin(cls, pin, data=None):
        w.pinMode(pin, w.OUTPUT)
        if data is not None:
            w.digitalWrite(pin, data)

    @classmethod
    def __set_data_bus_mode(cls, mode):
        for pin in range(0, 8):
            if mode == w.INPUT:
                cls.__set_input_pin(pin, w.PUD_UP)
            elif mode == w.OUTPUT:
                cls.__set_output_pin(pin, 0)

