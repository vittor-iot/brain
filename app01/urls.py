from django.contrib import admin
from django.urls import path
import app01.views as views 

urlpatterns = [
    path('test', views.test),
    # path('getname', views.getname),
    path('user/tele/login', views.login),                       #登录（验证码）
    path('user/getyzm', views.getyzm),                          #得到验证码
    path('user/submitAvatar', views.submitAvatar),              #修改头像
    path('user/editAccountInfo', views.editAccountInfo),        #编辑账户信息
    # path('gait/getReport', views.getReport),                  #获得评估报告
    path('user/editHealthInfo', views.editHealthInfo),          #编辑健康信息
    path('user/token/login', views.token_login),                #登录（token）
    path('user/we_chat/login', views.wechat_login),             #登录（微信）
    path('user/bind', views.bind),                              #绑定手机号
    path("user/comment", views.comment),                        #写入评论
    path('submit/toothData', views.toothData),                  #数据传输
    path('train/getTrainResult', views.getTrainResult),         #得到训练结果
    path('train/historyTrainData', views.histroyTrainData),         #查看历史训练结果
    path('train/inputTrainResult', views.inputTrainResult),     #输入训练结果(对外提供接口，需要token验证，算法)
    path('recovery/getRecoveryRank', views.getRecoveryRank),    #得到康复结果排名
    path('recovery/inputRecoveryRank', views.inputRecoveryRank),#输入康复结果排名(对外提供接口，需要token验证，算法)
    path('train/getTrainStatus', views.getTrainStatus),          #得到训练状态(算法)
    path('Gait/getGaitResult', views.getGaitResult),            #得到步态训练结果
    path('Gait/getGaitRank', views.getGaitRank),            #得到步态训练排名
    path('train/getRecoveryResult', views.getRecoveryResult),         #得到康复训练结果
    path('user/submitAddress', views.submitAddress),         #存经纬度



    path("video/getVideoList", views.getvideoList),             #获取视频列表
    path("video/getVideoDetails", views.getvideoDetails),       #得到视频详情
    path("video/submitVideo", views.submitVideo),               #上传视频
    

    path("gait/getReport", views.getReport),                    #获取报告

]
