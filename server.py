"""
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
"""
import requests, replitdb, asyncio, flask
from flask import make_response, jsonify, redirect
import json
from threading import Thread
import urllib.parse
import aiohttp
from aiohttp import web
import os
# limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hashlib # hashing a IP

# ============================ DEFINING VARIABLES ============================
with open("config.json") as f:
  data = json.load(f)
  f.close()

bannednames = data["SERVER"]["BANNEDNAMES"] #bans someone from using the front-end API. 
bannedIPs = data["SERVER"]["BANNEDIPS"] #bans a hashed ip from the cli api
Lockdown = data["SERVER"]["LOCKDOWN"] #lockdowns the pinger
ultraLockdown = data["SERVER"]["ULTRALOCKDOWN"] #lockdowns the entire pinger and every webpage -- still pings
admins = data["SERVER"]["ADMINS"] # admins that can add/remove all sites w/out being owner
admins.append(os.environ["EXTRA_ADMIN"])
MAXREPLS = data["SERVER"]["MAXREPLS"] #max repls allowed by a user to be added


dab = replitdb.AsyncClient() #replitdb var
app = flask.Flask(__name__) #flask var

limiter = Limiter( #ratelimits
    app,
    key_func=get_remote_address,
    default_limits=["100 per 15 minutes"],
    storage_uri="memory://",
)
# ============================ DEFINING VARIABLES ============================


if ultraLockdown: Lockdown = True #lockdown
if os.environ["REPL_ID"] != "1fcd37d8-24c8-455d-a7eb-abbbc3a0b45a": Lockdown = True
"""
@app.route('/') #old main page without login
def index():
  return flask.render_template('index.html')
"""

@app.route("/") #new main page with login
@app.route("/login")
@limiter.exempt
def login():
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302 #lockdownmode
    
      # check for banned hashed IP's
  ip = flask.request.remote_addr
  ipHash = hashlib.md5(ip.encode('utf-8')).hexdigest()
  if checkIP(ipHash): return flask.render_template("msg.html", message="This IP has been banned from using RDSL uptimer", removeInput=True)
  try:
    username = flask.request.headers['X-Replit-User-Name']
    userid = flask.request.headers['X-Replit-User-Id']
  except:
    username=None
    userid=None
  return flask.render_template('login.html',
        user_id=userid,
        user_name=username
    ), 200 #renders template

# ============================ Mobile pages ============================
@app.route("/m/") #new main page with login
@limiter.exempt
def login_mobile():
  if Lockdown: # lockdown
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302 #lockdown mode

    # check for banned hashed IP's
  ip = flask.request.remote_addr
  ipHash = hashlib.md5(ip.encode('utf-8')).hexdigest()
  if checkIP(ipHash): return flask.render_template("msg.html", message="This IP has been banned from using RDSL uptimer", removeInput=True)
  
  return flask.render_template('/mobile/login.html',
        user_id=flask.request.headers['X-Replit-User-Id'],
        user_name=flask.request.headers['X-Replit-User-Name']
    ), 200 #renders template


@app.route('/m/stats') # mobile stat page
def stats_mobile():
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302 #lockdown mode

      # check for banned hashed IP's
  ip = flask.request.remote_addr
  ipHash = hashlib.md5(ip.encode('utf-8')).hexdigest()
  if checkIP(ipHash): return flask.render_template("msg.html", message="This IP has been banned from using RDSL uptimer", removeInput=True)
    
  with open("./data/pings.txt", "r") as v: #obtain data
    content = v.read()
  replcount = str(asyncio.run(dab.view('pings'))).split('\n')
  replcount = str(len(replcount)) #repl count
  pingcount, online, offline, allpings, timebetween = content.split('\n') # data from ping file
  try:
    onlinepercent = round(int(online) / int(pingcount) * 100) #get all repls onlie in percentages
    onlinepercent = str(onlinepercent).replace('.0', '%')
  except: onlinepercent = 'ERROR WITH CALCULATION! TRY AGAIN LATER. (MY CAPS IS STUCK HELP)' #some weird error that sometimes happens
    
  return flask.render_template('mobile/stats.html', count=replcount, online=str(onlinepercent), pings=allpings, timebetween=timebetween), 200 #renders template


