#python -m pip install pycdlib
#https://github.com/clalancette/pycdlib
#For extracting iso files
import pycdlib

import time
import sys

from collections import defaultdict
from io import StringIO
import csv
import zipfile
import multiprocessing

import os
import shutil
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Combobox
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfilenames
from tkinter.filedialog import askdirectory
from tkinter.filedialog import asksaveasfilename

from promptuser import pufiles, pufile, pudir, pusavefile

def clean_create_folder(tmpfolder):
    '''
    Creates an empty Folder
    Deletes previous existence
    tmpfolder = path to folder
    '''
    if not os.path.exists(tmpfolder):
        os.mkdir(tmpfolder)
    else:
        shutil.rmtree(tmpfolder)
        while True:
            try:
                os.mkdir(tmpfolder)
                break
            except:
                pass

def get_relevant_files(tmpfolder):
    '''
    Return List [Path+Filenames, Path+Filename] in a Directory that start with "NSRL" and end with ".txt"
    These Files contain information like Productcode to Productname
    tmpfolder = path (str) to extracted iso of NSRL file
    '''
    #get content of tmpfolder
    isocontent = os.listdir(tmpfolder)

    #get relevant .txt files of tmpfolder which contain metadata
    relevant_files = []
    print("\n")
    for i in isocontent:
        if i.startswith("NSRL") and i.endswith(".txt"):
            relevant_files.append(tmpfolder+"/"+i)
    return relevant_files       

def make_dict(f, columns, key, val):
    '''
    Reads a csv File (First Line must contain the Names of the columns)
    Takes two Names of Columns and reterns them in Dictionary fasion
    '''
    #columns = list of strings (first line of file)
    # f = file object
    # key & val ) string
    #Return a Dictionary (reading a textfile) and extracting key and value of each line to a dict pair
    d={}
    kindex = columns.index(key)
    vindex = columns.index(val)
    for line in csv.reader(f, delimiter=",", skipinitialspace=True, escapechar="\\"):
        #values = [each[1:-1] for each in line]
        values = line

        #print(bytes(values[0], "utf-8"))
        #print(bool(values[0]))
        if not values[0]:
            break
       
        d[values[kindex]]=values[vindex]
    return d

def make_dicts(f, columns, keys, vals):
    '''
    Reads a csv File (First Line must contain the Names of the columns)
    Takes two Names of Columns and reterns them in Dictionary fasion
    '''
    #ONLY USE THIS FUNCTION FOR NSRLProd.txt BECUASE SOMEHOW THEY DONT QUOTE THE PRODUCT CODE IN THERE #CONSISTENCY >_<
    #keys, vals = list of strings

    L = [{} for i in keys]
    kindexes = [columns.index(each) for each in keys]
    vindexes = [columns.index(each) for each in vals]
    for line in csv.reader(f, delimiter=",", skipinitialspace=True, escapechar="\\"):
        #values=line[:1]
        #values += [each[1:-1] for each in line[1:]]
        values = line
        if not values[0]:
            break
        c=0
        for d in L:
            d[values[kindexes[c]]]=values[vindexes[c]]
            c+=1
    return L

def read_meta_files(relevant_files, mfgfields, osfields, prodfields):
    '''
    Reads all the additional information Files from the extracted iso
    Currently: MFG, OS, PROD
    '''
    D = {}
    for source in relevant_files:
        with open(source, "r", encoding="utf-8") as f:
            line = [each[1:-1] for each in f.readline().replace("\n", "").split(",")]
            columns=line.copy()
            #print(columns)

            #Get indexes of important info in list values
            if source.find("Mfg")>=0:
                #print("mfg")
                #Parsing the NSRLMfg.txt
                #D MfgCode -> MfgName
                D["mfgcode2mfgname"]=make_dict(f, columns, mfgfields["mfgcode"], mfgfields["mfgname"])

            if source.find("OS")>=0:
                #print("os")
                #D OsCOde -> Osname
                D["oscode2osname"]=make_dict(f, columns, osfields["oscode"], osfields["osname"])

            if source.find("Prod")>=0:
                #print("prod")
                #D ProdCode -> ProdType, MfgCode, ProdName

                D["prodcode2prodtype"],D["prodcode2mfgcode"],D["prodcode2prodname"], D["prodcode2oscode"]=make_dicts(f, columns, (prodfields["prodcode"], prodfields["prodcode"], prodfields["prodcode"], prodfields["prodcode"]), (prodfields["prodtype"], prodfields["mfgcode"], prodfields["prodname"], prodfields["oscode"]))
    return D
    
