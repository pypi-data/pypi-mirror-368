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
from fire import Fire
import datetime as dt

from console import fg
import sys


import re
from playwright.sync_api import Playwright, sync_playwright, expect

MYOUTPUT = []

def show(text):
    tag = "Aktuální dopravní nehody"
    tg2 = "SMS dopravní nehody"
    a =  text.split(tag)[-1]

    b =  a.split(tg2)[0]
    b = b.replace("více informací >","")
    b = b.replace("Výběr lokality dopravních informací:", "")
    b = b.replace("Aktuální situace","")
    b = b.replace("V této lokalitě nemáme hlášeny žádné dopravní nehody", "žádné nehody")
    return b



def run(playwright: Playwright) -> None:
    global MYOUTPUT
    browser = playwright.firefox.launch( headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.nehody-uzavirky.cz/nehody/")
    page.get_by_role("link", name="Uložit nastavení").click()
    page.locator("#di-okres").select_option("1")
    page.get_by_role("button", name="zobrazit").click()

    # ---------------------

    # Get the text content of the body
    page_text = page.locator('body').inner_text()
    MYOUTPUT.append( f"PRAHA:  {show(page_text)}")

    page.get_by_role("button", name="x").click()
    page.locator("#di-okres").select_option("78")
    page.get_by_role("button", name="zobrazit").click()

    page_text = page.locator('body').inner_text()
    #print("PRAHA-VYCHOD:", show(page_text))
    MYOUTPUT.append( f"PRAHA-VYCHOD:  {show(page_text)}")

    page.get_by_role("button", name="x").click()
    page.locator("#di-okres").select_option("79")
    page.get_by_role("button", name="zobrazit").click()

    page_text = page.locator('body').inner_text()
    #print("PRAHA-ZAPAD:",show(page_text))
    MYOUTPUT.append( f"PRAHA-ZAPAD:  {show(page_text)}")

    # page.get_by_role("button", name="x").click()
    # page.locator("#di-okres").select_option("69")
    # page.get_by_role("button", name="zobrazit").click()


    #page_text = page.locator('body').inner_text()
    #print(show(page_text))



    # If you want to get text from a specific element,
    # you would first locate that element and then use inner_text() or text_content()
    # For example, if there was a div with id="results":
    # results_text = page.locator("#results").inner_text()
    # print(results_text)

    context.close()
    browser.close()

def check_web_nehody():
    global MYOUTPUT
    with sync_playwright() as playwright:
        run(playwright)
    RES = "\n".join(MYOUTPUT)
    RES = RES.replace("\n\n\n", "\n")
    RES = RES.replace("\n\n", "\n")
    return RES

if __name__=="__main__":
    a = check_web_nehody()
    print(a)
