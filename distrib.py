import discord
from discord import app_commands
from discord.ext import commands
import io
import csv
import random
import os
from collections import Counter

# --- BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'BALAGBAG PRO is online. List mode enabled.')
    await bot.tree.sync()

@bot.tree.command(name="distribute", description="Shows full list of items without cutting them off")
async def distribute(interaction: discord.Interaction, file: discord.Attachment):
    await interaction.response.defer()

    if not file.filename.endswith('.csv'):
        return await interaction.followup.send("❌ Please upload a .csv file!")

    try:
        content = (await file.read()).decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        
        all_names = []
        prize_rules = []

        for row in csv_reader:
            if not row: continue
            name = row[0].strip()
            if name: all_names.append(name)
            if len(row) >= 3:
                item = row[1].strip()
                try:
                    count = int(row[2].strip())
                    if item and count > 0: prize_rules.append((item, count))
                except: pass

        if not all_names:
            return await interaction.followup.send("❌ No names found in Column A!")

        winners_dict = {}

        # --- MULTI-DROP LOGIC ---
        for item, count in prize_rules:
            # Picks winners for every single item quantity
            selected_winners = random.choices(all_names, k=count)
            for winner in selected_winners:
                if winner not in winners_dict:
                    winners_dict[winner] = []
                winners_dict[winner].append(item)

        # --- 1. NEW LIST FORMAT (No cutoff) ---
        result_message = "### 📦 BALAGBAG Distribution Results\n"
        
        for player, items in winners_dict.items():
            counts = Counter(items)
            # Formats as: "2x Chest, 1x Rune Ring"
            stacked_items = [f"{qty}x {name}" if qty > 1 else name for name, qty in counts.items()]
            item_list_str = ", ".join(stacked_items)
            
            # Adds each winner to the message
            result_message += f"**{player}**:\n> {item_list_str}\n"

        # --- 2. 30 RANDOM ANNOUNCEMENTS ---
        announcements = [
            "🎉 **Big wins today!** Your hard work is paying off. Keep participating!",
            "🏆 **Victory tastes sweet!** Let's maintain this energy and keep contributing!",
            "🌟 **Shining moments!** Your activity is what makes this guild strong! 💪",
            "🎊 **Rewards delivered!** The more we contribute, the bigger the loot gets!",
            "🔥 **The guild is on fire!** Let's stay active and dominate the next battle!",
            "👑 **Legendary effort!** Keep contributing to earn your spot next time! ✨",
            "📦 **Loot secured!** Your consistency helps the whole guild thrive. Keep it up!",
            "⚡ **Power move!** Let's keep pushing for more guild milestones together!",
            "🎖️ **Medals of honor!** Participation is the key to our collective success!",
            "💎 **Diamond standard!** Let's keep proving we are the top guild! 💎",
            "📣 **Roll call of winners!** You guys earned it. Keep providing for the family!",
            "🏹 **Bullseye!** Everyone, let's ramp up our efforts for the next round! 🎯",
            "🧱 **Building greatness!** Every contribution helps us reach the top tier!",
            "⚔️ **Battle-ready!** Keep grinding and keep the guild pride alive! 🦁",
            "✅ **Distribution confirmed!** Let's make sure our contribution points stay high!",
            "🔥 **Top tier performance!** You guys are the backbone of this guild! 🦴",
            "🌠 **Stellar work!** This is how a championship guild operates! 🌌",
            "🦾 **Solid grind!** Your dedication is reflected in these rewards! 🛠️",
            "🚩 **Leading the pack!** Let's keep our guild name at the top of the charts!",
            "🍻 **Cheers to the victors!** Drink up and get ready for the next war! 🍺",
            "🦅 **Eagle eye!** You saw the goal and you hit it. Great job everyone!",
            "🧨 **Explosive growth!** The guild is getting stronger because of you!",
            "🍀 **Luck meets skill!** Great job winners, keep that contribution coming!",
            "🤜 **Solid teamwork!** This loot is a symbol of our unit's strength!",
            "🔝 **Always peaking!** Let's never settle for second place! 🥇",
            "🌌 **Infinite potential!** Let's keep smashing those guild goals!",
            "🤺 **Masterclass!** You winners showed us how it's done today!",
            "🏰 **Defending the throne!** Your activity keeps our castle standing!",
            "🎭 **Main characters only!** Great job winners, stay active!",
            "🔋 **Full energy!** Let's carry this hype into next week's events!"
        ]

        # --- 3. 30 RANDOM ROASTS ---
        roasts = [
            "As for **{u}**, your luck is garbage. Go cry in a corner. 🤡",
            "**{u}**, the universe said 'No.' Imagine getting nothing. 📉",
            "**{u}**, delete the game. You're just a background character. 💀",
            "RNGesus hates **{u}** specifically. Luck dry as a desert. 🌵",
            "Imagine being **{u}** and getting nothing while everyone else eats. 🚮",
            "**{u}** failed the roll the hardest. Better luck in the next life. ⚰️",
            "Winners celebrate while **{u}** reconsiders all life choices. 🧠",
            "If luck was a sport, **{u}** would be a gold medalist in losing. 🎪",
            "**{u}** is why we can't have nice things. Absolute clown. 🤷",
            "Extreme salt detected from **{u}**. Get this loser a tissue. 🧂",
            "Loot successful for everyone except **{u}** and other nobodies. 👤",
            "**{u}** has the RNG of a wet paper towel. Truly impressive failure. 🧻",
            "We said 'Distribution,' but for **{u}**, we meant 'Disappointment.' 😞",
            "The bot was programmed to give **{u}** nothing. It was personal. 🤖",
            "To **{u}**: Your contribution was mid and your luck is worse. 🤡",
            "**{u}** is just here to spectate greatness. Carry on, loser. 🍿",
            "Is **{u}** even playing? Because your loot table is empty. 🕵️",
            "Error 404: **{u}**'s luck not found. Try being better. 🔌",
            "**{u}** is currently 0-1 against the random number generator. 🕯️",
            "Someone tell **{u}** that participation trophies aren't real loot. 🏆",
            "**{u}** is the human equivalent of a 'Miss' notification. 💨",
            "If failure was currency, **{u}** would be the richest person here. 💸",
            "**{u}** is just in the guild to make the winners look better. 🪵",
            "Breaking: **{u}** officially has the worst RNG in server history. 📢",
            "**{u}** is officially part of the 'No Loot' club. 🚫",
            "I'd roast **{u}**, but their loot history is already a burnt wreck. 🔥",
            "**{u}** is a master of getting 'Better Luck Next Time' messages. ✉️",
            "Watching **{u}** lose is the best entertainment we've had all day. 🎭",
            "**{u}**'s inventory is as empty as their contribution bar. 🕳️",
            "Don't worry **{u}**, someone has to be at the bottom of the food chain. 🐟"
        ]

        # Loser logic
        all_winners = set(winners_dict.keys())
        losers = [n for n in all_names if n not in all_winners]
        unlucky = random.choice(losers) if losers else "the RNG"

        # Assemble Final Message
        final_msg = f"{result_message}\n{random.choice(announcements)}\n\n🔔 @everyone\n> {random.choice(roasts).format(u=unlucky)}"
        
        await interaction.followup.send(final_msg)

    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")

bot.run(os.getenv('DISCORD_TOKEN'))