def extract(isofile, tmpfolder):
    '''
    extract a iso file to a folder
    '''
    #extract iso to tmpfolder
    # global isofile, tmpfolder
    print("extract")
    os.system("python pycdlib-extract-files.py \""+isofile+"\" -extract-to \""+tmpfolder+"\"")

def handle_iso():
    '''
    Run at Button "Extractt Iso"
    Extracts iso to folder and parses it for metainformation
    '''
    #Declare Temp Folder
    statustext.set("Status: Extracting iso")
    root.update_idletasks()
    root.update()
    global tmpfolder
    tmpfolder=str(int(time.time()))

    #Prompt user for Iso NSRL File
    #global isofile

    #Create tmpfolder
    clean_create_folder(tmpfolder)

    extract(comboinputs[0].get(), tmpfolder)
    
    #get content of tmpfolder
    isocontent = os.listdir(tmpfolder)

    #get relevant .txt files of tmpfolder which contain metadata
    relevant_files = get_relevant_files(tmpfolder)

    #Dicts needed:
    '''
    Key -> Value

    ProdCode -> ProdType
    ProdCode -> MfgCode
    ProdCode -> ProdName

    MfgCode -> MfgName

    OsCode -> Osname
    '''
    mfgfields = {"mfgcode":"MfgCode", "mfgname":"MfgName"}
    osfields = {"oscode":"OpSystemCode", "osname":"OpSystemName"}
    prodfields = {"prodcode":"ProductCode", "prodtype":"ApplicationType", "mfgcode":"MfgCode", "prodname":"ProductName", "oscode":"OpSystemCode"}
    #Read Files to Dictionaries

    global D
    D = read_meta_files(relevant_files, mfgfields, osfields, prodfields)
    

    global KL
    KL = create_keyword_list(D)

    D = make_cross_dicts(D)

    print("__________")
    for i in D:
        print(i, len(D[i]))
    print("__________")

    global KL_exists
    KL_exists = True
    statustext.set("Status: idle (select Filter)")
    root.update_idletasks()
    root.update()

def choose_iso():
    '''
    Prompt User for Path to iso file
    '''
    global comboinputs
    comboinputs[0].set(pufile())


