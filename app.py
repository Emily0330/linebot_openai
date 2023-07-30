from flask import Flask, request, abort

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

'''
def GPT_response(text):
    # 接收回應
    response = openai.Completion.create(model="text-davinci-003", prompt=text, temperature=0.5, max_tokens=500)
    print(response)
    # 重組回應
    answer = response['choices'][0]['text'].replace('。','')
    return answer
'''
# uid='000'

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

# todo_list=[]
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
    
    # echo
    # line_bot_api.reply_message(event.reply_token, TextSendMessage(msg))
    global todo_list
    global todo_dict
    # if userID not in todo_dict:
        # todo_dict[userID]=[]
    query = {"user_id": userID}
    result = collection.find_one(query)
    # print(type(result)) #test
    # 檢查結果是否為 None，即是否找到該 user_id 的資料
    if result is None:
        collection.insert_one({"user_id": userID, "todo_item": []})
    todo_list = result.get("todo_item", []) # default value is an empty list
    # add
    if msg[:4] == "add ":
        tmp=msg[4:].split(' ')
        for i in tmp:
            if i not in todo_list:
                todo_list.append(i)
        update = {"$set": {"todo_item": todo_list}} # $set是運算子
        result = collection.update_one(query, update)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Added successfully!"))

    elif msg == "list":
        if not todo_list: # the list is empty
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="今天還沒有待辦事項哦!\n使用add指令添加吧~"))
        else:
            retu = "、".join(todo_list)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"今日待辦事項:\n{retu}"))
        """
        if not todo_dict[userID]: # the usr's list is empty
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="今天還沒有待辦事項哦!\n使用add指令添加吧~"))
        else:
            retu = "、".join(todo_dict[userID])
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"今日待辦事項:\n{retu}"))
        """
    elif msg[:4] == "del ":
        del_item=msg[4:]
        """
        if del_item in todo_dict[userID]:
            todo_dict[userID].remove(del_item)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Deleted successfully!"))
            print(todo_dict) # test
        """
        if del_item in todo_list:
            todo_list.remove(del_item)
            update = {"$set": {"todo_item": todo_list}} # $set是運算子
            result = collection.update_one(query, update)
        elif del_item.strip() == "":
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你沒有告訴我要刪除什麼XD"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{del_item} 不在今日的TODO list!"))

    elif msg == "reset":
        todo_list = []
        # todo_dict[userID] = [] # dict
        update = {"$set": {"todo_item": todo_list}} # $set是運算子
        result = collection.update_one(query, update)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="TODO list has been reset!\n\
                                                                      Enjoy your day <3"))
    elif msg == "help":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="1. 輸入「add 事項1 事項2 事項3 ... 」新增今日待辦事項\n\
                                                                      2. 輸入「list」以列出今日待辦事項\n\
                                                                      3. 輸入「del 某事項」以刪除某待辦事項\n\
                                                                      4. 輸入「reset」一次清空所有待辦事項\n\
                                                                      5. 輸入「help」取得使用說明"))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="TODO機器人還沒有這個功能唷!\n\
                                                                      趕快聯繫開發者許願吧!"))
    '''
    with open("usr_info.json", "a", encoding="utf-8") as f:
        json.dump(todo_dict, f, indent=2, sort_keys=False, ensure_ascii=False)
        f.close()
    '''
@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    # global uid
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
