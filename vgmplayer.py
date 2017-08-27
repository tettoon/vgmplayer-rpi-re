#!/usr/bin/python

import gzip
import argparse
import sys

from vgm.vgm import Vgm, VgmError
from rpi_re.rpi_re import RPiReController


class VgmPlayer:

    def __init__(self):
        RPiReController.init()
        RPiReController.reset()

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

    def __write_handler(self, name, address, data):
        if name == 'AY8910':
            RPiReController.address(0)
            RPiReController.data(address)
            RPiReController.write()

            RPiReController.address(1)
            RPiReController.data(data)
            RPiReController.write()

        elif name == 'YM2151':
            RPiReController.address(0)
            RPiReController.data(address)
            RPiReController.write()

            RPiReController.address(1)
            RPiReController.data(data)
            RPiReController.write()

    def __mute_handler(self):
        RPiReController.reset()


with open(sys.argv[1], 'rb') as f:
    player = VgmPlayer()
    player.play(f)

