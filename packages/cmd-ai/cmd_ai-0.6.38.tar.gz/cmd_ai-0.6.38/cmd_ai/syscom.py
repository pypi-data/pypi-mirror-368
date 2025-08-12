#!/usr/bin/env python3
"""
We create a unit, that will be the test_ unit by ln -s simoultaneously. Runs with 'pytest'
"""
import sys
import subprocess as sp
from console import fg,bg,fx
from fire import Fire
import os
from cmd_ai import config, texts, best_examples
from cmd_ai.version import __version__
import json
# print("v... unit 'unitname' loaded, version:",__version__)
from cmd_ai import operate_context_files


def list_models():
    models = config.client.models.list()
    print(f"i... listing {len(models.data)} models")
    mids = []
    for i in models.data:
        #if i.id.find("gpt") >= 0:
        mids.append(i.id)
    for i in sorted(mids):
        print("   ", i)
    print("__________________ extra anthropic ___")
    print( "claude-3-7-sonnet-20250219" )
    print( "claude-3-5-sonnet-20241022")
    print("__________________ extra gemini    ___")
    print("gemini-2.5-pro-exp-03-25         (expired)")
    print("gemini-2.5-pro-preview-03-25     (to use)")
    print("__________________ big three   ___")
    print("big2   big3 big4" )
    print(" ... current+ claude37 +gemini25 +o3mini")

