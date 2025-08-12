#!/usr/bin/env python3

import datetime as dt
import time
import os
import tiktoken
from console import fg,bg,fx
from fire import Fire
import pandas as pd
import sys
import json # for function call
from fire import Fire

import openai # for errors
from openai import OpenAI
from console import fg, bg, fx

from cmd_ai import config, texts, api_key
from cmd_ai import function_chmi, function_goog, function_webc, function_calendar, function_gmail, function_sympy, function_nehody


import anthropic
from cmd_ai import api_key
#import get_api_key_anthropic

# NATIVE GOOGLE GEMINI API
from google import genai # uv pip install google.genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

########################################################
config.available_functions = {
    "getCzechWeather": function_chmi.get_chmi, #
    "searchGoogle": function_goog.get_google_urls, #
    "getWebContent": function_webc.fetch_url_content, #
    "getNehody": function_nehody.check_web_nehody, #
    "setMeetingRecord": function_calendar.setMeetingRecord, # i
    "sendGmail": function_gmail.sendGmail, #
    "getTodaysDateTime": function_calendar.getTodaysDateTime, #
    "callSympy": function_sympy.callSympy, #
}


# ===========================================================================
#   generated :  calculate price   GENERATED FROM ORG FILE
# ---------------------------------------------------------------------------
def get_price(model_name, input_tokens=0, output_tokens=0):
    """
    generated from the org  table by AI
    """
    data = {'Model': ['gpt-4o', 'gpt-4o-2024-08-06', 'gpt-4o-2024-11-20', 'gpt-4o-2024-08-06', 'gpt-4o-2024-05-13', 'gpt-4o-audio-preview', 'gpt-4o-audio-preview-2024-12-17', 'gpt-4o-audio-preview-2024-12-17', 'gpt-4o-audio-preview-2024-10-01', 'gpt-4o-realtime-preview', 'gpt-4o-realtime-preview-2024-12-17', 'gpt-4o-realtime-preview-2024-12-17', 'gpt-4o-realtime-preview-2024-10-01', 'gpt-4o-mini', 'gpt-4o-mini-2024-07-18', 'gpt-4o-mini-2024-07-18', 'gpt-4o-mini-audio-preview', 'gpt-4o-mini-audio-preview-2024-12-17', 'gpt-4o-mini-audio-preview-2024-12-17', 'gpt-4o-mini-realtime-preview', 'gpt-4o-mini-realtime-preview-2024-12-17', 'gpt-4o-mini-realtime-preview-2024-12-17', 'o1', 'o1-2024-12-17', 'o1-2024-12-17', 'o1-preview-2024-09-12', 'o1-mini', 'o1-mini-2024-09-12', 'o1-mini-2024-09-12', 'o3-mini-2025-01-31', 'gpt-4.5-preview', 'gpt-4.5-preview-2025-02-27', 'gpt-4.1-mini', 'gpt-4.1'], 'Input Price': [2.5, 2.5, 2.5, 2.5, 5.0, 2.5, 2.5, 2.5, 2.5, 5.0, 5.0, 5.0, 5.0, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.6, 0.6, 0.6, 15.0, 15.0, 15.0, 15.0, 3.0, 3.0, 3.0, 1.1, 75.0, 75.0, 0.4, 2.0], 'Output Price': [10.0, 10.0, 10.0, 10.0, 15.0, 10.0, 10.0, 10.0, 10.0, 20.0, 20.0, 20.0, 20.0, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 2.4, 2.4, 2.4, 60.0, 60.0, 60.0, 60.0, 12.0, 12.0, 12.0, 4.4, 150.0, 150.0, 1.6, 8.0]
             }
    df = pd.DataFrame(data)
    model_row = df[df['Model'] == model_name]

    if model_row.empty:
        return 0 #"Model not found."

    input_price = model_row['Input Price'].values[0]
    output_price = model_row['Output Price'].values[0]

    total_price = (input_tokens / 1_000_000) * input_price + (output_tokens / 1_000_000) * output_price

    return total_price



