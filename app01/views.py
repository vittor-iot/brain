from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse
from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError
import uuid
import json
import sys,os
import random
import time
import re
import pandas as pd
from app01.models import *
from brain.settings import *


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  # 导入分页器
from django.forms.models import model_to_dict

# Create your views here.
from django.conf import settings
from django.core.cache import cache
from django.core import signing
import hashlib
from django.db import transaction
from app01.tasks import execute,test_hello,pose_d
import pickle
import pytz
import requests

from apscheduler.schedulers.background import BackgroundScheduler

timezone = pytz.timezone("Asia/Shanghai")
inputTrainOpenid = 'this-is-brain-train-data-input-please-make-it'

HEADER = {'typ': 'JWP', 'alg': 'default'}
KEY = 'LI_WEI_QUAN'
SALT = 'www.yihcampus.com'

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)


'''
发布定时任务:
将数据写入csv
'''
sc1 = BackgroundScheduler()
@sc1.scheduled_job('interval', hours=7)
def db_connect():
    obj = TotalData.objects.all()

sc1.start()



sc = BackgroundScheduler()
@sc.scheduled_job('cron', day_of_week='*', hour=16, minute='16', second='30',timezone=timezone)
def getname():
    total_obj = RecordData.objects.all()
    if len(total_obj) == 0:
        return None
    recoder = []
    objs = []
    for i in total_obj:
        recoder.append(i.id)
        if len(objs) == 0:
            objs.append({'openid':i.openid,'sequenceid':i.sequenceid})
        else:
            temp = 0
            for tt in objs:
                if tt['openid'] == i.openid and tt['sequenceid'] == i.sequenceid:
                    temp = 1
                    break
            if temp == 0:
                objs.append({'openid':i.openid,'sequenceid':i.sequenceid})
            

    path = os.getcwd()
    for i in objs:
        data = []
        total = TranData.objects.filter(openid=i['openid'],sequenceid=i['sequenceid']).order_by("time")
        user = Userinfo.objects.get(openid=i['openid'])
        
        num = 0
        h = time.localtime()
        cid = []
        num1 = []
        ti = None
        s = ''
        for j in range(0,33):
            num1.append(str(j+1))
        for obj in total:
            s = s + obj.data
            ti = obj.time
        st1 = re.findall('a0.{62}c0', s)
        for st in st1:
            hj = []
            for j in range(0,33):
                hj.append(int((st[j*2:j*2+2]),16))

            data.append(hj)
            h = time.localtime(float(ti)/1000)
            if len(data) == 100:
                df = pd.DataFrame(data,columns=num1)
                h_time= time.strftime('%Y-%m-%d', h)
                h_name = time.strftime('%Y_%m_%d_%H_%M_%S', h)
                #h_path=path + '/data/'+i['openid']+'/'+h_time
                h_path=path + '/data/'+ user.phone 
                #true_path = path + '/data/'+i['openid']+'/'+h_time+'/'+user.phone+'_'+h_name+'.csv'
                true_path = path + '/data/'+user.phone+'/'+user.phone+'_'+h_name+'.csv'
                if not os.path.exists(true_path):
                    if not os.path.exists(h_path):
                        os.makedirs(h_path)
                    df.to_csv(true_path, mode='a',index=0)
                    FileStorage.objects.create(
                        openid=i['openid'],
                        address=true_path,
                    )
                else:
                    df.to_csv(true_path, mode='a',index=0,header=False)
                data.clear()
        df = pd.DataFrame(data,columns=num1)
        h_time= time.strftime('%Y-%m-%d', h)
        h_name = time.strftime('%Y_%m_%d_%H_%M_%S', h)
        #h_path=path + '/data/'+i['openid']+'/'+h_time
        h_path=path + '/data/'+ user.phone
        #true_path = path + '/data/'+i['openid']+'/'+h_time+'/'+user.phone+'_'+h_name+'.csv'
        true_path = path + '/data/'+user.phone+'/'+user.phone+'_'+h_name+'.csv'
        # true_path = path + '/data/'+i['openid']+'.csv'
        # print(true_path)
        # print(os.path.exists(true_path))
        if not os.path.exists(true_path):
            if not os.path.exists(h_path):
                os.makedirs(h_path)
            
            df.to_csv(true_path, mode='a',index=0)
            FileStorage.objects.create(
                openid=i['openid'],
                address=true_path,
            )
        else:
            df.to_csv(true_path, mode='a',index=0,header=False)




        # for obj in total:
        #     cid.append(obj.id)
        #     if len(obj.data) < 132:
        #         continue
        #     try:
        #         st1 = re.findall(r'\w{132}', obj.data)
        #     except:
        #         continue
        #     for st in st1:
        #         hj = []
        #         if len(st) < 132:
        #             continue
        #         if st[0:2] != 'a0':
        #             continue
        #         for j in range(0,66):
        #             hj.append(st[j*2:j*2+2])
                    
        #         data.append(hj)

        #         h = time.localtime(float(obj.time)/1000)
        #         num = num +1
        #         if len(data) == 100:
        #             df = pd.DataFrame(data,columns=num1)
        #             # print(h)
                    
        #             h_time= time.strftime('%Y-%m-%d', h)
        #             h_path=path + '/data/'+i['openid']+'/'+h_time
        #             true_path = path + '/data/'+i['openid']+'/'+h_time+'/data.csv'
        #             if not os.path.exists(true_path):
        #                 os.makedirs(h_path)
        #                 df.to_csv(true_path, mode='a',index=0)
        #                 FileStorage.objects.create(
        #                     openid=i['openid'],
        #                     address=true_path,
        #                 )
        #             else:
        #                 df.to_csv(true_path, mode='a',index=0,header=False)
        #             data.clear()
        # df = pd.DataFrame(data,columns=num1)
        # h_time= time.strftime('%Y-%m-%d', h)
        # h_path=path + '/data/'+i['openid']+'/'+h_time
        # true_path = path + '/data/'+i['openid']+'/'+h_time+'/data.csv'
        # # true_path = path + '/data/'+i['openid']+'.csv'
        # # print(true_path)
        # # print(os.path.exists(true_path))
        # if not os.path.exists(true_path):
        #     os.makedirs(h_path)
        #     df.to_csv(true_path, mode='a',index=0)
        #     FileStorage.objects.create(
        #         openid=i['openid'],
        #         address=true_path,
        #     )
        # else:
        #     df.to_csv(true_path, mode='a',index=0,header=False)
        # print(df)
        del data[:]
        try:
            TranData.objects.filter(openid=i['openid'],sequenceid=i['sequenceid']).delete()
            # pass  
        except:
            print("error!")
    try:
        RecordData.objects.filter(id__in = recoder).delete()
    except:
        print("error!")
    print(1111)
    return HttpResponse(True)