def minion(pq, pl, i, D, keywordslist):
    '''
    Multiprocessing Worker Unit
    Gets Lines from NSRLFile.txt from Queue and compares them to the keywordslist
    '''
    while True:
        #print("getting line")
        line = pq.get()
        if type(line)==str:
            try:
                if line == "STOPSTOPSTOP":
                    print("STOPPING")
                    break
            except:
                pass
        try:
  
            
       
            if not line[0]:
                break
            values = [line[1], line[3][1:-1], line[5], line[6][1:-1]]
            '''
            values: 0=md5, 1=name, 2=prodcode, 3=oscode
            translations:
            3 -> oscode2osname -> compare to keywords[2]
            2 -> prodcode2mfgcode -> mfgcode2mfgname -> compare to keywords[1]
            2 -> prodcode2prodname -> compare to keywords[4]
            2 -> prodcode2prodtype -> compare to keywords[3]
            1 -> compare to keywords[0]
            keywords empty string = wildcard
            '''
            
        except Exception as e:
            print("failed at one:", e)
            print(line)
            continue
        
        try:

            #translating the values with the dict to human readable data
            sample = []
            sample.append(D["prodcode2prodname"][values[2]])
            sample.append(D["mfgcode2mfgname"][D["prodcode2mfgcode"][values[2]]])
            sample.append(D["prodcode2prodtype"][values[2]])
            sample.append(D["oscode2osname"][values[3]])
            sample.append(values[1])
            sample.append(values[0])
            #print("sample:", sample)
            #print("keywordsL:", keywordslist)
            #sample = [prodname, mfgname, prodtype, osname, md5]
            dl=[]
            if sample[4] in keywordslist[0] or keywordslist[0]==[""]:
                if sample[0] in keywordslist[4] or keywordslist[4]==[""]:
                    dl.append(True)
                    if sample[1] in keywordslist[1] or keywordslist[1]==[""]:
                        dl.append(True)
                        if sample[2] in keywordslist[3] or keywordslist[3]==[""]:#ApplicationTypecan have multiple per programcode
                            dl.append(True)
                            if sample[3] in keywordslist[2] or keywordslist[2]==[""]:
                                dl.append(True)
                                print("little success", sample)
                                #append md5 to process list
                                pl.append(sample.pop())
                        elif sample[2].find(",")>=0:# Handle multiple Application Type (sep by comma)
                            f=StringIO(sample[2])
                            for line in csv.reader(f):
                                for word in line:
                                    if word in keywordslist[3]:
                                        if sample[3] in keywordslist[2] or keywordslist[2]==[""]:
                                            pl.append(sample.pop())
                                            break

            #print(values)
        
        except Exception as e:
            print("translating error", e)
            try:
                e=""
                for i in line:
                    e=e+str(bytes(i, "utf-8"))+", "
                print(e)
                print(dl)
            
                print(sample)
            except:
                pass

def export(filters, tmpfolder, D):
    statustext.set("Status: Exporting (unzipping)")
    root.update_idletasks()
    root.update()
    #filters = [stringvar, stringvar]
    #stringvar = "keyword, keyword"
    keywordslist=[]
    for field in filters:
        #keywords = field.get().replace('", "', '","').split('","')
        ##################################################################################################################################################
        madesth=False
        for keywords in csv.reader(StringIO(field.get()), delimiter=",", skipinitialspace=True, escapechar="\\"):
            madesth=True
            
            keywordslist.append(keywords)
        if not madesth:
            keywordslist.append([""])
    #keywordslist=[['.exe', '.jpg'], [Hersteller strings], [OS], [Type], [ProdName]] can be ['']
    
    #unzip the huge hash file
    with zipfile.ZipFile(tmpfolder+"/NSRLFile.txt.zip", "r") as zip_ref:
        zip_ref.extractall(tmpfolder)

    statustext.set("Status: Exporting (reading)")
    root.update_idletasks()
    root.update()
    #MULTIPROCESSING
    #loop over hashfile and compare with keywords using dicts
    with  open(tmpfolder+"/NSRLFile.txt", "r", encoding="utf-8") as f:
        failed = 0
        checked = 0
        passed = 0
        
        
        #Columns of Interes in NSRLFile.txt
        # 5 has no ""
        #MD5, Name, ProdCode, OSCode
        #compareindexes = [1, 3, 5, 6]
        ncores = 4
        ps=[]
        qlist = []
        for i in range(ncores):
            qlist.append(multiprocessing.Queue())
        mllist = []
        for i in range(ncores):
            mllist.append(multiprocessing.Manager().list())
        
        
        for i in range(ncores):
            p = multiprocessing.Process(target=minion, args=(qlist[i],mllist[i], i, D, keywordslist))
            ps.append(p)
            print("starting subprocess")
            p.start()

        f.readline()
        c=0
        for line in csv.reader(f, delimiter=",", skipinitialspace=True, escapechar="\\"):
            c+=1
            if line == []:
                continue
            #print("putting line in queue", len(line))
            qlist[c%ncores].put(line)
            #print("put:", line)
            if c%100000==0:
                print(c/1000, "K lines sent to queue")

        for i in range(ncores):
            qlist[i].put("STOPSTOPSTOP")
            print("finished reading file")
        statustext.set("Status: Exporting (processing)")
        root.update_idletasks()
        root.update()

        for p in ps:
            print("stopping subprocess")
            p.join()

    result = {}
    for L in mllist:
        for elem in L:
            result[elem]=True
    result=list(result)
    #mllist = [[md5, md5][md5, md5]]    
    print("Failed to check:", failed)
    print("Checked:", checked)
    print("passed:", passed)
    print("result list:", len(result))
    resulttext.set("# of Results: "+str(len(result)))
    root.update_idletasks()
    root.update()
    shutil.rmtree(tmpfolder)


    return result

