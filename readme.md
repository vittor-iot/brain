# brain项目本地开发环境搭建
## 一、环境准备
### 1. 安装Mysql、redis、虚拟换使用python3.7
## 二、安装依赖
### 1.pip freeze > requirements.txt
### 2.pip install -r requirements.txt
## 三、修改brain文件
### 1.修改brain/test_settings.py中的数据库配置为本地数据库配置
##### 将这三个参数：STATIC_IP、CACHES、DATABASES修改为本地配置
### 2.修改wsgi.py/wsgi.py中的环境变量为brain.test_settings.py 
    注：如果是生产环境，修改为brain.settings.py
## 四、初始化数据库
### 1. python manage.py makemigrations 或者 执行.sql文件（找项目负责人导出线上数据）