sc.start()

#创建token
def create_token(openid):
    # 0. 检查缓存里有没有同时在线
    # 1. 加密头信息
    header = signing.dumps(HEADER, key=KEY, salt=SALT)
    header = signing.b64_encode(header.encode()).decode()
    # 2. 构造Payload
    payload = {"username": openid, "iat": time.time()}
    # print(payload)
    payload = signing.dumps(payload, key=KEY, salt=SALT)
    payload = signing.b64_encode(payload.encode()).decode()
    # 3. 生成签名
    md5 = hashlib.md5()
    md5.update(("%s.%s" % (header, payload)).encode())
    signature = md5.hexdigest()
    token = "%s.%s.%s" % (header, payload, signature)
    # 存储到缓存中
    cache.set(openid, token, None)
    return token

#检查token
def check_token(token):
    try:
        payload = str(token).split('.')[1]
        payload = signing.b64_decode(payload.encode()).decode()
        payload = signing.loads(payload, key=KEY, salt=SALT)
        openid = payload['username']      
        last_token = cache.get(openid)
       
        if last_token == token:
            return True
        else:
            return False
    except:
        return False



def test(request):
    cache.set('name','wang',300)
    result = test_hello.delay()
    return HttpResponse(result)

def getopenid(token):
    payload = str(token).split('.')[1]
    payload = signing.b64_decode(payload.encode()).decode()
    payload = signing.loads(payload, key=KEY, salt=SALT)
    openid = payload['username']
    return openid

def getyzm(request):
    if request.method == 'POST':
        telephone = json.loads(request.body).get('phone', '')
        # 短信应用SDK AppID
        appid = 1400660077  # SDK AppID是1400开头
        # 短信应用SDK AppKey
        appkey = "ab7b1099c79ee0a0e542c30db95e386a"
        # 需要发送短信的手机号码
        phone_numbers = telephone
        # 短信模板ID，需要在短信应用中申请
        template_id = 1360235  # NOTE: 这里的模板ID`7839`只是一个示例，真实的模板ID需要在短信控制台中申请
        # 签名
        sms_sign = "意念中枢"  # NOTE: 这里的签名"腾讯云"只是一个示例，真实的签名需要在短信控制台中申请，另外签名参数使用的是`签名内容`，而不是`签名ID`
        code = ''
        #for循环生成数字

        for i in range(6):
            #使用random随机生成一个数字
            num = random.randint(0, 9)
            #对数字转换成字符串后进行拼接
            code += str(num)
        params = [code]  # 当模板没有参数时，`params = []`
        sms_type = 0  # Enum{0: 普通短信, 1: 营销短信}
        ssender = SmsSingleSender(appid, appkey)
        
        
        try:
            # result = ssender.send(sms_type, 86, phone_numbers[0], "5678", extend="", ext="")
            result = ssender.send_with_param(86, phone_numbers,template_id, params, sign=sms_sign, extend="", ext="")
            cache.set(telephone,code,None)
        # 签名参数未提供或者为空时，会使用默认签名发送短信
        except HTTPError as e:
            print(e)
            return HttpResponse(json.dumps({
                "status":0
            }))
        except Exception as e:
            print(e)
            return HttpResponse(json.dumps({
                "status":0
            }))
        # tele = cache.get(new)
        return HttpResponse(json.dumps({
            "status":200
        }) )
    else:
        return HttpResponse(json.dumps({
            "status":0
        }) )

def login(request):
    phone = json.loads(request.body).get('phone','')
    yzm = json.loads(request.body).get('yzm','')
    code = cache.get(phone)
    healthy = {}
    account = {}
    # print(code)
    # print(yzm)
    if yzm == code :
        
        try:
            
            obj_userinfo = Userinfo.objects.get(phone = phone)
           
            if obj_userinfo.disable == 0:
                return HttpResponse(json.dumps({
                    "status":4
                }) )
            obj_healthinfo = Healthinfo.objects.get(openid = obj_userinfo.openid)
            
            account['ipname'] = obj_userinfo.ipname
            account['gender'] = obj_userinfo.gender
            account['address'] = obj_userinfo.address
            account['phone'] = obj_userinfo.phone
            account['name'] = obj_userinfo.name
            account['avatar'] = obj_userinfo.avatar
            account['openid'] = obj_userinfo.openid
            

            healthy['birthyear'] = obj_healthinfo.birthyear + '年' if obj_healthinfo.birthyear != '' and obj_healthinfo.birthyear != None  else ''
            healthy['illtime'] = obj_healthinfo.illtime if obj_healthinfo.illtime != '' and obj_healthinfo.illtime != None else ''
            healthy['height'] = str(obj_healthinfo.height)+'cm' if obj_healthinfo.height != None else ''
            healthy['weight'] = str(obj_healthinfo.weight)+'kg' if obj_healthinfo.weight != None else ''
            healthy['surgerytime'] = obj_healthinfo.surgerytime if obj_healthinfo.surgerytime != '' and obj_healthinfo.surgerytime != None else ''
            healthy['degree'] = obj_healthinfo.degree if obj_healthinfo.degree != '' and obj_healthinfo.degree != None else ''
            healthy['illtype'] = obj_healthinfo.illtype if obj_healthinfo.illtype != '' and obj_healthinfo.illtype != None else ''

            token = create_token(obj_userinfo.openid)
           
            return HttpResponse(json.dumps({
                "status":200,
                "healthinfo":healthy,
                "accountinfo":account,
                "token":token
            },cls=DecimalEncoder)) 
        except:
            openid = str(uuid.uuid1())
            try:
                with transaction.atomic():
                    obj = Userinfo.objects.create(
                        openid = openid,
                        ipname = phone,
                        phone = phone,
                        disable=1,
                        avatar='http://162.14.104.207:8000/static/avatar/default.png'
                    )
                    Healthinfo.objects.create(
                        openid=openid,
                    )
                    account['ipname'] = obj.ipname
                    account['gender'] = obj.gender
                    account['address'] = obj.address
                    account['phone'] = obj.phone
                    account['avatar'] = obj.avatar
                    healthy['birthyear'] = None
                    healthy['illtime'] = None
                    healthy['height'] = None
                    healthy['weight'] = None
                    healthy['surgerytime'] = None
                    healthy['degree'] = None
                    healthy['illtype'] = None
                    token = create_token(obj.openid)
                    return HttpResponse(json.dumps({
                        "status":200,
                        "healthinfo":healthy,
                        "accountinfo":account,
                        "token":token
                    },cls=DecimalEncoder))
            except:
                return HttpResponse(json.dumps({
                    "status":1
                }) )
    else:
        return HttpResponse(json.dumps({
            "status":3
        }) )

