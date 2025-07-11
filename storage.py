import json
import sqlite3

from datetime import date
import os

__REFS = "__REFS"

STRUCTURE = {
    "classes": ("id", "name", "short"),
    "subjects": ("id", "name"),
    "teachers": ("id", "short"),
    "periods": ("id", "starttime"),
    "classrooms": ("id", "short"),
    # "days": ("id", "name"),
    "lessons": ("id", "groupnames", "durationperiods", "subjectid"),
    "cards": ("id", "days", "period", "lessonid")
}

def generateDBPath():
    candidate = str(date.today()) + ".db" 

    currentDBs = []
    for f in os.listdir("./database"):
        currentDBs.append(str(f))
    
    i = 0
    while i < 50:
        try:
            ind = currentDBs.index(candidate)
            i += 1
            candidate = f"{str(date.today())}-{i}.db"
        except ValueError:
            return "./database/" + candidate
    
    return "" # No database found (this should't happen)

def __processName(name: str):
    name = name.removesuffix(".db")
    if name.count("-") == 2:
        return name
    else:
        return name[name.index("-", -3):]

def getDBPath():
    databases = os.listdir("./database")
    
    databases.sort(reverse=True, key= __processName )

    if len(databases) == 0:
        return None

    return "./database/" + databases[0]

def storeData(jsonBlob):
    conn = sqlite3.connect(generateDBPath())
    cursor = conn.cursor()

    # Create table
    with open('createTables.sql') as file:
        sql = file.read()
    cursor.executescript(sql)
    conn.commit()

    # Parse data
    data = parseJsonBlob(jsonBlob)

    for name, vals in STRUCTURE.items():
        # Fill table
        for row in data[name].values():
            sql_query = f"""
            INSERT INTO {name}( 
            {','.join([n for n in vals])}) 
            VALUES ({ ','.join("?"*len(vals)) })"""
            data_insert = [row[key] for key in vals]    
            cursor.execute(sql_query, tuple(data_insert) )

            # Lessons relationships
            if name == "lessons":
                for cid in row["classids"]:
                    cursor.execute("INSERT INTO LessonsClass (lesson_id, class_id) VALUES (?, ?)", (row['id'], cid))
                               
                for tid in row["teacherids"]:
                    cursor.execute("INSERT INTO LessonsTeachers (lesson_id, teacher_id) VALUES (?, ?)", (row['id'], tid))
            # Cards relationships
            if name == "cards":
                for cid in row["classroomids"]:
                    cursor.execute("INSERT INTO CardsClassrooms (card_id, classroom_id) VALUES (?, ?)", (row['id'], cid))

        
        conn.commit()

    cursor.close()
    conn.close()


def parseJsonBlob(blob) -> dict[str, dict]:
    res = {}
    raw = json.loads(blob)
    for table in raw["r"]["dbiAccessorRes"]["tables"]:
        entries = {}
        for row in table["data_rows"]:
            if table["id"] == "lessons": # Combining groupnames into 1 string
                groupnames:list = row.get('groupnames', [])
                groupnames = [g for g in groupnames if len(g) != 0]
                row["groupnames"] = '/'.join(groupnames)

            if table["id"] == "cards": # converting mystery days to ind
                if len(row["days"]) == 0: continue
                row["days"] = row["days"].index('1')
            
            entries[row["id"]] = row
        res[table["id"]] = entries
    
    return res

