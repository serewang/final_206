from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import json
import sqlite3
import matplotlib
import matplotlib.pyplot as plt

# Sets up and returns a list of tuples for card info to later insert into the database. Takes nothing as input.
def cards():
    r = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php")
    jsonfile = r.json()
    idList = []
    nameList = []
    typeList = []
    raceList = []
    for i in jsonfile["data"]:
        idList.append(i['id'])
        nameList.append(i['name'])
        typeList.append(i['type'])
        raceList.append(i['race'])
    x = 0
    tuplist = []
    for x in range(len(idList)):
        tuplist.append((x, idList[x], nameList[x], typeList[x], raceList[x]))
        x += 1
    return tuplist


#A function to set up the database where all the information will be stored in. Takes the db_name as input and returns cur, conn.
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

#Sets overall database, takes the card data from cards() function and returns nothing.
def setDB(yugioh, cur, conn):
    # cur.execute("DROP TABLE IF EXISTS Yugioh")
    cur.execute("CREATE TABLE IF NOT EXISTS Yugioh (id INTEGER PRIMARY KEY, unique_id NUMBER, name text, type_id number, race_id INTEGER)")
    cur.execute('SELECT id FROM Yugioh WHERE id  = (SELECT MAX(id) FROM Yugioh)')
    start = cur.fetchone()
    if (start!=None):
        start = start[0] + 1
    else:
        start = 0
    for x in yugioh[start:start+25]:
        id = x[0]
        unique_id = x[1]
        name = x[2]
        cur.execute('SELECT Races.id, Races.race, Types.id, Types.type FROM Races, Types') #Using an index for races to save storage
        ids = cur.fetchall()
        for i in ids:
            if i[1] == x[4]:
                race_id = i[0]
                if i[3] == x[3]:
                    type_id = i[2]
                    cur.execute("INSERT or IGNORE INTO Yugioh (id, unique_id, name, type_id, race_id) VALUES(?, ?, ?, ?, ?)", (id, unique_id, name, type_id, race_id))
    conn.commit()
#Set up a separate database for the races and race ids. Takes cur, conn as input and returns nothing.
def setRaceDB(cur, conn):
    cur.execute("DROP TABLE IF EXISTS Races")
    l = ["Normal", "Quick-Play", "Fish", "Aqua", "Continuous", "Equip", "Machine", "Cyberse", "Warrior", "Insect", "Beast", "Field", "Spellcaster", "Ritual", "Fiend", "Rock", "Fairy", "Dragon", "Plant", "Sea Serpent", "Beast-Warrior"]
    cur.execute("CREATE TABLE IF NOT EXISTS Races (id INTEGER PRIMARY KEY, race TEXT)")
    for x in range(len(l)):
        cur.execute("INSERT INTO Races (id, race) VALUES (?,?)", (x, l[x]))
    conn.commit()
#Set up separate database for types and type ids. Takes cur, conn as input and returns nothing
def setTypeDB(cur, conn):
    cur.execute("DROP TABLE IF EXISTS Types")
    l = ["Spell Card", "Effect Monster", "Normal Monster", "Flip Effect Monster", "Trap Card", "Union Effect Monster", "Fusion Monster", "Pendulum Effect Monster", "Link Monster", "XYZ Monster", "Link Monster", "Synchro Tuner Monster"]
    cur.execute("CREATE TABLE IF NOT EXISTS Types (id INTEGER PRIMARY KEY, type TEXT)")
    for x in range(len(l)):
        cur.execute("INSERT INTO Types (id, type) VALUES (?,?)", (x, l[x]))
    conn.commit()
#Use a JOIN to get frequency of races, takes cur as input and returns a dictionary with the race as key and frequency as value
def getRaceFreq(cur):
    raceDict= {}
    cur.execute("""SELECT  Yugioh.name , Races.race FROM Yugioh
    JOIN Races
    ON Yugioh.race_id = Races.id""")
    raceFreq = cur.fetchall()  
    for i in raceFreq:
        if i[1] not in raceDict:
            raceDict[i[1]] = 1
        else:
            raceDict[i[1]] += 1
    return sorted(raceDict.items(), key = lambda item:item[1], reverse=True)
#Creates a barchart based off of the returned race dictionary, takes the output from getRaceFreq as input and returns nothing.
def barChart(raceDict):
    fig = plt.figure(figsize=(10,4))
    ax1 = fig.add_subplot()
    races = []
    frequency = []  
    for i in raceDict:
        if i[1] != 1:
            races.append(i[0])
            frequency.append(i[1])
    ax1.bar(races, frequency, align='center', alpha=0.5, color='pink')
    ax1.set(xlabel='Race', ylabel='Frequency',
    title='Frequency of Each Yugioh Race in a Random 100-Card Sample')
    plt.show()
#Gets frequency of types and takes cur as input, returns a dictionary with keys as types and values as frequencies
def getTypeFreq(cur):
    typeDict= {}
    cur.execute("""SELECT  Yugioh.name, Types.type FROM Yugioh
    JOIN Types
    ON Yugioh.type_id = Types.id""")
    typeFreq = cur.fetchall()  
    for i in typeFreq:
        if i[1] not in typeDict:
            typeDict[i[1]] = 1
        else:
            typeDict[i[1]] += 1
    return sorted(typeDict.items(), key = lambda item:item[1], reverse=True)

#Writes all calculated data to a csv file. Takes filename, output values from getRaceFreq and getTypeFreq as input and returns nothing.
def write_to_csv(filename, raceDict, typeDict):
    path = os.path.dirname(os.path.abspath(__file__)) + os.sep
    outFile = open(path+filename, "w")
    outFile.write("Race, Frequency\n")
    for i in raceDict:
        outFile.write(f"{i[0]}, {i[1]}")
        outFile.write("\n")
    outFile.write("\n")
    outFile.write("Type, Frequency\n")
    for i in typeDict:
        outFile.write(f"{i[0]}, {i[1]}")
        outFile.write("\n")
    outFile.close()

#Creates a pie chart showing the frequency of each type, takes output from getTypeFreq as input and returns nothing.
def pieChart(typeDict):
    fig = plt.figure(figsize=(10,4))
    ax1 = fig.add_subplot()
    types = []
    freq = []
    for i in typeDict:
        if i[1] > 3:
            types.append(i[0])
            freq.append(i[1])
    types.append("Other")
    freq.append(11)
    explode = (0.1, 0, 0, 0, 0, 0)
    ax1.pie(freq, explode=explode, labels = types,autopct='%1.1f%%',
        shadow=True, startangle=30)
    ax1.axis('equal')
    ax1.set(title='Type Frequency of Yugioh Cards')
    plt.show()

def main():
    data = cards()
    cur, conn = setUpDatabase('CardGames.db')
    # setRaceDB(cur, conn)
    # setTypeDB(cur, conn)
    # setDB(data,cur,conn)
    

    #uncomment to get visualizations 

    typeDict = getTypeFreq(cur)
    raceDict = getRaceFreq(cur)
    barChart(raceDict) 
    # pieChart(typeDict)
    
    # write_to_csv("yugioh.txt", raceDict, typeDict)
    


if __name__ == '__main__':
    main()