def editHealthInfo(request):
   
    usertoken = request.META.get("HTTP_USERTOKEN")
    
    flag = check_token(usertoken)
   
    if request.method == 'POST' and flag:
        
        birthYear = json.loads(request.body).get('birthYear','')
        illTime = json.loads(request.body).get('illTime','')
        height = json.loads(request.body).get('height','')
        weight = json.loads(request.body).get('weight','')
        surgeryTime = json.loads(request.body).get('surgeryTime','')
        degree = json.loads(request.body).get('degree','')
        illType = json.loads(request.body).get('illType','')
        openid = getopenid(usertoken)
        print(request.POST)
        print(openid)
        try:
            try:
                obj = Healthinfo.objects.get(openid = openid)
                Healthinfo.objects.filter(openid = openid).update(
                    birthyear = birthYear,
                    illtime = illTime,
                    height = height,
                    weight = weight,
                    surgerytime = surgeryTime,
                    degree = degree,
                    illtype = illType,
                )
                
                print('122')
            except:
                with transaction.atomic():
                    Healthinfo.objects.create(
                        openid = openid,
                        birthtear = birthYear,
                        illtime = illTime,
                        height = height,
                        weight = weight,
                        surgerytime = surgeryTime,
                        degree = degree,
                        illtype = illType,
                    )
            return HttpResponse(json.dumps(
                    {
                        'status':200,
                    }
                )

            )
        except:
            return HttpResponse(json.dumps(
                    {
                        'status':1,
                    }
                )

            )
    else:
        return HttpResponse(json.dumps(
                {
                    'status':2,
                }
            )

        )

def editAccountInfo(request):
    usertoken = request.META.get("HTTP_USERTOKEN")
    flag = check_token(usertoken)

    if request.method == 'POST' and flag:
        ipName = json.loads(request.body).get('ipName','')
        name = json.loads(request.body).get('name','')
        gender = json.loads(request.body).get('gender','')
        address = json.loads(request.body).get('address','')
        openid = getopenid(usertoken)
        try:
            with transaction.atomic():
                Userinfo.objects.filter(openid = openid).update(
                    ipname = ipName,
                    name = name,
                    gender = gender,
                    address = address,
                )
            return HttpResponse(json.dumps({
                "status":200
            }))
        except:
            return HttpResponse(json.dumps({
                "status":1
            }))
    else:
        return HttpResponse(json.dumps({
            "status":2
        }))

def token_login(request):
    token = request.META.get("HTTP_USERTOKEN")
    # print(token)
    account = {}
    healthy = {}
    try:
        payload = str(token).split('.')[1]
        payload = signing.b64_decode(payload.encode()).decode()
        payload = signing.loads(payload, key=KEY, salt=SALT)
        openid = payload['username']
        last_token = cache.get(openid)
        # print(token)
        # print(last_token)
        if(last_token != token):
            return HttpResponse(json.dumps({
                "status":401
            }))
        
        else:
            obj_userinfo = Userinfo.objects.get(openid = openid)
            if obj_userinfo.disable == 0:
                return HttpResponse(json.dumps({
                    "status":4
                }) )
            obj_healthinfo = Healthinfo.objects.get(openid = openid)
            
            account['ipname'] = obj_userinfo.ipname 
            account['gender'] = obj_userinfo.gender
            account['address'] = obj_userinfo.address
            account['phone'] = obj_userinfo.phone
            account['name'] = obj_userinfo.name
            account['avatar'] = obj_userinfo.avatar
            account['openid'] = obj_userinfo.openid

            healthy['birthyear'] = obj_healthinfo.birthyear + '年' if obj_healthinfo.birthyear != '' and obj_healthinfo.birthyear != None  else ''
            healthy['illtime'] = obj_healthinfo.illtime if obj_healthinfo.illtime != '' and obj_healthinfo.illtime != None else ''
            healthy['height'] = str(obj_healthinfo.height)+'cm' if obj_healthinfo.height != None else ''
            healthy['weight'] = str(obj_healthinfo.weight)+'kg' if obj_healthinfo.weight != None else ''
            healthy['surgerytime'] = obj_healthinfo.surgerytime if obj_healthinfo.surgerytime != '' and obj_healthinfo.surgerytime != None else ''
            healthy['degree'] = obj_healthinfo.degree if obj_healthinfo.degree != '' and obj_healthinfo.degree != None else ''
            healthy['illtype'] = obj_healthinfo.illtype if obj_healthinfo.illtype != '' and obj_healthinfo.illtype != None else ''

            token = create_token(obj_userinfo.openid)
            
            return HttpResponse(json.dumps({
                "status":200,
                "healthinfo":healthy,
                "accountinfo":account,
                "token":token,
            },cls=DecimalEncoder))
    except:
        return HttpResponse(json.dumps({
            "status":0
        }) )


