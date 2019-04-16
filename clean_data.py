import pandas as pd
import datetime
import re

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

data = pd.read_csv('./global_terrorism.csv')
print(data.head())

def fix_date_piece(date_piece):
    # print(date_piece)\
    if date_piece == "":
        return "January"

    if date_piece == "Unknown":
        return "1"
    parts = date_piece.split('-')
    # this is not a regular dash!!
    if "–" in date_piece:
        parts = date_piece.split('–')
    elif "/" in date_piece:
        parts = date_piece.split('/')
    return parts[0].strip()

def fix_date(row):
    date = "August 10 2000" if row.date == "August10 2000" else row.date
    if row.date == "25 1999":
        date = "February 25 1999"
    date = date.replace(",", "")
    date = date.replace("*", "")
    date = date.replace("\xa0", " ")
    date = date.replace("~", "")
    parts = date.split(' ')

    month_index = None
    if len(parts) == 2:
        parts = ["1"] + parts

    if len(parts) > 3:
        parts = parts[0:2] + [parts[-1]]

    # if parts[0] not in months and parts[1] not in months:
    #     print(parts, row.date)

    if parts[0] in months:
        date_format = "%B %d %Y"
        parts[0] = fix_date_piece(parts[0])
        parts[1] = fix_date_piece(parts[1])
        #special case
        if parts[0] == "November" and parts[1] == "31":
            parts[1] = "30"
        row.date = str(datetime.datetime.strptime(" ".join(parts[0:3]), date_format).date())
    else:
        date_format = "%d %B %Y"
        parts[0] = fix_date_piece(parts[0])
        parts[1] = fix_date_piece(parts[1])
        row.date = str(datetime.datetime.strptime(" ".join(parts[0:3]), date_format).date())

def parse_out_numbers(text):
    if not isinstance(text, str):
        return 0
    matches = re.findall("\d{0,3},\d+|\d+", text)
    if len(matches) > 1:
        sum = 0
        for match in matches:
            sum += int(match.replace(",", ""))
        return sum
    if len(matches) == 0:
        if "Dozens" in text:
            return 24
        if "Several" in text:
            return 3
        return 0

    return int(matches[0].replace(",", ""))

def fix_type(row):
    if not isinstance(row.type, str):
        row.type = "unknown"
        return
    type = row.type.lower()
    if "bomb" in type or "grenade" in type or "rocket" in type or "mortar" in type or "explosi" in type or "artillery" in type or "rpg" in type or "air" in type or "drone" in type or "missile" in type or "mine" in type:
        row.type = "bombing"
    elif "shoot" in type or "gun" in type or "sniper" in type or "shot" in type or "raid" in type or "armed" in type or "firefight" in type or "firing" in type:
        row.type = "shooting"
    elif "stab" in type or "machete" in type:
        row.type = "stabbing"
    elif "assassination" in type:
        row.type = "assassination"
    elif "massacre" in type:
        row.type = "massacre"
    elif "arson" in type:
        row.type = "arson"
    elif "kidnap" in type or "abduct" in type or "hostage" in type:
        row.type = "hostage"
    elif "bio" in type:
        row.type = "bioattack"
    elif "hijack" in type or "car" in type or "vehicle" in type:
        row.type = "hijacking"
    elif "melee" in type:
        row.type = "melee"
    elif "unknown" in type:
        row.type = "unknown"
    else:
        row.type = "other_violence"




def fix_dead_and_injured(row):
    row.dead = parse_out_numbers(row.dead)
    row.injured = parse_out_numbers(row.injured)

for i, row in data.iterrows():
    fix_date(row)
    fix_dead_and_injured(row)
    fix_type(row)

# fix_date(data.iloc[0])
print(data.head())

data.to_csv(r'./global_terrorism_clean.csv', index=None)
