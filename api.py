from flask import Flask, Response, request, g, jsonify, json
from flask_cors import CORS, cross_origin

import sqlite3

from storage import getDBPath
from utils import *

json.provider.DefaultJSONProvider.ensure_ascii = False

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Database managment
def getDatabase():
    if 'db' not in g:
        g.db = sqlite3.connect(getDBPath())
    return g.db

@app.teardown_appcontext
def closeDatabase(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# TODO TEMP home route
@app.route("/")
def home_path():
    return "Home page"

# api classes endpoint - get classess (optional filter based on year or name)
@app.route("/api/classes")
def api_classes():

    year = request.args.get("year", "")
    yearQuery = f"{year}%" if year.isdigit() else "%" # search by year or show everything

    nameQuery = "%-%" + request.args.get("name", "") + "%" # search after - in short

    # get data from db
    db = getDatabase()
    cursor = db.cursor()

    cursor.execute("SELECT id, short FROM classes WHERE short LIKE ? AND short LIKE ? ORDER BY short COLLATE NOCASE", (yearQuery, nameQuery))
    classes = cursor.fetchall() 

    cursor.close()

    # generate data
    res = {}
    for classId, short in classes:
        res[classId] = short

    if len(classes) == 0:
        return jsonify({"error": "Invalid queries!"}), 400

    return jsonify(res), 200

# api timetable endpoint - search classess based on class id or class name
@app.route("/api/timetable")
def api_timetable():
    classID = request.args.get("id", None)
    name = request.args.get("name", None)

    err = validateTimetableQueries(classID, name)

    if err != None:
        return jsonify({"error": err}), 401

    result = {}

    db = getDatabase()
    cur = db.cursor()

    if name: # fuzzy search based on name
        result = searchLessonsByName(cur, name)
    elif classID: # lookup based on class id
        result = getLessonsByClassID(cur, classID)

    cur.close()

    if len(result) == 0:
        return jsonify({"error": "Invalid query!"}), 400

    return jsonify(result), 200

# api teachers endpoint - search classess with specific teacher
@app.route("/api/teachers")
def api_teachers():
    name = request.args.get("name", None)
    
    err = validateTeacherQuery(name)

    if err != None:
        return jsonify({"error": err}), 400

    result = {}

    # get data
    cur = getDatabase().cursor()
    result = seatchLessonsByTeacher(cur, name)
    cur.close()

    if len(result) == 0:
        return jsonify({"error": "No results!"}), 400

    return jsonify(result), 200
    

if __name__ == "__main__":
    app.run(host="192.168.100.103", port=8080, debug=True)
  