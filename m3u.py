from __future__ import division, print_function, unicode_literals
import os
import re
import sys


class M3U:

    def __init__(self, filename):
        self.extm3u = False
        self.dir = os.path.dirname(filename)
        self.files = []

        with open(filename, 'r') as f:
            blank_pattern = re.compile("^\s*$")
            comment_pattern = re.compile('^\s*#')
            extm3u = False
            line_no = 0
            n = 0
            for line in f:
                line = line.strip("\r\n")
                if line_no == 0 and line == '#EXTM3U':
                    this.extm3u = True
                elif blank_pattern.match(line):
                    pass
                elif comment_pattern.match(line):
                    pass
                else:
                    file = os.path.join(self.dir, line)
                    self.files.append(file)
                line_no += 1

