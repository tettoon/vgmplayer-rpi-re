#!/usr/bin/python

import argparse
import gzip
import signal
import sys

from vgm.vgm import Vgm, VgmError
from rpi_re.rpi_re import RPiReController


class VgmPlayer:

    _modules = {}

    show_gd3 = False

    def __init__(self):
        RPiReController.init()
        RPiReController.reset()

    @property
    def modules(self):
        return self._modules

    def play(self, f):
        try:
            self.__play(f)
        except VgmError:
            f.seek(0)
            try:
                with gzip.GzipFile(fileobj=f, mode='rb') as z:
                    self.__play(z)
            except VgmError as e:
                raise e

    def __play(self, f):

        signal.signal(signal.SIGINT, self.__break_handler)
 
        self.vgm = Vgm(f)
        self.vgm.reset_handlers.append(self.__reset_handler)
        self.vgm.write_handlers.append(self.__write_handler)
        self.vgm.mute_handlers.append(self.__mute_handler)

        gd3 = self.vgm.gd3
        if self.show_gd3 and gd3 is not None:
            print "Track name (en): " + gd3.track_name_en
            print "Track name (ja): " + gd3.track_name_ja
            print "Game name (en): " + gd3.game_name_en
            print "Game name (ja): " + gd3.game_name_ja
            print "System name (en): " + gd3.system_name_en
            print "System name (ja): " + gd3.system_name_ja
            print "Name of Original Track Author (en): " + gd3.original_track_author_en
            print "Name of Original Track Author (ja): " + gd3.original_track_author_ja
            print "Date of game's release: " + gd3.released_at
            print "Name of person who converted it to a VGM file: " + gd3.converted_by
            print "Notes: " + gd3.notes

        self.vgm.play()

    def __break_handler(self, signal, frame):
        self.vgm.stop()

    def __write_module(self, address, data):
        RPiReController.address(address & 0xff)
        RPiReController.data(data & 0xff)
        RPiReController.write()

    def __reset_handler(self):
        RPiReController.reset()
        if self.modules[0] == 'YM2608':
            self.__write_module(0, 0x29)
            self.__write_module(1, 0x80)

    def __write_handler(self, name, address, data):
        if name == 'AY8910' and self.modules[0] == name:
            self.__write_module(0, address)
            self.__write_module(1, data)

        elif name == 'YM2413' and self.modules[0] == name:
            self.__write_module(0, address)
            self.__write_module(1, data)

        elif name == 'YM2151' and self.modules[0] == name:
            self.__write_module(0, address)
            self.__write_module(1, data)

        elif name == 'YM2608' and self.modules[0] == name:
            if (address & 0x100) == 0:
                self.__write_module(0, address)
                self.__write_module(1, data)
            else:
                self.__write_module(2, address)
                self.__write_module(3, data)

    def __mute_handler(self):
        RPiReController.reset()


parser = argparse.ArgumentParser(description='Playback VGM data.')
parser.add_argument("-m", "--module", type=str, help='RE:birth module identifier')
parser.add_argument("-g", "--gd3", action="store_true", help='show GD3 tag')
parser.add_argument("file")
args = parser.parse_args()

player = VgmPlayer()
player.modules[0] = args.module
if args.gd3:
    player.show_gd3 = True

with open(args.file, 'rb') as f:
    player.play(f)

