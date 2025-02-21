import RPi.GPIO as GPIO
import RPi_I2C_driver
import time

GPIO.setmode(GPIO.BCM)

SERVO_PIN = 17
RED_PIN = 16
GREEN_PIN = 20
BLUE_PIN = 21
SCL_PIN = 27
SDA_PIN = 22

GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(GREEN_PIN, GPIO.OUT)
GPIO.setup(BLUE_PIN, GPIO.OUT)
GPIO.setup(SCL_PIN, GPIO.OUT)
GPIO.setup(SDA_PIN, GPIO.IN)

servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(2.5)

lcd = RPi_I2C_driver.lcd()

def read_keypad():
    key = "0"
    GPIO.output(SCL_PIN, GPIO.LOW)
    time.sleep(0.000093)
    GPIO.output(SCL_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    
    for i in range(8, 0, -1):
        GPIO.output(SCL_PIN, GPIO.LOW)
        if not GPIO.input(SDA_PIN):
            key = str(9-i)
        GPIO.output(SCL_PIN, GPIO.HIGH)
        time.sleep(0.000001)
    
    time.sleep(0.002)
    return key

def set_rgb(r, g, b):
    GPIO.output(RED_PIN, r)
    GPIO.output(GREEN_PIN, g)
    GPIO.output(BLUE_PIN, b)

def open_door():
    servo.ChangeDutyCycle(2.5)
    time.sleep(0.5)
    servo.ChangeDutyCycle(7.5)
    time.sleep(5)
    servo.ChangeDutyCycle(2.5)
    time.sleep(0.5)

def main():
    correct_password = "8123"
    entered_password = ""
    last_key = "0"
    
    try:
        lcd.lcd_clear()
        lcd.lcd_display_string("Enter Password:", 1)
        lcd.lcd_display_string("Password: ", 2)
        
        while True:
            key = read_keypad()
            if key != "0" and key != last_key:
                last_key = key
                entered_password += key
                lcd.lcd_display_string("Enter Password:", 1)
                lcd.lcd_display_string("Password: " + "*" * len(entered_password), 2)
                time.sleep(0.2)
                
                if len(entered_password) == 4:
                    if entered_password == correct_password:
                        lcd.lcd_clear()
                        lcd.lcd_display_string("Access Granted!", 1)
                        set_rgb(0, 0, 1)
                        open_door()
                    else:
                        lcd.lcd_clear()
                        lcd.lcd_display_string("Access Denied!", 1)
                        set_rgb(1, 0, 0)
                    
                    time.sleep(2)
                    entered_password = ""
                    last_key = "0"
                    lcd.lcd_clear()
                    lcd.lcd_display_string("Enter Password:", 1)
                    lcd.lcd_display_string("Password: ", 2)
                    set_rgb(0, 0, 0)
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        lcd.lcd_clear()
        servo.stop()
        GPIO.cleanup()

if __name__ == '__main__':
    main()


