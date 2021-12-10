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
    # cur.execute("INSERT or IGNORE INTO Pokemon_Type (type_name, number) VALUES(?, ?)", ('Colorless', 0))
    # cur.execute("INSERT or IGNORE INTO Pokemon_Type (type_name, number) VALUES(?, ?)", ('Darkness', 0))
    # cur.execute("INSERT or IGNORE INTO Pokemon_Type (type_name, number) VALUES(?, ?)", ('Dragon', 0))
    # cur.execute("INSERT or IGNORE INTO Pokemon_Type (type_name, number) VALUES(?, ?)", ('Fighting', 0))
    # cur.execute("INSERT or IGNORE INTO Pokemon_Type (type_name, number) VALUES(?, ?)", ('Fire', 0))
    # cur.execute("INSERT or IGNORE INTO Pokemon_Type (type_name, number) VALUES(?, ?)", ('Grass', 0))
    # cur.execute("INSERT or IGNORE INTO Pokemon_Type (type_name, number) VALUES(?, ?)", ('Lightning', 0))
    # cur.execute("INSERT or IGNORE INTO Pokemon_Type (type_name, number) VALUES(?, ?)", ('Metal', 0))
    # cur.execute("INSERT or IGNORE INTO Pokemon_Type (type_name, number) VALUES(?, ?)", ('Psychic', 0))
    # cur.execute("INSERT or IGNORE INTO Pokemon_Type (type_name, number) VALUES(?, ?)", ('Water', 0))
    # cur.execute("INSERT or IGNORE INTO Pokemon_Type (type_name, number) VALUES(?, ?)", ('notypes', 0))
    for x in data[start: start+25]:
        
        cur.execute("INSERT INTO Pokemon_cards (pokemon_id, name, rarity, type) VALUES(?, ?, ?, ?)", (x[0], x[1], x[2], x[3]))
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

    l1 = dict()
    cur.execute('SELECT type_name,number FROM Pokemon_Type ORDER BY number DESC')
    cur1 = cur.fetchall()
    for row in cur1:
        l1[row[0]]=row[1]

    people = []
    apperances=[]
    for key,value in l1.items():
        people.append(key)
        apperances.append(value)
    ax1.bar(people,apperances,align='center', alpha=0.5, color='blue')
    ax1.set(xlabel='Pokemon Name', ylabel='Amount',
       title='Amount of each Pokemon Type')
    ax1.set_xticklabels(people,FontSize='9')
    plt.show()
def pieChart(cur):

    fig = plt.figure(figsize=(10,4))
    ax1 = fig.add_subplot()   

    l1 = dict()
    cur.execute('SELECT rarity_type,number FROM Pokemon_rarity ORDER BY number DESC')
    cur1 = cur.fetchall()
    for row in cur1:
        l1[row[0]]=row[1]

    people = []
    apperances=[]
    for key,value in l1.items():
        people.append(key)
        apperances.append(value)
    ax1.pie(apperances, labels = people,autopct='%1.1f%%',
        shadow=False, startangle=180)
    ax1.axis('equal')
    ax1.set(title='Rarity of each Pokemon Card')
    plt.show()

    
def main():

    # createJSON()
    json_data = readDataFromFile("pokemon.json")
    cur, conn = setUpDatabase('Pokemon.db')
    pokemon_list = setUpEpisodes(json_data)
    makeTable(pokemon_list, cur, conn)
    # barChart(cur)
    # pieChart(cur)
    conn.close()

if __name__ == "__main__":
    main()
    unittest.main(verbosity = 2)