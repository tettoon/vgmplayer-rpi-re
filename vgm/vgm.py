import array
import sys
import time

from gd3 import Gd3, Gd3Error

class Vgm:

    MAGIC = bytearray('Vgm ')

    VGM_DATA_OFFSET_POS = 0x34

    reset_handlers = []
    write_handlers = []
    mute_handlers = []

    is_playing = False

    def __init__(self, buffer):
        self.buffer = buffer
        self.__load_header()
        self.__prepare_processor()

    def __load_header(self):

        self.buffer.seek(0)

        # ident
        ident = bytearray(self.buffer.read(4))
        for (a, b) in zip(self.MAGIC, ident):
            if a != b:
                raise VgmError('Invalid file identification.')

        # header
        self.eof_offset = self.read_int32(self.buffer)
        self.version = self.read_int32(self.buffer)
        self.sn76489_clock = self.read_int32(self.buffer)
        self.ym2413_clock = self.read_int32(self.buffer)
        self.gd3_offset = self.read_int32(self.buffer)
        self.total_samples = self.read_int32(self.buffer)
        self.loop_offset = self.read_int32(self.buffer)
        self.loop_samples = self.read_int32(self.buffer)

        if self.version >= 0x101:
            # self.buffer.seek(0x24)
            self.rate = self.read_int32(self.buffer)

        if self.version >= 0x110:
            # self.buffer.seek(0x28)
            self.sn76489_feedback = self.read_int16(self.buffer)

        if self.version >= 0x151:
            # self.buffer.seek(0x2b)
            self.sn76489_flags = self.read_int8(self.buffer)

        if self.version >= 0x110:
            self.buffer.seek(0x2c)
            self.ym2612_clock = self.read_int32(self.buffer)
            self.ym2151_clock = self.read_int32(self.buffer)

        if self.version >= 0x150:
            self.buffer.seek(self.VGM_DATA_OFFSET_POS)
            self.vgm_data_offset = self.read_int32(self.buffer)
        else:
            self.vgm_data_offset = self.read_int32(0x0000000c)

        if self.version >= 0x151:
            # self.buffer.seek(0x38)
            self.buffer.seek(0x44)
            self.ym2203_clock = self.read_int32(self.buffer)
            self.ym2608_clock = self.read_int32(self.buffer)
            self.ym2610_clock = self.read_int32(self.buffer)
            self.ym3812_clock = self.read_int32(self.buffer)
            self.ym3526_clock = self.read_int32(self.buffer)
            self.y8950_clock = self.read_int32(self.buffer)
            self.ymf262_clock = self.read_int32(self.buffer)
            # self.ymf278b_clock = self.read_int32(self.buffer)
            # self.ymf271_clock = self.read_int32(self.buffer)
            # self.ymz280b_clock = self.read_int32(self.buffer)

            self.buffer.seek(0x74)
            self.ay8910_clock = self.read_int32(self.buffer)
            self.ay_chip_type = self.read_int8(self.buffer)
            self.ay_flags = self.read_int8(self.buffer)
            self.ym2203_ay8910_flags = self.read_int8(self.buffer)
            self.ym2608_ay8910_flags = self.read_int8(self.buffer)

        if self.version >= 0x160:
            self.buffer.seek(0x7c)
            self.volume_modifier = self.read_int8(self.buffer)
            self.buffer.read(1)  # reserved
            self.loop_base = self.read_int8(self.buffer)

        if self.version >= 0x151:
            self.buffer.seek(0x7f)
            self.loop_modifier = self.read_int8(self.buffer)

        if self.version >= 0x161:
            self.buffer.seek(0x80)
            # 

        if self.version >= 0x170:
            self.buffer.seek(0xbc)
            self.extra_header_offset = self.read_int32(self.buffer)

        # GD3 tag
        if self.gd3_offset != 0:
            self.buffer.seek(0x14+self.gd3_offset)
            self.gd3 = Gd3(self.buffer)
        else:
            self.gd3 = None

        # VGM data
        self.buffer.seek(self.VGM_DATA_OFFSET_POS + self.vgm_data_offset)

    def __prepare_processor(self):
        processors = {}

        # processors[0x4f] = self.__process_4f
        # processors[0x50] = self.__process_50
        processors[0x51] = self.__process_51
        processors[0x52] = self.__process_52
        processors[0x53] = self.__process_53
        processors[0x54] = self.__process_54
        processors[0x55] = self.__process_55
        processors[0x56] = self.__process_56
        processors[0x57] = self.__process_57
        # processors[0x58] = self.__process_58
        # processors[0x59] = self.__process_59
        processors[0x5a] = self.__process_5a
        processors[0x5b] = self.__process_5b
        processors[0x5c] = self.__process_5c
        # processors[0x5d] = self.__process_5d
        # processors[0x5e] = self.__process_5e
        # processors[0x5f] = self.__process_5f

        processors[0x61] = self.__process_61
        processors[0x62] = self.__process_62
        processors[0x63] = self.__process_63
        processors[0x64] = self.__process_64
        processors[0x66] = self.__process_66
        processors[0x67] = self.__process_67

        for i in range(0x70, 0x80):
            processors[i] = self.__process_7n

        processors[0x90] = self.__process_90
        processors[0x91] = self.__process_91
        processors[0x92] = self.__process_92
        processors[0x93] = self.__process_93
        processors[0x94] = self.__process_94
        processors[0x95] = self.__process_95

        processors[0xa0] = self.__process_a0

        self.processors = processors

    def play(self):
        self.is_playing = True
        self.__wait_samples_62 = 735
        self.__wait_samples_63 = 882
        self.__samples = 0

        self.__fire_reset()

        self.__origin_time = time.time()

        while self.is_playing:
            command = self.read_int8(self.buffer)
            # print "Command {0:X} found.".format(command)

            processor = None
            if command in self.processors:
                processor = self.processors[command]
                processor(command, self.buffer)
            else:
                if command >= 0x30 and command <=0x3f:
                    self.buffer.read(1)
                elif command >= 0x40 and command <= 0x4e:
                    self.buffer.read(2)
                elif command >= 0x51 and command <= 0x5f:
                    self.buffer.read(2)
                elif command >= 0xa1 and command <= 0xaf:
                    self.buffer.read(2)
                elif command >= 0xb0 and command <= 0xbf:
                    self.buffer.read(2)
                elif command >= 0xc0 and command <= 0xdf:
                    self.buffer.read(3)
                elif command >= 0xe0 and command <= 0xff:
                    self.buffer.read(4)
                else:
                    raise VgmError("Unsupported command: {0:X}".format(command))

        self.__fire_mute()

    def stop(self):
        self.is_playing = False

    @classmethod
    def read_int32(self, buffer):
        data = bytearray(buffer.read(4))
        if len(data) == 4:
           return data[0] | data[1] << 8 | data[2] << 16 | data[3] << 24
        else:
           raise VgmException("Unexpected EOF.")

    @classmethod
    def read_int16(self, buffer):
        data = bytearray(buffer.read(2))
        if len(data) == 2:
            return data[0] | data[1] << 8
        else:
           raise VgmException("Unexpected EOF.")

    @classmethod
    def read_int8(self, buffer):
        data = bytearray(buffer.read(1))
        if len(data) == 1:
           return data[0]
        else:
           raise VgmException("Unexpected EOF.")

    @classmethod
    def read_string(self, buffer):
        pass

    def __wait_samples(self, samples):
        self.__samples += samples
        while self.__samples > (time.time()-self.__origin_time)*44100:
            pass

    def __process_4f(self, command, buffer):
        dd = self.read_int8(buffer)
        # print "Game Gear PSG stereo, write {0:X} to port 0x06".format(dd)
	self.__wait_samples(1)

    def __process_50(self, command, buffer):
        dd = self.read_int8(buffer)
        self.__fire_write('SN76489', 0, data)
	self.__wait_samples(1)

    def __process_51(self, command, buffer):
        address = self.read_int8(buffer)
        data = self.read_int8(buffer)
        self.__fire_write('YM2413', address, data)
	self.__wait_samples(1)

    def __process_52(self, command, buffer):
        address = self.read_int8(buffer)
        data = self.read_int8(buffer)
        self.__fire_write('YM2612', address, data)
	self.__wait_samples(1)

    def __process_53(self, command, buffer):
        address = self.read_int8(buffer)
        data = self.read_int8(buffer)
        self.__fire_write('YM2612', address | 0x100, data)
	self.__wait_samples(1)

    def __process_54(self, command, buffer):
        address = self.read_int8(buffer)
        data = self.read_int8(buffer)
        self.__fire_write('YM2151', address, data)
	self.__wait_samples(1)

    def __process_55(self, command, buffer):
        address = self.read_int8(buffer)
        data = self.read_int8(buffer)
        self.__fire_write('YM2203', address, data)
	self.__wait_samples(1)

    def __process_56(self, command, buffer):
        address = self.read_int8(buffer)
        data = self.read_int8(buffer)
        self.__fire_write('YM2608', address, data)
	self.__wait_samples(1)

    def __process_57(self, command, buffer):
        address = self.read_int8(buffer)
        data = self.read_int8(buffer)
        self.__fire_write('YM2608', address | 0x100, data)
	self.__wait_samples(1)

    def __process_5a(self, command, buffer):
        address = self.read_int8(buffer)
        data = self.read_int8(buffer)
        self.__fire_write('YM3812', address, data)
	self.__wait_samples(1)

    def __process_5b(self, command, buffer):
        address = self.read_int8(buffer)
        data = self.read_int8(buffer)
        self.__fire_write('YM3526', address, data)
	self.__wait_samples(1)

    def __process_5c(self, command, buffer):
        address = self.read_int8(buffer)
        data = self.read_int8(buffer)
        self.__fire_write('Y8950', address, data)
	self.__wait_samples(1)

    def __process_5e(self, command, buffer):
        address = self.read_int8(buffer)
        data = self.read_int8(buffer)
        self.__fire_write('YMF262', address, data)
	self.__wait_samples(1)

    def __process_5f(self, command, buffer):
        address = self.read_int8(buffer)
        data = self.read_int8(buffer)
        self.__fire_write('YMF262', address | 0x100, data)
	self.__wait_samples(1)

    def __process_61(self, command, buffer):
        samples = self.read_int16(buffer)
        self.__wait_samples(samples)

    def __process_62(self, command, buffer):
        self.__wait_samples(self.__wait_samples_62)

    def __process_63(self, command, buffer):
        self.__wait_samples(self.__wait_samples_63)

    def __process_64(self, command, buffer):
        cc = self.read_int8(buffer)
        samples = self.read_int16(buffer)
        if cc == 0x62:
            self.__wait_samples_62 = samples
        elif cc == 0x63:
            self.__wait_samples_63 = samples
        else:
            raise VgmError("Invalid command value on command 0x64: {0:X}".format(cc))

    def __process_66(self, command, buffer):
        self.stop()

    def __process_67(self, command, buffer):
        start_time = time.time()
        buffer.read(1)  # skip 0x66
        type = self.read_int8(buffer)
        size = self.read_int32(buffer)
        # print "type={0:X}, size={1}".format(type, size)
        if type >= 0x80 and type <= 0xbf:
            rom_size = self.read_int32(buffer)
            rom_start = self.read_int32(buffer)
            rom_stop = rom_start + size - 8 - 1
            rom_data = buffer.read(size-8)

            if type == 0x81:
                # YM2608 ADPCM
                start_addr = rom_start >> 2
                stop_addr = rom_stop >> 2
                sys.stdout.write("Writing YM2608 RAM (start=0x{0:X}, stop=0x{1:X})...".format(rom_start, rom_stop))
                sys.stdout.flush()
                self.__fire_write("YM2608", 0x100, 0x00)
                self.__fire_write("YM2608", 0x100, 0x01)
                self.__fire_write("YM2608", 0x101, 0x00)
                self.__fire_write("YM2608", 0x102, start_addr & 0xff)
                self.__fire_write("YM2608", 0x103, (start_addr >> 8) & 0xff)
                self.__fire_write("YM2608", 0x104, stop_addr & 0xff)
                self.__fire_write("YM2608", 0x105, (stop_addr >> 8) & 0xff)
                self.__fire_write("YM2608", 0x10c, 0xff)
                self.__fire_write("YM2608", 0x10d, 0xff)
                self.__fire_write("YM2608", 0x110, 0x1f)
                self.__fire_write("YM2608", 0x100, 0x60)
                for d in array.array('b', rom_data):
                    self.__fire_write("YM2608", 0x108, d)
                self.__fire_write("YM2608", 0x100, 0x00)
                self.__fire_write("YM2608", 0x110, 0x80)
                sys.stdout.write("Done.\n")
                sys.stdout.flush()

            else:
                print "Unsupported chip type: {0:X}".format(type)
        else:
            buffer.read(size)  # skip data

        stop_time = time.time()
        self.__origin_time += stop_time - start_time

    def __process_7n(self, command, buffer):
        self.__wait_samples(command-0x70+1)

    def __process_90(self, command, buffer):
        stream_id = self.read_int8(buffer)
        chip_type = self.read_int8(buffer)
        pp = self.read_int8(buffer)
        cc = self.read_int8(buffer)
        # skip

    def __process_91(self, command, buffer):
        stream_id = self.read_int8(buffer)
        data_bank_id = self.read_int8(buffer)
        step_size = self.read_int8(buffer)
        step_base = self.read_int8(buffer)
        # skip

    def __process_92(self, command, buffer):
        stream_id = self.read_int8(buffer)
        freq = self.read_int32(buffer)
        # skip

    def __process_93(self, command, buffer):
        stream_id = self.read_int8(buffer)
        offset = self.read_int32(buffer)
        length_mode = self.read_int8(buffer)
        length = self.read_int32(buffer)
        # skip

    def __process_94(self, command, buffer):
        stream_id = self.read_int8(buffer)
        # skip

    def __process_95(self, command, buffer):
        stream_id = self.read_int8(buffer)
        block_id = self.read_int16(buffer)
        flags = self.read_int8(buffer)
        # skip

    def __process_a0(self, command, buffer):
        address = self.read_int8(buffer)
        data = self.read_int8(buffer)
        self.__fire_write('AY8910', address, data)
	self.__wait_samples(1)

    def __process_b7(self, command, buffer):
        address = self.read_int8(buffer)
        data = self.read_int8(buffer)
        self.__fire_write('OKI6258', address, data)
	self.__wait_samples(1)

    def __fire_reset(self):
        for h in self.reset_handlers:
            h()

    def __fire_write(self, name, address, data):
        for h in self.write_handlers:
            h(name, address, data)

    def __fire_mute(self):
        for h in self.mute_handlers:
            h()


class VgmError(Exception):

    def __init__(self, message):
        self.message = message

