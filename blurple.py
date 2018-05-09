# THIS BLOCK OF 'import' BELOW INCLUDE LIBS NOT INCLUDED IN DEFAULT PYTHON
# THESE CAN BE INSTALLED BY TYPING THE PIP INSTALLS INTO COMMAND PROMPT
# This code is copied straight from my original, therefore there are some
# little hidden unused things you might find when looking around. ;)

# https://www.python.org/downloads/ v3.6.5

from config import *

import discord
# discord.py rewrite

import asyncio

try:
    import uvloop
    loop = uvloop.new_event_loop()
except ImportError:
    loop = asyncio.get_event_loop()
# Tries to use uvloop for the event loop.

from PIL import Image, ImageEnhance, ImageSequence
import PIL
# pip install Pillow

from io import BytesIO
import io
import datetime
import aiohttp
import copy
import sys
import time

from resizeimage import resizeimage
# pip install python-resize-image

import math

bot = discord.AutoShardedClient(
    shard_count=5,
    loop=loop
)

blurple = (114, 137, 218)
bluplehex = 0x7289da
darkblurple = (78, 93, 148)
white = (255, 255, 255)

allowedusers = {204778476102877187, 226595531844091904, 191602259904167936}
# put your user id here, and it will allow you to use the 'hidden' commands
# (and shutdown command)

approved_channels = {418987056111550464, 436300339273269278}

commands = dict()


def command(
    description="No description given.",
    allowed_users_only=False,
    not_dms=True,
    command_name=None
):
    def deco(func):
        if command_name:
            n = command_name
        else:
            n = func.__name__
        func.cmd_attr = {
            "description": description,
            "allowed_users_only": allowed_users_only,
            "not_dms": not_dms
        }
        commands[n] = func
    return deco


@bot.event
async def on_connect():
    print('------')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    activity = discord.Game(name=f"Type {BOT_PREFIX}help")
    await bot.change_presence(activity=activity)


@command("Shuts down the bot.", allowed_users_only=True)
async def shutdown(message, args):
    embed = discord.Embed(
        timestamp=datetime.datetime.utcnow(),
        colour=0x7289da
    )
    embed.add_field(
        name="Shutting down<a:underscore:420740967939964928>",
        value="Blurplefied"
    )
    await message.channel.send(embed=embed)
    await bot.logout()


@command("Displays the help.")
async def help(message, args):
    embed = discord.Embed(
        timestamp=datetime.datetime.utcnow(),
        colour=0x7289da
    )
    special = message.author.id in allowedusers
    embed.set_author(name="Commands list")
    for c in commands:
        attrs = c.cmd_attr
        if not (not special and attrs["allowed_users_only"]):
            embed.add_field(
                name=BOT_PREFIX + c,
                value=attrs["description"]
            )
    embed.set_footer(text=f"Help message requested by {message.author}")
    embed.set_thumbnail(url=bot.user.avatar_url)
    await message.channel.send(embed=embed)


@command("Pings the bot.")
async def ping(message, args):
    latency = bot.latency*1000
    latency = round(latency, 2)
    embed = discord.Embed(
        colour=0x7289da,
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_author(name="Ping!")
    embed.add_field(name='Bot latency', value=f"{latency}ms")
    await message.channel.send(embed=embed)


@command("Counts down to Discord's birthday.")
async def countdown(message, args):
    def strfdelta(tdelta, fmt):
        d = {"days": tdelta.days}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)

    timeleft = (
        datetime.datetime(2018, 5, 13) + datetime.timedelta(hours=7) -
        datetime.datetime.utcnow()
    )
    embed = discord.Embed(name="", colour=0x7289da)
    embed.set_author(name="Time left until Discord's 3rd Anniversary")
    embed.add_field(
        name="Countdown to midnight May 13 California time (UTC-7)",
        value=(
            strfdelta(
                timeleft,
                "**{days}** days, **{hours}** hours, **{minutes}** minutes,"
                " and **{seconds}** seconds"
            )
        )
    )
    await message.channel.send(embed=embed)


