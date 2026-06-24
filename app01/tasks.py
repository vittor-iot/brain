from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time
import pymysql
import uuid
import subprocess
import imageio_ffmpeg
from brain.settings import *
import csv
import cv2
import os
import mediapipe as mp

from tools.pymysql_pack import Connect

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


# For static images:

# Forforin webcam input:
def transcode_to_web_mp4(input_file_path, output_file_path=None):
    root, _ = os.path.splitext(input_file_path)
    output_file_path = output_file_path or (root + '.mp4')
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    tmp_output = output_file_path + '.tmp.mp4'
    cmd = [
        ffmpeg, '-y', '-i', input_file_path,
        '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
        '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
        tmp_output,
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError('ffmpeg mp4 transcode failed: {}'.format(result.stderr[-1000:]))
    os.replace(tmp_output, output_file_path)
    return output_file_path


def video_to_web_mp4(input_file_path):
    root, ext = os.path.splitext(input_file_path)
    output_file_path = root + '.mp4'
    if ext.lower() == '.mp4':
        output_file_path = root + '.web.mp4'
    return transcode_to_web_mp4(input_file_path, output_file_path)


def avi_to_web_mp4(input_file_path):
    return video_to_web_mp4(input_file_path)


def mp4_to_flv(input_file_path):
    return video_to_web_mp4(input_file_path)


'''
启动celery
celery -A celery_task worker -P eventlet --loglevel=INFO --concurrency=10

'''


def get_db_config():
    db_settings = DATABASES.get('default', {})
    return {
        'host': os.environ.get('MYSQL_HOST', db_settings.get('HOST', 'localhost')),
        'user': os.environ.get('MYSQL_USER', db_settings.get('USER', 'brain')),
        'password': os.environ.get('MYSQL_PASSWORD', db_settings.get('PASSWORD', '53510678')),
        'database': os.environ.get('MYSQL_DATABASE', db_settings.get('NAME', 'brain')),
        'port': int(os.environ.get('MYSQL_PORT', db_settings.get('PORT', 3306))),
        'charset': 'utf8mb4',
    }


def get_db():
    return pymysql.connect(**get_db_config())


def get_connect():
    return Connect(**get_db_config())


@shared_task
def test_hello():
    print("hello,world!")


@shared_task
def execute(data, openid, jobname, sequenceId, type):
    db = get_db()
    cursor = db.cursor()

    for i in data:
        obj = i['data']
        # print(obj)
        time = i['time']
        sql = "insert into tran_data (openid,data,time,sequenceid,jobname,type) values ('" + openid + "','" + obj + "','" + str(
            time) + "','" + sequenceId + "','" + jobname + "','" + type + "')"
        cursor.execute(sql)
    sql = "insert into record_data (openid,sequenceid) values ('" + openid + "','" + sequenceId + "')"
    cursor.execute(sql)
    try:
        db.commit()

    except:
        db.rollback()
    finally:
        db.close()
    print(str(jobname) + ' execute cmplete!')


@shared_task
def pose_d(path, id):
    print('begin-1')
    cap = cv2.VideoCapture(path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 视频编解码器
    fps = cap.get(cv2.CAP_PROP_FPS) or 25  # 帧数
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 宽高
    name = str(uuid.uuid1())
    raw_after_path = STATIC_ROOT + 'posevideo/' + name + '.raw.mp4'
    after_path = STATIC_ROOT + 'posevideo/' + name + '.mp4'
    csv_name = STATIC_ROOT + 'posecsv/' + name + '.csv'
    print(csv_name)
    out = cv2.VideoWriter(raw_after_path, fourcc, fps, (width, height))  # 写入临时视频
    if not cap.isOpened() or not out.isOpened():
        cap.release()
        out.release()
        raise RuntimeError('Cannot open input or output video for pose task')
    hh = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
         31, 32, 33]]
    with open(csv_name, 'w+') as csvfile:
        writer = csv.writer(csvfile)
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
            input_csv = open(csv_name, 'a')
            h, w, c = image.shape
            # input_csv.close()
            dd = []

            csv_write = csv.writer(input_csv, dialect='excel')
            ###3D坐标
            # if results.pose_world_landmarks:
            #     for index, landmarks in enumerate(results.pose_world_landmarks.landmark):
            #         # print(index )
            #         dd.append((landmarks.x,landmarks.y,landmarks.z))
            ###2D坐标
            if results.pose_landmarks:
                for index, landmarks in enumerate(results.pose_landmarks.landmark):
                    # print(index )
                    dd.append((int(landmarks.x * w), int(landmarks.y * h)))
            if len(dd) != 0:
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
    transcode_to_web_mp4(raw_after_path, after_path)
    try:
        os.remove(raw_after_path)
    except OSError:
        pass
    b = after_path.split(STATIC_ROOT)[1]
    new_path = STATIC_IP + 'static/' + b
    new_csv = STATIC_IP + 'static/posecsv/' + name + '.csv'

    # db = get_db()
    # cursor = db.cursor()
    # sql = "update pose set after_url='"+new_path+"'where id = " + str(id)
    # sql1 = "update pose set csv_url='"+new_csv+"'where id = " + str(id)
    # cursor.execute(sql)
    # cursor.execute(sql1)
    # try:
    #     db.commit()
    # except:
    #     db.rollback()
    # finally:
    #     db.close()
    con = get_connect()
    con.table_update('pose', {'after_url': new_path, 'csv_url': new_csv, 'assessStatus': 1}, 'id', id)
    con.close()

    print('视频转换完成')


