import sqlite3
import telebot
from telebot import types
from telebot.types import Message
from datetime import datetime
import schedule
import time
import threading

# create DataBases Methods
#
conn = sqlite3.connect("dataUser.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (chatId INTEGER, autoSend BOOLEAN, status TEXT )")
conn.commit()
conn.close()



conn = sqlite3.connect("dataJobs.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS jobs (job TEXT, status TEXT, district TEXT, timeOfJob TEXT, hours TEXT, salary TEXT, contact TEXT)")
conn.commit()
conn.close()

bot = telebot.TeleBot("5312203210:AAF088YbTAftWuMwgYJ_dF-tta7OF6IUYOE")

# Outlets and Variables

job = ''
status = ''
timeOfJob = ''


# ViewsMethods
def viewSpecialJobs(status_job):
  # added
  delete()
  conn = sqlite3.connect("dataJobs.db")
  cur = conn.cursor()
  cur.execute("SELECT job,status,district,timeOfJob,hours,salary,contact FROM jobs WHERE status = ? " , (status_job,))
  rows = cur.fetchall()
  conn.close()
  return rows


# поиск среди всех работ
def viewAllJobs():
  conn = sqlite3.connect("dataJobs.db")
  cur = conn.cursor()
  cur.execute("SELECT job,status,district,timeOfJob,hours,salary,contact FROM jobs")
  rows = cur.fetchall()
  conn.close()
  return rows



# поиск пользователей
def viewUsers():
  conn = sqlite3.connect("dataUser.db")
  cur = conn.cursor()
  cur.execute("SELECT chatId, autoSend FROM users")
  rows = cur.fetchall()
  conn.close()
  return rows
#cleanDataBaseMethod


def delete():
  date = datetime.today().strftime('%d.%m.%Y')
  nowdate = datetime.today().strptime(date,'%d.%m.%Y')
  conn = sqlite3.connect("dataJobs.db")
  cur = conn.cursor()
  cur.execute("SELECT * FROM jobs")
  rows = cur.fetchall()
  for i in rows:
      jobdate = datetime.strptime(i[3], '%d.%m.%Y')
      if jobdate < nowdate:
          conn = sqlite3.connect("dataJobs.db")
          cur = conn.cursor()
          cur.execute("DELETE FROM jobs WHERE timeOfJob=?", (i[3],))
          conn.commit()
          conn.close()

# job TEXT, status TEXT, district TEXT, timeOfJob TEXT, hours TEXT, salary TEXT, contact TEXT
def insertToDB(job,status,district,timeOfJob,hours,salary,contact):
  now = datetime.today()
  timeOfJob = timeOfJob + '.' + str(now.year)
  print(timeOfJob)
  conn = sqlite3.connect("dataJobs.db")
  cur = conn.cursor()
  cur.execute("INSERT INTO jobs VALUES (?,?,?,?,?,?,?)",(job,status,district,timeOfJob,hours,salary,contact))
  conn.commit()
  conn.close()

def insertChatId(chatId, autoSend, status):
  conn = sqlite3.connect("dataUser.db")
  cur = conn.cursor()
  cur.execute("INSERT INTO users VALUES(?,?,?)",(chatId,autoSend,status))
  print("Inserting is good")
  conn.commit()
  conn.close()

# DoubleCheck of UserId

def doubleCheckId(numId):
  conn = sqlite3.connect("dataUser.db")
  cur = conn.cursor()
  cur.execute("SELECT chatId FROM users")
  rows = cur.fetchall()
  checkExistedId = False
  for i in rows:
      for var in i:
          print(var)
          if var == numId:
              print("Id already exists")
              checkExistedId = True
  return checkExistedId




#autoSending Functions
def func_send(userId,status):
  for i in viewSpecialJobs(status):
      jobString = ''
      for var in i:
          jobString = jobString + " " + var
      try:
          bot.send_message(userId, jobString)
      except:
          print("User blocked Bot")
  # bot.send_message(userId, "Привет авто!")
  print("Schedule")


def subscribing():
  while True:
      conn = sqlite3.connect("dataUser.db")
      cur = conn.cursor()
      cur.execute("SELECT chatId, status FROM users WHERE autoSend = ?", (True,))
      rows = cur.fetchall()
      for i in rows:
          schedule.every(5).minutes.do(func_send,i[0],i[1]).tag(i[0])
          # for var in i:
          #     # print(var)
          #     print(i[0])
          #     print(i[1])
          #     # schedule.every().day.at("20:00").do(func_send,i[0],i[1]).tag(var)
          #         # func_send(var)
      print(rows)
      conn.close()
      while True:
          print("While")
          schedule.run_pending()
          time.sleep(1)