# ===============================================================================================
def log_price(model, tokens_in = 1, tokens_out = 1):
    price = round(100000*get_price( model, tokens_in, tokens_out ))/100000
    with open( os.path.expanduser( config.CONFIG['pricelog']), "a" )  as f:
        now = dt.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        f.write(f"{now} {tokens_in} {tokens_out} {price}")
        f.write("\n")


# ###================================================================================


#     # ========================================================================



def announce_model(model):
    """
    same printout for all
    """
    #print("...",bg.green," >>OK", bg.default, f" model={model}")
    print(fg.dimgray, "... ... ... ... ...  model=",texts.color_of_model(model, inverse=True), model, fg.default, bg.default)



def execute_function_call(function_name,arguments):
    """
    colorful call ...
    """
    print("i... executing  ", bg.darkorange3, fg.white, function_name, bg.default, fg.default, arguments)
    function = config.available_functions.get(function_name,None)
    if function:
        #print("i+++ executing function:   ", function_name)
        arguments = json.loads(arguments)
        #if config.DEBUG: print("i--- running ", arguments )
        results = function(**arguments)
        #print("r... results size=", sys.getsizeof(results))
    else:
        print("X---  executing function:   ", function_name)
        results = f"Error: function {function_name} does not exist"
    return results



# ============================================================
#    for debugging
# ------------------------------------------------------------
#
def xprint(x, style, level=0):
    SPC = " " * level * 5
    #print(f"{SPC}============================================================")
    print(style, end="")
    print( f"{SPC} DDD {x}", fg.default, bg.default, fx.default)
    #print()
    #print("------------------------------------------------------------")


#
#
#
#


#
# ============================================================
#    CHATGPT
# --------------------------------------------------------------
#
def g_ask_gptchat_new(prompt, temp,model,
                  dontadd=False):
