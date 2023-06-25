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

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser,WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,FollowEvent, ImageSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction,
    CarouselTemplate, CarouselColumn, FlexSendMessage, BubbleContainer, BoxComponent, ImageComponent, TextComponent, ButtonComponent, SeparatorComponent

)


app = Flask(__name__)

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
    if event.message.text =='test':

        user_id = event.source.user_id

        greeting_message = "Hello! Thank you for following."

        # Create carousel columns
        column1 = CarouselColumn(
            thumbnail_image_url='https://example.com/thumbnail1.jpg',
            title='Option 1',
            text='Description 1',
            actions=[PostbackTemplateAction(label='Select 1', data='option1')]
        )
        column2 = CarouselColumn(
            thumbnail_image_url='https://example.com/thumbnail2.jpg',
            title='Option 2',
            text='Description 2',
            actions=[PostbackTemplateAction(label='Select 2', data='option2')]
        )
        column3 = CarouselColumn(
            thumbnail_image_url='https://example.com/thumbnail3.jpg',
            title='Option 3',
            text='Description 3',
            actions=[PostbackTemplateAction(label='Select 3', data='option3')]
        )
        column4 = CarouselColumn(
            thumbnail_image_url='https://example.com/thumbnail4.jpg',
            title='Option 4',
            text='Description 4',
            actions=[PostbackTemplateAction(label='Select 4', data='option4')]
        )

        # Create carousel template
        carousel_template = CarouselTemplate(columns=[column1, column2, column3, column4])

        # Create template message
        template_message = TemplateSendMessage(
            alt_text='Welcome',
            template=carousel_template
        )

        # Create image message
        image_message = ImageSendMessage(
            original_content_url='https://example.com/image.jpg',
            preview_image_url='https://example.com/image_preview.jpg'
        )

        # Send both image and template messages
        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text=greeting_message), image_message, template_message]
        )
    
    elif event.message.text.lower() == 'flex':
        # Create Flex Message
        flex_message = FlexSendMessage(
            alt_text='Flex Message',
            contents={
                      "type": "bubble",
                      "direction": "ltr",
                      "hero": {
                        "type": "image",
                        "url": "https://vos.line-scdn.net/bot-designer-template-images/bot-designer-icon.png",
                        "size": "full",
                        "aspectRatio": "1.51:1",
                        "aspectMode": "fit",
                        "offsetTop": "10px",
                        "offsetBottom": "10px"
                      },
                      "footer": {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                          {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                              {
                                "type": "button",
                                "action": {
                                  "type": "uri",
                                  "label": "สมัครสมาชิก",
                                  "uri": "https://linecorp.com"
                                },
                                "color": "#545FF6FF"
                              },
                              {
                                "type": "button",
                                "action": {
                                  "type": "uri",
                                  "label": "เข้าสู่ระบบสมาชิก",
                                  "uri": "https://linecorp.com"
                                }
                              }
                            ]
                          },
                          {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                              {
                                "type": "button",
                                "action": {
                                  "type": "uri",
                                  "label": "จองคลาสเรียน",
                                  "uri": "https://linecorp.com"
                                }
                              },
                              {
                                "type": "button",
                                "action": {
                                  "type": "uri",
                                  "label": "ข้อมูลทั่วไป",
                                  "uri": "https://linecorp.com"
                                }
                              }
                            ]
                          }
                        ]
                      }
                    }
        )

        line_bot_api.reply_message(
            event.reply_token,
            flex_message
        )

    else :

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))
    
    
@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)

    greeting_message = "Hello! " + profile.display_name + "Thank you for following."

    # Create buttons template
    buttons_template = ButtonsTemplate(
        title='Welcome to our bot!',
        text='Please select an option:',
        actions=[
            PostbackTemplateAction(label='สมัครสมาชิกใหม่', data='option1'),
            PostbackTemplateAction(label='เข้าสู่ระบบสมาชิก', data='option2'),
            PostbackTemplateAction(label='จองคลาสเรียน', data='option3'),
            PostbackTemplateAction(label='ข้อมูลทั่วไป', data='option4')
        ],
        image_size='contain',
        image_aspect_ratio='rectangle',
        thumbnail_image_url='https://example.com/thumbnail.jpg',
        image_background_color='#0000FF',
        image_aspect_mode='cover'
    )

    # Create template message
    template_message = TemplateSendMessage(
        alt_text='Welcome',
        template=buttons_template
    )

    # Create image message
    image_message = ImageSendMessage(
        original_content_url='https://example.com/image.jpg',
        preview_image_url='https://example.com/image_preview.jpg'
    )

    # Send both image and template messages
    line_bot_api.reply_message(
        event.reply_token,
        [TextSendMessage(text=greeting_message), image_message, template_message]
    )




if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)