@command("Times the execution of a command.", allowed_users_only=True)
async def timeit(message, args):
    cmd = args[0].lower()
    del args[0]

    if cmd not in commands:
        await message.channel.send(
            "Command not found."
        )
        return

    start = time.time()
    await commands[cmd](message, args)
    end = time.time()

    await message.channel.send(
        f'**{BOT_PREFIX}{cmd}** took **{end - start:.2f}s** to run'
    )


@command(
    "Checks if your profile picture is blurple enough and if so gives "
    "you a role. If you provide a image, it will check that.",
    command_name="blurple"
)
async def _blurple(message, args):
    picture = None

    await message.channel.send(
        f"{message.author.mention}, starting blurple image"
        " analysis (Please note that this may take a while)"
    )

    start = time.time()
    if len(args) > 0:
        if "<@!" in args[0]:
            arg1 = args[0][:-1]
            arg1 = arg1[3:]
        elif "<@" in arg1:
            arg1 = args[0][:-1]
            arg1 = arg1[2:]
        if args[0].isdigit():
            try:
                user = await bot.get_user_info(int(arg1))
                picture = user.avatar_url
            except Exception:
                pass
        else:
            picture = args[0]
    else:
        picture = None
        link = message.attachments
        if len(link) > 0:
            picture = link[0].url

    if not picture:
        picture = message.author.avatar_url

    try:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(picture) as r:
                response = await r.read()
    except ValueError:
        await message.channel.send(
            f"{message.author.meniton}, please link a valid image URL"
        )
        return

    colourbuffer = 20

    try:
        im = Image.open(BytesIO(response))
    except Exception:
        await message.channel.send(
            f"{message.author.mention}, please link a valid image URL"
        )
        return

    im = im.convert('RGBA')
    imsize = list(im.size)
    impixels = imsize[0]*imsize[1]
    maxpixelcount = 1562500

    if impixels > maxpixelcount:
        downsizefraction = math.sqrt(maxpixelcount/impixels)
        im = resizeimage.resize_width(im, (imsize[0]*downsizefraction))
        imsize = list(im.size)
        impixels = imsize[0]*imsize[1]
        end = time.time()
        await message.channel.send(
            f'{message.author.display_name}, image'
            f' resized smaller for easier processing ({end-start:.2f}s)'
        )
        start = time.time()

    def imager(im):
        global noofblurplepixels
        noofblurplepixels = 0
        global noofwhitepixels
        noofwhitepixels = 0
        global noofdarkblurplepixels
        noofdarkblurplepixels = 0
        global nooftotalpixels
        nooftotalpixels = 0
        global noofpixels
        noofpixels = 0

        blurple = (114, 137, 218)
        darkblurple = (78, 93, 148)
        white = (255, 255, 255)

        img = im.load()

        for x in range(imsize[0]):
            i = 1
            for y in range(imsize[1]):
                pixel = img[x, y]
                check = 1
                checkblurple = 1
                checkwhite = 1
                checkdarkblurple = 1
                for i in range(3):
                    if not(
                        blurple[i]+colourbuffer > pixel[i] >
                        blurple[i]-colourbuffer
                    ):
                        checkblurple = 0
                    if not(
                        darkblurple[i]+colourbuffer > pixel[i] >
                        darkblurple[i]-colourbuffer
                    ):
                        checkdarkblurple = 0
                    if not(
                        white[i]+colourbuffer > pixel[i] >
                        white[i]-colourbuffer
                    ):
                        checkwhite = 0
                    if (
                        checkblurple == 0 and
                        checkdarkblurple == 0 and
                        checkwhite == 0
                    ):
                        check = 0
                if check == 0:
                    img[x, y] = (0, 0, 0, 255)
                if check == 1:
                    nooftotalpixels += 1
                if checkblurple == 1:
                    noofblurplepixels += 1
                if checkdarkblurple == 1:
                    noofdarkblurplepixels += 1
                if checkwhite == 1:
                    noofwhitepixels += 1
                noofpixels += 1

        image_file_object = io.BytesIO()
        im.save(image_file_object, format='png')
        image_file_object.seek(0)
        return image_file_object

    image = discord.File(fp=(
            await bot.loop.run_in_executor(None, imager, im)
        ), filename='image.png'
    )

    blurplenesspercentage = round(((nooftotalpixels/noofpixels)*100), 2)
    percentblurple = round(((noofblurplepixels/noofpixels)*100), 2)
    percentdblurple = round(((noofdarkblurplepixels/noofpixels)*100), 2)
    percentwhite = round(((noofwhitepixels/noofpixels)*100), 2)

    blurpleuserrole = discord.utils.get(
        message.guild.roles, id=436300514561622016
    )
    embed = discord.Embed(colour=0x7289DA)
    embed.add_field(
        name="Total amount of Blurple",
        value=f"{blurplenesspercentage}%",
        inline=False
    )
    embed.add_field(
        name="Blurple (rgb(114, 137, 218))",
        value=f"{percentblurple}%",
        inline=True
    )
    embed.add_field(
        name="White (rgb(255, 255, 255))",
        value=f"{percentwhite}%",
        inline=True
    )
    embed.add_field(
        name="Dark Blurple (rgb(78, 93, 148))",
        value=f"{percentdblurple}%",
        inline=True
    )
    embed.add_field(
        name="Guide",
        value="Blurple, White, Dark Blurple = Blurple, White, and "
        "Dark Blurple (respectively) \nBlack = Not Blurple, White, "
        "or Dark Blurple",
        inline=False
    )
    embed.set_footer(
        text="Please note: Discord slightly reduces quality of the"
        " images, therefore the percentages may be slightly inaccurate."
        f" | Content requested by {message.author.mention}")
    embed.set_image(url="attachment://image.png")
    embed.set_thumbnail(url=picture)
    await message.channel.send(embed=embed, file=image)

    if (
        blurplenesspercentage > 75 and picture == message.author.avatar_url and
        blurpleuserrole not in message.author.roles and percentblurple > 5
    ):
        await message.author.send(
            f"{message.author.display_name}, as your profile picture has "
            "enough blurple (over 75% in total and over 5% blurple), you have "
            f"recieved the role **{blurpleuserrole.name}**!"
        )
        await message.author.add_roles(blurpleuserrole)
    elif (
        picture == message.author.avatar_url and
        blurpleuserrole not in message.author.roles
    ):
        await message.author.send(
            f"{message.author.display_name}, your profile "
            "pic does not have enough blurple (over 75% in"
            " total and over 5% blurple), therefore you are"
            f" not eligible for the role '{blurpleuserrole.name}'. "
            "However, this colour detecting algorithm is automated, so if you"
            " believe your pfp is blurple enough, please DM a Staff member and"
            " they will manually give you the role if it is blurple enough. "
            "(Not sure how to make a blurple logo? Head over to "
            "<#412755378732793868> or <#436026199664361472>!)"
        )


