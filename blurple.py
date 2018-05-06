# THIS BLOCK OF 'import' BELOW INCLUDE LIBS NOT INCLUDED IN DEFAULT PYTHON
# THESE CAN BE INSTALLED BY TYPING THE PIP INSTALLS INTO COMMAND PROMPT
# This code is copied straight from my original, therefore there are some little hidden unused things you might find when looking around. ;)



# https://www.python.org/downloads/ v3.6.5

from config import *
import discord # discord.py rewrite
# pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import asyncio
from PIL import Image, ImageEnhance, ImageSequence
import PIL
#pip install Pillow
from io import BytesIO
import io
import datetime
import aiohttp
import copy
import sys
import time
from resizeimage import resizeimage
#pip install python-resize-image
import math

description = '''Blurple Bot'''
bot = commands.Bot(command_prefix=BOT_PREFIX, description=description)

rocked = 204778476102877187

blurple = (114, 137, 218)
bluplehex = 0x7289da
darkblurple = (78, 93, 148)
white = (255, 255, 255)

bot.remove_command('help')

allowedusers = {204778476102877187, 226595531844091904, 191602259904167936} #put your user id here, and it will allow you to use the 'hidden' commands (and shutdown command)
approved_channels = {418987056111550464, 436300339273269278}

def allowed_users():
    async def pred(ctx):
        return ctx.author.id in allowedusers
    return commands.check(pred)

@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None

@bot.check
async def only_in_commands_channels(ctx):
    return ctx.channel.id in approved_channels or ctx.author.id in allowedusers

@bot.event
async def on_connect():
    print('------')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    activity = discord.Game(name="Type "+BOT_PREFIX+"help")
    await bot.change_presence(activity=activity)

@bot.command(name='shutdown', aliases=["reboot"])
@allowed_users()
async def shutdown(ctx):
    embed=discord.Embed(title="", timestamp=datetime.datetime.utcnow(), colour=0x7289da)
    embed.add_field(name="Shutting down<a:underscore:420740967939964928>", value="Blurplefied")
    await ctx.send(embed=embed)
    await bot.logout()

@bot.command()
async def help(ctx):
    embed=discord.Embed(title="", timestamp=datetime.datetime.utcnow(), colour=0x7289da)
    embed.set_author(name="Commands list")
    embed.add_field(name="Countdown", value=f"Time until Discord's Anniversary. \n**Usage:**\n`{BOT_PREFIX}countdown`")
    embed.add_field(name="Blurple", value=f"Check how much blurple is in an image. If used without a picture, it analyses your own profile picture, and if it has enough blurple, you will receive a role. \n**Usage:**\n`{BOT_PREFIX}blurple <@username/user ID/picture url/None/uploaded image>`")
    embed.add_field(name="Blurplefy", value=f"Blurplefy your image/gif! \n**Usage:**\n`{BOT_PREFIX}blurplefy <@username/user ID/picture url/None/uploaded image>`")
    embed.set_footer(text=f"Help message requested by {ctx.message.author}")
    embed.set_thumbnail(url=bot.user.avatar_url)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    latency=bot.latency*1000
    latency=round(latency,2)
    latency=str(latency)
    embed=discord.Embed(title="", colour=0x7289da, timestamp=datetime.datetime.utcnow())
    embed.set_author(name="Ping!")
    embed.add_field(name='Bot latency', value=latency+"ms")
    await ctx.send(embed=embed)

