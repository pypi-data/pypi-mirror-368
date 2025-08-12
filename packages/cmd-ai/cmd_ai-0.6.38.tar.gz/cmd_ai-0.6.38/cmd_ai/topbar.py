#!/usr/bin/env python3

# from {proj}.version import __version__
import datetime as dt
import threading  # for key input
import time

import pytermgui
from console import bg, fg, fx
from fire import Fire
from pytermgui import (bold, cursor_up, inverse, italic, move_cursor, print_to,
                       report_cursor, restore_cursor, save_cursor, terminal,
                       underline)

theight = terminal.height
twidth = terminal.width

global_mode = " "


class Topbar:
    def __init__(self, pos=1, bgcolor=bg.blue):
        self.pos = pos
        self.positions = {}
        self.t2 = None
        if pos == 1:
            self.BCOL = bgcolor  # bg.blue
        elif pos == 2:
            self.BCOL = bgcolor  # bg.white
        # self.t = threading.currentThread()

        try:
            # print("report_cursor to appear")
            print("i... topbar: pos/cursor", pos, report_cursor())
            # print("report done")
        except:
            print("X... problem with report_cursor")

        # print("i... topbar bar started")

    def add(self, two=2, bgcolor=bg.blue):
        if two == 2:
            self.t2 = Topbar(two, bgcolor=bgcolor)
        else:
            print("X... nobody wanted more than two......  NOT OK")
        return self.t2

    def print_to(self, tup, s):
        if type(tup) is tuple:
            x, y = tup[0], tup[1]
            print("X.......... TUPLE in the TOPBAR  IS SUPRESSED")
        elif type(tup) is int:
            x = tup
            y = 1
        else:
            print(
                "X... NOBODY WANTED something else than tuple or int in the TOPBAR  position"
            )
        self.positions[x] = s

    def place(self):
        """
        Place he BAR on screen
        """
        curs = (-1, -1)
        if self.pos == 1:
            save_cursor()
        print_to((1, self.pos), f"{self.BCOL}" + " " * twidth + bg.default)
        print_to((1, self.pos + 1), " " * twidth)

        ###### self.positions[ twidth] = f"{fx.default}{fg.default}{bg.default}"

        for k in self.positions.keys():
            print_to(
                (k, self.pos),
                f"{self.BCOL}{self.positions[k]}{bg.default}{fx.default}{fg.default}",
            )

        if self.t2 is not None:
            self.t2.place()

        if self.pos == 1:
            restore_cursor()
            print("", end="\r")  # this make GOOD thing in printing


def main():
    # print()
    t = Topbar(1)
    for i in range(100):
        #
        # DO whatever stuff and PLACE PRINTTO SLEEP
        #
        t.place()
        t.print_to((1, 1), f"{fg.white} {str(dt.datetime.now())[:-4]} {fg.default}")
        time.sleep(0.1)


if __name__ == "__main__":
    Fire(main)
