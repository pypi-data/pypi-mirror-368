#!/usr/bin/env python3
"""
We create a unit, that will be the test_ unit by ln -s simoultaneously. Runs with 'pytest'
"""
import datetime as dt
import time
import os
import tiktoken
from console import fg,bg,fx
from fire import Fire

import openai
from cmd_ai import config
from cmd_ai import texts
from cmd_ai.version import __version__

#### ---- functions -----
#from  cmd_ai import function_chmi
#from  cmd_ai import function_goog # google search
#from  cmd_ai import function_webc # web content
import json # for function call

# importing modules
import urllib.request
from PIL import Image
import tempfile
import datetime as dt

def get_tmp( folder = "/tmp/", timetag = False, shortname = ""):
    """
    the printer understands to PNG
    """
    suffix = '.jpg'
    tmp_dir = folder # '/tmp'
    temp_filename = ""
    if timetag:
        tag = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"{tmp_dir}{tag}_{shortname}.jpg"
    else:
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, dir=tmp_dir, delete=False)
        temp_filename = temp_file.name
        temp_file.close()
    return temp_filename




def g_askdalle(
        prompt,
        temp=0.0,
        model="dall-e-3",
        # limit_tokens=300,
        total_model_tokens=4096 * 2 - 50, # guess
        size="1024x1024",
        quality="standard",
        n=1
):
    """
    send demand to dalle  and fetch the image()
    """

    print(f"{fg.orange}i... using EXACT PROMPT: {fg.default}\n",texts.role_dalle, prompt)
    response = config.client.images.generate(
        model=model,# "dall-e-3",
        prompt=texts.role_dalle + prompt, # "a white siamese cat",
        size=size,# "1024x1024",
        quality=quality,# "standard",
        n=n# 1,
    )
    print("D... responded...")


    if response is None:
        return None

    image_url = response.data[0].url
    short = prompt.replace(" ","_").strip()
    short = short.replace("$","_").strip()
    short = short.replace("#","_").strip()
    short = short.replace("/","_").strip()
    short = short.replace("(","_").strip()
    short = short.replace(")","_").strip()
    short = short.replace("{","_").strip()
    short = short.replace("}","_").strip()
    short = short.replace("!","_").strip()
    short = short.replace("?","_").strip()
    if len(short)>14: short = short[:14]
    OUTPUT = get_tmp(folder="./", timetag=True, shortname = short  ) # use "/"
    print(f"D... fetching {OUTPUT}...")
    urllib.request.urlretrieve( image_url , OUTPUT )

    img = Image.open( OUTPUT)
    img.show()

    return response



if __name__ == "__main__":
    print("i... in the __main__ of unitname of cmd_ai")
    Fire()
