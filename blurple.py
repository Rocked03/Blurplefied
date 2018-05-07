import traceback
import datetime
import aiohttp
import copy
import math
import time
import io
import re
import os

import numpy as np
import discord

from PIL import Image, ImageEnhance, ImageSequence

from discord.ext.commands.cooldowns import BucketType
from discord.ext import commands

try:
    from config import TOKEN, BOT_PREFIX
except ModuleNotFoundError:
    # Probably in a docker container, just read environment
    TOKEN = os.environ.get('TOKEN')
    BOT_PREFIX = os.environ.get('BOT_PREFIX')

description = '''Blurple Bot'''
bot = commands.Bot(command_prefix=BOT_PREFIX, description=description)

rocked = 204778476102877187

BLURPLE = (114, 137, 218, 255)
BLURPLE_HEX = 0x7289da
DARK_BLURPLE = (78, 93, 148, 255)
WHITE = (255, 255, 255, 255)

PIXEL_COUNT_LIMIT = 3840 * 2160
MAX_PIXEL_COUNT = 1280 * 720
MAX_FILE_SIZE = 8 * 1024 * 1024 * 16  # 16M

COLOUR_BUFFER = 20

MENTION_RE = re.compile(r'<@!?([0-9]+)>')

bot.remove_command('help')

allowed_users_list = set([int(i) for i in os.environ.get('ALLOWED_USERS').split(',')])
approved_channels = set([int(i) for i in os.environ.get('APPROVED_CHANNELS').split(',')])


class ImageStats:
    __slots__ = ('dark', 'blurple', 'white', 'pixels')

    def __init__(self, dark, blurple, white, pixels):
        self.dark = dark
        self.blurple = blurple
        self.white = white
        self.pixels = pixels

    @property
    def total(self):
        return self.dark + self.blurple + self.white

    def percentage(self, value):
        return round(value / self.pixels * 100, 2)

    @classmethod
    def from_image(cls, img):
        arr = np.asarray(img).copy()

        dark = np.all(np.abs(arr - DARK_BLURPLE) < COLOUR_BUFFER, axis=2).sum()
        blurple = np.all(np.abs(arr - BLURPLE) < COLOUR_BUFFER, axis=2).sum()
        white = np.all(np.abs(arr - WHITE) < COLOUR_BUFFER, axis=2).sum()
        pixels = img.size[0] * img.size[1]

        mask = np.logical_and(np.abs(arr - DARK_BLURPLE) >= COLOUR_BUFFER,
                              np.abs(arr - BLURPLE) >= COLOUR_BUFFER,
                              np.abs(arr - WHITE) >= COLOUR_BUFFER)
        mask = np.any(mask, axis=2)

        arr[mask] = (0, 0, 0, 255)

        image_file_object = io.BytesIO()
        Image.fromarray(np.uint8(arr)).save(image_file_object, format='png')
        image_file_object.seek(0)

        return image_file_object, ImageStats(dark, blurple, white, pixels)


def allowed_users():
    async def pred(ctx):
        return ctx.author.id in allowed_users_list

    return commands.check(pred)


@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


@bot.check
async def only_in_commands_channels(ctx):
    return ctx.channel.id in approved_channels or ctx.author.id in allowed_users_list



@bot.event
async def on_connect():
    print('------')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    activity = discord.Game(name="Type " + BOT_PREFIX + "help")
    await bot.change_presence(activity=activity)


@bot.command(name='shutdown', aliases=["reboot"])
@allowed_users()
async def shutdown(ctx):
    embed = discord.Embed(title="", timestamp=datetime.datetime.utcnow(), colour=0x7289da)
    embed.add_field(name="Shutting down<a:underscore:420740967939964928>", value="Blurplefied")
    await ctx.send(embed=embed)
    await bot.logout()


@bot.command()
async def help(ctx):
    embed = discord.Embed(title="", timestamp=datetime.datetime.utcnow(), colour=0x7289da)
    embed.set_author(name="Commands list")
    embed.add_field(name="Countdown", value=f"Time until Discord's Anniversary. \n**Usage:**\n`{BOT_PREFIX}countdown`")
    embed.add_field(name="Blurple",
                    value=f"Check how much blurple is in an image. If used without a picture, it analyses your own "
                          f"profile picture, and if it has enough blurple, you will receive a role. \n**Usage:**\n"
                          f"`{BOT_PREFIX}blurple <@username/user ID/picture url/None/uploaded image>`")
    embed.add_field(name="Blurplefy",
                    value=f"Blurplefy your image/gif! \n**Usage:**\n`{BOT_PREFIX}blurplefy <@username/user ID/picture "
                          f"url/None/uploaded image>`")
    embed.set_footer(text=f"Help message requested by {ctx.message.author}")
    embed.set_thumbnail(url=bot.user.avatar_url)
    await ctx.send(embed=embed)


