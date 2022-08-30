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
from django.contrib.auth.hashers import make_password, check_password
from app01.tasks import *
from django.shortcuts import redirect

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  # 导入分页器
from django.forms.models import model_to_dict

# Create your views here.
from django.conf import settings
from django.core.cache import cache
from django.core import signing
import hashlib
from django.db import transaction

import pickle
import pytz
import requests
from apscheduler.schedulers.background import BackgroundScheduler
HEADER = {'typ': 'JWP', 'alg': 'default'}
KEY = 'LI_WEI_QUAN'
SALT = 'www.yihcampus.com'
HASHER = 'pbkdf2_sha1'
sc2 = BackgroundScheduler()
@sc2.scheduled_job('interval', hours=7)
def db_connect():
    obj = TotalData.objects.all()

sc2.start()

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)


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



# 查询（康复等）视频列表
def queryVideoList(request):
    usertoken = json.loads(request.body).get('token', None)
    flag = check_token(usertoken)
    if request.method == 'POST' and flag:
        # 读取前端发送的参数
        page = json.loads(request.body).get('page', None)
        pageSize = json.loads(request.body).get('pageSize', None)
        videoList = []
        try:
            videoObjectList = LookVideo.objects.filter(status__lt=9).order_by('-id')    # 筛选出状态码小于9的数据
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
                response['data'] = None
                response['page'] = page
                response['status'] = 200
                return JsonResponse(response)

            for video in videos:  # videos就是分页后页上的数据，现在进行一个遍历打包数据
                v = model_to_dict(video)
                # print(v)
                context = dict()  # 在循环处定义字典，免得在添加进列表时被前面添加的数据后面的覆盖
                context['videoId'] = v['id']
                context['url'] = v['url']
                # print(v['videotype'])
                if v['videotype'] == 1:
                    context['type'] = "康复师教学"
                elif v['videotype'] == 2:
                    context['type'] = "医生病例分享"
                elif v['videotype'] == 3:
                    context['type'] = "康复原理"    
                # context['type'] = v['videotype']
                videoList.append(context)  # 字典添加data列表一并返回

            response = dict()
            response['total'] = LookVideo.objects.filter(status__lt=9).count()
            response['data'] = videoList
            response['page'] = page
            response['status'] = 200
            return JsonResponse(response)
        except:
            response = dict()
            response['status'] = 0
            return JsonResponse(response)
    else:
        
        
        return HttpResponse('Error!')


# 删除（康复等）视频
def deleteVideo(request):
    usertoken = json.loads(request.body).get('token', None)
    flag = check_token(usertoken)
    if request.method == 'POST' and flag:
        # print(request.body)
        # 获取要删除的视频id
        videoId = json.loads(request.body).get('videoId', None)

        try:
            vob = LookVideo.objects.get(id=videoId)
            vob.status = 9
            vob.save()
            print("id为" + str(videoId) + "的视频删除成功")

            cobList = Comments.objects.filter(videoid=videoId)
            print(cobList)
            for cob in cobList:
                cob.status=9
                cob.save()
            print("id为" + str(videoId) + "的视频评论删除成功")

            response = dict()
            response['status'] = 200
            return JsonResponse(response)
        except:
            response = dict()
            response['status'] = 0
            return JsonResponse(response)
    else:
        
        return HttpResponse('Error!')


