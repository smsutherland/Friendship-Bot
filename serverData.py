import discord
import time
import os

def formPairs(items):
    pairs = []
    for x in range(len(items)):
        for y in range(x+1, len(items)):
            pairs.append((items[x], items[y]))
    return pairs

class serverData:
    def __init__(self, memberList):
        self.friendshipData = {}
        self.messageHistory = []
        self.guild = memberList[0].guild
        self.lastSaveTime = time.time()
        self.commandPrefix = '/'
        
        memberListNoBots = []
        for member in memberList:
            if not member.bot:
                memberListNoBots.append(member)
            
        memberPairs = formPairs(memberListNoBots)
        for pair in memberPairs:
            self.friendshipData[pair] = [0, 0]

    async def saidSomething(self, member, channel):
        self.messageHistory.append((member, time.time(), channel.id))
        while True:
            removed = False
            for messageTime in self.messageHistory:
                if time.time() - messageTime[1] > 30:
                    self.messageHistory.remove(messageTime)
                    removed = True
                    break
            if not removed:
                break

        for prevMember in self.messageHistory:
            if prevMember[2] != channel.id:
                continue
            prevMember = prevMember[0]
            if (member, prevMember) in self.friendshipData.keys():
                pair = (member, prevMember)
                self.friendshipData[pair][1] += 1
                if self.friendshipData[pair][1] > self.friendshipData[pair][0] * 25 + 50:
                    self.friendshipData[pair][1] -= (self.friendshipData[pair][0] * 25 + 50)
                    self.friendshipData[pair][0] += 1
                    await self.sendLevelUp(member, prevMember, channel, self.friendshipData[pair][0])
            elif (prevMember, member) in self.friendshipData.keys():
                pair = (prevMember, member)
                self.friendshipData[pair][1] += 1
                if self.friendshipData[pair][1] > self.friendshipData[pair][0] * 25 + 50:
                    self.friendshipData[pair][1] -= (self.friendshipData[pair][0] * 25 + 50)
                    self.friendshipData[pair][0] += 1
                    await self.sendLevelUp(member, prevMember, channel, self.friendshipData[pair][0])

        if self.timeForSave():
            self.saveFriends()

    async def sendLevelUp(self, member1, member2, channel, level):
        levelUpMessage = ""
        levelUpMessage += member1.display_name
        levelUpMessage += " and "
        levelUpMessage += member2.display_name
        levelUpMessage += " leveled up their friendship to level "
        levelUpMessage += str(level)
        levelUpMessage += '!'
        await channel.send(levelUpMessage)

    def listFriends(self, person): 
        toReturn = ""
        for pair in self.friendshipData.keys():
            if person in pair:
                otherPerson = person
                for x in pair:
                    if not x == person:
                        otherPerson = x
                if self.friendshipData[pair][0] > 0:
                    toReturn += str(otherPerson.display_name)
                    toReturn += ": friendship level "
                    toReturn += str(self.friendshipData[pair][0])
                    toReturn += "\n"
        return toReturn

    def saveFriends(self):
        try:
            os.mkdir("fpdata")
            print(os.getcwd())
        except FileExistsError as e:
            pass
        os.chdir("fpdata")
        saveFile = open(str(self.guild.id) + ".txt", 'w')

        for ele in self.friendshipData:
            saveFile.write(str(ele[0].id))
            saveFile.write(',')
            saveFile.write(str(ele[1].id))
            saveFile.write(',')
            saveFile.write(str(self.friendshipData[ele][0]))
            saveFile.write(',')
            saveFile.write(str(self.friendshipData[ele][1]))
            saveFile.write('\n')
        saveFile.write(self.commandPrefix)
        saveFile.close()
        os.chdir("..")

    def loadFriends(self):
        try:
            os.chdir("fpdata")
            loadFile = open(str(self.guild.id) + ".txt", 'r')
            lines = loadFile.readlines()
            loadFile.close()

            for line in lines[:-1]:
                if len(line) > 0:
                    parts = line.split(',')
                    for pair in self.friendshipData:
                        if pair[0].id == int(parts[0]) or pair[1].id == int(parts[0]):
                            if pair[0].id == int(parts[1]) or pair[1].id == int(parts[1]):
                                self.friendshipData[pair][0] = int(parts[2])
                                self.friendshipData[pair][1] = int(parts[3])
            self.commandPrefix = lines[-1]

        except FileNotFoundError as e:
            pass
        if str(os.getcwd()).endswith("fpdata"):
            os.chdir("..")


    def timeForSave(self):
        return time.time() - self.lastSaveTime > 300

    async def displayFP(self, member1, member2, channel):
        pair = None
        if (member1, member2) in self.friendshipData:
            pair = (member1, member2)
        elif (member2, member1) in self.friendshipData:
            pair = (member2, member1)
        await channel.send(f"{member1.display_name} and {member2.display_name} are at friendship level {self.friendshipData[pair][0]} and have {self.friendshipData[pair][1]} fp out of {self.friendshipData[pair][0] * 25 + 50}")

    def setCommandPrefix(self, newPrefix):
        self.commandPrefix = newPrefix