@bot.command()
async def ping(ctx):
    latency = bot.latency * 1000
    latency = round(latency, 2)
    latency = str(latency)
    embed = discord.Embed(title="", colour=0x7289da, timestamp=datetime.datetime.utcnow())
    embed.set_author(name="Ping!")
    embed.add_field(name='Bot latency', value=latency + "ms")
    await ctx.send(embed=embed)


#@bot.command()
async def countdown(ctx):
    def strfdelta(tdelta, fmt):
        d = {"days": tdelta.days}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)

    time_left = datetime.datetime(2018, 5, 13) + datetime.timedelta(hours=7) - datetime.datetime.utcnow()
    embed = discord.Embed(name="", colour=0x7289da)
    embed.set_author(name="Time left until Discord's 3rd Anniversary")
    embed.add_field(name="Countdown to midnight May 13 California time (UTC-7)", value=(
        strfdelta(time_left, "**{days}** days, **{hours}** hours, **{minutes}** minutes, and **{seconds}** seconds")))
    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    channel = bot.get_channel(436790039750508544)
    # ignored = (commands.CommandNotFound, commands.UserInputError)
    ignored = (commands.CommandNotFound)
    if isinstance(error, ignored):
        return

    if isinstance(error, commands.CommandOnCooldown):
        if int(ctx.message.author.id) in allowed_users_list:
            await ctx.reinvoke()
            return
        else:
            msg = await ctx.send(
                f"{ctx.author.mention}, please slow down! The command `{BOT_PREFIX}{ctx.command}` has "
                f"{round(error.retry_after, 1)}s left of cooldown.")
            # await asyncio.sleep(5)
            # await msg.delete()
            # await ctx.message.delete()
            return

    print(''.join(traceback.format_exception(type(error), error, error.__traceback__)))

    if isinstance(error, commands.CheckFailure):
        return


@bot.command()
@allowed_users()
async def timeit(ctx, *, command: str):
    msg = copy.copy(ctx.message)
    msg.content = ctx.prefix + command

    new_ctx = await ctx.bot.get_context(msg)

    start = time.time()
    await new_ctx.reinvoke()
    end = time.time()

    await ctx.send(f'**{BOT_PREFIX}{new_ctx.command.qualified_name}** took **{end - start:.2f}s** to run')


@bot.command()
@commands.cooldown(rate=1, per=180, type=BucketType.user)
async def blurple(ctx, arg1=None):
    picture = None

    #await ctx.send(f"{ctx.message.author.mention}, starting blurple image analysis (Please note that this may take a while)")

async def collect_image(ctx, hint, static=False):
    mentions = MENTION_RE.findall(hint) if hint is not None else []

    if mentions:
        user = await bot.get_user_info(int(mentions[0]))
        url = user.avatar_url
    elif hint:
        url = hint
    elif ctx.message.attachments:
        url = ctx.message.attachments[0].url
    else:
        url = ctx.author.avatar_url

    data = io.BytesIO()
    length = 0
    async with aiohttp.ClientSession() as cs:
        async with cs.get(url) as resp:
            while True:
                dat = await resp.content.read(16384)
                if not dat:
                    break
                length += len(dat)
                if length > MAX_FILE_SIZE:
                    return None, None, None
                data.write(dat)

    data.seek(0)
    im = Image.open(data)

    if im.size[0] * im.size[1] > PIXEL_COUNT_LIMIT:
        return None, None, None

    frames = []
    for frame in ImageSequence.Iterator(im):
        frames.append(frame.copy())
        if static:
            break

    if im.size[0] * im.size[1] > MAX_PIXEL_COUNT:
        aspect = im.size[0] / im.size[1]

        height = math.sqrt(MAX_PIXEL_COUNT / aspect)
        width = height * aspect

        if height < im.size[1] and width < im.size[0]:
            for n, frame in enumerate(frames):
                frames[n] = frame.resize((int(width), int(height)), Image.ANTIALIAS)

    for n, frame in enumerate(frames):
        frames[n] = frame.convert('RGBA')

    return frames, url


def blurplefy_image(img):
    img = img.convert(mode='L')
    img = ImageEnhance.Contrast(img).enhance(1000)
    img = img.convert(mode='RGB')

    arr = np.asarray(img).copy()
    arr[np.any(arr != 255, axis=2)] = BLURPLE[:-1]

    return Image.fromarray(np.uint8(arr))


