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

def chunk_table(data_dict, chunk_size=20):
    it = iter(data_dict.items())
    for i in range(0, len(data_dict), chunk_size):
        yield {k: next(it)[1] for k in list(data_dict)[i:i + chunk_size]}

@bot.tree.command(name="distribute", description="Distribute items and roast the losers")
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

        # Distribute
        dist = {p: [] for p in players}
        for i, item in enumerate(items):
            recipient = players[i % len(players)]
            dist[recipient].append(item)

        # --- SEPARATE WINNERS AND LOSERS ---
        winners = {p: loot for p, loot in dist.items() if loot}
        losers = [p for p, loot in dist.items() if not loot]

        await interaction.followup.send(f"### 📦 BALAGBAG Distribution: {len(winners)} Lucky Winners")

        # Only show the table for winners
        if winners:
            for chunk in chunk_table(winners, chunk_size=20):
                table = "```\n+----------------+--------------------------+\n"
                table += "| Winner         | Items Received           |\n"
                table += "+----------------+--------------------------+\n"
                
                for player, loot in chunk.items():
                    items_str = ", ".join(loot)
                    p_disp = (player[:14] + "..") if len(player) > 14 else player
                    i_disp = (items_str[:22] + "...") if len(items_str) > 22 else items_str
                    table += f"| {p_disp:<14} | {i_disp:<24} |\n"
                
                table += "+----------------+--------------------------+```"
                await interaction.followup.send(table)
        else:
            await interaction.followup.send("_No items were distributed._")

        # --- THE SILLY ROAST MESSAGE ---
        roast_message = "🔔 @everyone\n"
        if losers:
            # Join names with commas, or just mention the count if there are too many
            if len(losers) > 10:
                unlucky_text = f"{len(losers)} people (including {random.choice(losers)})"
            else:
                unlucky_text = ", ".join(losers)

            roast_message += (
                f"> **Loot Summary:** Congrats to the winners. \n"
                f"> As for **{unlucky_text}**... your luck absolutely sucks. Better luck next time, losers! 🤡"
            )
        else:
            roast_message += "> **Notice:** Everyone actually got something today. Must be a miracle."

        await interaction.followup.send(roast_message)

    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")

bot.run(os.getenv('DISCORD_TOKEN'))
