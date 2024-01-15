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

# 設定 MongoDB Atlas 連線字串, <username>:<password>
mongo_uri = "mongodb+srv://qomolanma:zDZvD94Q3D7bOw0b@cluster0.bojsa1o.mongodb.net/?retryWrites=true&w=majority"

# 連線到 MongoDB Atlas Cluster
client = pymongo.MongoClient(mongo_uri)
db = client.get_database("ta_chu")  # 替換成你的資料庫名稱


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

tachu_dict={}
'''
{
    "name": "" #link
}
'''
# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    # userID = event.source.user_id # get userID
    # 在此處使用 MongoDB 進行資料庫操作
    # 例如，儲存使用者的 todo list

    # add
    if str(msg).strip() == "現在集點":
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Added successfully!"))
        collection = db.get_collection("spots")  # 替換成你的集合名稱
        # 檢索所有資料
        cursor = collection.find()
        # 將檢索到的資料轉換為 Python 列表
        data = list(cursor)

        # 隨機選擇一個項目
        random_item = random.choice(data)

        # 現在您有了隨機選擇的項目，可以使用它進一步處理或傳送給使用者
        print("隨機選擇的項目：", random_item[name], random_item[link])
   
        """ # 建立 Buttons Template 選單
        checkbox_template = TemplateSendMessage(
            alt_text="Please select what you want to delete.",
            template=ButtonsTemplate(
                title=response,
                text="Please select what you want to delete: ",
                actions=actions
            )
        )
        print(checkbox_template)
        # 回覆使用者訊息，使用 Buttons Template 提供選項
        line_bot_api.reply_message(event.reply_token, checkbox_template) """

   
    elif str(msg).lower() == "help":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="1. 輸入「add 事項1 事項2 事項3 ... 」新增今日待辦事項\n\
                                                                      2. 輸入「list」以列出今日待辦事項\n\
                                                                      3. 輸入「del 某事項」以刪除某待辦事項\n\
                                                                      4. 輸入「reset」一次清空所有待辦事項\n\
                                                                      5. 輸入「help」取得使用說明"))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="機器人還沒有這個功能唷!\n\
                                                                      趕快聯繫開發者許願吧!"))
    return jsonify({"success": True})

""" @handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data) # check at backend
    userID = event.source.user_id
    # 在此處使用 MongoDB 進行資料庫操作
    # 例如，儲存使用者的 todo list
    collection = db.get_collection("todo_lists")  # 替換成你的集合名稱
    
    query = {"user_id": userID}
    result = collection.find_one(query)
    # 檢查結果是否為 None，即是否找到該 user_id 的資料
    if result is None:
        collection.insert_one({"user_id": userID, "todo_item": []})
    todo_list = result.get("todo_item", []) # default value is an empty list

    # 解析使用者選擇的項目編號
    selected_index = int(event.postback.data.split()[1]) - 1  # 因為使用者輸入的編號是從 1 開始，而我們的索引是從 0 開始
    # 執行刪除功能
    del todo_list[selected_index]
    update = {"$set": {"todo_item": todo_list}}
    result = collection.update_one(query, update)

    # 回覆 "已刪除!" 的訊息給使用者
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已刪除!")) """


""" @handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入，請輸入「help」取得使用說明')
    line_bot_api.reply_message(event.reply_token, message) """
        
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
