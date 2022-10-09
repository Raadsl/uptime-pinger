import requests, replitdb, asyncio
from server import actualrun


actualrun()


dab = replitdb.AsyncClient()


print(asyncio.run(dab.view('pings')))

async def ping():
  
  an=0
  gn=0
  bn=0
  lst = []
  pings = str(await dab.view('pings')).split('\n')
  for i in pings:
    if i not in lst:
      try:
        if i != '':
          requests.get(i)
          an+=1
          gn+=1
          
      except:
        an+=1
        bn+=1 
        continue
      lst.append(i)
    with open("pings.txt", "w") as v:
      v.write(f'{an}\n{gn}\n{bn}')
      

async def loop():

  while True:

    await ping()
    await asyncio.sleep(16)

asyncio.run(loop())
#loop1 = asyncio.get_event_loop()
#loop1.run_until_complete(loop())
#loop1.close()
