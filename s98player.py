#!/usr/bin/env python

from __future__ import division, print_function, unicode_literals
import argparse
import io
import os
import signal
import sys
import time

from module_controller import ModuleInfo, ModuleController
from m3u import M3U
from s98.s98 import S98, S98Error


class S98Player:

    def __init__(self):
        self.mc = ModuleController()
        self.playlist = False
        self.show_tag = False
        self.cancel = False
        self.repeat = False
        self.loop_count = -1

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
            self.__play_s98(data)

    def __play_s98(self, f):
        self.s98 = S98(f)
        self.s98.reset_handlers.append(self.mc.reset)
        self.s98.write_handlers.append(self.mc.write)
        self.s98.mute_handlers.append(self.mc.mute)
        self.s98.repeat = self.repeat
        self.s98.loop_count = self.loop_count

        # tag = self.s98.tag
        if self.show_tag == True and self.s98.tag is not None:
            print(self.s98.tag)
            pass

        self.s98.play()

    def __playlist(self, filename):
        self.playlist = M3U(filename)
        while not self.cancel:
            for file in self.playlist.files:
                if self.cancel:
                    break
                print(file)
                self.__play(file)

    def stop(self):
        if self.s98 is not None and self.s98.playing:
            self.s98.stop()
            while self.s98.playing and not self.s98.stopped:
                pass
            del self.s98
            self.cancel = True


def break_handler(signal, frame):
    print("Interrupted.")
    player.stop()


parser = argparse.ArgumentParser(description='Playback S98 data.')
parser.add_argument("-t", "--tag", action="store_true", help='show tag')
parser.add_argument("-l", "--list", action="store_true", help='load M3U playlist')
parser.add_argument("-m", "--module", type=str, help='RE:birth module identifier')
parser.add_argument("-r", "--repeat", type=int, help='Repeat song')
parser.add_argument("file", type=str, help="S98 file")
args = parser.parse_args()

signal.signal(signal.SIGINT, break_handler)

player = S98Player()
for i, m in enumerate(args.module.split(",")):
    player.modules.append(ModuleInfo.find(m))
if args.tag:
    player.show_tag = True
if args.list:
    player.playlist = True
if args.repeat != None:
    if args.repeat > 0:
        player.loop_count = args.repeat
    else:
        player.repeat = True

player.play(args.file)

