# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.


import os
import sys
from argparse import ArgumentParser
import psycopg2
from datetime import datetime

from flask import Flask, request, abort ,render_template ,redirect, request
import requests
from linebot import (
    LineBotApi, WebhookParser,WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,FollowEvent, ImageSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction,
    CarouselTemplate, CarouselColumn, FlexSendMessage, BubbleContainer, BoxComponent, ImageComponent, TextComponent, ButtonComponent, SeparatorComponent,
    PostbackEvent, QuickReply, QuickReplyButton, MessageAction,URIAction 

)


app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True




@app.route('/')
def hello_world():

    return 'Hello, World!'

@app.route('/profile')
def profile():
    
    return render_template('profile.html')


@app.route('/callback')
def callback():
    code = request.args.get('code')

    # Exchange the authorization code for an access token
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': '1661524605',
        'client_secret': 'c4ceab5e11eab903babfdaf38edb58f4',
        'redirect_uri': 'https://liff.line.me/1661524605-5Z902Yep'
    }

    response = requests.post('https://api.line.me/oauth2/v2.1/token', data=payload)
    if response.status_code == 200:
        access_token = response.json()['access_token']

        # Use the access token to retrieve user information
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        user_response = requests.get('https://api.line.me/v2/profile', headers=headers)
        if user_response.status_code == 200:
            user_info = user_response.json()
            # You can now use the user_info to authenticate the user in your web application
            # For example, you can store the user's LINE ID or display name in your database

            return 'Login successful'
    
    return 'Login failed'


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)