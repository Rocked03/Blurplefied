# THIS BLOCK OF 'import' BELOW INCLUDE LIBS NOT INCLUDED IN DEFAULT PYTHON
# THESE CAN BE INSTALLED BY TYPING THE PIP INSTALLS INTO COMMAND PROMPT
# This code is copied straight from my original, therefore there are some little hidden unused things you might find
# when looking around. ;)

# https://www.python.org/downloads/ v3.6.5

from config import *
import discord  # discord.py rewrite
# pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from PIL import Image, ImageEnhance, ImageSequence
# pip install Pillow
from io import BytesIO
import io
import datetime
import aiohttp
import copy
import time
from resizeimage import resizeimage
import numpy as np
# pip install python-resize-image
import math

description = '''Blurple Bot'''
bot = commands.Bot(command_prefix=BOT_PREFIX, description=description)

rocked = 204778476102877187

BLURPLE = (114, 137, 218, 255)
BLURPLE_HEX = 0x7289da
DARK_BLURPLE = (78, 93, 148, 255)
WHITE = (255, 255, 255, 255)

MAX_PIXEL_COUNT = 1562500

bot.remove_command('help')

# Put your user id here, and it will allow you to use the 'hidden' commands (and shutdown command)
allowed_users_list = {204778476102877187, 226595531844091904, 191602259904167936}
approved_channels = {418987056111550464, 436300339273269278}


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


@bot.command()
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

    '''tracebackerror = traceback.print_exception(type(error), error, error.__traceback__)
    await channel.send(tracebackerror)'''

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

    print(error)

    import traceback
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

    start = time.time()
    if arg1 is not None:
        if "<@!" in arg1:
            arg1 = arg1[:-1]
            arg1 = arg1[3:]
        if "<@" in arg1:
            arg1 = arg1[:-1]
            arg1 = arg1[2:]
        if arg1.isdigit():
            try:
                user = await bot.get_user_info(int(arg1))
                picture = user.avatar_url
            except Exception:
                pass
        else:
            picture = arg1
    else:
        link = ctx.message.attachments
        if len(link) != 0:
            for image in link:
                picture = image.url

    if picture is None:
        picture = ctx.author.avatar_url

    try:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(picture) as r:
                response = await r.read()
    except ValueError:
        return await ctx.message.add_reaction('\N{CROSS MARK}')

    colour_buffer = 20

    try:
        im = Image.open(BytesIO(response))
    except Exception:
        return await ctx.message.add_reaction('\N{CROSS MARK}')

    im = im.convert('RGBA')
    impixels = im.size[0] * im.size[1]

    end = time.time()
    # await ctx.send(f'{ctx.message.author.display_name}, image fetched, analysing image (This process can sometimes '
    #                f'take a while depending on the size of the image) ({end - start:.2f}s)')
    start = time.time()
    if impixels > MAX_PIXEL_COUNT:
        downsizefraction = math.sqrt(MAX_PIXEL_COUNT / impixels)
        im = resizeimage.resize_width(im, (im.size[0] * downsizefraction))
        await ctx.send(
            f'{ctx.message.author.display_name}, image resized smaller for easier processing ({end-start:.2f}s)')

    def scan_blurple(im):
        arr = np.asarray(im).copy()

        no_dark = np.all(np.abs(arr - DARK_BLURPLE) < colour_buffer, axis=2).sum()
        no_blurple = np.all(np.abs(arr - BLURPLE) < colour_buffer, axis=2).sum()
        no_white = np.all(np.abs(arr - WHITE) < colour_buffer, axis=2).sum()
        no_total = no_dark + no_blurple + no_white
        no_pixels = im.size[0] * im.size[1]

        mask = np.logical_and(np.abs(arr - DARK_BLURPLE) >= colour_buffer,
                              np.abs(arr - BLURPLE) >= colour_buffer,
                              np.abs(arr - WHITE) >= colour_buffer)
        mask = np.all(mask, axis=2)

        arr[mask] = (0, 0, 0, 255)

        image_file_object = io.BytesIO()
        Image.fromarray(np.uint8(arr)).save(image_file_object, format='png')
        image_file_object.seek(0)
        return image_file_object, no_dark, no_white, no_blurple, no_pixels, no_total

    # start = time.time()
    image, no_dark, no_white, no_blurple, no_pixels, no_total = await bot.loop.run_in_executor(None, scan_blurple,
                                                                                               im)
    # end = time.time()
    # await ctx.send(f"{ctx.author.display_name}, image data extracted ({end - start:.2f}s)")
    image = discord.File(fp=image, filename='image.png')

    blurpleness_percentage = round(((no_total / no_pixels) * 100), 2)
    percent_blurple = round(((no_blurple / no_pixels) * 100), 2)
    percentd_blurple = round(((no_dark / no_pixels) * 100), 2)
    percent_white = round(((no_white / no_pixels) * 100), 2)

    blurple_user_role = discord.utils.get(ctx.message.guild.roles, id=436300514561622016)
    embed = discord.Embed(Title="", colour=0x7289DA)
    embed.add_field(name="Total amount of Blurple", value=f"{blurpleness_percentage}%", inline=False)
    embed.add_field(name="Blurple (rgb(114, 137, 218))", value=f"{percent_blurple}%", inline=True)
    embed.add_field(name="White (rgb(255, 255, 255))", value=f"{percent_white}\%", inline=True)
    embed.add_field(name="Dark Blurple (rgb(78, 93, 148))", value=f"{percentd_blurple}\%", inline=True)
    embed.add_field(name="Guide",
                    value="Blurple, White, Dark Blurple = Blurple, White, and Dark Blurple (respectively) \nBlack = Not Blurple, White, or Dark Blurple",
                    inline=False)
    embed.set_footer(
        text=f"Please note: Discord slightly reduces quality of the images, therefore the percentages may be slightly inaccurate. | Content requested by {ctx.author}")
    embed.set_image(url="attachment://image.png")
    embed.set_thumbnail(url=picture)
    await ctx.send(embed=embed, file=image)

    if blurple_user_role is not None:
        if blurpleness_percentage > 75 and picture == ctx.author.avatar_url and \
                blurple_user_role not in ctx.author.roles and percent_blurple > 5:
            await ctx.send(
                f"{ctx.message.author.display_name}, as your profile pic has enough blurple (over 75% in total and over 5% blurple), you have recieved the role **{blurple_user_role.name}**!")
            await ctx.author.add_roles(blurple_user_role)
        elif picture == ctx.author.avatar_url and blurple_user_role not in ctx.author.roles:
            await ctx.send(
                f"{ctx.message.author.display_name}, your profile pic does not have enough blurple (over 75% in total and over 5% blurple), therefore you are not eligible for the role '{blurple_user_role.name}'. However, this colour detecting algorithm is automated, so if you believe your pfp is blurple enough, please DM a Staff member and they will manually give you the role if it is blurple enough. (Not sure how to make a blurple logo? Head over to <#412755378732793868> or <#436026199664361472>!)")