#def main():
    """
    ************************************ MAIN FUNCTION FOR CHAAT **********
    RETURNS :  response, reason_to_stop,  model_used
    """
    if config.client is None:
        config.client = OpenAI(api_key=api_key.get_api_key())

    #print("----------------->>> config DEBUG", config.DEBUG)
    newmsg = [] # this is total copy o config.messages
    additional_msg = [] # this is stuff to add to config.messages

    #print(fg.springgreen, config.messages, fg.default)

    for i in config.messages:
        #print("D...", type(i), i)
        #if i["role"] == "assistant": continue
        newmsg.append( i )

    # ---- if no system present, add it
    if len(config.messages) == 0:
        newmsg.append({"role": "assistant", "content": texts.role_assistant})
        additional_msg.append( {"role": "assistant", "content": texts.role_assistant}  ) # later to append to config.messages
    # add the message~
    #if tool:
    #    print("X... THIS NEVER HAPPENS .... TOOL TRUE.... ")
    #    newmsg.append( prompt )
    #else:
    newmsg.append({"role": "user", "content": prompt})
    additional_msg.append( {"role": "user", "content": prompt} ) # later to append to config.messages

    # -------------------  newmsg done

    # # assure the starting conditions *********** added for g_ask.
    # if len(config.messages) == 0:
    #     config.messages.append({"role": "assistant", "content": texts.role_assistant})
    # # ADD PROMPT
    # config.messages.append({"role": "user", "content": prompt})

    limit_tokens = config.CONFIG['limit_tokens']
    if limit_tokens < 30000: # ;max_tokens
        max_tokens = limit_tokens
    else:
        max_tokens = 300

    # FORCE MODEL TO SYNC # NO  DONOT ***********
    #config.MODEL_TO_USE = model


    # ----------------------------- DEBUGS ------------------

    PRINT_FULL_MESSAGES = False
    PRINT_RESPONSES = False # aqua ChatCompletion()   when tool is required
    # always print reason
    PRINT_TOOL_RESULTS = False # PINK  n: [ tool list ]
    if config.DEBUG:
        PRINT_FULL_MESSAGES = True
        PRINT_RESPONSES = True # aqua ChatCompletion()   when tool is required
        # always print reason
        PRINT_TOOL_RESULTS = True # PINK  n: [ tool list ]


    # my statistics
    ntoolcalls = 0
    toolcalls_datasize = 0
    total_tokens_in = 0
    total_tokens_out = 0



    # IMPORTANT THINGS variables used over the function
    resp_content = "nil"
    resp_reason = "x"
    tokens_out = 0
    tokens_in = 0
    tokens = 0

    ### ENTRY POINT FOR LOOP
    KEEP_LOOPING = True
    while KEEP_LOOPING:
        #xprint(config.messages[-1], fg.cyan)

        if PRINT_FULL_MESSAGES:
            #xprint(config.messages, fg.white)
            xprint(newmsg, fg.pink)

        responded = False
        response = None
        kill_me_on_0 = 3
        #print("D...    ************ DEBUG new")
        try:
            # MODEL
            if (model.find("o1") == 0) or (model.find("o3") == 0) or (model.find("o4") == 0):
                #print("D... MODEL o134 ", model)
                response = config.client.chat.completions.create( #aks_gpt_chat_new
                    model=model,
                    messages=newmsg
                    #tool_choice="auto",
                    #tools= config.TOOLLIST
                    )
            elif model.find("gpt-4o")==0:  # not o. they dont know tools
                #print("D... MODEL 4o ", model)
                response = config.client.chat.completions.create( #aks_gpt_chat_new
                    model=model,
                    messages=newmsg,
                    #tool_choice="auto",
                    #tools= config.TOOLLIST
                    )
            elif (model.find("gpt-4.1")==0) or (model.find("gpt-4-")==0) or (model == "gpt-4") :
                #print("D... MODEL 41* ", model)
                response = config.client.chat.completions.create( # ask_gpt_chat_new
                    model=model,
                    messages=newmsg, #config.messages,
                    temperature=temp,
                    max_tokens=max_tokens,
                    tool_choice="auto",
                    tools= config.TOOLLIST
                )
            elif (model.find("gpt-5") == 0):#
                #print("D... MODEL 5 ", model)
                response = config.client.chat.completions.create( #aks_gpt_chat_new
                    model=model,
                    messages=newmsg,
                    tool_choice="auto",
                    tools= config.TOOLLIST
                    #tool_choice="auto",
                    #tools= config.TOOLLIST
                )
            else:# o3-mini-2025-01-31   had some problem with tools??
                #print("D... MODEL ?? ", model)
                response = config.client.chat.completions.create( #aks_gpt_chat_new
                    model=model,
                    messages=newmsg,
                    #tool_choice="auto",
                    #tools= config.TOOLLIST
                )
            responded = True

        except openai.RateLimitError as e:
            if hasattr(e,"code"): print("  rateLimit...", e.code)
            if hasattr(e,"type"): print("  rateLimit...", e.type)
            print(f"Rate limit exceeded. Retrying in 5 seconds...")
            time.sleep(5)
            kill_me_on_0 -= 1

        except openai.APIError as e:
            if hasattr(e,"code"): print(" ... API - error code:", e.code)
            if hasattr(e,"type"): print(" ... API - error type:", e.type)
            print(f" ... API error occurred. Retrying in 5 seconds...")
            print(" ... ... might be for difficulties when calling a tool? Unallowd options?")
            time.sleep( 5)
            kill_me_on_0 -= 1

        except openai.ServiceUnavailableError as e:
            if hasattr(e,"code"): print(" ...ServiceUnavailable...", e.code)
            if hasattr(e,"type"): print(" ...ServiceUnavailable...", e.type)
            print(f"Service is unavailable. Retrying in 5 seconds...")
            time.sleep(5)
            kill_me_on_0 -= 1

        except openai.Timeout as e:
            if hasattr(e,"code"): print("... Timeout...", e.code)
            if hasattr(e,"type"): print("... Timeout...", e.type)
            print(f"Request timed out: {e}. Retrying in 5 seconds...")
            time.sleep(5)
            kill_me_on_0 -= 1

        except OSError as e:
            if isinstance(e, tuple) and len(e) == 2 and isinstance(e[1], OSError):
                if hasattr(e,"code"): print("... OSError...", e.code)
                if hasattr(e,"type"): print("... OSError...", e.type)
                print(f"Connection error occurred: {e}. Retrying in 5 seconds...")
                time.sleep(5)
                kill_me_on_0 -= 1
            else:
                print(f"Connection error occurred: {e}. Retrying in 5 seconds...")
                time.sleep(5)
                kill_me_on_0 -= 1
                raise e

        if kill_me_on_0 <= 0:
            sys.exit(1)

        if not responded:
            continue

        # ALL EXCEPTIONS DONE AND SOLVED **********************
        if PRINT_FULL_MESSAGES:
            xprint(response, fg.white + fx.italic)

        resp_content = response.choices[0].message.content # when no tools
        resp_reason = response.choices[0].finish_reason
        tokens_out = response.usage.completion_tokens
        tokens_in = response.usage.prompt_tokens
        total_tokens_in += tokens_in
        total_tokens_out += tokens_out
        tokens = response.usage.total_tokens



        if resp_reason != "stop": # Dont report standard stop reason
            if resp_reason != "tool_calls":
                xprint(resp_reason, fg.red) # always print reason

        # ****************** TOOLCALLS*******************
        # ****************** TOOLCALLS*******************
        # ****************** TOOLCALLS*******************
        if resp_reason == "tool_calls" and len(config.TOOLLIST) > 0:
            resp_message = response.choices[0].message
            tool_calls = response.choices[0].message.tool_calls
            if PRINT_RESPONSES:
                xprint(resp_message, fg.aquamarine)

            ###---
            newmsg.append(   resp_message  )
            additional_msg.append(  resp_message   )
            # config.messages.append( resp_message ) # ASPPENDING THIS TO CHAT!!!

            if PRINT_TOOL_RESULTS:
                xprint(f" {len(tool_calls)}: {tool_calls}", fg.pink)
            if len(tool_calls) > 0 and len(config.TOOLLIST) > 0:
                for tool_call in tool_calls:
                    fun_name = tool_call.function.name
                    fun_to_call = config.available_functions[fun_name]
                    fun_args = tool_call.function.arguments # NO json.loads
                    fun_response = execute_function_call( fun_name, fun_args  )
                    ntoolcalls += 1
                    toolcalls_datasize += sys.getsizeof(fun_response)
                    #
                    #if len(fun_response) > 1000:
                    #    run_response = fun_response[:1000]
                    #
                    #xprint(fun_response, fg.lime, level=1) # this is just my function output....
                    GEN_MESSAGE = {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": fun_name,
                        "content": fun_response,
                    }
                    newmsg.append(GEN_MESSAGE)
                    additional_msg.append(GEN_MESSAGE)
                    #    config.messages.append( GEN_MESSAGE ) # ASPPENDING THIS TO CHAT!!!

                # NOW ALL TOOL CALLS ARE FINISHED.....
                # xprint(config.messages, fg.orchid)
                # response = config.client.chat.completions.create(
                #     model=model,
                #     messages=config.messages,
                #     temperature=temp,
                #     max_tokens=max_tokens,
                #     tool_choice="auto",
                #     tools= config.TOOLLIST
                # )
                # xprint(response, fg.white)
                # resp_content = response.choices[0].message.content
                # resp_reason = response.choices[0].finish_reason
                # xprint(resp_content, fg.orange)
                # xprint(resp_reason, fg.red)
                # GOES TO WHILE START
            else:
                print("X... tools requested but ???... no tool_calls prepared ???")
                KEEP_LOOPING = False
                sys.exit(1)
        # ------ END OF TOOL CALLS -------------
        elif resp_reason == "stop":
            KEEP_LOOPING = False # go home after all done
            # add non tools response:
            if resp_content is not None: # Dont report None conntent....it is tools....
                newmsg.append( {"role": "assistant", "content":  resp_content } )
                additional_msg.append( {"role": "assistant", "content":  resp_content } )
                if PRINT_RESPONSES:
                    xprint(resp_content, fg.coral)
        else:
            print("X... other reason ... resp_reason == {resp_reason} ")
            KEEP_LOOPING = False # go home after all done



    # ----------------- While loop ends here ------------------------
    price = get_price( model, total_tokens_in, total_tokens_out)

    print(f"{fg.dimgray}i... TOOLS={ntoolcalls};  ... TOTAL data size {toolcalls_datasize}    total tokens={total_tokens_in+total_tokens_out} for {price:.4f} $ {fg.default}")

    log_price( model, total_tokens_in, total_tokens_out )
    #xprint(resp_content, fg.lime) # REAL LAST RESPONSE
    if not config.silent:
        announce_model(model)

    #print(config.messages)
    if not dontadd: #
        for i in additional_msg:
            #print(f"DDD APPEDING: /{type(config.messages)}/" )
            #print(f"DDD APPEDING: /{i}/" )
            config.messages.append( i ) # ASPPENDING THIS TO CHAT!!!
            #print()
            #print(config.messages)
            #print()

    return resp_content, resp_reason, model








