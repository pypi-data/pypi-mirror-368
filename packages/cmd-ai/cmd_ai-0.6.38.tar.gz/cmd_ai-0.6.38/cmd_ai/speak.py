#!/usr/bin/env python3
"""
We create a unit, that will be the test_ unit by ln -s simoultaneously. Runs with 'pytest'
"""
from fire import Fire

from cmd_ai import config
from cmd_ai.version import __version__
import os
# from playsound import playsound # some problem with uv uvx
import time
from gtts import gTTS
import hashlib

import sys
from console import fg,bg,fx
import multiprocessing


#   pip install unidecode
from unidecode import unidecode
import signal

import subprocess as sp
import shlex

# Handler function to be called when the alarm signal is received
def timeout_handler(signum, frame):
    raise TimeoutError

def input_expiring(txt):
    # Set the signal handler for the SIGALRM signal
    signal.signal(signal.SIGALRM, timeout_handler)
    user_input = None
    try:
        # Set the alarm for 1 second
        signal.alarm(1)
        print("",end="\r")
        user_input = input( txt )
        signal.alarm(0)  # Cancel the alarm
        print("(-)")
        #print(f"You entered: {user_input}")
    except TimeoutError:
        #print("Sorry, time is up")
        pass
    return user_input


def getHash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def getSize(filename):
    st = os.stat(filename)
    return st.st_size


def TRANSLATE(text, outname, lang="cs", path="/tmp/"):
    tts=None
    maxtries=5
    while maxtries>0:
        print("i... translating", end=" ", flush=True)
        try:
            tts = gTTS( text , lang=lang)
            maxtries=-5
        except:
            maxtries-=1
            print("X... PROBLEM WITH CONNECTION?. NO TTS TRYING IN 1 MINUTE, try#",maxtries)
            time.sleep(60)
    if maxtries==0:
        print("X... maxtries exhaused. quit.")
        sys.exit(1)
    # if maxtries==-5: ok

    try:
        os.mkdir(path)
    except:
        print(end="\r")

    #print("D... saving {}        ".format(outname) )
    tts.save( outname )
    return



#==============================================
#
#
def str_to_mp3( text,  path="/tmp/tts_one_sentence" , readme=False, lang="cs"):
    """
    this will save or not
    """
    # remove cases with signle ?,?
    chktext=text
    chktext=chktext.replace("?","")
    chktext=chktext.replace("!","")
    chktext=chktext.replace(".","")
    chktext=chktext.replace(",","")
    chktext=chktext.replace(" ","")
    if len(chktext)<2:
        print("X... WHY THIS SHORT SENTENCE? /{}/".format(text))
        return False

    #------- create mp3 filename------+ check FNAME chars.
    #w=text.strip().split(" ")[0]
    w=text[:32]
    w=w.replace("/","_")
    w=w.replace(" ","_")
    #outname="{}/{:06d}_{}".format( path, n, w )


    HS=getHash(text)[:8] # first 8== > 4 bilions possibilities
    w = unidecode(w) # ALL ASCII
    outname=f"{path}/{w}_{lang}_{HS}" # .format( path, n, w )
    # print(outname)


    badchar=" !-,.–… ?:--«»()‘…{}\"'"  # canbe /_
    for i in range(len(badchar)):
        outname=outname.replace( badchar[i] ,"_")

    #---------------------------remove nonascii ??? badway
    outname=''.join([i if ord(i) < 128 else '_' for i in outname])
    #-----------------------if zero add smthng
    #print("/{}/".format(w) )
    if len(w)==0:outname=outname+"_"
    outname=outname+".mp3"
    #============================== FNAmE OK


    #------------------------------ check if exists and is ok size
    CREATENEW = False
    if  os.path.isfile( outname ):
        # this was earlier ment to restart a book
        if getSize( outname )<100:
            print(f"X... file exists...size LESS THAN 100 = {fg.red}PROBLEM{fg.default}", outname)
            CREATENEW = True
        else:
            print(f"i... {fg.yellow}reusing the file{fg.default}", outname)
            CREATENEW = False
    else:
        print(f"i... {fg.green}creating new file:{fg.default}", outname)
        CREATENEW = True
    #--------------------------------------DONE


    #print("{:06d} {}".format(n,text) )
    #print("{}".format(text) )
    if CREATENEW:
        TRANSLATE( text, outname, lang=lang, path=path)

    if readme:

        #p = multiprocessing.Process(target=playsound, args=(outname,))
        #p.start()
        #while p.is_alive():
        #    r = input_expiring(f"{fx.italic}press ENTER to stop playback{fx.default}")
        #    if r is not None: break
        #p.terminate()
        #print("x...  playsound not used as there is a problem with uv uvx")
        CMD = f"mpv --speed=1.4 {outname}"
        CMD = shlex.split(CMD)
        res = sp.Popen(CMD, stdout=sp.DEVNULL, stderr=sp.DEVNULL )
        #print(CMD, res)
        #playsound(outname)

    return True

    #tts.write_to_fp(sodata)
    #loop = AudioSegment.from_wav("metallic-drums.wav")
    #song = AudioSegment.from_file( BytesIO( sodata ), format="mp3")
    #song.export("outname", format="mp3")
    #data = open( outname , 'rb').read()
    #song = AudioSegment.from_file( io.BytesIO(data), format="mp3")
    #play(song)





# print("v... unit 'unitname' loaded, version:",__version__)

def main( text):
    print("~ ~ ~ speaking ...")
    str_to_mp3( text,  readme=True)

if __name__ == "__main__":
    print("i... in the __main__ of speak of cmd_ai")
    Fire(main)
