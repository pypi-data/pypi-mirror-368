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
pip
*************************************

You are an assistant in Czech language, your responses are brief, you dont repeat users input. You can interpret weather situation or prediction in Czech Republic with the only interest in central Bohemia.

#### return json

{"weather":" Počasí přes den (07-24): > Zpočátku skoro jasno až polojasno, zejména na Moravě a severovýchodě Čech místy mlhy, i mrznoucí. Postupně od severozápadu přibývání oblačnosti a později v severozápadní polovině území místy déšť, i mrznoucí, a nad 1000 m i sněžení. Nejvyšší teploty 6 až 10 °C, při slabém větru kolem 4 °C, zejména na střední Moravě a severovýchodě Čech, v 1000 m na horách kolem 5 °C. Mírný jihozápadní až západní vítr 3 až 7 m/s, místy s nárazy kolem 15 m/s. Zejména na severovýchodě Čech a na Moravě vítr jen slabý proměnlivý do 3 m/s."}

"""


from fire import Fire
import datetime as dt
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from subprocess import getoutput

from console import fg,bg



def get_chmi(time, url="https://www.chmi.cz/predpovedi/predpovedi-pocasi/ceska-republika/predpoved-na-dnesek-resp-zitra"):
    res = f"No information about weather for {time} is currently available."
    if time not in ["dnes","zítra","zitra","noc","night","today","tomorrow","vystraha","varovani","alert"]:
        return json.dumps(  {"weather":res } , ensure_ascii=False)  # MUST OUTPUT FORMAT



    options = Options()
    #firefox_options = FirefoxOptions()
    #firefox_options.add_argument("--headless")  # Run in headless mode


    options.binary_location = getoutput("find /snap/firefox -name firefox").split("\n")[-1]
    options.add_argument("--headless")  # Run in headless mode

    driver = webdriver.Firefox(service = Service(executable_path = getoutput("find /snap/firefox -name geckodriver").split("\n")[-1]),    options = options)
    #url = 'https://cnn.com'
    driver.get(url)

    # Fetch the webpage
    #print("D... getting")
    driver.get(url)

    #print(" Get the page source and close the browser")
    page_source = driver.page_source
    driver.quit()

    #print("# Parse the page source with BeautifulSoup")
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find the desired heading
    heading = soup.find('p', class_='nadpis')
    heading_text = heading.get_text(strip=True) if heading else 'Heading not found'

    # Find all the paragraphs with the specified class and extract their text
    #paragraphs = soup.find_all


    hierarchy = {}
    current_header = None
    current_sub = None
    numb=0

    for p in soup.find_all('p',class_=['podnadpis','textik1','textik2']):
        if "podnadpis" in p['class']:
            numb+=1
            current_header = p.get_text()
            current_header = f"N{numb} {current_header}"
            print(fg.orange,current_header,fg.default)
            hierarchy[current_header] = {}
            current_sub = None

        elif 'textik1' in p['class'] or 'textik2' in p['class']:
            if current_header is not None:
                # Add text to the current header section
                line = p.get_text()
                if 'textik1' in p['class']:
                    line = f"{line}" # utf8 trick

                    current_sub = p.get_text()
                    current_sub = current_sub.replace("(","")
                    current_sub = current_sub.replace(")","")
                    #current_sub = current_sub.replace("-","_")
                    current_sub = current_sub.replace(":","")
                    current_sub = f"{current_sub}" #utf8
                    hierarchy[current_header][current_sub]=[]

                    if line.find("Počasí")>=0:
                        print(fg.lightyellow, current_sub, fg.white, bg.magenta, "Počasí", bg.default,fg.default)
                    else:
                        print(fg.yellow, line, fg.default)


                if 'textik2' in p['class']:
                    line = f"{line}" #utf8
                    line = line.replace(r'\xa0','') # DOESNT HELP
                    #print(f"{fg.green}/{current_header}/{current_sub}/{fg.default}{line}")
                    print(f"{line}")
                    if current_sub is not None:
                        hierarchy[current_header][current_sub].append( line)


    # I have all:
    WDT = dt.datetime.now().strftime("%A")
    WDM = (dt.datetime.now()+dt.timedelta(days=1)).strftime("%A")
    WDd = {
        "Monday": "pondělí",
        "Tuesday": "úterý",
        "Wednesday": "středu",
        "Thursday": "čtvrtek",
        "Friday": "pátek",
        "Saturday": "sobotu",
        "Sunday": "neděli"
    }


    # #print("Today is : ", WDT, WDd[WDT] )
    # situace = []
    # for i,v in hierarchy.items():
    #     #print(i)
    #     for j in list(v.keys()):
    #         if j=="Tlaková tendence:" or j=="Rozptylové podmínky:" or j=="KOMENTÁŘ METEOROLOGA:":
    #             del v[j]
    #         if j == "Situace:" :
    #             situace.append( "".join(v[j])  ) # list with one element.
    #             del v[j]
    #         #print(j):

    # situace =     "".join(situace)
    # print()
    # print( situace )
    # print()


    # paragraphs = [p.get_text() for p in soup.find_all('p', class_=['podnadpis','textik1','textik2'])]

    for ch in list( hierarchy.keys() ): # drop the empty keys
        #print("HIE:",  ch,  hierarchy[ch].keys() )
        if len(hierarchy[ch].keys()) ==0:
            del hierarchy[ch]


    DEMANDED = []
    # ---------------------- identify DAY-----------------------------
    for i,v in hierarchy.items():
        #print(i, end=" ")
        if i.find("Předpověď")>=0:

            if time == "vystraha" or time == "alert":
                for j,w in v.items():
                    #print("VYSTRAHA",j)
                    if j.find("KOMENTÁŘ METEOROLOGA")>=0 and len(DEMANDED)==0:
                        #print("BINGO",w)
                        DEMANDED = w # just pocasi, not tendence rozptyl
                    elif j.find("KOMENTÁŘ METEOROLOGA")>=0 :
                        DEMANDED.append(w) # just pocasi, not tendence rozptyl



            if i.find(WDd[WDT])>=0:
                if time == "today" or time == "dnes":#TODAY
                    for j,w in v.items():
                        if j.find("Počasí")>=0:
                            DEMANDED = w # just pocasi, not tendence rozptyl

            elif i.find(WDd[WDM])>=0: #TOMORROW NIGHT and DAY
                if time == "night" or  time == "noc":
                    for j,w in v.items():
                        if j.find("Počasí")>=0 and j.find("noc")>=0 :
                            DEMANDED = w # just pocasi, not tendence rozptyl

                if time == "tomorrow" or time == "zitra" or time == "zítra":
                    for j,w in v.items():
                        if j.find("Počasí")>=0 and j.find("den")>=0 :
                            DEMANDED = w # just pocasi, not tendence rozptyl
            else:
                print()
        else:
            print()

    #print("---")
    #print(DEMANDED)
    #print("---")

        #for j,w in v.items():
            #print("  ",j)
            #for k in w:
                #print(i.decode('utf8') )# subst(r'\xa0','') )
                #print("  > ",k )#.replace(r'\xa0','') )



    # #print(hierarchy.keys())
    # dnes=None
    # noc=None
    # zitra=None



    # for ch in hierarchy.keys():
    #     for su in hierarchy[ch].keys():
    #         print( "f: ",ch.find("N1") , ch, su  )
    #         if ch.find("N1")==0: dnes=hierarchy[ch][su][0]
    #         if ch.find("N2")==0 and su.find("noc")>0: noc=hierarchy[ch][su][0]
    #         if ch.find("N2")==0 and su.find("den")>0: zitra=hierarchy[ch][su][0]
    #         print(fg.orange,ch,fg.default,"...",fg.yellow,su,fg.default)
    #         print("... ... ",hierarchy[ch][su][0])
    # print("                             ....",time)
    # print(dnes)
    # print("--")
    # print(hierarchy[ch].keys())


    # res = None
    # if time =="dnes":
    #     res = dnes
    #     print(dnes)
    # elif time=="zítra" or time=="zitra":
    #     res = zitra
    #     print(zitra)
    # print()


    ###################################################### DEMANDED
    res=None
    if len(DEMANDED)>0:
        res=" ".join(DEMANDED) # normally just [0], but if vystraha??? 2x??
    #     print("-")
    #     print(DEMANDED)
    #     print("-")
    #     res = []
    #     for i,v in DEMANDED.items():
    #         for j in v:
    #             res.append(j)
    #     res = "".join(res)
    # # Formulate output
    return json.dumps(  {"weather":res } , ensure_ascii=False)  # MUST OUTPUT FORMAT


if __name__=="__main__":
    Fire(get_chmi)