@bot.message_handler(content_types=['text'])
@bot.message_handler(commands=['start','reg','endSubscribe'])
def inlineBtn(message: Message):
  chatNum = message.chat.id
  # Doublecheck and Inserting Id of User
  checkId = doubleCheckId(chatNum)
  if checkId == False:
      insertChatId(chatNum,False,'None')
      print("Id Inserted Succesfully")

  for i in viewUsers():
      for var in i:
          print(var)
  if message.text == '/start':

      delete()
      bot.send_message(message.chat.id,"Привет, Мы поможем найти тебе работу!")
      bot.send_message(message.chat.id, "Если вы роботодатель, напишите /reg")
      keyboard = types.InlineKeyboardMarkup()
      btn1 = types.InlineKeyboardButton(text="Работу", callback_data = "Full_time")
      btn2 = types.InlineKeyboardButton(text="Подработку", callback_data = "Part_time")
      keyboard.add(btn1, btn2)
      bot.send_message(message.chat.id, "Привет, ищешь работу или подработку?", reply_markup=keyboard)
  elif message.text == '/reg':
      bot.send_message(message.chat.id,"Привет) Давай по порядку.")
      delete()
      keyboard = types.InlineKeyboardMarkup()
      btn1 = types.InlineKeyboardButton(text="Полное", callback_data="Full_time1")
      btn2 = types.InlineKeyboardButton(text="Подработка", callback_data="Part_time1")
      keyboard.add(btn1, btn2)
      bot.send_message(message.chat.id, "Какое время работы кандидата", reply_markup=keyboard)
      bot.register_next_step_handler(message, get_job)
  elif message.text == '/statistic':
      conn = sqlite3.connect("dataUser.db")
      cur = conn.cursor()
      cur.execute("SELECT chatId FROM users WHERE status = ?", ('Men(FullTime)',))
      rowsMenFullTime = len(cur.fetchall())
      cur.execute("SELECT chatId FROM users WHERE status = ?", ('Men(PartTime)',))
      rowsMenPartTime = len(cur.fetchall())
      cur.execute("SELECT chatId FROM users WHERE status = ?", ('Women(FullTime)',))
      rowsWomenFullTime = len(cur.fetchall())
      cur.execute("SELECT chatId FROM users WHERE status = ?", ('Women(PartTime)',))
      rowsWomenPartTime = len(cur.fetchall())
      bot.send_message(message.chat.id,"nМужчина или Женщина - %s;"%(rowsMenFullTime,rowsMenPartTime,rowsWomenFullTime,rowsWomenPartTime))

  elif message.text == '/endsubscribe':
      conn = sqlite3.connect("dataUser.db")
      cur = conn.cursor()
      cur.execute("UPDATE users SET autoSend = ? WHERE chatId = ? ", (False, message.chat.id))
      conn.commit()
      conn.close()
      bot.send_message(message.chat.id, "Вы отписались от получения новых уведомлений!")
      schedule.clear(message.chat.id)
  elif message.text == '/subscribeAnyone':
      conn = sqlite3.connect("dataUser.db")
      cur = conn.cursor()
      cur.execute("UPDATE users SET autoSend = ? WHERE chatId = ? ", (True, message.chat.id))
      cur.execute("UPDATE users SET status = ? WHERE chatId = ? AND autoSend = ? ", ('Anyone', message.chat.id, True))
      conn.commit()
      conn.close()
      schedule.every(5).minutes.do(func_send,message.chat.id,'Anyone').tag(message.chat.id)
      bot.send_message(message.chat.id, "Поздравляем вы подписались на ежедневную рассылку! Чтобы отписаться введите команду /endsubscribe")

  elif message.text == '/subscribeMenFullTime':
      conn = sqlite3.connect("dataUser.db")
      cur = conn.cursor()
      cur.execute("UPDATE users SET autoSend = ? WHERE chatId = ? ", (True, message.chat.id))
      cur.execute("UPDATE users SET status = ? WHERE chatId = ? AND autoSend = ? ", ('Men(FullTime)', message.chat.id, True))
      conn.commit()
      conn.close()
      schedule.every(5).minutes.do(func_send,message.chat.id,'Men(FullTime)').tag(message.chat.id)
      bot.send_message(message.chat.id, "Поздравляем вы подписались на ежедневную рассылку! Чтобы отписаться введите команду /endsubscribe")

  elif message.text == '/subscribeWomenFullTime':
      conn = sqlite3.connect("dataUser.db")
      cur = conn.cursor()
      cur.execute("UPDATE users SET autoSend = ? WHERE chatId = ? ", (True, message.chat.id))
      cur.execute("UPDATE users SET status = ? WHERE chatId = ? AND autoSend = ? ", ('Women(FullTime)', message.chat.id, True))
      conn.commit()
      conn.close()
      schedule.every(5).minutes.do(func_send,message.chat.id,'Women(FullTime)').tag(message.chat.id)
      bot.send_message(message.chat.id, "Поздравляем вы подписались на ежедневную рассылку! Чтобы отписаться введите команду /endsubscribe")

  elif message.text == '/subscribeMenPartTime':
      conn = sqlite3.connect("dataUser.db")
      cur = conn.cursor()
      cur.execute("UPDATE users SET autoSend = ? WHERE chatId = ? ", (True, message.chat.id))
      cur.execute("UPDATE users SET status = ? WHERE chatId = ? AND autoSend = ? ", ('Men(PartTime)', message.chat.id, True))
      conn.commit()
      conn.close()
      schedule.every(5).minutes.do(func_send,message.chat.id,'Men(PartTime)').tag(message.chat.id)
      bot.send_message(message.chat.id, "Поздравляем вы подписались на ежедневную рассылку! Чтобы отписаться введите команду /endsubscribe")

  elif message.text == '/subscribeWomenPartTime':
      conn = sqlite3.connect("dataUser.db")
      cur = conn.cursor()
      cur.execute("UPDATE users SET autoSend = ? WHERE chatId = ? ", (True, message.chat.id))
      cur.execute("UPDATE users SET status = ? WHERE chatId = ? AND autoSend = ? ", ('Women(PartTime)', message.chat.id, True))
      conn.commit()
      conn.close()
      schedule.every(5).minutes.do(func_send,message.chat.id,'Women(PartTime)').tag(message.chat.id)
      bot.send_message(message.chat.id, "Поздравляем вы подписались на ежедневную рассылку! Чтобы отписаться введите команду /endsubscribe")



