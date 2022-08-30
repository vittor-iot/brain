from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
 
# 设置django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "celery_task.settings",)
app = Celery("celery_task", backend='redis://localhost:6379/15', broker='redis://localhost:6379/14',include=['app01.tasks'])
 
app.config_from_object('django.conf:settings', namespace='CELERY')
# 发现任务文件每个app下的task.py
app.autodiscover_tasks()
