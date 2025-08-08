# -*- coding: utf-8 -*-
from sys import platform


def return_platform():
    if platform == "linux" or platform == "linux2":
        return 'linux'
    elif platform == "win32":
        return 'windows'
    else:
        return 'other platform'
