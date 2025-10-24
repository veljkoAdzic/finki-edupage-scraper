from sqlite3 import Cursor

### BETTER API UTILS
def __format_data(cur: Cursor):
    res = []

    appended_lessons = {}

    for lesson_id, subject, teacher, group, location, startTime, duration, day in cur.fetchall():
        if lesson_id not in appended_lessons.keys():
          appended_lessons[lesson_id] = len(res)
          res.append({
            "subject": subject,
            "teachers": teacher,
            "group": group,
            "location": location,
            "startTime": startTime,
            "duration": duration,
            "day": day
          })
        else:
          entry = res[ appended_lessons[lesson_id] ]
          entry["teachers"] = entry["teachers"] + ', ' + teacher
          res[ appended_lessons[lesson_id] ] = entry
    
    return res


def getLessonsByClassID(cur: Cursor, classID:str):

    with open("sql/queryLessonsByClassID.sql") as f:
        sql = f.read()

    cur.execute(sql, (classID,))

    return __format_data(cur)

def searchLessonsByName(cur: Cursor, name: str):    
    nameQuery = f"%{name}%"

    with open("sql/queryLessonsByName.sql") as f:
        sql = f.read()

    cur.execute(sql, (nameQuery,))

    return __format_data(cur)

def seatchLessonsByTeacher(cur: Cursor, name: str):
    if len(name) == 0:
        return []

    nameQuery = f"%{name}%"

    with open("sql/queryLessonsByName.sql") as f:
        sql = f.read()

    cur.execute(sql, (nameQuery,))

    return __format_data(cur)

### QUERY VALIDATION ###
def validateTimetableQueries(classID, name):
    # requires id or name
    if classID == None and name == None:
        return "Missing query!"
    
    # blocking both queries
    if classID and name:
        return "Invalid query! Search by id or name."

    # filter out wildcard characters
    if name and (name.find('%') != -1 or name.find('_') != -1):
        return "Invalid query - Illegal characters in query!"

    # Valid queries
    return None

def validateTeacherQuery(name):
    # must have name
    if name == None:
        return "Missing query!"

    # block if wildcard character is in name
    if name.find('%') != -1 or name.find('_') != -1:
        return "Invalid query - Illegal characters in query!"
    
    return None



### LEGACY API UTILS ###
def getLessonsByClassID_legacy(cur:Cursor, classID):
    result = [] # list of rows

    # Get lesson ids
    cur.execute("SELECT (lesson_id) FROM LessonsClass WHERE class_id == (?)", (classID,))
    lessonIDs = cur.fetchall()

    for lessonID in lessonIDs:
        row = {}

        # Get lesson data
        cur.execute("SELECT groupnames, durationperiods, subjectId FROM lessons WHERE id == (?)", lessonID)
        lesson = cur.fetchone()
        if not lesson: continue
        group, duration, subjectID = lesson

        # Get subject name
        cur.execute("SELECT (name) FROM subjects WHERE id == (?)", (subjectID,))
        sub = cur.fetchone()
        subject = sub[0] if sub else "-"

        # Get teachers
        cur.execute("SELECT (teacher_id) FROM LessonsTeachers WHERE lesson_id == (?)", lessonID)
        teacherIDs = [ t[0] for t in cur.fetchall()]

        if teacherIDs:
            placeholders = ','.join(['?'] * len(teacherIDs))
            cur.execute(f"SELECT (short) FROM teachers WHERE id in ({placeholders})", teacherIDs)
            teachers = ', '.join([t[0] for t in cur.fetchall() ])
        else:
            teachers = "-"
        
        # get cards
        cur.execute("SELECT id, period, days FROM cards WHERE lessonid == (?)", lessonID)
        cards = cur.fetchall()

        for cardID, period, day in cards:
            # Get start time
            cur.execute("SELECT (starttime) FROM periods WHERE id == (?)", (period,))
            startTime = cur.fetchone()[0] 

            # get location
            location = "-"
            cur.execute("SELECT (classroom_id) FROM CardsClassrooms WHERE card_id == (?)", (cardID,))
            classroomID = cur.fetchone()
            if classroomID:
                cur.execute("SELECT (short) FROM classrooms WHERE id == (?)", classroomID)
                l = cur.fetchone()
                location = l[0] if l else "-"
        
            result.append({
                "subject": subject,
                "teachers": teachers,
                "group": group,
                "location": location,
                "startTime": startTime,
                "duration": duration,
                "day": day
            })

    return result
        
