from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import pymongo # for MongoDB

def delete(del_item, todo_list, query, event, collection):
    if del_item.strip() == "":
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你沒有告訴我要刪除什麼XD"))
    else:
        del_list=[]
        first_char = del_item[0]
        for item in todo_list:
            if first_char == item[0]:
                del_list.append(item)
        match len(del_list):
            case 0:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{del_item} 不在今日的TODO list!"))
            case 1:
                todo_list.remove(del_item)
                update = {"$set": {"todo_item": todo_list}} # $set是運算子
                result = collection.update_one(query, update)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Deleted successfully!"))
            case _: # default case, more than one item
                