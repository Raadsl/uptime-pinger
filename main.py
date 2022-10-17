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
import requests, replitdb, asyncio # to ping, replitDB, and asyncio for replitDB async
from server import actualrun # loads site
import aiohttp #to ping

actualrun()


dab = replitdb.AsyncClient()

print("All sites in DB:") #cool
print(asyncio.run(dab.view('pings')))

async def ping(): #pinging
  ping=0
  an=0
  gn=0
  bn=0
  lst = []
  pings = str(await dab.view('pings')).split('\n') #get list of all URLS in db
  for i in pings:
    if i not in lst:
      try:
        if i != '':
          timeout = aiohttp.ClientTimeout(total=10) #10 seonds timeout max
          async with aiohttp.ClientSession(timeout=timeout) as session: #now using aiohttp instead of requests
            async with session.get(i) as resp:
              if resp.status in [200, 304, 100, 201, 202, 206, 302]:
                an += 1
                gn += 1
                bn += 1
              else:
                an+=1
                bn+=1 
                print(f"Failed: {i} - {resp.status}")
              print(f"Pong: {i} - {resp.status}")
          
          await asyncio.sleep(.05)
      except:
        print(f"Failed: {i} - timed out probably") # exception appeared. Useally timeout error. No i dont feel like making an exception catcher only for timeouts and another for others things
        an+=1
        bn+=1 
        continue
      lst.append(i) #appends url to list with done pinged
      ping+=1
  with open("./data/pings.txt", "r") as v: #opens file. Using this file instead of replitDB because.... idk. It works now. Thats alright for now=)
    impdata = v.read()
    donepings, goodpings, notgoodpings, allpings = impdata.split('\n') # gets data
    totalPings = int(allpings) + ping #all pings that have been SEND. Not necissarily received
  with open("./data/pings.txt", "w") as v:
    v.write(f'{an}\n{gn}\n{bn}\n{totalPings}') #adds data to data file
    
  print(ping)
  #with open("data/allpings.txt", "a+") as f:
    #pongs = f.read()
    #totalpings = int(pongs)+pings
    #f.write(f'{totalpings}')
    
    

  
      

async def loop(): # looping ping system

  while True:
    print("Pinging\n")
    await ping() #start pinging
 
    print("done with pinging")
    await asyncio.sleep(60) #sleep

asyncio.run(loop())
#loop1 = asyncio.get_event_loop()
#loop1.run_until_complete(loop())
#loop1.close()

"""
 * @INFO
 * RDSL Pinger Coded by Raadsel#9398 | https://replit.com/@Raadsel
 * @INFO
 * Please mention Me, when using this Code!
 * @INFO
 """
# I am still doing it KEKW: Credits format from replit.com/discordaddict :)