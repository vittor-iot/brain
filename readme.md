# brain项目本地开发环境搭建
## 一、环境准备
### 1. 安装Mysql、redis、虚拟换使用python3.8.12
## 二、安装依赖
### 1.pip freeze > requirements.txt
    注：window下，再requirements.txt中添加一行：pywin32==225
### 2.pip install -r requirements.txt
## 三、修改brain文件
### 1.修改brain/test_settings.py中的数据库配置为本地数据库配置
##### 将这三个参数：STATIC_IP、CACHES、DATABASES修改为本地配置
### 2.修改wsgi.py/wsgi.py中的环境变量为brain.test_settings.py 
    注：如果是生产环境，修改为brain.settings.py
## 四、初始化数据库
### 1. 修改manage.py中的环境变量为brain.test_settings.py
    注：如果是生产环境，修改为brain.settings.py
### 1. python manage.py migrate 或者 执行.sql文件（找项目负责人导出线上数据）


# code-runserver
## 1.登录code-runserver
### 网址：http://162.14.104.207:8889/login
### 密码：138969031790.wjt
## 2.从github上拉取代码
### git pull origin master
## 3.重新部署代码
### 1.查看8000端口是否被占用
#### netstat -anp | grep 8000
### 2.如果被占用，kill掉占用的进程
#### kill -9 进程号
### 3.重新部署
#### 3.1 启动django框架
##### 进入项目目录 -> 激活django虚拟环境 -> 运行项目
cd ~/jupyter/backend/brain; conda activate brain; python manage.py runserver 0.0.0.0:8000
#### 3.2 启动celery
##### 重新打开一个终端 -> 进入项目目录 -> 激活django虚拟环境 -> 运行celery
cd ~/jupyter/backend/brain; conda activate brain; celery -A celery_task worker -P eventlet --loglevel=INFO --concurrency=10
#### 3.3 启动前端程序 
##### 重新打开一个终端 -> 进入项目目录 -> 运行前端程序
cd ~/jupyter/backend/liujiboy-env_web-EnvironmentalVisualization-dev/; npm run serve
