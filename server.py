from flask import Flask
from flask import request, render_template, jsonify
from te_bot import Bot
import requests
import pyowm
import json

app = Flask(__name__)
owm = pyowm.OWM('59a52b5d66e49cdcddafa6048e51cb41', language='ru')
bot = Bot("/home/Gene1989/Weather-bot/config.ini")

def tempt(message):
	obs = owm.weather_at_place(message)
	w = obs.get_weather()
	temp = w.get_temperature('celsius')['temp']
	return temp

def get_temp(message):
	try:
		obs = owm.weather_at_place(message)
		w = obs.get_weather()
		temp = w.get_temperature('celsius')['temp']
		answer = 'В городе ' + message + ' сейчас ' + w.get_detailed_status() + '\n'
		answer += 'Температура сейчас в районе: ' + str(temp) + '\n\n'
		if not message == 'Ухань':
			if temp < 0:
				answer += 'На улице мороз, одевай пуховик!'
			elif temp < 5:
				answer += 'Холодина на улице одевайся тепло!'
			elif temp < 10:
				answer += 'Уххх, холодно...Одевайся в пальто!'
			elif temp < 15:
				answer += 'Без тёплой куртки не выходить.'
			elif temp < 20:
				answer += 'Лучше одеть ветровку.'
			elif temp < 25:
				answer += 'Одевайся легко!!!'
			elif temp < 30:
				answer += 'На улице жарко, выходи в шортах с майкой'
			elif temp < 35:
				answer += 'Кааапец как жарко, на улицу лучше не выходить!!!'
			else:
				answer += 'Срочно ледянной душ и две порции мохито со льдом!!!'
			return answer
		else:
			answer = 'Что ты забыл в Ухани?\nБез хим-защиты не выходи!!!!'
			return answer
	except Exception as e:
		answer = 'Не могу найти город ' + message
		with open('error.log', 'a') as f:
			f.write(str(e)+'\n\n')
			f.close()
		return answer

def global_main(r):
	try:
		inline_query_id = r['inline_query']['id']
		if r['inline_query']['query'] == '':
			pass
		else:
			message = r['inline_query']['query']
			answer = get_temp(message)
			if 'Не могу' in answer:
				bot.answer_inline_query(inline_query_id, message, answer, 'Такого города нет')
			temp = tempt(message)
			if temp < 0:
				t = '-{}°С'.format(str(int(temp)))
			elif temp > 0:
				t = '+{}°С'.format(str(int(temp)))
			else:
				t = '{}°С'.format(str(int(temp)))
		r = bot.answer_inline_query(inline_query_id, message, answer, t)
	except:
		pass

def main(r):
	chat_id = r['message']['chat']['id']
	try:
		if r['message']['chat']['type'] == 'supergroup' or r['message']['chat']['type'] == 'group':
			pos = r['message']['text'].find('@wbot')
			pos1 = r['message']['text'].find('@weather_for_you_bot')
			if not pos == -1:
				message = r['message']['text'][:pos]
			elif not pos1 == -1:
				message = r['message']['text'][:pos1]
			else:
				message = None
		else:
			pos = None
			message = r['message']['text']
	except KeyError:
		message = None
	try:
		user_name = r['message']['from']['username']
	except KeyError:
		user_name = r['message']['from']['first_name']
	user_id = chat_id
	if message == '/start':
		bot.send_message(chat_id, "Привет, {}\nЯ умею показывать погоду".format(user_name))
		bot.send_message(chat_id, 'Введите город:')
		with open('stat.log', 'r') as f:
			u = f.read()
			if not u.find(user_name) == -1:
				f.close()
			else:
				with open('stat.log', 'a') as l:
					l.write(user_name+', ')
					l.close()
	elif message == '/help':
		if r['message']['chat']['type'] == 'private':
			bot.send_message(chat_id, 'Просто введите город:')
		elif not pos == -1 or not pos1 == -1:
			bot.send_message(chat_id, 'Просто введите город \nс @wbot в конце\nПример: Киев@wbot')
		else:
			bot.send_message(chat_id, 'Вы нашли баг просьба написать в инстаграм @kir_thunder')
	elif message == '/privacy':
		answer = 'Приватная политика: \nчто о мне хранит этот бот? \n1.Бот хранит только ваш юзернейм \n2.Любые другие данные нигде не хранятся \n3.В целях безопастности не сообщайте боту любые личные данные \n(пароли, логины, мобильные номера) \n4.Юзернеймы хранятся исключительно в целях составления статистики'
		bot.send_message(chat_id, answer)
	elif message == '/statistics':
		with open('stat.log', 'r') as f:
			u = f.read()
			bot.have_permission(chat_id)(chat_id, u)
			f.close()
	elif message:
		answer = get_temp(message)
		bot.send_message(chat_id, answer)
		with open('stat.log', 'r') as f:
			u = f.read()
			if not u.find(user_name) == -1:
				f.close()
			else:
				with open('stat.log', 'a') as l:
					l.write(user_name+', ')
					l.close()
	else:
		pass
	return jsonify(r)



@app.route('/', methods=['POST', 'GET'])
def index():
	if request.method == 'POST':
		r = request.get_json()
		try:
			trying = r['message']['chat']['id']
			main(r)
		except Exception as e:
			try:
				trying = r['inline_query']['id']
				global_main(r)
			except Exception as e:
				print(e)
	return 'hi'


if __name__ == '__main__':
	app.run()