# 接收上传的视频
# 接收 file、type
def uploadVideo(request):
    # print(request.body)
    usertoken = request.POST.get('token',None)
    flag = check_token(usertoken)

    if request.method == 'POST' and flag:
        videoType = request.POST.get('type',None)
        # /home/ubuntu/jupyter/backend/brain/app01/static/lookvideo/
        try:
            # 读取前端传来的视频文件
            # print(videoType)
            myfile = request.FILES.get("file", None)
            if not myfile:
                print("没有上传视频文件")
            print("上传的文件名字是：" + myfile.name)
            videoName = str(uuid.uuid1()) + "." + myfile.name.split('.').pop()
            destination = open("/home/ubuntu/jupyter/backend/brain/app01/static/lookvideo/" + videoName,
                                "wb+")  # 打开特定的文件进行二进制的写操作
            for chunk in myfile.chunks():  # 分块写入文件
                destination.write(chunk)
            destination.close()
            path = "/home/ubuntu/jupyter/backend/brain/app01/static/lookvideo/" + videoName
            
            # job = pose.delay("/home/ubuntu/jupyter/backend/brain/app01/static/lookvideo/" + videoName)

            # 将视频url和type写入数据库
            url = "http://162.14.104.207:8000/static/lookvideo/" + videoName
            print(url)
            vob = LookVideo()
            vob.url = url
            vob.status = 1
            vob.videotype = int(videoType)
            vob.save()

            print(path)
            backendtoflv.delay(path, vob.id)
            return JsonResponse({'status': 200, 'videoId': vob.id})
        except:
            response = dict()
            response['status'] = 0
            return JsonResponse(response)
    else:
        
        return HttpResponse('Error!')

# 接收上传视频的封面
# 接收 file、id
def uploadLogo(request):
    # print(request.body)
    usertoken = request.POST.get('token',None)
    flag = check_token(usertoken)

    if request.method == 'POST' and flag:
        videoId = request.POST.get('videoId',None)
        print(videoId)
        # /home/ubuntu/jupyter/backend/brain/app01/static/lookvideo/
        try:
            # 读取前端传来的文件
            # print(videoType)
            myfile = request.FILES.get("file", None)
            if not myfile:
                print("没有上传图片文件")
            print("上传的文件名字是：" + myfile.name)
            videoName = str(uuid.uuid1()) + "." + myfile.name.split('.').pop()
            path = "/home/ubuntu/jupyter/backend/brain/app01/static/lookvideologo/" + videoName
            destination = open(path, "wb+")  # 打开特定的文件进行二进制的写操作
            for chunk in myfile.chunks():  # 分块写入文件
                destination.write(chunk)
            destination.close()
            
            # job = pose.delay("/home/ubuntu/jupyter/backend/brain/app01/static/lookvideo/" + videoName)

            # 将logo的url写入数据库
            logourl = "http://162.14.104.207:8000/static/lookvideologo/" + videoName
            print(logourl)
            vob = LookVideo.objects.get(id=videoId)
            vob.logourl = logourl
            vob.save()

            return JsonResponse({'status': 200})
        except:
            response = dict()
            response['status'] = 0
            return JsonResponse(response)
    else:
        
        return HttpResponse('Error!')


# 查询评论列表
# 接收 page、pageSize
def queryCommentList(request):
    usertoken = json.loads(request.body).get('token', None)
    flag = check_token(usertoken)
    if request.method == 'POST' and flag:
        # 读取前端发送的参数
        page = json.loads(request.body).get('page', None)
        pageSize = json.loads(request.body).get('pageSize', None)
        commentsList = []
        try:
            videoComentObList = Comments.objects.filter(status__lt=9).order_by("-videoid")    # 筛选出状态码小于9的数据
            paginator = Paginator(videoComentObList, pageSize)  # 进行分页，pageSize为每一页的数量
            num = paginator.num_pages  # 页数

            try:  # 正常页，没有超过最大页数
                comments = paginator.page(page)
            except PageNotAnInteger:  # 如果页数不为整数，则取第一页
                comments = paginator.page(1)
            except EmptyPage:  # 可考虑为最后一页
                # 最后一页返回数据
                response = dict()
                response['total'] = num
                response['page'] = page
                response['data'] = None
                response['status'] = 200
                return JsonResponse(response)

            for comment in comments:  # videos就是分页后页上的数据，现在进行一个遍历打包数据
                print(model_to_dict(comment))
                context = dict()  # 在循环处定义字典，免得在添加进列表时被前面添加的数据后面的覆盖
                context['commentId'] = comment.id
                context['comment'] = comment.comment
                commenter = Userinfo.objects.get(openid=comment.userid)
                context['nickname'] = commenter.ipname
                currentVideo = LookVideo.objects.get(id=comment.videoid)
                context['url'] = currentVideo.url
                context['videoId'] = currentVideo.id
                commentsList.append(context)  # 字典添加data列表一并返回

            response = dict()
            response['total'] = Comments.objects.filter(status__lt=9).count()
            response['data'] = commentsList
            response['page'] = page
            response['status'] = 200
            return JsonResponse(response)
        except:
            response = dict()
            response['status'] = 0
            return JsonResponse(response)
    else:
        
        return HttpResponse('Error!')


