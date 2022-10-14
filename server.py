import requests, replitdb, asyncio, flask
from threading import Thread
import urllib.parse
import aiohttp
from aiohttp import web
import requests

dab = replitdb.AsyncClient()
app = flask.Flask(__name__)

"""
@app.route('/') #old main page
def index():
  return flask.render_template('index.html')
"""

@app.route("/") #new main page with login
def login():
  
  return flask.render_template('login.html',
        user_id=flask.request.headers['X-Replit-User-Id'],
        user_name=flask.request.headers['X-Replit-User-Name']
    )


@app.route("/factory")
def factory():
  return flask.render_template('factory.html')




@app.route("/others")
def others():
  return flask.render_template('others.html')

@app.route("/ping")
def ping():
  return "200" #backup pinger

@app.route("/coolpeeps")
def pplwhousethis():
  pongs = str(asyncio.run(dab.view('pings'))).split('\n')
  coolpeeps = "Cool peeps who use this pinger: Raadsel"
  coolpeepsarr = ["raadsel"]
  for i in pongs:
    try:
      o, name, repl, co = i.split(".")
      if not name in coolpeepsarr:
        coolpeepsarr.append(name)
        coolpeeps += f", {name}"
        print(f"NEW COOLPEEP {name}")
        print(coolpeeps)
      else: 
        print("already in")
        continue
    except:
      print("not repl thing")
      continue
  return flask.render_template('coolpeeps.html', peeps=coolpeeps)
  

async def remove(url):
  pings = str(dab.view('pings')).split('\n')
  dab.set(pings=str(dab.view('pings')).replace("\n"+url, ""))


async def check_replit(url, username, s=None):
  url = urllib.parse.urlparse(url)
  host = url.netloc
  url = f'https://{host}/__repl'
  own_session = False
  if not s:
    timeout = aiohttp.ClientTimeout(total=15)
    s = aiohttp.ClientSession(timeout=timeout)
    own_session = True

  try:
    r = await s.get(url)
    if own_session: await s.close()
    if str(r.status)[0] == '4' and not str(r.url).startswith('https://replit.com/'):
      print(r.status, str(r.url))
      return False
    else:
      return False
    print(url, r.url, r.status)

  except Exception as e:
    print(type(e), e, '----- WARNING ')
    if own_session: await s.close()
    return True


  
async def check_owner(url, username, s=None):
  url = urllib.parse.urlparse(url)
  host = url.netloc
  url = f'https://{host}/__repl'
  own_session = False
  if not s:
    timeout = aiohttp.ClientTimeout(total=15)
    s = aiohttp.ClientSession(timeout=timeout)
    own_session = True

  try:
    r = await s.get(url)
    if own_session: await s.close()
    if str(r.status)[0] == '4' and not str(r.url).startswith('https://replit.com/'):
      print(r.status, str(r.url))
      return False
    print(url, r.url, r.status)
    inputuser1 = str(r.url)
    inputuser1 = inputuser1.replace("https://replit.com/@", "")
    inputuser, slug = inputuser1.split("/")
    print(inputuser)
    
    with open("projects.txt", "a") as f:
      f.write(f"{r.url}\n")
    if username == inputuser:
      print("check_replit: ", username, "is the owner")
      return True
    else:
      print("check_replit: ", username, "is not the owner")
      return False
  except Exception as e:
    print(type(e), e, '----- WARNING ')
    if own_session: await s.close()
    return True



@app.route('/stats')
def stats():
  with open("pings.txt", "r") as v:
    content = v.read()
  replcount = str(asyncio.run(dab.view('pings'))).split('\n')
  replcount = str(len(replcount))
  pingcount, online, offline = content.split('\n')
  try:
    onlinepercent = round(int(online) / int(pingcount) * 100)
    onlinepercent = str(onlinepercent).replace('.0', '%')
  except: onlinepercent = 'ERROR WITH CALCULATION! TRY AGAIN LATER. (MY CAPS IS STUCK HELP)'
    
  return flask.render_template('stats.html', count=replcount, online=str(onlinepercent), pings="soon")



def checknames(inname):
  pongs = str(asyncio.run(dab.view('pings'))).split('\n')
  pingercount = 0
  names = []
  for i in pongs:
    try:
      o, name, repl, co = i.split(".")
      if name.lower() == 'raadsel':
        return 0
      if not o in names:
        names.append(o)
        if repl.lower() == inname.lower():
          pingercount += 1
      else:
        continue
    except:
      continue
  print(pingercount)
  return pingercount




  
