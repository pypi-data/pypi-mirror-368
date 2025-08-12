#!/usr/bin/env python3

# from {proj}.version import __version__
import threading
import time

from console import bg, fg, fx
from fire import Fire
# import readchar
from sshkeyboard import listen_keyboard, stop_listening

global_key = ""


def get_global_key():
    global global_key
    a = global_key
    # global_key = ""
    return a


# https://sshkeyboard.readthedocs.io/en/latest/reference.html#sshkeyboard.listen_keyboard_manual
# https://github.com/ollipal/sshkeyboard


class KeyboardThreadSsh(threading.Thread):
    def __init__(self, name="keyboard-input-thread", ending=None):
        """
        Restart itself as thread
        """
        self.block = False
        self.ending = ending
        self.cursor = 0

        self.history = {}  # dict with past commands
        self.history_pointer = 0
        super(KeyboardThreadSsh, self).__init__(name=name)
        self.start()

    def text_split(self):
        """
        operates on global_key and cursor, returns 3 parts
        0 is before 1.st letter
        """
        global global_key
        a, b, c = "", "", ""
        lel = len(global_key)

        cursor = self.cursor

        if cursor > lel:
            cursor = lel
        if cursor < 0:
            cursor = 0

        if lel == 0:
            return a, b

        #  a b c
        # 0 1 2 3
        if cursor == lel:
            a = global_key
            return a, b

        if cursor == 0:
            b = global_key
            return a, b

        if cursor == 1:
            a = global_key[0]
            b = global_key[1:]
            return a, b
        else:
            a = global_key[:cursor]
            b = global_key[cursor:]
        return a, b

    def press(self, key):
        """
        the callback - uses the global_key to remember
        """
        global global_key
        # print("D...", f"'{key}' pressed")
        # print("D...", f"{global_key} , cu=={self.cursor} :", self.text_split() )

        # the tricks: space up down
        if key == "space":
            key = " "
            # self.cursor+=1 # not here ...
        elif key == "delete":
            if self.cursor <= len(global_key):
                global_key = global_key[: self.cursor] + global_key[self.cursor + 1 :]
            key = ""
        elif key == "backspace":
            global_key = global_key[: self.cursor - 1] + global_key[self.cursor :]
            self.cursor -= 1
            key = ""
        elif key == "end":
            self.cursor = len(global_key)
            key = ""
        elif key == "home":
            self.cursor = 0
            key = ""
        elif key == "left":
            self.cursor -= 1
            key = ""
        elif key == "right":
            self.cursor += 1
            key = ""
        elif key == "enter":
            key = "\n"
            self.cursor = len(global_key)  # there is a reason
            n = len(self.history)
            self.history[n] = global_key
            self.history_pointer = n + 1
            print(self.history, self.history_pointer)
        elif key == "up":
            key = ""
            if self.history_pointer > 0:
                self.history_pointer -= 1
                global_key = self.history[self.history_pointer]
                self.cursor = len(global_key)
        elif key == "down":
            key = ""
            if self.history_pointer < len(self.history) - 1:
                self.history_pointer += 1
                global_key = self.history[self.history_pointer]
                self.cursor = len(global_key)
            elif self.history_pointer == len(self.history) - 1:
                # print("D... EDGE")
                self.history_pointer += 1  # empty
                global_key = ""
                self.cursor = 0
        elif key == "tab":
            key = ""
        # else:
        #    self.cursor+=1

        # print("D...  ..........",self.cursor, "after press /    limit",len(global_key)+1)

        #### global_key = f"{global_key[:self.cursor+1]}{key}{global_key[self.cursor+1:]}" # KEEP IT GLOBAL !!!!!
        a, b = self.text_split()
        # print(f"i... joining {a} {key} {b}")
        global_key = f"{a}{key}{b}"  # KEEP IT GLOBAL !!!!!
        if len(key) > 0:
            self.cursor += 1

        # correct cursor if  it went too far
        if self.cursor > len(global_key) + 1:
            self.cursor = len(global_key) + 1
        if self.cursor < 0:
            self.cursor = 0

        # print("D...",f"RESULT: '{global_key}' , cu=={self.cursor} :", self.text_split() )
        # print("D...")
        # self.cursor+=1

        if key == "\n":
            stop_listening()

    def get_global_key(self):
        """
        use to read the situation and reset on enter from the main program, True when ENTER
        """
        global global_key
        if global_key.find("\n") >= 0:
            a = global_key
            global_key = ""
            return a, True, self.text_split()
        return global_key, False, self.text_split()

    def run(self):
        """
        this is a mandatory for Thread child
        """
        global global_key
        self.t = threading.current_thread()
        while True:
            # print("!...  ........................keyboard listen START")
            listen_keyboard(
                on_press=self.press,
                # debug = True,
                delay_second_char=0.1,
                delay_other_chars=0.05,
                lower=False,  # IT WAS DEFAULT
                sequential=True,
            )  # syncio
            # print("!...  ........................keyboard listen STOP")
            # print("D...",f"/{global_key}/")
            if global_key.strip() == self.ending:
                # print("!...  ........................keyboard listen BREAK")
                break
        print("!...  ........................keyboard THREAD  ENDED")


# --------https://stackoverflow.com/questions/2408560/python-nonblocking-console-input
# ON ENTER
# CALL WITH CALLBACK FUNCTION AS A PARAMETER
# class KeyboardThread(threading.Thread):


def main():
    print()


if __name__ == "__main__":
    Fire(main)