# ============================ Mobile pages ============================

@app.route("/admin") #admin dashboard. Supposed to see all added repls and then remove them via dashboard if its spam
def admin():
  if ultraLockdown: return "The server is currently in (Ultra) lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302 #lockdown mode
  if flask.request.headers.get('X-Replit-User-Name') in admins:
    repls = asyncio.run(dab.view('pings')).split('\n')
    with open("./data/404s.txt", "r") as f:
      fourOfours = f.read()
    return flask.render_template("admin.html",
                           user_id=flask.request.headers['X-Replit-User-Id'],
                           user_name=flask.request.headers['X-Replit-User-Name'],
                           repls=repls,
                           APIKEY=os.environ["ALLREPLSAPIKEY"],
                                MSG = flask.request.args.get('msg'),
                                lenrepls=len(repls),
                                fourofours = fourOfours.split("\n"))
  else:
    return "You are not an admin!"


    

  
@app.route("/factory")
def factory(): #smoll advertisement place: )
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302
  return flask.render_template('factory.html'), 200


@app.route('/logout') #remove all REPL_AUTH cookies for the domains up.rdsl.ga and defauly repl slug domain
def logout():
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302
  resp = make_response(flask.render_template('removing-cook.html'))
  resp.delete_cookie("REPL_AUTH", path='/', domain="up.rdsl.ga") #remove all repl auth cookies from all possible domains
  resp.delete_cookie("REPL_AUTH", path='/', domain="up.raadsel.repl.co") #default repl domain
  resp.delete_cookie("REPL_AUTH", path='/', domain="1fcd37d8-24c8-455d-a7eb-abbbc3a0b45a.id.repl.co") #repl id domain
  return resp

@app.route("/others")
def others(): #shows other, community made pingers
  return flask.render_template('/info/others.html'), 200 # imune to lockdown. 

@app.route("/other")
def other(): #shows other, community made pingers diff url
  return flask.render_template('/info/others.html'), 200 # imune to lockdown. 


@app.route("/FAQ") # FAQ page
def faqhtml():
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302 #lockdown
  return flask.render_template('/info/FAQ.html'), 200

@app.route("/TOS")
def toshtml(): #TOS page with CSS. 
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries! To view the clean TOS go to https://up.rdsl.ga/static/tos.txt", 302
  return flask.render_template('/info/TOS.html'), 200
  

@app.route("/ping") #always available ping page
@limiter.exempt
def ping():
  if ultraLockdown: return "Ultra Lockdown"
  if Lockdown: return "Lockdown"
  return "200", 200 #backup pinger - - Lockdown mode imune

@app.route("/coolpeeps") #shows all users using this service
def allusingpeeps():
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302
      # check for banned hashed IP's
  ip = flask.request.remote_addr
  ipHash = hashlib.md5(ip.encode('utf-8')).hexdigest()
  if checkIP(ipHash): return flask.render_template("msg.html", message="This IP has been banned from using RDSL uptimer", removeInput=True)
    
  pongs = str(asyncio.run(dab.view('pings'))).split('\n')
  coolpeeps = "Cool peeps who use this pinger: Raadsel"
  coolpeepsarr = ["Raadsel"] #already added me:)
  for i in pongs:
    try:
      o, name, repl, co = i.split(".")
      if not name in coolpeepsarr:
        coolpeepsarr.append(name)
        coolpeeps += f", {name}"
      else: 

        continue
    except:

      continue
  return flask.render_template('coolpeeps.html', peeps=coolpeeps)


async def CheckIfRepl(url, username=None, s=None): #check if the domain is a repl. If not it returns false <-- It should return it. (pls work)
  print("checking replit")
  url = urllib.parse.urlparse(url)
  host = url.netloc
  url = f'https://{host}/__repl' #url goes to spotlight page
  own_session = False
  if not s:
    timeout = aiohttp.ClientTimeout(total=15)
    s = aiohttp.ClientSession(timeout=timeout)
    own_session = True

  try:
    r = await s.get(url)
    
    if own_session: await s.close()
    if str(r.status)[0] == '4' and not str(r.url).startswith('https://replit.com/'): #checks if it refers to replit.com
      print(r.status, str(r.url))
      return False
    else:
      return True
    print(url, r.url, r.status)

  except Exception as e:
    print(type(e), e, '----- WARNING ') #errors
    if own_session: await s.close()
    return True #somehow returns true if it fails. Benifit of the doubt


  
