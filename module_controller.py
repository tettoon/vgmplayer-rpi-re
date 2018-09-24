from __future__ import division, print_function, unicode_literals
import time

from rpi_re.rpi_re import RPiReController
from module_info import ModuleInfo


class ModuleController:

    def __init__(self):
        self.modules = []
        self.__ym2608_address_p0 = None
        self.__ym2608_address_p1 = None

        RPiReController.init()
        self.reset()

    def find_module_info(self, name, num=0):
        count = 0
        for i, m in enumerate(ModuleInfo.MODULES):
            if m.name == name:
                if i == num:
                    return m
                else:
                    count += 1
        return None

    def __find_slot(self, name, num=0):
        c = 0
        for i, m in enumerate(self.modules):
            if not m is None and m.name == name:
                if c == num:
                    return i
                c += 1

    def reset(self):
        RPiReController.reset(microseconds=1000)
         
        for i, m in enumerate(self.modules):
            # Module Initialization
            if m == ModuleInfo.YM2608:
                self.__write_ym2608_p0(i, 0x29, 0x80)

            self.mute()

    def write(self, name, num, address, data):
        slot = self.__find_slot(name, num)
        if slot is None:
            return

        if name == ModuleInfo.AY8910.name:
            self.__write_ay8910(slot, address, data)
        elif name == ModuleInfo.SN76489.name:
            self.__write_sn76489(slot, data)
        elif name == ModuleInfo.YM2151.name:
            self.__write_ym2151(slot, address, data)
        elif name == ModuleInfo.YM2203.name:
            self.__write_ym2203(slot, address, data)
        elif name == ModuleInfo.YM2413.name:
            self.__write_ym2413(slot, address, data)
        elif name == ModuleInfo.YM2608.name:
            if (address & 0x100) == 0:
                self.__write_ym2608_p0(slot, address, data)
            else:
                self.__write_ym2608_p1(slot, address, data)
        elif name == ModuleInfo.YM2612.name:
            if (address & 0x100) == 0:
                self.__write_ym2612_p0(slot, address, data)
            else:
                self.__write_ym2612_p1(slot, address, data)
        elif name == ModuleInfo.YM3526.name:
            self.__write_ym3526(slot, address, data)
        elif name == ModuleInfo.YM3812.name:
            self.__write_ym3812(slot, address, data)

    def __write_module(self, slot, address, data):
        if slot == 0:
            RPiReController.cs0(0)
        elif slot == 1:
            RPiReController.cs0(1)
        else:
            return

        RPiReController.address(address & 0xff)
        RPiReController.data(data & 0xff)
        RPiReController.wr(0)
        RPiReController.wr(1)

    def __write_ay8910(self, slot, address, data):
        self.__write_module(slot, 0, address)
        self.__write_module(slot, 1, data)

    def __write_sn76489(self, slot, data):
        if slot >= 2:
            return

        while RPiReController.irq() == 0:
            pass

        RPiReController.address(0)
        RPiReController.data(data & 0xff)

        if slot == 0:
            RPiReController.cs0(0)
        else:
            RPiReController.cs0(1)

        RPiReController.wr(0)
        time.sleep(0.00001)
        RPiReController.wr(1)

        if slot == 0:
            RPiReController.cs0(1)
        else:
            RPiReController.cs0(0)

        time.sleep(0.00002)

    def __write_ym2151(self, slot, address, data):
        self.__write_module(slot, 0, address)
        self.__write_module(slot, 1, data)

    def __write_ym2203(self, slot, address, data):
        self.__write_module(slot, 0, address)
        self.__write_module(slot, 1, data)

    def __write_ym2413(self, slot, address, data):
        self.__write_module(slot, 0, address)
        self.__write_module(slot, 1, data)

    def __write_ym2608_p0(self, slot, address, data):
        if self.__ym2608_address_p0 != address:
            self.__write_module(slot, 0, address)
            self.__ym2608_address_p0 = address
            self.__ym2608_address_p1 = None
        self.__write_module(slot, 1, data)

    def __write_ym2608_p1(self, slot, address, data):
        if self.__ym2608_address_p1 != address:
            self.__write_module(slot, 2, address)
            self.__ym2608_address_p0 = None
            self.__ym2608_address_p1 = address
        self.__write_module(slot, 3, data)

    def __write_ym2612_p0(self, slot, address, data):
        self.__write_module(slot, 0, address)
        self.__write_module(slot, 1, data)

    def __write_ym2612_p1(self, slot, address, data):
        self.__write_module(slot, 2, address)
        self.__write_module(slot, 3, data)

    def __write_ym3526(self, slot, address, data):
        self.__write_module(slot, 0, address)
        self.__write_module(slot, 1, data)

    def __write_ym3812(self, slot, address, data):
        self.__write_module(slot, 0, address)
        self.__write_module(slot, 1, data)

    def mute(self):
        for i, m in enumerate(self.modules):
            self.__mute(i, m)

    def __mute(self, slot, module):
        if module == ModuleInfo.AY8910:
            self.__write_ay8910(slot, 0x7, 0x3f)
        elif module == ModuleInfo.SN76489:
            self.__write_sn76489(slot, 0x9f)
            self.__write_sn76489(slot, 0xbf)
            self.__write_sn76489(slot, 0xdf)
            self.__write_sn76489(slot, 0xff)
        elif module == ModuleInfo.YM2151:
            for d in range(8):
                self.__write_ym2151(slot, 0x08, d)
        elif module == ModuleInfo.YM2203:
            self.__write_ym2203(slot, 0x07, 0x3f)
            for d in [0, 1, 2]:
                self.__write_ym2203(slot, 0x28, d)
        elif module == ModuleInfo.YM2413:
            for r in range(9):
                self.__write_ym2413(slot, 0x20+r, 0)
        elif module == ModuleInfo.YM2608:
            self.__write_ym2608_p0(slot, 0x7, 0x3f)
            self.__write_ym2608_p0(slot, 0x11, 0)
            for d in [0, 1, 2, 4, 5, 6]:
                self.__write_ym2608_p0(slot, 0x28, d)
            self.__write_ym2608_p1(slot, 0x0b, 0)
        elif module == ModuleInfo.YM2612:
            for d in [0, 1, 2, 4, 5, 6]:
                self.__write_ym2612_p0(slot, 0x28, d)
        elif module == ModuleInfo.YM3526:
            for r in range(9):
                self.__write_ym3526(slot, 0xb0+r, 0)
        elif module == ModuleInfo.YM3812:
            for r in range(9):
                self.__write_ym3812(slot, 0xb0+r, 0)