@app.route('/add', methods=['POST'])
def send():
  newPing = flask.request.form['add']
  pings = str(asyncio.run(dab.view('pings'))).split('\n')
  rawpings = str(asyncio.run(dab.view('pings')))
  print(str(asyncio.run(dab.view('pings'))))
  print(pings)
  # remove ping
  if 'X-Replit-User-Name' in flask.request.headers:
   username = flask.request.headers['X-Replit-User-Name']
  is_replit = asyncio.run(check_replit(newPing, username))
  if not is_replit:
    return flask.render_template('msg.html', message="This is not a replit server, or this isnt a Repl from you!! RDSL Uptimer only supports Replit projects, that were added by there owners!")
  is_owner = asyncio.run(check_owner(newPing, username))
  if not is_owner:
    return flask.render_template('msg.html', message="This isnt a Repl from you!! RDSL Uptimer only pings Repls with permission from their owners!")
  newPing = newPing.lower()
  remPing = newPing.replace("rem ", "", 1)
  if remPing in pings and newPing.startswith("rem "):
    #newPings = str(asyncio.run(dab.view('pings')).replace(remPing+"\n", ""))
    #print(newPings)
    #asyncio.run(dab.set())

    asyncio.run(dab.set(pings=rawpings.replace("\n"+remPing, "")))
    print("removed "+remPing)
    print(str(asyncio.run(dab.view('pings'))))
    return flask.render_template('msg.html', message="Removed "+remPing)

    
  if newPing not in pings:
    if newPing.startswith("http"):
    # ping the newping
      try:
        reqq = requests.get(newPing)
        if not reqq.status_code in [200, 304, 100, 201, 202, 206, 302]:
          return flask.render_template('msg.html', message="Invalid URL! Please make sure you configured the webserver right!")
        if checknames(newPing) >= 25:
          return flask.render_template('msg.html', message="You are already at 25 replits! Thats the max we ping. Also you can't have more then 20 Repls online at the same time on your Replit account, so its useless anyway. You can remove repls by inputting `rem + replurl` to the urlpinger input.")
        asyncio.run(dab.set(pings=str(asyncio.run(dab.view('pings'))) + '\n' + newPing))
        return flask.render_template('msg.html', message="URL successfully Added! consider tipping me at the bottom-right of the site, since you get one dollar for free!")
      except:
        return flask.render_template('msg.html', message="Invalid URL! Please make sure you configured the webserver right!")
    else:
      return flask.render_template('msg.html', message="Invalid URL! Please put in a valid URL including protocols like https://!") # I know that a URL should always start with protocols like https://, but some peeps dont
  else:
    return flask.render_template('msg.html', message="I am already pinging that URL!")


@app.route('/api/cli', methods=['POST']) #yes ik this is less protected (w\out repl auth)
def sendcli():
  
  newPing = flask.request.form['add']
  pings = str(asyncio.run(dab.view('pings'))).split('\n')
  rawpings = str(asyncio.run(dab.view('pings')))
  print(str(asyncio.run(dab.view('pings'))))
  print(pings)
  # remove ping
  is_replit = asyncio.run(check_replit(newPing))
  if not is_replit:
    return "This is not a replit server! RDSL Uptimer only supports Replit projects!"
  newPing = newPing.lower()
  remPing = newPing.replace("rem ", "", 1)
  if remPing in pings and newPing.startswith("rem "):
    #newPings = str(asyncio.run(dab.view('pings')).replace(remPing+"\n", ""))
    #print(newPings)
    #asyncio.run(dab.set())

    asyncio.run(dab.set(pings=rawpings.replace("\n"+remPing, "")))
    print("removed "+remPing)
    print(str(asyncio.run(dab.view('pings'))))
    return "200 - Succesfully Removed "+remPing

    
  if newPing not in pings:
    if newPing.startswith("http"):
      try:
        
        requests.get(newPing)
        asyncio.run(dab.set(pings=str(asyncio.run(dab.view('pings'))) + '\n' + newPing))
        print(f"Added {newPing} to the database via CLI")
        return "200 - URL successfully Added! consider tipping me at https://zink.tips/raadsel, since you get one dollar for free!"
      except:
        return "Invalid URL! Please make sure you configured the webserver right!"
    else:
      return "Invalid URL! Please put in a valid URL including protocols like https://!" # I know that a URL should always start with protocols like https://, but some peeps dont
  else:
    return "226 - I am already pinging that URL!"


import random
def run():
  from waitress import serve
  serve(app, host='0.0.0.0', port=random.randint(1000, 9999))
  
def actualrun():  
    t = Thread(target=run)
    t.start()