async def CheckOwner(url, username, s=None): #check if the user who submitted the repl is actually the owner
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
    if str(r.status)[0] == '4' and not str(r.url).startswith('https://replit.com/'): #checks if its a repl
      print(r.status, str(r.url))
      return False
    print(url, r.url, r.status)
    inputuser1 = str(r.url)
    inputuser1 = inputuser1.replace("https://replit.com/@", "")
    inputuser, slug = inputuser1.split("/")
    print(inputuser) #username
    
    with open("data/projects.txt", "a") as f:
      f.write(f"{r.url}\n")
    if username == inputuser:
      print("Check If URL is a Repl: ", username, "is the owner")
      return True #good
    if username in admins:
      print("Check If URL is a Repl: ", username, "is an admin, so bypasses the owner req")
      return True #good
    else:
      print("Check If URL is a Repl: ", username, "is not the owner")
      return False #bad
  except Exception as e:
    print(type(e), e, '----- WARNING ')
    if own_session: await s.close()
    return True
    
if os.environ["REPL_ID"] != "1fcd37d8-24c8-455d-a7eb-abbbc3a0b45a": Lockdown = True #bad
# IF, you fork this. Please just give GOOD credits
  
def CheckReplCount(inname): #check names is To see if a user has exceeded the 25 repls limit - Edit: 40 is the limit
  pongs = str(asyncio.run(dab.view('pings'))).split('\n') #get all repls
  pingercount = 0
  names = []
  for i in pongs:
    try:
      o, name, repl, co = i.split(".") #get the name if its a default repl domain
      if name in admins: # I am built different
        return 0
      if not o in names:
        names.append(o)
        if repl.lower() == inname.lower():
          pingercount += 1 #add 1 to the total count
      else:
        continue
    except:
      continue
  print(pingercount)
  return pingercount #returns the number if pinged repls of that user

def add(repl):
  try:
    print("Adding: "+repl)
    asyncio.run(dab.set(pings=str(asyncio.run(dab.view('pings'))) + '\n' + repl))
    print("Added "+repl)
  except:
    print("ERROR WITH ADDING "+repl)

def remove(repl, ip=None, gui=False):
  try:
    print("Removing: "+repl)
    rawpings = str(asyncio.run(dab.view('pings')))
    asyncio.run(dab.set(pings=rawpings.replace("\n"+repl, "")))
    if ip is not None:
      if gui:
        with open("data/removes.txt", "a") as f:
          f.write(ip + ":" + repl + " --GUI\n")
          f.close()
      else:
        with open("data/removes.txt", "a") as f:
          f.write(ip + ":" + repl + " --CLI\n")
          f.close()
          
    print("Removed "+repl)
  except:
    print("ERROR WITH REMOVING "+repl)

def checkIP(IP):
  if IP in bannedIPs: return True
  else: return False

@app.route('/stats') #stat page
def stats():
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302 #lockdown

    # check for banned hashed IP's
  ip = flask.request.remote_addr
  ipHash = hashlib.md5(ip.encode('utf-8')).hexdigest()
  if checkIP(ipHash): return flask.render_template("msg.html", message="This IP has been banned from using RDSL uptimer", removeInput=True)
    
  with open("./data/pings.txt", "r") as v: #opens file to obtaind ata
    content = v.read()
  replcount = str(asyncio.run(dab.view('pings'))).split('\n') #get all repls in db
  replcount = str(len(replcount)) #get number of relps
  pingcount, online, offline, allpings, timebetween = content.split('\n') #import all stat data
  try:
    Ronlinepercent = round(int(online) / int(pingcount) * 100)
    onlinepercent = str(Ronlinepercent).replace('.0', '%')
  except: onlinepercent = 'ERROR WITH CALCULATION! TRY AGAIN LATER. (MY CAPS IS STUCK HELP)' #weird error that sometimes appears
    
  return flask.render_template('stats.html', count=replcount, online=str(onlinepercent), pings=allpings, rawpercent = Ronlinepercent, timebetween=timebetween), 200 #renders template

  
