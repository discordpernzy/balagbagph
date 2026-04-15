import discord
from discord import app_commands
from discord.ext import commands
import io
import csv
import random
import os

# --- BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'BALAGBAG is online as {bot.user}')
    await bot.tree.sync()

@bot.tree.command(name="distribute", description="Pick X number of winners for each item from the list")
async def distribute(interaction: discord.Interaction, file: discord.Attachment):
    await interaction.response.defer()

    if not file.filename.endswith('.csv'):
        return await interaction.followup.send("❌ Please upload a .csv file!")

    try:
        content = (await file.read()).decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        
        all_names = []
        prize_rules = [] # List of (item_name, num_winners)

        # 1. Parse the CSV
        for row in csv_reader:
            if not row: continue
            
            # Column A: Collect Names
            name = row[0].strip()
            if name:
                all_names.append(name)
            
            # Column B & C: Collect Item and Number of Winners
            if len(row) >= 3:
                item_name = row[1].strip()
                try:
                    num_winners = int(row[2].strip())
                    if item_name and num_winners > 0:
                        prize_rules.append((item_name, num_winners))
                except ValueError:
                    pass # Skip if Column C is not a number

        if not all_names or not prize_rules:
            return await interaction.followup.send("❌ Error: Column A needs names, Column B needs items, and Column C needs a number!")

        # 2. Start the Lottery
        pool = all_names.copy()
        winners_dict = {} # {Name: [Items]}

        for item, count in prize_rules:
            # Pick 'count' number of people from whoever is left in the pool
            if not pool:
                break # Stop if we run out of people
            
            # random.sample handles picking multiple unique people at once
            selected_winners = random.sample(pool, min(len(pool), count))
            
            for winner in selected_winners:
                if winner not in winners_dict:
                    winners_dict[winner] = []
                winners_dict[winner].append(item)
                # Remove from pool so they don't win multiple items in one session
                pool.remove(winner)

        # 3. Output Table
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

        # 4. Final Roast Message
        if pool:
            unlucky_soul = random.choice(pool)
            msg = (
                f"🔔 @everyone\n"
                f"> **Distribution Finalized.** {len(winners_dict)} winners picked.\n"
                f"> For the **{len(pool)}** of you who got nothing—especially **{unlucky_soul}**...\n"
                f"> Your luck is absolute garbage. Go cry in a corner. 🤡"
            )
            await interaction.followup.send(msg)
        else:
            await interaction.followup.send("🔔 @everyone\n> Everyone won something. This guild is too soft.")

    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")

bot.run(os.getenv('DISCORD_TOKEN'))
