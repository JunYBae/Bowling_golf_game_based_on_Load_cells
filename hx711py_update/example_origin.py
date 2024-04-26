# for Sound
import pygame
import tkinter as tk
import time 
import sys
from hx711 import HX711
import math
import threading
import RPi.GPIO as GPIO
from tkinter import messagebox

global layer_frame
global label_red, label_blue, label_red_score, label_blue_score
global count_red_blue
global label_timer, state, seconds 
global new_window

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
    elif point == 980:
        pygame.mixer.music.load("red_team_win.mp3")
    elif point == 981:
        pygame.mixer.music.load("blue_team_win.mp3")
    elif point == 982:
        pygame.mixer.music.load("draw.mp3")
    else:
        return
    
    pygame.mixer.music.play() # 음악 재생
    
    # 음악 재생이 끝날 때까지 기다립니다. 실제 애플리케이션에서는 이 방법 대신 적절한 이벤트 처리를 해야 할 수도 있습니다.
    # while pygame.mixer.music.get_busy(): 
        #pygame.time.Clock().tick(10)


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

## ----------------------------------------------------------------------------------
BG_Position_of_Point_info = [30, 50, 50, 30, 60, 70, 60, 80, 80, 100]  # 포인트에 대한 점수
BG_weight = [0] * 10  # 공의 무게에 대한 정보를 지님
BG_state = [0] * 10  # 홀 내부 공의 존재 여부
BG_count = [0] * 10

global val
val = [0] * 10

global BG_score
BG_score = 0

global BG_is_hole
BG_is_hole = False


def CheckAndUpdateHoleState():
    global BG_score, BG_is_hole, val
    
    for BG_HoleNum in range(range_set):
        BG_weight[BG_HoleNum] = int(val[BG_HoleNum] * 100)

        if BG_state[BG_HoleNum] == 0 and BG_weight[BG_HoleNum] >= 300:  # 이전 상태에서 홀 내부 공이 존재하지 않음 && 공의 무게가 감지됨 (공이 들어온 상태)
            BG_count[BG_HoleNum] += 1
            if BG_count[BG_HoleNum] >= 5:  # 5번 이상 체크가 된 경우
                BG_state[BG_HoleNum] = 1  # 홀 내부 공이 존재하는 상태로 변경
                BG_Point_Sound(BG_Position_of_Point_info[BG_HoleNum])  # 점수 사운드 출력
                BG_score = BG_Position_of_Point_info[BG_HoleNum]
                BG_is_hole = True

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
        global val
        while True:
            try:
                for index, sensor in enumerate(self.hx):
                    val[index] = abs(int(sensor.get_weight(1)))
                    #print("[{}].{}||".format(index, val[index]))
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

## ----------------------------------------------------------------------------------


count_red_blue = 0 # red 는 짝수, blue 는 홀수 
state = False # 타이머 상태 (False는 타이머가 동작하지 않음을 의미)
seconds = 11 # 게임 시간 ( 기본 시간 + 1초 해야함 )

def create_layer(parent, row, column, color, content):
    global layer_frame
    global label_red, label_blue, label_red_score, label_blue_score
    global label_timer, state, second
    global new_window
    
    layer_frame = tk.Frame(parent, bg=color)
    layer_frame.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")
    parent.grid_rowconfigure(row, weight=1)
    parent.grid_columnconfigure(column, weight=1)

    if content == '빨강팀':
        label_red = tk.Label(layer_frame, text=content, font=("Arial", 24), bg=color, fg="red")
        label_red.pack(padx=10, pady=10)
        # 레이블을 수평 및 수직으로 가운데 정렬
        label_red.pack_configure(expand=True, anchor=tk.CENTER)
        
    elif content == '파랑팀':
        label_blue = tk.Label(layer_frame, text=content, font=("Arial", 24), bg=color, fg="blue")
        label_blue.pack(padx=10, pady=10)
        # 레이블을 수평 및 수직으로 가운데 정렬
        label_blue.pack_configure(expand=True, anchor=tk.CENTER)
        
    elif content == 100:
        label_red_score = tk.Label(layer_frame, text=str(0), font=("Arial", 24), bg=color)
        label_red_score.pack(padx=10, pady=10)
        # 레이블을 수평 및 수직으로 가운데 정렬
        label_red_score.pack_configure(expand=True, anchor=tk.CENTER)
        
    elif content == 200:
        label_blue_score = tk.Label(layer_frame, text=str(0), font=("Arial", 24), bg=color)
        label_blue_score.pack(padx=10, pady=10)
        # 레이블을 수평 및 수직으로 가운데 정렬
        label_blue_score.pack_configure(expand=True, anchor=tk.CENTER)
        
    elif content == '타이머': 
        label_timer = tk.Label(layer_frame, font=("Arial", 24), bg=color)
        # 레이블을 수평 및 수직으로 가운데 정렬
        label_timer.pack_configure(expand=True, anchor=tk.CENTER)
        label_timer.config(text=f"Timer: Ready")

    elif isinstance(content, list):  # 버튼 생성
        button_frame = tk.Frame(layer_frame)  # 버튼을 담을 수평 상자
        button_frame.pack(pady=5)

        for button_text in content:
            if button_text == '시작':
                button = tk.Button(button_frame, text=button_text, width=15, height=2, command=game_start)
            elif button_text == '돌아가기':
                button = tk.Button(button_frame, text=button_text, width=15, height=2, command=back)
            elif button_text == '초기화':
                button = tk.Button(button_frame, text=button_text, width=15, height=2, command=reset)
            button.pack(side=tk.LEFT, padx=5)

        # 버튼을 수평 및 수직 가운데 정렬
        button_frame.pack_configure(expand=True, anchor=tk.CENTER)

