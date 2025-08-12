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
from cmd_ai.api_key import get_api_key
from cmd_ai.version import __version__

#### ---- functions -----
#from  cmd_ai import function_chmi
#from  cmd_ai import function_goog # google search
#from  cmd_ai import function_webc # web content
import json # for function call

# importing modules
#import urllib.request
#from PIL import Image
#import tempfile

import base64
import requests
import glob

import re

import os
import time
import glob


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def latest_screenshot(directory="~/Pictures/Screenshots", pattern="Screenshot*"):
    directory = os.path.expanduser(directory)
    files = glob.glob(os.path.join(directory, pattern))
    if not files:
        return "No screenshots found."
    latest_file = max(files, key=os.path.getmtime)
    return latest_file


def is_recent(file_path, max_age_seconds=3600):
    if not os.path.exists(file_path):
        return False
    file_mtime = os.path.getmtime(file_path)
    current_time = time.time()
    #print(file_path, file_mtime, current_time)
    age = current_time - file_mtime
    return age #< max_age_seconds


def g_askvision(
        prompt,
        image_path = None,
        temp=0.0,
        model="gpt-4o-2024-11-20",
        # limit_tokens=300,
        total_model_tokens=4096 * 2 - 50, # guess
        size="1024x1024",
        detail="low",
        n=1
):
    """
    upload an image
    """

    print(f"{fg.orange}i... VISION, detail={detail}: {fg.default}", prompt )

    # OpenAI API Key
    myapi_key = get_api_key() #"YOUR_OPENAI_API_KEY"


    # Path to your image
    #image_path = "path_to_your_image.jpg"
    # Getting the base64 string

    image_path1 = image_path

    # ======================
    if image_path1 is None: #first thing in the prompt
        #print(f"i... looking for some image.jpg form the prompt:/{prompt}/ ...")
        guess = prompt.split(".jpg")
        if len(guess) == 1:
            print(f"x... {fg.orange} no JPG found in prompt ... png?", fg.default)
            guess = prompt.split(".png")
            if len(guess) == 1:
                print(f"X... {fg.orange}nor PNG image found  in prompt ...", fg.default)
                #return None, None
            else:
                image_path1 = guess.split(" ")[-1]+".png"
                image_path1 = image_path1.strip()
                print( fg.green, f"/{image_path1}/", fg.default)
        else:
            image_path1 = guess[0].split(" ")[-1]+".jpg"
            image_path1 = image_path1.strip()
            print( fg.green, f"/{image_path1}/", fg.default)

    if image_path1 is None:
        screenshot = latest_screenshot()
        #print("D... last screenshot seen...", screenshot)
        if is_recent(screenshot) < 3600:
            print(f"i... {fg.green} I take {screenshot} as an input... {fg.default}")
            image_path1 = screenshot
        else:
            print(f"X... {fg.red} it is too old  {fg.default}  {screenshot}   old  {is_recent(screenshot)} sec")

    # # =============== ENTER INPUT ============================================
    # if image_path1 is None or not os.path.exists(image_path1):
    #     print(f"{fg.red}X... image /{image_path1}/ doesnt exist {fg.default}")
    #     print("i...available=", glob.glob("*.jpg"))
    #     #IMG = input("> INPUT jpg filename without .jpg :")
    #     #image_path1 = IMG+".jpg"
    #     return None, False, model

    #
    if image_path1 is None  or not os.path.exists(image_path1):
        print(f"{fg.red}X... no image defined{fg.default}")
        return None, False, model
        #return None


    limit_tokens = config.CONFIG['limit_tokens']

    base64_image = encode_image(image_path1)

    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {myapi_key}"
    }

    payload = {
      "model": model,
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": prompt
            },
            {
              "type": "image_url",
              "image_url": {
                  "url": f"data:image/jpeg;base64,{base64_image}",
                  "detail": detail
              }
            }
          ]
        }
      ],
      "max_tokens": limit_tokens
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    #print( response.json())
    #print( "res   ",type(response) ) # req models response
    #print( "res js",type(response.json() ) ) # dict

    resdi = response.json()
    #print( type(resdi) )  # dict
    #print( resdi )
    if "error" in resdi.keys() :
        print("X...", fg.red, resdi["error"]["message"], fg.default)
        return None, False, model
    #print( resdi.keys() )
    #print(resdi['choices'] )
    #print( resdi['choices'][0] )
    #print( resdi['choices'][0]['message'] )
    #print( resdi['choices'][0]['message']['content'] )
    res = resdi['choices'][0]['message']['content']
    finish = resdi['choices'][0]['finish_reason'] != "stop"

    #finish = response.choices[0].finish_reason
    return res, finish, model

if __name__ == "__main__":
    print("... see the returned list:")
    Fire( g_askvision )
