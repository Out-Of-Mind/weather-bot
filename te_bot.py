from configparser import ConfigParser, NoSectionError
from string import Template
import requests
import json
import os

class CannotFindUser(Exception):
	def __init__(self, text):
		self.text = text

class WrongResponse(Exception):
	def __init__(self, response):
		print('\nResponse from telegram is ' + str(response) + '\n')

class Bot():
	def __init__(self, path_to_configfile):
		self.config = config = ConfigParser()

		# "config.ini" it's yours config file
		self.config.read(path_to_configfile)

		try:
			# here we're geting token from config.ini
			self.token = config.get("default", "token")
		except NoSectionError:
			print('Cannot find section [default]\n or file config.ini isn\'t in this dirrectory')
			exit()

		# our url	
		self.URL = "https://api.telegram.org/bot{}/".format(self.token)

		# count of users from config.ini
		try:
			self.users_count = self.config["allowed-users"]["users_count"]
		except NoSectionError:
			print('Cannot find section [allowed-users]\n or file config.ini isn\'t in this dirrectory')
			exit()

		if self.users_count == '*':
			pass
		else:
			# make a list for users
			self.users = [i for i in range(0,int(self.users_count))]
			# add to list users
			try:
				for user in range(0,int(self.users_count)):
					self.users[user] = self.config["allowed-users"]["user"+str(user)]
			except KeyError:
					print("User_count is defined bad")
					exit()


	# send message 
	def send_message(self, chat_id, text='hi, I\'ve just start working'):
		answer = {'chat_id': chat_id, 'text': text}
		r = requests.post(self.URL + "sendmessage", json=answer)
		if not str(r)[11:14] == '200':
			raise WrongResponse(str(r)[11:14])

	# checking permission for user
	def have_permission(self, user_id):
		def inner(chat_id, text):
			if not self.users_count == '*':
				permission = False
				for u in range(0,int(self.users_count)):
					if int(user_id) == int(self.users[int(u)]):
						permission = True 
						self.send_message(chat_id, text)
						break
				else:	
					if not permission:
						self.send_message(chat_id, text='403 forbidden')
			else:
				self.send_message(chat_id, text)
		return inner

	# forward message from from_chat_id to chat_id with message_id
	def forward_message(self, chat_id, from_chat_id, message_id, disable_notification=False):
		url = self.URL + 'forwardmessage?' + 'chat_id=' + str(chat_id) + '&' + 'from_chat_id=' + str(from_chat_id) + 'disable_notification=' + str(disable_notification) + '&' + 'message_id=' + str(message_id)
		r = requests.get(url)
		if not str(r)[11:14] == '200':
			raise WrongResponse(str(r)[11:14])

	# send photo to chat id with photo path = url or telegram path or via file id
	def send_photo(self, chat_id, photo_path, caption=None, disable_notification=False, reply_to_message_id=None):
		url = self.URL + 'sendphoto?' + 'chat_id=' + str(chat_id) + '&' + 'photo=' + str(photo_path)
		if caption:
			url += '&' + 'caption=' + str(caption)
		if reply_to_message_id:
			url += '&' + 'reply_to_message_id=' + str(reply_to_message_id)
		url += '&' + 'disable_notification=' + str(disable_notification)
		r = requests.get(url)
		if not str(r)[11:14] == '200':
			raise WrongResponse(str(r)[11:14])

	# getting updates
	def get_updates(self):
		r = requests.get(self.URL + 'getupdates')
		return r.json()

	def answer_inline_query(self, inline_query_id, title, message_text, description):
		results = Template('[{"type": "article", "id": "1", "title": "$title", "input_message_content": {"message_text": "$message_text"}, "description": "$description"}]')
		re = {'inline_query_id': inline_query_id, 'results': results.substitute(title=title, message_text=message_text, description=description)}
		r = requests.post(self.URL+'answerInlineQuery', params=re)
		return r

