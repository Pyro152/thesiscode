import csv

from pprint import pprint
import requests

import numpy as np

import sys
import json


infile=open('3leLEO.txt','r')
tlelist=infile.read()
lines=tlelist.splitlines()

satinfolist=[]  #format [number, name, inc, mass(added later)]
for i in range(len(lines)):
    if i%3 == 2:
        satinfolist.append([int(lines[i][2:7]),lines[i-2][0:24],float(lines[i][8:16])])
        
#print(len(satinfolist))


URL = 'https://discosweb.esoc.esa.int'
token = 'IjJmOTQ0NjkzLTY5MjUtNGJjYi05NzRjLTZiMWFkOWJkZDdkMCI.IfGYzT-GQrbGivJvfQbVjPwJKuE'

searchkey=tuple(satellite[0] for satellite in satinfolist)
#print(str(searchkey))

splitnum=30
bitesize=tuple(tuple(searchkey[i:i+splitnum]) for i in range(0,len(searchkey),splitnum))
#pprint(bitesize)
'''
#bitesize=bitesize[0:7]
satellitesmasses={}
for bite in bitesize:
    #remove spaces from bite
    bitestr=str(bite)
    bitestr=bitestr.replace(' ','')
    
    #get satellite info
    response = requests.get(
        f'{URL}/api/objects',
        headers={
            'Authorization': f'Bearer {token}',
            'DiscosWeb-Api-Version': '2',
        },
        params={
            'filter': "in(satno," + bitestr + ")",
        },
    )
    
    try: 
        data=response.json()
    except Exception:
        print('failure!')
        print(response.status_code)
        print(response.text)
        sys.exit()
        
    if response.ok:
        print('downloaded successful!')
        datalen=len(data['data'])
        pprint(datalen)
        for sat in data['data']:
            satellitesmasses[sat['attributes']['satno']]=sat['attributes']['mass']
            #satellitesmasses[data['data'][i]['attributes']['satno']]=data['data'][i]['attributes']['mass']
    else:
        pprint(data['errors'])
        
print(satellitesmasses)

with open("output.json", "w") as f:
    json.dump(satellitesmasses, f, indent=4)

    
'''


with open("output.json", "r") as f:
    mydict = json.load(f)


#parse
incdict={}
skippedlist=[]
print(len(satinfolist))
for i in range(len(satinfolist)):
    print(i)
    try:
        mass=mydict[str(satinfolist[i][0])]      
        satinfolist[i].append(mass)
        
        if mass is None:
            print('Skipped satellite ',satinfolist[i][0],', ',satinfolist[i][1],'!')
        else:
            inc=satinfolist[i][2]
            if inc > 90:
                inc=180-inc
            if inc == 90:
                inc=89.9
            
            incbin=int(inc)
            if incbin in incdict:
                incdict[incbin][1]+=mass
            else:
                incdict[incbin]=['inc '+str(incbin)+' - '+str(incbin+1),mass,incbin+0.5]
    except Exception:
        skippedlist.append(satinfolist[i][0])
        
print(skippedlist)
pprint(incdict)

forprint=list(incdict.values())


with open("satconstinfo.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["number", "mass", "inc"])
    for entry in forprint:
        writer.writerow(entry)
    