def wechat_login(request):
    authResult = json.loads(request.body).get('authResult',None)
    account = {}
    healthy = {}

    access_url = 'https://api.weixin.qq.com/sns/auth'
    access_para = {'access_token':authResult['access_token'], 'openid':authResult['openid']}
    access_res = requests.get(access_url, params = access_para)
    user_url = 'https://api.weixin.qq.com/sns/userinfo'
    user_para =  {'access_token':authResult['access_token'], 'openid':authResult['openid'], 'lang':'zh_CN'}
    user_res = requests.get(user_url,params=user_para)
    print(access_res.text)
    print(json.loads(user_res.content))
    data = json.loads(user_res.content)
    print("-----")
    if request.method == 'POST':
        try:
            obj = AuthTable.objects.get(accountid=data['openid'],type='wechat')
            if obj.openid == None:
                print(1)
                return HttpResponse(json.dumps({
                    'status':1,
                    'message':"该账号还没有绑定手机号",
                },cls=DecimalEncoder))
            else:
                openid = obj.openid
                try:
                    print(openid)
                    obj_userinfo = Userinfo.objects.get(openid = openid)
                    obj_healthinfo = Healthinfo.objects.get(openid = openid)
                    if obj_userinfo.disable == 0:
                        return HttpResponse(json.dumps({
                            "status":4
                        }) )
                    account['ipname'] = obj_userinfo.ipname
                    account['gender'] = obj_userinfo.gender
                    account['address'] = obj_userinfo.address
                    account['phone'] = obj_userinfo.phone
                    account['avatar'] = obj_userinfo.avatar
                    account['name'] = obj_userinfo.name
                    account['openid'] = obj_userinfo.openid
                    
                    
                    healthy['birthyear'] = obj_healthinfo.birthyear + '年' if obj_healthinfo.birthyear != '' and obj_healthinfo.birthyear != None  else ''
                    healthy['illtime'] = obj_healthinfo.illtime if obj_healthinfo.illtime != '' and obj_healthinfo.illtime != None else ''
                    healthy['height'] = str(obj_healthinfo.height)+'cm' if obj_healthinfo.height != None else ''
                    healthy['weight'] = str(obj_healthinfo.weight)+'kg' if obj_healthinfo.weight != None else ''
                    healthy['surgerytime'] = obj_healthinfo.surgerytime if obj_healthinfo.surgerytime != '' and obj_healthinfo.surgerytime != None else ''
                    healthy['degree'] = obj_healthinfo.degree if obj_healthinfo.degree != '' and obj_healthinfo.degree != None else ''
                    healthy['illtype'] = obj_healthinfo.illtype if obj_healthinfo.illtype != '' and obj_healthinfo.illtype != None else ''
                    
                    token = create_token(obj_userinfo.openid)
                    print(200)
                    return HttpResponse(json.dumps({
                        "status":200,
                        "healthinfo":healthy,
                        "accountinfo":account,
                        'token':token,
                    },cls=DecimalEncoder))
                except:
                    print(0)
                    return HttpResponse(json.dumps({
                        "status":0,
                    },cls=DecimalEncoder))
        except:
            try:
                with transaction.atomic():
                    AuthTable.objects.create(
                        accountid=data['openid'],
                        type='wechat',
                        avatar=data['headimgurl'],
                        nickname=data['nickname'],
                        # name=data['name']
                    )
                return HttpResponse(json.dumps({
                    "status":1,   #1表示没有绑定手机号码
                },cls=DecimalEncoder))
            except:
                return HttpResponse(json.dumps({
                    "status":0,
                },cls=DecimalEncoder))
    else:
        return HttpResponse(json.dumps({
            "status":0,
        },cls=DecimalEncoder))

