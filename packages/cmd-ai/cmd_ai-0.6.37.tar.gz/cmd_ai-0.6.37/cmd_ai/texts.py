#!/usr/bin/env python3
"""
We create a unit, that will be the test_ unit by ln -s simoultaneously. Runs with 'pytest'
"""
from fire import Fire
import datetime as dt
from console import fg, bg, fx

from cmd_ai import config
from cmd_ai.version import __version__

HELP = """
________________SYSTEM COMMANDS_____
.h      help
.q      quit
.e      execute the shown code
.r      reset messages, scripts
.l      show tokens
.m      show models
.l; .l number ... change limit tokens
.g      add functions ... google,CHMI weather, webcont, CALENDAR, datetime
.v      read the answer aloud
.c      catch up messages after crash...
________________ ROLES _______________
.a   assistant (default in INTERACTIVE and CMDLINE)
.s   secretary (+.g for calendar and gmail)
.p   python coder
.d   dalle 3 ... most exact prompt variant
.t   translator
.i   use vision - low detail
"""
# .s   shell expert (default in PIPE)





#######################################################################
#     T O O L S ..... functions
#######################################################################
# localted  function_chmi.py  get_chmi()
#
#  ADD ALSO TO g_askme.py ... vvvvvvvvvvvvvvvvvvvvvvvvv
#

#
# ADD
#

tool_getCzechWeather = {
                    "type": "function",
                    "function": {
                        "name": "getCzechWeather",
                        "description": "The function provides weather forecast for today(dnes), night(noc) and tomorrow(zitra) in Czech Republic. The function can also provide actual weather alert(vystraha) for Czech Republic. Text in Czech, parameters in Czech.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "time": {"type": "string", "description": "Useful options are: dnes | noc | zitra | vystraha , other options will lead to uncertain or unknown prediction."}
                            },
                            "required": ["time"]
                        }
                    }
                }


tool_searchGoogle = {
                    "type": "function",
                    "function": {
                        "name": "searchGoogle",
                        "description": "Search Google.com for a phrase and obtain list of urls. Find todays date before with tool: getTodaysDateTime",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "searchstring": {"type": "string", "description": "optimal search phrase"}
                            },
                            "required": ["searchstring"]
                        }
                    }
                }


tool_getWebContent = {
                    "type": "function",
                    "function": {
                        "name": "getWebContent",
                        "description": "Retrieve the content of a web page by BeautifulSoup. The content is only the text part of the page, page may be not found.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string", "description": "url of a web page to retrieve"}
                            },
                            "required": ["url"]
                        }
                    }
                }


tool_getNehody = {
                    "type": "function",
                    "function": {
                        "name": "getNehody",
                        "description": "Retrieve the list of current trafic accidents in three Bohemian regions."
                    }
                }

# with google functions in syscom.py
tool_setMeetingRecord = {
                    "type": "function",
                    "function": {
                        "name": "setMeetingRecord",
                        "description": "For a future meeting/event/task/deadline record the date, time, name and content to a calendar. Check todays date before ussing the tool getTodaysDateTime.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "date_": {
                                    "type": "string",
                                    "description": "The date of the meeting in the format %Y%m%d."
                                },
                                "time_": {
                                    "type": "string",
                                    "description": "The time in the 24h format %H%M. If unknown, use 1200."
                                },
                                "hint": {
                                    "type": "string",
                                    "description": "A short hint or title for the meeting content."
                                },
                                "content": {
                                    "type": "string",
                                    "description": "The details about the meeting, especially any links."
                                }
                        },
                            "required": ["date_", "time_", "hint", "content"]
                        }
                    }
                }

# with google functions in syscom.py
tool_sendGmail = {
                    "type": "function",
                    "function": {
                        "name": "sendGmail",
                        "description": "send email.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "email_recipient": {
                                    "type": "string",
                                    "description": "email address of the recipient."
                                },
                                "email_subject": {
                                    "type": "string",
                                    "description": "A subject. Should be short, clear but specific."
                                },
                                "email_body": {
                                    "type": "string",
                                    "description": "Text content of the email. If the signature is not specified, use 'the AI Assistant'. Never use options in brackets [] - be always specific"
                                },
                                "attachment_path": {
                                    "type": "string",
                                    "description": "If an attachment needed, give the filename or the path of this attachment. Path starting with ~/ is also allowed."
                                }
                        },
                            "required": ["email_recipient", "email_subject", "email_body"]
                        }
                    }
                }

