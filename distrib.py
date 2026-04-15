import discord
from discord import app_commands
from discord.ext import commands
import io
import csv
import random
import os

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'BALAGBAG is online as {bot.user}')
    await bot.tree.sync()

@bot.tree.command(name="distribute", description="Pick winners and drop one of 15 random roasts")
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

        if not all_names or not prize_rules:
            return await interaction.followup.send("❌ Check your CSV formatting!")

        pool = all_names.copy()
        winners_dict = {}

        for item, count in prize_rules:
            if not pool: break
            selected = random.sample(pool, min(len(pool), count))
            for winner in selected:
                if winner not in winners_dict: winners_dict[winner] = []
                winners_dict[winner].append(item)
                pool.remove(winner)

        # Output Table
        await interaction.followup.send(f"### 📦 BALAGBAG Distribution Results")
        table = "```\n+----------------+-----------------------------------+\n"
        table += "| Winner         | Item Won                          |\n"
        table += "+----------------+-----------------------------------+\n"
        for player, items in winners_dict.items():
            item_str = ", ".join(items)
            p_disp = (player[:14] + "..") if len(player) > 14 else player
            i_disp = (item_str[:32] + "...") if len(item_str) > 32 else item_str
            table += f"| {p_disp:<14} | {i_disp:<33} |\n"
        table += "+----------------+-----------------------------------+```"
        await interaction.followup.send(table)

        # --- THE 15 ROASTS ---
        if pool:
            unlucky = random.choice(pool)
            loser_count = len(pool)
            
            roasts = [
                f"> **Looting Over.** {loser_count} people got nothing. **{unlucky}**, your luck is absolute garbage. Go cry in a corner. 🤡",
                f"> **Distribution Finalized.** **{unlucky}**, the universe specifically said 'No' to you today. Imagine being the lead loser. 📉",
                f"> **Notice:** **{unlucky}**, delete the game. You and the other {loser_count} losers are just background characters. 💀",
                f"> **Breaking News:** RNGesus hates **{unlucky}** specifically. Your luck is as dry as a desert. 🌵",
                f"> **Summary:** Imagine being **{unlucky}** and getting nothing while everyone else eats. Uninstalling is free! 🚮",
                f"> **Ouch:** {loser_count} people failed the roll, but **{unlucky}** failed the hardest. Better luck in the next life. ⚰️",
                f"> **Status Report:** {winners_dict.keys().__len__()} people are celebrating. **{unlucky}** is currently reconsidering all life choices. 🧠",
                f"> **RNG Alert:** If being unlucky was a sport, **{unlucky}** would be a gold medalist. Absolute clown behavior. 🎪",
                f"> **Fact Check:** **{unlucky}** is the reason we can't have nice things. Imagine being part of the {loser_count} unlucky group. 🤷",
                f"> **Warning:** Extreme salt detected coming from **{unlucky}**. Someone get this loser a tissue. 🧂",
                f"> **System Update:** Loot distribution successful for everyone except **{unlucky}** and {loser_count-1} other nobodies. 👤",
                f"> **Analysis:** **{unlucky}** has the RNG of a wet paper towel. Truly impressive failure. 🧻",
                f"> **Correction:** We said 'Distribution,' but for **{unlucky}**, we meant 'Disappointment.' 😞",
                f"> **Top Secret:** The bot was programmed to give **{unlucky}** nothing. It was personal. 🤖",
                f"> **Final Word:** Congrats to the winners! To **{unlucky}**: Your contribution was mid and your luck is worse. 🤡"
            ]
            
            await interaction.followup.send(f"🔔 @everyone\n{random.choice(roasts)}")
        else:
            await interaction.followup.send("🔔 @everyone\n> Everyone won. My roasting sensors are bored. 🙄")

    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")

bot.run(os.getenv('DISCORD_TOKEN'))
