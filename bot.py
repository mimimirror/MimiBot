import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import os


scope = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
    ]
file_name = 'client_key.json'
creds = None
try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
except:
    f = open(file_name, "w")
    f.write(os.environ['CREDS'])
    f.close()
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_name, scope)
gclient = gspread.authorize(creds)

boss_red = [182, 249, 201, 234, 180]
boss_green = [215, 203, 218, 153, 167]
boss_blue = [168, 156, 248, 153, 214]
sheet_num = 4

# Some boilerplate discord bot stuff
client = discord.Client()

cb_start = None

sheet_name = "EoS Pinecone Mimi Test"
worksheet_name = "CB4"

def update_sheet(player, team, boss, damage, bonus):
    info_sheet = gclient.open(sheet_name).sheet1
    names = info_sheet.col_values(4)
    row = -1

    for i in range(len(names)):
        name = names[i]
        if "#" in name:
            name = name[:name.index("#")]
        if name == player:
            row = i + 2

    if row == -1:
        return (False, "Player " + player + " not found in sheet")

    # dmg_sheet = gclient.open(sheet_name).get_worksheet(sheet_num)
    dmg_sheet = gclient.open(sheet_name).worksheet(worksheet_name)

    day = get_day()

    col = 2 * team + 1 + 6 * (day - 1) + bonus

    cell_name = chr(64 + col%26) + str(row)
    
    if col > 26:
        cell_name = "A" + cell_name

    cell_name = cell_name + ":" + cell_name

    dmg_sheet.update_cell(row, col, str(damage))
    dmg_sheet.format(cell_name, {
        "backgroundColor": {
            "red": 256 - boss_red[boss - 1],
            "green": 256 - boss_green[boss - 1],
            "blue": 256 - boss_blue[boss - 1]
        }
    })

    return (True, "")

def get_cb_start_datetime(month, day, year):
    return datetime.datetime(year, month, day, 13, 0, 0, 0, tzinfo=datetime.timezone.utc)

def get_day():
    now = datetime.datetime.now(datetime.timezone.utc)
    diff = now - cb_start
    num_days = diff.seconds // 3600 // 24 + 1 + diff.days
    return max(1, num_days)

@client.event
async def on_ready():
    global cb_start
    cb_start = get_cb_start_datetime(5, 19, 2021)
    print("The bot is ready!")


@client.event
async def on_message(message):
    # Don't reply to your own messages
    if message.author == client.user:
        return


    elif (message.channel.name == "edms-dungeon" or message.channel.name == "cb-attack-channel"):
        #expected format: team X boss Y DAMAGE
        split_msg = message.content.split(" ")
        if len(split_msg) < 5 or split_msg[0].lower() != "team" or split_msg[2].lower() != "boss":
            return
        else:
            player = message.author.name
            try:
                team = int(split_msg[1])
                boss = int(split_msg[3])
                damage = int(split_msg[4].replace(',','').replace('.',''))
                bonus = 0
                if message.content.find("bonus") != -1:
                    bonus = 1

                if team < 1 or team > 3:
                    await message.channel.send("Team 1, 2, or 3 only please")
                    return
                if boss < 1 or boss > 5:
                    await message.channel.send("Boss 1, 2, 3, 4, or 5 only please")
                    return
            except:
                await message.channel.send("EDM keeps me locked up, but even I know that's not a real number")
                return
            success, err = update_sheet(player, team, boss, damage, bonus)
            if success:
                await message.add_reaction('<:PecoSalute:792800585636249600>')
            else:
                await message.channel.send(err)


# Stuff for hosting it
client.run(os.environ['TOKEN'])