# app查看Lookvideo中的视频
@shared_task
def backendtoflv(path, id):
    oo = mp4_to_flv(path)
    a = oo.split(STATIC_ROOT)[1]
    new_path = STATIC_IP + 'static/' + a

    db = get_db()
    cursor = db.cursor()
    sql = "update look_video set appurl='" + new_path + "'where id = " + str(id)
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
def backendtoflv_pose(path, id):
    oo = mp4_to_flv(path)
    a = oo.split(STATIC_ROOT)[1]
    new_path = STATIC_IP + 'static/' + a

    db = get_db()
    cursor = db.cursor()
    sql = "update pose set doctor_app_url='" + new_path + "'where id = " + str(id)
    cursor.execute(sql)
    try:
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()
    print(oo)


@shared_task
def pose_score(path, id):
    score = get_score_by_video_path(path)
    con = get_connect()
    con.table_update('pose', {'score': score}, 'id', id)
    con.close()


def get_pose_score(frame):
    # 将视频帧转换为灰度图像
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 使用阈值分割灰度图像
    ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    # 计算二值图像的轮廓
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # 取出最大的轮廓
    if len(contours) == 0:
        return 0
    else:
        max_contour = max(contours, key=cv2.contourArea)
    # 用最大轮廓绘制外接矩形
    x, y, w, h = cv2.boundingRect(max_contour)
    # 计算外接矩形的面积
    rect_area = w * h
    # 计算最大轮廓的面积
    contour_area = cv2.contourArea(max_contour)
    # 计算步态评估分数
    pose_score = rect_area / contour_area

    return pose_score


def get_score_by_video_path(path):
    cap = cv2.VideoCapture(path)
    pose_frame_total = 0
    pose_score_total = 0
    res_pose_score = 0
    # 循环读取每一帧
    while True:
        # 读取一帧图片
        ret, frame = cap.read()
        # 如果没有读取到图片，则退出循环
        if ret is False:
            print("步态评估总分数：{:.0f}".format(pose_score_total / pose_frame_total * 1000))
            # 释放资源
            res_pose_score = int(pose_score_total / pose_frame_total * 1000)
            break

        # 获取每一帧的步态评估分数
        pose_score = get_pose_score(frame)
        pose_frame_total = pose_frame_total + 1
        pose_score_total = pose_score_total + pose_score
        print("步态评估分数：{:.0f}".format(pose_score * 1000))
    # 释放资源
    cap.release()
    # 返回步态评估总分数
    return res_pose_score
