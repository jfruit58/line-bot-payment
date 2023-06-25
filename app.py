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


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)


line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)
handler = WebhookHandler(channel_secret)




@app.route('/')
def hello_world():

    return 'Hello, World!'

@app.route('/profile')
def profile():
    
    return render_template('profile.html')

@app.route("/chatbot", methods=['POST'])
def chatbot():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)

    greeting_message = "สวัสดีค่ะ!😊 " + profile.display_name + " ขอบคุณที่เป็นเพื่อนกับเรา. \n\n ยินดีตอนรับสู่ JPBeauty's Line Official Channel, 🥳\n\n ✨JPBeauty ยินดีที่ได้เป็นตัวเลือกในการช่วยให้คุณสามารถ🛒ช๊อปปี้สินค้าหลายรายการจาก duty free ทั่วโลกอย่างสะดวกสบายโดยไม่ต้องเดินทาง✈️ \n\n🌈 ไม่ว่าจะเป็นสินค้าชนิดใด ทีมของเรายินดีสัญหาเพื่อให้การบริการที่ดีที่สุดแก่ท่าน ✨ \n\n 🔥ท่านสามาถเลือกชมรายการสินค้าได้จากเมนูด้านล่าง หากท่านมีข้อสงสัย ทีมงานจะตอบกลับท่านโดยเร็วที่สุด ขอให้มีความสุขในการช็อปปิ้งค่ะ❤️"    

    # Send both image and template messages
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=greeting_message)
    )


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