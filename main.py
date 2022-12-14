print("""
Copyright 2022 Raadsel

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
""") #cool license
# watch out! More docs than code ahead!
# imports
import requests, replitdb, asyncio, json # to ping, replitDB, and asyncio for replitDB async and json for config values
from server import actualrun # loads site
import aiohttp #to ping
import time

actualrun()


dab = replitdb.AsyncClient()

with open("config.json") as f:
  data = json.load(f)
  f.close()

# all variables from config json
TIMEOUT = data["PINGER"]["TIMEOUT"] #timeout with pings in seconds
SLEEPTIME = data["PINGER"]["SLEEPTIME"]
SLEEPONSTART = data["PINGER"]["SLEEPONSTART"]
LASTPING = 0
printallonstart = data["PINGER"]["PRINTALLONSTART"]

Startuptime = round(time.time()) # time that the repl started

if printallonstart:
  
  print("All sites in DB:") #all sites in DB
  print(asyncio.run(dab.view('pings')))


def remove(remPing): #remove a repl
  rawpings = str(asyncio.run(dab.view('pings')))
  asyncio.run(dab.set(pings=rawpings.replace("\n"+remPing, "")))


async def ping(starttime): #pinging
  ping=0
  an=0
  gn=0
  bn=0
  lst = []
  pings = str(await dab.view('pings')).split('\n') #get list of all URLS in db

  with open("./data/pings.txt", "r") as f:
    pingdata = f.read()
  
  all, succes, failed, allpingsever, timebetweenpingss = pingdata.split("\n")#-1 bcuz empty first one, the other -1 because this one starts at 0?
  print(f"Pinging {all} repls:")

  for i in pings:
    if i not in lst:
      try:
        if i != '':
          timeout = aiohttp.ClientTimeout(total=TIMEOUT) #timeout max
          async with aiohttp.ClientSession(timeout=timeout) as session: #now using aiohttp instead of requests
            async with session.get(i) as resp:
              
              if resp.status in [200, 304, 100, 201, 202, 206, 302]: #succesfully pinged
                an += 1
                gn += 1
              
              else:
                an+=1
                bn+=1 
                if resp.status == 404: # if it 404s
                  with open("./data/404s.txt", "r") as v:
                    replswitfouro = v.read().split("\n")
                  if i not in replswitfouro: 
                    with open("./data/404s.txt", "a") as f:
                      f.write(i+"\n")
                  continue

                # failed

                print(f"\033[31mFailed: {i}\nStatus code: {resp.status}\nTimestamp: {time.time()}\nQueue: {an}/{all}\033[0\nm")
                continue
              print(f"\033[32mPong: {i}\nStatus code: {resp.status}\nTimestamp: {time.time()}\nQueue: {an}/{all}\033[0m\n")
          
      except Exception as e:
        print(f"\033[31mFailed: {i} \nStatus code: probably timed out - {e}\nTimestamp: {time.time()}\nQueue: {an}/{all}\033[0m\n") # exception appeared. Useally timeout error. 
        an+=1
        bn+=1 
        continue
      lst.append(i) #appends url to list with done pinged
      ping+=1
  with open("./data/pings.txt", "r") as v: 
    impdata = v.read()
    donepings, goodpings, notgoodpings, allpings, betweenpings = impdata.split('\n') # gets data
    totalPings = int(allpings) + ping #all pings that have been SEND. Not necissarily received
    end = time.time()
    totaltime = end - starttime
    betweenpings = totaltime + SLEEPTIME
  with open("./data/pings.txt", "w") as v:
    v.write(f'{an}\n{gn}\n{bn}\n{totalPings}\n{round(betweenpings)}') #adds data to data file
  
  print(f"Total sent & received pings: {ping}")
  print(f"Total sent pings: {an}")


  


  
      

async def loop(): # looping ping system

  while True:
    print(" ==================== Pinging ==================== \n")
    start = time.time()
    await ping(start) #start pinging
    end = time.time()
    totaltime = end - start
    print(f" =============== Done with pinging =============== \nTook: {round(totaltime, 1)} seconds\nFun fact: This repl has been online for {round(time.time()) - Startuptime} seconds!\nSleeping {SLEEPTIME} seconds...")
    print(LASTPING)
    if start + 50 + SLEEPTIME< end: #if somehow it gets overloaded
      print("Pinging took too long, ignoring sleep time...")
      continue
    else:
      await asyncio.sleep(SLEEPTIME) #sleep

if SLEEPONSTART != 0:
    print(f"\n\033[31mSleeping {SLEEPONSTART} seconds before I start pinging!\033[0m\n")
time.sleep(SLEEPONSTART)

# run the program
asyncio.run(loop())

"""
 * @INFO
 * RDSL Pinger Coded by Raadsel#9398 | https://replit.com/@Raadsel
 * @INFO
 * Please mention Me, when using this Code!
 * @INFO
 """