'''
1.绑定手机号码没有被注册
2.绑定的手机号码已经注册并且暂时还没有微信id绑定
3.绑定的手机号码已经被绑定
'''
def bind(request):
    phone =json.loads(request.body).get('phone',None)
    wxid = json.loads(request.body).get('wxid',None)
    yzm = json.loads(request.body).get('yzm',None)
    account = {}
    healthy = {}
    code = cache.get(phone)
    print(request.body)
    print(yzm)
    print(yzm == code)
    if request.method == 'POST' and yzm == code:
       
        try:
            
            obj1 = Userinfo.objects.get(phone = phone)
           
            try:
                obj2 = AuthTable.objects.get(openid=obj1.openid)
                return HttpResponse(json.dumps({
                    'status':2    #2表示该手机号码已经被绑定
                }))
            except:
                try:
                    obj3 = AuthTable.objects.get(accountid=wxid,type='wechat')
                    
                    with transaction.atomic():
                        AuthTable.objects.filter(accountid=wxid,type='wechat').update(
                            
                            openid=obj1.openid,
                        )
                        
                except:
                    return HttpResponse(json.dumps({
                        'status':3    #3表示该微信还没有注册
                    }))
                openid = obj1.openid
                obj_userinfo = Userinfo.objects.get(openid = openid)
                obj_healthinfo = Healthinfo.objects.get(openid = openid)
                
                account['ipname'] = obj_userinfo.ipname
                account['gender'] = obj_userinfo.gender
                account['address'] = obj_userinfo.address
                account['phone'] = obj_userinfo.phone
                account['avatar'] = obj_userinfo.avatar
                account['name'] = obj_userinfo.name
                account['openid'] = obj_userinfo.openid

                healthy['birthyear'] = obj_healthinfo.birthyear + '年' if obj_healthinfo.birthyear != '' and obj_healthinfo.birthyear != None  else ''
                healthy['illtime'] = obj_healthinfo.illtime if obj_healthinfo.illtime != '' and obj_healthinfo.illtime != None else ''
                healthy['height'] = str(obj_healthinfo.height)+'cm' if obj_healthinfo.height != None else ''
                healthy['weight'] = str(obj_healthinfo.weight)+'kg' if obj_healthinfo.weight != None else ''
                healthy['surgerytime'] = obj_healthinfo.surgerytime if obj_healthinfo.surgerytime != '' and obj_healthinfo.surgerytime != None else ''
                healthy['degree'] = obj_healthinfo.degree if obj_healthinfo.degree != '' and obj_healthinfo.degree != None else ''
                healthy['illtype'] = obj_healthinfo.illtype if obj_healthinfo.illtype != '' and obj_healthinfo.illtype != None else ''

                token = create_token(obj_userinfo.openid)
                return HttpResponse(json.dumps({
                    "status":200,
                    "healthinfo":healthy,
                    "accountinfo":account,
                    'token':token,
                },cls=DecimalEncoder))

        except:
            openid = str(uuid.uuid1())
            try:
                obj4 = AuthTable.objects.get(accountid=wxid,type='wechat')
               
                with transaction.atomic():
                   
                    obj = Userinfo.objects.create(
                        openid = openid,
                        ipname = obj4.nickname,
                        phone = phone,
                        avatar=obj4.avatar,
                        disable=1,
                        name=obj4.name
                    )
                   
                    Healthinfo.objects.create(
                        openid=openid,
                    )
                   
                    AuthTable.objects.filter(accountid=wxid).update(
                        openid=openid
                    )
                    
                    account['ipname'] = obj.ipname
                    account['gender'] = obj.gender
                    account['address'] = obj.address
                    account['phone'] = obj.phone
                    account['avatar'] = obj.avatar
                    account['openid'] = openid
                   
                    healthy['birthyear'] = None
                    healthy['illtime'] = None
                    healthy['height'] = None
                    healthy['weight'] = None
                    healthy['surgerytime'] = None
                    healthy['degree'] = None
                    healthy['illtype'] = None
                    
                    token = create_token(openid)
                   
                return HttpResponse(json.dumps({
                    "status":200,
                    "healthinfo":healthy,
                    "accountinfo":account,
                    "token":token
                },cls=DecimalEncoder))
            except:
                return HttpResponse(json.dumps({
                    "status":0,
                },cls=DecimalEncoder))
    else:
        return HttpResponse(json.dumps({
            "status":0,
        },cls=DecimalEncoder))


def toothData(request):
    usertoken = request.META.get("HTTP_USERTOKEN")
    flag = check_token(usertoken)
    if request.method == 'POST' and flag:

        data = json.loads(request.body).get('data','')
        sequenceId = json.loads(request.body).get('sequenceId','')
        jobname = json.loads(request.body).get('jobName','')
        openid = getopenid(usertoken)
        try:
            execute.delay(data, openid,jobname,sequenceId)
            return HttpResponse(json.dumps({
                "status":200,
            },cls=DecimalEncoder))
        except:
            return HttpResponse(json.dumps({
                "status":0,
            },cls=DecimalEncoder))


# XFork
# 获取视频列表
# 接收 typepost、page、pageSize
def getvideoList(request):
    usertoken = request.META.get("HTTP_USERTOKEN")
    flag = check_token(usertoken)
    # flag = True

    if request.method == 'POST' and flag:
        # 读取前端发送的参数
        typepost = json.loads(request.body).get('typepost', '')
        page = json.loads(request.body).get('page', '')
        pageSize = json.loads(request.body).get('pageSize', '')
        videoList = []
        try:
            if int(typepost) == 0:
                videoObjectList = LookVideo.objects.filter(status__lt=9)
            else:
                videoObjectList = LookVideo.objects.filter(videotype=int(typepost), status__lt=9)
            paginator = Paginator(videoObjectList, pageSize)  # 进行分页，pageSize为每一页的数量
            num = paginator.num_pages  # 页数
            try:  # 正常页，没有超过最大页数
                videos = paginator.page(page)
            except PageNotAnInteger:  # 如果页数不为整数，则取第一页
                videos = paginator.page(1)
            except EmptyPage:  # 可考虑为最后一页
                # 最后一页返回数据
                response = dict()
                response['total'] = num
                response['videoList'] = ''
                response['page'] = page
                response['status'] = 200
                return JsonResponse(response)

            for video in videos:  # videos就是分页后页上的数据，现在进行一个遍历打包数据
                v = model_to_dict(video)
                # print(v)
                context = dict()  # 在循环处定义字典，免得在添加进列表时被前面添加的数据后面的覆盖
                context['videoId'] = v['id']
                context['url'] = v['appurl']    # 经过mp4_to_flv函数转化后的视频地址
                context['logoUrl'] = v['logourl']
                videoList.append(context)  # 字典添加data列表一并返回

            response = dict()
            response['total'] = num
            response['videoList'] = videoList
            response['page'] = page
            response['status'] = 200

            return JsonResponse(response)
        except:
            response = dict()
            response['status'] = 0
            return JsonResponse(response)
    else:
        context = {'status': 'GET'}
        return JsonResponse(context)

# 得到视频详情
# 接收 videoid
def getvideoDetails(request):
    usertoken = request.META.get("HTTP_USERTOKEN")
    flag = check_token(usertoken)
    # flag = True

    if request.method == 'POST' and flag:
        # 读取前端发送的参数
        videoId = json.loads(request.body).get('videoId', '')
        print(videoId)
        commentsList = []
        try:
            videoComentObList = Comments.objects.filter(videoid=videoId, status__lt=9)  # 获取所需videoId的评论集合
            video = LookVideo.objects.get(id=int(videoId))  # 获取这条视频，转化为int类型

            for videoComent in videoComentObList:
                # vc = model_to_dict(videoComent)
                # print(vc)
                commenter = Userinfo.objects.get(openid=videoComent.userid)
                print(commenter)
                context = dict()  # 在循环处定义字典，免得在添加进列表时被前面添加的数据后面的覆盖
                context['comment'] = videoComent.comment
                context['nickname'] = commenter.ipname
                context['avatar'] = commenter.avatar
                commentsList.append(context)  # 字典添加data列表一并返回
            response = dict()
            response['commentsList'] = commentsList
            response['url'] = video.url
            response['status'] = 200
            return JsonResponse(response)

        except:
            response = dict()
            response['status'] = 0
            return JsonResponse(response)
    else:
        context = {'status': 'GET'}
        return JsonResponse(context)


