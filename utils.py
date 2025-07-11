from sqlite3 import Cursor

def getLessonsByClassID(cur:Cursor, classID):
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
        
def searchLessonsByName(cur: Cursor, name: str):
    result = []

    if len(name) == 0: # safety
        return []
    
    nameQuery = f"%{name}%"
    print(nameQuery)

    # Get subject name
    cur.execute("SELECT id, name FROM subjects WHERE LOWER(name) LIKE LOWER(?)", (nameQuery,))
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