def list_to_file(data, dest, header=True):
    statustext.set("Status: Exporting (write)")
    root.update_idletasks()
    root.update()

    with open(dest, "w") as f:
        if header:
            f.write("md5\n")
        for h in data:
            f.write(h+"\n")
    return header

def finalexport1():
    saveas = pusavefile()
    global tmpfolder
    global D
    data = export(comboinputs[1:], tmpfolder, D)

    if list_to_file(data, saveas):
        print("SUCCESS")

    #XWAYS MD5 HEADER?
    statustext.set("Status: Finished")
    root.update_idletasks()
    root.update()

def finalexport2():
    saveas = pusavefile()
    #Nuix NO MD5 HEADER
    global tmpfolder
    global D
    data = export(comboinputs[1:], tmpfolder, D)

    if not list_to_file(data, saveas, False):
        print("SUCCESS")
    statustext.set("Status: Finished")
    root.update_idletasks()
    root.update()
def create_keyword_list(D):
    #Mfg, OS, Prodtype, Prodname
    KL = {}
    for d in D:
        KL[d]=[]
        for k, v in D[d].items():
            KL[d].append(v)
    #KL = {"mfgcode2mfgname":[str, str, str]}
    return KL

def keyword_suggestion(KL, topic, deja):
    #topic = "mfgcode2mfgname"
    #READ DEJA WITH CSV READER
    #if deja=="":
    #    return ['"'+str(bytes(each, "utf-8"))+'"' for each in KL[topic]]
    possible = []
    print("alive1")
    f = StringIO(deja.get().lower())
    print("alive2")
    print(bytes(deja.get().lower(), "utf-8"))
    print("alive2.5")
    entered=False
    for words in csv.reader(f, delimiter=",", skipinitialspace=True, escapechar="\\"):
        entered=True
        print("alive3")
        for word in words:
            for elem in KL[topic]:
            
                if elem.lower().find(word) >= 0:
                    #print(bytes(word, "utf-8"), bytes(elem, "utf-8"))
                    possible.append('"'+str(bytes(elem, "utf-8"))[2:-1]+'"')
    if entered:
        return possible
    return ['"'+str(bytes(each, "utf-8"))[2:-1]+'"' for each in KL[topic]]

def keyword_suggestion_keepdeja(KL, topic, deja):
    #topic = "mfgcode2mfgname"
    #READ DEJA WITH CSV READER
    #if deja=="":
    #    return ['"'+str(bytes(each, "utf-8"))+'"' for each in KL[topic]]
    possible = []
    extra = []
    #print("alive1")
    f = StringIO(deja.get())
    #print("alive2")
    #print(bytes(deja.get().lower(), "utf-8"))
    #print("alive2.5")
    entered=False
    for words in csv.reader(f, delimiter=",", skipinitialspace=True, escapechar="\\"):
        entered=True
        #print("alive3")

        word=words.pop()
        formerstr = ""
        for former in words:
            formerstr=formerstr+'"'+former+'"'+','#######################
        for elem in KL[topic]:
        
            if elem.lower().find(word.lower()) >= 0:
                #print(bytes(word, "utf-8"), bytes(elem, "utf-8"))
                #possible.append(formerstr+'"'+str(bytes(elem, "utf-8"))[2:-1]+'"')
                # filter cyrillic (non ascii) letters, they dont work in tkinter tcl GUI:
                #possible.append(formerstr+'"'+str(bytes("".join([letter if ord(letter)<128 else "" for letter in elem]), "utf-8"))[2:-1]+'"')
                possible.append(str(bytes("".join([letter if ord(letter)<128 else "" for letter in elem]), "utf-8"))[2:-1])
                ###WITHOUT FORMER AND QUOTES -> ADD THEM WITH LIST COMPREHENSION AFTER THE CROSS FILTER AND VOILA IT SHOULD WORK

    if entered:
        return list(dict.fromkeys(possible)), formerstr
    #return ['"'+str(bytes(each, "utf-8"))[2:-1]+'"' for each in KL[topic]]
    #return {'"'+str(bytes("".join([letter if ord(letter)<128 else "" for letter in each]), "utf-8"))[2:-1]+'"' for each in KL[topic]}
    return {str(bytes("".join([letter if ord(letter)<128 else "" for letter in each]), "utf-8"))[2:-1] for each in KL[topic]}, ""