# 接收上传的视频
# 接收 file
def submitVideo(request):
    # usertoken = request.META.get("HTTP_USERTOKEN")
    # flag = check_token(usertoken)
    flag = True

    if request.method == 'POST' and flag:
 
        # /home/ubuntu/jupyter/backend/brain/app01/static/lookvideo/
        try:
            # 读取前端传来的视频文件
            # print(request.POST.get('openid',None))
            openid = request.POST.get('openid',None)
            # print(openid)
            # openid = '061a6e54-4f58-11ec-b5ea-556b45fb49a9'
            myfile = request.FILES.get("file", None)
            if not myfile:
                print("没有上传视频文件")
            print("上传的文件名字是：" + myfile.name)

            videoName = str(uuid.uuid1()) + "." + myfile.name.split('.').pop()
            destination = open(STATIC_ROOT+"lookvideo/" + videoName, "wb+")  # 打开特定的文件进行二进制的写操作
            for chunk in myfile.chunks():  # 分块写入文件
                destination.write(chunk)
            destination.close()
            obj = Pose.objects.create(
                before_url=STATIC_IP+"static/lookvideo/" + videoName,
                user_openid=openid,
                assessstatus=0,
                time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
            )
            print(STATIC_ROOT+"static/lookvideo/" + videoName)
            job = pose_d.delay(STATIC_ROOT+"lookvideo/" + videoName,obj.id)
            
            print(job)
            response = dict()
            response['status'] = 200
            return JsonResponse(response)

        except:
            response = dict()
            response['status'] = 0
            return JsonResponse(response)
    else:
        context = {'status': 'GET'}
        return JsonResponse(context)    

def getGaitResult(request):
    
    usertoken = request.META.get("HTTP_USERTOKEN")
    flag = check_token(usertoken)
    # flag = True
    # print(flag)
    if request.method == 'POST' and flag:
        try:
            openid = json.loads(request.body).get('openid',None)
            all_num = Pose.objects.filter(assessstatus = 1).count()
            obj = Pose.objects.filter(user_openid=openid,assessstatus=1).order_by('-time').first()
            lte_num = Pose.objects.filter(score__lte=obj.score,assessstatus=1).count()
            percent = round(float(lte_num)/float(all_num),4) * 100
            print(obj.time)
            return HttpResponse(json.dumps({
                "status":200,
                "trainScore":obj.score,
                "percent":percent,
            },cls=DecimalEncoder))
        except:
            return HttpResponse(json.dumps({
                "status":0,
            },cls=DecimalEncoder))
    else:
        return HttpResponse(json.dumps({
            "status":1,
        },cls=DecimalEncoder))

def getTrainResult(request):
    usertoken = request.META.get("HTTP_USERTOKEN")
    flag = check_token(usertoken)
    # flag = True

    if request.method == 'POST' and flag:
        try:
            openid = json.loads(request.body).get('openid',None)
            all_num = TrainResult.objects.all().count()
            obj = TrainResult.objects.filter(openid=openid).order_by('-time').first()
            lte_num = TrainResult.objects.filter(trainscore__lte=obj.trainscore).count()
            percent = round(float(lte_num)/float(all_num),4) * 100
            print(obj.time)
            return HttpResponse(json.dumps({
                "status":200,
                "trainScore":obj.trainscore,
                "percent":percent,
            },cls=DecimalEncoder))
        except:
            return HttpResponse(json.dumps({
                "status":0,
            },cls=DecimalEncoder))
    else:
        return HttpResponse(json.dumps({
            "status":1,
        },cls=DecimalEncoder))

def getRecoveryResult(request):
    usertoken = request.META.get("HTTP_USERTOKEN")
    flag = check_token(usertoken)
    # flag = True

    if request.method == 'POST' and flag:
        try:
            openid = json.loads(request.body).get('openid',None)
            all_num = RecoveryRank.objects.all().count()
            obj = RecoveryRank.objects.filter(openid=openid).order_by('-time').first()
            print(openid)
            lte_num = RecoveryRank.objects.filter(score__lte=obj.score).count()
            percent = round(float(lte_num)/float(all_num),4) * 100
            print(obj.time)
            return HttpResponse(json.dumps({
                "status":200,
                "trainScore":obj.score,
                "percent":percent,
            },cls=DecimalEncoder))
        except:
            return HttpResponse(json.dumps({
                "status":0,
            },cls=DecimalEncoder))
    else:
        return HttpResponse(json.dumps({
            "status":1,
        },cls=DecimalEncoder))

def inputTrainResult(request):
    '''
    token:ZXlKMGVYQWlPaUpLVjFBaUxDSmhiR2NpT2lKa1pXWmhkV3gwSW4wOjFtdkR0eDp5QVVpSzhidWtaRERMdFFqOE05VHFxWUIyM0hZTkxQdDlYZkUxOGdIaFRJ.
    ZXlKMWMyVnlibUZ0WlNJNkluUm9hWE10YVhNdFluSmhhVzR0ZEhKaGFXNHRaR0YwWVMxcGJuQjFkQzF3YkdWaGMyVXRiV0ZyWlMxcGRDSXNJbWxoZENJNk1UWXpPVEF
    6TlRBNU55NHpNVEF6TURFMWZROjFtdkR0eDptTGFTUXdUTWJhUkZRVEVMMWZKN05Xd1lPOXB3dG5fV05LMHg1YlF5dlFn.a3de728aed894c15727c5050b5d52c1e
    '''

    '''
    这里需要算法自己去data文件夹在下读取用户的历史训练数据，然后返回用户openid(即文件名)，训练分数已经评价时间，完成后，请注销885行到889行代码，并令flag=True
    例如：
    openid,trainscore,time = 你引入的算法名（data文件路径）
    同时 一般这个是做一个定时任务，定时任务的模板参考51行到56行的定时任务
    
    '''
    token = json.loads(request.body).get('token',None)
    openid = json.loads(request.body).get('openid',None)
    trainscore = json.loads(request.body).get('trainscore',None)
    time = json.loads(request.body).get('time',None)
    flag = check_token(token)
    

    if flag:
        try:
      
            with transaction.atomic():
                TrainResult.objects.create(
                    openid=openid,
                    time=time,
                    trainscore=trainscore
                )
            return HttpResponse(json.dumps({
                "status":200,
            },cls=DecimalEncoder))
        except:
            return HttpResponse(json.dumps({
                "status":0,
            },cls=DecimalEncoder))
    else:
        return HttpResponse(json.dumps({
            "status":1,
        },cls=DecimalEncoder))
 
            
