import os
import telebot
from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import json


TOKEN = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(TOKEN)

server = Flask(__name__)

def weather():

    reply = 'Weather'

    url = 'https://www.cwb.gov.tw/V7/forecast/txt/w01.htm'
    resp = requests.get(url)
    resp.encoding = 'utf8'
    soup = BeautifulSoup(resp.text, 'html.parser')

    weather_titles = soup.find('div', 'w01', 'pre')
    reply += weather_titles.text
    reply += '離開: /leave'

    return reply


def tnfshnew():

    reply = ''

    url = 'https://www.tnfsh.tn.edu.tw/files/501-1000-1012-1.php?Lang=zh-tw'
    resp = requests.get(url)
    resp.encoding = 'utf8'
    soup = BeautifulSoup(resp.text, 'html.parser')

    sesoup = soup.find_all('span', 'ptname ')

    for i in range(10):
        reply += str(i+1) + '.'
        reply += sesoup[i].find('a').string.strip('\n').strip(' ') + '\n'
        reply += sesoup[i].find('a')['href'].strip('\n').strip(' ') + '\n'

    reply += '\n\n離開: /leave'

    return reply


def get_user_id(user_id):

    print(user_id)

    path = 'users'

    ids = []

    try:
        docs = database.collection(path).get()

        for doc in docs:
            ids.append(doc.to_dict()['id'])

        if user_id not in ids:
            doc_to_add = {
                'id': user_id
            }

            doc_ref = database.document(path + '/user_' + str(user_id))
            doc_ref.set(doc_to_add)
    except:
        pass


@bot.message_handler(commands=['start', 'help', 'leave'])
def start(message):
    get_user_id(str(message.chat.id))
    print('command: /main_page')
    helpmess = '.\n這裡有部分功能可以嘗試><'
    helpmess += '\n/weather  - 查詢天氣小幫手'
    helpmess += '\n/tnfshnew - 查詢南一中新訊息'
    bot.reply_to(message, 'Hi, ' + message.from_user.first_name + helpmess)


@bot.message_handler(commands=['weather'])
def get_weather(message):
    get_user_id(str(message.chat.id))
    print('command: /weather')
    bot.reply_to(message, weather())


@bot.message_handler(commands=['tnfshnew'])
def get_tnfshnew(message):
    get_user_id(str(message.chat.id))
    print('command: /tnfshnew')
    bot.reply_to(message, tnfshnew())


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    get_user_id(str(message.chat.id))
    print(message.text)
    bot.reply_to(message, message.text)


bot.polling()


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://littlechin-tg-python.herokuapp.com/' + TOKEN)
    print('success')
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
