from __future__ import division, print_function, unicode_literals


class ModuleInfo:
    """
    Modules information.
    """

    MODULES = []

    def __init__(self, id, name):
        self.id = id
        self.name = name

    @classmethod
    def find(self, name):
        for m in self.MODULES:
            if m.name == name:
                return m
        return None


ModuleInfo.SN76489 = ModuleInfo(0x50, "SN76489")
ModuleInfo.YM2413 = ModuleInfo(0x51, "YM2413")
ModuleInfo.YM2612 = ModuleInfo(0x52, "YM2612")
ModuleInfo.YM2151 = ModuleInfo(0x54, "YM2151")
ModuleInfo.YM2203 = ModuleInfo(0x55, "YM2203")
ModuleInfo.YM2608 = ModuleInfo(0x56, "YM2608")
ModuleInfo.YM3812 = ModuleInfo(0x5a, "YM3812")
ModuleInfo.YM3526 = ModuleInfo(0x5b, "YM3526")
ModuleInfo.Y8950 = ModuleInfo(0x5c, "Y8950")
ModuleInfo.AY8910 = ModuleInfo(0xa0, "AY8910")
ModuleInfo.OKIM6258 = ModuleInfo(0xb7, "OKIM6258")
ModuleInfo.MODULES.extend([
    ModuleInfo.SN76489,
    ModuleInfo.YM2413,
    ModuleInfo.YM2612,
    ModuleInfo.YM2151,
    ModuleInfo.YM2203,
    ModuleInfo.YM2608,
    ModuleInfo.YM3812,
    ModuleInfo.YM3526,
    ModuleInfo.Y8950,
    ModuleInfo.AY8910,
    ModuleInfo.OKIM6258
])

