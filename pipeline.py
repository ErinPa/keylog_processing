import os
import numpy as np
import pandas as pd
from collections import Counter
import re
import spacy
nlp = spacy.load('en_core_web_sm')
from pathlib import Path
import random

import json
 
 
#Cleanup function: converts the .json keylogger output into a csv and standardizes some of the formatting
def cleanup(j, j_noext):

    #getfilename
    filename=j
    #cleanup
    filename=filename.lower()
    filename=re.sub('[^A-Za-z0-9]+', ' ', filename)
    #extract all the words
    lst=filename.split()


    # absolute path to json file
    jsonpath = Path(j)

    # reading the json file
    with jsonpath.open('r', encoding='utf-8') as dat_f:
        dat = json.loads(dat_f.read())

    # creating the dataframe
    df = pd.json_normalize(dat)
    #save the tech info in a variable
    techinfo=df.loc[0,'useragent']
    #save full text into a variable
    text=df["v"].iloc[-1]
    #drop useless columns
    df=df.drop(columns=['language', 'useragent'])
    #rename important columns
    df=df.rename(columns={"t": "time", "e": "type",'k':'key','c':"key_code"})

    df["type"].replace('u', 'up', inplace=True)
    df["type"].replace('m', 'mouse', inplace=True)
    df["type"].replace('d', 'down', inplace=True)
    df["type"].replace('i', 'input', inplace=True)
    df["type"].replace('c', 'click', inplace=True)
    df["type"].replace('s', 'start', inplace=True)
    #remove input rows
    df = df[df.type != "input"]
    df = df.reset_index(drop=True)
    #handle up and down and put on same row
    keyname=[]
    timepress=[]
    timerelease=[]
    keycode=[]
    for i in df.index:
        if df.loc[i,'type']=="down":
            if df.loc[i,'key']=="Dead":
                timepress.append(df.loc[i+2,'time'])
                keyname.append(df.loc[i+2,'key'])
                keycode.append(df.loc[i+2,'key_code'])
                timerelease.append(df.loc[i+2,'time'])
            for j in range(i+1, i+10,1):
                if j<len(df):
                    if (df.loc[j,'key']==df.loc[i,'key'] or df.loc[j,'key']==df.loc[i,'key'].lower() ) and df.loc[j,'type']=="up":
                        timepress.append(df.loc[i,'time'])
                        keyname.append(df.loc[i,'key'])
                        keycode.append(df.loc[i,'key_code'])
                        timerelease.append(df.loc[j,'time'])
                        break
    output= pd.DataFrame(list(zip(keyname, keycode, timepress,timerelease)),
                columns =['keyname','keycode', 'timepress','timerelease'])
    output["keyname"].replace('Backspace', 'backspace', inplace=True)
    output["keyname"].replace('CapsLock', 'capslock', inplace=True)
    output["keyname"].replace('Shift', 'shift', inplace=True)
    output["keyname"].replace('ArrowLeft', 'LEFT', inplace=True)
    output["keyname"].replace('ArrowRight', 'RIGHT', inplace=True)

    # for i in lst:
    #     if "essay" in i:
    #         output['session']="essay"
    #         usrid=re.findall(r"(\d+)(?!.*\d)", j_noext)[0]
    #         output['userid']=usrid
    #     if "copy" in i:
    #         output['session']="copy"   
    #         usrid=re.findall(r"(\d+)(?!.*\d)", j_noext)[0]
    #         output['userid']=usrid
    # print(j_noext)
    output['session']="unkown"
    # regex = r"\\([^;]*)\\"
    # matches = re.finditer(regex, j_noext, re.MULTILINE)
    # for matchNum, match in enumerate(matches, start=1):
    #     for groupNum in range(0, len(match.groups())):
    #         groupNum = groupNum + 1
    #     usrid=int(match.group(groupNum))


    obj= ['Rock', 'Paper', 'Scissor', 'Water', 'Earth','Cookie','Bear','Bird','Cat','Dog','Music','River','Beach','Clock','Minute','Fish','Wave',"Coffee",'Tea','Screen','Bottle','Mouse','Lamp','Table','Piano','Guitar','Note','Pencil','Sweater','Baseball','Hat']
    number= ['1', '2', '3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35']
    usrid=str(random.choice(obj))+(random.choice(number))

    output['userid']=usrid
    #for dev use only
    # output['userid']=1
    output['sessionid']=1
    # output['session']="free1"


    ###addition
    output['sessiontext']=text
    textfile = open(j_noext+'.txt', 'w')
    textfile.write(text)
    textfile.close()
    output.to_csv(j_noext+'_cleanup.csv',index=False,encoding="utf-8")



