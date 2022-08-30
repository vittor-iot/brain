from __future__ import absolute_import , unicode_literals
from celery import shared_task
import time
import pymysql
import uuid
import subprocess 
from brain.settings import *
import csv
import cv2
import os
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


# For static images:

# Forforin webcam input:
def avi_to_web_mp4(input_file_path):
    '''
    ffmpeg -i test_result.avi -vcodec h264 test_result.mp4
    @param: [in] input_file_path 带avi或mp4的非H264编码的视频的全路径
    @return: [output] output_file_path 生成的H264编码视频的全路径
    '''
    output_file_path = input_file_path[:-3] + 'mp4'
    cmd = 'ffmpeg -y -i {} -vcodec h264 {}'.format(input_file_path, output_file_path)
    subprocess.call(cmd, shell=True)
    return output_file_path


def mp4_to_flv(input_file_path):
    '''
    ffmpeg -i test_result.avi -vcodec h264 test_result.mp4
    @param: [in] input_file_path 带avi或mp4的非H264编码的视频的全路径
    @return: [output] output_file_path 生成的H264编码视频的全路径
    '''
    output_file_path = input_file_path[:-3] + 'flv'
    cmd = 'ffmpeg -y -i {} -vcodec h264 {}'.format(input_file_path, output_file_path)
    subprocess.call(cmd, shell=True)
    return output_file_path





'''
启动celery
celery -A celery_task worker -P eventlet --loglevel=INFO --concurrency=10

'''
def get_db():
    db =pymysql.connect(host="localhost", user="brain", password="53510678", database="brain",charset="utf8mb4")
    return db

@shared_task
def test_hello():
    print("hello,world!")



@shared_task
def execute(data,openid,jobname,sequenceId):
    db = get_db()
    cursor = db.cursor()
   
    for i in data:
        obj = i['data']
        # print(obj)
        time = i['time']    
        sql = "insert into tran_data (openid,data,time,sequenceid) values ('"+openid+"','"+obj+"','"+str(time) +"','"+sequenceId +"')"
        cursor.execute(sql)
    sql = "insert into record_data (openid,sequenceid) values ('"+openid+"','"+sequenceId +"')"
    cursor.execute(sql)
    try:
        db.commit()
        
    except:
        db.rollback()
    finally:
        db.close()
    print(str(jobname)+' execute cmplete!')

    
@shared_task
def pose_d(path,id):
    print('begin')
    cap = cv2.VideoCapture(path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 视频编解码器
    fps = cap.get(cv2.CAP_PROP_FPS)  # 帧数
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 宽高
    name = str(uuid.uuid1())
    after_path = STATIC_ROOT+'posevideo/'+name+'.avi'
    csv_name = STATIC_ROOT+'posecsv/'+name+'.csv'
    print(csv_name)
    out = cv2.VideoWriter(after_path, fourcc, fps, (width, height))  # 写入视频
    hh=[[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33]]
    with open(csv_name,'w+') as csvfile:
        writer  = csv.writer(csvfile)
        for row in hh:
            writer.writerow(row)

    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            success, image = cap.read()
            
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                break

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            input_csv = open(csv_name,'a')
            h, w, c = image.shape
        # input_csv.close()
            dd = []
            
            csv_write = csv.writer(input_csv,dialect='excel')
            ###3D坐标
            # if results.pose_world_landmarks:
            #     for index, landmarks in enumerate(results.pose_world_landmarks.landmark):
            #         # print(index )
            #         dd.append((landmarks.x,landmarks.y,landmarks.z))
            ###2D坐标
            if results.pose_landmarks:
                for index, landmarks in enumerate(results.pose_landmarks.landmark):
                    # print(index )
                    dd.append((int(landmarks.x*w),int(landmarks.y*h)))
            if len(dd)!=0:
                csv_write.writerow(dd)


            # Draw the pose annotation on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            # Flip the image horizontally for a selfie-view display.
            out.write(cv2.flip(image, 1))
            # cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
            if cv2.waitKey(5) & 0xFF == 27:
                break
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    oo = avi_to_web_mp4(after_path)
    a = oo.split(STATIC_ROOT)[1]
    new_path = STATIC_IP +'static/'+ a
    new_csv = STATIC_IP + 'static/posecsv/'+name+'.csv'

    db = get_db()
    cursor = db.cursor()
    sql = "update pose set after_url='"+new_path+"'where id = " + str(id)
    sql1 = "update pose set csv_url='"+new_csv+"'where id = " + str(id)
    cursor.execute(sql)
    cursor.execute(sql1)
    try:
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()

    
    os.remove(after_path)
    print(oo)

# app查看Lookvideo中的视频
@shared_task
def backendtoflv(path,id):
    oo = mp4_to_flv(path)
    a = oo.split(STATIC_ROOT)[1]
    new_path = STATIC_IP +'static/'+ a

    db = get_db()
    cursor = db.cursor()
    sql = "update look_video set appurl='"+new_path+"'where id = " + str(id)
    cursor.execute(sql)
    try:
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()
    print(oo)

# app查看pose中的doctor_url视频
@shared_task
def backendtoflv_pose(path,id):
    oo = mp4_to_flv(path)
    a = oo.split(STATIC_ROOT)[1]
    new_path = STATIC_IP +'static/'+ a

    db = get_db()
    cursor = db.cursor()
    sql = "update pose set doctor_app_url='"+new_path+"'where id = " + str(id)
    cursor.execute(sql)
    try:
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()
    print(oo)


