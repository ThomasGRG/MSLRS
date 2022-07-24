from sys import argv
import cv2
import mediapipe as mp
import itertools
import numpy as np
import time
from collections import deque
from multiprocessing import Queue, Process
from queue import Empty
import atexit
from math import ceil
from pathlib import Path
import base64
import json
import tensorflow as tf
import keras

import train
import holistic
import common
import eel

USE_HOLISTIC = False


PRINT_FREQ = 30
PRED_FREQ = 5
assert PRINT_FREQ % PRED_FREQ == 0

#LABELS = common.get_labels('output1/')
LABELS = [None, '00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62']

f_q = Queue()
p_q = Queue()
l_q = Queue()
img_q = Queue()
sStop = 0
model_path = ""

@eel.expose
def waitForStart():
    global sStop
    sStop = 1

@eel.expose
def stop():
    global sStop
    sStop = 2
    print("stopping...")
    print("waiting...")

def video_loop(feature_q, prediction_q, use_holistic, label_q, img_q):
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    cap.set(cv2.CAP_PROP_FOURCC, fourcc)
    if not cap.isOpened():
        print("Error opening Camera")
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("Webcam FPS = {}".format(fps))

    # width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # mp_drawing = mp.solutions.drawing_utils
    print("Awaiting start signal from predict")
    prediction_q.get()
    timestamp = None
    delay = 0
    tag = deque([" "]*5, 5)
    pdecay = time.time()
    print("starting image cap")
    for image, results in holistic.process_capture(cap, use_holistic):
        newtime = time.time()
        if timestamp is not None:
            diff = newtime - timestamp
            #Uncomment to print time between each frame
            #print(diff)
        timestamp = newtime

        raw_flat_row = holistic.to_landmark_row(results, use_holistic)
        normalized_row = holistic.normalize_features(raw_flat_row)
        try:
            feature_q.put(np.array(normalized_row))
        except:
            print("put error")

        try:
            out = prediction_q.get_nowait()
            # out = prediction_q.get()
            # out = prediction_q.get(True,3)
            prediction = np.argmax(out)
            if delay >= PRINT_FREQ:
                if out[prediction] > .75:
                    # if out[prediction] > .6:
                    print("{} {}%".format(
                        LABELS[prediction], out[prediction]*100))
                    if LABELS[prediction] is not None:
                        label_q.put(json.dumps({"label":LABELS[prediction]}))
                    # label_q.put("{} {}%".format(LABELS[prediction], out[prediction]*100))
                    # if LABELS[prediction] not in [tag[-1], None, "None"]:
                        # tag.append(LABELS[prediction])
                    pdecay = time.time()

                else:
                    print("None ({} {}% Below threshold)".format(
                        LABELS[prediction], out[prediction]*100))
                    # label_q.put(json.dumps({"label":"None"}))
                    # label_q.put("None ({} {}% Below threshold)".format(LABELS[prediction], out[prediction]*100))

                delay = 0
            if feature_q.qsize() > 300:
                print(
                    "Warning: Model feature queue overloaded - size = {}".format(feature_q.qsize()))
            print("--> ", end='')
            for i, label in enumerate(out):
                print("{}:{:.2f}% | ".format(LABELS[i], label*100), end='')
            print("\n")
        except Empty:
            print("prediction_q-empty")
            pass

        delay += 1
        if time.time() - pdecay > 7:
            tag = deque([" "]*5, 5)
        # holistic.draw_landmarks(image, results, use_holistic, ' '.join(tag))
        holistic.draw_landmarks(image, results, use_holistic)
        _, imdata = cv2.imencode('.JPG',image)
        img_q.put(json.dumps({"image": base64.b64encode(imdata).decode('ascii')}))
        # cv2.imshow("SignSense", image)


def predict_loop(feature_q, prediction_q, Model_path):
    print("Starting prediction init")
    train.init_gpu()
    model = keras.models.load_model(Model_path)
    print("Sending ready to video loop")
    prediction_q.put("start")

    delay = 0
    window = None
    results = None
    results_len = ceil(PRINT_FREQ / PRED_FREQ)
    print("Starting prediction")
    while True:
        # print("loop")
        try:
            # row = feature_q.get(True,2)
            row = feature_q.get()
            # print(row)
            if window is None:
                window = np.zeros((train.TIMESTEPS, len(row)))

            # Discard oldest frame and append new frame to data window
            window[:-1] = window[1:]
            window[-1] = row

            if delay >= PRED_FREQ:
                out = model(np.array([window]))
                if results is None:
                    results = np.zeros((1, len(LABELS)))
                    # results = np.zeros((results_len, len(LABELS)))
                results[:-1] = results[1:]
                results[-1] = out

                prediction_q.put(np.mean(results, axis=0))
                    # print(np.mean(results, axis=0))
                delay = 0

            delay += 1
        except Empty:
            print("feature_q-empty")
            pass

def waitForCommand(modelPath):
    global sStop
    print("waiting...")
    while sStop == 0:
        eel.sleep(1)
    live_predict(modelPath, USE_HOLISTIC)

def live_predict(modelpath, use_holistic):
    global sStop
    while True:
        if sStop == 1:
            print("starting...")
            started = 0

            p = Process(target=video_loop, args=(f_q, p_q, use_holistic, l_q, img_q,))
            w = Process(target=predict_loop, args=(f_q, p_q, modelpath,))
            # atexit.register(exit_handler, p)
            p.start()

            # atexit.register(exit_handler, w)
            w.start()
            # predict_loop(f_q, p_q)
            
            while True:
                try:
                    if not l_q.empty():
                        row = l_q.get_nowait()
                        eel.print_label(row)
                    if not img_q.empty():
                        row = img_q.get_nowait()
                        eel.print_image(row)
                        if started == 0:
                            started = 1
                    if started == 1:
                        started = 2
                        eel.startStop()
                    if sStop == 2:
                        sStop = 0
                        p.terminate()
                        w.terminate()
                        p.join()
                        w.join()
                        p.close()
                        w.close()
                        clearQ()
                        eel.startStop()
                        break
                except Empty:
                    pass
                eel.sleep(0)
        eel.sleep(1)

def clearQ():
    try:
        while True:
            p_q.get_nowait()
    except Empty:
        pass
    try:
        while True:
            f_q.get_nowait()
    except Empty:
        pass
    try:
        while True:
            l_q.get_nowait()
    except Empty:
        pass
    try:
        while True:
            img_q.get_nowait()
    except Empty:
        pass


def exit_handler(p):
    try:
        p.kill()
    except:
        print("Couldn't kill video_loop")


eel.init('web')

# Usage: [model_path]
if __name__ == "__main__":
    model_path = argv[1]

    #eel.start('index.html', block=False)
    eel.start('index.html', mode='edge', block=False)
    # Use MP Hands only
    #live_predict(model_path, USE_HOLISTIC)
    waitForCommand(model_path)