-- Select all lesson data based on class id
SELECT 
	l.id AS lesson_id,
	l.groupnames,
	l.durationperiods,
	s.name AS subject,
	t.short AS teacher,
	c.id AS card_id,
	c.period,
	c.days,
	p.starttime,
	cr.short AS classroom
FROM LessonsClass lc
JOIN lessons l ON lc.lesson_id = l.id
LEFT JOIN subjects s ON l.subjectId = s.id
LEFT JOIN LessonsTeachers lt ON l.id = lt.lesson_id
LEFT JOIN teachers t ON lt.teacher_id = t.id
LEFT JOIN cards c ON c.lessonid = l.id
LEFT JOIN periods p ON c.period = p.id
LEFT JOIN CardsClassrooms cc ON c.id = cc.card_id
LEFT JOIN classrooms cr ON cc.classroom_id = cr.id
WHERE lc.class_id = ?
-- ORDER BY c.days, p.starttime