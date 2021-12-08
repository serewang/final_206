from bs4 import BeautifulSoup
import requests
import re
import os
import json
import csv
import unittest
import sqlite3
import matplotlib
import matplotlib.pyplot as plt


def cards():
    r = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php")
    jsonfile = r.json()
    idList = []
    nameList = []
    typeList = []
    raceList = []
    archetypeList = []
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
yugiohList = cards()

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setDB(yugioh, cur, conn):
    # cur.execute("DROP TABLE IF EXISTS Yugioh")
    cur.execute("CREATE TABLE IF NOT EXISTS Yugioh (id INTEGER PRIMARY KEY, unique_id NUMBER, name text, type TEXT, race TEXT)")
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
        type = x[3]
        race = x[4]
        cur.execute("INSERT INTO Yugioh (id, unique_id, name, type, race) VALUES(?, ?, ?, ?, ?)", (id, unique_id, name, type, race))
    conn.commit()

def main():
    data = cards()
    cur, conn = setUpDatabase('Yugioh.db')
    setDB(data,cur,conn)

if __name__ == '__main__':
    main()
