SELECT s.student_name, COALESCE(c.course_name, 'Not enrolled') AS course_name
FROM students s
LEFT JOIN enrollments e ON s.student_id = e.student_id
LEFT JOIN courses c ON e.course_id = c.course_id;
