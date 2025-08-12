#!/usr/bin/env python3
import datetime as dt
import json
import os
import sys
from console import fg,bg
from fire import Fire

from cmd_ai.version import __version__

MODEL_TO_USE = None
# ----- port here. 5000 is flask; is moved to 8000 by gunicorn; to 80 by nginx
CONFIG = {
    "filename": "~/.config/cmd_ai/cfg.json",
    "api_key": None,
    "api_key_gemini": None,
    "api_key_anthropic": None,
    "limit_tokens":300,
    "pricelog":"~/cmd_ai_price.log",
    "pyscript":"/tmp/cmd_ai_code",
    "shscript":"/tmp/cmd_ai_bash",
    "sourcecode":"/tmp/cmd_ai_sourcecode",
    "sourcecodeext":"txt", # it is changing during process...
    "current_messages":"/tmp/cmd_ai_messages",
    "last_prompt":"undefined",
    "last_response":"/tmp/cmd_ai_last_response",
    "conversations":"~/conversations.org",
    "current_role":"assistant",
    "current_name":"zulu",
    "calendar_token":"~/.config/cmd_ai/token.json",
    "calendar_credentials":"~/.config/cmd_ai/credentials.json",
    "gmail_token":"~/.config/cmd_ai/tokengm.json",
    "gmail_credentials":"~/.config/cmd_ai/credentialsgm.json",
    "model_to_use": "gpt-4o-2024-11-20",
    "python_interpretter": "~/.venv/defaul/bin/python3",
#    "model_to_use": "gpt-4o-2024-08-06",
    "quit": False,  # this is howto quit
}
#  names == current messages, scripts and last_response
#
#

gemini_chat = None # THIS IS A GLOBAL GENMINI CHAT.... reset it on reset

# This is the list of all tools - functions available =NEW=
available_functions = {} # later on we fill
TOOLLIST = [] # tools/functions available - being sent to the model

# TTS
READALOUD = 0
READALOUDSET = [None,'en','cs']


pipeinput = None # for pipe for linux system

silent = False # when pipe i like to be silent

client = None
tokens = 0
started_task = None
started_total = None
myPromptSession = None

messages = []
# system_role = "assistant" # in texts

started_task = dt.datetime.now()
started_total = dt.datetime.now()

# PYSCRIPT = "/tmp/gpt_code.py"
PYSCRIPT_EXISTS = False
SHSCRIPT_EXISTS = False
SOURCECODE_EXISTS = False

# CFG_DEBUG = True
CFG_DEBUG = False
# ======================================== ALL DEBUG
DEBUG = False # from main
BUDGET = False # from main



# ===========================================================
# ===========================================================
# ===========================================================


def verify_config(filename=""):
    """used inside, verification of bak json version"""
    global CONFIG
    if filename != "":
        CONFIG["filename"] = filename
    cfg = CONFIG["filename"]
    # if CFG_DEBUG:print("D... verifying config from",cfg)
    ok = False
    try:
        if os.path.isfile(os.path.expanduser(cfg)):
            with open(os.path.expanduser(cfg), "r") as f:
                dicti = json.load(f)
        ok = True
        if CFG_DEBUG:
            print("D... config verified")
    except:
        if CFG_DEBUG:
            print("D... verification config FAILED")
    return ok


def get_config_file():
    """returns the filename where config is stored"""
    global CONFIG
    return CONFIG["filename"]


def show_config(cdict=None, filename=""):
    """used inside, shows current config dictionary OR other dict"""
    global CONFIG
    if filename != "":
        CONFIG["filename"] = filename
    if cdict == None:
        print(json.dumps(CONFIG, indent=1))
    else:
        print(json.dumps(cdict, indent=1))


def cfg_to_bak(filenamebk="", filename=""):
    """used inside, rename config (before save)"""
    global CONFIG
    if filename != "":
        CONFIG["filename"] = filename

    if filenamebk == "":
        cfg = CONFIG["filename"]
    else:
        cfg = filenamebk

    cfgbak = cfg + ".bak"
    # print("D... cfg:",cfg)
    # print("D... cfgbak:",cfgbak)
    if CFG_DEBUG:
        print("D... creating a backup config:", cfgbak)
    if not os.path.isfile(os.path.expanduser(cfg)):
        print(f"X... config {cfg} doesnt exist (yet?, OK)")
        return True

    ### rozXXXX
    try:
        os.rename(os.path.expanduser(cfg), os.path.expanduser(cfgbak))
        result = True
    except:
        print("X... couldnt rename old:", cfg, "no bak file created")
        result = False
    return result