def update_dropdowns():
    #prodcode2prodname
    #mfgcode2mfgname
    #prodcode2prodtype
    #oscode2osname
    
    global KL 
    global comboinputs
    NL = ["mfgcode2mfgname", "oscode2osname", "prodcode2prodtype", "prodcode2prodname"]
    c = 0
    offset = 2
    for dd in comboboxes[offset:]:

        #print("updating:", comboinputs[offset+c].get())
        dd["values"]=keyword_suggestion_keepdeja(KL, NL[c], comboinputs[offset+c])
        c+=1
    #topic = "mfgcode2mfgname

def dxl(d, keys):
    #is like calling a dict D[key]
    #but works with a list of keys
    #returns list of results (RESULTS NOT LIST THEMSELVES!)
    values = []
    for k in keys:
        values.append(d[k])
    return values
def inv_dict_keep_dup(d):
    inv_d = defaultdict(list)
    for k, v in d.items():
        inv_d[v].append(k)
    return inv_d
def a2dl(d, k, v):
    #add a value to a dicts key (list)
    if type(d)!=defaultdict:
        d = defaultdict(list)
    d[k].append(v)
    return d

def make_cross_dicts(D):
    print("crossdicting")
    #D={"x2y":{x1: y1}}
    #D.items values keys ()
    #prodcode2prodname
    #mfgcode2mfgname
    #prodcode2prodtype
    #prodcode2mfgcode
    #oscode2osname
    '''target:
    needed:
    prodcode2oscode from file in function make dict
    mfgcode2prodcode value=list
    oscode2prodcode value=list
    prodtype2prodcode value=list

    final goal:
    mfgname2osname value = list
    mfgname2prodtype value = list
    mfgname2prodname value = list

    osname2mfgname value = list
    osname2prodtype value = list
    osname2prodname value = list

    prodtype2mfgname value = list
    prodtype2osname value = list
    prodtype2prodname value = list

    prodname2mfgname
    prodname2osname
    prodname2prodtype
    '''
    #needed
    D["mfgcode2prodcode"]=inv_dict_keep_dup(D["prodcode2mfgcode"])
    D["prodtype2prodcode"]=inv_dict_keep_dup(D["prodcode2prodtype"])
    D["oscode2prodcode"]=inv_dict_keep_dup(D["prodcode2oscode"])
    D["mfgname2osname"]={k: dxl(D["oscode2osname"], dxl(D["prodcode2oscode"], D["mfgcode2prodcode"][c])) for c, k in D["mfgcode2mfgname"].items()}
    # D["mfgname2osname"]?{str: list}
    '''
    for i in D["mfgname2osname"]:
        print("---", bytes(i, "utf-8"))
        for e in D["mfgname2osname"][i]:
            print(bytes(e, "utf-8"))
    '''
    D["mfgname2prodtype"]={k: dxl(D["prodcode2prodtype"], D["mfgcode2prodcode"][c]) for c, k in D["mfgcode2mfgname"].items()}#
    D["mfgname2prodname"]={k: dxl(D["prodcode2prodname"],D["mfgcode2prodcode"][c]) for c, k in D["mfgcode2mfgname"].items()}#
    D["osname2mfgname"]={k: dxl(D["mfgcode2mfgname"], dxl(D["prodcode2mfgcode"], D["oscode2prodcode"][c])) for c, k in D["oscode2osname"].items()}
    D["osname2prodtype"]={k: dxl(D["prodcode2prodtype"], D["oscode2prodcode"][c]) for c, k in D["oscode2osname"].items()}
    D["osname2prodname"]={k: dxl(D["prodcode2prodname"], D["oscode2prodcode"][c]) for c, k in D["oscode2osname"].items()}

    D["prodtype2mfgname"]=defaultdict(list)
    for pt, mfgn in ((k, D["mfgcode2mfgname"][D["prodcode2mfgcode"][c]]) for c, k in D["prodcode2prodtype"].items()):######################
        a2dl(D["prodtype2mfgname"], pt, mfgn)

    D["prodtype2osname"]=defaultdict(list)
    for pt, osn in ((k, D["oscode2osname"][D["prodcode2oscode"][c]]) for c, k in D["prodcode2prodtype"].items()):
        a2dl(D["prodtype2osname"], pt, osn)

    D["prodtype2prodname"]=defaultdict(list)
    for pt, pn in ((k, D["prodcode2prodname"][c]) for c,k in D["prodcode2prodtype"].items()):
        a2dl(D["prodtype2prodname"], pt, pn)

    D["prodname2mfgname"]={k: [D["mfgcode2mfgname"][D["prodcode2mfgcode"][c]]] for c,k in D["prodcode2prodname"].items()}
    D["prodname2osname"]={k: [D["oscode2osname"][D["prodcode2oscode"][c]]] for c,k in D["prodcode2prodname"].items()}
    D["prodname2prodtype"]={k: [D["prodcode2prodtype"][c]] for c,k in D["prodcode2prodname"].items()}

    print("finished crossdicting")
    return D