# 删除（康复等）评论
def deleteComment(request):
    usertoken = json.loads(request.body).get('token', None)
    flag = check_token(usertoken)
    if request.method == 'POST' and flag:
        # 获取要删除的视频id
        commentId = json.loads(request.body).get('commentId', None)
        try:
            cob = Comments.objects.get(id=commentId)
            # print(model_to_dict(cob))
            cob.status = 9
            cob.save()
            print("id为" + str(commentId) + "的评论删除成功")

            response = dict()
            response['status'] = 200
            return JsonResponse(response)
        except:
            response = dict()
            response['status'] = 0
            return JsonResponse(response)
    else:
        
        return HttpResponse('Error!')


# 查询报告列表
# 接收 page、pageSize
def queryReportList(request):
    usertoken = json.loads(request.body).get('token', None)
    flag = check_token(usertoken)
    if request.method == 'POST' and flag:
        # 读取前端发送的参数
        page = json.loads(request.body).get('page', None)
        pageSize = json.loads(request.body).get('pageSize', None)
        reportsList = []
        try:
            reportObList = Pose.objects.all().order_by('-id')   # 获取所有集合
            paginator = Paginator(reportObList, pageSize)  # 进行分页，pageSize为每一页的数量
            num = paginator.num_pages  # 页数
            try:  # 正常页，没有超过最大页数
                reports = paginator.page(page)
            except PageNotAnInteger:  # 如果页数不为整数，则取第一页
                reports = paginator.page(1)
            except EmptyPage:  # 可考虑为最后一页
                # 最后一页返回数据
                response = dict()
                response['total'] = num
                response['page'] = page
                response['data'] = None
                response['status'] = 200
                return JsonResponse(response)

            for report in reports:  # videos就是分页后页上的数据，现在进行一个遍历打包数据
                # print(model_to_dict(report))
                context = dict()  # 在循环处定义字典，免得在添加进列表时被前面添加的数据后面的覆盖
                context['reportId'] = report.id
                context['beforeUrl'] = report.before_url
                context['afterUrl'] = report.after_url
                if report.assessstatus == 1:
                    context['assessStatus'] = True
                elif report.assessstatus == 0:
                    context['assessStatus'] = False
                # context['assessStatus'] = report.assessstatus
                reportsList.append(context)  # 字典添加data列表一并返回

            response = dict()
            response['total'] = Pose.objects.all().count()
            response['page'] = page
            response['status'] = 200
            response['data'] = reportsList
            return JsonResponse(response)
        except:
            response = dict()
            response['status'] = 0
            return JsonResponse(response)
    else:
        
        return HttpResponse('Error!')


# 查询报告详情
# 接收 reportId，返回content:报告文字内容; url:评估结果视频地址
def queryReportDetails(request):
    usertoken = json.loads(request.body).get('token', None)
    flag = check_token(usertoken)
    if request.method == 'POST' and flag:
        # 读取前端发送的参数
        reportId = json.loads(request.body).get('reportId', None)
        comentsList = []
        try:
            report = Pose.objects.get(id=reportId)  # 获取这条报告数据
            context = {'content': report.pose_report, 'doctorUrl': report.doctor_url}
            comentsList.append(context)

            response = dict()
            response['status'] = 200
            response['data'] = context
            return JsonResponse(response)

        except:
            response = dict()
            response['status'] = 0
            return JsonResponse(response)
    else:
        
        return HttpResponse('Error!')