# ------------------------
tool_getTodaysDateTime = {
                    "type": "function",
                    "function": {
                        "name": "getTodaysDateTime",
                        "description": "get today date and time in the European format: %a %d.%m. %Y %H:%M, where %a is the abbreviated day. No parameters required."

                    }
                }

# ------------------------
tool_callSympy = {
    "type": "function",
    "function": {
        "name": "callSympy",
        "description": "Exactly calculate mathematical expressions using python sympy module. ",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A mathematical expression in python sympy notation, that should lead to a float number. The content will go as the parameter to sympify() function."
                }
            },
            "required": ["expression"]
        }
    } # func tion
    }


#######################################################################
#     R O L E S
#######################################################################

role_secretary = f"""You are a personal assistant. Respond correctly, but briefly. Use a short and brief language. Do not repeat yourself nor the users' questions. Before every answer, CHECK the current year!, date and time using getTodaysDateTime. The prompt frequently contains just information on appointment, meeting, deadline, event etc: use the tool "setMeetingRecord" to record a future meeting (check the current year). If the prompt contains date(s), it is very probably a task for setMeetingRecord. If the task explicitely requires to send an email, use sendGmail tool."""

role_assistant = f"""It is {dt.datetime.now().strftime("%a %h. %d %Y")}. You are a general assistant, respond correctly but briefly. You use a short and brief language, you do not repeat yourself nor the users' questions. All the answers are short but precise. """

#role_assistant = """You are the assistant, you respond questions correctly, you fulfill tasks. You use a short and brief language, you do not repeat yourself nor the users' questions. All the answers are short but precise. If the text is an information on a task,appointment,meeting,deadline,event AND the tool "setMeetingRecord" is available, consider recording a meeting."""

# The code must be always safe and secure, no harm for the filesystem nor for the network.
role_pythonista = """You are PYTHON program writer. The prompts instruct you to create a python code. The code must be able to run from the commandline - use click and use default values. For graphs, use matplotlib. You use a short and brief language. Never repeat user questions. Make the answers short but precise. Do not give examples how to run the code from shell. Never use example paths e.g. '/path/to/', if not specified, use the current directory. Provide maximum ONE code block per response. Do not show how to install packages, unless explicitelly asked."""



role_translator = """ You translate scientific text prompts from English to Czech. Use clean and concise language. Reformulate the translated text clean and fluent.
It contains specific nuclear physics terminology so
 - "beam" means "svazek" in Czech
 - "target" means "terč" in Czech
 - "beam time" means "urychlovačový čas" in Czech
 - "beam dump" means "zařízení pro zastavení svazku" in Czech
 - "is promissing" mean "je slibná" or "je slibný" in Czech
 In a case I give you a text in SRT subtitles format : `line_number \n time-start --> time-end \n some_sentence(s) \n\n`. The time is in the format of srt: hh:mm:ss,fff - in that case you keep the format exactly he same and translate the sentences to czech.
"""

# #  and secure, no harm for the filesystem nor for the network
# role_sheller = """ You are an Ubuntu 22 commandline and bash expert. The code must be always safe. You use a short and brief language. Do not repeat the user questions.  Do not repeat yourself. You make the answers short but precise. Only shell code, no examples how to run. Never use example paths e.g. '/path/to/', if not specified, use the current directory. One code block per response maximum.
# """

#  and secure, no harm for the filesystem nor for the network
role_piper = """ You are an Ubuntu 22 commandline and bash expert. You use a short and brief language. Do not repeat the user questions. Do not repeat yourself. Your answers are short but precise. No examples 'how to run'. Never use example paths e.g. '/path/to/', '/path/to/search', use current directory.
"""

role_dalle = """I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:"""
role_dalle = ""#"DO NOT add text to the following prompt, use it AS-IS:"""

role_vision = """What is in the picture?"""

#######################################################################
#     O R G
#######################################################################