@app.route('/add', methods=['POST']) #add repls by POST request
@limiter.limit("1/6 seconds", override_defaults=False) #ratelimit
def send():
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries!", 302 #lockdown mode. No repls can be added
  # check for banned hashed IP's
  ip = flask.request.remote_addr
  ipHash = hashlib.md5(ip.encode('utf-8')).hexdigest()
  if checkIP(ipHash): return flask.render_template("msg.html", message="This IP has been banned from using RDSL uptimer", removeInput=True)

    
  newPing = flask.request.form['add']
  pings = str(asyncio.run(dab.view('pings'))).split('\n')


  if 'X-Replit-User-Name' in flask.request.headers:
   username = flask.request.headers['X-Replit-User-Name'] #Check name
  if username in bannednames: return "You have been banned from using this service, please contact the admin", 403
  is_replit = asyncio.run(CheckIfRepl(newPing, username))
  if not is_replit: #check if site is from repl
    return flask.render_template('msg.html', message="This is not a replit server, or this isnt a Repl from you!! RDSL Uptimer only supports Replit projects, that were added by there owners!") #not replit
  is_owner = asyncio.run(CheckOwner(newPing, username))
  if not is_owner: #check if user is the owner
    print("NOT OWNER, -- not adding")
    return flask.render_template('msg.html', message="This isnt a Repl from you!! RDSL Uptimer only pings Repls with permission from their owners! If this is a team repl. Im sorry for the difficulties, you can bypass this by ading it via the CLI/API!") #not replit owner
  newPing = newPing.lower()
  remPing = newPing.replace("rem ", "", 1)
  if remPing in pings and newPing.startswith("rem "): #check if user wants to remove it
    # Get hashed IP:
    ip = flask.request.remote_addr
    ipHash = hashlib.md5(ip.encode('utf-8')).hexdigest() #unrecoverable hash
    
    remove(remPing, ipHash, gui=True)
    
    return flask.render_template('msg.html', message="Removed "+remPing)

  if newPing not in pings: # no saturn bots
    if "saturn" in newPing: return flask.render_template('msg.html', message="This is a Saturn discord bot, RDSL pinger doesnt support saturn bots!")
      
    if "discord-status-bot" in newPing: #check discord status bot status mode 1
      url = urllib.parse.urlparse(newPing)
      host = url.netloc
      f = requests.get("https://"+host+"/statusmode")
      if f.status_code != 200:
        print("Discord status bot doesnt have statusmode 1")
        return flask.render_template('msg.html', message="This is a a Discord Status bot repl that doesnt have status mode 1. Please enable it on line 4!\nIf you did enable statusmode 1 and it still gives this message, please update to the latest version! (fork it here --> https://replit.com/@Raadsel/Discord-Status-bot?v=1)"), 403
      
    if newPing.startswith("http"): #has to be http thing
    # ping the newping
      try:
        reqq = requests.get(newPing)
        if not reqq.status_code in [200, 304, 100, 201, 202, 206, 302]: #check if site is online
          return flask.render_template('msg.html', message="Invalid URL! Please make sure you configured the webserver right!") #if pinging failed
        if CheckReplCount(newPing) >= MAXREPLS:
          return flask.render_template('msg.html', message="You are already at 40 repls! Thats the max we ping. Also you can't have more then 40 Repls online at the same time on your Replit account, so its useless anyway. You can remove repls by inputting `rem + replurl` to the urlpinger input.")
        
        add(newPing) # ADD REPL
        
        return flask.render_template('msg.html', message="URL successfully Added! consider tipping me at the bottom-right of the site, since you get one dollar for free!"), 200 #added & self promo
      except:
        return flask.render_template('msg.html', message="Invalid URL! Please make sure you configured the webserver right!")
    else:
      return flask.render_template('msg.html', message="Invalid URL! Please put in a valid URL including protocols like https://") # I know that a URL should always start with protocols like https://, but some peeps dont
  else:
    return flask.render_template('msg.html', message="I am already pinging that URL!"), 226 # If the url is already in the database



 # API

