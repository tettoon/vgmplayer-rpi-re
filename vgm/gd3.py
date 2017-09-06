from __future__ import unicode_literals

class Gd3:

    MAGIC = bytearray('Gd3 ', 'latin-1')

    def __init__(self, buffer):
        ident = bytearray(buffer.read(4))
        for (a, b) in zip(self.MAGIC, ident):
            if a != b:
                raise Gd3Error('Invalid GD3 identifier.')

        self.version = self.__read_int32(buffer)
        self.size = self.__read_int32(buffer)

        self.track_name_en = self.__read_string(buffer)
        self.track_name_ja = self.__read_string(buffer)
        self.game_name_en = self.__read_string(buffer)
        self.game_name_ja = self.__read_string(buffer)
        self.system_name_en = self.__read_string(buffer)
        self.system_name_ja = self.__read_string(buffer)
        self.original_track_author_en = self.__read_string(buffer)
        self.original_track_author_ja = self.__read_string(buffer)
        self.released_at = self.__read_string(buffer)
        self.converted_by = self.__read_string(buffer)
        self.notes = self.__read_string(buffer)

    def __read_int32(self, buffer):
        data = bytearray(buffer.read(4))
        return data[0] | (data[1] << 8) | (data[2] << 16) | (data[3] << 24)

    def __read_string(self, buffer):
        b = bytearray()
        while True:
            data = bytearray(buffer.read(2))
            c = data[0] | (data[1] << 8)
            if c == 0:
                break
            b.extend(data)
        return b.decode('utf-16')


class Gd3Error(Exception):

    def __init__(self, message):
        self.message = message