@bot.command()
@commands.cooldown(rate=1, per=180, type=BucketType.user)
async def blurple(ctx, arg1=None):
    frames, url = await collect_image(ctx, arg1, True)
    if frames is None:
        return await ctx.message.add_reaction('\N{CROSS MARK}')

    image, stats = await bot.loop.run_in_executor(None, ImageStats.from_image, frames[0])
    image = discord.File(fp=image, filename='image.png')

    embed = discord.Embed(Title="", colour=0x7289DA)
    embed.add_field(name="Total amount of Blurple", value=f"{stats.percentage(stats.total)}%", inline=False)
    embed.add_field(name="Blurple (rgb(114, 137, 218))", value=f"{stats.percentage(stats.blurple)}%", inline=True)
    embed.add_field(name="White (rgb(255, 255, 255))", value=f"{stats.percentage(stats.white)}\%", inline=True)
    embed.add_field(name="Dark Blurple (rgb(78, 93, 148))", value=f"{stats.percentage(stats.dark)}\%", inline=True)
    embed.add_field(name="Guide",
                    value="Blurple, White, Dark Blurple = Blurple, White, and Dark Blurple (respectively)\n"
                          "Black = Not Blurple, White, or Dark Blurple",
                    inline=False)
    embed.set_footer(
        text=f"Please note: Discord slightly reduces quality of the images, therefore the percentages may be slightly "
             f"inaccurate. | Content requested by {ctx.author}")
    embed.set_image(url="attachment://image.png")
    embed.set_thumbnail(url=url)
    await ctx.send(embed=embed, file=image)

    if url == ctx.author.avatar_url:
        blurple_user_role = discord.utils.get(ctx.message.guild.roles, id=436300514561622016)

        if blurple_user_role is not None:
            if stats.percentage(stats.total) > 75 and blurple_user_role not in ctx.author.roles and \
                    stats.percentage(stats.blurple) > 5:
                await ctx.send(
                    f"{ctx.message.author.mention}, as your profile pic has enough blurple (over 75% in total and "
                    f"over 5% blurple), you have received the role **{blurple_user_role.name}**!")
                await ctx.author.add_roles(blurple_user_role)
            elif url == ctx.author.avatar_url and blurple_user_role not in ctx.author.roles:
                await ctx.send(
                    f"{ctx.message.author.display_name}, your profile pic does not have enough blurple (over 75% in "
                    f"total and over 5% blurple), therefore you are not eligible for the role "
                    f"'{blurple_user_role.mention}'. However, this colour detecting algorithm is automated, so if you "
                    f"believe your pfp is blurple enough, please DM a Staff member and they will manually give you the "
                    f"role if it is blurple enough. (Not sure how to make a blurple logo? Head over to "
                    f"<#412755378732793868> or <#436026199664361472>!)")


@bot.command(aliases=['blurplfy', 'blurplefier', 'blurplfygif', 'blurplefiergif', 'blurplefygif'])
@commands.cooldown(rate=1, per=180, type=BucketType.user)
async def blurplefy(ctx, arg1=None):
    frames, url = await collect_image(ctx, arg1)
    if frames is None:
        return await ctx.message.add_reaction('\N{CROSS MARK}')

    if len(frames) > 1:
        gif_loop = int(frames[0].info.get('loop', 0))
        gif_duration = frames[0].info.get('duration')
    else:
        gif_loop = gif_duration = None

    def process_sequence(frames, loop, duration):
        for n, frame in enumerate(frames):
            frames[n] = blurplefy_image(frame)

        image_file_object = io.BytesIO()
        if len(frames) > 1:
            frames[0].save(image_file_object, format='gif', save_all=True, append_images=frames[1:], loop=loop,
                           duration=duration)
        else:
            frames[0].save(image_file_object, format='png')
        image_file_object.seek(0)

        return image_file_object

    image = await bot.loop.run_in_executor(None, process_sequence, frames, gif_loop, gif_duration)
    image = discord.File(fp=image, filename='blurple.png' if len(frames) == 1 else 'blurple.gif')

    try:
        embed = discord.Embed(Title="", colour=0x7289DA)
        embed.set_author(name="Blurplefier - makes your image blurple!")
        if len(frames) == 1:
            embed.set_image(url="attachment://blurple.png")
            embed.set_footer(
                text=f"Please note - This blurplefier is automated and therefore may not always give you the best "
                     f"result. | Content requested by {ctx.author}")
        else:
            embed.set_image(url="attachment://blurple.gif")
            embed.set_footer(
                text=f"Please note - This blurplefier is automated and therefore may not always give you the best "
                     f"result. Disclaimer: This image is a gif, and the quality does not always turn out great. "
                     f"HOWEVER, the gif is quite often not as grainy as it appears in the preview | Content "
                     f"requested by {ctx.author}")
        embed.set_thumbnail(url=url)
        await ctx.send(embed=embed, file=image)
    except discord.errors.DiscordException:
        await ctx.send(
            f"{ctx.author.mention}, whoops! It looks like this image is too big to upload. If you want, you can "
            f"give it another go, except with a smaller version of the image. Sorry about that!")


if __name__ == '__main__':
    bot.run(TOKEN)
