import copy
import json
import pickle
import uuid
from channels.generic.websocket import WebsocketConsumer
from django_redis import get_redis_connection
import os

from brain.test_settings import WEBSOCKET_CLIENTS


class LoginConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        # 生成唯一标识符，绑定客户端
        uid = str(uuid.uuid1())
        # 进行uid和客户端的绑定
        # 使用cache和redis没有成功,self当前的对象，不能被序列化
        WEBSOCKET_CLIENTS[uid] = self

        # 发送uid给客户端
        self.send_message(data={"uid": uid})

    def disconnect(self, close_code):
        # 从字典中删除客户端
        pass

    def receive(self, text_data):
        pass

    def send_message(self, status=200, data=None, message='ok'):
        self.send(text_data=json.dumps({
            'status': status,
            'data': data,
            'message': message
        }))


class QtConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        data = text_data_json.get('data', None)
        if data is None:
            self.send_message(message='The message information does not meet the specifications', status=400)

        uid = data.get("uid", None)
        phone_num = data.get("phone_num", None)

        client = self.client_mark(uid)
        if client is None:
            self.send_message(data="uuid is not exist")
        client.send_message(data={"phone_num": phone_num})

    def send_message(self, status=200, data=None, message='ok'):
        self.send(text_data=json.dumps({
            'status': status,
            'data': data,
            'message': message
        }))