# 上传步态评估报告
# 接收 file、content
def uploadReport(request):
    usertoken = request.POST.get('token',None)
    flag = check_token(usertoken)
    if request.method == 'POST' and flag:
        content = request.POST.get('content',None)
        reportId = request.POST.get('reportId',None)
        print(content)
        print(reportId)
        # /home/ubuntu/jupyter/backend/brain/app01/static/lookvideo/
        try:
            # 读取前端传来的视频文件
            myfile = request.FILES.get("file", None)
            if not myfile:
                print("没有上传视频文件")
            print("上传的文件名字是：" + myfile.name)
            videoName = str(uuid.uuid1()) + "." + myfile.name.split('.').pop()
            destination = open("/home/ubuntu/jupyter/backend/brain/app01/static/posevideo/" + videoName,
                               "wb+")  # 打开特定的文件进行二进制的写操作
            for chunk in myfile.chunks():  # 分块写入文件
                destination.write(chunk)
            destination.close()
            # job = pose.delay("/home/ubuntu/jupyter/backend/brain/app01/static/lookvideo/" + videoName)

            # 将视频url和type写入数据库
            url = "http://162.14.104.207:8000/static/posevideo/" + videoName
            print(url)
            report = Pose.objects.get(id=reportId)
            print(report)
            report.pose_report = content
            report.doctor_url = url
            report.save()

            path = "/home/ubuntu/jupyter/backend/brain/app01/static/posevideo/" + videoName
            backendtoflv_pose.delay(path, reportId)

            response = dict()
            response['status'] = 200
            return JsonResponse(response)
        except:
            response = dict()
            response['status'] = 0
            return JsonResponse(response)
    else:
        
        return HttpResponse('Error!')

# 改变评估状态
# 接收 reportId
def changeAssess(request):
    usertoken = json.loads(request.body).get('token', None)
    flag = check_token(usertoken)
    if request.method == 'POST' and flag:
        reportId = json.loads(request.body).get('reportId', None)

        try:
            report = Pose.objects.get(id=reportId)
            # print("修改前的状态为：" + str(report.assessstatus))
            # print("修改后的状态为：" + str(abs(report.assessstatus - 1)))
            report.assessstatus = abs(report.assessstatus - 1)
            report.save()

            response = dict()
            response['status'] = 200
            response['assessStatus'] = report.assessstatus
            return JsonResponse(response)
        except:
            response = dict()
            response['status'] = 0
            return JsonResponse(response)
    else:
        
        return HttpResponse('Error!')








def getyzm(request):
    if request.method == 'POST':
        
        telephone = json.loads(request.body).get('phone', None)
        
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
        
        for i in range(0,6):
           
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
            new_name = 'admin'+str(telephone)
            cache.set(new_name,code,None)
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


def register(request):
    phone = json.loads(request.body).get('phone', None)
    password = json.loads(request.body).get('password', None)
    new_password = make_password(password,SALT,HASHER)
    openid = str(uuid.uuid1())
    try:
        user = Adminuser.objects.get(phone=phone)
        return HttpResponse(json.dumps({
            "status":0,
            "message":"this phone has been registered!",
        }) )

    except:
        
        try:
            with transaction.atomic():
                Adminuser.objects.create(
                    admin_id=openid,
                    phone=phone,
                    password=new_password,
                    disable=0,
                )
            return HttpResponse(json.dumps({
                "status":200
            }) )
        except:
            return HttpResponse(json.dumps({
                "status":0
            }) )

