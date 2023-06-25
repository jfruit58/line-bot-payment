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

from flask import Flask, request, abort ,render_template ,redirect
from linebot import (
    LineBotApi, WebhookParser,WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,FollowEvent, ImageSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction,
    CarouselTemplate, CarouselColumn, FlexSendMessage, BubbleContainer, BoxComponent, ImageComponent, TextComponent, ButtonComponent, SeparatorComponent,
    PostbackEvent, QuickReply, QuickReplyButton, MessageAction,URIAction , 

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

# Get the DATABASE_URL environment variable
url = os.getenv('DATABASE_URL', None)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)
handler = WebhookHandler(channel_secret)


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/shop/<user_id>')
def shop(user_id):

    #get product
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute("SELECT * FROM shop_products")
    shop_products = cur.fetchall()

    # close the cursor and connection
    cur.close()
    conn.close()
    
    return render_template("shop.html",data=shop_products,user_id=user_id,)

@app.route('/cart/<user_id>')
def cart(user_id):
    #get product
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    #cur.execute("SELECT * FROM shop_cart_items WHERE user_id = %s;", (user_id,))
    cur.execute("SELECT c.*, p.name, p.price FROM shop_cart_items c JOIN shop_products p ON c.product_id = p.id WHERE c.user_id = %s", (user_id,))
    cart = cur.fetchall()

    print(cart)

    # close the cursor and connection
    cur.close()
    conn.close()
    return render_template("cart.html",data=cart,user_id=user_id,)

@app.route('/order/<user_id>')
def order(user_id):
    return render_template("order.html")

@app.route("/additem/<user_id>", methods=['POST'])
def additem(user_id):

    user_id = request.form.get('user_id')
    product_id = request.form.get('product_id')

    # add new item to cart in database
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute("SELECT * FROM shop_cart_items WHERE user_id = %s AND product_id = %s", (user_id, product_id))
    existing_item = cur.fetchone()

    if existing_item:
        # If the item already exists, update the quantity
        cur.execute("UPDATE shop_cart_items SET quantity = quantity + 1 WHERE user_id = %s AND product_id = %s", (user_id, product_id))
    else:
        # If the item doesn't exist, insert a new row with quantity = 1
        cur.execute("INSERT INTO shop_cart_items (user_id, product_id, quantity) VALUES (%s, %s, 1)", (user_id, product_id))

    conn.commit()

    cur.execute("SELECT * FROM shop_products")
    shop_products = cur.fetchall()

    # Close the cursor and connection
    cur.close()
    conn.close()

    return render_template("shop.html", data=shop_products, user_id=user_id)


@app.route("/callback", methods=['POST'])
def callback():
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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id

    switch_case_example(event.message.text,event)
    
@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)

    greeting_message = "สวัสดีค่ะ!😊 " + profile.display_name + " ขอบคุณที่เป็นเพื่อนกับเรา. \n\n ยินดีตอนรับสู่ JPBeauty's Line Official Channel, 🥳\n\n ✨JPBeauty ยินดีที่ได้เป็นตัวเลือกในการช่วยให้คุณสามารถ🛒ช๊อปปี้สินค้าหลายรายการจาก duty free ทั่วโลกอย่างสะดวกสบายโดยไม่ต้องเดินทาง✈️ \n\n🌈 ไม่ว่าจะเป็นสินค้าชนิดใด ทีมของเรายินดีสัญหาเพื่อให้การบริการที่ดีที่สุดแก่ท่าน ✨ \n\n 🔥ท่านสามาถเลือกชมรายการสินค้าได้จากเมนูด้านล่าง หากท่านมีข้อสงสัย ทีมงานจะตอบกลับท่านโดยเร็วที่สุด ขอให้มีความสุขในการช็อปปิ้งค่ะ❤️"
    
    # collect user_id if new user
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute("SELECT * FROM shop_users WHERE user_id = %s", (user_id,))
    rows = cur.fetchall()

    # close the cursor and connection
    cur.close()
    conn.close()

    print(rows)
  
    if len(rows) == 0 :
         # add new user to database
        cur.execute("INSERT INTO shop_users (user_id,time) VALUES (%s,%s)",(user_id,datetime.now(),))
        conn.commit()
        

    # Send both image and template messages
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=greeting_message)
    )

