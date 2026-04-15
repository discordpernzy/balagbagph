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
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# --- THE COMMAND ---
@bot.tree.command(name="distribute", description="Upload a CSV: Col 1 = Names, Col 2 = Items")
async def distribute(interaction: discord.Interaction, file: discord.Attachment):
    await interaction.response.defer()

    if not file.filename.endswith('.csv'):
        return await interaction.followup.send("❌ Please upload a .csv file!")

    try:
        content = (await file.read()).decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        raw_data = list(csv_reader)
        
        # Extract and clean data
        players = sorted(list(set(row[0].strip() for row in raw_data if len(row) > 0 and row[0].strip())))
        items = [row[1].strip() for row in raw_data if len(row) > 1 and row[1].strip()]

        if not players or not items:
            return await interaction.followup.send("❌ CSV must have names in Col 1 and items in Col 2.")

        random.shuffle(items)
        random.shuffle(players)

        dist = {p: [] for p in players}
        for i, item in enumerate(items):
            recipient = players[i % len(players)]
            dist[recipient].append(item)

        # 1. Send Individual Embeds
        for player, loot in dist.items():
            loot_text = "\n".join(loot) if loot else "No items"
            embed = discord.Embed(
                title=f"🎒 {player}",
                description=f"```{loot_text}```",
                color=0x00ff88
            )
            await interaction.followup.send(embed=embed)

        # 2. Create Summary Table
        summary_table = "```\n+----------------+--------------------------+\n"
        summary_table += "| Recipient      | Items Distributed        |\n"
        summary_table += "+----------------+--------------------------+\n"
        
        for player, loot in dist.items():
            items_str = ", ".join(loot) if loot else "None"
            # Truncate if items list is too long for the table row
            if len(items_str) > 24:
                items_str = items_str[:21] + "..."
            summary_table += f"| {player[:14]:<14} | {items_str:<24} |\n"
            
        summary_table += "+----------------+--------------------------+```"

        # 3. Final Formal Message & @everyone
        # Note: Mentioning @everyone requires the bot to have "Mention Everyone" permissions
        final_message = (
            f"**Distribution Complete**\n\n"
            f"{summary_table}\n\n"
            f"🔔 @everyone\n"
            f"> **Notice:** The distribution process has concluded. All designated winners are formally requested "
            f"to verify their allocated items and update the records accordingly."
        )
        
        await interaction.followup.send(final_message)

    except Exception as e:
        await interaction.followup.send(f"❌ Error processing CSV: {e}")

# --- STARTUP LOGIC ---
TOKEN = os.getenv('DISCORD_TOKEN')

if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ ERROR: 'DISCORD_TOKEN' not found in environment variables.")