@bot.command(aliases=['blurplfy', 'blurplefier'])
@commands.cooldown(rate=1, per=180, type=BucketType.user)
async def blurplefy(ctx, arg1=None):
    picture = None

    start = time.time()
    if arg1 is not None:
        if "<@!" in arg1:
            arg1 = arg1[:-1]
            arg1 = arg1[3:]
        if "<@" in arg1:
            arg1 = arg1[:-1]
            arg1 = arg1[2:]
        if arg1.isdigit():
            try:
                user = await bot.get_user_info(int(arg1))
                picture = user.avatar_url
            except Exception:
                pass
        else:
            picture = arg1
    else:
        link = ctx.message.attachments
        if len(link) != 0:
            for image in link:
                picture = image.url

    if picture is None:
        picture = ctx.author.avatar_url

    try:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(picture) as r:
                response = await r.read()
    except ValueError:
        return await ctx.message.add_reaction('\N{CROSS MARK}')

    colourbuffer = 20

    try:
        im = Image.open(BytesIO(response))
    except Exception:
        return await ctx.message.add_reaction('\N{CROSS MARK}')

    try:
        i = im.info["version"]
        is_gif = True
        gif_loop = int(im.info["loop"])
    except Exception:
        is_gif = False
        gif_loop = None

    # end = time.time()
    # await ctx.send(f'{ctx.message.author.display_name}, image fetched, analysing image (This process can sometimes '
    #                f'take a while depending on the size of the image) ({end - start:.2f}s)')
    # start = time.time()
    if im.size[0] * im.size[1] > MAX_PIXEL_COUNT:
        downsizefraction = math.sqrt(MAX_PIXEL_COUNT / (im.size[0] * im.size[1]))
        im = resizeimage.resize_width(im, (im.size[0] * downsizefraction))
        # end = time.time()
        # await ctx.send(f'{ctx.message.author.display_name}, image resized smaller for easier processing '
        #                f'({end-start:.2f}s)')
        # start = time.time()

    def imager(im):
        im = im.convert(mode='L')
        im = ImageEnhance.Contrast(im).enhance(1000)
        im = im.convert(mode='RGB')

        arr = np.asarray(im).copy()
        arr[np.any(arr != 255, axis=2)] = BLURPLE[:-1]

        image_file_object = io.BytesIO()
        Image.fromarray(np.uint8(arr)).save(image_file_object, format='png')
        image_file_object.seek(0)
        return image_file_object

    def gifimager(im, gifloop):
        frames = [frame.copy() for frame in ImageSequence.Iterator(im)]
        newgif = []

        for frame in frames:
            frame = frame.convert(mode='L')
            frame = ImageEnhance.Contrast(frame).enhance(1000)
            frame = frame.convert(mode='RGB')

            arr = np.asarray(frame).copy()
            arr[np.any(arr != 255, axis=2)] = BLURPLE[:-1]

            newgif.append(Image.fromarray(np.uint8(arr)))

        image_file_object = io.BytesIO()

        gif = newgif[0]
        gif.save(image_file_object, format='gif', save_all=True, append_images=newgif[1:], loop=0)

        image_file_object.seek(0)
        return image_file_object

    # start = time.time()
    if not is_gif:
        image = await bot.loop.run_in_executor(None, imager, im)
    else:
        image = await bot.loop.run_in_executor(None, gifimager, im, gif_loop)
    # end = time.time()
    # await ctx.send(f"{ctx.author.display_name}, image data extracted ({end - start:.2f}s)")
    if not is_gif:
        image = discord.File(fp=image, filename='image.png')
    else:
        image = discord.File(fp=image, filename='image.gif')

    try:
        embed = discord.Embed(Title="", colour=0x7289DA)
        embed.set_author(name="Blurplefier - makes your image blurple!")
        if not is_gif:
            embed.set_image(url="attachment://image.png")
            embed.set_footer(
                text=f"Please note - This blurplefier is automated and therefore may not always give you the best"
                     f"result. | Content requested by {ctx.author}")
        else:
            embed.set_image(url="attachment://image.gif")
            embed.set_footer(
                text=f"Please note - This blurplefier is automated and therefore may not always give you the best"
                     f"result. Disclaimer: This image is a gif, and the quality does not always turn out great."
                     f"HOWEVER, the gif is quite often not as grainy as it appears in the preview | Content"
                     f"requested by {ctx.author}")
        embed.set_thumbnail(url=picture)
        await ctx.send(embed=embed, file=image)
    except Exception:
        await ctx.send(
            f"{ctx.author.display.name}, whoops! It looks like this gif is too big to upload. If you want, you can"
            f"give it another go, except with a smaller version of the image. Sorry about that!")


