# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals
import array
import sys
import time

DEVICE_NONE = 0
DEVICE_SSG = 1
DEVICE_OPN = 2
DEVICE_OPN2 = 3
DEVICE_OPNA = 4
DEVICE_OPM = 5
DEVICE_OPLL = 6
DEVICE_OPL = 7
DEVICE_OPL2 = 8
DEVICE_OPL3 = 9
DEVICE_PSG = 15
DEVICE_DCSG = 16

class S98:

    MAGIC = 'S98'.encode('latin-1')
    BOM = [0xef, 0xbb, 0xbf]

    def __init__(self, buffer):
        self.buffer = buffer
        self.playing = False
        self.stopped = True
        self.repeat = False
        self.loop_count = -1
        self.reset_handlers = []
        self.write_handlers = []
        self.mute_handlers = []

        self.__load_header()

    def __load_header(self):

        self.buffer.seek(0)

        # ident
        ident = bytes(self.buffer.read(len(self.MAGIC)))
        if self.MAGIC != ident:
            raise S98Error('Invalid file identification.')

        # header
        self.version = self.read_int8(self.buffer)

        self.timer_info = self.read_int32(self.buffer)
        if self.timer_info == 0:
            self.timer_info = 10
        self.timer_info2 = self.read_int32(self.buffer)
        if self.timer_info2 == 0:
            self.timer_info2 = 1000
        self.resolution = self.timer_info2 / self.timer_info

        self.comressing = self.read_int32(self.buffer)
        self.file_offset_tag = self.read_int32(self.buffer)
        self.file_offset_dump_data = self.read_int32(self.buffer)
        self.file_offset_loop_point = self.read_int32(self.buffer)
        self.device_count = self.read_int32(self.buffer)
        self.device_info = []
        if self.device_count == 0:
            self.device_info.append({
                "device_type": 4,
                "clock": 7987200,
                "pan": 0,
                "num": 0
            })
            self.device_count = 1
        else:
            if self.device_count > 64:
                raise S98Error('Device count must be less than 64.')
            for i in range(self.device_count):
                d = {
                    "device_type": self.read_int32(self.buffer),
                    "clock": self.read_int32(self.buffer),
                    "pan": self.read_int32(self.buffer),
                }
                c = 0
                for j in self.device_info:
                    if j["device_type"] == d["device_type"]:
                        c += 1
                        break 
                d["num"] = c
                self.device_info.append(d)
                self.read_int32(self.buffer)

        # tag
        if self.file_offset_tag != 0:
            self.buffer.seek(self.file_offset_tag)
            bom_test = self.buffer.read(3)
            if bom_test == self.BOM:
                # UTF-8
                # print("utf-8")
                tag_data = bytearray()
                while True:
                    b = self.buffer.read(1)
                    if b is None or b == str('\0'):
                        break
                    tag_data.append(b)
                self.tag = tag_data
            else:
                # Shift JIS
                # print("Shift JIS")
                self.buffer.seek(self.file_offset_tag)
                tag_data = bytearray()
                while True:
                    b = self.buffer.read(1)
                    if b is None or b == str('\0'):
                        break
                    tag_data.append(b)
                self.tag = tag_data.decode('sjis')
        else:
            self.tag = None

        # Dump data
        self.buffer.seek(self.file_offset_dump_data)

    def play(self):
        self.__samples = 0

        self.__fire_reset()

        self.__origin_time = time.time() + 0.5
        opna_adpcm_ctrl1 = 0

        self.playing = True
        self.stopped = False
        while self.playing:
            command = self.read_int8(self.buffer)
            # print("Command {0:X} found.".format(command))

            if command == 0xff:
                self.__wait_samples(1)
            elif command == 0xfe:
                s = 0
                n = 0
                c = True
                while c:
                    p = self.read_int8(self.buffer)
                    n |= (p & 0x7f) << s
                    s += 7
                    c = (p & 0x80) != 0
                self.__wait_samples(n+2)
            elif command == 0xfd:
                if self.file_offset_loop_point == 0:
                    self.playing = False
                elif self.repeat:
                    self.buffer.seek(self.file_offset_loop_point)
                elif self.loop_count != 1:
                    if self.loop_count > 1:
                        self.loop_count -= 1
                    self.buffer.seek(self.file_offset_loop_point)
                else:
                    self.playing = False
            else:
                device_num = (command >> 1) & 0x7f
                # print("{0}, {1}".format(device_num, self.device_count))
                if device_num >= self.device_count:
                    raise S98Error("Invalid device number: {0}".format(device_num))
                extend = command & 1
                address = self.read_int8(self.buffer)
                data = self.read_int8(self.buffer)

                device_info = self.device_info[device_num]
                device_type = device_info['device_type']
                num = device_info['num']
                if device_type == DEVICE_NONE:
                    pass
                elif device_type == DEVICE_OPN:
                    if extend == 0:
                        self.__fire_write('YM2203', num, address, data)
                elif device_type == DEVICE_OPNA:
                    if extend == 0:
                        self.__fire_write('YM2608', num, address, data)
                    else:
                        self.__fire_write('YM2608', num, address | 0x100, data)
                        if address == 0:
                            opna_adpcm_ctrl1 = data
                        if opna_adpcm_ctrl1 & 0x60 == 0x60:
                            # self.__origin_time += time.time() - t
                            self.__samples = 0
                            self.__origin_time = time.time()
                            continue
                elif device_type == DEVICE_OPM:
                    if extend == 0:
                        self.__fire_write('YM2151', num, address, data)
                else:
                    raise S98Error("Unsupported command: 0x{0:X}".format(command))

            while self.__samples > (time.time()-self.__origin_time)*self.resolution:
                pass

        self.__fire_mute()
        self.playing = False
        self.stopped = True

    def stop(self):
        self.playing = False

    @classmethod
    def read_int32(self, buffer):
        data = bytearray(buffer.read(4))
        if len(data) == 4:
           return data[0] | data[1] << 8 | data[2] << 16 | data[3] << 24
        else:
           raise S98Error("Unexpected EOF.")

    @classmethod
    def read_int16(self, buffer):
        data = bytearray(buffer.read(2))
        if len(data) == 2:
            return data[0] | data[1] << 8
        else:
           raise S98Error("Unexpected EOF.")

    @classmethod
    def read_int8(self, buffer):
        data = bytearray(buffer.read(1))
        if len(data) == 1:
           return data[0]
        else:
           raise S98Error("Unexpected EOF.")

    @classmethod
    def read_string(self, buffer):
        pass

    def __wait_samples(self, samples):
        self.__samples += samples

    def __fire_reset(self):
        for h in self.reset_handlers:
            h()

    def __fire_write(self, name, num, address, data):
        for h in self.write_handlers:
            h(name, num, address, data)

    def __fire_mute(self):
        for h in self.mute_handlers:
            h()


class S98Error(Exception):

    def __init__(self, message):
        self.message = message