def find_in_list(l, s):
    for elem in l:
        if elem.find(s)>=0:
            return True
    return False

def update_dropdowns_crossfilter():
    '''
    prodcode2prodname
    mfgcode2mfgname
    prodcode2prodtype
    prodcode2mfgcode
    oscode2osname
    prodcode2oscode 

    mfgcode2prodcode value=list
    oscode2prodcode value=list
    prodtype2prodcode value=list

    mfgname2osname value = list
    mfgname2prodtype value = list
    mfgname2prodname value = list

    osname2mfgname value = list
    osname2prodtype value = list
    osname2prodname value = list

    prodtype2mfgname value = list
    prodtype2osname value = list
    prodtype2prodname value = list

    prodname2mfgname
    prodname2osname
    prodname2prodtype

    #FILTER:
    MFG Suggestions:
        mfgsug must be in 
        OS translated to mfg
        Type
        Name
        if msgsub in os2mfg or 
    OS Suggestions:
    Type Suggestions:
    Name Suggestions:
    '''

    global KL 
    global comboinputs
    NL = ["mfgcode2mfgname", "oscode2osname", "prodcode2prodtype", "prodcode2prodname"]
    c = 0
    offset = 2
    for dd in comboboxes[offset:]:

        #print("updating:", comboinputs[offset+c].get())
        ks, fs =keyword_suggestion_keepdeja(KL, NL[c], comboinputs[offset+c])
        #ks = list of possible suggestions including former sug

        #Filter out ones that dont match
        #ks = [str, str, str]
        #c=                 0    1     2        3 
        #dd = current box (Mfg, OS, prodtype, prodname)
        filtered_ks=[]



        # at which one?
        cur = NL[c][NL[c].find("2")+1:]
        others = [x[x.find("2")+1:] for x in NL if x!=NL[c]]
        cis = comboinputs[offset:]
        del cis[c]
        ois = [each.get() for each in cis]
        tois=[]
        for i in ois:
            t = StringIO(i)
            m=False
            for line in csv.reader(t, delimiter=",", skipinitialspace=True, escapechar="\\"):
                tois.append(line)
                m=True
            if not m:
                tois.append("")
        ois=tois

        #print(ois)
        #print("______________________")
        #ois = [["","",""],["","",""]]


        c2 = 0
        other_trans=[]
        for other in others:
            #print(ois, "--", ois[c2], type(ois[c2]))
            other_trans.append([D[other+"2"+cur][x] if type(D[other+"2"+cur])==defaultdict else D[other+"2"+cur].get(x, [""]) for x in ois[c2]])
            #other_trans = list (of lists) = [input, input] -> input=[translated, translated] //of the same topic so now OR input
            #other_trans=[[],[],[]]
            c2 += 1
        c3=0

        for l in other_trans:
            if l==[]:
                other_trans[c3]=[[""]]
            c3+=1
        
        #print(len(other_trans))
        for i in other_trans:
            pass
            #print("..", len(i))
            #print("...", type(i[0]))
        #other_trans=[[[1,1,1],[2,2,2],[3,3,3]],[[""]],[[""]]]

        #other_trans=list of lists of lists of strings
        #[mfg, os, ...] -> mfg = [Microsoft, Riot, ...] -> Microsoft = ["Windwos", "Word"] // mfg = [""]

        #print("othertrans:", bytes(other_trans[0][0]+other_trans[1][0]+other_trans[2][0], "utf-8"))
        minthreshhold=3 #n of other filters
        
        #csv reader read formerstring of already inputed:
        fsl = []
        for line in csv.reader(StringIO(fs), delimiter=",", skipinitialspace=True, escapechar="\\"):
            fsl=line

        for elem in ks:
            curscore = 0
            #other inputs = comboinputs
            #if c=3
            #elem must be in in other inputs (mfg)
            #elem must be in 
            for ot in other_trans:
                #print(elem)
                if ot != [""]:
                    pass
                #print("OT:", ot)
                #ot = mfg = [input1, input2] last input might be incomplete!
                fh=False
                for subot in ot:#SubOT = one specific term, is list because translated to multiple possible states
                    
                    if elem in subot or subot==[""] or find_in_list(subot, elem):
                        #print(elem, ":", subot)
                        fh=True
                if fh:
                    curscore+=1
            #print(curscore)
            if curscore >= minthreshhold and not elem in fsl:
                if elem.find("\\")>=0:
                    print("____---____")
                    print(elem)
                    print(fs)
                    print(fsl)
                    print(fs+' "'+elem+'"')
                filtered_ks.append(fs+' "'+elem.replace("\t", "").replace("\\", "")+'"')
            #elem muss in allen other sein AND other
           


        dd["values"]=filtered_ks
        c+=1
    #topic = "mfgcode2mfgname