@bot.command()
async def countdown(ctx):
    def strfdelta(tdelta, fmt):
        d = {"days": tdelta.days}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)

    timeleft = datetime.datetime(2018, 5, 13) + datetime.timedelta(hours=7) - datetime.datetime.utcnow()
    embed = discord.Embed(name="", colour=0x7289da)
    embed.set_author(name="Time left until Discord's 3rd Anniversary")
    embed.add_field(name="Countdown to midnight May 13 California time (UTC-7)", value=(strfdelta(timeleft, "**{days}** days, **{hours}** hours, **{minutes}** minutes, and **{seconds}** seconds")))
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    channel = bot.get_channel(436790039750508544)
    #ignored = (commands.CommandNotFound, commands.UserInputError)
    ignored = (commands.CommandNotFound)
    if isinstance(error, ignored):
        return

    '''tracebackerror = traceback.print_exception(type(error), error, error.__traceback__)
    await channel.send(tracebackerror)'''

    if isinstance(error, commands.CommandOnCooldown):
        if int(ctx.message.author.id) in allowedusers:
            await ctx.reinvoke()
            return
        else:
            msg = await ctx.send(f"{ctx.author.mention}, please slow down! The command `{BOT_PREFIX}{ctx.command}` has {round(error.retry_after, 1)}s left of cooldown.")
            #await asyncio.sleep(5)
            #await msg.delete()
            #await ctx.message.delete()
            return

    print(error)

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
async def blurple(ctx, arg1 = None):
    picture = None

    await ctx.send(f"{ctx.message.author.mention}, starting blurple image analysis (Please note that this may take a while)")


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
                pass
        else:
            picture = arg1
    else:
        link = ctx.message.attachments
        if len(link) != 0:
            for image in link:
                picture = image.url

    if picture == None:
        picture = ctx.author.avatar_url

    try:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(picture) as r:
                response = await r.read()
    except ValueError:
        await ctx.send(f"{ctx.author.display_name}, please link a valid image URL")
        return

    colourbuffer = 20

    try:
        im = Image.open(BytesIO(response))
    except Exception:
        await ctx.send(f"{ctx.author.display_name}, please link a valid image URL")
        return

    im = im.convert('RGBA')
    imsize = list(im.size)
    impixels = imsize[0]*imsize[1]
    #1250x1250 = 1562500
    maxpixelcount = 1562500

    end = time.time()
    #await ctx.send(f'{ctx.message.author.display_name}, image fetched, analysing image (This process can sometimes take a while depending on the size of the image) ({end - start:.2f}s)')
    start = time.time()
    if impixels > maxpixelcount:
        downsizefraction = math.sqrt(maxpixelcount/impixels)
        im = resizeimage.resize_width(im, (imsize[0]*downsizefraction))
        imsize = list(im.size)
        impixels = imsize[0]*imsize[1]
        end = time.time()
        await ctx.send(f'{ctx.message.author.display_name}, image resized smaller for easier processing ({end-start:.2f}s)')
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
                pixel = img[x,y]
                check = 1
                checkblurple = 1
                checkwhite = 1
                checkdarkblurple = 1
                for i in range(3):
                    if not(blurple[i]+colourbuffer > pixel[i] > blurple[i]-colourbuffer):
                        checkblurple = 0
                    if not(darkblurple[i]+colourbuffer > pixel[i] > darkblurple[i]-colourbuffer):
                        checkdarkblurple = 0
                    if not(white[i]+colourbuffer > pixel[i] > white[i]-colourbuffer):
                        checkwhite = 0
                    if checkblurple == 0 and checkdarkblurple == 0 and checkwhite == 0:
                        check = 0
                if check == 0:
                    img[x,y] = (0, 0, 0, 255)
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

    with aiohttp.ClientSession() as session:
        start = time.time()
        image = await bot.loop.run_in_executor(None, imager, im)
        end = time.time()
        #await ctx.send(f"{ctx.author.display_name}, image data extracted ({end - start:.2f}s)")
        image = discord.File(fp=image, filename='image.png')

        blurplenesspercentage = round(((nooftotalpixels/noofpixels)*100), 2)
        percentblurple = round(((noofblurplepixels/noofpixels)*100), 2)
        percentdblurple = round(((noofdarkblurplepixels/noofpixels)*100), 2)
        percentwhite = round(((noofwhitepixels/noofpixels)*100), 2)

        blurpleuserrole = discord.utils.get(ctx.message.guild.roles, id=436300514561622016)
        embed = discord.Embed(Title = "", colour = 0x7289DA)
        embed.add_field(name="Total amount of Blurple", value=f"{blurplenesspercentage}%", inline=False)
        embed.add_field(name="Blurple (rgb(114, 137, 218))", value=f"{percentblurple}%", inline=True)
        embed.add_field(name="White (rgb(255, 255, 255))", value=f"{percentwhite}\%", inline=True)
        embed.add_field(name="Dark Blurple (rgb(78, 93, 148))", value=f"{percentdblurple}\%", inline=True)
        embed.add_field(name="Guide", value="Blurple, White, Dark Blurple = Blurple, White, and Dark Blurple (respectively) \nBlack = Not Blurple, White, or Dark Blurple", inline=False)
        embed.set_footer(text=f"Please note: Discord slightly reduces quality of the images, therefore the percentages may be slightly inaccurate. | Content requested by {ctx.author}")
        embed.set_image(url="attachment://image.png")
        embed.set_thumbnail(url=picture)
        await ctx.send(embed=embed, file=image)

        if blurplenesspercentage > 75 and picture == ctx.author.avatar_url and blurpleuserrole not in ctx.author.roles and percentblurple > 5:
            await ctx.send(f"{ctx.message.author.display_name}, as your profile pic has enough blurple (over 75% in total and over 5% blurple), you have recieved the role **{blurpleuserrole.name}**!")
            await ctx.author.add_roles(blurpleuserrole)
        elif picture == ctx.author.avatar_url and blurpleuserrole not in ctx.author.roles:
            await ctx.send(f"{ctx.message.author.display_name}, your profile pic does not have enough blurple (over 75% in total and over 5% blurple), therefore you are not eligible for the role '{blurpleuserrole.name}'. However, this colour detecting algorithm is automated, so if you believe your pfp is blurple enough, please DM a Staff member and they will manually give you the role if it is blurple enough. (Not sure how to make a blurple logo? Head over to <#412755378732793868> or <#436026199664361472>!)")

