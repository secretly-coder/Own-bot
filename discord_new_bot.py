import discord
from discord.ext import commands
import os
import json

# Enable intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="m.", intents=intents)

# Stock save/load file
STOCK_FILE = "stock.json"

# Load stock from JSON file
def load_stock():
    try:
        with open(STOCK_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save stock to JSON file
def save_stock():
    with open(STOCK_FILE, "w") as f:
        json.dump(stock, f, indent=4)

# In-memory stock
stock = load_stock()

# Role name allowed to manage stock
ADMIN_ROLE = "Admin"

# ---------------- Commands ----------------

@bot.command()
@commands.has_role(ADMIN_ROLE)
async def addstock(ctx, item: str, *codes):
    """Add one or more codes to stock for an item (Admins only)."""
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
@commands.cooldown(1, 21600, commands.BucketType.user)  # 6 hours cooldown
async def gen(ctx, item: str):
    """Generate a code from stock and DM it to the user."""
    item = item.lower()
    if item not in stock or len(stock[item]) == 0:
        await ctx.send(f"No stock available for **{item}**.")
        return

    code = stock[item].pop(0)
    save_stock()

    # Public success embed
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

    # Private DM embed
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
    except discord.Forbidden:
        await ctx.send("I couldn't send you a DM. Please check your privacy settings.")


@bot.command(name="stock")
async def stock_command(ctx):
    """Show all stock in a beautiful embed."""
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


@bot.command()
@commands.has_role(ADMIN_ROLE)
async def delstock(ctx, item: str):
    """Delete a stock category (Admins only)."""
    item = item.lower()
    if item not in stock:
        await ctx.send(f"❌ No stock found for **{item}**.")
        return

    del stock[item]
    save_stock()
    await ctx.send(f"🗑️ Deleted stock category **{item}**.")


@bot.command(name="helpme")
async def help_command(ctx):
    embed = discord.Embed(
        title="📖 Bot Help Menu",
        description="Here are all the available commands:",
        color=discord.Color.gold()
    )
    embed.add_field(name="➕ Add Stock", value="`m.addstock <item> <code1> <code2> ...` (Admin only)", inline=False)
    embed.add_field(name="🎁 Generate Code", value="`m.gen <item>` (6h cooldown per user)", inline=False)
    embed.add_field(name="📦 Check Stock", value="`m.stock`", inline=False)
    embed.add_field(name="🗑️ Delete Stock", value="`m.delstock <item>` (Admin only)", inline=False)
    embed.set_footer(text="Made with ❤️ | Only trusted roles can generate codes.")
    await ctx.send(embed=embed)


# ----------------- Run Bot -----------------
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("❌ ERROR: BOT_TOKEN not found in environment variables.")
else:
    bot.run(TOKEN)