@bot.command(aliases=['blurplfygif', 'blurplefiergif'])
@commands.cooldown(rate=1, per=90, type=BucketType.user)
@allowed_users()
async def blurplefygif(ctx, arg1=None):
    picture = None

    start = time.time()
    if arg1 != None:
        if "<@!" in arg1:
            arg1 = arg1[:-1]
            arg1 = arg1[3:]
        if "<@" in arg1:
            arg1 = arg1[:-1]
            arg1 = arg1[2:]
        if arg1.isdigit() == True:
            try:
                user = await bot.get_user_info(int(arg1))
                picture = user.avatar_url
            except Exception:
                return await ctx.message.add_reaction('\N{CROSS MARK}')
        else:
            picture = arg1
    else:
        link = ctx.message.attachments
        if len(link) != 0:
            for image in link:
                picture = image.url

    if picture is None:
        picture = ctx.author.avatar_url

    try:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(picture) as r:
                response = await r.read()
    except ValueError:
        return await ctx.message.add_reaction('\N{CROSS MARK}')

    colourbuffer = 20

    try:
        im = Image.open(BytesIO(response))
    except Exception:
        return await ctx.message.add_reaction('\N{CROSS MARK}')

    if im.format != 'GIF':
        return await ctx.message.add_reaction('\N{CROSS MARK}')

    imsize = list(im.size)
    impixels = imsize[0] * imsize[1]

    maxpixelcount = 1562500

    end = time.time()
    await ctx.send(f'{ctx.message.author.display_name}, image fetched, analysing image (This process can sometimes take'
                   f'a while depending on the size of the image) ({end - start:.2f}s)')
    start = time.time()
    if impixels > maxpixelcount:
        downsizefraction = math.sqrt(maxpixelcount / impixels)
        im = resizeimage.resize_width(im, (imsize[0] * downsizefraction))
        imsize = list(im.size)
        impixels = imsize[0] * imsize[1]
        end = time.time()
        await ctx.send(
            f'{ctx.message.author.display_name}, image resized smaller for easier processing ({end-start:.2f}s)')
        start = time.time()

    def imager(im):
        frames = [frame.copy() for frame in ImageSequence.Iterator(im)]
        newgif = []

        for frame in frames:
            frame = frame.convert(mode='L')
            frame = ImageEnhance.Contrast(frame).enhance(1000)
            frame = frame.convert(mode='RGB')

            arr = np.asarray(frame).copy()
            arr[np.any(arr != 255, axis=2)] = BLURPLE[:-1]

            newgif.append(Image.fromarray(np.uint8(arr)))

        image_file_object = io.BytesIO()

        gif = newgif[0]
        gif.save(image_file_object, format='gif', save_all=True, append_images=newgif[1:], loop=0)

        image_file_object.seek(0)
        return image_file_object

    # start = time.time()
    image = await bot.loop.run_in_executor(None, imager, im)
    # end = time.time()
    # await ctx.send(f"{ctx.author.display_name}, image data extracted ({end - start:.2f}s)")
    image = discord.File(fp=image, filename='image.gif')

    embed = discord.Embed(Title="", colour=0x7289DA)
    embed.set_author(name="Blurplefier - makes your image blurple!")
    embed.set_footer(
        text=f"Please note - This blurplefier is automated and therefore may not always give you the best result. This also currently does not work with gifs. | Content requested by {ctx.author}")
    embed.set_image(url="attachment://image.gif")
    embed.set_thumbnail(url=picture)
    await ctx.send(embed=embed, file=image)


try:
    bot.run(TOKEN)
except Exception:
    print("Whoops, bot failed to connect to Discord.")
