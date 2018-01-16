from __future__ import division, print_function, unicode_literals
import time

from rpi_re.rpi_re import RPiReController


class ModuleController:

    modules = {}

    def __init__(self):
        self.__ym2608_address_p0 = None
        self.__ym2608_address_p1 = None

        RPiReController.init()
        self.reset()

    def reset(self):
        RPiReController.reset(microseconds=1000)
         
        for i, m in self.modules.items():
            # Module Initialization
            if m == 'YM2608':
                self.__write_ym2608_p0(i, 0x29, 0x80)
            if m == 'SN76489':
                self.__write_sn76489(i, 0x9f)
                self.__write_sn76489(i, 0xbf)
                self.__write_sn76489(i, 0xdf)
                self.__write_sn76489(i, 0xff)

    def write(self, name, address, data):
        for i, m in self.modules.items():
            if name == 'AY8910' and m == name:
                self.__write_ay8910(i, address, data)
            elif name == 'SN76489' and m == name:
                self.__write_sn76489(i, data)
            elif name == 'YM2151' and m == name:
                self.__write_ym2151(i, address, data)
            elif name == 'YM2203' and m == name:
                self.__write_ym2203(i, address, data)
            elif name == 'YM2413' and m == name:
                self.__write_ym2413(i, address, data)
            elif name == 'YM2608' and m == name:
                if (address & 0x100) == 0:
                    self.__write_ym2608_p0(i, address, data)
                else:
                    self.__write_ym2608_p1(i, address, data)
            elif name == 'YM2612' and m == name:
                if (address & 0x100) == 0:
                    self.__write_ym2612_p0(i, address, data)
                else:
                    self.__write_ym2612_p1(i, address, data)
            elif name == 'YM3526' and m == name:
                self.__write_ym3526(i, address, data)
            elif name == 'YM3812' and m == name:
                self.__write_ym3812(i, address, data)

    def __write_module(self, address, data):
        RPiReController.address(address & 0xff)
        RPiReController.data(data & 0xff)
        RPiReController.write()

    def __write_ay8910(self, slot, address, data):
        self.__write_module(0, address)
        self.__write_module(1, data)

    def __write_oki6258(self, slot, address, data):
        print("OKI6258: {0:X}, {1:X}".format(address, data))

    def __write_sn76489(self, slot, data):
        RPiReController.data(data & 0xff)

        RPiReController.cs0(0)
        RPiReController.wr(0)

        while RPiReController.irq() == 0:
            pass

        RPiReController.cs0(1)
        RPiReController.wr(1)

    def __write_ym2151(self, slot, address, data):
        self.__write_module(0, address)
        self.__write_module(1, data)

    def __write_ym2203(self, slot, address, data):
        self.__write_module(0, address)
        self.__write_module(1, data)

    def __write_ym2413(self, slot, address, data):
        self.__write_module(0, address)
        self.__write_module(1, data)

    def __write_ym2608_p0(self, slot, address, data):
        if self.__ym2608_address_p0 != address:
            self.__write_module(0, address)
            self.__ym2608_address_p0 = address
            self.__ym2608_address_p1 = None
        self.__write_module(1, data)

    def __write_ym2608_p1(self, slot, address, data):
        if self.__ym2608_address_p1 != address:
            self.__write_module(2, address)
            self.__ym2608_address_p0 = None
            self.__ym2608_address_p1 = address
        self.__write_module(3, data)

    def __write_ym2612_p0(self, slot, address, data):
        self.__write_module(0, address)
        self.__write_module(1, data)

    def __write_ym2612_p1(self, slot, address, data):
        self.__write_module(2, address)
        self.__write_module(3, data)

    def __write_ym3526(self, slot, address, data):
        self.__write_module(0, address)
        self.__write_module(1, data)

    def __write_ym3812(self, slot, address, data):
        self.__write_module(0, address)
        self.__write_module(1, data)

    def mute(self):
        RPiReController.reset()

