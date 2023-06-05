import telebot
import os
import JoJoSiteParse
from telebot import types
import sqlite3 as sql
import searchManga
import settings

bot = telebot.TeleBot(settings.BOT_TOKEN)

checker = os.path.exists('userSubs.db')
sqlite_connection = sql.connect('userSubs.db', check_same_thread=False)
cursor = sqlite_connection.cursor()

sqlite_create_table_query = '''CREATE TABLE IF NOT EXISTS userSubs (
                                   userid INTEGER,
                                   sub VARCHAR NOT NULL);'''
cursor.execute(sqlite_create_table_query)
sqlite_connection.commit()

sqlite_create_table_query = '''CREATE TABLE IF NOT EXISTS urls (
                                   title VARCHAR PRIMARY KEY,
                                   url VARCHAR NOT NULL);'''
cursor.execute(sqlite_create_table_query)
sqlite_connection.commit()


@bot.message_handler(commands=['start'])
def start_message(message):
    a = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Manga")
    a.add(item1)
    bot.send_message(message.chat.id, 'Hello, this bot will update you on new chapters of your favorite manga!\n'
                                      "Type /manga to get choosin'\n"
                                      "/help to get help on our commands", reply_markup=a)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'This is a bot that for now tells you the latest chapter of a manga\n\n'
                                      'Type in the name of the manga and after choose your desired title from the list'
                                      '\n\n/manga to choose out of your manga\n'
                                      '/add to subscribe to a title\n'
                                      '/del to unsubscribe from a title')


def answer_anyManga(message):
    bot.send_message(message.chat.id, 'Wait a minute... Fetching data...')
    info = cursor.execute('SELECT url FROM urls WHERE title=?', (message.text,))
    data = info.fetchone()

    a, b = JoJoSiteParse.parseSite(data[0])

    a = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Manga")
    a.add(item1)
    bot.send_message(message.chat.id, b, reply_markup=a)


@bot.message_handler(commands=['manga'])
def answer_manga(message):
    info = cursor.execute('SELECT sub FROM userSubs WHERE userid=?', (message.from_user.id,))
    data = info.fetchall()
    print(data)

    if data == None:
        bot.send_message(message.chat.id, 'You dont have any manga yet, try /add to add some to your sub list!')
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for el in data:
        item = types.KeyboardButton(el[0])
        markup.add(item)

    bot.send_message(message.chat.id, 'What manga do you want to get an update on?', reply_markup=markup)


@bot.message_handler(commands=['del'])
def del_sub(message):
    if message.text == "/del":
        info = cursor.execute('SELECT sub FROM userSubs WHERE userid=?', (message.from_user.id,))
        data = info.fetchall()
        if data == None:
            msg = bot.send_message(message.chat.id, "You dont have any titles added yet, "
                                                    "you can't unsub from anything yet ;)")
            return
        mess = "Type the number that correlates to the title you would like to delete?\n\n"
        counter = 1
        for sub in data:
            mess = mess + str(counter) + ". " + sub[0] + "\n"
            counter += 1
        mess = mess + "\n(If you would like to cancel unsubscribing, type 0)"
        msg = bot.send_message(message.chat.id, mess)
        bot.register_next_step_handler(msg, cancel_sub)


def cancel_sub(message):
    if message.text == '0':
        bot.send_message(message.chat.id, "Process of unsubscribing cancelled...")
        return
    try:
        number = int(message.text) - 1
        info = cursor.execute('SELECT sub FROM userSubs WHERE userid=?', (message.from_user.id,))
        data = info.fetchall()

        title = data[number][0]

        sqlite_delete_with_param = 'DELETE FROM userSubs WHERE userid=? AND sub=?'
        data_tuple = (message.from_user.id, title)
        cursor.execute(sqlite_delete_with_param, data_tuple)
        sqlite_connection.commit()

        msg = bot.send_message(message.chat.id, "Successfully unsubscribed from " + title + "!")
    except Exception:
        msg = bot.send_message(message.chat.id, "Try another number, if you can't find your manga, type 0")
        bot.register_next_step_handler(msg, cancel_sub)


@bot.message_handler(commands=['add'])
def add_sub(message):
    if message.text == "/add":
        msg = bot.send_message(message.chat.id, "Now send what title you are looking for\n\n"
                                                "(If you would like to cancel to process of subscribing, type 0)")
        bot.register_next_step_handler(msg, add_sub_choice)


def add_sub_choice(message):
    if message.text == '0':
        bot.send_message(message.chat.id, "Process of subscribing cancelled...")
        return

    title = message.text
    bot.send_message(message.chat.id, "Okay, let me find the results of *" + title + "*...", parse_mode="Markdown")
    options = searchManga.search(title)
    if len(options) == 0:
        msg = bot.send_message(message.chat.id, "Couldn't find anything for *" + title + "*\nTry another name:")
        bot.register_next_step_handler(msg, add_sub_choice)
        return
    list = "Now send a number that correlates to the desired title\n\n"
    counter = 1
    for opt in options:
        list = list + str(counter) + ". " + opt["title"].strip() + "\n"
        counter = counter + 1
        # print(list)
    list = list + "\nIf you cannot find your title here, type 0"
    msg = bot.send_message(message.chat.id, list)
    bot.register_next_step_handler(msg, add_finale, options, cursor)


def add_finale(message, options, curs):
    if message.text == '0':
        bot.send_message(message.chat.id, "Sorry I couldn't find your manga ;(")
        return
    try:
        number = int(message.text)
        title = options[number - 1]["title"].strip()
        print(title)
        info = cursor.execute('SELECT sub FROM userSubs WHERE userid=?', (message.from_user.id,))
        data = info.fetchall()
        print("--------")
        print(title)
        print(data)
        print("--------")
        if data != [] and (title,) in data:
            msg = bot.send_message(message.chat.id, "You are already subbed to this title\n"
                                                    "If you want to unsubscribe, type /del")
        else:
            sqlite_insert_with_param = """INSERT INTO userSubs
                                                          (userid, sub)
                                                          VALUES (?, ?);"""
            data_tuple = (message.from_user.id, title)
            curs.execute(sqlite_insert_with_param, data_tuple)
            sqlite_connection.commit()

            url_info = curs.execute('SELECT * FROM urls WHERE title=?', (title,))
            data = url_info.fetchone()
            if data == None:
                sqlite_insert_with_param = """INSERT INTO urls
                                                              (title, url)
                                                              VALUES (?, ?);"""
                data_tuple = (title, "https://mangareader.to" + options[number - 1]["href"])
                curs.execute(sqlite_insert_with_param, data_tuple)
                sqlite_connection.commit()

            msg = bot.send_message(message.chat.id, "Successfully subbed to " + title + "!")
    except Exception:
        msg = bot.send_message(message.chat.id, "Try another number, if you can't find your manga, type 0")
        bot.register_next_step_handler(msg, add_finale, options, curs)


@bot.message_handler(content_types='text')
def message_reply(message):
    info = cursor.execute('SELECT url FROM urls WHERE title=?', (message.text,))
    data = info.fetchone()
    print(data)

    if message.text.lower() == "manga":
        answer_manga(message)
    elif data != None:
        answer_anyManga(message)


bot.polling(none_stop=True)