def getGaitRank(request):
    usertoken = request.META.get("HTTP_USERTOKEN")
    flag = check_token(usertoken)
    print('-------------------------------------')
    if request.method == 'POST' and flag:
        try:
            openid = json.loads(request.body).get('openid',None)
            # all_num = RecoveryRank.objects.all().count()
            # print(openid)
            obj = Pose.objects.filter(user_openid=openid,assessstatus=1).order_by('-time').first()
            # print(obj)
            lte_num = Pose.objects.filter(assessstatus=1).values('user_openid').distinct()
            # print(lte_num)
            # print(lte_num[0])
            
            test = []
            # print(888888)
            for i in lte_num:
                # print(i['user_openid'])
                # print(i.openid)
                ob = Pose.objects.filter(user_openid=i['user_openid'],assessstatus=1).order_by('-time').first()
                print(1)
                if ob.score != None and ob.score != '':
                    test.append(ob)
            def soo(elem):
                return elem.score
            test.sort(key=soo,reverse=True)
            # print(121212)
            print(test)
            data = []
            rank=0
            h=0
            for i in test:
                # print(1212)
                h = h+1
                print(i.user_openid)
                dic = {}
                dic['name'] = Userinfo.objects.get(openid=i.user_openid).ipname
                dic['score'] = i.score
                data.append(dic)
                if i.user_openid == openid:
                    rank = h
            
            # print(data)
            return HttpResponse(json.dumps({
                "status":200,
                'rank':rank,
                "rankList":data,
            
            },cls=DecimalEncoder))
        except:
            return HttpResponse(json.dumps({
                "status":1,
            },cls=DecimalEncoder))
    else:
        return HttpResponse(json.dumps({
            "status":0,
        },cls=DecimalEncoder))

def getRecoveryRank(request):
    usertoken = request.META.get("HTTP_USERTOKEN")
    flag = check_token(usertoken)
    if request.method == 'POST' and flag:
        try:
            openid = json.loads(request.body).get('openid',None)
            # all_num = RecoveryRank.objects.all().count()
            # print(openid)
            obj = RecoveryRank.objects.filter(openid=openid).order_by('-time').first()
            # print(obj)
            lte_num = RecoveryRank.objects.filter().values('openid').distinct()
            # print(lte_num)
            # print(lte_num[0])
            test = []
            for i in lte_num:
                # print(i['openid'])
                # print(i.openid)
                ob = RecoveryRank.objects.filter(openid=i['openid']).order_by('-time').first()
                test.append(ob)
            def soo(elem):
                return elem.score
            test.sort(key=soo,reverse=True)
            
            rank=0
            data = []
            h=0
            for i in test:
                # print(i)
                h=h+1
                dic = {}
                dic['name'] = Userinfo.objects.get(openid=i.openid).ipname
                dic['score'] = i.score
                data.append(dic)
                # print(i.openid)
                if i.openid == openid:
                    rank = h
               
            return HttpResponse(json.dumps({
                "status":200,
                'rank':rank,
                "rankList":data,
            
            },cls=DecimalEncoder))
        except:
            print(1)
            return HttpResponse(json.dumps({
                "status":1,
            },cls=DecimalEncoder))
    else:
        return HttpResponse(json.dumps({
            "status":0,
        },cls=DecimalEncoder))

def inputRecoveryRank(request):
    '''
    token:ZXlKMGVYQWlPaUpLVjFBaUxDSmhiR2NpT2lKa1pXWmhkV3gwSW4wOjFtdkR0eDp5QVVpSzhidWtaRERMdFFqOE05VHFxWUIyM0hZTkxQdDlYZkUxOGdIaFRJ.
    ZXlKMWMyVnlibUZ0WlNJNkluUm9hWE10YVhNdFluSmhhVzR0ZEhKaGFXNHRaR0YwWVMxcGJuQjFkQzF3YkdWaGMyVXRiV0ZyWlMxcGRDSXNJbWxoZENJNk1UWXpPVEF
    6TlRBNU55NHpNVEF6TURFMWZROjFtdkR0eDptTGFTUXdUTWJhUkZRVEVMMWZKN05Xd1lPOXB3dG5fV05LMHg1YlF5dlFn.a3de728aed894c15727c5050b5d52c1e
    '''
    token = json.loads(request.body).get('token',None)
    score = json.loads(request.body).get('score',None)
    time = json.loads(request.body).get('time',None)
    openid = json.loads(request.body).get('openid',None)
    flag = check_token(token)
    print(flag)
    '''
    
    如果要在后端代码里面直接加入算法，请在这里提供算法函数接口，并返回分数，时间和用户唯一标识符
    例如：
    openid,score,time = 你引入的算法名（data文件路径）
    同时 一般这个是做一个定时任务，定时任务的模板参考51行到56行的定时任务

    如果考虑直接加函数输入康复结果排名，那么将969-973行代码注释，并令flag=True
    '''
    if flag:
        try:
            RecoveryRank.objects.create(
                openid=openid,
                time=time,
                score=score
            )
            return HttpResponse(json.dumps({
                "status":200,
            },cls=DecimalEncoder))
        except:
            return HttpResponse(json.dumps({
                "status":0,
            },cls=DecimalEncoder))
    else:
        return HttpResponse(json.dumps({
            "status":0,
        },cls=DecimalEncoder))