@app.route("/api")
def APIdocs():
  return flask.render_template("info/api.html")

@app.route('/api/cli', methods=['POST']) #yes ik this is not protected by repl auth + API post request
@limiter.limit("1/6 seconds", override_defaults=False) #ratelimit
def sendcli():
  if Lockdown:
    return "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries! Lockdown mode also means the entire API goes offline!", 302
  # check for banned hashed IP's
  ip = flask.request.remote_addr
  ipHash = hashlib.md5(ip.encode('utf-8')).hexdigest()
  if checkIP(ipHash): return "403, this IP has been banned from using RDSL uptimer"
    
  newPing = flask.request.form['add']
  pings = str(asyncio.run(dab.view('pings'))).split('\n')

  is_replit = asyncio.run(CheckIfRepl(newPing))
  if not is_replit:
    return "This is not a replit server! RDSL Uptimer only supports Replit projects!", 400
  newPing = newPing.lower()
  remPing = newPing.replace("rem ", "", 1)
  
  
  if remPing in pings and newPing.startswith("rem "):
    # get hashed IP
    ip = flask.request.remote_addr
    ipHash = hashlib.md5(ip.encode('utf-8')).hexdigest()
    if checkIP(ipHash):
      return "Your IP has been banned from using RDSL uptimer"
    remove(remPing, ipHash)

    return "200 - Succesfully Removed "+remPing, 200
  try:
    o, name, repl, co = newPing.split(".")
    if name in bannednames: return "You have been banned from using up.rdsl.ga!"
  except: 
    print("no repl domain")
    
  if newPing not in pings:
    if newPing.startswith("http"):
      try:
        req = requests.get(newPing)
        if req.status_code != 200:
          return flask.jsonify({"msg": f"The URL '{newPing}' does not respond to our pings. Please check your webserver and if you entered the right URL and try again!"}), 302
        if CheckReplCount(newPing) >= MAXREPLS:
          return "403 - You are already at 40 uptimed repls! Thats the max we ping. Also you can't have more then 40 Repls online at the same time on your Replit account, so its useless anyway. You can remove repls by inputting `rem + replurl` to the urlpinger input."


        if checkIP(ipHash):
          return "Your IP has been banned from using RDSL uptimer"
        
        add(newPing)
        
        requests.get(newPing)
          # Get hashed IP:
        ip = flask.request.remote_addr
          # HASH IP:
        ipHash = hashlib.md5(ip.encode('utf-8')).hexdigest()
        with open("data/cliadds.txt", "a") as f:
          f.write(ipHash + ":" + remPing + "\n")
        print(f"Added {newPing} to the database via CLI"), 200
        
        return "200 - URL successfully Added! consider tipping me at https://zink.tips/raadsel, since you get one dollar free credits to up!", 200
      except:
        return "Invalid URL! Please make sure you configured the webserver right!", 400
    else:
      return "Invalid URL! Please put in a valid URL including protocols like https://!" # I know that a URL should always start with protocols like https://, but some peeps dont
  else:
    return "226 - I am already pinging that URL!", 226


