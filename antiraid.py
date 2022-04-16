from discord.ext import commands
from dislash import InteractionClient, Option, OptionType, ActionRow, Button, ButtonStyle
import discord,requests,threading,json,random,asyncio,os,dislash
from colorama import Fore
from datetime import datetime

with open("config.json","r") as f:
    config = json.load(f)
__token__ =config["Account"]["Token"]
__prefix__ =config["Account"]["Prefix"]
themes = {
    "yellow": "[33m",
    "green":"[32m",
    "blue":"[34m",
    "cyan":"[36m",
    "magenta":"[35m"
}
__theme__ = themes[config.get('Theme')]
if config["Mode"] == "Ban" or config["Mode"] == "ban":
    __mode__="ban"
else:
    __mode__="kick"

bot = commands.Bot(command_prefix=__prefix__,intents=discord.Intents().all())
#slash = InteractionClient(bot)

if os.name == "nt":
    os.system("cls")
    os.system("mode 100,40")
else:
    os.system("clear")

def banner():
    banner= f"""
                         █████╗ ███╗   ██╗████████╗██╗██████╗  █████╗ ██╗██████╗ 
                        ██╔══██╗████╗  ██║╚══██╔══╝██║██╔══██╗██╔══██╗██║██╔══██╗
                        ███████║██╔██╗ ██║   ██║   ██║██████╔╝███████║██║██║  ██║
                        ██╔══██║██║╚██╗██║   ██║   ██║██╔══██╗██╔══██║██║██║  ██║
                        ██║  ██║██║ ╚████║   ██║   ██║██║  ██║██║  ██║██║██████╔╝
                        ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═════╝ {Fore.WHITE}"""
    banner=banner.replace("█", Fore.WHITE+"█").replace("╝", f"{__theme__}╝").replace("╚", f"{__theme__}╚").replace("╔", f"{__theme__}╔").replace("╗", f"{__theme__}╗").replace("║", f"{__theme__}║").replace("═", f"{__theme__}═")
    return banner

#guild_ids=gids,

@bot.event
async def on_command(ctx):
    print(f"{__theme__}[{Fore.WHITE}{datetime.now().strftime('%H:%M:%S')}{__theme__}]{Fore.WHITE} Used Command: {ctx.message.content}{Fore.WHITE}")
    await ctx.message.delete()

@bot.event
async def on_connect():
    await bot.change_presence(activity=discord.Game(name=".help - #AntiRaid"))
    
    print(banner())
    text=f"\nGuilds:"
    if bool(bot.guilds) == True:
        for guild in bot.guilds:
            text=text+f"\n  {__theme__}{guild.name}{Fore.WHITE}"
    else:
        text=""
    print(f"""
Bot Info:
  {__theme__}Name:{Fore.WHITE} {bot.user.name}#{bot.user.discriminator}
  {__theme__}ID:{Fore.WHITE} {bot.user.id}{text}
____________________________________________________________________________________________________""")
def banuser(gid,id,nam):
    if __mode__ == "kick":
        r=requests.delete(f"https://discord.com/api/v{random.randint(6, 9)}/guilds/{gid}/members/{id}",headers={"Authorization": f"Bot {__token__}","x-audit-log-reason": "Alt"})
    else:
        r=requests.put(f"https://discord.com/api/v{random.randint(6, 9)}/guilds/{gid}/bans/{id}",headers={"Authorization":f"Bot {__token__}","x-audit-log-reason": "Alt"},json={"delete_message_days": "1"})
    if r.status_code == 204:
        #print(f"[KICK] {nam}")

        if __mode__ == "kick":
            print(f"{__theme__}[{Fore.WHITE}{datetime.now().strftime('%H:%M:%S')}{__theme__}]{Fore.WHITE} Kicked member: {__theme__}{nam} ({id}){Fore.WHITE}")
        else:
            print(f"{__theme__}[{Fore.WHITE}{datetime.now().strftime('%H:%M:%S')}{__theme__}]{Fore.WHITE} Banned member: {__theme__}{nam} ({id}){Fore.WHITE}")