def open_new_window():
    global new_window
    new_window = tk.Toplevel(root)
    new_window.attributes('-fullscreen', True)
    new_window.title("새로운 창")
    # new_window.state('zoomed')  # 최대화
    
    colors = ["white", "white", "white", "white", "white", "white"]
    contents = ['빨강팀', ['초기화', '시작', '돌아가기'], '파랑팀', 100, '타이머', 200]

    for i in range(2):
        for j in range(3):
            index = i * 3 + j
            color = colors[index]
            content = contents[index]
            create_layer(new_window, i, j, color, content)

root = tk.Tk()
root.title("메인 창")
# root.state('zoomed')  # 최대화

def quit_app():
    root.destroy()

def back():
    global new_window, seconds, count_red_blue
    seconds = 11
    count_red_blue = 0
    new_window.destroy()

def reset():
    global new_window, seconds, count_red_blue
    seconds = 11
    count_red_blue = 0
    new_window.destroy()
    open_new_window()

def game_start(count=2):
    global layer_frame
    global label_red, label_blue, label_red_score, label_blue_score
    global label_timer, state, BG_score, BG_is_hole

    if count > 0:
        label_timer.config(text=f"Timer: {count}")
        label_timer.after(1000, game_start, count-1)

    else:
        state = True
        label_blue.config(fg="black")
        BG_score = 0
        BG_is_hole = False
        #label_timer.config(text=f"Timer: {count}")
        running_timer()

def running_timer():
    global label_red, label_blue, label_red_score, label_blue_score
    global count_red_blue
    global label_timer, state, seconds
    global BG_score, BG_is_hole

    if state and count_red_blue < 10 :
        print(count_red_blue)
        
        if seconds > 0:
            seconds -= 1
            label_timer.config(text=f"Timer: {seconds}")
        
        elif seconds <= 0:
            if count_red_blue % 2 == 0: # count down 상태, 전판이 red team 이 했을경우 
                label_red.config(fg="black")
                label_blue.config(fg="blue")
                count_red_blue += 1
                seconds = 11

            elif count_red_blue %2 == 1: # count down 상태, 전판이 blue team 이 했을경우
                label_red.config(fg="red")
                label_blue.config(fg="black")
                count_red_blue += 1
                seconds = 11
                
        if BG_is_hole:
            if count_red_blue % 2 == 0:
                score = int(label_red_score.cget('text'))
                BG_score += score
                label_red_score.config(text=BG_score)
                BG_score = 0
                BG_is_hole = False
                seconds = 0
                
            elif count_red_blue % 2 == 1:
                score = int(label_blue_score.cget('text'))
                BG_score += score
                label_blue_score.config(text=BG_score)
                BG_score = 0
                BG_is_hole = False
                seconds = 0    
                               
        repeat = new_window.after(1000, running_timer)
        
    if count_red_blue == 10:
        
        red_score = int(label_red_score.cget('text'))
        blue_score = int(label_blue_score.cget('text'))
        
            
        if red_score > blue_score:    
            label_timer.config(text="빨강팀 승리", fg='red')
            BG_Point_Sound(980)
        
        elif red_score < blue_score:
            label_timer.config(text="파랑팀 승리", fg='blue')
            BG_Point_Sound(981)
            
        elif red_score == blue_score:
            label_timer.config(text="무승부", fg='green')
            BG_Point_Sound(982)
            
        new_window.after_cancel(repeat)
        return     

# # --------------------------------------------------------------------------------------# #
# 시작 초반 '볼링 골프!' 레이블 출력 
main_title = tk.Label(root, text="볼링 골프!", font=('Helvetica', 24))
main_title.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

game_play_btn = tk.Button(root, text="게임 진행하기", command=open_new_window, width=15, height=2,
                                        font=('Helvetica', 12, 'bold'))  # 텍스트 크기 및 굵기 설정
game_play_btn.place(relx=0.3, rely=0.5, anchor=tk.CENTER) # 중앙에 배치

game_end_btn = tk.Button(root, text="게임 종료하기", command=quit_app, width=15, height=2,
                                      font=('Helvetica', 12, 'bold'))  # 텍스트 크기 및 굵기 설정
game_end_btn.place(relx=0.7, rely=0.5, anchor=tk.CENTER)  # 중앙에 배치
        
initializeLoadcell()
# hx 리스트는 initializeLoadcell 함수에서 초기화됩니다.
# LoadCellThread 인스턴스를 생성하고 시작합니다.
load_cell_thread = LoadCellThread(hx)
load_cell_thread.start()
root.attributes('-fullscreen', True)
root.mainloop()