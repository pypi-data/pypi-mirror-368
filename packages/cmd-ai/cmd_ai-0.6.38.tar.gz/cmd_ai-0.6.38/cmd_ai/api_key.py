#!/usr/bin/env python3
"""
We create a unit, that will be the test_ unit by ln -s simoultaneously. Runs with 'pytest'

change models with .m   .mmodelname   SEE syscom.list_models
"""
import os
import sys
from fire import Fire
from console import fg, bg
from cmd_ai import config
from cmd_ai.version import __version__

# ===============================================================================================


def get_api_key():
    """
    openAI
    """
    #print(f"i... openai key", config.CONFIG['api_key'])
    if config.CONFIG['api_key'] is not None:
        return config.CONFIG['api_key']

    openai_api_key = os.getenv("OPENAI_API_KEY")

    # print("KEY from ENV  ===  ", openai_api_key )
    if (openai_api_key == "") or (openai_api_key == None):
        # print("X... {fg.red} NO KEY in ENV.... {fg.default}")
        with open(os.path.expanduser("~/.openai.token")) as f:
            res = f.readlines()[0].strip()
        if not res is None and res != "":
            openai_api_key = res
        else:
            #print("X... I need OPENAI_API_KEY  set !!!!!")
            print(f"X...  I need to set {fg.red} export OPENAI_API_KEY= {fg.default}")
            sys.exit(1)

    # print("KEY ... final  ===  ", openai_api_key )
    # openai.api_key = openai_api_key
    return openai_api_key



def get_api_key_anthropic():
    """
    anthropic
    """
    OPENAIANTHROPICTOKEN = os.path.expanduser("~/.openai_anthropic.token")
    #print(f"i... anthropic key", config.CONFIG['api_key_anthropic'])
    if config.CONFIG['api_key_anthropic'] is not None:
        return config.CONFIG['api_key_anthropic']

    openai_api_key = os.getenv("ANTHROPIC_API_KEY")

    # print("KEY from ENV  ===  ", openai_api_key )
    if (openai_api_key == "") or (openai_api_key == None):
        # print("X... {fg.red} NO KEY in ENV.... {fg.default}")
        res = None
        if os.path.exists( OPENAIANTHROPICTOKEN ):
            with open(OPENAIANTHROPICTOKEN) as f:
                res = f.readlines()[0].strip()
        if not res is None and res != "":
            openai_api_key = res
        else:
            #print("X... I need ANTHROPIC_API_KEY  set !!!!!")
            print(f"X... I need to set {fg.red} export ANTHROPIC_API_KEY= {fg.default}")
            return None
            #sys.exit(1)

    # print("KEY ... final  ===  ", openai_api_key )
    # openai.api_key = openai_api_key
    return openai_api_key


def get_api_key_gemini():
    """
    google gemini
    """
    OPENAIGENIMITOKEN = os.path.expanduser("~/.openai_gemini.token")
    #print(f"i... gemini key", config.CONFIG['api_key_gemini'])
    if config.CONFIG['api_key_gemini'] is not None:
        #print("D... returning cfg key gemini")
        return config.CONFIG['api_key_gemini']
    openai_api_key = os.getenv("GEMINI_API_KEY")

    # print("KEY from ENV  ===  ", openai_api_key )
    if (openai_api_key == "") or (openai_api_key == None):
        # print("X... {fg.red} NO KEY in ENV.... {fg.default}")
        res = None
        if os.path.exists(OPENAIGENIMITOKEN):
            with open(OPENAIGEMINITOKEN) as f:
                res = f.readlines()[0].strip()
        if not res is None and res != "":
            openai_api_key = res
        else:
            #print("X... I need GEMINI_API_KEY  set !!!!!")
            print(f"X... I need to set {fg.red} export GEMINI_API_KEY= {fg.default}")
            #sys.exit(1)
            return None

    # print("KEY ... final  ===  ", openai_api_key )
    # openai.api_key = openai_api_key
    return openai_api_key


if __name__ == "__main__":
    print("i... in the __main__ of unitname of cmd_ai")
    Fire()