def login(request):
    phone = json.loads(request.body).get('phone', None)
    password = json.loads(request.body).get('password', None)
    try:
        # print(request.body)
        user = Adminuser.objects.get(phone=phone)
        # print(password)
        a_true = check_password(password, user.password)
        # print(a_true)
        if a_true:
            if user.disable == 2:
                    return HttpResponse(json.dumps({
                    "status":0,
                    'message':'you have no access to use this system!'
                }) )
            else:
            
                # print(user.admin_id)
                token = create_token(user.admin_id)
                # print(token)
                return HttpResponse(json.dumps({
                    "status":200,
                    'token':token,
                    'disable':user.disable,
                    'openid':user.admin_id,
                }) )
        else:
            return HttpResponse(json.dumps({
                "status":1
            }) )
    
    except:
        return HttpResponse(json.dumps({
            "status":0
        }) )
    

def forgetPassword(request):
    phone = json.loads(request.body).get('phone', None)
    password = json.loads(request.body).get('passWord', None)
    code = json.loads(request.body).get('code', None)
    true_code = cache.get('admin'+str(phone))
    print(request.body)
    if code == true_code:
        try:
            # print(password)
            # print(Adminuser.objects.get(phone=phone).phone)
            user = Adminuser.objects.get(phone=phone)
            Adminuser.objects.filter(phone=phone).update(
                password=make_password(password,SALT,HASHER),
            )
            return HttpResponse(json.dumps({
                "status":200
            }) )

        except:
            return HttpResponse(json.dumps({
                "status":0,
                "message":"no admin",
            }) )
    else:
        return HttpResponse(json.dumps({
            "status":0
        }) )
'''
管理员disable:
    0:超级管理员
    1:普通管理员
    2:禁用
'''
def addAdmin(reuqest):
    print(reuqest.body)
    
    phone = json.loads(reuqest.body).get('phone', None)
    
    password = json.loads(reuqest.body).get('password', None)
    
    disable = int(json.loads(reuqest.body).get('disable', None))
    
    openid = json.loads(reuqest.body).get('openid', None)
    usertoken = json.loads(reuqest.body).get('token', None)
    flag = check_token(usertoken)
    
    if reuqest.method == 'POST' and flag:
        try:
            user = Adminuser.objects.get(admin_id=openid)
            if user.disable == 0:
                new_password = make_password(password,SALT,HASHER)
                openid = str(uuid.uuid1())
                try:
                    user_oo = Adminuser.objects.get(phone=phone)
                    return HttpResponse(json.dumps({
                        "status":0,
                        "message":"this phone has been registered!",
                    }) )
                except:
                    try:
                        with transaction.atomic():
                            Adminuser.objects.create(
                                admin_id=openid,
                                phone=phone,
                                password=new_password,
                                disable=disable,
                            )
                        return HttpResponse(json.dumps({
                            "status":200
                        }) )
                    except:
                        return HttpResponse(json.dumps({
                            "status":0
                        }) )
            else:
                return HttpResponse(json.dumps({
                    "status":0,
                    'message':'you are not superAdmin!'
                }) )
        except:
            return HttpResponse(json.dumps({
                "status":0
            }) )
    else:
        
        return HttpResponse('Error!')

def queryUserList(request):
  
    usertoken = json.loads(request.body).get('token', None)
  
    flag = check_token(usertoken)
    
    
    if flag:
        pageSize = json.loads(request.body).get('pageSize', None)
        page = json.loads(request.body).get('page', None)
        start = (page-1)*pageSize
        sql = 'SELECT * FROM userinfo limit '+str(start)+','+str(start+pageSize)
        
        objs = Userinfo.objects.raw(sql)
        
        all = Userinfo.objects.all().count()
        
        data = []
        for obj in objs:
           
            content = {}
            content['userId'] = obj.openid
            content['nickname'] = obj.ipname
            
            if obj.disable == 1:
                content['disableStatus'] = False
            else:
                content['disableStatus'] = True
            data.append(content)
        return HttpResponse(json.dumps({
            "status":200,
            'page':page,
            'totalPage':all,
            'data':data,
        }) )
    else:
        
        return HttpResponse('Error!')