# ============================================================
#
# ------------------------------------------------------------
#



# model="claude-3-7-sonnet-20250219"
# model="claude-3-5-sonnet-20241022"
# ============================================================
#    ANTHROPIC return resp_content, resp_reason, config.MODEL_TO_USE
# ------------------------------------------------------------
#
def g_ask_claude(prompt ,
                 temp=0,
                 model="claude-3-7-sonnet-20250219",
#                 model="claude-3-5-sonnet-20241022",
                 #role=None,
                 dontadd=False):
    STOPPED_BY_LENGTH = False
    # ** init
    APIKEY = api_key.get_api_key_anthropic()
    if APIKEY is None:
        return "failed", "failed", model
    clienta = anthropic.Anthropic(api_key=APIKEY)

    system_prompt = texts.role_assistant
    #if role is None:
    #    system_prompt = texts.role_assistant
    # my message system (may be difference in naming)
    nmsg = []
    for i in config.messages:
        nmsg.append( i )

    nmsg.append({"role": "user", "content": [{"type": "text", "text": prompt}] } )
    limit_tokens = config.CONFIG['limit_tokens']

    #********************************************** GO
    message = clienta.messages.create(
        model=model,
        max_tokens=limit_tokens,
        temperature=temp,
        system=system_prompt,
        messages=nmsg
    )
    # **********
    response = message.content
    res = response[0].text #decode_response_anthropic(message.content)

    # i just add prompt and answer here....bug until 20250405
    if not dontadd:
        config.messages.append(  {"role": "user", "content": prompt} )
        config.messages.append(  {"role": "assistant", "content": res} )

    if not config.silent:
        announce_model(model)
        #print("...",bg.green," >>OK", bg.default, f" model={model}") # claude
    return res, STOPPED_BY_LENGTH, model





