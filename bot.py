import discord
from discord.ext import commands, tasks
import requests
import datetime
import pytz
import random

TOKEN = "TON_TOKEN_DISCORD"
API_KEY = "TA_API_FOOTBALL"

API_URL = "https://v3.football.api-sports.io"

channel_id = 1481318159142092952

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

timezone = pytz.timezone("Africa/Lubumbashi")


def get_matches():

    today = datetime.datetime.now(timezone).strftime("%Y-%m-%d")

    url = f"{API_URL}/fixtures?date={today}"

    headers = {
        "x-apisports-key": API_KEY
    }

    r = requests.get(url, headers=headers)

    data = r.json()

    matches = []

    for game in data["response"][:20]:

        home = game["teams"]["home"]["name"]
        away = game["teams"]["away"]["name"]

        matches.append({
            "home": home,
            "away": away
        })

    return matches


def generate_predictions(matches):

    random.shuffle(matches)

    scores = matches[:5]
    btts = matches[5:10]
    over = matches[10:15]
    double = matches[15:20]

    return scores, btts, over, double


def generate_coupons(matches):

    coupons = []

    for i in range(3):

        games = random.sample(matches, 5)

        odds = round(random.uniform(50, 300), 2)

        coupons.append((games, odds))

    return coupons


@bot.command()

async def pronos(ctx):

    await ctx.send("⏳ Analyse des matchs en cours...")

    matches = get_matches()

    scores, btts, over, double = generate_predictions(matches)

    message = "⚽ **PRONOSTICS CASHGOAL**\n\n"

    message += "🎯 **Scores Exacts**\n"

    for m in scores:

        s = f"{random.randint(0,3)}-{random.randint(0,3)}"

        message += f"{m['home']} vs {m['away']} → {s}\n"

    message += "\n🔥 **BTTS (Les deux équipes marquent)**\n"

    for m in btts:

        message += f"{m['home']} vs {m['away']} → OUI\n"

    message += "\n📊 **Over 2.5 buts**\n"

    for m in over:

        message += f"{m['home']} vs {m['away']} → OVER 2.5\n"

    message += "\n🛡 **Equipe mène et ne perd pas**\n"

    for m in double:

        message += f"{m['home']} vs {m['away']} → 1X\n"

    coupons = generate_coupons(matches)

    message += "\n💰 **Coupons Combinés**\n"

    for i,c in enumerate(coupons):

        message += f"\nCoupon {i+1} (cote {c[1]})\n"

        for g in c[0]:

            message += f"{g['home']} vs {g['away']}\n"

    await ctx.send(message)


@tasks.loop(minutes=60)

async def daily_post():

    now = datetime.datetime.now(timezone)

    if now.hour == 9 and now.minute == 30:

        channel = bot.get_channel(channel_id)

        matches = get_matches()

        text = "📊 **Pronostics du jour**\nTapez `!pronos` pour voir les analyses."

        await channel.send(text)


@bot.event

async def on_ready():

    print("Bot connecté")

    daily_post.start()


bot.run(TOKEN)