def case_1(event):
        carousel_template = CarouselTemplate(
            columns=[
                CarouselColumn(
                      thumbnail_image_url='https://scontent.fbkk12-5.fna.fbcdn.net/v/t1.6435-9/45878479_10161252279455323_4524037980867788800_n.jpg?_nc_cat=1&ccb=1-7&_nc_sid=09cbfe&_nc_ohc=GtpHn2ff_7AAX-QivK-&_nc_ht=scontent.fbkk12-5.fna&oh=00_AfBYqyOFNU5N0oFnIKHqhsGYn__MZvt_x_izRYLd9dNaaw&oe=64AE542D',
                      title='Duty free',
                      text='Duty free',
                      actions=[URIAction(label='Shop now', uri='https://bot-jpbeauty.onrender.com/shop/'+event.source.user_id)]
                      ),
                CarouselColumn(
                    thumbnail_image_url='https://citymonitor.ai/wp-content/uploads/sites/3/2022/10/shutterstock_1707139477.webp',
                    title='เยอรมัน',    
                    text='เยอรมัน', 
                    actions=[URIAction(label='Shop now', uri='https://bot-jpbeauty.onrender.com/shop/'+event.source.user_id)]
                ),
                CarouselColumn(
                      thumbnail_image_url='https://rimage.gnst.jp/livejapan.com/public/article/detail/a/00/04/a0004314/img/basic/a0004314_main.jpg?20200402155321&q=80',
                      title='ญี่ปุ่น',   
                      text='ญี่ปุ่น',  
                      actions=[URIAction(label='Shop now', uri='https://bot-jpbeauty.onrender.com/shop/'+event.source.user_id)]
                      ),
                CarouselColumn(
                    thumbnail_image_url='https://travellersworldwide.com/wp-content/uploads/2022/11/Shutterstock_607235345-960x600.jpg.webp',
                    title='อังกฤษ',
                    text='อังกฤษ',
                    actions=[URIAction(label='Shop now', uri='https://bot-jpbeauty.onrender.com/shop/'+event.source.user_id)]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://www.avanse.com/blogs/images/blog-4-aug.jpg',
                    title='ออสเตเรีย',
                    text='ออสเตเรีย',
                    actions=[URIAction(label='Shop now', uri='https://bot-jpbeauty.onrender.com/shop/'+event.source.user_id)]
                ),
            ]
        )

        carousel_message = TemplateSendMessage(
            alt_text='You received a message',
            template=carousel_template
        )
        
        line_bot_api.reply_message(event.reply_token, carousel_message)

def case_2(event):
    #get product
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute("SELECT * FROM shop_products")
    shop_products = cur.fetchall()

    # close the cursor and connection
    cur.close()
    conn.close()

    print(shop_products)
    
    webpage_url = 'https://example.com'
    
    
    line_bot_api.reply_message(
        event.reply_token,
        TextMessage(text=webpage_url)
    )

def case_3(event):
    webpage_url = 'https://example.com'
    uri_action = URIAction(
        label='Open Webpage',
        uri=webpage_url
    )
    message = TextSendMessage(text='Opening the webpage...')
    message.action = uri_action

    line_bot_api.reply_message(
        event.reply_token,
        TextMessage(text=webpage_url)
    )




def default_case(event):
    message = "ขอบคุณที่ส่งข้อความถึงเรา\nนี่เป็นระบบตอบกลับอัตโนมัติ\nเราจะให้เจ้าหน้าที่ตอบกลับท่านโดยด่วน\n"

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=message))

def switch_case_example(text,event):
    match text:
        case 'เลือกสินค้า':
            print(text)
            return case_1(event)
        case 'สมาชิก':
            print(text)
            return case_2(event)
        case 'ยกเลิก':
            print(text)
            return case_2(event)
        case _:
            print('default_case')
            return default_case(event)
    


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)