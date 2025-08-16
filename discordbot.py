import discord
from discord.ext import commands
import json
import os
import asyncio

# Enable intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="m.", intents=intents)

# File for storing stock
STOCK_FILE = "stock.json"

# Load stock from file or create empty dict
if os.path.exists(STOCK_FILE):
    with open(STOCK_FILE, "r") as f:
        stock = json.load(f)
else:
    stock = {}

# Save stock to file
def save_stock():
    with open(STOCK_FILE, "w") as f:
        json.dump(stock, f, indent=4)

# Cooldown dictionary {user_id: timestamp}
cooldowns = {}

# Role ID allowed to gen codes
GEN_ROLE_ID = 1405983771043430410  # Replace with your role ID

@bot.command()
async def addstock(ctx, item: str, *codes):
    if not codes:
        await ctx.send("❌ You must provide at least one code to add.")
        return
    item_lower = item.lower()
    if item_lower not in stock:
        stock[item_lower] = []
    stock[item_lower].extend(codes)
    save_stock()
    await ctx.send(f"✅ Added **{len(codes)}** code(s) to stock for **{item_lower}**. Total: {len(stock[item_lower])}")

@bot.command()
async def gen(ctx, item: str):
    item_lower = item.lower()
    # Check cooldown
    user_id = str(ctx.author.id)
    if user_id in cooldowns:
        remaining = int(cooldowns[user_id] - asyncio.get_event_loop().time())
        if remaining > 0:
            await ctx.send(f"⏳ You are on cooldown. Try again in {remaining//3600}h {(remaining%3600)//60}m.")
            return

    # Check role
    role_ids = [role.id for role in ctx.author.roles]
    if GEN_ROLE_ID not in role_ids:
        await ctx.send("❌ You don't have permission to generate codes.")
        return

    if item_lower not in stock or len(stock[item_lower]) == 0:
        await ctx.send(f"No stock available for **{item_lower}**.")
        return

    code = stock[item_lower].pop(0)
    save_stock()
    cooldowns[user_id] = asyncio.get_event_loop().time() + 21600  # 6 hours

    # Public success embed
    public_embed = discord.Embed(
        description=(
            f"<a:emoji_7:1405847680713883718> **Your {item_lower} code has been generated successfully!**\n\n"
            f"<a:emoji_6:1405847349691027596> Check your DMs for the details "
            f"<a:emoji_8:1405847707821539338>"
        ),
        color=discord.Color.blue()
    )
    public_embed.set_footer(text="Thanks for using our bot!")
    await ctx.send(embed=public_embed)

    # Private DM embed
    try:
        dm_embed = discord.Embed(
            title="<a:emoji_6:1405847349691027596> 🎁 Your Code is Ready!",
            description=f"**Item:** {item_lower}\n**Code:**\n```{code}```\n<a:emoji_7:1405847680713883718> Redeem it as soon as possible!",
            color=discord.Color.purple()
        )
        dm_embed.set_footer(text="Generated with ❤️ by Our Bot")
        dm_embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1405847707821539338.gif?size=96&quality=lossless")
        await ctx.author.send(embed=dm_embed)
    except discord.Forbidden:
        await ctx.send("I couldn't send you a DM. Please check your privacy settings.")

@bot.command()
async def delstock(ctx, item: str):
    item_lower = item.lower()
    if item_lower in stock:
        del stock[item_lower]
        save_stock()
        await ctx.send(f"🗑️ Stock for **{item_lower}** deleted.")
    else:
        await ctx.send(f"No stock found for **{item_lower}**.")

@bot.command(name="stock")
async def stock_command(ctx):
    if not stock:
        embed = discord.Embed(
            title="📦 Current Stock",
            description="❌ No stock available for any item.\nAdd stock using `m.addstock <item> <code>`",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title="📦 Current Stock",
        description="Here’s the list of all available items and their stock counts:",
        color=discord.Color.green()
    )
    for item, codes in stock.items():
        embed.add_field(
            name=f"🎯 {item}",
            value=f"**{len(codes)}** code(s) available",
            inline=False
        )
    embed.set_footer(text=f"📊 Total items: {len(stock)} | Use m.gen <item> to get a code")
    await ctx.send(embed=embed)

@bot.command()
async def helpme(ctx):
    embed = discord.Embed(
        title="📜 Bot Commands",
        description=(
            "**m.addstock <item> <codes...>** - Add code(s) to stock\n"
            "**m.gen <item>** - Generate a code (requires gen role)\n"
            "**m.delstock <item>** - Delete stock of an item\n"
            "**m.stock** - Show all stock\n"
        ),
        color=0xFFD700  # Gold color
    )
    await ctx.send(embed=embed)

bot.run("YOUR_BOT_TOKEN")
