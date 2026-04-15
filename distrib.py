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
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()

# Helper function to split the table into chunks
def chunk_table(data_dict, chunk_size=20):
    it = iter(data_dict.items())
    for i in range(0, len(data_dict), chunk_size):
        yield {k: next(it)[1] for k in list(data_dict)[i:i + chunk_size]}

@bot.tree.command(name="distribute", description="Handles large guilds (up to 50+ members)")
async def distribute(interaction: discord.Interaction, file: discord.Attachment):
    await interaction.response.defer()

    if not file.filename.endswith('.csv'):
        return await interaction.followup.send("❌ Please upload a .csv file!")

    try:
        content = (await file.read()).decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        raw_data = list(csv_reader)
        
        players = sorted(list(set(row[0].strip() for row in raw_data if len(row) > 0 and row[0].strip())))
        items = [row[1].strip() for row in raw_data if len(row) > 1 and row[1].strip()]

        if not players or not items:
            return await interaction.followup.send("❌ CSV data is empty or malformed.")

        random.shuffle(items)
        random.shuffle(players)

        dist = {p: [] for p in players}
        for i, item in enumerate(items):
            recipient = players[i % len(players)]
            dist[recipient].append(item)

        # --- OUTPUT LOGIC FOR LARGE GROUPS ---
        await interaction.followup.send(f"### 📦 BALAGBAG Distribution: {len(players)} Members Found")

        # Split players into groups of 20 to avoid the 2000 character limit
        for chunk in chunk_table(dist, chunk_size=20):
            table = "```\n+----------------+--------------------------+\n"
            table += "| Recipient      | Items                    |\n"
            table += "+----------------+--------------------------+\n"
            
            for player, loot in chunk.items():
                items_str = ", ".join(loot) if loot else "None"
                p_disp = (player[:14] + "..") if len(player) > 14 else player
                i_disp = (items_str[:22] + "...") if len(items_str) > 22 else items_str
                table += f"| {p_disp:<14} | {i_disp:<24} |\n"
            
            table += "+----------------+--------------------------+```"
            await interaction.followup.send(table)

        # Final Notification
        final_notice = (
            f"🔔 @everyone\n"
            f"> **Formal Notice:** Distribution for all {len(players)} members is complete. "
            f"Please verify your allocated items in the tables above."
        )
        await interaction.followup.send(final_notice)

    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")

bot.run(os.getenv('DISCORD_TOKEN'))
