import requests, replitdb, asyncio, flask
from threading import Thread
dab = replitdb.AsyncClient()
app = flask.Flask(__name__)

@app.route('/')
def index():

  return flask.render_template('index.html')
  
async def remove(url):
  pings = str(dab.view('pings')).split('\n')
  dab.set(pings=str(dab.view('pings')).replace(url+"\n", ""))
  

@app.route('/stats')
def stats():
  with open("pings.txt", "r") as v:
    content = v.read()
  replcount = str(asyncio.run(dab.view('pings'))).split('\n')
  replcount = str(len(replcount))
  pingcount, online, offline = content.split('\n')
  try:
    onlinepercent = int(online) / int(pingcount) * 100
    onlinepercent = str(onlinepercent).replace('.0', '%')
  except: onlinepercent = 'ERROR WITH CALCULATION! TRY AGAIN LATER. (MY CAPS IS STUCK HELP)'
    
  return flask.render_template('stats.html', count=replcount, online=str(onlinepercent), pings="soon")

  
@app.route('/add', methods=['POST'])
def send():
  newPing = flask.request.form['add']
  pings = str(asyncio.run(dab.view('pings'))).split('\n')
  print(str(asyncio.run(dab.view('pings'))))
  print(pings)
  # remove ping
  newPing = newPing.lower()
  remPing = newPing.replace("rem ", "", 1)
  if remPing in pings and newPing.startswith("rem "):
    newPings = str(asyncio.run(dab.view('pings')).replace(remPing+"\n", ""))
    print(newPings)
    #asyncio.run(dab.set())

    asyncio.run(dab.set(pings=pings.remove(remPing)))
    print("removed "+remPing)
    print(pings)
    return flask.render_template('msg.html', message="Removed "+remPing)




    
  if not newPing.endswith("repl.co"):
    return flask.render_template('msg.html', message="Invalid URL! Urls should end with `repl.co`")
    
  if newPing not in pings:
    if newPing.startswith("http"):
      try:
        requests.get(newPing)
        asyncio.run(dab.set(pings=str(asyncio.run(dab.view('pings'))) + '\n' + newPing))
        return flask.render_template('msg.html', message="URL successfully Added! consider tipping me at the bottom-right of the site, since you get one dollar for free!")
      except:
        return flask.render_template('msg.html', message="Invalid URL! Please make sure you configured the webserver right!")
    else:
      return flask.render_template('msg.html', message="Invalid URL! Please put in a valid URL including protocols like https://!") # I know that a URL should always start with protocols like https://, but some peeps dont
  else:
    return flask.render_template('msg.html', message="I am already pinging that URL!")



import random
def run():
  app.run(host='0.0.0.0', port=random.randint(1000, 9999))
  
def actualrun():  
    t = Thread(target=run)
    t.start()