@app.route('/api/cli/json', methods=['POST']) #yes ik this is not protected by repl auth + API post request
@limiter.limit("1/10 seconds", override_defaults=False) #ratelimit
def sendcliJSON():
  if Lockdown:
    lockdownmsg = {"msg": "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries! Lockdown mode also means the entire API goes offline!"}
    return flask.jsonify(lockdownmsg), 302
    
  # check for banned hashed IP's
  ip = flask.request.remote_addr
  ipHash = hashlib.md5(ip.encode('utf-8')).hexdigest()
  if checkIP(ipHash): return flask.jsonify({"msg": "this IP has been banned from using RDSL uptimer", "succes": False}), 403
    
  newPing = flask.request.form['add']
  pings = str(asyncio.run(dab.view('pings'))).split('\n')
  rawpings = str(asyncio.run(dab.view('pings')))

  # remove ping
  is_replit = asyncio.run(CheckIfRepl(newPing))
  if not is_replit:
    msg = { "msg": "This is not a replit server! RDSL Uptimer only supports Replit projects!"}
    return flask.jsonify(msg), 400
  newPing = newPing.lower()
  remPing = newPing.replace("rem ", "", 1)
  if remPing in pings and newPing.startswith("rem "):
    # Get hashed IP:
    ip = flask.request.remote_addr
    # HASH IP:
    ipHash = hashlib.md5(ip.encode('utf-8')).hexdigest()

    remove(remPing, ipHash)
    print("removed "+remPing)
    
    msg = { "msg": "Succesfully Removed "+remPing}
    return flask.jsonify(msg), 200

  try:
    o, name, repl, co = newPing.split(".")
    if name in bannednames: return flask.jsonify({"msg": "You have been banned from using up.rdsl.ga!", "succes": False}), 403
  except: 
    print("no repl domain")
    
  if newPing not in pings:
    if newPing.startswith("http"):
      try:
        
        req = requests.get(newPing)
        if req.status_code != 200:
          return flask.jsonify({"msg": f"The URL '{newPing}' does not respond to our pings. Please check your webserver and if you entered the right URL and try again!"}), 302
        if CheckReplCount(newPing) >= MAXREPLS:
          return flask.jsonify({"msg": "You are already at 40 repls! Thats the max we ping. Also you can't have more then 40 Repls online at the same time on your Replit account, so its useless anyway. You can remove repls by inputting `rem + replurl` to the urlpinger input.", "succes": False}), 400
        asyncio.run(dab.set(pings=str(asyncio.run(dab.view('pings'))) + '\n' + newPing))
          # Get hashed IP:
        ip = flask.request.remote_addr
          # HASH IP:
        ipHash = hashlib.md5(ip.encode('utf-8')).hexdigest()
        with open("data/cliadds.txt", "a") as f:
          f.write(ipHash + ":" + remPing + "\n")
          
        print(f"Added {newPing} to the database via CLI")
        msg = { "msg": "URL successfully Added! consider tipping me at https://zink.tips/raadsel, since you get one dollar free credits to up!", "succes": True}
        return flask.jsonify(msg), 200
      except:
        msg = { "msg": "Invalid URL! Please make sure you configured the webserver right!", "succes": False }
        return flask.jsonify(msg), 400
   
    else:
      msg = { "msg": "Invalid URL! Please put in a valid URL including protocols like https://!", "succes": False }
      return flask.jsonify(msg), 400 # I know that a URL should always start with protocols like https://, but some peeps dont

  else:
    msg = { "msg": "226 - I am already pinging that URL!", "succes": False }
    return flask.jsonify(msg), 226
    

@app.route('/api/stats', methods=['GET']) 
@limiter.limit("1/30 seconds", override_defaults=False) #ratelimit
def statsAPI():
  if Lockdown:
    data = {"msg": "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries! Lockdown mode also means the entire API goes offline!"}
    return flask.jsonify(data), 302
  # check for banned hashed IP's
  ip = flask.request.remote_addr
  ipHash = hashlib.md5(ip.encode('utf-8')).hexdigest()
  if checkIP(ipHash): return flask.jsonify({"msg": "This IP has been banned from using RDSL uptimer", "succes": False}), 403
  with open("./data/pings.txt", "r") as v: #opens file to obtaind ata
    content = v.read()
  replcount = str(asyncio.run(dab.view('pings'))).split('\n')
  replcount = str(len(replcount))
  pingcount, online, offline, allpings, timebetween = content.split('\n')

  try:
    onlinepercent = round(int(online) / int(pingcount) * 100)
    onlinepercent = str(onlinepercent).replace('.0', '%')
  except: onlinepercent = 'ERROR WITH CALCULATION! TRY AGAIN LATER. (MY CAPS IS STUCK HELP)' #weird error that sometimes appears
  try:

    data = {"error": False,
          "Pinged_Repls_Count": int(replcount),  
          "Online_Repls_Percent": int(onlinepercent),
          "Offline_Repls_Count": int(offline),
          "Online_Repls_Count": int(online),
          "All_Repls_Count": int(pingcount),
          "All_Pings_Sent": int(allpings),
          "Time_Between_Pings": int(timebetween),
          "Owner": {
            "Name": "Raadsel",
            "Replit": "https://replit.com/@Raadsel",
            "Github": "https://github.com/Raadsl"
          },
          "Admins": admins,
          "Maxreplsallowed": MAXREPLS
          
          }
    
  
    return flask.jsonify(data), 200
  except:
    data = {"error": True}
    return flask.jsonify(data), 400
                               

