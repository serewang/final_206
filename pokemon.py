import requests
import json
import sys
import os
import matplotlib
import sqlite3
import unittest
import csv
import matplotlib.pyplot as plt


def createJSON():
    # apiKey = "Y1FiRjhG75DZ5REYKGAeNrAvVxGCqnTM"
    baseurl = "https://api.pokemontcg.io/v2/cards"
    response = requests.get(baseurl)
    jsonVersion = response.json()
    # print(jsonVersion["cards"])
    with open('pokemon.json', 'w') as json_file:
        json.dump(jsonVersion, json_file)
        json_file.close

def readDataFromFile(filename):
    full_path = os.path.join(os.path.dirname(__file__), filename)
    f = open(full_path)
    file_data = f.read()
    f.close()
    json_data = json.loads(file_data)
    return json_data

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


   

def setUpEpisodes(data):
    pokemon_id = 0
    pokemonCards = []
    for i in data["data"]:
        
        try:
            name = i['name']
        except:
            name = "noname"
        try:
            subtype = i['rarity']
        except:
            subtype = "norarity"
        try:
            types = i['types'][0]
        except:
            types = "notypes"
        tuplePokemon = (pokemon_id, name, subtype, types)
        pokemon_id = pokemon_id + 1
        pokemonCards.append(tuplePokemon)
    return pokemonCards
def setRarityDB(cur, conn):
    cur.execute("DROP TABLE IF EXISTS RarityPokemonKey")
    l = ["Rare Holo","Common","Promo", "norarity", "Rare Holo GX", "Rare", "Uncommon", "Rare Holo V"]
    cur.execute("CREATE TABLE IF NOT EXISTS RarityPokemonKey (id INTEGER PRIMARY KEY, rarity TEXT)")
    for x in range(len(l)):
        cur.execute("INSERT INTO RarityPokemonKey (id, rarity) VALUES (?,?)", (x, l[x]))
    conn.commit()
def setTypeDB(cur, conn):
    cur.execute("DROP TABLE IF EXISTS TypePokemonKey")
    l = ["Darkness", "Colorless", "Grass", "Water", "Metal", "Psychic", "Lightning", "Dragon", "Fire",  "Fighting"]
    cur.execute("CREATE TABLE IF NOT EXISTS TypePokemonKey (id INTEGER PRIMARY KEY, type TEXT)")
    for x in range(len(l)):
        cur.execute("INSERT INTO TypePokemonKey (id, type) VALUES (?,?)", (x, l[x]))
    conn.commit()
