#!/usr/bin/python

import argparse
import gzip
import signal
import sys
import time

from module_controller import ModuleController
from vgm.vgm import Vgm, VgmError


class VgmPlayer:

    show_gd3 = False

    def __init__(self):
        self.mc = ModuleController()

    @property
    def modules(self):
        return self.mc.modules

    def play(self, f):
        self.f = f

        try:
            self.__play(self.f)
        except VgmError:
            f.seek(0)
            try:
                with gzip.GzipFile(fileobj=self.f, mode='rb') as z:
                    self.__play(z)
            except VgmError as e:
                raise e

    def __play(self, f):
        self.vgm = Vgm(f)
        self.vgm.reset_handlers.append(self.mc.reset)
        self.vgm.write_handlers.append(self.mc.write)
        self.vgm.mute_handlers.append(self.mc.mute)

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

    def stop(self):
        if self.vgm is not None:
            self.vgm.stop()


def break_handler(signal, frame):
    print "Interrupted."
    player.stop()


parser = argparse.ArgumentParser(description='Playback VGM data.')
parser.add_argument("-m", "--module", type=str, help='RE:birth module identifier')
parser.add_argument("-g", "--gd3", action="store_true", help='show GD3 tag')
parser.add_argument("file")
args = parser.parse_args()

player = VgmPlayer()
player.modules[0] = args.module
if args.gd3:
    player.show_gd3 = True

signal.signal(signal.SIGINT, break_handler)

with open(args.file, 'rb') as f:
    player.play(f)

