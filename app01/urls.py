from django.urls import path, re_path
import app01.views as views
from app01 import consumers

urlpatterns = [
    path('test', views.test),
    path('user/tele/login', views.login),                         # 登录（验证码）
    path('user/getyzm', views.getyzm),                            # 得到验证码
    path('user/submitAvatar', views.submitAvatar),                # 修改头像
    path('user/editAccountInfo', views.editAccountInfo),          # 编辑账户信息
    path('user/editHealthInfo', views.editHealthInfo),            # 编辑健康信息
    path('user/token/login', views.token_login),                  # 登录（token）
    path('user/we_chat/login', views.wechat_login),               # 登录（微信）
    path('user/bind', views.bind),                                # 绑定手机号
    path('user/QRbind', views.qr_bind),                           # 绑定二维码于扫码的手机号
    path('user/submitAddress', views.submitAddress),              # 存经纬度
    path("user/comment", views.comment),                          # 写入评论

    path('submit/toothData', views.toothData),                    # 数据传输

    path('train/getTrainResult', views.getTrainResult),           # 得到训练结果
    path('train/inputGameScore', views.input_game_score),         # 传入游戏得分
    path('train/getGameScore', views.get_game_score),             # 获取游戏得分
    path('train/historyTrainData', views.histroyTrainData),       # 查看历史训练结果
    path('train/inputTrainResult', views.inputTrainResult),       # 输入训练结果(对外提供接口，需要token验证，算法)
    path('train/getTrainStatus', views.getTrainStatus),           # 得到训练状态(算法)
    path('train/getRecoveryResult', views.getRecoveryResult),     # 得到康复训练结果

    path('recovery/getRecoveryRank', views.get_recovery_rank),      # 得到康复结果排名
    path('recovery/inputRecoveryRank', views.inputRecoveryRank),  # 输入康复结果排名(对外提供接口，需要token验证，算法)

    path("video/getVideoList", views.getvideoList),               # 获取视频列表
    path("video/getVideoDetails", views.getvideoDetails),         # 得到视频详情
    path("video/submitVideo", views.submitVideo),                 # 上传视频

    path('Gait/getGaitResult', views.getGaitResult),              # 得到步态训练结果
    path('Gait/getGaitRank', views.get_gait_rank),                  # 得到步态训练排名
    path("gait/getReport", views.getReport),                      # 获取报告
]

websocket_urlpatterns = [
    # 所有websocket以ws/开始是约定俗成的
    re_path(r'login/$', consumers.LoginConsumer.as_asgi()),
]