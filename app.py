from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======python的函數庫==========
import tempfile, os
import datetime
# import openai
import time
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN')) #記得加回去
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
# OPENAI API Key初始化設定
# openai.api_key = os.getenv('OPENAI_API_KEY')

'''
def GPT_response(text):
    # 接收回應
    response = openai.Completion.create(model="text-davinci-003", prompt=text, temperature=0.5, max_tokens=500)
    print(response)
    # 重組回應
    answer = response['choices'][0]['text'].replace('。','')
    return answer
'''
uid=0

# 監聽所有來自 /callback 的 Post Request
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
        abort(400)
    return 'OK'

todo_list=[]
todo_dict={}
# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    # echo
    # line_bot_api.reply_message(event.reply_token, TextSendMessage(msg))
    if msg[:4] == "add ":
        tmp=msg[4:].split(' ')
        for i in tmp:
            if i not in todo_list:
                todo_list.append(i)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Added successfully!"))

    elif msg == "list":
        retu = "、".join(todo_list)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"今日待辦事項:\n{retu}"))

    elif msg[:4] == "del ":
        del_item=msg[4:]
        if del_item in todo_list:
            todo_list.remove(del_item)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Deleted successfully!"))
        elif del_item.strip() == "":
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你沒有告訴我要刪除什麼XD"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{del_item} 不在今日的TODO list!"))
    elif msg == "help":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="1. 輸入「add 事項1 事項2 事項3 ... 」新增今日待辦事項\n\
                                                                      2. 輸入「list」以列出今日待辦事項\n\
                                                                      3. 輸入「del 某事項」以刪除某待辦事項\n\
                                                                      4. 輸入「help」取得使用說明"))

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    global uid
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入，請輸入「help」取得使用說明')
    line_bot_api.reply_message(event.reply_token, message)
        
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
