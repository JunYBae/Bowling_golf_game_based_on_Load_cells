#! /usr/bin/python2


# for Sound

import pygame


# for HX711 
import time
import sys
import RPi.GPIO as GPIO
from hx711 import HX711

import math


# for threading
import threading

## ----------------------------------------------------------------------------------



## ----------------------------------------------------------------------------------



## ----------------------------------------------------------------------------------

# Sound Code ...
# pygame 라이브러리 초기화
pygame.init()

def BG_Point_Sound(point): # 음악 파일 로드
    if point == 30:
        pygame.mixer.music.load("point_30.mp3")
    elif point == 50:
        pygame.mixer.music.load("point_50.mp3")
    elif point == 60:
        pygame.mixer.music.load("point_60.mp3")
    elif point == 70:
        pygame.mixer.music.load("point_70.mp3")
    elif point == 80:
        pygame.mixer.music.load("point_80.mp3")
    elif point == 100:
        pygame.mixer.music.load("point_100.mp3")
    elif point == 999:
        pygame.mixer.music.load("initial_start_sound.mp3")
    elif point == 998:
        pygame.mixer.music.load("initial_finish_sound.mp3")
    else:
        return
    
    pygame.mixer.music.play() # 음악 재생
    
    # 음악 재생이 끝날 때까지 기다립니다. 실제 애플리케이션에서는 이 방법 대신 적절한 이벤트 처리를 해야 할 수도 있습니다.
    while pygame.mixer.music.get_busy(): 
        pygame.time.Clock().tick(10)


## ----------------------------------------------------------------------------------

referenceUnit = [3166, 3083, 3783, 2766, 2800, 3583, 3266, 2700, 2783, 3500] #each other of loadcell that calibration val
# DC, SCK NUMBERING

# Loadcell PIN many
range_set = 10

# HX711 Loadcell 
hx = []


def initializeLoadcell():
    
    pygame.mixer.music.load("initial_start_sound.mp3")
    pygame.mixer.music.play()
    
    # GPIO 핀 번호 설정
    # 왼쪽 헤더 핀 번호 설정
    left_pins = [4, 17, 27, 22, 10, 9, 11, 5, 6, 13]
    # 오른쪽 헤더 핀 번호 설정
    right_pins = [18, 23, 24, 25, 8, 7, 12, 16, 20, 21]
    
    for i in range(range_set):
        hx.append(HX711(left_pins[i],right_pins[i]))
    
    for sensor in hx:
        sensor.set_reading_format("MSB", "MSB")
    
    for i in range(range_set):
        hx[i].set_reference_unit(referenceUnit[i])
        hx[i].reset()
        hx[i].tare()
        print("Tare done! {}".format(i))
    
    pygame.mixer.music.load("initial_finish_sound.mp3")
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy(): 
        pygame.time.Clock().tick(10)


initializeLoadcell()


## ----------------------------------------------------------------------------------

    

#hx.set_reference_unit(92)



# update

# def cleanAndExit():
#     print("Cleaning...")
#         
#     print("Bye!")
#     sys.exit()
# 
# while True:
#     try:
#         for index, sensor in enumerate(hx):
#             val = int(sensor.get_weight(1))
#             print("[{}].{}||".format(index, val))  # 여기서 index는 센서의 번호입니다.
#             sensor.power_down()
#             sensor.power_up()
#             time.sleep(0.1)
#             
#     except (KeyboardInterrupt, SystemExit):
#         cleanAndExit()
#



BG_Position_of_Point_info = [30, 50, 50, 30, 60, 70, 60, 80, 80, 100]  # 포인트에 대한 점수
BG_weight = [0] * 10  # 공의 무게에 대한 정보를 지님
BG_state = [0] * 10  # 홀 내부 공의 존재 여부
BG_count = [0] * 10
val = [0] * 10

def CheckAndUpdateHoleState():
    for BG_HoleNum in range(range_set):
        BG_weight[BG_HoleNum] = int(val[BG_HoleNum] * 100)

        if BG_state[BG_HoleNum] == 0 and BG_weight[BG_HoleNum] >= 300:  # 이전 상태에서 홀 내부 공이 존재하지 않음 && 공의 무게가 감지됨 (공이 들어온 상태)
            BG_count[BG_HoleNum] += 1
            if BG_count[BG_HoleNum] >= 5:  # 5번 이상 체크가 된 경우
                BG_state[BG_HoleNum] = 1  # 홀 내부 공이 존재하는 상태로 변경
                BG_Point_Sound(BG_Position_of_Point_info[BG_HoleNum])  # 점수 사운드 출력

        elif BG_state[BG_HoleNum] == 0 and BG_weight[BG_HoleNum] < 300:  # 이전 상태에서 홀 내부 공이 존재하지 않음 && 공의 무게가 감지되지 않음 (공이 홀 내부에서 계속 비어있는 상태)
            BG_count[BG_HoleNum] = max(0, BG_count[BG_HoleNum] - 1)

        elif BG_state[BG_HoleNum] == 1 and BG_weight[BG_HoleNum] < 300:  # 이전 상태에서 홀 내부 공이 존재함 && 공의 무게가 감지되지 않음 (공이 빠져나간 상태)
            BG_count[BG_HoleNum] -= 1
            if BG_count[BG_HoleNum] <= 0:  # 30g미만의 상태를 30번 조회 했을 때 유지가 된 상태에서 아직까지 공이 들어왔다고 판단이 안되었다면.
                BG_state[BG_HoleNum] = 0  # 공이 존재하지 않는 상태로 변경

        elif BG_state[BG_HoleNum] == 1 and BG_weight[BG_HoleNum] >= 300:  # 이전 상태에서 홀 내부 공이 존재함 && 공의 무게가 됨 (공이 계속하여 존재하는 상태)
            BG_count[BG_HoleNum] = min(5, BG_count[BG_HoleNum] + 1)



class LoadCellThread(threading.Thread):
    def __init__(self, hx):
        threading.Thread.__init__(self)
        self.hx = hx
        self.daemon = True  # 메인 프로그램 종료 시 쓰레드도 함께 종료되도록 설정

    def run(self):
        while True:
            try:
                for index, sensor in enumerate(self.hx):
                    val[index] = abs(int(sensor.get_weight(1)))
                    print("[{}].{}||".format(index, val[index]))
                    sensor.power_down()
                    sensor.power_up()
                    # time.sleep(0.1)
                CheckAndUpdateHoleState()
                
            except (KeyboardInterrupt, SystemExit):
                cleanAndExit()

def cleanAndExit():
    print("Cleaning...")
    # GPIO 정리 코드 추가 가능
    GPIO.cleanup()  # GPIO 핀 상태를 정리합니다.
    print("Bye!")
    sys.exit()


# hx 리스트는 initializeLoadcell 함수에서 초기화됩니다.
# LoadCellThread 인스턴스를 생성하고 시작합니다.
load_cell_thread = LoadCellThread(hx)
load_cell_thread.start()