# ============================================================
#    GOOGLE GEMINI return resp_content, resp_reason, config.MODEL_TO_USE
# ------------------------------------------------------------
#
def g_ask_gemini(prompt ,
                 temp=0,
                 model="gemini-2.5-pro-exp-03-25",
#                 max_tokens=1000,
#                 role=None,
                 dontadd=False):
    APIKEY = api_key.get_api_key_gemini()
    if APIKEY is None:
        return "failed", "failed", model
    STOPPED_BY_LENGTH = False
    # ** init

    system_prompt = texts.role_assistant
    #if role is None:
    #    system_prompt = texts.role_assistant
    newmsg = []

    for i in config.messages:
        newmsg.append( i )
    newmsg.append(  {"role": "user", "content": prompt} )

    if not dontadd:
        config.messages.append(  {"role": "user", "content": prompt} )

    #newmsg.append({"role": "user", "content": [{"type": "text", "text": prompt}] } )
    limit_tokens = config.CONFIG['limit_tokens']
    # GEMINI HAS PROBLEM with limits
    #limit_tokens = 3500 + limit_tokens

    limit_tokens = limit_tokens + 2500 + int(sys.getsizeof(newmsg) / 2)# in bytes... tokens is always less.
    if config.DEBUG:
        print("D... tokens in gemini: ", limit_tokens)
        print(fg.pink, newmsg, fg.default)


    res = ""
    # NATIVE GEMINI  API STYLE -------------------------------------------------------
    NATIVE = True
    if NATIVE:
        client = genai.Client(api_key=APIKEY)


        google_search_tool = Tool(
            google_search = GoogleSearch()
        )

        if config.gemini_chat is None:
            config.gemini_chat = client.chats.create(model=model)

        response = config.gemini_chat.send_message(prompt, config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        )
        )
        res = ""
        for i in  response.candidates[0].content.parts:
            res = f"{res}\n{i.text}"

        #res = response.text # chat..
        # response = client.models.generate_content(
        #     model=model,
        #     #contents=["How does AI work?"]
        #     contents=newmsg
        # )
        # #print(response.text)
        # res = response.text

    else:
        # OPENAI _ API STYLE -------------------------------------------------------
        clientg = openai.OpenAI( api_key= APIKEY,
                          base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
                         )

        #************ GO
        try:
            message = clientg.chat.completions.create(
                model=model,
                max_tokens=limit_tokens,
                temperature=temp,
                messages=newmsg
            )
        except Exception as e:
            print(fg.red, f"X... {e.message}", fg.default)
            return "Failed to answer", True

        # DONE ******
        if config.DEBUG: print(fg.cyan, message, fg.default)

        if message.choices is None:
            print(fg.red,"D... NO RESPONSE.... CHECK AVAILABLE TOKENS... ", fg.default)
            print(fg.dimgray, message, fg.default)
            return "Failed to answer", True
        response = message.choices[0].message

        #print(fg.lime, response, fg.default)
        res = response.content #[0].text #decode_response_anthropic(message.content)
        #print(fg.yellow, res, fg.default)

    # ================= HERE res contains the response content =====================  RES =====

    if not dontadd: # when big3 big4 used...
        if res is None:
            config.messages.append(  {"role": "assistant", "content": "<Internal error>"} )
        else:
            config.messages.append(  {"role": "assistant", "content": res} )

    if not config.silent:
        announce_model(model)
        #print("...",bg.green," >>OK", bg.default, f" model={model}") # gemini
    return res, STOPPED_BY_LENGTH, model