def bak_to_cfg(filenamebk="", filename=""):
    """used inside, rename back the bak version"""
    global CONFIG
    if filename != "":
        CONFIG["filename"] = filename

    if filenamebk == "":
        cfg = CONFIG["filename"]
    else:
        cfg = filenamebk

    cfgbak = cfg + ".bak"
    if CFG_DEBUG:
        print("D... testing if backup config exists:", cfgbak)
    if os.path.isfile(os.path.expanduser(cfgbak)):
        if CFG_DEBUG:
            print("D... BACUP config exists:", cfgbak, "... renaming to:", cfg)
        os.rename(os.path.expanduser(cfgbak), os.path.expanduser(cfg))
        if CFG_DEBUG:
            print("D... config is recovered from:", cfgbak)
    else:
        if CFG_DEBUG:
            print("D... bak config did not exist:", cfgbak, "no bak file recovery")


def save_config(filenamesv="", filename=""):  # duplicit... filename overrides
    """FRONT function, save config to filename"""
    global CONFIG
    if filename != "":
        CONFIG["filename"] = filename

    if filenamesv == "":
        cfg = CONFIG["filename"]
    else:
        cfg = filenamesv

    if CFG_DEBUG:
        print("D... calling cfg_to_bak:", cfg)
    if not cfg_to_bak(cfg):
        sys.exit(1)

    if CFG_DEBUG:
        print("D... writing config:", cfg)

    ### rozxxx
    dir2create = os.path.dirname(cfg)
    # print("D...",dir2create)
    if not os.path.isdir(os.path.expanduser(dir2create)):
        if CFG_DEBUG:
            print(f"D... trying to create directory {dir2create} if needed")
        result = False
        os.mkdir(os.path.expanduser(dir2create))

    with open(os.path.expanduser(cfg), "w+") as f:
        f.write(json.dumps(CONFIG, indent=1))
        if CFG_DEBUG:
            print("D... config was written:", cfg)

    if verify_config(filename):
        if CFG_DEBUG:
            print("D... verified by verify_config ... ok ... ending here")
        return True
    # ====ELSE RECOVER BAK
    return bak_to_cfg()


def load_config(filename=""):
    """FRONT function, load config file"""
    global CONFIG
    if filename != "":
        CONFIG["filename"] = filename
    cfg = CONFIG["filename"]
    cfg = cfg + ".from_memory"
    if CFG_DEBUG:
        print("D... calling save_config:")
    save_config(cfg)

    cfg = CONFIG["filename"]
    if CFG_DEBUG:
        print("D... loading config from", cfg)

    if not verify_config(filename):
        print("X... FAILED on verifications")
        return False

    if CFG_DEBUG:
        print("D... passed verification of:", cfg)
    dicti = CONFIG

    if CFG_DEBUG:
        print("D... directly loading json:", cfg)
    if os.path.isfile(os.path.expanduser(cfg)):
        with open(os.path.expanduser(cfg), "r") as f:
            dicti = json.load(f)

    # rewriting in memory
    if sorted(dicti.keys()) == sorted(CONFIG.keys()):
        if CFG_DEBUG:
            print("D... memory and disk identical:")
    else:
        if CFG_DEBUG:
            print("X... memory and disk differ:")
        # show_config(CONFIG)
        # there may be more lines in the CODE after upgrade.
        for k in CONFIG.keys():  # search CODE version
            if not (k in dicti.keys()):
                dicti[k] = CONFIG[k]
                if DEBUG: print(f"{fg.lightslategray}W... config-key /{k}/  not on DISK! Setting to {dicti[k]}  {fg.default}")

    CONFIG = dicti
    if CFG_DEBUG:
        print("D... final CONFIG:")
    # show_config(filename)
    if CFG_DEBUG:
        print("D... end load")


def loadsave(filename=""):
    """FRONT function, if DISK is earlier version than CODE, this may update DISK"""
    if filename != "":
        CONFIG["filename"] = filename

    load_config(filename)
    save_config()  # ?


# ==========================================================


def func(debug=False):
    print("D... in unit config function func DEBUG may be filtered")
    print("i... in unit config function func - info")
    print("X... in unit config function func - ALERT")
    return True


def test_func():
    print("i... TESTING function func")
    assert func() == True


if __name__ == "__main__":
    print("i... in the __main__ of config of codeframe")
    Fire()