org_header = r"""
# ######################## CODE DEFINITIONS ############################
#+OPTIONS: toc:nil        (no default TOC at all)
# # -------------- dont interpret ^_ as in math...
#+OPTIONS: ^:nil
#+OPTIONS: _:nil
# # --------------- do not number sections
#  +OPTIONS: num:nil

# +LATEX_HEADER: \addtolength{\textwidth}{4cm}
# +LATEX_HEADER: \addtolength{\textheight}{3cm}
# +LATEX_HEADER: \addtolength{\hoffset}{-2cm}
# +LATEX_HEADER: \addtolength{\voffset}{-3cm}


# -----------------------------------------  colored SOURCE blocks
# -----------pip install Pygments; mod .emacs
#+LaTeX_HEADER: \usepackage{minted}
#+LaTeX_HEADER: \usepackage{bookmark}
# --------- margins
#+LATEX_HEADER: \makeatletter \@ifpackageloaded{geometry}{\geometry{margin=2cm}}{\usepackage[margin=2cm]{geometry}} \makeatother
#+LaTeX_HEADER: \usemintedstyle{xcode}
#       xcode,monokai, paraiso-dark,, zenburn ... ... NOT shell /cd |
#       fruity .... NOT  + blackbg
#       colorful ... ok
#       vs ... too simple
#       inkpot ... yellowish-brown
#       vim ... pipe too light
#       gruvbox-dark,sas, stata, abap,algol, lovalace, igor, native, rainbow_dash, tango, manni, borland, autumn:), murphy, material, trac    ... italic
#       rrt ... too light green
#       perldoc, pastie, xcode, arduino ... ok (pastie,arduino (gray comments)
#  +LATEX_HEADER: % !TeX TXS-program:compile = txs:///pdflatex/[--shell-escape]


#
# ========================== this is for quote ... easy ========================
#+LaTeX_HEADER: \usepackage{etoolbox}\AtBeginEnvironment{quote}{\itshape\bf}


# =========================== new verbatim environment -------- gray example
#   tricky ... extra package needed... redefinition needed (example => verbatim)
#          ... it breaks "gray!10!white" color definitions......
#+LaTeX_HEADER: \usepackage{verbatim}
#+LaTeX_HEADER: \usepackage{framed,color,verbatim}
#+LaTeX_HEADER: \definecolor{shadecolor}{rgb}{.95, 1., .9}
#+LaTeX_HEADER: \definecolor{codecolor}{rgb}{.95, .95, .99}
#+LATEX_HEADER: \let\oldverbatim=\verbatim
#+LATEX_HEADER: \let\oldendverbatim=\endverbatim
#+LATEX_HEADER: \renewenvironment{verbatim}[1][test]
#+LATEX_HEADER: {
#+LATEX_HEADER:   \snugshade\oldverbatim
#+LATEX_HEADER: }
#+LATEX_HEADER: {
#+LATEX_HEADER:   \oldendverbatim\endsnugshade
#+LATEX_HEADER: }
"""



def color_of_model(model, inverse=False):
    """
    one function for all places
    """
    es = f"{fx.default}{fg.gray}{bg.default}"
    if model.find("gpt") >= 0:
        es = f"{fx.default}{bg.default}{fg.lightyellow}" # response is in yellow
        if inverse:
            es = f"{fx.default}{fg.black}{bg.lightyellow}" # response is in yellow
    elif model.find("o1") >= 0:
        es = f"{fx.default}{bg.default}{fg.gold}" # response is in
        if inverse:
            es = f"{fx.default}{fg.black}{bg.gold}" # response is in
    elif model.find("o3") >= 0:
        es = f"{fx.default}{bg.default}{fg.khaki}" # response is in
        if inverse:
            es = f"{fx.default}{fg.black}{bg.khaki}" # response is in
    elif model.find("claude") >= 0:
        es = f"{fx.default}{bg.default}{fg.aquamarine}" # response is in
        if inverse:
            es = f"{fx.default}{fg.black}{bg.aquamarine}" # response is in
    elif model.find("gemini") >= 0:
        es = f"{fx.default}{bg.default}{fg.plum}" # response is in
        if inverse:
            es = f"{fx.default}{fg.black}{bg.plum}" # response is in
    else:
        es = f"{fx.default}{bg.default}{fg.palegreen}" # response is in
        if inverse:
            es = f"{fx.default}{fg.black}{bg.palegreen}" # response is in

    return es




if __name__ == "__main__":
    print("i... in the __main__ of unitname of cmd_ai")
    Fire()
