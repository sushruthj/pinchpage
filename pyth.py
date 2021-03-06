from io import BytesIO
import urllib
import isbnlib
from isbnlib import *

import cv2
from pyzbar.pyzbar import decode
import time
import requests
import telebot
import telegram
import zbar
import zbar.misc
import pathlib
import pygame
from telegram.ext import Updater
from telebot import types
import numpy as np
from PIL import Image

TOKEN = '1061731390:AAGCU813ySLv2OqioBfLuJz7B8-bkW3tqmw'

knownUsers = []  # todo: save these in a file,
userStep = {}  # so they won't reset every time the bot restarts

commands = {  # command description used in the "help" command
    'start'       : 'Get used to the bot',
    'help'        : 'Gives you information about the available commands',
    'sendLongText': 'A test using the \'send_chat_action\' command',
    'getImage'    : 'A test using multi-stage messages, custom keyboard, and media sending'
}

imageSelect = types.ReplyKeyboardMarkup(one_time_keyboard=True)  # create the image selection keyboard
imageSelect.add('Mickey', 'Minnie')

hideBoard = types.ReplyKeyboardRemove()  # if sent as reply_markup, will hide the keyboard


# error handling if user isn't known yet
# (obsolete once known users are saved to file, because all users
#   had to use the /start command and are therefore known to the bot)
def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        knownUsers.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


# only used for console output now
def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        if m.content_type == 'text':
            # print the sent message to the console
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)
        elif m.content_type == 'photo':
            print ("Photo Received")


bot = telebot.TeleBot(TOKEN)
bot.set_update_listener(listener)  # register listener


# handle the "/start" command
@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    if cid not in knownUsers:  # if user hasn't used the "/start" command yet:
        knownUsers.append(cid)  # save user id, so you could brodcast messages to all users of this bot later
        userStep[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" command
        bot.send_message(cid, "Hello, stranger, let me scan you...")
        bot.send_message(cid, "Scanning complete, I know you now")
        command_help(m)  # show the new user the help page
    else:
        bot.send_message(cid, "I already know you, no need for me to scan you again!")


# help page
@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "The following commands are available: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)  # send the generated help page


# chat_action example (not a good one...)
@bot.message_handler(commands=['sendLongText'])
def command_long_text(m):
    cid = m.chat.id
    bot.send_message(cid, "If you think so...")
    bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
    time.sleep(3)
    bot.send_message(cid, ".")


# user can chose an image (multi-stage command example)
@bot.message_handler(commands=['getImage'])
def command_image(m):
    cid = m.chat.id
    bot.send_message(cid, "Please choose your image now", reply_markup=imageSelect)  # show the keyboard
    userStep[cid] = 1  # set the user to the next step (expecting a reply in the listener now)


# if the user has issued the "/getImage" command, process the answer
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 1)
def msg_image_select(m):
    cid = m.chat.id
    text = m.text

    # for some reason the 'upload_photo' status isn't quite working (doesn't show at all)
    bot.send_chat_action(cid, 'typing')

    if text == 'Mickey':  # send the appropriate image based on the reply to the "/getImage" command
        bot.send_photo(cid, open('rooster.jpg', 'rb'),
                       reply_markup=hideBoard)  # send file and hide keyboard, after image is sent
        userStep[cid] = 0  # reset the users step back to 0
    elif text == 'Minnie':
        bot.send_photo(cid, open('kitten.jpg', 'rb'), reply_markup=hideBoard)
        userStep[cid] = 0
    else:
        bot.send_message(cid, "Please, use the predefined keyboard!")
        bot.send_message(cid, "Please try again")


# filter on a specific message
@bot.message_handler(func=lambda message: message.text == "hi")
def command_text_hi(m):
    bot.send_message(m.chat.id, "I love you too!")


# default handler for every other text
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    # this is the standard reply to a normal message
    bot.send_message(m.chat.id, "I don't understand \"" + m.text + "\"\nMaybe try the help page at /help")
    
@bot.message_handler(func=lambda message: True, content_types=['photo'])
def command_default(m):
    # this is the standard reply to a normal message
    bot.send_message(m.chat.id, "Let me search for it.")
    fileID = m.photo[-1].file_id
    print(fileID)
    file_info = bot.get_file(fileID)
    file ="https://api.telegram.org/file/bot"+TOKEN+"/"+file_info.file_path
    #bot.send_message(m.chat.id, file)
    
    filename=file_info.file_path
    print (filename)

    
    outfile="./home/susruthanvesh/tbt/pics/"+fileID+".jpeg"  
    urllib.urlretrieve(file, "xyz.jpeg")  
    
    decodeval=(decode(Image.open('xyz.jpeg')))
    bardata=decodeval[0].data
    #print bardata
    image = cv2.imread('xyz.jpeg')
   #cv2.imshow("xyz.jpeg", image)
    cv2.waitKey(0)
    barcodes = decode(image)
    print barcodes
    #barcodeDatap = barcode.data.decode("utf-8")
    #isbndata=editions(barcodeDatap, service='merge')  
    #print isbndata
    for barcode in barcodes:
        (x,y,w,h) = barcode.rect
        cv2.rectangle(image, (x,y), (x+w, y+h), (0, 0, 255), 2)
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
        
        
        
        text = "{} ({})".format(barcodeData, barcodeType)
        textisb="{}".format(barcodeData)
        descrp=isbnlib.meta(barcodeData, service='goob')
        print barcodeData
        print(descrp)
        book=descrp['Title']
        author=descrp['Authors']
       # des=isbnlib.desc(barcodeData)
       # print ("this is about: "+ des)
        
        
        
        cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        r = requests.get('http://openlibrary.org/api/books?bibkeys=ISBN:'+barcodeData+"&format=json&jscmd=data")
     #   print("This is supposedly: "+r.json()['ISBN:'+barcodeData]['title'])
     #   print('----by----')
     #   print(r.json()['ISBN:'+barcodeData]['authors'][0]['name'])
        bot.send_message(m.chat.id, "This ISBN is supposedly: "+book+' by '+'author')
       # bot.send_message(m.chat.id, "Read about it at: "+'http://openlibrary.org/api/books?bibkeys=ISBN:'+barcodeData+"&format=json&jscmd=data")
            
    
    
    
  #  photo = open('xyz.jpeg', 'rb')
  #  bot.send_photo(m.chat.id, photo)
    
    
bot.polling()
