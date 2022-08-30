
#broker
broker_url = "redis://127.0.0.1/14"
#任务储存队列
result_backend = "redis://127.0.0.1/15"
 
CELERY_RESULT_SERIALIZER = 'json'  # 结果序列化方案

