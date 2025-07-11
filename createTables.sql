CREATE TABLE IF NOT EXISTS classes (
    id TEXT PRIMARY KEY,
    name TEXT,
    short TEXT
);

CREATE TABLE IF NOT EXISTS subjects (
    id TEXT PRIMARY KEY,
    name TEXT
);

CREATE TABLE IF NOT EXISTS teachers (
    id TEXT PRIMARY KEY,
    short TEXT
);

CREATE TABLE IF NOT EXISTS periods (
    id TEXT PRIMARY KEY,
    starttime TEXT
);

CREATE TABLE IF NOT EXISTS classrooms (
    id TEXT PRIMARY KEY,
    short TEXT
);

-- CREATE TABLE IF NOT EXISTS days (
--     id TEXT PRIMARY KEY,
--     name TEXT
-- );

CREATE TABLE IF NOT EXISTS LessonsClass (
    id INTEGER PRIMARY KEY,
    lesson_id TEXT NOT NULL,
    class_id TEXT NOT NULL,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

CREATE TABLE IF NOT EXISTS LessonsTeachers (
    id INTEGER PRIMARY KEY,
    lesson_id TEXT NOT NULL,
    teacher_id TEXT NOT NULL,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id),
    FOREIGN KEY (teacher_id) REFERENCES teacher(id)
);

CREATE TABLE IF NOT EXISTS lessons (
    id TEXT PRIMARY KEY,
    groupnames TEXT,
    durationperiods INT,
    subjectid TEXT NOT NULL,
    FOREIGN KEY (subjectid) REFERENCES subjects(id)
);

CREATE TABLE IF NOT EXISTS CardsClassrooms (
    id INTEGER PRIMARY KEY,
    card_id TEXT NOT NULL,
    classroom_id TEXT NOT NULL,
    FOREIGN KEY (card_id) REFERENCES cards(id),
    FOREIGN KEY (classroom_id) REFERENCES classrooms(id)
);

CREATE TABLE IF NOT EXISTS cards (
    id TEXT PRIMARY KEY,
    lessonid TEXT NOT NULL,
    period TEXT NOT NULL,
    days INT,
    FOREIGN KEY (lessonid) REFERENCES lessons(id),
    FOREIGN KEY (period) REFERENCES periods(id)
);