@command(
    "Allows you to blurplefy your image/GIF! Simply don't put any arguements "
    "if you want to blurplefy your profile picture or attach a file/link if "
    "you want that blurplefied!"
)
async def blurplefy(message, args):
    picture = None

    await message.channel.send(
        f"{message.author.mention}, starting blurple image analysis"
        " (Please note that this may take a while)"
    )

    if len(args) > 0:
        if "<@!" in args[0]:
            arg1 = args[0][:-1]
            arg1 = arg1[3:]
        if "<@" in arg1:
            arg1 = args[0][:-1]
            arg1 = arg1[2:]
        if args[0].isdigit():
            try:
                user = await bot.get_user_info(int(args[0]))
                picture = user.avatar_url
            except Exception:
                pass
        else:
            picture = arg1
    else:
        link = message.attachments
        if len(link) > 0:
            picture = link[0].url

    if not picture:
        picture = message.author.avatar_url

    try:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(picture) as r:
                response = await r.read()
    except ValueError:
        await message.channel.send(
            f"{message.author.display_name},"
            " please link a valid image URL."
        )
        return

    try:

        def open_image():
            return Image.open(BytesIO(response))

        im = await loop.run_in_executor(
            None, open_image
        )
    except Exception:
        await message.channel.send(
            f"{message.author.mention}, "
            "please link a valid image URL."
        )
        return

    imsize = list(im.size)
    impixels = imsize[0]*imsize[1]
    # 1250x1250 = 1562500
    maxpixelcount = 1562500

    try:
        isgif = True
        gifloop = int(im.info["loop"])
    except Exception:
        isgif = False

    if impixels > maxpixelcount:
        downsizefraction = math.sqrt(maxpixelcount/impixels)
        im = resizeimage.resize_width(im, (imsize[0]*downsizefraction))
        imsize = list(im.size)
        impixels = imsize[0]*imsize[1]

    def imager(im):
        im = im.convert(mode='L')
        im = ImageEnhance.Contrast(im).enhance(1000)
        im = im.convert(mode='RGB')

        img = im.load()

        for x in range(imsize[0]-1):
            for y in range(imsize[1]-1):
                pixel = img[x, y]

                if pixel != (255, 255, 255):
                    img[x, y] = (114, 137, 218)

        image_file_object = io.BytesIO()
        im.save(image_file_object, format='png')
        image_file_object.seek(0)
        return image_file_object

    def gifimager(im, gifloop):
        frames = [frame.copy() for frame in ImageSequence.Iterator(im)]
        newgif = []

        for frame in frames:

            frame = frame.convert(mode='L')
            frame = ImageEnhance.Contrast(frame).enhance(1000)
            frame = frame.convert(mode='RGB')

            img = frame.load()

            for x in range(imsize[0]):
                for y in range(imsize[1]):
                    pixel = img[x, y]

                    if pixel != (255, 255, 255):
                        img[x, y] = (114, 137, 218)

            newgif.append(frame)

        image_file_object = io.BytesIO()

        gif = newgif[0]
        gif.save(
            image_file_object,
            format='gif',
            save_all=True,
            append_images=newgif[1:],
            loop=0
        )

        image_file_object.seek(0)
        return image_file_object

    if not isgif:
        image = await bot.loop.run_in_executor(None, imager, im)
    else:
        image = await bot.loop.run_in_executor(
            None, gifimager, im, gifloop
        )

    if not isgif:
        image = discord.File(fp=image, filename='image.png')
    else:
        image = discord.File(fp=image, filename='image.gif')

    try:
        embed = discord.Embed(colour=0x7289DA)
        embed.set_author(name="Blurplefier - makes your image blurple!")
        if not isgif:
            embed.set_image(url="attachment://image.png")
            embed.set_footer(
                text=f"Please note - This blurplefier is "
                "automated and therefore may not always give you the best"
                f" result. | Content requested by {message.author.name}"
            )
        else:
            embed.set_image(url="attachment://image.gif")
            embed.set_footer(
                text=f"Please note - This blurplefier is "
                "automated and therefore may not always give you the best"
                " result. Disclaimer: This image is a gif, and the quality"
                " does not always turn out great. HOWEVER, the gif is quite"
                " often not as grainy as it appears in the preview | Content"
                F" requested by {message.author.name}")
        embed.set_thumbnail(url=picture)
        await message.channel.send(embed=embed, file=image)
    except Exception:
        await message.channel.send(
            f"{message.author.name}, whoops! It looks like this gif "
            "is too big to upload. If you want, you can give it another go, "
            "except with a smaller version of the image. Sorry about that!"
        )

try:
    bot.run(TOKEN)
except Exception:
    print("Whoops, bot failed to connect to Discord.")
