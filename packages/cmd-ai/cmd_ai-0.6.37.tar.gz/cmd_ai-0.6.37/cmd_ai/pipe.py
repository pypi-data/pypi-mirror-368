#!/usr/bin/env python3
"""
pipe test
"""
from fire import Fire

from cmd_ai import config
from cmd_ai.version import __version__

# print("v... unit 'unitname' loaded, version:",__version__)

import sys
import select
# import fileinput


def main(question):
    if select.select([sys.stdin, ], [], [], 0.0)[0]:
        print("Pipe mode! Q:", question)

        for line in sys.stdin:
            print("...",line.strip())

    else:
        print("No pipe")



if __name__ == "__main__":
    print("i... in the __main__ of pipe of cmd_ai")
    Fire(main)
