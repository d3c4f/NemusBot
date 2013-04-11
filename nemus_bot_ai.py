from bot import Bot
import smtplib
import re
import psycopg2
import time 
import ConfigParser


class NemusBotAI(Bot):

	def __init__(self):
		
		config = ConfigParser.RawConfigParser()
		config.read('/etc/nemusbot/nemus_bot.cfg')	

		host 		= config.get('Bot','host')
		channel 	= config.get('Bot','channel')
		password 	= config.get('Bot','password')
		nicks 		= config.get('Bot','nicks') 
		hostname 	= config.get('Bot','hostname')
		debug 		= config.getboolean('Bot','debug')
		log 		= config.getboolean('Bot','log')
		hidden 		= config.getboolean('Bot','hidden')

		self.dsn 			= config.get('Database','dsn')
		self.sheep 			= config.getboolean('Sheep','enabled')
		self.sheep_number 	= config.get('Sheep','number')
		self.sheep_regex 	= config.get('Sheep','regex')
		self.smtp_server 	= config.get('SMTP','ip')
		self.page_number 	= config.get('Page','number')
		self.logged_in		= False

		super(NemusBotAI,self).__init__(host,channel,password,nicks,hostname,debug,log,hidden)
	

	def log_connectivity(self,text):

		conn = psycopg2.connect(self.dsn)
		cur = conn.cursor()
		timestamp = str(int(time.time()))
		cur.execute('INSERT into connectivity_messages (message,timestamp) values (%s,%s) RETURNING id', (text,timestamp))
		conn.commit()
		connectivity_id = cur.fetchone()[0]
		cur.close()
		conn.close()
	
	def archive_message(self,text,timestamp):
		
		message = self.parsemsg(text)
		conn = psycopg2.connect(self.dsn)
		cur = conn.cursor()
		cur.execute('select id,name from channels where name = %s', (message['channel'],))
		rows = cur.fetchall()

		handle_id = None
		channel_id = None

		if len(rows) == 1:
			for row in rows:
				channel_id = row[0]
	
		else:
			cur.execute('INSERT into channels (name) values (%s) RETURNING id', (message['channel'],))
			channel_id = cur.fetchone()[0]
			conn.commit()


		cur.execute('SELECT id,handle from handles where handle = %s', (message['handle'],))
		rows = cur.fetchall()

		if len(rows) == 1:
			for row in rows:
				handle_id = row[0]

		else:
			cur.execute('INSERT INTO handles (handle) values (%s) RETURNING id' , (message['handle'],))
			handle_id = cur.fetchone()[0]
			conn.commit()

		sql = 'INSERT INTO messages (handle_id,channel_id,timestamp,message) values (%s,%s,%s,%s)'

		cur.execute(sql,(handle_id,channel_id,timestamp,message['text']))
		conn.commit()
		cur.close()
		conn.close()

	def custom_ai(self,text,timestamp):
		
	 	parsed_msg = self.parsemsg(text)
		if text.find(':!penetrate') != -1:
			self.sendm("Bah Bah Bah -('')- ")

		if text.find (':!fight') != -1:
			self.sendm(parsed_msg['handle'].split('!~')[0] +'has started a fight with ')


		if parsed_msg is not None:

			sheep_match = re.search(self.sheep_regex, text)

			if sheep_match:
				if self.sheep and text.find(':!sheep_paging') == -1:
					regex_array = re.findall(self.sheep_regex,text)
					self.sendm(parsed_msg['handle'].split('!~')[0] + ' said \'sheep\'. Paging L34N. Someone said \'sheep\'');
					self.send_email(parsed_msg, self.sheep_number,"sheep-alarm@dc801.com","SHEEP")

			if text.find(':!sheep_paging') != -1:
				sheep = text.split("!sheep_paging")
				if self.sheep:
					self.sheep = False
					self.sendm('Sheep Paging Disabled');
				else:
					self.sheep = True
					self.sendm('Sheep Paging Enabled');
			if self.logged_in:
				if parsed_msg['text'].lower().find('nemus') != -1 and (parsed_msg['channel'].lower().find('#dc801') != -1 or parsed_msg['channel'].find(self.nicks) != -1) != -1:
					pass
					#self.send_email(parsed_msg,self.page_number,"dc801-irc@obscuritysystems.com",parsed_msg['channel'])

	def send_email(self,parsed_msg,TO,FROM,SUBJECT):
		TEXT = parsed_msg['handle'] + ' : ' + parsed_msg['text']


		message = """\
FROM: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(TO),SUBJECT,TEXT)

		smtp_server_obj = smtplib.SMTP(self.smtp_server)
		smtp_server_obj.sendmail(FROM,TO,message)
		smtp_server_obj.quit()

#bot = NemusBotAI()
#bot.run()