def makeTable(data, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Pokemon_cards (pokemon_id INTEGER PRIMARY KEY, name TEXT, rarity TEXT, type TEXT)")
    cur.execute('CREATE TABLE IF NOT EXISTS Pokemon_Type (type_name TEXT PRIMARY KEY, number INTEGER)')
    cur.execute('CREATE TABLE IF NOT EXISTS Pokemon_rarity (rarity_type TEXT PRIMARY KEY, number INTEGER)')
    start = None
    cur.execute('SELECT pokemon_id FROM Pokemon_cards WHERE pokemon_id = (SELECT MAX(pokemon_id) FROM Pokemon_cards)')
    start = cur.fetchone()
    if (start!=None):
        start = start[0] + 1
    else:
        start = 0
    for x in data[start: start+25]:
        cur.execute('SELECT id, type from TypePokemonKey')
        typefetch = cur.fetchall()
        typeId = 0
        for i in typefetch:
            if x[3] == i[1]:
                typeId = i[0]
        cur.execute('SELECT id, rarity from RarityPokemonKey')
        rarityfetch = cur.fetchall()
        rarityId = 0
        for i in rarityfetch:
            if x[2] == i[1]:
                rarityId = i[0]
        
        cur.execute("INSERT INTO Pokemon_cards (pokemon_id, name, rarity, type) VALUES(?, ?, ?, ?)", (x[0], x[1], rarityId, typeId))
        cur.execute("INSERT or IGNORE INTO Pokemon_Type (type_name, number) VALUES(?, ?)", (x[3],0))
        cur.execute('SELECT type_name FROM Pokemon_Type')
        row = cur.fetchall()
        cur.execute('update Pokemon_Type set number = number + 1 where type_name = ?', (x[3],))
        cur.execute("INSERT or IGNORE INTO Pokemon_rarity (rarity_type, number) VALUES(?, ?)", (x[2],0))
        cur.execute('SELECT rarity_type FROM Pokemon_rarity')
        row = cur.fetchall()
        cur.execute('update Pokemon_rarity set number = number + 1 where rarity_type = ?', (x[2],))
    conn.commit()

def barChart(cur):

    fig = plt.figure(figsize=(10,4))
    ax1 = fig.add_subplot()   

    pokemonDict = dict()
    cur.execute('SELECT type_name,number FROM Pokemon_Type ORDER BY number DESC')
    cur1 = cur.fetchall()
    for row in cur1:
        pokemonDict[row[0]]=row[1]

    types = []
    frequency=[]
    for key,value in pokemonDict.items():
        types.append(key)
        frequency.append(value)
    ax1.bar(types,frequency,align='center', alpha=0.5, color='blue')
    ax1.set(xlabel='Pokemon Name', ylabel='Frequency',
       title='Frequency of each Pokemon Type in a Random 100-Card Sample')
    ax1.set_xticklabels(types,FontSize='9')
    plt.show()
def pieChart(cur):

    fig = plt.figure(figsize=(10,4))
    ax1 = fig.add_subplot()   

    pokemonDict = dict()
    cur.execute('SELECT rarity_type,number FROM Pokemon_rarity ORDER BY number DESC')
    cur1 = cur.fetchall()
    for row in cur1:
        pokemonDict[row[0]]=row[1]

    types = []
    frequency=[]
    for key,value in pokemonDict.items():
        types.append(key)
        frequency.append(value)
    ax1.pie(frequency, labels = types,autopct='%1.1f%%',
        shadow=False, startangle=180)
    ax1.axis('equal')
    ax1.set(title='Rarity of each Pokemon Card in a Random 100-Card Sample')
    plt.show()
def writeCSV(filename, cur):
    path = os.path.dirname(os.path.abspath(__file__)) + os.sep
    outFile = open(path+filename, "w")
    outFile.write("Type, Frequency of Type\n")
    cur.execute('SELECT type_name,number FROM Pokemon_Type ORDER BY number DESC')
    cur1 = cur.fetchall()
    pokemonDict = dict()
    for row in cur1:
        pokemonDict[row[0]]=row[1]

    for key,value in pokemonDict.items():
        outFile.write(f"{key}, {value}")
        outFile.write("\n")
    cur.execute('SELECT rarity_type,number FROM Pokemon_rarity ORDER BY number DESC')
    cur2 = cur.fetchall()
    rarityDict = dict()
    outFile.write("\n")
    for row in cur2:
        rarityDict[row[0]]=row[1]
    outFile.write("Rarity, Frequency of Rarity\n")
    for key,value in rarityDict.items():
        outFile.write(f"{key}, {value}")
        outFile.write("\n")
    outFile.close()
def writeCSVforboth(filename, cur):
    path = os.path.dirname(os.path.abspath(__file__)) + os.sep
    outFile = open(path+filename, "w")
    outFile.write("Type, Frequency of Type\n")
    cur.execute('SELECT type_name,number FROM Pokemon_Type')
    cur1 = cur.fetchall()
    cardGameDict = dict()
    for row in cur1:
        cardGameDict[row[0]]=row[1]
    cur.execute("SELECT name, type FROM Yugioh")
    typeFreq = cur.fetchall()  
    for i in typeFreq:
        if i[1] not in cardGameDict:
            cardGameDict[i[1]] = 1
        else:
            cardGameDict[i[1]] += 1
    cardGameDict = sorted(cardGameDict.items(), key = lambda item:item[1], reverse=True)
    for x in cardGameDict:
        outFile.write(f"{x[0]}, {x[1]}")
        outFile.write("\n")
    total = 0
    for x in cardGameDict:
        total = total + x[1]
    average = total/len(cardGameDict)
    outFile.write("average: " + f"{round(average, 2)}")
    
    outFile.close()
    return cardGameDict
def barChartforBoth(cardGameDict):
    fig = plt.figure(figsize=(10,4))
    ax1 = fig.add_subplot()
    races = []
    frequency = []  
    for i in cardGameDict:
        if i[1] >= 10:
            races.append(i[0])
            frequency.append(i[1])
    ax1.bar(races, frequency, align='center', alpha=1, color='pink')
    ax1.set(xlabel='Types', ylabel='Frequency',
    title='Top types in Pokemon and Yugioh in a Random 100-Card Sample')
    plt.show()
    
def main():

    createJSON()
    json_data = readDataFromFile("pokemon.json")
    cur, conn = setUpDatabase('CardGames.db')
    setTypeDB(cur, conn)
    setRarityDB(cur, conn)
    pokemon_list = setUpEpisodes(json_data)
    makeTable(pokemon_list, cur, conn)
    # barChart(cur)
    # pieChart(cur)
    # writeCSV("pokemon.txt", cur)
    # cardGameDict = writeCSVforboth("cardGameTypes.txt", cur)
    # barChartforBoth(cardGameDict)
    conn.close()

if __name__ == "__main__":
    main()
    unittest.main(verbosity = 2)