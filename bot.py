import discord
import serverData as sData

client = discord.Client()
servers = {}

@client.event
async def on_ready():
    game = discord.Game(f'say "Friendship Bot" ~ {str(len(client.guilds))} servers')
    await client.change_presence(status = discord.Status.online, activity=game)
    for currentGuild in client.guilds:
        servers[currentGuild.id] = sData.serverData(currentGuild.members)
        servers[currentGuild.id].loadFriends()
    print("Logged on as", client.user)

@client.event
async def on_disconnect():
    print("disconnected")
    for serverData in servers.values():
        serverData.saveFriends()
    

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    commandPrefix = servers[message.guild.id].commandPrefix
    if message.content == "Friendship Bot":
        await message.channel.send(f'say "{commandPrefix}help" for help')
    if message.content.strip().startswith(commandPrefix):
        command = message.content.strip()[len(commandPrefix):].strip()
        commandIndex = command.find(' ')
        if commandIndex == -1:
            commandIndex = len(command)
        arguments = command[commandIndex + 1:]
        command = command[:commandIndex].casefold()

        channel = message.channel
        sender = message.author
        guild = channel.guild
        if command == "myfriends":
            friendList = servers[guild.id].listFriends(sender)
            if friendList == "":
                friendList = "You have no friends right now.\nTalk to people to make friends with them!"
            await channel.send(friendList)
        elif command in ["fp", "friendshipwith", "friendshiplevel", "friendshippoints"]:
            if arguments == "all":
                hasFriends = False
                for member in guild.members:
                    if member != sender and member.bot == False:
                        hasFriends = True
                        await servers[guild.id].displayFP(sender, member, channel)
                if not hasFriends:
                    await channel.send("You have no friends right now.\nTalk to people to make friends with them!")
            else:
                for member in guild.members:
                    if member.bot:
                        continue
                    possibleNames = [member.display_name.casefold(), member.discriminator, str(member.id), member.name.casefold(), member.mention]
                    argumentLower = arguments.casefold()
                    if argumentLower in possibleNames and member != sender:
                        await servers[guild.id].displayFP(sender, member, channel)
                        break
                else:
                    await channel.send("There's no one with that name in the server.")
        elif command == "ping":
            await channel.send("%.2fms" % (client.latency * 1000))
        elif command == "setprefix":
            servers[guild.id].setCommandPrefix(arguments.strip())
            servers[guild.id].saveFriends()
            await channel.send(f"Command prefix changed to {arguments.strip()}")
        elif command == "help":
            if arguments == "":
                await channel.send(f"""```Command List:
For specific help about a given command, type "{commandPrefix}help [command]"
Any whitespace between the command prefix and the command itself will be ignored
    {commandPrefix}help: brings up this page
    {commandPrefix}myfriends: shows a list of your friends and their friendship level
    {commandPrefix}fp [person]: shows your friendship level and points with [person]
    {commandPrefix}setPrefix [something]: changes the prefix for commands from {commandPrefix} to [someting]```""")
            elif arguments in ["help", f"{commandPrefix}help"]:
                await channel.send(f"```{commandPrefix}help brings up the full list of commands and gives each one a brief description.```")
            elif arguments in ["myfriends", f"{commandPrefix}myfriends"]:
                await channel.send(f"```{commandPrefix}myfriends sends out a list of all people on the server that you are at at least friendship level 1 with. It displays your friendship level, but not how many friendship points you have. If there are no people in the server that you are at least level 1 friends with, /myfriends will send a message informing you of how to make friends.```")
            elif arguments in ["fp", f"{commandPrefix}fp"]:
                await channel.send(f"```{commandPrefix}fp [person] will send out your current friendship level and fp with [person] it will also inform you of how many fp you need to reach the next friendship level. In place of person, you can have a user's nickname, username, number, or mention. \"{commandPrefix}fp all\" will send the fp information for all other users in the server.```")
            elif arguments in ["setPrefix", f"{commandPrefix}setPrefix"]:
                await channel.send(f"```{commandPrefix}setPrefix [something] will change the prefix for Friendship Bot commands from the current prefix, {commandPrefix}, to [something]. Any leading or trailing whitespace around [someting] will be ignored```")
    else:
        await servers[message.guild.id].saidSomething(message.author, message.channel)


client.run("TOKEN")
