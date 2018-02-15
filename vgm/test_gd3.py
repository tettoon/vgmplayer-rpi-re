# -*- coding: utf8 -*-
from __future__ import division, print_function, unicode_literals

from io import BytesIO
from gd3 import Gd3, Gd3Error
import unittest

GD3_ENCODING = 'utf-16'

class TestGd3(unittest.TestCase):

    def __write_int32(self, buffer, value):
        data = bytearray()
        data.append(value & 0xff)
        data.append((value >> 8) & 0xff)
        data.append((value >> 16) & 0xff)
        data.append((value >> 24) & 0xff)
        return buffer.write(data)

    def __write_string(self, buffer, value):
        data = bytearray((value+"\0").encode(GD3_ENCODING))
        return buffer.write(data)

    def create_data(self):
        tag = BytesIO()
        self.__write_string(tag, "Track Name")
        self.__write_string(tag, "トラック名")
        self.__write_string(tag, "Game Name")
        self.__write_string(tag, "ゲーム名")
        self.__write_string(tag, "System Name")
        self.__write_string(tag, "システム名")
        self.__write_string(tag, "Original Track Author")
        self.__write_string(tag, "作曲者")
        self.__write_string(tag, "2017/02/01")
        self.__write_string(tag, "John Doe")
        self.__write_string(tag, "This is a test data!")
        tag_data = tag.getvalue()

        data = BytesIO()
        data.write("\0\0\0\0".encode('latin-1'))  # padding (dummy)
        data.write("Gd3 ".encode('latin-1'))
        self.__write_int32(data, 0x1234)  # version
        self.__write_int32(data, len(tag_data))  # size
        data.write(tag_data)

        data.seek(4)  # skip padding data
        return data

    def test_init_ok(self):
        data = self.create_data()

        testee = Gd3(data)
        self.assertEqual(testee.track_name_en, "Track Name")
        self.assertEqual(testee.track_name_ja, "トラック名")
        self.assertEqual(testee.game_name_en, "Game Name")
        self.assertEqual(testee.game_name_ja, "ゲーム名")
        self.assertEqual(testee.system_name_en, "System Name")
        self.assertEqual(testee.system_name_ja, "システム名")
        self.assertEqual(testee.original_track_author_en, "Original Track Author")
        self.assertEqual(testee.original_track_author_ja, "作曲者")
        self.assertEqual(testee.released_at, "2017/02/01")
        self.assertEqual(testee.converted_by, "John Doe")
        self.assertEqual(testee.notes, "This is a test data!")

    def test_init_error(self):
        data = BytesIO()
        data.write("\0\0\0\0".encode('latin-1'))
        data.seek(0)

        with self.assertRaises(Gd3Error) as cm:
            testee = Gd3(data)
        e = cm.exception
        self.assertEqual(e.message, "Invalid GD3 identifier.")

if __name__ == '__main__':
    unittest.main()
