import RPi.GPIO as GPIO
import time
import I2C_LCD_driver
from pad4pi import rpi_gpio
from gpiozero import Servo
from signal import pause

# GPIO SETTING
GPIO.setmode(GPIO.BCM)

# LCD RESET
lcd = I2C_LCD_driver.lcd()

# 서보 모터 설정 (GPIO 18)
servo = Servo(18)

# 키패드 설정 (4x3 Key)
KEYPAD = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
    ["*", 0, "#"]
]

ROW_PINS = [5, 6, 13, 19]  # Keypad Column pin
COL_PINS = [12, 16, 20]    # Keypad Row pin

factory = rpi_gpio.KeypadFactory()
keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)

# PW Save
PASSWORD_FILE = "password.txt"

# First PW ( defalut 1234 )
try:
    with open(PASSWORD_FILE, "r") as file:
        PASSWORD = file.read().strip()
except FileNotFoundError:
    PASSWORD = "1234"
    with open(PASSWORD_FILE, "w") as file:
        file.write(PASSWORD)

entered_code = ""
setting_password = False  


def save_password(new_password):
    """New Password"""
    global PASSWORD
    PASSWORD = new_password
    with open(PASSWORD_FILE, "w") as file:
        file.write(new_password)
    lcd.lcd_clear()
    lcd.lcd_display_string("Password Set!", 1)
    time.sleep(1)


def open_lock():
    """open function"""
    lcd.lcd_clear()
    lcd.lcd_display_string("Unlocked!", 1)
    servo.max()  # 서보 모터 열기
    time.sleep(3)
    close_lock()


def close_lock():
    """잠금 함수"""
    lcd.lcd_clear()
    lcd.lcd_display_string("Locked", 1)
    servo.min()  # Servo close


def key_pressed(key):
    """Key press"""
    global entered_code, setting_password

    if key == "#":  # Enter
        if setting_password:  # 새로운 비밀번호 저장 모드 Setting PW Mode
            if len(entered_code) >= 4:  
                save_password(entered_code)
                setting_password = False
            else:
                lcd.lcd_clear()
                lcd.lcd_display_string("Min 4 digits!", 1)
                time.sleep(1)
            entered_code = ""  # RESET
            lcd.lcd_display_string("Enter Code:", 1)

        else:  # login mode
            if entered_code == PASSWORD:
                open_lock()
            else:
                lcd.lcd_clear()
                lcd.lcd_display_string("Wrong Password", 1)
                time.sleep(1)
            entered_code = ""  # enter reset
            lcd.lcd_display_string("Enter Code:", 1)

    elif key == "*":  # PW Setting 
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
    pause() 
except KeyboardInterrupt:
    GPIO.cleanup()