@bot.command(aliases=['blurplfy', 'blurplefier'])
@commands.cooldown(rate=1, per=180, type=BucketType.user)
async def blurplefy(ctx, arg1 = None):
    picture = None

    await ctx.send(f"{ctx.message.author.mention}, starting blurple image analysis (Please note that this may take a while)")


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
                pass
        else:
            picture = arg1
    else:
        link = ctx.message.attachments
        if len(link) != 0:
            for image in link:
                picture = image.url

    if picture == None:
        picture = ctx.author.avatar_url

    try:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(picture) as r:
                response = await r.read()
    except ValueError:
        await ctx.send(f"{ctx.author.display_name}, please link a valid image URL")
        return

    colourbuffer = 20

    try:
        im = Image.open(BytesIO(response))
    except Exception:
        await ctx.send(f"{ctx.author.display_name}, please link a valid image URL")
        return

    imsize = list(im.size)
    impixels = imsize[0]*imsize[1]
    #1250x1250 = 1562500
    maxpixelcount = 1562500

    try:
        i = im.info["version"]
        isgif = True
        gifloop = int(im.info["loop"])
    except Exception:
        isgif = False


    

    end = time.time()
    #await ctx.send(f'{ctx.message.author.display_name}, image fetched, analysing image (This process can sometimes take a while depending on the size of the image) ({end - start:.2f}s)')
    start = time.time()
    if impixels > maxpixelcount:
        downsizefraction = math.sqrt(maxpixelcount/impixels)
        im = resizeimage.resize_width(im, (imsize[0]*downsizefraction))
        imsize = list(im.size)
        impixels = imsize[0]*imsize[1]
        end = time.time()
        #await ctx.send(f'{ctx.message.author.display_name}, image resized smaller for easier processing ({end-start:.2f}s)')
        start = time.time()

    def imager(im):
        im = im.convert(mode='L')
        im = ImageEnhance.Contrast(im).enhance(1000)
        im = im.convert(mode='RGB')

        img = im.load()

        for x in range(imsize[0]-1):
            i = 1
            for y in range(imsize[1]-1):
                pixel = img[x,y]

                if pixel != (255, 255, 255):
                    img[x,y] = (114, 137, 218)

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
                i = 1
                for y in range(imsize[1]):
                    pixel = img[x,y]

                    if pixel != (255, 255, 255):
                        img[x,y] = (114, 137, 218)

            newgif.append(frame)

        image_file_object = io.BytesIO()

        gif = newgif[0]
        gif.save(image_file_object, format='gif', save_all=True, append_images=newgif[1:], loop=0)

        image_file_object.seek(0)
        return image_file_object


    with aiohttp.ClientSession() as session:
        start = time.time()
        if isgif == False:
            image = await bot.loop.run_in_executor(None, imager, im)
        else:
            image = await bot.loop.run_in_executor(None, gifimager, im, gifloop)
        end = time.time()
        #await ctx.send(f"{ctx.author.display_name}, image data extracted ({end - start:.2f}s)")
        if isgif == False:
            image = discord.File(fp=image, filename='image.png')
        else:
            image = discord.File(fp=image, filename='image.gif')

        try:
            embed = discord.Embed(Title = "", colour = 0x7289DA)
            embed.set_author(name="Blurplefier - makes your image blurple!")
            if isgif == False:
                embed.set_image(url="attachment://image.png")
                embed.set_footer(text=f"Please note - This blurplefier is automated and therefore may not always give you the best result. | Content requested by {ctx.author}")
            else:
                embed.set_image(url="attachment://image.gif")
                embed.set_footer(text=f"Please note - This blurplefier is automated and therefore may not always give you the best result. Disclaimer: This image is a gif, and the quality does not always turn out great. HOWEVER, the gif is quite often not as grainy as it appears in the preview | Content requested by {ctx.author}")
            embed.set_thumbnail(url=picture)
            await ctx.send(embed=embed, file=image)
        except Exception:
            await ctx.send(f"{ctx.author.display.name}, whoops! It looks like this gif is too big to upload. If you want, you can give it another go, except with a smaller version of the image. Sorry about that!")

