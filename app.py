from flask import Flask, request, abort, jsonify

import requests

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import pymongo # for MongoDB

#======python的函數庫==========
import tempfile, os
import datetime
# import openai
import time
# import json
import json
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN')) #記得加回去
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
# OPENAI API Key初始化設定
# openai.api_key = os.getenv('OPENAI_API_KEY')

# 設定 MongoDB Atlas 連線字串, <username>:<password>
mongo_uri = "mongodb+srv://qomolanma:zDZvD94Q3D7bOw0b@cluster0.bojsa1o.mongodb.net/?retryWrites=true&w=majority"

# 連線到 MongoDB Atlas Cluster
client = pymongo.MongoClient(mongo_uri)
db = client.get_database("TODO_bot")  # 替換成你的資料庫名稱


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
# Line bot 接收訊息的 Webhook 路由
# @app.route("/callback", methods=["POST"])
'''
def webhook():
    data = request.get_json()

    # 獲取使用者的訊息內容
    user_id = data["events"][0]["source"]["userId"]
    message_text = data["events"][0]["message"]["text"]
    # 在此處使用 MongoDB 進行資料庫操作
    # 例如，儲存使用者的 todo list
    collection = db.get_collection("todo_lists")  # 替換成你的集合名稱

    query = {"user_id": user_id}
    result = collection.find_one(query)
    # 檢查結果是否為 None，即是否找到該 user_id 的資料
    if result is None:
        collection.insert_one({"user_id": user_id, "todo_item": []})
    todo_items = result.get("todo_item", []) # default value is an empty list

    if message_text == "del":
        response = "請選擇要刪除的項目："

        # 動態生成 Checkbox Template 的 actions
        actions = []
        for i, item in enumerate(todo_items):
            action = {
                "type": "postback",
                "label": item,
                "data": f"/delete_confirm {i+1}"  # 回傳使用者選擇的項目編號（從 1 開始）
            }
            actions.append(action)

        # 建立 Checkbox Template 選單
        checkbox_template = {
            "type": "template",
            "altText": "請勾選要刪除的項目",
            "template": {
                "type": "buttons",
                "text": response,
                "actions": actions
            }
        }

        # 回覆使用者訊息，使用 Checkbox Template 提供選項
        reply_message = {
            "replyToken": data["events"][0]["replyToken"],
            "messages": [checkbox_template]
        }

        # 傳送回覆訊息給 Line bot
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer YOUR_CHANNEL_ACCESS_TOKEN"  # 替換成你的 Line bot 的 Channel Access Token
        }
        response = requests.post("https://api.line.me/v2/bot/message/reply", json=reply_message, headers=headers)

    elif message_text.startswith("/delete_confirm "):
        # 解析使用者選擇的項目編號
        selected_index = int(message_text.split()[1]) - 1  # 因為使用者輸入的編號是從 1 開始，而我們的索引是從 0 開始
        # 執行刪除功能
        del todo_items[selected_index]
        update = {"$set": {"todo_item": todo_items}} # $set是運算子
        result = collection.update_one(query, update)

        # 取得 Line bot 的 reply_token
        reply_token = data["events"][0]["replyToken"]
        # 使用 requests.post 發送 "已刪除!" 的訊息給使用者
        line_bot_api.reply_message(reply_token, "已刪除!")

    return jsonify({"success": True})
'''
todo_dict={}
'''
{
    "USER_ID": [] #todo_list
}
'''
# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    userID = event.source.user_id # get userID
    # 在此處使用 MongoDB 進行資料庫操作
    # 例如，儲存使用者的 todo list
    collection = db.get_collection("todo_lists")  # 替換成你的集合名稱
    
    global todo_list
    global todo_dict
    query = {"user_id": userID}
    result = collection.find_one(query)
    # 檢查結果是否為 None，即是否找到該 user_id 的資料
    if result is None:
        collection.insert_one({"user_id": userID, "todo_item": []})
    todo_list = result.get("todo_item", []) # default value is an empty list
    # add
    if str(msg[:4]).lower() == "add ":
        tmp=msg[4:].split(' ')
        for i in tmp:
            if i not in todo_list:
                todo_list.append(i)
        update = {"$set": {"todo_item": todo_list}} # $set是運算子
        result = collection.update_one(query, update)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Added successfully!"))

    elif str(msg).lower() == "list":
        if not todo_list: # the list is empty
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="今天還沒有待辦事項哦!\n使用add指令添加吧~"))
        else:
            retu = "、".join(todo_list)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"今日待辦事項:\n{retu}"))
            
    # delete
    elif str(msg).lower() == "del":
        response = "請選擇要刪除的項目："

        # 動態生成 Checkbox Template 的 actions
        actions = []
        for i, item in enumerate(todo_list):
            action = {
                "type": "postback",
                "label": item,
                "data": f"/delete_confirm {i+1}"  # 回傳使用者選擇的項目編號（從 1 開始）
            }
            actions.append(action)

        # 建立 Checkbox Template 選單
        checkbox_template = {
            "type": "template",
            "altText": "請勾選要刪除的項目",
            "template": {
                "type": "buttons",
                "text": response,
                "actions": actions
            }
        }

        # 回覆使用者訊息，使用 Checkbox Template 提供選項
        reply_message = {
            "replyToken": event.reply_token,
            "messages": [checkbox_template]
        }

        # 傳送回覆訊息給 Line bot
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('CHANNEL_ACCESS_TOKEN')}"  # 替換成你的 Line bot 的 Channel Access Token
        }
        # response = requests.post("https://api.line.me/v2/bot/message/reply", json=reply_message, headers=headers)
        line_bot_api.reply_message(event.reply_token, TemplateSendMessage(alt_text="請勾選要刪除的項目", template=checkbox_template))
        print("here!") #test

    elif msg.startswith("/delete_confirm "):
        # 解析使用者選擇的項目編號
        selected_index = int(msg.split()[1]) - 1  # 因為使用者輸入的編號是從 1 開始，而我們的索引是從 0 開始
        # 執行刪除功能
        del todo_list[selected_index]
        update = {"$set": {"todo_item": todo_list}} # $set是運算子
        result = collection.update_one(query, update)

        print("Hi!") # test

        # 取得 Line bot 的 reply_token
        reply_token = event.reply_token
        # 使用 requests.post 發送 "已刪除!" 的訊息給使用者
        line_bot_api.reply_message(reply_token, "已刪除!")

    # return jsonify({"success": True})

        '''
        if co_possi_item == 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{del_item} 不在今日的TODO list!"))
        elif
        elif del_item in todo_list:
            todo_list.remove(del_item)
            update = {"$set": {"todo_item": todo_list}} # $set是運算子
            result = collection.update_one(query, update)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Deleted successfully!"))
        else:
        '''
    elif str(msg).lower() == "reset":
        todo_list = []
        # todo_dict[userID] = [] # dict
        update = {"$set": {"todo_item": todo_list}} # $set是運算子
        result = collection.update_one(query, update)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="TODO list has been reset!\n\
                                                                      Enjoy your day <3"))
    elif str(msg).lower() == "help":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="1. 輸入「add 事項1 事項2 事項3 ... 」新增今日待辦事項\n\
                                                                      2. 輸入「list」以列出今日待辦事項\n\
                                                                      3. 輸入「del 某事項」以刪除某待辦事項\n\
                                                                      4. 輸入「reset」一次清空所有待辦事項\n\
                                                                      5. 輸入「help」取得使用說明"))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="TODO機器人還沒有這個功能唷!\n\
                                                                      趕快聯繫開發者許願吧!"))
    return jsonify({"success": True})

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
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