def searchLessonsByName_legacy(cur: Cursor, name: str):
    result = []

    if len(name) == 0: # safety
        return []
    
    nameQuery = f"%{name}%"

    # Get subject name
    cur.execute("SELECT id, name FROM subjects WHERE name LIKE ?", (nameQuery,))
    subjects = cur.fetchall()

    for subjectID, subject in subjects:
        row = {}
        # Get lesson data
        cur.execute("SELECT id, groupnames, durationperiods FROM lessons WHERE subjectId == (?)", (subjectID,))

        for lessonID, group, duration in cur.fetchall():
            # Get teachers
            cur.execute("SELECT (teacher_id) FROM LessonsTeachers WHERE lesson_id == (?)", (lessonID,))
            teacherIDs = [ t[0] for t in cur.fetchall()]

            if teacherIDs:
                placeholders = ','.join(['?'] * len(teacherIDs))
                cur.execute(f"SELECT (short) FROM teachers WHERE id in ({placeholders})", teacherIDs)
                teachers = ', '.join([t[0] for t in cur.fetchall() ])
            else:
                teachers = "-"
            
            # get cards
            cur.execute("SELECT id, period, days FROM cards WHERE lessonid == (?)", (lessonID,))
            cards = cur.fetchall()

            for cardID, period, day in cards:
                # Get start time
                cur.execute("SELECT (starttime) FROM periods WHERE id == (?)", (period,))
                startTime = cur.fetchone()[0] 

                # get location
                location = "-"
                cur.execute("SELECT (classroom_id) FROM CardsClassrooms WHERE card_id == (?)", (cardID,))
                classroomID = cur.fetchone()
                if classroomID:
                    cur.execute("SELECT (short) FROM classrooms WHERE id == (?)", classroomID)
                    l = cur.fetchone()
                    location = l[0] if l else "-"
            
                result.append({
                    "subject": subject,
                    "teachers": teachers,
                    "group": group,
                    "location": location,
                    "startTime": startTime,
                    "duration": duration,
                    "day": day
                })

    return result

def seatchLessonsByTeacher_legacy(cur: Cursor, name: str):
    result = [] # list of rows

    if len(name) == 0:
        return []

    queryName = f"%{name}%"

    # get teacher ids
    cur.execute("SELECT id, short FROM teachers WHERE short LIKE ?", (queryName,))
    teacherIDs = [t[0] for t in cur.fetchall()]

    if len(teacherIDs) == 0:
        return []

    # Get lessons
    cur.execute(f"SELECT (lesson_id) FROM LessonsTeachers WHERE teacher_id IN ({','.join(['?']*len(teacherIDs))})", teacherIDs)
    lessonIDs = cur.fetchall()

    for lessonID in lessonIDs:
        # Get lesson data
        cur.execute("SELECT groupnames, durationperiods, subjectId FROM lessons WHERE id == (?)", lessonID)
        lesson = cur.fetchone()
        if not lesson: continue
        group, duration, subjectID = lesson

        # Get subject name
        cur.execute("SELECT (name) FROM subjects WHERE id == (?)", (subjectID,))
        sub = cur.fetchone()
        subject = sub[0] if sub else "-"

        # get current teacher ids
        cur.execute("SELECT teacher_id FROM LessonsTeachers WHERE lesson_id == ?", lessonID)
        currTeacherIDs = [t[0] for t in cur.fetchall()]

        # get teachers
        placeholders = ','.join(['?'] * len(currTeacherIDs))
        cur.execute(f"SELECT (short) FROM teachers WHERE id IN ({placeholders})", currTeacherIDs)
        teachers = ', '.join([t[0] for t in cur.fetchall() ])
        
        # get cards
        cur.execute("SELECT id, period, days FROM cards WHERE lessonid == (?)", lessonID)
        cards = cur.fetchall()

        for cardID, period, day in cards:
            # Get start time
            cur.execute("SELECT (starttime) FROM periods WHERE id == (?)", (period,))
            startTime = cur.fetchone()[0] 

            # get location
            location = "-"
            cur.execute("SELECT (classroom_id) FROM CardsClassrooms WHERE card_id == (?)", (cardID,))
            classroomID = cur.fetchone()
            if classroomID:
                cur.execute("SELECT (short) FROM classrooms WHERE id == (?)", classroomID)
                l = cur.fetchone()
                location = l[0] if l else "-"
        
            result.append({
                "subject": subject,
                "teachers": teachers,
                "group": group,
                "location": location,
                "startTime": startTime,
                "duration": duration,
                "day": day
            })
    
    return result