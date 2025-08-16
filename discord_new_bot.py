import discord
from discord.ext import commands, tasks
import os
import json
import asyncio
from collections import defaultdict
import time

# ----------------- Rate Limiting -----------------
# Global dictionary to track user cooldowns
user_last_command = defaultdict(lambda: 0)
GLOBAL_COOLDOWN = 1  # seconds between any command per user

def is_on_global_cooldown(user_id):
    """Check if user is on a short global cooldown."""
    now = time.time()
    if now - user_last_command[user_id] < GLOBAL_COOLDOWN:
        return True
    user_last_command[user_id] = now
    return False

# ----------------- Bot Setup -----------------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="m.", intents=intents)

STOCK_FILE = "stock.json"

# ----------------- Stock Handling -----------------
def load_stock():
    try:
        with open(STOCK_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_stock():
    with open(STOCK_FILE, "w") as f:
        json.dump(stock, f, indent=4)

stock = load_stock()

# ----------------- Commands -----------------
@bot.command()
async def addstock(ctx, item: str, *codes):
    """Add one or more codes to stock for an item."""
    if is_on_global_cooldown(ctx.author.id):
        return await ctx.send("⏱ Please wait a moment before using another command.")
    
    if not codes:
        await ctx.send("❌ You must provide at least one code to add.")
        return
    item = item.lower()
    if item not in stock:
        stock[item] = []
    stock[item].extend(codes)
    save_stock()
    await ctx.send(f"✅ Added **{len(codes)}** code(s) to stock for **{item}**. Total: {len(stock[item])}")

@bot.command()
@commands.cooldown(1, 21600, commands.BucketType.user)  # 6 hours cooldown per user
async def gen(ctx, item: str):
    """Generate a code from stock and DM it to the user."""
    if is_on_global_cooldown(ctx.author.id):
        return await ctx.send("⏱ Please wait a moment before using another command.")
    
    item = item.lower()
    if item not in stock or len(stock[item]) == 0:
        await ctx.send(f"No stock available for **{item}**.")
        return

    code = stock[item].pop(0)
    save_stock()

    # Public embed
    public_embed = discord.Embed(
        description=(
            f"<a:emoji_7:1405847680713883718> **Your {item} code has been generated successfully!**\n\n"
            f"<a:emoji_6:1405847349691027596> Check your DMs for the details "
            f"<a:emoji_8:1405847707821539338>"
        ),
        color=discord.Color.blue()
    )
    public_embed.set_footer(text="Thanks for using our bot!")
    await ctx.send(embed=public_embed)
    await asyncio.sleep(0.5)  # Small delay to prevent rate limits

    # DM embed
    try:
        dm_embed = discord.Embed(
            title="<a:emoji_6:1405847349691027596> 🎁 Your Code is Ready!",
            description=(
                f"**Item:** {item}\n"
                f"**Code:**\n```{code}```\n"
                "<a:emoji_7:1405847680713883718> Redeem it as soon as possible!"
            ),
            color=discord.Color.purple()
        )
        dm_embed.set_footer(text="Generated with ❤️ by Our Bot")
        dm_embed.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1405847707821539338.gif?size=96&quality=lossless"
        )
        await ctx.author.send(embed=dm_embed)
        await asyncio.sleep(0.5)  # Delay to reduce chance of 429
    except discord.Forbidden:
        await ctx.send("I couldn't send you a DM. Please check your privacy settings.")

