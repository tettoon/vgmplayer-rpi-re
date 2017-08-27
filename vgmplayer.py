#!/usr/bin/python

import gzip
import argparse
import sys

from vgm.vgm import Vgm, VgmError
from rpi_re.rpi_re import RPiReController


class VgmPlayer:

    _modules = {}

    def __init__(self):
        RPiReController.init()
        RPiReController.reset()

    @property
    def modules(self):
        return self._modules

    def play(self, f):
        vgm = None
        try:
            vgm = Vgm(f)
            self.__play(vgm)
        except VgmError:
            try:
                f.seek(0)
                with gzip.GzipFile(fileobj=f, mode='rb') as z:
                    vgm = Vgm(z)
                    self.__play(vgm)
            except VgmError as e:
                print e.message
                raise e

    def __play(self, vgm):
        vgm.reset_handlers.append(self.__reset_handler)
        vgm.write_handlers.append(self.__write_handler)
        vgm.mute_handlers.append(self.__mute_handler)
        vgm.play()

    def __reset_handler(self):
        RPiReController.reset()
        if self.modules[0] == 'YM2608':
            RPiReController.address(0)
            RPiReController.data(0x29)
            RPiReController.write()

            RPiReController.address(1)
            RPiReController.data(0x80)
            RPiReController.write()

    def __write_handler(self, name, address, data):
        if name == 'AY8910' and self.modules[0] == name:
            RPiReController.address(0)
            RPiReController.data(address)
            RPiReController.write()

            RPiReController.address(1)
            RPiReController.data(data)
            RPiReController.write()

        elif name == 'YM2151' and self.modules[0] == name:
            RPiReController.address(0)
            RPiReController.data(address)
            RPiReController.write()

            RPiReController.address(1)
            RPiReController.data(data)
            RPiReController.write()

        elif name == 'YM2608_p0' and self.modules[0] == name[0:6]:
            RPiReController.address(0)
            RPiReController.data(address)
            RPiReController.write()

            RPiReController.address(1)
            RPiReController.data(data)
            RPiReController.write()

        elif name == 'YM2608_p1' and self.modules[0] == name[0:6]:
            RPiReController.address(2)
            RPiReController.data(address)
            RPiReController.write()

            RPiReController.address(3)
            RPiReController.data(data)
            RPiReController.write()

        elif False and name[0:6] == 'YM2608' and self.modules[0] == name[0:6]:
            a1 = (address & 0x100) != 0
            # a1 = True
            if not a1:
                RPiReController.address(0)
                RPiReController.data(address & 0xff)
                RPiReController.write()

                RPiReController.address(1)
                RPiReController.data(data)
                RPiReController.write()

            else:
                RPiReController.address(2)
                RPiReController.data(address & 0xff)
                RPiReController.write()

                RPiReController.address(3)
                RPiReController.data(data)
                RPiReController.write()

    def __mute_handler(self):
        RPiReController.reset()


parser = argparse.ArgumentParser(description='Playback VGM data.')
parser.add_argument("-m", "--module", type=str, help='Present RE:birth module identifier.')
parser.add_argument("file")
args = parser.parse_args()


with open(args.file, 'rb') as f:
    player = VgmPlayer()
    player.modules[0] = args.module
    player.play(f)


