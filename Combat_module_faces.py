import cv2
import RPi.GPIO as GPIO
import time

# Ініціалізація камери
cap = cv2.VideoCapture(0)

# Завантаження попередньо навченої моделі Haarcascades для детекції облич
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
# Відключення виведення помилок
GPIO.setwarnings(False)

# Фукнкії обробки кута в дані DutyCycle для керування сервоприводами
def main_x(x):
    OUT_PIN = 12
    PULSE_FREQ = 50
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(OUT_PIN, GPIO.OUT) 
    servo1 = GPIO.PWM(OUT_PIN, PULSE_FREQ)
    servo1.start(0) 
    servo1.ChangeDutyCycle(x/18+3)
    time.sleep(0.05)
    servo1.stop()     
def main_y(y):
    OUT_PIN = 13
    PULSE_FREQ = 50
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(OUT_PIN, GPIO.OUT) 
    servo1 = GPIO.PWM(OUT_PIN, PULSE_FREQ)
    servo1.start(0) 
    servo1.ChangeDutyCycle(y/18+3)
    time.sleep(0.05)
    servo1.stop()

# Основний цикл програми
while True:
    # Захоплення кадру з камери
    ret, frame = cap.read()

    # Перетворення кадру у відтінки сірого
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Детекція облич
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(30, 30))

    # Початкове положення обличчя для сервоприводів
    center_x = 280
    center_y = 210
    # Малювання перехрестя у вигляді прицілу на кожному виявленому обличчі
    for (x, y, w, h) in faces:
        # Знаходження центру обличчя
        center_x = x + w // 2
        center_y = y + h // 2

        # Виведення на екран координат центра обличчя
        coordinates = f"x={center_x}, y={center_y}"
        cv2.putText(frame, coordinates, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        # Малювання вертикальної лінії
        cv2.line(frame, (center_x, y), (center_x, y + h), (0, 255, 0), 2)
        # Малювання горизонтальної лінії
        cv2.line(frame, (x, center_y), (x + w, center_y), (0, 255, 0), 2)
        cv2.circle(frame, (center_x, center_y), 40, (0, 0, 255), 2)
        cv2.circle(frame, (center_x, center_y), 5, (0, 255, 255), 2)

    # Умова спрацювування лазера при виявлені обличчя
    if len(faces) == 0:
        GPIO.setmode(GPIO.BCM)
        pin_relay = 21
        GPIO.setup(pin_relay, GPIO.OUT)
        GPIO.output(pin_relay, GPIO.HIGH)
    else:
        GPIO.setmode(GPIO.BCM)
        pin_relay = 21
        GPIO.setup(pin_relay, GPIO.OUT)
        GPIO.output(pin_relay, GPIO.LOW)

    # переведення координат обличчя в кут для сервоприводів
    ServX = (550-center_x)/6
    ServY = (center_y)/4+37.5

    # переведення координат обличчя в кут для сервоприводів
    main_x(ServX)
    main_y(ServY)

    # Відображення результату на екрані
    cv2.imshow('Face Tracking', frame)

    # Переривання циклу при натисканні клавіші 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Звільнення ресурсів
cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()