def process_syscom(cmd):
    # ***************************************
    if cmd.strip() == ".q":
        sys.exit(0)

    # ***************************************
    elif cmd.strip() == ".h":
        print(texts.HELP)
        print("_______________")
        print(best_examples.main())


    # ***************************************
    elif cmd.strip() == ".e":


        # ANY ROLE, just source--------------------------------------------
        if config.SOURCECODE_EXISTS:
            OUTFILE = operate_context_files.get_filename_my_sourcecode()
            #f"{config.CONFIG['sourcecode']}.{config.CONFIG['sourcecodeext']}"
            # print(OUTFILE)
            if os.path.exists(OUTFILE): # and input("RUN THIS?  y/n  ")=="y":
                print(" ... extension to process :  ",config.CONFIG['sourcecodeext'])
                if config.CONFIG['sourcecodeext']=="dot":
                    # Graphviz.
                    print("i... producing dot.png with graphiz" )
                    outpng = operate_context_files.get_filename_my_png() #"/tmp/cmd_ai_dot.png"
                    sp.run(['dot','-Tpng', OUTFILE, "-o", outpng])
                    print("i... showing with dot.png display " )
                    sp.run(['geeqie', outpng])
                    #dot -Tpng dd.dot -o dd.png
                elif config.CONFIG['sourcecodeext']=="python" or (config.CONFIG['sourcecodeext']=="py"):
                    # -- fixing PEP 668
                    pin = "python3"
                    if "python_interpretter" in config.CONFIG:
                        pin = config.CONFIG["python_interpretter"]
                        if os.path.exists(os.path.expanduser(pin)):
                            pin = os.path.expanduser(pin)
                        else:
                            pin = "python3"
                    print("D... using ", pin)
                    sp.run([pin, OUTFILE ])
                    #dot -Tpng dd.dot -o dd.png
                elif config.CONFIG['sourcecodeext']=="bash":
                    sp.run(['chmod','+x', OUTFILE ])
                    sp.run(['bash','-c', OUTFILE ])
                    #dot -Tpng dd.dot -o dd.png
                elif config.CONFIG['sourcecodeext']=="latex":
                    #sp.run(['chmod','+x', OUTFILE ])
                    sp.run(['pdflatex', OUTFILE ])
                    #dot -Tpng dd.dot -o dd.png
                else:
                    print("X... undefined extension of:", OUTFILE," ->",config.CONFIG['sourcecodeext'] )
            else:
                print(f"X... file {OUTFILE} not found")
        else:
            print("X...  seems that there is no /active script/ flag. Sorry ")

    # ***************************************
    elif cmd.strip() == ".r":
        print(f"i...  {bg.green}{fg.white} RESET {bg.default}{fg.default}")

        #print(f"i... My name is {fg.palegreen}{config.CONFIG['current_name']}{fg.default} and I remember {fg.palegreen}nothing{fg.default} from previous conversations. My role is {fg.palegreen}assistant{fg.default}")

        print(f"i... My name is {fg.palegreen}{config.CONFIG['current_name']}{fg.default}, I remember {fg.orange}0{fg.default} lines from previous conversation. Model is currently {fg.palegreen}{config.MODEL_TO_USE}{fg.default}")

        config.messages = ['You are  useful assistant']  # i hope it automaticall assigns a role
        config.messages[0]={"role": "assistant", "content": texts.role_assistant}
        config.PYSCRIPT_EXISTS = False
        config.SHSCRIPT_EXISTS = False
        config.gemini_chat = None # RESET GLOBAL GEMINI

    # ***************************************
    elif cmd.strip().find(".l")==0 and len(cmd.strip().split(" "))==1:
        print(f'i... limit tokens = {config.CONFIG["limit_tokens"]}')
    elif cmd.strip().find(".l")==0 and len(cmd.strip().split(" "))>1:
        print(f'i... limit tokens = {config.CONFIG["limit_tokens"]}')
        if len(cmd.strip())>4 :
            tk = int(cmd.strip().split(" ")[-1])
            config.CONFIG["limit_tokens"] = tk
            print(f'i... limit tokens = {config.CONFIG["limit_tokens"]}')


    # *************************************** show models
    elif cmd.strip() == ".m":
        list_models()
    elif cmd.strip().find(".m") == 0:
        selmod = cmd.strip().split(".m")[-1]
        selmod = "".join(selmod)
        config.MODEL_TO_USE = selmod
        print(f"{bg.darkorange3}{fg.white}i... new model : {config.MODEL_TO_USE} ", bg.default, fg.default)
        # RESET
        config.messages = ['You are  useful assistant']  # i hope it automaticall assigns a role
        config.messages[0]={"role": "assistant", "content": texts.role_assistant}
        config.PYSCRIPT_EXISTS = False
        config.SHSCRIPT_EXISTS = False


    # ***************************************
    # ***************************************
    #  ROLES: I cant just append a role.... he sees te original all the time
    # ***************************************
    # ***************************************
    elif cmd.strip() == ".p":
        print(f"i...  {bg.green}{fg.white} Python expert {bg.default}{fg.default}")

        #config.messages=[]
        config.messages = [{"role": "assistant", "content": texts.role_pythonista}]
        config.CONFIG["current_role"] = "pythonista"

    # # *************************************** shell expert
    # elif cmd.strip() == ".s":
    #     print(f"i...  {bg.green}{fg.white} Shell expert {bg.default}{fg.default}")
    #     if len(config.messages)>0:
    #         config.messages=[{"role": "assistant", "content": "You speak briefly, in short sentences."} ]
    #     else:
    #         config.messages.append({"role": "assistant", "content": texts.role_sheller})
    #     config.CONFIG["current_role"] = "sheller"


    # *************************************** dalle - no need of content....
    elif cmd.strip() == ".d":
        print(f"i...  {bg.green}{fg.white} DALLE expert {bg.default}{fg.default}")
        if len(config.messages)>0:
            config.messages[0]={"role": "assistant", "content": texts.role_dalle}
        else:
            config.messages.append({"role": "assistant", "content": texts.role_dalle})

        config.CONFIG["current_role"] = "dalle"

    # *************************************** vision ... no need of content...
    elif cmd.strip() == ".i":
        print(f"i...  {bg.green}{fg.white} VISION expert {bg.default}{fg.default}")
        if len(config.messages)>0:
            config.messages[0]={"role": "assistant", "content": texts.role_vision}
        else:
            config.messages.append({"role": "assistant", "content": texts.role_vision})

        config.CONFIG["current_role"] = "vision"

    # *************************************** translator
    elif cmd.strip() == ".t":
        print(f"i...  {bg.green}{fg.white} Translator from english to czech - or czech to english {bg.default}{fg.default}")
        if len(config.messages)>0:
            config.messages[0]={"role": "assistant", "content": texts.role_translator}
        else:
            config.messages.append({"role": "assistant", "content": texts.role_translator})

        config.CONFIG["current_role"] = "translator"

    # *************************************** assistant
    elif cmd.strip() == ".a":
        print(f"i...  {bg.green}{fg.white} Brief assistant {bg.default}{fg.default}")
        if len(config.messages)>0:
            config.messages[0]={"role": "assistant", "content": texts.role_assistant}
        else:
            config.messages.append({"role": "assistant", "content": texts.role_assistant})

        config.CONFIG["current_role"] = "assistant"


    # *************************************** assistant
    elif cmd.strip() == ".s":
        print(f"i...  {bg.green}{fg.white} Secretary {bg.default}{fg.default}")
        if len(config.messages)>0:
            config.messages[0]={"role": "assistant", "content": texts.role_secretary}
        else:
            config.messages.append({"role": "assistant", "content": texts.role_secretary})

        config.CONFIG["current_role"] = "secretary"





    # *************************************** help
    elif cmd.strip() == ".h":
        print(texts.HELP)

    # *************************************** help
    elif cmd.strip() == ".v":
        config.READALOUD+=1
        modu = config.READALOUD%len(config.READALOUDSET)
        print(f"i...  {bg.green}{fg.white} Reading Aloud is {config.READALOUDSET[modu]} {bg.default}{fg.default}")
        #print("i... reading disabled...")

    # # *************************************** google functions  NEEDS TO UPGRADE googlesearch-python
    # elif cmd.strip() == ".g":
    #     if len(config.TOOLLIST)==0:
    #         print(f"i...  {bg.green}{fg.white} google search functions + meeting record ON {bg.default}{fg.default}")
    #         config.TOOLLIST = [  texts.tool_searchGoogle, texts.tool_getWebContent, texts.tool_setMeetingRecord, texts.tool_getTodaysDateTime]
    #         for i in config.TOOLLIST:
    #             print(" ... ",i['function']['name'])
    #     else:
    #         print(f"i...  {bg.red}{fg.white} google search functions OFF NOW {bg.default}{fg.default}")
    #         config.TOOLLIST = []

    # *************************************** utility/test functions
    elif cmd.strip() == ".g":
        if len(config.TOOLLIST)==0:
            print(f"i...  {bg.green}{fg.white} TOOLS functions ON {bg.default}{fg.default}")
            config.TOOLLIST = [ texts.tool_getCzechWeather,
                                texts.tool_setMeetingRecord,
                                texts.tool_sendGmail,
                                texts.tool_getTodaysDateTime,
                                texts.tool_searchGoogle,
                                texts.tool_getWebContent,
                                texts.tool_getNehody,
                                texts.tool_callSympy]
            for i in config.TOOLLIST:
                if config.DEBUG: print(" ... ",i['function']['name'])
        else:
            print(f"i...  {bg.darkorange3}{fg.white} TOOLS functions OFF NOW {bg.default}{fg.default}")
            config.TOOLLIST = []



    # ***************************************
    else:
        print(f"!... {fg.red} unknown system command {fg.default}")


if __name__ == "__main__":
    print("i... in the __main__ of unitname of cmd_ai")
    Fire()
