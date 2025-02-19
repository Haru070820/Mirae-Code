import RPi.GPIO as GPIO
import time
import I2C_LCD_driver
from pad4pi import rpi_gpio
from gpiozero import Servo
from signal import pause

# GPIO 설정
GPIO.setmode(GPIO.BCM)

# LCD 초기화
lcd = I2C_LCD_driver.lcd()

# 서보 모터 설정 (GPIO 18)
servo = Servo(18)

# 키패드 설정 (4x3 키패드 예시)
KEYPAD = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
    ["*", 0, "#"]
]

ROW_PINS = [5, 6, 13, 19]  # 키패드 행 핀
COL_PINS = [12, 16, 20]    # 키패드 열 핀

factory = rpi_gpio.KeypadFactory()
keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)

# 비밀번호 저장 파일 (라즈베리파이에서 유지됨)
PASSWORD_FILE = "password.txt"

# 초기 비밀번호 설정 (파일 없을 경우 기본값)
try:
    with open(PASSWORD_FILE, "r") as file:
        PASSWORD = file.read().strip()
except FileNotFoundError:
    PASSWORD = "1234"
    with open(PASSWORD_FILE, "w") as file:
        file.write(PASSWORD)

entered_code = ""
setting_password = False  # 비밀번호 설정 모드 여부


def save_password(new_password):
    """새 비밀번호를 저장하는 함수"""
    global PASSWORD
    PASSWORD = new_password
    with open(PASSWORD_FILE, "w") as file:
        file.write(new_password)
    lcd.lcd_clear()
    lcd.lcd_display_string("Password Set!", 1)
    time.sleep(1)


def open_lock():
    """잠금 해제 함수"""
    lcd.lcd_clear()
    lcd.lcd_display_string("Unlocked!", 1)
    servo.max()  # 서보 모터 열기
    time.sleep(3)
    close_lock()


def close_lock():
    """잠금 함수"""
    lcd.lcd_clear()
    lcd.lcd_display_string("Locked", 1)
    servo.min()  # 서보 모터 닫기


def key_pressed(key):
    """키패드 입력 처리"""
    global entered_code, setting_password

    if key == "#":  # 엔터키 역할
        if setting_password:  # 새로운 비밀번호 저장 모드
            if len(entered_code) >= 4:  # 비밀번호 최소 4자리 이상
                save_password(entered_code)
                setting_password = False
            else:
                lcd.lcd_clear()
                lcd.lcd_display_string("Min 4 digits!", 1)
                time.sleep(1)
            entered_code = ""  # 입력 초기화
            lcd.lcd_display_string("Enter Code:", 1)

        else:  # 일반 로그인 모드
            if entered_code == PASSWORD:
                open_lock()
            else:
                lcd.lcd_clear()
                lcd.lcd_display_string("Wrong Password", 1)
                time.sleep(1)
            entered_code = ""  # 입력 초기화
            lcd.lcd_display_string("Enter Code:", 1)

    elif key == "*":  # 비밀번호 변경 모드
        lcd.lcd_clear()
        lcd.lcd_display_string("New Password:", 1)
        entered_code = ""
        setting_password = True

    else:
        entered_code += str(key)
        lcd.lcd_display_string("*" * len(entered_code), 2)


keypad.registerKeyPressHandler(key_pressed)

lcd.lcd_display_string("Enter Code:", 1)
close_lock()

try:
    pause()  # 키 입력 대기
except KeyboardInterrupt:
    GPIO.cleanup()