@app.route('/api/ModInfo', methods=['GET'])  # Get some mod info, used for backup pinger
@limiter.limit("1/30 seconds", override_defaults=False) #ratelimit
def ModeratorInfoAPI():
  if Lockdown:
    data = {"msg": "The server is currently in lockdown mode. Please try again later. Your Repls are still being pinged, no worries! Lockdown mode also means the entire API goes offline!"}
    return flask.jsonify(data), 302
  # check for banned hashed IP's
  ip = flask.request.remote_addr
  ipHash = hashlib.md5(ip.encode('utf-8')).hexdigest()
  if checkIP(ipHash): return flask.jsonify({"msg": "This IP has been banned from using RDSL uptimer", "succes": False}), 403
  data = {
    "data": {
    "Admins": admins,
    "BannedUsers": bannednames,
    "BannedHashedIps": bannedIPs,
    "Lockdown": Lockdown, #woah, if this is true you cant see this lolololol
    "UltraLockdown": ultraLockdown,
    "MaxReplsAllowed": MAXREPLS
  },
  "succes": True
  }
  return flask.jsonify(data), 200


    
@app.route("/api/private/allrepls", methods=['GET'])
def allreplsAPI(): #for backup pinger
  key = flask.request.args.get('key')
  if key != os.environ["ALLREPLSAPIKEY"]:
    return flask.jsonify({"Error": "Invalid API key", "succes": False}), 403
  repls = str(asyncio.run(dab.view('pings'))).split('\n')
  return flask.jsonify({"Error": None, "All_Repls": repls, "succes": True})


  
    
@app.route("/api/private/ezremove", methods=['GET'])
def removeAPI(): #for backup pinger
  key = flask.request.args.get('key')
  repl = flask.request.args.get('repl')
  if key != os.environ["ALLREPLSAPIKEY"]:
    return flask.jsonify({"Error": "Invalid API key", "succes": False}), 403
  else:
    remove(repl)
    return flask.redirect("https://up.rdsl.ga/admin?msg=succes"),200
   # else:
    #  return flask.redirect("/admin?msg=failed%20See%20Logs"),400

@app.route("/api/private/ezadd", methods=['GET'])
def addAPI(): #for backup pinger
  key = flask.request.args.get('key')
  repl = flask.request.args.get('repl')
  if key != os.environ["ALLREPLSAPIKEY"]:
    return flask.jsonify({"Error": "Invalid API key", "succes": False}), 403
  else:
    add(repl)
    return flask.redirect("https://up.rdsl.ga/admin?msg=succes"),200
    

#ERROR HANDLING
@app.errorhandler(404)
def page_not_found(e): #404 error
    return flask.render_template('/errors.html', error=404, msg="It looks like you got a 404 error! The page you are looking for is not here D:"), 404

@app.errorhandler(500)
def internal_error(e): #500 error
    return flask.render_template('/errors.html', error=500, msg="The server failed to complete the request because server encountered an error"), 500

@app.errorhandler(429) #ratelimit error
def ratelimit_handler(e):
    return flask.make_response(
            jsonify(error=f"ratelimit exceeded {e.description}")
            , 429
    )



import random
def run():
  port = random.randint(1000, 9999) 
  print(f"[Waitress] Server started on port {port}") #cool log thing
  from waitress import serve
  serve(app, host='0.0.0.0', port=port) #runs repl on random port
  
def actualrun():  
    t = Thread(target=run)
    t.start() #called by main.py



"""
 * @INFO
 * RDSL Pinger Coded by Raadsel#9398 | https://replit.com/@Raadsel
 * @INFO
 * Please mention me, when using this Code!
 * @INFO
 """
