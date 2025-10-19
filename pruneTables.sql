-- prune lessons that have no actula card for display
DELETE FROM lessons 
WHERE id IN ( 
	SELECT l.id 
	FROM LessonsClass lc 
	JOIN lessons l ON lc.lesson_id = l.id 
	LEFT JOIN cards c ON c.lessonid = l.id 
	WHERE c.id IS NULL AND 1=1 
)