@bot.command(name="stock")
async def stock_command(ctx):
    """Show all stock in an embed."""
    if is_on_global_cooldown(ctx.author.id):
        return await ctx.send("⏱ Please wait a moment before using another command.")

    if not stock:
        embed = discord.Embed(
            title="<a:emoji_8:1405847707821539338> 📦 Current Stock",
            description="❌ No stock available for any item.\nAdd stock using `m.addstock <item> <code>`",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title="<a:emoji_8:1405847707821539338> 📦 Current Stock",
        description="Here’s the list of all available items and their stock counts:",
        color=discord.Color.green()
    )
    for item, codes in stock.items():
        embed.add_field(
            name=f"🎯 {item}",
            value=f"<a:emoji_6:1405847349691027596> **{len(codes)}** code(s) available",
            inline=False
        )
    embed.set_footer(text=f"📊 Total items: {len(stock)} | Use m.gen <item> to get a code")
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/emojis/1405847349691027596.gif?size=96&quality=lossless"
    )
    await ctx.send(embed=embed)
    await asyncio.sleep(0.5)

@bot.command()
async def delstock(ctx, item: str):
    """Delete a stock category."""
    if is_on_global_cooldown(ctx.author.id):
        return await ctx.send("⏱ Please wait a moment before using another command.")

    item = item.lower()
    if item not in stock:
        await ctx.send(f"❌ No stock found for **{item}**.")
        return

    del stock[item]
    save_stock()
    await ctx.send(f"🗑️ Deleted stock category **{item}**.")

@bot.command(name="helpme")
async def help_command(ctx):
    if is_on_global_cooldown(ctx.author.id):
        return await ctx.send("⏱ Please wait a moment before using another command.")

    embed = discord.Embed(
        title="📖 Bot Help Menu",
        description="Here are all the available commands:",
        color=discord.Color.gold()
    )
    embed.add_field(name="➕ Add Stock", value="`m.addstock <item> <code1> <code2> ...`", inline=False)
    embed.add_field(name="🎁 Generate Code", value="`m.gen <item>` (6h cooldown per user)", inline=False)
    embed.add_field(name="📦 Check Stock", value="`m.stock`", inline=False)
    embed.add_field(name="🗑️ Delete Stock", value="`m.delstock <item>`", inline=False)
    embed.set_footer(text="Made with ❤️ | Only trusted roles can generate codes.")
    await ctx.send(embed=embed)
    await asyncio.sleep(0.5)

# ----------------- Run Bot -----------------
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("❌ ERROR: BOT_TOKEN not found in environment variables.")
else:
    bot.run(TOKEN)        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title="<a:emoji_8:1405847707821539338> 📦 Current Stock",
        description="Here’s the list of all available items and their stock counts:",
        color=discord.Color.green()
    )

    for item, codes in stock.items():
        embed.add_field(
            name=f"🎯 {item}",
            value=f"<a:emoji_6:1405847349691027596> **{len(codes)}** code(s) available",
            inline=False
        )

    embed.set_footer(text=f"📊 Total items: {len(stock)} | Use m.gen <item> to get a code")
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/emojis/1405847349691027596.gif?size=96&quality=lossless"
    )
    await ctx.send(embed=embed)


@bot.command()
async def delstock(ctx, item: str):
    """Delete a stock category."""
    item = item.lower()
    if item not in stock:
        await ctx.send(f"❌ No stock found for **{item}**.")
        return

    del stock[item]
    save_stock()
    await ctx.send(f"🗑️ Deleted stock category **{item}**.")


# Custom help command
@bot.command(name="helpme")
async def help_command(ctx):
    embed = discord.Embed(
        title="📖 Bot Help Menu",
        description="Here are all the available commands:",
        color=discord.Color.gold()
    )
    embed.add_field(name="➕ Add Stock", value="`m.addstock <item> <code1> <code2> ...`", inline=False)
    embed.add_field(name="🎁 Generate Code", value="`m.gen <item>` (6h cooldown per user)", inline=False)
    embed.add_field(name="📦 Check Stock", value="`m.stock`", inline=False)
    embed.add_field(name="🗑️ Delete Stock", value="`m.delstock <item>`", inline=False)
    embed.set_footer(text="Made with ❤️ | Only trusted roles can generate codes.")
    await ctx.send(embed=embed)


# ----------------- Run Bot -----------------
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("❌ ERROR: BOT_TOKEN not found in environment variables.")
else:
    bot.run(TOKEN)