@bot.command(description="Sends Blacklist of blacklisted names")
async def blacklist(ctx):
    las=""
    with open("blacklist.json", "r",encoding="utf8") as black:
        blacklist1 = json.load(black)
    for x in blacklist1["blacklist"]:
        las=las+x+"\n"
    em=discord.Embed(title="Blacklisted Names:",description=las,color=0xFF0000)
    await ctx.reply(embed=em)

@bot.command(options=[Option('name', 'Name of blacklisted name', OptionType.STRING)],description="Add blacklisted name to name list")
@dislash.has_permissions(administrator=True)
async def addblacklistedname(ctx,name):
    with open('blacklist.json', 'r',encoding='utf8') as f:
        chid = json.load(f) 

        cs=chid["blacklist"]
        cs.append(f"{name}")

        chid["blacklist"] = cs
        with open('blacklist.json', 'w',encoding='utf8') as f:
            json.dump(chid, f, indent=4)

    em=discord.Embed(title="Blacklist",description=f"Added {name} to blacklist",color=0xFF0000)
    await ctx.reply(embed=em)

@bot.event
async def on_member_join(member):
    with open("blacklist.json", "r",encoding="utf8") as black2:
        blacklist2 = json.load(black2)
    with open("logs.json", "r",encoding="utf8") as ga:
        lgs = json.load(ga)
    logs=bot.get_channel(int(lgs[str(member.guild.id)]))
    for mem in member.guild.members:
        for eeeee in blacklist2["blacklist"]:
            if mem.name.endswith(" | "+eeeee) or mem.name.startswith(eeeee+" | "):
                #await member.kick(reason="Raid?!")
                em=discord.Embed(title=f"{mem.name} has been kicked!",description=f"Member: {mem.name}#{mem.discriminator} [{mem.id}]\n> Reason: Blacklisted name.")
                await logs.send(embed=em)
                threading.Thread(target=banuser,args=(str(mem.guild.id),str(mem.id),f"{mem.name}#{mem.discriminator}", )).start()

@bot.command(options=[Option('channel', 'Channel where will be send logs', OptionType.CHANNEL)],description="Sets logs channels")
@commands.has_permissions(administrator=True)
async def setlogschannel(ctx,channel:discord.TextChannel):
    with open(f'logs.json', 'r',encoding='utf8') as f:
        chid = json.load(f) 

        chid[str(ctx.guild.id)] = str(channel.id)
        with open(f'logs.json', 'w',encoding='utf8') as f:
            json.dump(chid, f, indent=4)
    em=discord.Embed(title="Logs channel",description=f"Logs channel has been set to <#{channel.id}>",color=0xFF0000)
    await ctx.reply(embed=em)

@bot.command(description="Remove all alts on server")
@commands.has_permissions(administrator=True)
async def kill(ctx):
    with open("blacklist.json", "r",encoding="utf8") as black3:
        blacklist3 = json.load(black3)
    for mem in ctx.guild.members:
        for eeeee in blacklist3["blacklist"]:
            if mem.name.endswith(" | "+eeeee) or mem.name.startswith(eeeee+" | "):
                threading.Thread(target=banuser,args=(str(mem.guild.id),str(mem.id),f"{mem.name}#{mem.discriminator}", )).start()

@bot.command(description="Send stats of bot")
async def stats(ctx):
    mem=0
    for guild in bot.guilds:
        for member in guild.members:
            mem=mem+1
    descript=f"""
Servers: {len(bot.guilds)}
Users: {mem}
Bot Latency: {round(bot.latency * 1000)} ms
Developer: <@895318672229408828>"""
    em=discord.Embed(title="Bots Statistics:",description=f"{descript}",color=0xFF0000)
    await ctx.reply(embed=em)

def run():
    bot.run(__token__)
run()