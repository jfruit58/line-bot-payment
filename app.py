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

# Get the DATABASE_URL environment variable
url = os.getenv('DATABASE_URL', None)

@app.route('/')
def hello_world():

    return 'Hello, World!'

@app.route('/liff')
def liff():
    
    return render_template('liff.html')

@app.route("/profile", methods=["GET"])
def profile():
   
    user_id = request.args.get('user_id')
    pic = request.args.get('pic')

    # create a connection to the database
    conn = psycopg2.connect(url)
    
    # create a cursor
    cur = conn.cursor()

    # Check user is not already taken
    cur.execute("SELECT * FROM payment_users WHERE user_id = %s", (user_id,))

    rows = cur.fetchall()

    print(rows)
  
    if len(rows) != 0 :
        
        return  render_template("profile.html",data=rows[0] , pic = pic )


    return render_template("register.html", user_id=user_id )

@app.route("/regis", methods=["POST"])
def regis():
   
    if request.method == "POST":
        
        user_id = request.args.get('user_id')

        # create a connection to the database
        conn = psycopg2.connect(url)

        # create a cursor
        cur = conn.cursor()

        # Check user is not already taken
        cur.execute("SELECT * FROM payment_users WHERE user_id = %s", (user_id,))

        rows = cur.fetchall()

        print(rows)
    
        if len(rows) != 0 :

            return  render_template("profile.html",data=rows[0]  )
        
        name = request.form.get('name')
        surname = request.form.get('surname')
        phone = request.form.get('phone')
        idnumber = request.form.get('idnumber')
        
        # Check user is not already taken
        cur.execute("SELECT * FROM payment_users WHERE idnumber = %s", (idnumber,))

        rows = cur.fetchall()

        if len(rows) == 0 :

            message = 'ข้อมูลของคุณไม่อยู่ใน database กรุณาติดต่อ admin'

            return  render_template("message.html",message=message  )
        
        # Check user is not already taken
        cur.execute("UPDATE payment_users SET user_id = %s WHERE idnumber = %s", (user_id,idnumber,))

        conn.commit()

        # Check user is not already taken
        cur.execute("SELECT * FROM payment_users WHERE user_id = %s", (user_id,))

        rows = cur.fetchall()

        print(rows)
    
        if len(rows) != 0 :

            return  render_template("profile.html",data=rows[0]  )


        return render_template("register.html", user_id=user_id )
   
    # User reached route via GET (as by clicking a link or via redirect)
    else:
    
        return render_template('liff.html')
   


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

    greeting_message = "สวัสดีครับ!😊 คุณ" + profile.display_name + " ขอบคุณที่เป็นเพื่อนกับเรา. \n\n ยินดีตอนรับสู่ Line Official Channel, 🥳\n\n ✨เรายินดีที่ได้เป็นตัวเลือกในการช่วยให้คุณสามารถเช็คยอดค้างชำระด้วยตนเองได้อย่างสะดวกและรวดเร็วทุกทีทุกเวลา \n\n🌈  ทีมของเรายินดีพัฒนาการทำงานเพื่อให้การบริการที่ดีที่สุดแก่ท่าน ✨ \n\n 🔥ท่านที่เข้ามาครั้งแรกกรุณาสมัครสมาชิกเพื่อยืนยันตัวตนจากเมนูด้านล่าง หากท่านมีข้อสงสัย ทีมงานจะตอบกลับท่านโดยเร็วที่สุด ขอให้มีความสุขกับบริการใหม่ของเราครับ❤️"    

    # Send both image and template messages
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=greeting_message)
    )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    user_id = event.source.user_id

    # create a connection to the database
    conn = psycopg2.connect(url)
    
    # create a cursor
    cur = conn.cursor()

    # Check user is not already taken
    cur.execute("SELECT * FROM payment_users WHERE user_id = %s", (user_id,))

    rows = cur.fetchall()

    if len(rows) == 0 :
        
        message = "กรุณาลงทะเบียนสมาชิกก่อนใช้บริการครับ"

    elif event.message.text =='เช็คยอด':

        flex_message = FlexSendMessage(
                alt_text='You received a message',
                contents={
                    
                              "type": "bubble",
                              "body": {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                  {
                                    "type": "text",
                                    "text": "ใบแจ้งหนี้",
                                    "weight": "bold",
                                    "color": "#1DB446",
                                    "size": "sm"
                                  },
                                  {
                                    "type": "text",
                                    "text": "Studio Service",
                                    "weight": "bold",
                                    "size": "xxl",
                                    "margin": "md"
                                  },
                                  {
                                    "type": "text",
                                    "text": "89 Sun Tower, Lak si , Bangkok",
                                    "size": "xs",
                                    "color": "#aaaaaa",
                                    "wrap": True
                                  },
                                  {
                                    "type": "separator",
                                    "margin": "xxl"
                                  },
                                  {
                                    "type": "box",
                                    "layout": "vertical",
                                    "margin": "xxl",
                                    "spacing": "sm",
                                    "contents": [
                                      {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                          {
                                            "type": "text",
                                            "text": "Main service",
                                            "size": "sm",
                                            "color": "#555555",
                                            "flex": 0
                                          },
                                          {
                                            "type": "text",
                                            "text": "4000 THB",
                                            "size": "sm",
                                            "color": "#111111",
                                            "align": "end"
                                          }
                                        ]
                                      },
                                      {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                          {
                                            "type": "text",
                                            "text": "Mainternance",
                                            "size": "sm",
                                            "color": "#555555",
                                            "flex": 0
                                          },
                                          {
                                            "type": "text",
                                            "text": "1000 THB",
                                            "size": "sm",
                                            "color": "#111111",
                                            "align": "end"
                                          }
                                        ]
                                      },
                                      {
                                        "type": "separator",
                                        "margin": "xxl"
                                      }
                                    ]
                                  },
                                  {
                                    "type": "box",
                                    "layout": "vertical",
                                    "margin": "xxl",
                                    "spacing": "sm",
                                    "contents": [
                                      {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                          {
                                            "type": "text",
                                            "text": "Total",
                                            "size": "sm",
                                            "color": "#555555",
                                            "flex": 0,
                                            "weight": "bold"
                                          },
                                          {
                                            "type": "text",
                                            "text": "5000 THB",
                                            "size": "sm",
                                            "color": "#111111",
                                            "align": "end"
                                          }
                                        ]
                                      }
                                    ]
                                  },
                                  {
                                    "type": "separator",
                                    "margin": "xxl"
                                  },
                                  {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "margin": "md",
                                    "contents": [
                                      {
                                        "type": "text",
                                        "text": "SLIP ID",
                                        "size": "xs",
                                        "color": "#aaaaaa",
                                        "flex": 0
                                      },
                                      {
                                        "type": "text",
                                        "text": "#743289384279",
                                        "color": "#aaaaaa",
                                        "size": "xs",
                                        "align": "end"
                                      }
                                    ]
                                  },
                                  {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                      {
                                        "type": "filler"
                                      },
                                      {
                                        "type": "box",
                                        "layout": "baseline",
                                        "contents": [
                                          {
                                            "type": "filler"
                                          },
                                          {
                                            "type": "text",
                                            "text": "ชำระค่าบริการ",
                                            "color": "#ffffff",
                                            "flex": 0,
                                            "offsetTop": "-2px"
                                          },
                                          {
                                            "type": "filler"
                                          }
                                        ],
                                        "spacing": "sm"
                                      },
                                      {
                                        "type": "filler"
                                      }
                                    ],
                                    "borderWidth": "1px",
                                    "cornerRadius": "20px",
                                    "spacing": "sm",
                                    "borderColor": "#00c900",
                                    "margin": "xxl",
                                    "height": "40px",
                                    "backgroundColor": "#00c900"
                                  }
                                ]
                              },
                              "styles": {
                                "footer": {
                                  "separator": True
                                }
                              }
                            })
        
        # Send both image and template messages
        line_bot_api.reply_message(
            event.reply_token,
            flex_message
        )

        return

    else :

        message = "ขอบคุณที่ส่งข้อความถึงเรา\nนี่เป็นระบบตอบกลับอัตโนมัติ\nเราจะให้เจ้าหน้าที่ตอบกลับท่านโดยด่วน\nหากเหตุฉุกเฉินกรุณาติดต่อ\n 📞Callcenter 02-111222333"

    
    # Send both image and template messages
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
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