def queryAdminList(request):
    usertoken = json.loads(request.body).get('token', None)
    flag = check_token(usertoken)
    if flag:
        pageSize = json.loads(request.body).get('pageSize', None)
        page = json.loads(request.body).get('page', None)
        start = (page-1)*pageSize
        sql = 'SELECT * FROM adminuser limit '+str(start)+','+str(start+pageSize)
        objs = Adminuser.objects.raw(sql)
        all = Adminuser.objects.all().count()
        data = []
        for obj in objs:
            content = {}
            content['userId'] = obj.admin_id
            content['phone'] = obj.phone
            if obj.disable != 2:

                content['disableStatus'] = False
            else:
                content['disableStatus'] = True
            if obj.disable == 0:
                content['type'] = 0
            else:
                content['type'] = 1
            data.append(content)
        return HttpResponse(json.dumps({
            "status":200,
            'page':page,
            'totalPage':all,
            'data':data,
        }) )
    else:
        
        return HttpResponse('Error!')



def disableU(request):
    usertoken = json.loads(request.body).get('token', None)
    flag = check_token(usertoken)
    if flag:
        userId = json.loads(request.body).get('openid', None)
        # disable = json.loads(request.body).get('disable', None)
        print(userId)
        try:
            enable = Userinfo.objects.get(openid=userId).disable
            if enable == 1:

                with transaction.atomic():
                    Userinfo.objects.filter(openid=userId).update(
                        disable=0,
                    )
                    token = create_token(userId)
                return HttpResponse(json.dumps({
                    "status":200,
                    'disable':0
                }) )
            else:
                with transaction.atomic():
                    Userinfo.objects.filter(openid=userId).update(
                        disable=1,
                    )
                    token = create_token(userId)
                return HttpResponse(json.dumps({
                    "status":200,
                    'disable':0
                }) )
        except:
            return HttpResponse(json.dumps({
                "status":0
            }) )
    else:
        
        return HttpResponse('Error!')


def disableA(request):
    usertoken = json.loads(request.body).get('token', None)
    flag = check_token(usertoken)
    if flag:
        userId = json.loads(request.body).get('userId', None)
        openid = json.loads(request.body).get('openid', None)

        try:
            if Adminuser.objects.get(admin_id=userId).disable == 0:
                
                return HttpResponse(json.dumps({
                    "status":0
                }) )
            
            obj = Adminuser.objects.get(admin_id=openid)
            if obj.disable == 0:
                kk = Adminuser.objects.get(admin_id=userId).disable
                if kk == 2:

                    with transaction.atomic():
                        Adminuser.objects.filter(admin_id=userId).update(
                            disable=1,
                        )
                        token = create_token(userId)
                    return HttpResponse(json.dumps({
                        "status":200,
                        'disable':1
                    }) )
                else:
                    with transaction.atomic():
                        Adminuser.objects.filter(admin_id=userId).update(
                            disable=2,
                        )
                        token = create_token(userId)
                    return HttpResponse(json.dumps({
                        "status":200,
                        'disable':2
                    }) )
        except:
            return HttpResponse(json.dumps({
                "status":0
            }) )
    else:
        
        return HttpResponse('Error!')


def changePwd(request):
    openid = json.loads(request.body).get('openid', None)
    old_password = json.loads(request.body).get('oldPassWord', None)
    new_password = json.loads(request.body).get('newPassWord', None)
    usertoken = json.loads(request.body).get('token', None)
    flag = check_token(usertoken)
    if flag:
        try:
            user = Adminuser.objects.get(admin_id=openid)
            if check_password(old_password, user.password):
                Adminuser.objects.filter(admin_id=openid).update(
                    password=make_password(new_password,SALT,HASHER)
                )
                return HttpResponse(json.dumps({
                    "status":200
                }) )
            else:
                 return HttpResponse(json.dumps({
                    "status":0
                }) )
        except:
             return HttpResponse(json.dumps({
                "status":0
            }) )
    else:
        
        return HttpResponse('Error!')