def submitAvatar(request):
    usertoken = request.META.get("HTTP_USERTOKEN")
    flag = check_token(usertoken)
    # flag = True

    if request.method == 'POST' and flag:
        try:
        # print(request.body)
            openid = request.POST.get('openid',None)
            # print(openid)
        
            img1=request.FILES.get('file','')
            # print((1111))
            stuff = img1.name.split('.')[-1]
        
            name = str(uuid.uuid1())
            path = STATIC_ROOT + 'avatar/' + name + '.' + stuff
            url = STATIC_IP + 'static/avatar/' + name + '.' + stuff
            # print(path)
            with open(path, 'wb')as fp:
                for i in img1.chunks():
                    #将图片数据写入自己的那个文件
                    fp.write(i)
            print(path)
            with transaction.atomic():
                Userinfo.objects.filter(openid=openid).update(
                    avatar=url
                )
            return HttpResponse(json.dumps({
                "status":200,
                'avatar':url
            },cls=DecimalEncoder))

        except:
            return HttpResponse(json.dumps({
                "status":0,
            },cls=DecimalEncoder))
    else:
        return HttpResponse(json.dumps({
            "status":0,
        },cls=DecimalEncoder))



# def getReport(request):
#     usertoken = request.META.get("HTTP_USERTOKEN")
#     flag = check_token(usertoken)
#     # flag = True

#     if request.method == 'POST' and flag:
#         try:
        
#             openid = json.loads(request.body).get('openid',None)
#             obj = Pose.objects.filter(userid=)


# 写入评论
def comment(request):
    if request.method == 'POST':
        # 读取前端发送的参数
        videoid = json.loads(request.body).get('videoId', '')
        openid = json.loads(request.body).get('openid', '')
        nickname = json.loads(request.body).get('nickname', '')     # 用不上
        avatar = json.loads(request.body).get('avatar', '')         # 用不上
        comment = json.loads(request.body).get('comment', '')
        try:
            cob = Comments()
            cob.videoid = videoid
            cob.userid = openid
            cob.comment = comment
            cob.status = 1
            cob.save()

            response = dict()
            response['status'] = 200
            return JsonResponse(response)
        except:
            response = dict()
            response['status'] = 0
            return JsonResponse(response)
    else:
        context = {'status': 'GET'}
        return JsonResponse(context)


# 获取评估后的报告信息
def getReport(request):
    if request.method == 'POST':
        # 读取前端发送的参数
        openid = json.loads(request.body).get('openid', '')
        data = []
        try:
            reports = Pose.objects.filter(user_openid=openid, assessstatus=1)
            print(reports)
            for report in reports:
                rob = {'content': report.pose_report, 'url': report.doctor_app_url, 'reportId': report.id}
                data.append(rob)

            response = dict()
            response['status'] = 200
            response['data'] = data
            return JsonResponse(response)
        except:
            response = dict()
            response['status'] = 0
            return JsonResponse(response)
    else:
        context = {'status': 'GET'}
        return JsonResponse(context)


def histroyTrainData(request):
    usertoken = request.META.get("HTTP_USERTOKEN")
    flag = check_token(usertoken)
    # flag = True

    if request.method == 'POST' and flag:
        openid = json.loads(request.body).get('openid', '')
        try:
            objs = TrainResult.objects.filter(openid=openid).order_by('-time')
            data = []
            
            for obj in objs:
                content = {}
                time_before = obj.time.split(' ')[0]
                year = time_before.split('-')[0]
                month = time_before.split('-')[1]
                day = time_before.split('-')[2]
                content['time'] = year +'年'+month+'月'+day+'日'
                content['score'] = obj.trainscore
                data.append(content)
            
            oobs = TrainResult.objects.filter(openid=openid).order_by('time')[0:7]
            x = []
            y = []
            
            for obj in oobs:
                
                name = obj.time.split(' ')[0].split('-')[-1] + '日'
                # print(name)
                x.append(name)
                y.append(obj.trainscore)
            return HttpResponse(json.dumps({
                "history":data,
                'x':x,
                'y':y,
                'status':200
            },cls=DecimalEncoder))
        except:
            return HttpResponse(json.dumps({
                "status":0,
            },cls=DecimalEncoder))
    else:
        return HttpResponse(json.dumps({
            "status":0,
        },cls=DecimalEncoder))


def getTrainStatus(request):
    usertoken = request.META.get("HTTP_USERTOKEN")
    flag = check_token(usertoken)
    # flag = True

    if request.method == 'POST' and flag:
        data = json.loads(request.body).get('data',None)
        leftHansZ = None
        rightHandZ = None
        bang = None
        '''
        在这里加算法函数
        函数需要返回leftHansZ,rightHandZ和气球是否bang

        leftHansZ,rightHandZ,bang = 你的算法名字（data）
        
        '''
        return HttpResponse(json.dumps({
                "leftHansZ":leftHansZ,
                'rightHandZ':rightHandZ,
                'bang':bang,
                'status':200
            },cls=DecimalEncoder))  


def submitAddress(request):
    usertoken = request.META.get("HTTP_USERTOKEN")
    flag = check_token(usertoken)
    # flag = True

    if request.method == 'POST' and flag:
        longitude = json.loads(request.body).get('longitude',None)
        latitude = json.loads(request.body).get('latitude',None)
        openid = json.loads(request.body).get('openid',None)
        

        with transaction.atomic():
            Userinfo.objects.filter(openid=openid).update(
                longitude=str(longitude),
                latitude=str(latitude)
            )
        return HttpResponse(json.dumps({
                
                'status':200
            },cls=DecimalEncoder)) 
    else:
        return HttpResponse(json.dumps({
               
                'status':0
            },cls=DecimalEncoder)) 