#Reconstructing function: reconstruct words, sentences and paragraphs
def reconstructing(j, j_noext):
    ##Only needs to be ran once, at the begining of each session
    alpha_lower=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','è','é','à','ù','â', 'ê', 'î', 'ô', 'û','ç',"'",'/',":"];
    alpha=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z','è''é','à','ù','â', 'ê', 'î', 'ô', 'û','ç',"'",'/',":"]
    #alphabetic characters+hyphen
    alphahy=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z','-','è','é','à','ù','â', 'ê', 'î', 'ô', 'û','ç',"'","(",")",'/',':']
    num=['1','2','3','4','5','6','7','8','9']
    punct=['""',"''",'.',',','?','!',':',';'] #à completer
    special_keys=["backspace","capslock", "enter"]


    #open the dataframe
    # df = pd.read_csv(j_noext+'_cleanup.csv',delimiter=',')

    df = pd.read_csv(j_noext+'.csv',delimiter=',')
    j_noext = j_noext.replace("_cleanup", "" )

    # df['keyname']=str(df['keyname'])
    
    # df.to_csv(j_noext+'_inter.csv',index=False,encoding="utf-8")

    #ADD OTHER KEYS
    no_bs=["shift","capslock","tab"]

    df = df.reset_index(drop=True)

    def backspace(df):
        for i in df.index:
            if(df.loc[i, "keyname"] == "backspace"):
                j=0
                while (df.loc[i-j,"keyname"] == "backspace" or "bs" in df.loc[i-j,"keyname"]) and int(i)-int(j)>=1:
                    j += 1
                    if i-1>0 and df.loc[i-j,"keyname"] in no_bs:
                        j+=1
                x = str(df.loc[i-j, "keyname"])+"-bs"
                if i-j>1 and df.loc[i-j, "keyname"] not in no_bs:
                    df.loc[i-j, "keyname"] = x  
    backspace(df)

    #handle arrow keys
    def left_right(df):
        df["keyname_arrow"]=df["keyname"]
        for i in range(df["keyname_arrow"].shape[0]):
            if(df.loc[i, "keyname_arrow"] == "LEFT"):
                j=0
                while (df.loc[i-j,"keyname_arrow"] == "LEFT" or "left" in df.loc[i-j,"keyname_arrow"]) and i-j>0:
                    j += 1
                    x = str(df.loc[i-j, "keyname_arrow"])+"-left" #to test
                    df.loc[i-j, "keyname_arrow"] = x  
            if(df.loc[i, "keyname_arrow"] == "RIGHT"):
                j=0
                while i+j<len(df)-1 and (df.loc[i+j,"keyname_arrow"] == "RIGHT" or "right" in df.loc[i+j,"keyname_arrow"]):
                    j += 1
                    x = str(df.loc[i+j, "keyname_arrow"])+"-right" #to test
                    df.loc[i+j, "keyname_arrow"] = x  

                
    left_right(df)


    def word (df):
        #keynames that are word boundaries
        B=[" ","enter"]
        C=['""',"''",'.',',','?','!',':',';'] #à completer
        boundary=[" ",'""',"''",'.',',','?','!',':',';']
        special=["capslock","left","right"]

        #create the columns
        df["word"]=0
        df["wordid"]=0
        words=[] #where the words go
        w="" #where the current word goes
        edits_bi=[]#was there a backspace within the word ?
        edits=0
        counter=0
        session=df.loc[0,"session"]
        for i in df.index:
            if "-bs" in str(df.loc[i, "keyname"]):
                edits=1
            df.loc[i,"wordid"]= counter
            #if alphabet or hyphen
            if (df.loc[i, "keyname"] in alphahy) and ("-bs" not in df.loc[i, "keyname"])and df.loc[i, "keyname"] not in special:
                w=w+str(df.loc[i, "keyname"])  #add key to word
            #elif word boundary markers
            if df.loc[i, "session"] != session:
                counter +=1
                words.append(w)
                w=""
                edits_bi.append(edits)
                edits=0
                session=df.loc[i,"session"]
                if (df.loc[i, "keyname"] in alphahy) and ("-bs" not in df.loc[i, "keyname"])and df.loc[i, "keyname"] not in special:
                    w=df.loc[i, "keyname"]
            if (df.loc[i, "keyname"] in B) and  i-1>0:
                if (df.loc[i-1, "keyname"] in B) or (df.loc[i-1, "keyname"] in C) :
                    counter +=1
                    words.append(w)
                    w=""
                    edits_bi.append(edits)
                    edits=0
                else :
                    counter +=1
                    df.loc[i,"wordid"]=counter
                    words.append(w) #append finished word
                    w=""
                    edits_bi.append(edits)
                    edits=0
                    counter +=1
                    words.append(w)
                    w=""
                    edits_bi.append(edits)
                    edits=0
            if (df.loc[i, "keyname"] in C):
                if (df.loc[i-1, "keyname"] in B) or (df.loc[i-1, "keyname"] in C) :
                    w=df.loc[i, "keyname"]
                    counter +=1
                    words.append(w)
                    w=""
                    edits_bi.append(edits)
                    edits=0
                else :
                    counter +=1
                    df.loc[i,"wordid"]=counter
                    words.append(w) #append finished word
                    edits_bi.append(edits)
                    edits=0
                    w=df.loc[i, "keyname"]
                    counter +=1
                    words.append(w)
                    w=""
                    edits_bi.append(edits)
                    edits=0

        
        words.append(w)
        edits_bi.append(edits)
        edits=0
        session=df.loc[0,"session"]
        # print (edits_bi)

        df["edit_binary"]=0
        for i in range(df["keyname"].shape[0]):
            if (df.loc[i, "keyname"] in boundary) or (df.loc[i, "session"] != session):
                x=df.loc[i,"wordid"]
                if (df.loc[i, "keyname"] in alphahy) and ("-bs" not in df.loc[i, "keyname"])and df.loc[i, "keyname"] not in special:
                    df.loc[i,"word"]= words[x]
                    df.loc[i,"edit_binary"]=edits_bi[x]

                else:
                    df.loc[i,"word"]=" "
            else:
                df.loc[i,"word"]=" "
                session = df.loc[i, "session"]
                x=df.loc[i,"wordid"]

                df.loc[i,"word"]= words[x]
                df.loc[i,"edit_binary"]=edits_bi[x]


        #drop the lines with space (tentative)
        todrop=[" ","enter"]
        df = df[~df['keyname'].isin(todrop)]
        return words
        
    word(df)   
    words=word(df)

    #reconstruct sentences
    def sentence(df):
        df["sentence"]=0
        df["sentenceid"]=0
        sentences=[]
        s=""
        counter=0
        session=df.loc[1,"session"]
        non_boundary=["backspace","capslock","enter",'.']
        arrowcounter=0
        df['insert']=0

        for i in range(df["keyname"].shape[0]):
            df.loc[i,"sentenceid"]= counter
            #if no sentence boundary
            if (((df.loc[i, "keyname"] in alphahy) or df.loc[i, "keyname"] == " " or df.loc[i, "keyname"] == "," ) \
                and ("-bs" not in df.loc[i, "keyname"]))and len(df.loc[i, "keyname"]) <2\
            and (df.loc[i, "session"] == session)and  df.loc[i, "insert"]!=1:
                #if space -> add space
                if (df.loc[i, "keyname"] ==" "):
                    s=s+str(" ")
                else:
                    s=s+str(df.loc[i, "keyname"])
            #if period -> end sentence
            elif (df.loc[i, "keyname"] ==".") :
                s=s+str(df.loc[i, "keyname"])
                counter +=1
                sentences.append(s)
                s=""
                session = df.loc[i, "session"]
            #if end of session, end sentence and session
            elif (df.loc[i,"session"]!=session):
                counter +=1
                sentences.append(s)
                if (df.loc[i, "keyname"] in alphahy):
                    s=df.loc[i,"keyname"]
                else:
                    s=""
                session = df.loc[i, "session"]
            if ("left" in str(df.loc[i,"keyname_arrow"])):
                arrowcounter+=1
            if ("-left" not in str(df.loc[i,"keyname_arrow"]) and arrowcounter >0 and i+arrowcounter<len(df)):
                string = s[-arrowcounter:]
                s = s[:-arrowcounter]
                s=s+str(df.loc[i+arrowcounter, "keyname"])
                s=s+string
                df.loc[i+arrowcounter, "insert"]=1
                extra=0
                if df.loc[i+1,"keyname"] != "RIGHT" or df.loc[i+1,"keyname"] != "NEXT":
                    extra+=1
                    s = s[:-arrowcounter]
                    s=s+str(df.loc[i+arrowcounter+extra, "keyname"])
                    s=s+string
                    df.loc[i+arrowcounter+1, "insert"]=1
                arrowcounter=0
        
        sentences.append(s)
        session=df.loc[1,"session"]
        
        for i in range(df["keyname"].shape[0]):
            if (str(df.loc[i, "session"]) != str(session)):
                x=int(df.loc[i,"sentenceid"])+1
                df.loc[i,"sentence"]= sentences[x]
                session = df.loc[i, "session"]
            elif (df.loc[i, "keyname"] !="."):
                x=df.loc[i,"sentenceid"]
                df.loc[i,"sentence"]= sentences[x]
                session = df.loc[i, "session"]
            else:
                df.loc[i,"sentence"]=" "

    sentence(df)

    #reconstruct session
    def session(df):
        df["session_text"]=0
        df['nb'] = df.index
        sess=[]
        current_sentence=str(df.loc[1, "sentence"])
        session_sentence=str(df.loc[1, "sentence"])
    #     sess.append(df.loc[1, "sentence"])
        current_session=df.loc[1, "session"] 
        df["session_index"]=0
        counter=0
        for i in range(df["sentence"].shape[0]):
            if ((df.loc[i, "session"])!= current_session):
                counter+=1
                sess.append(session_sentence)
                session_sentence=str(df.loc[i, "sentence"])
                current_session=df.loc[i, "session"]
                current_sentence =str(df.loc[i, "sentence"])
            if (df.loc[i, "sentence"])!= current_sentence:
                session_sentence= str(session_sentence) +str(df.loc[i, "sentence"]) 
                current_sentence=(df.loc[i, "sentence"])
            if df.loc[i, "nb"] == (len(df.index)-1):
                if len(current_sentence)<len(session_sentence):
                    sess.append(session_sentence)
                else:
                    sess.append(current_sentence)

            df.loc[i, "session_index"]=counter

        counter = 0
        for i in range(df["keyname"].shape[0]):
            if (df.loc[i, "session_index"] == counter):
                x=df.loc[i,"session_index"]
                df.loc[i,"session_text"]= sess[x]
            else:
                counter =+1
                x=df.loc[i,"session_index"]
                df.loc[i,"session_text"]= sess[x]
 

    session(df)

    #pause 1 -> Timerelease to timepress (will give negative values when there is a rollover)
    def pause_1(df):
        df["pause_1_after"]=0
        count_row = (df.shape[0]) -2 
        current_session=0
        for i in range(df["keyname"].shape[0]):
            if i <=count_row:
                x=df.loc[i,"timerelease"]
                y=df.loc[i+1,"timepress"]
                df.loc[i,"pause_1_after"]=y-x
            if df.loc[i,"session_index"]!=current_session:
                df.loc[i-1,"pause_1_after"]=None
                current_session +=1
        df["pause_1_before"] = None
        df.iloc[1:, df.columns.get_loc("pause_1_before")] = df.iloc[:-1, df.columns.get_loc("pause_1_after")].values

            
    #pause 2 -> Timepress to timepress          
    def pause_2(df):
        df["pause_2_after"]=0
        count_row = (df.shape[0]) -2 
        current_session=0
        for i in range(df["keyname"].shape[0]):
            if i <=count_row:
                x=df.loc[i,"timepress"]
                y=df.loc[i+1,"timepress"]
                df.loc[i,"pause_2_after"]=y-x
            if df.loc[i,"session_index"]!=current_session:
                df.loc[i-1,"pause_2_after"]=None
                current_session +=1
        df["pause_2_before"] = None
        df.iloc[1:, df.columns.get_loc("pause_2_before")] = df.iloc[:-1, df.columns.get_loc("pause_2_after")].values


    #the length during which a key is pressed down
    def hold_time(df):
        df["hold_time"]=0
        count_row = (df.shape[0]) -1 
        for i in range(df["keyname"].shape[0]):
            if i <=count_row:
                x=df.loc[i,"timerelease"]
                y=df.loc[i,"timepress"]
                df.loc[i,"hold_time"]=x-y

    pause_1(df)
    pause_2(df)
    hold_time(df)


    #keylevel chunks
    #p-bursts and R-bursts

    def chunks(df):
        df =df.reset_index(drop=True)
        df["chunkid"]=0
        df["chunk"]=0
        df["burst_type"]=0
        chunkid=0
        pchunkid=0
        sess=df.loc[0,"session"]
        c=""
        chunks=[]
        burst_type=[]
        for i in range(df["keyname"].shape[0]):
            # print(i)

            if (i>0 and "back" in str(df.loc[i,"keyname"]) and "-bs" in str(df.loc[i-1,"keyname"]) \
                    and i>0) : #and "-bs" not in df.loc[i,"keyname"]
                j=1
                while i+j<len(df) and  "back"  in df.loc[i+j,"keyname"]:
                    j+=1
                nonewburst = True
                for h in range(j+1):
                    if i+h<len(df):
                        pause=df.loc[i+h,"pause_2_before"]
                        if pause  >1000:
                            nonewburst=False
                    
                if nonewburst == False:
                    burst_type.append("r-burst")
                    chunkid+=1

            if (i>0 and "back" not in str(df.loc[i,"keyname"]) and "back" in str(df.loc[i-1,"keyname"])):
                j=1
                while i-j>=1 and "back" in df.loc[i-j,"keyname"]:
                    j+=1
                nonewburst = True
                for h in range(j):
                    pause=df.loc[i-h,"pause_2_before"]
                    if pause  >1000:
                        nonewburst=False

                if nonewburst == False:
                    burst_type.append("revision")
                    chunkid+=1

            elif ("back" in str(df.loc[i,"keyname"])) or ("-bs" in str(df.loc[i,"keyname"])):
                chunkid=chunkid
            elif (i>0 and df.loc[i,"pause_2_before"] >= 2000) or df.loc[i,"session"] != sess :
                chunkid+=1
                if (i>0 and df.loc[i,"pause_2_before"] >= 2000) and  df.loc[i,"session"] != sess:
                    burst_type.append("p-burst/end")
                elif (i>0 and df.loc[i,"pause_2_before"] >= 2000):
                    burst_type.append("p-burst")
                elif df.loc[i,"session"] != sess:
                    burst_type.append("end")
    #         df.loc[i,"chunkid"]=chunkid
            #if current id is same as chunkid, append key to string

            #RECONSTRUCTING SENTENCES
            if chunkid==pchunkid:
                if (df.loc[i, "keyname"] in alphahy or("-bs" in df.loc[i,"keyname"]) or df.loc[i, "keyname"] in punct) and ("back" not in df.loc[i,"keyname"]):
                    if ("-bs" in df.loc[i,"keyname"]):
                        if(i>0 and "["not in c or "bs" not in df.loc[i-1,"keyname"]):
                            c=c+"["+df.loc[i,"keyname"]
                        else:
                            c=c+df.loc[i,"keyname"]
                    else:
                        c=c+df.loc[i,"keyname"]
                    if ( i< len(df) and "-bs" in df.loc[i,"keyname"] and "-bs" not in df.loc[i+1,"keyname"]):
                        c=c+"] "
                if df.loc[i,"keyname"]==" ":
                    c=c+" "
            #if current id is different, append to list
            #APPENDING FINISHED CHUNKS
            if chunkid != pchunkid:
                chunks.append(c)
                # print(str(chunkid)+" - "+str(pchunkid))
                if (df.loc[i, "keyname"] in alphahy or df.loc[i, "keyname"] in punct) and ("back" not in df.loc[i,"keyname"]) and ("-bs" not in df.loc[i,"keyname"]):
                    c=df.loc[i,"keyname"]
                else:
                    c=""
                pchunkid=chunkid
                sess=df.loc[i,"session"]
            #append last chunk
            if i==len(df)-1:
                chunks.append(c)
                burst_type.append("end")
            df.loc[i,"chunkid"]=chunkid        
            

        for i in range(df["keyname"].shape[0]):
            x=df.loc[i,"chunkid"]
            if "[" in str(chunks[x])and "]"not in str(chunks[x]):
                chunks[x]=chunks[x]+"]"
            chunks[x]=chunks[x].replace("-bs", "")
            chunks[x]=chunks[x].replace(" ", " ")

            
            df.loc[i,"chunk"]= chunks[x]
            df.loc[i,"burst_type"]= burst_type[x]
                
        return df

    # chunks(df)
    df=chunks(df)

    def timestamps(df):
        timepress_start=[df.loc[0, "timepress"]]
        timepress_end=[]
        current_wordid=0
        current_timepress=df.loc[0, "timepress"]
        current_session=df.loc[0,"session"]

        for i in range(df["keyname"].shape[0]):
            if (df.loc[i, "wordid"] != current_wordid):
                if current_session != df.loc[i,"session"]:
                    timepress_end.append(df.loc[i-2,"timepress"])
                    current_session=df.loc[i,"session"]
                else:
                    timepress_end.append(current_timepress)
                timepress_start.append(df.loc[i, "timepress"])
                current_timepress=df.loc[i, "timepress"]
                current_wordid +=1
            current_timepress=df.loc[i, "timepress"]
        return timepress_start, timepress_end



    timepress_start, timepress_end = timestamps(df)

    def user_session(df):
        userid=[df.loc[0, "userid"]]
        session=[df.loc[0, "session"]]
        session_index=[df.loc[0, "session_index"]]
        current_userid=df.loc[0, "userid"]
        current_session=df.loc[0, "session"]
        current_session_index=[df.loc[0, "session_index"]]
        current_wordid=0
        for i in range(df["word"].shape[0]):
            if (df.loc[i, "wordid"] != current_wordid):
                userid.append(df.loc[i, "userid"])
                session.append(df.loc[i, "session"])
                session_index.append(df.loc[i, "session_index"])

                current_userid=df.loc[i, "userid"]
                current_session=df.loc[i, "session"]
                current_session_index=[df.loc[i, "session_index"]]

                current_wordid +=1
            current_userid=df.loc[i, "userid"]
        return userid, session, session_index


    userid, session, session_index = user_session(df)


    df.to_csv(j_noext+'_keylevel.csv',index=False,encoding="utf-8")

    text=str(df.loc[0,'session_text'])
    # # print(df.loc[0,'session_text'])
    # textfile = open(j_noext+'.txt', 'w')
    # textfile.write(text)
    # textfile.close()
    result = pd.DataFrame()
    #userid
    result.loc[0,"userid"]=df.loc[5,'userid']
    #automatically grab the task 
    filename=j_noext
    if "copy" in filename:
        result.loc[0,'task']="copy"
    if "essay" in filename:
        result.loc[0,'task']="essay"
    if "free1" in filename:
        result.loc[0,'task']="free1"
    if "free2" in filename:
        result.loc[0,'task']="free2"
    if "free3" in filename:
        result.loc[0,'task']="free3"
    else:
        result.loc[0,'task']="NA"



    #total
    total=df.at[df.index[-1], 'wordid']
    #remove the space
    c=0
    for i in df.index:
        if df.loc[i,'word']==" ":
            c+=1

    word_count=total-c
    result.loc[0,'wordcount']=word_count

    #how long in ms first time press to last time release
    start=df.loc[0,"timepress"]
    end=df.at[df.index[-1], 'timerelease']
    length_ms=end-start
    length_s=length_ms/1000
    result.loc[0,'length_ms']=length_ms
    result.loc[0,'length_s']=length_s

    #nb of backspace
    nb_backspace=0
    nb_backspace_sequence=0
    bs=[]
    for i in df.index:
        if df.loc[i,'keyname']=="backspace":
            for j in range(i, len(df),1):
                if df.loc[j,'keyname']!="backspace":
                    if j not in bs:
                        bs.append(j)
                        nb_backspace_sequence+=1
                    break;



            nb_backspace+=1

    result.loc[0,'nb_backspace']=nb_backspace
    result.loc[0,'nb_backspace_sequence']=nb_backspace_sequence

    #nb of keys
    nb_keystrokes=len(df)
    result.loc[0,'nb_keystrokes']=nb_keystrokes


    #get WPM
    df["timepress_from_0_min"]=((df["timepress"]-df.loc[0,'timepress'])/1000)/60
    df["keystroke_count"]=df['nb']+1
    df['GrossWPM']=(df["keystroke_count"]/5)/df["timepress_from_0_min"]

    result.loc[0,'GrossWPM_10thpercentile']=df.GrossWPM.quantile(0.1) # 10th percentile

    result.loc[0,'GrossWPM_median']=df.GrossWPM.quantile(0.5) # 10th percentile

    result.loc[0,'GrossWPM_90thpercentile']=df.GrossWPM.quantile(0.9) # 10th percentile
    
    result.to_csv(j_noext+'_sessionmetrics.csv',index=False,encoding="utf-8")




    #this function gets the data from the key-level dataset and puts in into a list to be transfered to the word-level dataset

    def recup(df):
        current_wordid=0
        sentence=[]
        sentenceid=[]
        session_text=[]
        session_index=[]
        proficiency=[]
        chunks=[]
        for i in range(df["keyname"].shape[0]):
            if (df.loc[i, "wordid"] != current_wordid)and i>0:
                sentence.append(df.loc[i-1,"sentence"])
                sentenceid.append(df.loc[i-1,"sentenceid"])
                session_text.append(df.loc[i-1,"session_text"])
                session_index.append(df.loc[i-1,"session_index"])
                chunks.append(df.loc[i-1,"chunk"])

    #             proficiency.append(df.loc[i-1,"proficiency"])
                current_wordid+=1  
        return sentence, sentenceid, session_text,session_index,chunks
    sentence, sentenceid, session_text,session_index,chunks=recup(df)

    #concatenate the lists into a column

    dfw = pd.DataFrame(list(zip(userid, session, words, timepress_start, timepress_end,sentence, sentenceid, session_text,session_index,chunks)), columns =['userid','session','word', 'timepress_start', 'timepress_end',"sentence", "sentenceid", "session_text","session_index","chunk"]) 


    todrop=[""]
    dfw = dfw[~dfw['word'].isin(todrop)]
    dfw =dfw.reset_index()
    dfw
    df=dfw

    df["session"]= "u-"+df["userid"].map(str) + "s-"+ df["session"].map(str)

    #labeled as pause one but its not since its two timpresses
    def pause_1(df):
        df["pause_1_after"]=0
        count_row = (df.shape[0]) -2 
        current_session=0
        for i in range(df["word"].shape[0]):
            if i <=count_row:
                x=df.loc[i,"timepress_end"]
                y=df.loc[i+1,"timepress_start"]
                df.loc[i,"pause_1_after"]=y-x
            if df.loc[i,"session_index"]!=current_session:
                df.loc[i-1,"pause_1_after"]=None
                current_session +=1
        df["pause_1_before"] =0
        df.iloc[1:, df.columns.get_loc("pause_1_before")] = df.iloc[:-1, df.columns.get_loc("pause_1_after")].values


            
    pause_1(df)
    def duration(df):
        df["duration"]=0
        count_row = (df.shape[0]) -1 
        for i in range(df["word"].shape[0]):
            if i <=count_row:
                x=df.loc[i,"timepress_end"]
                y=df.loc[i,"timepress_start"]
                df.loc[i,"duration"]=x-y
    duration(df)

    def nchar(df):
        df["nchar_word"]=0
    #     df["nchar_sen"]=0
    #     df["nchar_session"]=0
        for i in range(df["word"].shape[0]):
            df.loc[i,"nchar_word"]=len(df.loc[i,"word"])
    #         df.loc[i,"nchar_sentence"]=len(df.loc[i,"sentence"])
    #         df.loc[i,"nchar_session"]=len(df.loc[i,"session_text"])

    nchar(df)

    def char_speed_word(df):
        df["char_speed_word"]=0
        for i in range(df["word"].shape[0]):
            if df.loc[i,"duration"] != 0:
                df.loc[i,"char_speed_word"]=((df.loc[i,"nchar_word"])/(df.loc[i,"duration"]))*1000
    char_speed_word(df)

    #part of speech
    pos = []
    for doc in nlp.pipe(df['word'].astype('unicode').values):
        if doc.is_parsed:
            pos.append([n.pos_ for n in doc])
        else:
            pos.append(None)

    pos_new = [i[0] for i in pos]
    df['word_pos'] = pos_new

    df["word_pos+1"] = None
    df["word_pos+2"] = None
    df.iloc[:-1, df.columns.get_loc("word_pos+1")] = df.iloc[1:, df.columns.get_loc("word_pos")].values
    df.iloc[:-2, df.columns.get_loc("word_pos+2")] = df.iloc[2:, df.columns.get_loc("word_pos")].values

    df["following_trigram"]=df["word_pos"]+" " +df["word_pos+1"]+ " "+df["word_pos+2"]

    df["word_pos-1"] = None
    df["word_pos-2"] = None
    df.iloc[1:, df.columns.get_loc("word_pos-1")] = df.iloc[:-1, df.columns.get_loc("word_pos")].values
    df.iloc[2:, df.columns.get_loc("word_pos-2")] = df.iloc[:-2, df.columns.get_loc("word_pos")].values

    df["previous_trigram"]=df["word_pos-2"]+" " +df["word_pos-1"]+ " "+df["word_pos"]

    df.to_csv(j_noext+'_wordlevel.csv',index=False,encoding="utf-8") 




##Step1: save the folder names in a list
path =[PATH]
direc=[]
for root, directories, files in os.walk(path):
    for directory in directories:
        direc.append(os.path.join(root, directory))

# next(os.walk('C:\dir1\dir2\startdir'))[0]


#open the directory and save files into a list too
file_sub=[]
for i in direc:
    path=i
    for files in os.walk(path):
        for file in files:
            file_sub.append(file)
        #filter out empty str and unneeded info
        file_sub=list(filter(None, file_sub))
file_sub=file_sub[1::2]


for i in range(0,len(direc)):

    user_folder=direc[i]
    for j in file_sub[i]:
        current_path=str(user_folder)+"\\"+str(j)
        csv_name=j
        match_object = re.match(r'(.+?)(\.[^.]*$|$)', current_path)
        j_noext=(match_object.group(1))
        combined = '\t'.join(file_sub[i])
        print(j_noext)
        # print(current_path)
        print("------")

        if '_cleanup' not in combined:
            cleanup(current_path,j_noext)
        if '_cleanup' in j_noext:
            if '_wordlevel' not in combined:
                reconstructing(current_path,j_noext)


