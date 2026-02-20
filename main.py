import discord, random, json, os
from discord.ext import commands
from discord import app_commands

BOT = commands.Bot(command_prefix="!", intents=discord.Intents.default())
BOT.intents.message_content = True

TOKEN = ""
OWNER = 

files = {}
files["b"] = "beauty_scores.json"
files["s1"] = "surgery_used.json"
files["s2"] = "surgery2_used.json"
files["a"] = "ascended.json"
files["m"] = "money.json"

def loadf(f):
    if os.path.exists(f):
        return json.load(open(f))
    return {}

def savef(f,d):
    with open(f,"w") as x:
        json.dump(d,x)

beauty = loadf(files["b"])
s1 = loadf(files["s1"])
s2 = loadf(files["s2"])
asc = loadf(files["a"])
money = loadf(files["m"])

def gmon(uid):
    return money.get(uid,0)

def bmsg(v):
    if v<=10: return "give up"
    if v<=30: return "better luck next time"
    if v<=60: return "average"
    if v<=90: return "nice"
    if v<=100: return "the chosen one"
    if v<=120: return "him."
    if v<=150: return "divine genetics"
    if v<=180: return "luck's on your side"
    if v==200: return "???"
    return "beyond comprehension"

@BOT.event
async def on_ready():
    print("logged in as",BOT.user)
    await BOT.tree.sync()

@BOT.tree.error
async def err(inter,err):
    if isinstance(err, app_commands.CommandOnCooldown):
        await inter.response.send_message("try later in "+str(int(err.retry_after))+"s",ephemeral=True)
    else:
        raise err

@BOT.tree.command(name="beauty")
async def b(inter):
    uid = str(inter.user.id)
    beauty.setdefault(uid,random.randint(0,100))
    money.setdefault(uid,0)
    savef(files["b"],beauty)
    savef(files["m"],money)
    await inter.response.send_message(f"{inter.user.display_name}\nBeauty: {beauty[uid]}\nRating: {bmsg(beauty[uid])}\nMoney: ${gmon(uid)}")

@BOT.tree.command(name="bonesmash")
@app_commands.checks.cooldown(1,10)
async def bones(inter):
    uid=str(inter.user.id)
    beauty.setdefault(uid,random.randint(0,100))
    if random.random()<0.1:
        beauty[uid]-=10
        t="Bone broken -10"
    else:
        x=random.randint(2,4)
        beauty[uid]+=x
        t="Bone smash +" + str(x)
    cap = 200 if asc.get(uid) else 100
    beauty[uid]=max(0,min(cap,beauty[uid]))
    savef(files["b"],beauty)
    await inter.response.send_message(t)

@BOT.tree.command(name="buy")
@app_commands.describe(item="makeup or bonefix")
async def buy(inter,item:str):
    uid=str(inter.user.id)
    money.setdefault(uid,0)
    beauty.setdefault(uid,random.randint(0,100))
    it=item.lower()
    if it=="makeup": c,g=250,12
    elif it=="bonefix": c,g=1000,22
    else: await inter.response.send_message("invalid",ephemeral=True); return
    if money[uid]<c:
        await inter.response.send_message("not enough money",ephemeral=True)
        return
    cap=200 if asc.get(uid) else 100
    beauty[uid]=min(cap,beauty[uid]+g)
    money[uid]-=c
    savef(files["b"],beauty)
    savef(files["m"],money)
    await inter.response.send_message("Bought "+it+" for $"+str(c)+" Beauty +"+str(g))

@BOT.tree.command(name="daily")
@app_commands.checks.cooldown(1,86400)
async def daily(inter):
    uid=str(inter.user.id)
    money[uid]=gmon(uid)+50
    savef(files["m"],money)
    await inter.response.send_message("daily +50")

@BOT.tree.command(name="work")
@app_commands.checks.cooldown(1,900)
async def work(inter):
    uid=str(inter.user.id)
    money[uid]=gmon(uid)+10
    savef(files["m"],money)
    await inter.response.send_message("worked +10")

@BOT.tree.command(name="setbeauty")
async def setb(inter,uid:str,val:int):
    if inter.user.id!=OWNER:
        await inter.response.send_message("owner only",ephemeral=True)
        return
    beauty[uid]=max(0,min(val,300))
    savef(files["b"],beauty)
    await inter.response.send_message("set "+uid+" to "+str(val))

@BOT.tree.command(name="leaderboard")
async def lb(inter):
    s=sorted(beauty.items(),key=lambda x:x[1],reverse=True)
    msg=""
    c=0
    for uid,v in s:
        if c>=5: break
        try:
            u=await BOT.fetch_user(int(uid))
            if u.bot: continue
            c+=1
            msg+=str(c)+". "+u.display_name+" - "+str(v)+"\n"
        except: continue
    await inter.response.send_message(msg if c else "no users")

@BOT.tree.command(name="pfp")
async def p(inter,uid:str):
    try:
        u=await BOT.fetch_user(int(uid))
        em=discord.Embed(title=u.name+" profile")
        em.set_image(url=u.display_avatar.url)
        await inter.response.send_message(embed=em)
    except:
        await inter.response.send_message("invalid user",ephemeral=True)

@BOT.tree.command(name="mog")
@app_commands.checks.cooldown(1,30)
async def mog(inter,target:discord.User):
    a=str(inter.user.id)
    t=str(target.id)
    beauty.setdefault(a,random.randint(0,100))
    beauty.setdefault(t,random.randint(0,100))
    ab=beauty[a]; tb=beauty[t]
    win=0.5
    if ab>tb: win=0.75
    elif ab<tb: win=0.25
    capa=300 if asc.get(a) else 100
    capt=300 if asc.get(t) else 100
    if random.random()<win:
        st=min(5,tb)
        beauty[t]-=st
        beauty[a]=min(capa,ab+st)
        r="mogged "+target.display_name+" stole "+str(st)
    else:
        st=min(5,ab)
        beauty[a]-=st
        beauty[t]=min(capt,tb+st)
        r="got mogged by "+target.display_name+" lost "+str(st)
    savef(files["b"],beauty)
    await inter.response.send_message(r)

BOT.run(TOKEN)
