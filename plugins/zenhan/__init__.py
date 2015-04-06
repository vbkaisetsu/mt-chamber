# -*- coding: utf-8 -*-

__version__ = '0.5.2'
ASCII = 1
DIGIT = 2
KANA  = 4
ALL = ASCII | DIGIT | KANA

class _Converter(object):

    def __init__(self):
        self.zh_ascii = dict(zip(self.z_ascii, self.h_ascii))
        self.hz_ascii = dict(zip(self.h_ascii, self.z_ascii))

        self.zh_digit = dict(zip(self.z_digit, self.h_digit))
        self.hz_digit = dict(zip(self.h_digit, self.z_digit))

        self.zh_kana = dict(zip(self.z_kana, self.h_kana))
        self.hz_kana = dict(zip(self.h_kana, self.z_kana))

    def _is_valid_mode(self, mode):
        if isinstance(mode, int) and 0 <= mode <= 7:
            return True
        else:
            return False

    def _make_zen2han_dict(self, mode):
        d = {}

        if mode >= 4:
            d.update(self.zh_kana)
            mode = mode - 4

        if mode >= 2:
            d.update(self.zh_digit)
            mode = mode - 2

        if mode:
            d.update(self.zh_ascii)

        return d

    def _make_han2zen_dict(self, mode):
        d = {}

        if mode >= 4:
            d.update(self.hz_kana)
            mode = mode - 4

        if mode >= 2:
            d.update(self.hz_digit)
            mode = mode - 2

        if mode:
            d.update(self.hz_ascii)

        return d


    def zen2han(text, mode, ignore):
        pass

    def han2zen(text, mode, ignore):
        pass

import sys

if sys.version_info >= (3, 0):
    from . import converter3
    converter = converter3.Converter()
elif sys.version_info >= (2, 0):
    from . import converter2
    converter = converter2.Converter()
else:
    sys.exit('Use Python 2 or 3')


def z2h(text, mode = ALL, ignore = ()):
    return converter.zen2han(text, mode, ignore)

def h2z(text, mode = ALL, ignore=()):
    return converter.han2zen(text, mode, ignore)


