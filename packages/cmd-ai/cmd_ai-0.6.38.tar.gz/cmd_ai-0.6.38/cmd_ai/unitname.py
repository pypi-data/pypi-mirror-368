#!/usr/bin/env python3
"""
We create a unit, that will be the test_ unit by ln -s simoultaneously. Runs with 'pytest'
"""
from fire import Fire

from cmd_ai import config
from cmd_ai.version import __version__

# print("v... unit 'unitname' loaded, version:",__version__)


def func(debug=False):
    print("D... in unit unitname function func DEBUG may be filtered")
    print("i... in unit unitname function func - info")
    print("X... in unit unitname function func - ALERT")
    return True


def test_config_save():
    config.CONFIG["filename"] = "~/.config/cmd_ai/cfg.json"
    config.show_config()
    print(config.get_config_file())
    assert config.save_config() == True


def test_config_read():
    config.CONFIG["filename"] = "~/.config/cmd_ai/cfg.json"
    config.load_config()
    config.show_config()
    print(config.get_config_file())
    assert config.save_config() == True


def test_func():
    print("i... TESTING function func")
    assert func() == True


if __name__ == "__main__":
    print("i... in the __main__ of unitname of cmd_ai")
    Fire()