@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
  if call.data == "Full_time":
      keyboard = types.InlineKeyboardMarkup()
      btn1 = types.InlineKeyboardButton(text="Мужчина", callback_data = "MenFullTime")
      btn2 = types.InlineKeyboardButton(text="Женщина", callback_data = "WomenFullTime")
      keyboard.add(btn1, btn2)
      bot.send_message(call.message.chat.id, "Выбери пол?", reply_markup=keyboard)

  elif call.data == "Part_time":
      keyboard = types.InlineKeyboardMarkup()
      btn1 = types.InlineKeyboardButton(text="Мужчина", callback_data = "MenPartTime")
      btn2 = types.InlineKeyboardButton(text="Женщина", callback_data = "WomenPartTime")
      keyboard.add(btn1, btn2)
      bot.send_message(call.message.chat.id, "Выбери пол?", reply_markup=keyboard)

  elif call.data == "MenFullTime":
      try:
          for i in viewSpecialJobs('Men(FullTime)'):
              jobString = ''
              for var in i:
                  jobString = jobString + " " + var
              bot.send_message(call.message.chat.id, jobString)
      except:
          bot.send_message(call.message.chat.id, "Пока что нет работы")
      bot.send_message(call.message.chat.id, "Хочешь получать рассылку - напиши - \n/subscribeMenFullTime")

  elif call.data == "WomenFullTime":
      try:
          for i in viewSpecialJobs('Women(FullTime)'):
              jobString = ''
              for var in i:
                  jobString = jobString + " " + var
          bot.send_message(call.message.chat.id, jobString)
      except:
          bot.send_message(call.message.chat.id, "Пока что нет работы")
      bot.send_message(call.message.chat.id, "Хочешь получать рассылку - напиши - \n/subscribeWomenFullTime")

  elif call.data == "MenPartTime":
     try:
         for i in viewSpecialJobs('Men(PartTime)'):
             jobString = ''
             for var in i:
                 jobString = jobString + " " + var
         bot.send_message(call.message.chat.id, jobString)
     except:
         bot.send_message(call.message.chat.id, "Пока что нет работы")
     bot.send_message(call.message.chat.id, "Хочешь получать рассылку - напиши - \n/subscribeMenPartTime")

  elif call.data == "WomenPartTime":
      try:
          for i in viewSpecialJobs('Women(PartTime)'):
              jobString = ''
              for var in i:
                  jobString = jobString + " " + var
          bot.send_message(call.message.chat.id, jobString)
      except:
          bot.send_message(call.message.chat.id, "Пока что нет работы")
      bot.send_message(call.message.chat.id, "Хочешь получать рассылку - напиши - \n/subscribeWomenPartTime")
  elif call.data == "Part_time1":
      keyboard = types.InlineKeyboardMarkup()
      btn1 = types.InlineKeyboardButton(text="Мужчина", callback_data="MenPartTime1")
      btn2 = types.InlineKeyboardButton(text="Женщина", callback_data="WomenPartTime1")
      keyboard.add(btn1, btn2)
      bot.send_message(call.message.chat.id, "Пол кандидата", reply_markup=keyboard)

  elif call.data == "Full_time1":
      keyboard = types.InlineKeyboardMarkup()
      btn1 = types.InlineKeyboardButton(text="Мужчина", callback_data="MenFullTime1")
      btn2 = types.InlineKeyboardButton(text="Женщина", callback_data="WomenFullTime1")
      keyboard.add(btn1, btn2)
      bot.send_message(call.message.chat.id, "Пол кандидата", reply_markup=keyboard)
if __name__ == "__main__":
  threading.Thread(target=subscribing).start()
  while True:
      try:
          bot.polling(none_stop=True, interval=0, timeout=20)
          print('polling')
      except Exception:
          print(Exception)
          time.sleep(15)
          continue