def update_dropdowns_debug():
    #prodcode2prodname
    #mfgcode2mfgname
    #prodcode2prodtype
    #oscode2osname
    print("p")
    global KL
    global comboinputs
    NL = ["mfgcode2mfgname", "oscode2osname", "prodcode2prodtype", "prodcode2prodname"]
    c = 0
    offset = 2
    for dd in comboboxes[offset:]:
        print("updating:", comboinputs[offset+c].get())
        sugs = keyword_suggestion(KL, NL[c], comboinputs[offset+c])
        for sug in sugs:
            print(sug)
            dd["values"]=[sug]
        
        

            root.update_idletasks()
            root.update()
        c+=1
    #topic = "mfgcode2mfgname
####################################################################################################################
if __name__ == '__main__':
    multiprocessing.freeze_support()




##############################################################################





    root=Tk()
    KL_exists = False

    class Window(Frame):
        '''
        THE GUI
        '''
        def __init__(self, master=None):
            
            Frame.__init__(self, master)
            self.master = master
            self.pack(fill=BOTH, expand=1)



    #Progressbar: only used in standalone verison
    #pb = ttk.Progressbar(info, orient="horizontal", length=200, mode="determinate")
    #pb.pack(side=BOTTOM)
    #pb["maximum"] = 100
    #pb["value"] = 0
    #pb.update_idletasks()

    
    ################
    ### THE  GUI ###
    ################
    labelwidth = 15
    nrows = 6
    rows = []
    textlabels = []
    texts = [".iso File:", "File Extension:", "Hersteller:", "OS:", "Produkt-Typ:", "Produkt:"]
    comboinputs = []
    #comboplaceholder = ["nsrl.iso", '".exe",".jpg"', '"Microsoft", "Apple"', '"Windows"', '"Antivirus"', '"WindowsDefender"']
    comboplaceholder = ["", '', '', '', '', '']
    selections=[]
    comboboxes=[]
    #MAKE ROWS
    for i in range(nrows):
        #ROW
        rows.append(Frame(root))
        rows[i].pack(side=TOP, fill=X, padx=5, pady=5)
        #DESCR
        textlabels.append(Label(rows[i], text=texts[i], font=("Helvetica", 12), anchor=W, justify=LEFT, width=labelwidth))
        textlabels[i].pack(side=LEFT, padx=10, pady=10)
        #COMBOBOX
        comboinputs.append(StringVar())
        comboinputs[i].set(comboplaceholder[i])
        selections.append([])
        comboboxes.append(Combobox(rows[i], textvariable=comboinputs[i], values=selections[i]))
        comboboxes[i].pack(side=LEFT, expand=YES, fill=X, padx=10, pady=10)

    # ROW 0

    #The Start Button "Run"
    #Declares D (Dictionary to translate info in Hash to what sb entered)
    #Creates tmpfolder
    startbutton_txt = StringVar()
    startbutton_txt.set("Extract .iso")
    startbutton = Button(rows[0], textvariable=startbutton_txt, command=handle_iso)
    startbutton.pack(side=RIGHT, padx=10, pady=10)

    #The Iso Button "Choose .iso"
    #Declares global isofile with path of .iso
    isobutton = Button(rows[0], text="Select .iso", command=choose_iso)
    isobutton.pack(side=RIGHT, padx=10, pady=10)

    # RUNROW
    runrow=Frame(root)
    runrow.pack(side=TOP, fill=X, padx=5, pady=5)
    spaceleft = Label(runrow, text="", font=("Helvetica", 12), anchor=W, justify=LEFT, width=labelwidth)
    spaceleft.pack(side=LEFT, padx=10, pady=10)
    #XWays AXIOM Button Export
    finalbutton1 = Button(runrow, text="Export for X-Ways & AXIOM", command=finalexport1)
    finalbutton1.pack(side=RIGHT, padx=10, pady=10)
    #Nuix & UFED Button Export
    finalbutton2 = Button(runrow, text="Export for Nuix & UFED", command=finalexport2)
    finalbutton2.pack(side=RIGHT, padx=10, pady=10)

    #Status Text Label
    statusrow = Frame(root)
    statusrow.pack(side=TOP, fill=X, padx=5, pady=5)
    statustext = StringVar()
    statustext.set("Status: idle")
    statuslabel = Label(statusrow, textvariable=statustext, font=("Helvetica", 12), anchor=W, justify=LEFT, width=labelwidth*2)
    statuslabel.pack(side=LEFT, padx=10, pady=10)
    #Result Text Label
    resulttext = StringVar()
    resultlabel = Label(statusrow, textvariable=resulttext, font=("Helvetica", 12), anchor=W, justify=LEFT, width=labelwidth*2)
    resultlabel.pack(side=LEFT, padx=10, pady=10)
    

    #GUI Window Title and Size:
    root.wm_title("NSRL Hash Selector")
    root.geometry(str(int(800))+"x"+str(int(800)))

    #Make the left-Labels the same size:
    root.update()

    
    selections[1]=["0"]

    prevcomboinputs=["" for each in comboinputs]
    print("entering mainloop")
    while 1:
        root.update_idletasks()
        root.update()    
        if KL_exists:
            #only update dropdowns if the input changed, takes a long time to update
            if prevcomboinputs != [each.get() for each in comboinputs]:
                print(prevcomboinputs)
                print([each.get() for each in comboinputs])

                update_dropdowns_crossfilter()
                prevcomboinputs=[each.get() for each in comboinputs]
                print("updates comboboxes")



        #tkinter GUI mainloop, after that (after user clicks Run button) the whole program runs




