#!/usr/bin/python

from __future__ import division, print_function, unicode_literals
import argparse
import gc
import gzip
import io
import os
import signal
import sys
import time

from module_controller import ModuleController
from m3u import M3U
from vgm.vgm import Vgm, VgmError


class VgmPlayer:

    playlist = False
    show_gd3 = False
    cancel = False

    def __init__(self):
        self.mc = ModuleController()

    @property
    def modules(self):
        return self.mc.modules

    def play(self, filename):
        if self.playlist:
            self.__playlist(filename)
        else:
            self.__play(filename)

    def __play(self, filename):
        file_bytes = None

        with io.FileIO(filename, 'rb') as f:
            file_bytes = f.readall()

        with io.BytesIO(file_bytes) as data:
            try:
                self.__play_vgm(data)
            except VgmError:
                data.seek(0)
                with gzip.GzipFile(fileobj=data, mode='rb') as dataz:
                    self.__play_vgm(dataz)

    def __play_vgm(self, f):
        self.vgm = Vgm(f)
        self.vgm.reset_handlers.append(self.mc.reset)
        self.vgm.write_handlers.append(self.mc.write)
        self.vgm.mute_handlers.append(self.mc.mute)

        gd3 = self.vgm.gd3
        if self.show_gd3 and gd3 is not None:
            print("")
            print("Track name (en): " + gd3.track_name_en)
            print("Track name (ja): " + gd3.track_name_ja)
            print("Game name (en): " + gd3.game_name_en)
            print("Game name (ja): " + gd3.game_name_ja)
            print("System name (en): " + gd3.system_name_en)
            print("System name (ja): " + gd3.system_name_ja)
            print("Name of Original Track Author (en): " + gd3.original_track_author_en)
            print("Name of Original Track Author (ja): " + gd3.original_track_author_ja)
            print("Date of game's release: " + gd3.released_at)
            print("Name of person who converted it to a VGM file: " + gd3.converted_by)
            print("Notes: " + gd3.notes)

        self.vgm.play()

    def __playlist(self, filename):
        self.playlist = M3U(filename)
        while not self.cancel:
            for file in self.playlist.files:
                if self.cancel:
                    break
                self.__play(file)

    def stop(self):
        if self.vgm is not None and self.vgm.playing:
            self.vgm.stop()
            while self.vgm.playing and not self.vgm.stopped:
                pass
            del self.vgm
            gc.collect()
            self.cancel = True


def break_handler(signal, frame):
    print("Interrupted.")
    player.stop()


gc.enable()

parser = argparse.ArgumentParser(description='Playback VGM data.')
parser.add_argument("-g", "--gd3", action="store_true", help='show GD3 tag')
parser.add_argument("-l", "--list", action="store_true", help='load M3U playlist')
parser.add_argument("-m", "--module", type=str, help='RE:birth module identifier')
parser.add_argument("file", type=str, help="VGM file")
args = parser.parse_args()

signal.signal(signal.SIGINT, break_handler)

player = VgmPlayer()
player.modules[0] = args.module
if args.gd3:
    player.show_gd3 = True
if args.list:
    player.playlist = True

player.play(args.file)

