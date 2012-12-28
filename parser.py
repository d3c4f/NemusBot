import sys
import time 
import psycopg2
from datetime import date

class IRC_Parser:

	def __init__(self):
		self.dsn = "host=localhost dbname=ircbot user=ircman password=2much20ften"

	def get_messages(self):
		conn = psycopg2.connect(self.dsn)
		cur = conn.cursor()
		cur.execute('SELECT id, message, "timestamp" FROM connectivity_messages')
		rows = cur.fetchall()
		return rows

	def archive_message(self,text,timestamp):
	
		message = self.parsemsg(text)
		print message

		conn = psycopg2.connect(self.dsn)
		cur = conn.cursor()
		cur.execute('select id,name from channels where name = \'%s\'' % message['channel'])
		rows = cur.fetchall()

		handle_id = None
		channel_id = None

		if len(rows) == 1:
			for row in rows:
				channel_id = row[0]
	
		else:
			cur.execute('INSERT into channels (name) values (\'%s\') RETURNING id' % message['channel'])
			channel_id = cur.fetchone()[0]
			conn.commit()


		cur.execute('SELECT id,handle from handles where handle = \'%s\'' % message['handle'])
		rows = cur.fetchall()

		if len(rows) == 1:
			for row in rows:
				handle_id = row[0]

		else:
			cur.execute('INSERT INTO handles (handle) values (\'%s\') RETURNING id' % message['handle'])
			handle_id = cur.fetchone()[0]
			conn.commit()

		sql = 'INSERT INTO messages (handle_id,channel_id,timestamp,message) values (\'%s\',\'%s\',%s,%s)'
		#timestamp = str(int(time.time()))
		cur.execute(sql,(handle_id,channel_id,timestamp,message['text']))
		conn.commit()
		cur.close()
		conn.close()
	
	def parsemsg(self,s):
		"""Breaks a message from an IRC server into its prefix, command, and arguments."""
		prefix = ''
		trailing = []
		if not s:
			raise IRCBadMessage("Empty line.")
		if s[0] == ':':
			prefix, s = s[1:].split(' ', 1)

		if s.find(' :') != -1:
			s, trailing = s.split(' :', 1)
			args = s.split()
			args.append(trailing)
		else:
			args = s.split()
		command = args.pop(0)
				
		return {'channel':args[0],'handle':prefix.split('@')[0],'text':args[1]}
	
parser = IRC_Parser()
rows = parser.get_messages()

for row in rows:
	if row[1].find('PRIVMSG') != -1:
		print row
		parser.archive_message(row[1],row[2])
		#channel = message[2][0]
		#user_text = message[2][1]
		#user_info =  message[0].split('@')
		#handle = user_info[0]

		#print 'Channel : ' + channel + ' Handle: ' + handle + ' Text: ' + user_text


