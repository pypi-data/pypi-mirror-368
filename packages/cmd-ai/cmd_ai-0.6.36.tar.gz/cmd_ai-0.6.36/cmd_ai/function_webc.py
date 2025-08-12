#!/usr/bin/env python3

from cmd_ai import config
from cmd_ai.version import __version__
import json

"""
texts.py contains the description: tool_***={}
In syscom.py ADD the tool_Name to  config.TOOLLIST
In g_askme.py IMPORT module:   from cmd_ai import  function_***
In g_askme.py - add to ... config.available_functions

*************************************
pip3 install --upgrade
*************************************

"""

from googlesearch import search

from fire import Fire
import datetime as dt
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment

# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager

# from webdriver_manager.firefox import GeckoDriverManager

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from subprocess import getoutput

from console import fg
import sys

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def fetch_url_content(url):
    #print("D...  requesting", url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    cont = []
    res=""
    if response.status_code == 200:
        #print("D...  response is OK (webC)")
        soup = BeautifulSoup(response.text, 'html.parser')
        texts = soup.findAll(string=True)
        visible_texts = filter(tag_visible, texts)
        #print(visible_texts)
        for i in visible_texts:
            i = i.strip()
            if len(i)==0: continue
            cont.append(i)
        res =  "\n".join(cont)
        #return  json.dumps(   {"result":"ok", "url_content":"bitwadren is very safe application and website" }  , ensure_ascii=False)
        # print("D... returning json in webc. Size ", sys.getsizeof(res) )
        # if sys.getsizeof(res) < 100:
        #     print(res)
        # if sys.getsizeof(res) > 1000:
        #     res = res[:1000]
        #print("i... function WEC RETURN OK , Size ", sys.getsizeof(res) )
        #return json.dumps(  {"result":"error", "url_content":"Page not found" } , ensure_ascii=False)  # MUST OUTPUT FORMAT
        return json.dumps(   {"result":"ok", "url_content": res } , ensure_ascii=False)  # MUST OUTPUT FORMAT

    else:
        #print("X... function WEC RETURN FAIL")
        return json.dumps(  {"result":"error", "url_content":"Page request failed" } , ensure_ascii=False)  # MUST OUTPUT FORMAT
        #return f"Error: Unable to fetch the URL. Status code: {response.status_code}"




if __name__=="__main__":
    Fire(fetch_url_content)
