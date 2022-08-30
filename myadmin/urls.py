from django.contrib import admin
from django.urls import path
import myadmin.views as views 

urlpatterns = [
    path("queryVideoList", views.queryVideoList),           # 查询（康复等）视频列表
    path("deleteVideo", views.deleteVideo),                 # 删除（康复等）视频
    path("uploadVideo", views.uploadVideo),                 # 接收上传的（康复等）视频
    path("uploadLogo", views.uploadLogo),                 # 接收上传的（康复等）视频
    path("queryCommentList", views.queryCommentList),       # 查询评论列表
    path("deleteComment", views.deleteComment),             # 删除（康复等视频）评论
    path("queryReportList", views.queryReportList),         # 查询报告列表
    path("queryReportDetails", views.queryReportDetails),   # 查询报告详情
    path("uploadReport", views.uploadReport),               # 上传步态评估报告
    path("changeAssess", views.changeAssess),               # 改变评估状态


    path("getyzm", views.getyzm),                           # 得到验证码a
    # path("register", views.register),                       # 注册超级管理员
    path("login", views.login),                             # 登录
    path("forgetPassword", views.forgetPassword),           # 忘记密码
    path("addAdmin", views.addAdmin),                       # 添加管理员
    path("queryUserList", views.queryUserList),             # 查询用户列表
    path("queryAdminList", views.queryAdminList),           # 查询管理员列表
    path("disableU", views.disableU),                       # 用户禁用
    path("disableA", views.disableA),                       # 管理员禁用
    path("changePwd", views.changePwd),                     # 修改密码


]