@bot.command(aliases=['blurplfygif', 'blurplefiergif'])
@commands.cooldown(rate=1, per=90, type=BucketType.user)
@allowed_users()
async def blurplefygif(ctx, arg1 = None):
    picture = None

    await ctx.send(f"{ctx.message.author.mention}, starting blurple image analysis (Please note that this may take a while)")


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
                await ctx.send("Please send a valid user mention/ID")
        else:
            picture = arg1
    else:
        link = ctx.message.attachments
        if len(link) != 0:
            for image in link:
                picture = image.url

    if picture == None:
        picture = ctx.author.avatar_url

    try:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(picture) as r:
                response = await r.read()
    except ValueError:
        await ctx.send(f"{ctx.author.display_name}, please link a valid image URL")
        return

    colourbuffer = 20

    try:
        im = Image.open(BytesIO(response))
    except Exception:
        await ctx.send(f"{ctx.author.display_name}, please link a valid image URL")
        return

    if im.format != 'GIF':
        return

    imsize = list(im.size)
    impixels = imsize[0]*imsize[1]

    maxpixelcount = 1562500

    end = time.time()
    await ctx.send(f'{ctx.message.author.display_name}, image fetched, analysing image (This process can sometimes take a while depending on the size of the image) ({end - start:.2f}s)')
    start = time.time()
    if impixels > maxpixelcount:
        downsizefraction = math.sqrt(maxpixelcount/impixels)
        im = resizeimage.resize_width(im, (imsize[0]*downsizefraction))
        imsize = list(im.size)
        impixels = imsize[0]*imsize[1]
        end = time.time()
        await ctx.send(f'{ctx.message.author.display_name}, image resized smaller for easier processing ({end-start:.2f}s)')
        start = time.time()

    def imager(im):
        frames = [frame.copy() for frame in ImageSequence.Iterator(im)]
        newgif = []

        for frame in frames:

            frame = frame.convert(mode='L')
            frame = ImageEnhance.Contrast(frame).enhance(1000)
            frame = frame.convert(mode='RGB')

            img = frame.load()

            for x in range(imsize[0]):
                i = 1
                for y in range(imsize[1]):
                    pixel = img[x,y]

                    if pixel != (255, 255, 255):
                        img[x,y] = (114, 137, 218)

            newgif.append(frame)

        image_file_object = io.BytesIO()

        gif = newgif[0]
        gif.save(image_file_object, format='gif', save_all=True, append_images=newgif[1:], loop=0)

        image_file_object.seek(0)
        return image_file_object

    with aiohttp.ClientSession() as session:
        start = time.time()
        image = await bot.loop.run_in_executor(None, imager, im)
        end = time.time()
        await ctx.send(f"{ctx.author.display_name}, image data extracted ({end - start:.2f}s)")
        image = discord.File(fp=image, filename='image.gif')


        embed = discord.Embed(Title = "", colour = 0x7289DA)
        embed.set_author(name="Blurplefier - makes your image blurple!")
        embed.set_footer(text=f"Please note - This blurplefier is automated and therefore may not always give you the best result. This also currently does not work with gifs. | Content requested by {ctx.author}")
        embed.set_image(url="attachment://image.gif")
        embed.set_thumbnail(url=picture)
        await ctx.send(embed=embed, file=image)

