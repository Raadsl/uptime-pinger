import requests, replitdb, asyncio
from server import actualrun
import aiohttp

actualrun()


dab = replitdb.AsyncClient()

print("All sites in DB:")
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
          timeout = aiohttp.ClientTimeout(total=10)
          async with aiohttp.ClientSession(timeout=timeout) as session:
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
      except Exception as e:
        print(f"Failed: {i} - timed out probably")
        an+=1
        bn+=1 
        continue
      lst.append(i)
  with open("pings.txt", "w") as v:
    v.write(f'{an}\n{gn}\n{bn}')
    

  
      

async def loop():

  while True:
    print("Pinging\n")
    await ping()

    print("done with pinging")
    await asyncio.sleep(16)

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