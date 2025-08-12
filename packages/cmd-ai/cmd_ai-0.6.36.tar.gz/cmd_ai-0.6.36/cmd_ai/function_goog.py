#!/usr/bin/env python3

from cmd_ai import config
from cmd_ai.version import __version__

"""
texts.py contains the description: tool_***={}
In syscom.py ADD the tool_Name to  config.TOOLLIST
In g_askme.py IMPORT module:   from cmd_ai import  function_***
In g_askme.py - add to ... config.available_functions


*************************************
pip
*************************************

"""

from googlesearch import search
import json

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


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def fetch_url_content(url):
    """
    not this!!!!!!
    """
    #print("D...  requesting", url)
    response = requests.get(url)
    cont = []
    res=""
    if response.status_code == 200:
        print("D...  response is OK (goog)")
        soup = BeautifulSoup(response.text, 'html.parser')
        texts = soup.findAll(string=True)
        visible_texts = filter(tag_visible, texts)
        print(visible_texts)
        for i in visible_texts:
            i = i.strip()
            if len(i)==0: continue
            cont.append(i)
            print("       ",fg.orchid, i, fg.default)
        res =  "\n".join(cont)
        return json.dumps(  {"url_content":res } , ensure_ascii=False)  # MUST OUTPUT FORMAT

    else:
        print("D...  response is NOT OK (goog)", res)
        return json.dumps(  {"url_content":res } , ensure_ascii=False)  # MUST OUTPUT FORMAT
        #return f"Error: Unable to fetch the URL. Status code: {response.status_code}"



def get_google_urls(searchstring):
    """
    working horse
    """
    pool = search( searchstring)#, num_results=5)
    urls = []
    cont = []
    for i in pool:
        urls.append(i)
    urls = list(set(urls))
    for i in urls:
        #cont.append("# URL ADDRESS:")
        cont.append(i)
        print(f"  >>   {i}")
    res = cont#"\n".join( cont)

    # must return json for GPT
    return json.dumps(  {"urls":res } , ensure_ascii=False)  # MUST OUTPUT FORMAT



if __name__=="__main__":
    Fire({'g':get_google_urls,
          'f':fetch_url_content})
