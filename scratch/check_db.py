import sqlite3

conn = sqlite3.connect('backend/formmind.db')
c = conn.cursor()
form_id = '754ee58e-55be-4271-badc-8b08edbba18b'

c.execute('SELECT count(*) FROM form_responses WHERE form_id = ?', (form_id,))
print('Responses count:', c.fetchone()[0])

c.execute('SELECT count(*) FROM response_answers WHERE response_id in (SELECT id FROM form_responses WHERE form_id = ?)', (form_id,))
print('Answers count:', c.fetchone()[0])

c.execute('SELECT id, title, total_responses_count, response_access_status, analysis_status, status_message FROM forms WHERE id = ?', (form_id,))
print('Form row:', c.fetchall())