'''@bot.command(name='color', aliases=["colour"])
async def color(ctx, *arg1):
    link = ctx.message.attachments
    if len(link) != 0:
        for image in link:
            picture = image.url
    else:
        await ctx.send("Please upload an image")
        return

    if len(arg1) != 3:
        await ctx.send("Please specify an RGB code in the format `(R, G, B)` (eg `(114, 137, 218)`)")
        return

    try:
        arg1 = list(arg1)
        for i in range(3):
            arg1[i] = int(arg1[i])
        arg1 = tuple(arg1)
    except ValueError:
        await ctx.send("Please specify an RGB code in the format `(R, G, B)` (eg `(114, 137, 218)`)")

    colourbuffer = 20
    nooftotalpixels = 0
    noofpixels = 0

    await ctx.send("Fetching image...")

    async with aiohttp.ClientSession() as cs:
        async with cs.get(picture) as r:
            response = await r.read()

    blurple = (114, 137, 218)
    darkblurple = (78, 93, 148)
    white = (255, 255, 255)

    colourbuffer = 20

    try:
        im = Image.open(BytesIO(response))
    except Exception:
        await ctx.send("Something went wrong, please try again")
        return

    await ctx.send("Analysing image...")

    def imager(image_bytes, im):
        response = requests.get(picture)
        im = Image.open(BytesIO(response.content))
        im = im.convert('RGBA')
        imsize = list(im.size)
        img = im.load()

        for x in range(imsize[0]-1):
            i = 1
            for y in range(imsize[1]-1):
                pixel = img[x,y]
                check = 1
                for i in range(3):
                    if not(int(arg1[i])+colourbuffer > pixel[i] > int(arg1[i])-colourbuffer):
                        check = 0
                if check == 0:
                    img[x,y] = (0, 0, 0, 255)
                else:
                    img[x,y] = (255, 255, 255, 255)

        image_file_object = io.BytesIO()
        im.save(image_file_object, format='png')
        image_file_object.seek(0)
        return image_file_object

    response = requests.get(picture)
    im = Image.open(BytesIO(response.content))
    im = im.convert('RGBA')
    imsize = list(im.size)
    img = im.load()

    for x in range(imsize[0]-1):
        i = 1
        for y in range(imsize[1]-1):
            pixel = img[x,y]
            check = 1
            for i in range(3):
                if not(int(arg1[i])+colourbuffer > pixel[i] > int(arg1[i])-colourbuffer):
                    check = 0
            if check == 1:
                nooftotalpixels += 1
            noofpixels += 1

    colorpercentage = round(((nooftotalpixels/noofpixels)*100), 2)

    avatar_url = ctx.message.author.avatar_url
    with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as resp:
            avy_bytes = io.BytesIO(await resp.read())
            image = await bot.loop.run_in_executor(None, imager, avy_bytes, im)
            await ctx.send("Image formed...")
            image = discord.File(fp=image, filename='image.png')

            embed = discord.Embed(Title = "", colour = 0x7289DA)
            embed.add_field(name=f"Total amount of RGB{arg1} in the below image", value=f"{colorpercentage}%", inline=False)
            embed.add_field(name="Guide", value=f"White = Pixels with the colour RGB{arg1} \nBlack = All other pixels")
            embed.set_image(url="attachment://image.png")
            embed.set_thumbnail(url=picture)
            await ctx.send(embed=embed, file=image)'''

'''@bot.command(hidden=True)
async def colortest(ctx):
    link = ctx.message.attachments
    for image in link:
        picture = image.url

    blurple = (114, 137, 218)
    darkgrey = (54, 57, 62)
    colourbuffer = 20
    await ctx.send("Analysing image...")

    def imager(image_bytes):

        response = requests.get(picture)
        im = Image.open(BytesIO(response.content))
        imsize = list(im.size)
        img = im.load()

        for x in range(imsize[0]-1):
            i = 1
            for y in range(imsize[1]-1):
                pixel = img[x,y]
                check = 1
                for i in range(3):
                    if not(blurple[i]+colourbuffer > pixel[i] > blurple[i]-colourbuffer):
                        check = 0
                if check == 0:
                    img[x,y] = (0, 0, 0, 255)
                #else:
                    #img[x,y] = (255, 255, 255, 255)

        image_file_object = io.BytesIO()
        im.save(image_file_object, format='png')
        image_file_object.seek(0)
        return image_file_object

    avatar_url = ctx.message.author.avatar_url
    with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as resp:
            avy_bytes = io.BytesIO(await resp.read())
            image = await bot.loop.run_in_executor(None, imager, avy_bytes)
            image = discord.File(fp=image, filename='image.png')
            await ctx.send(file=image)'''

try:
    bot.run(TOKEN)
except Exception:
    print("Whoops, bot failed to connect to Discord.")