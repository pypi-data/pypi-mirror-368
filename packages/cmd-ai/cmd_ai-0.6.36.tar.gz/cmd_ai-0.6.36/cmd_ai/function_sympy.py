#!/usr/bin/env python3

from cmd_ai import config
from cmd_ai.version import __version__
import json
import os
import datetime as dt
import sys

"""
texts.py contains the description: tool_***={}


*************************************
pip3 install --upgrade
*************************************

"""


import datetime

from fire import Fire
import datetime as dt
from console import fg

import  sympy
import re
#from sympy import sympify, pi, symbols
#from sympy.abc import x, y, z

def safe_sympify(input_str):
    # Remove any string that might contain dangerous commands
    if any(dangerous in input_str for dangerous in ['__',  'exec', 'import', 'open', 'os', 'sys', 'subprocess']):
        return "X...Potentially unsafe input rejected"
    # Only allow alphanumeric characters, basic math operators and common math functions
    safe_pattern = r'^[a-zA-Z0-9\s\+\-\*\/\^\(\)\[\]\{\}\.\,\=\_\>\<\!\&\|]+$'
    if not re.match(safe_pattern, input_str):
        return "X...Input contains disallowed characters"
    if not re.match(r'^[\d\w\s\+\-\*/\^\(\)\.,\[\]]+$', input_str):
        return "X...Potentially unsafe characters rejected"
        #raise ValueError("Invalid input: contains unsafe characters.")

    result = ""
    try:
        # Use sympify with evaluate=True but in a restricted namespace
        result = sympy.sympify(input_str, locals={"pi": sympy.pi, "e": sympy.E, "i": sympy.I}, evaluate=True)
        #print(result)
        result = result.evalf()
        #print(result)
        #result = str(result)
    except Exception as e:
        result = f"the {input_str} results in error: {str(e)}, I must try better"
    return str(result)


# ============================================================
#
# ------------------------------------------------------------
def callSympy( expression ):
    """
    call (check if sanitized) sympy
    """
    res = safe_sympify(expression)
    print(f"D... SYMPYCALL: {expression} => {res}")
    return json.dumps(  {"result":res } , ensure_ascii=False)



# ============================================================
#
# ------------------------------------------------------------
if __name__=="__main__":
    Fire({'m':make_dir_with_date,
          'f':setMeetingRecord,
          'g':getTodaysDateTime})
