#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a simple echo bot using decorators and webhook with CherryPy
# It echoes any incoming text messages and does not use the polling method.

import logging

import cherrypy

import telebot

from constants import *


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(TOKEN)


# WebhookServer, process webhook calls
class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message,
                 ("Hi there, I am EchoBot.\n"
                  "I am here to echo your kind words back to you."))


# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, message.text)


# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(url=URL + PATH,
                certificate=open(SSL_CERTIFICATE, 'r'))

# Disable CherryPy requests log

# Start cherrypy server
cherrypy.config.update({
    'server.socket_host'    : LISTEN,
    'server.socket_port'    : PORT,
    'server.ssl_module'     : 'builtin',
    'server.ssl_certificate': SSL_CERTIFICATE,
    'server.ssl_private_key': SSL_KEY
})

cherrypy.quickstart(WebhookServer(), PATH, {'/': {}})