# ============================================================
#    ANY MODEL LANDING PLACE
# ------------------------------------------------------------
#
def g_ask_anyone(
        prompt,
        temp=0.0,
        model="gpt-4-1106-preview",
        # limit_tokens=300,
        total_model_tokens=4096 * 2 - 50, # guess
        tool = False
):
    """
    CALL g_ask_chat() .... depending on model ask_claude  or ask_chat  or ask_gemini
    """
    print(bg.white, fg.black, "-------", fg.default, bg.default)

    #if model is not None:
    if config.DEBUG:
        print("D... inside g_ask_anyone... DEBUG IS ON, model=", model)
    config.MODEL_TO_USE = model   # HARD SWITCH MODEL

    # #model_change = False
    # if prompt.lower().find("claude,") == 0:
    #     MODEL_TO_USE = "claude-3-5-sonnet-20241022"  # sonnet is fast, may bbe worse in math, good in science
    #     #model_change = True
    # elif prompt.lower().find("opus,") == 0:
    #     MODEL_TO_USE = "claude-3-opus-20240229" # no reason, maybe math+reasoning
    #     #model_change = True
    # elif prompt.lower().find("gpt,") == 0:
    #     MODEL_TO_USE = "gpt-4o-2024-08-06"
    #     #model_change = True
    # else:
    #     MODEL_TO_USE = model

    #estimate_tokens = num_tokens_from_messages() + len(prompt) + 600
    #estimate_tokens = 300
    estimate_tokens = config.CONFIG['limit_tokens']
    #if not config.silent:
    #    print(f"D....  {fg.lightslategray}{fx.italic}g_ask estimate tokens {estimate_tokens}; {MODEL_TO_USE}",fg.default, fx.default)

    resdi = None
    if config.MODEL_TO_USE.find("claude") >= 0:
        #print("C")
        resdi = g_ask_claude( prompt, temp, model=config.MODEL_TO_USE)
    elif config.MODEL_TO_USE.find("gemini") >= 0:
        #print("G")
        resdi = g_ask_gemini( prompt, temp, model= config.MODEL_TO_USE)
        #resdi = g_ask_gemini( prompt, temp, config.MODEL_TO_USE, estimate_tokens, tool=tool )
    elif config.MODEL_TO_USE.find("gpt") >= 0 or config.MODEL_TO_USE.find("o3") == 0 or config.MODEL_TO_USE.find("o1") == 0:
        #print("O")
        #resdi = g_ask_gptchat_new( prompt, temp, config.MODEL_TO_USE, estimate_tokens, tool=tool )
        resdi = g_ask_gptchat_new( prompt, temp, model=config.MODEL_TO_USE )
        #
    elif config.MODEL_TO_USE.find("big") >= 0 : # BIG 2 3 4
        models = [ "gpt-4o-2024-11-20", "claude-3-7-sonnet-20250219", "gemini-2.5-pro-preview-03-25", "o3-mini-2025-01-31"]
        models = [ config.CONFIG['model_to_use'], "claude-3-7-sonnet-20250219", "gemini-2.5-pro-preview-03-25", "o3-mini-2025-01-31"]

        if config.MODEL_TO_USE.find("big2") >= 0:
            models = models[:2]
        elif config.MODEL_TO_USE.find("big3") >= 0:
            models = models[:3]
        elif config.MODEL_TO_USE.find("big4") >= 0:
            pass
        #print(models)
        allresponses = {}
        for tmpmodel in models:
            #print(tmpmodel)
            if tmpmodel.find("claude") >= 0:
                resdi = g_ask_claude( prompt, temp, tmpmodel,  dontadd=True)
            elif tmpmodel.find("gemini") >= 0:
                resdi = g_ask_gemini( prompt, temp, tmpmodel , dontadd=True)
            else:
                resdi = g_ask_gptchat_new( prompt, temp, tmpmodel, dontadd=True )
            allresponses[tmpmodel] = resdi[0]
            print(texts.color_of_model(tmpmodel), resdi[0], fg.default)

        # tmpmodel = "claude-3-7-sonnet-20250219"
        # resdi = g_ask_claude( prompt, temp, tmpmodel,  dontadd=True)
        # print(texts.color_of_model(tmpmodel), resdi[0], fg.default)

        # tmpmodel = "gemini-2.5-pro-exp-03-25"
        # resdi = g_ask_gemini( prompt, temp, tmpmodel , dontadd=True)
        # print(texts.color_of_model(tmpmodel),resdi[0], fg.default)

        # tmpmodel = "gpt-4o-2024-11-20"
        # resdi = g_ask_gptchat_new( prompt,  tmpmodel, dontadd=True )
        # print(texts.color_of_model("gpt"),  resdi[0], fg.default)

        # tmpmodel = "o3-mini-2025-01-31"
        # resdi = g_ask_gptchat_new( prompt,  tmpmodel, dontadd=True )
        # print(texts.color_of_model(tmpmodel),  resdi[0], fg.default)

        # #if config.MODEL_TO_USE.find("big4") >= 0 :
        # #
        resdi = "dialog is not recorded yet", allresponses, config.MODEL_TO_USE
    else:
        print(f"X... {fg.red}not sure that I know this model: {fg.default}", model)
        resdi = None

    #if model_change:
    if resdi is None:
        return None, "no_answer",  config.MODEL_TO_USE
    return resdi[0],resdi[1], config.MODEL_TO_USE
    #return resdi



def main():
    """
    for Fire
    """
    config.client = OpenAI(api_key=api_key.get_api_key())
    g_ask_chat("Hi", model = "gpt-4o-2024-11-20", temp=0)

if  __name__ == "__main__":
    Fire(main)
