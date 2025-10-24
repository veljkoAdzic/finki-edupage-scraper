-- Select all lesson data based on class id
SELECT 
	l.id AS lesson_id,
	s.name AS subject,
	t.short AS teacher,
	l.groupnames,
	cr.short AS classroom,
	p.starttime,
	l.durationperiods,
	c.days
FROM LessonsClass lc
JOIN lessons l ON lc.lesson_id = l.id
LEFT JOIN subjects s ON l.subjectId = s.id
LEFT JOIN LessonsTeachers lt ON l.id = lt.lesson_id
LEFT JOIN teachers t ON lt.teacher_id = t.id
LEFT JOIN cards c ON c.lessonid = l.id
LEFT JOIN periods p ON c.period = p.id
LEFT JOIN CardsClassrooms cc ON c.id = cc.card_id
LEFT JOIN classrooms cr ON cc.classroom_id = cr.id
WHERE lc.class_id = (?)