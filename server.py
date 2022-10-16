import requests, replitdb, asyncio, flask
from flask import make_response
from threading import Thread
import urllib.parse
import aiohttp
from aiohttp import web
import requests

Lockdown = False
admins = ["Raadsel"]

dab = replitdb.AsyncClient()
app = flask.Flask(__name__)

"""
@app.route('/') #old main page
def index():
  return flask.render_template('index.html')
"""

@app.route("/") #new main page with login
def login():
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302
  
  return flask.render_template('login.html',
        user_id=flask.request.headers['X-Replit-User-Id'],
        user_name=flask.request.headers['X-Replit-User-Name']
    ), 200

@app.route("/devindex") #new main page with login - Lockdown mode imune
def devindex():
  
  return flask.render_template('dev.html',
        user_id=flask.request.headers['X-Replit-User-Id'],
        user_name=flask.request.headers['X-Replit-User-Name']
    )

@app.route("/admin")
def admin():
  
  if flask.request.headers.get('X-Replit-User-Name') in admins:
    return flask.render_template("admin.html",
                           user_id=flask.request.headers['X-Replit-User-Id'],
                           user_name=flask.request.headers['X-Replit-User-Name'])
  else:
    return "You are not an admin!"


  
@app.route("/factory")
def factory():
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302
  return flask.render_template('factory.html'), 200

@app.route("/api")
def api():
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302
  return flask.render_template('/info/api.html',
        user_id=flask.request.headers['X-Replit-User-Id'],
        user_name=flask.request.headers['X-Replit-User-Name']
    ), 200


@app.route('/logout')
def logout():
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302
  resp = make_response(flask.render_template('removing-cook.html'))
  resp.delete_cookie("REPL_AUTH", path='/', domain="up.rdsl.ga")
  return resp

@app.route("/others")
def others():
  return flask.render_template('others.html'), 200 # imune to lockdown


@app.route("/FAQ")
def faqhtml():
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302
  return flask.render_template('/info/FAQ.html'), 200

@app.route("/TOS")
def toshtml():
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries! To view the clean TOS go to https://up.rdsl.ga/static/tos.txt", 302
  return flask.render_template('/info/TOS.html'), 200
  

@app.route("/ping")
def ping():
  return "200", 200 #backup pinger - - Lockdown mode imune

@app.route("/coolpeeps")
def pplwhousethis():
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302
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
  print("checking replit")
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
      return True
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
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302
  with open("pings.txt", "r") as v:
    content = v.read()
  replcount = str(asyncio.run(dab.view('pings'))).split('\n')
  replcount = str(len(replcount))
  pingcount, online, offline = content.split('\n')
  try:
    onlinepercent = round(int(online) / int(pingcount) * 100)
    onlinepercent = str(onlinepercent).replace('.0', '%')
  except: onlinepercent = 'ERROR WITH CALCULATION! TRY AGAIN LATER. (MY CAPS IS STUCK HELP)'
    
  return flask.render_template('stats.html', count=replcount, online=str(onlinepercent), pings="soon"), 200



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




  
@app.route('/add', methods=['POST']) #add repls by POST request
def send():
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302
  newPing = flask.request.form['add']
  pings = str(asyncio.run(dab.view('pings'))).split('\n')
  rawpings = str(asyncio.run(dab.view('pings')))
  print(str(asyncio.run(dab.view('pings'))))
  print(pings)
  # remove ping
  if 'X-Replit-User-Name' in flask.request.headers:
   username = flask.request.headers['X-Replit-User-Name'] #Check name
  is_replit = asyncio.run(check_replit(newPing, username))
  if not is_replit: #check if site is from repl
    return flask.render_template('msg.html', message="This is not a replit server, or this isnt a Repl from you!! RDSL Uptimer only supports Replit projects, that were added by there owners!")
  is_owner = asyncio.run(check_owner(newPing, username))
  if not is_owner: #check if user is the owner
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
        if not reqq.status_code in [200, 304, 100, 201, 202, 206, 302]: #check if site is online
          return flask.render_template('msg.html', message="Invalid URL! Please make sure you configured the webserver right!")
        if checknames(newPing) >= 25:
          return flask.render_template('msg.html', message="You are already at 25 replits! Thats the max we ping. Also you can't have more then 20 Repls online at the same time on your Replit account, so its useless anyway. You can remove repls by inputting `rem + replurl` to the urlpinger input.")
        asyncio.run(dab.set(pings=str(asyncio.run(dab.view('pings'))) + '\n' + newPing))
        return flask.render_template('msg.html', message="URL successfully Added! consider tipping me at the bottom-right of the site, since you get one dollar for free!"), 200
      except:
        return flask.render_template('msg.html', message="Invalid URL! Please make sure you configured the webserver right!")
    else:
      return flask.render_template('msg.html', message="Invalid URL! Please put in a valid URL including protocols like https://") # I know that a URL should always start with protocols like https://, but some peeps dont
  else:
    return flask.render_template('msg.html', message="I am already pinging that URL!"), 226 # If the url is already in the database


@app.route('/api/cli', methods=['POST']) #yes ik this is not protected by repl auth
def sendcli():
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302
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
    return "200 - Succesfully Removed "+remPing, 200

    
  if newPing not in pings:
    if newPing.startswith("http"):
      try:
        
        requests.get(newPing)
        asyncio.run(dab.set(pings=str(asyncio.run(dab.view('pings'))) + '\n' + newPing))
        print(f"Added {newPing} to the database via CLI")
        return "200 - URL successfully Added! consider tipping me at https://zink.tips/raadsel, since you get one dollar free credits to up!", 200
      except:
        return "Invalid URL! Please make sure you configured the webserver right!"
    else:
      return "Invalid URL! Please put in a valid URL including protocols like https://!" # I know that a URL should always start with protocols like https://, but some peeps dont
  else:
    return "226 - I am already pinging that URL!", 226


#ERROR HANDLING
@app.errorhandler(404)
def page_not_found(e):
    return flask.render_template('/errors.html', error=404, msg="It looks like you got a 404 error! The page you are looking for is not here D:"), 404

@app.errorhandler(500)
def internal_error(e):
    return flask.render_template('/errors.html', error=500, msg="The server failed to complete the request because server encountered an error"), 500


import random
def run():
  print("[Waitress] Server started")
  from waitress import serve
  serve(app, host='0.0.0.0', port=random.randint(1000, 9999))
  
def actualrun():  
    t = Thread(target=run)
    t.start()



"""
 * @INFO
 * RDSL Pinger Coded by Raadsel#9398 | https://replit.com/@Raadsel
 * @INFO
 * Please mention Me, when using this Code!
 * @INFO
 """



