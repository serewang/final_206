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
    baseurl = "https://api.pokemontcg.io/v1/cards"
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
    # cur.execute("CREATE TABLE IF NOT EXISTS Pokemon_cards (pokemon_id INTEGER PRIMARY KEY, name TEXT, subtype TEXT, type INTEGER)")
    # cur.execute('CREATE TABLE IF NOT EXISTS Pokemon_Type (type_id INTEGER PRIMARY KEY, type_name TEXT, number INTEGER)')
    for i in data["cards"]:
        try:
            print(i['name'])
        except:
            print("noname")
        try:
            print(i['subtype'])
        except:
            print("nosubtype")
        try:
            print(i['types'][0])
        except:
            print("notypes")
    # conn.commit()
    
def main():
    # cur, conn = setUpDatabase('JRP.db')

    # #SECTION 1: get data
    # #to create accurate visualizations, you should gather at least 200 pieces of data (run code 8 times)
    # try:
    #     cur.execute('SELECT episode_id FROM Spotify_Episodes WHERE episode_id  = (SELECT MAX(episode_id) FROM Spotify_Episodes)')
    #     start = cur.fetchone()
    #     start = start[0]
    # except:
    #     start = 0
    # data = episodes_search('4rOoJ6Egrf8K2IrywzwOMk', start, cur)
    # setUpEpisodes(data, cur, conn)

    # #SECTION 2: if you want to see calculations + visualizations, uncomment lines below.
    # # createPieChart(cur)
    # createBarGraph(cur, 'fileOutputEpisodes.txt')
    
    
    createJSON()
    data = readDataFromFile("pokemon.json")
    setUpEpisodes(data)
    # cardSearch()

if __name__ == '__main__':
    main()