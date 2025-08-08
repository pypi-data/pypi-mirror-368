import socket
import json
import time

# Define the server IP and port
SERVER_IP = '192.168.4.1'  # Replace with the IP address of the ESP32
SERVER_PORT = 80
TIMEOUT_SECONDS = 3

class SERobESP:
    def __init__(self):
        self.toGPIO = {'0':15, '1':4, '2':16, '3':17, '4':5, '5':18, '6':19, '7':21, '8':22, '9':23}
        self.toAnalog = {'0':0, '1':3, '2':6, '3':7, '4':4, '5':5}
        self.toPwm = {'0':25, '1':26, '2':27, '3':14, '4':13}

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        time.sleep(2)
        self.sock.connect((SERVER_IP, SERVER_PORT))

        self.usrf = self.Usrf(self)
        self.analog = self.Analog(self)
        self.gpio = self.Gpio(self)
        self.servo = self.Servo(self)
        self.pwm = self.Pwm(self)

    def Close(self):
        self.sock.close()

    class Usrf:
        def __init__(self, outer_instance):
            self.outer = outer_instance

        def Distance(self, triggerPin: int, echoPin: int):
            if (triggerPin < 0 or triggerPin > 7) or (echoPin < 0 or echoPin > 7):
                print('\u001b[31m\nUnavailable pin! You can only put 0-7 gpio pin\n\033[0m')
                return
            
            data = {
                "type": "usrf",
                "triggerPin": self.outer.toGPIO[str(triggerPin)],
                "echoPin": self.outer.toGPIO[str(echoPin)]
            }

            self.outer.sock.sendall(str(json.dumps(data) + '\n').encode('utf-8'))
            respone = self.outer.sock.recv(1024).decode('utf-8')

            start_timeout = time.time()
            while respone == '\r\n' and time.time() - start_timeout <= TIMEOUT_SECONDS:
                respone = self.outer.sock.recv(1024).decode('utf-8')

            if respone == '\r\n':
                return -1

            return int(respone)

    class Analog:
        def __init__(self, outer_instance):
            self.outer = outer_instance

        def In(self, pin: int):
            if pin < 0 or pin > 5:
                print('\u001b[31m\nUnavailable pin! You can only put 0-5 analog pin\n\033[0m')
                return
            
            data = {
                "type": "analog",
                "pin": self.outer.toAnalog[str(pin)]
            }
            
            self.outer.sock.sendall(str(json.dumps(data) + '\n').encode('utf-8'))
            respone = self.outer.sock.recv(1024).decode('utf-8')

            start_timeout = time.time()
            while respone == '\r\n' and time.time() - start_timeout <= TIMEOUT_SECONDS:
                respone = self.outer.sock.recv(1024).decode('utf-8')

            if respone == '\r\n':
                return -1

            return int(respone)

    class Gpio:
        def __init__(self, outer_instance):
            self.outer = outer_instance

        def In(self, pin: int):
            if pin < 0 or pin > 7:
                print('\u001b[31m\nUnavailable pin! You can only put 0-7 gpio pin\n\033[0m')
                return
    
            data = {
                "type": "gpioIn",
                "pin": self.outer.toGPIO[str(pin)]
            }

            self.outer.sock.sendall(str(json.dumps(data) + '\n').encode('utf-8'))
            respone = self.outer.sock.recv(1024).decode('utf-8')

            start_timeout = time.time()
            while respone == '\r\n' and time.time() - start_timeout <= TIMEOUT_SECONDS:
                respone = self.outer.sock.recv(1024).decode('utf-8')

            if respone == '\r\n':
                return False

            return bool(int(respone))
        
        def Out(self, pin: int, val: bool):
            if pin < 0 or pin > 7:
                print('\u001b[31m\nUnavailable pin! You can only put 0-7 gpio pin\n\033[0m')
                return
            
            data = {
                "type": "gpioOut",
                "pin": self.outer.toGPIO[str(pin)],
                "value": int(val)
            }

            self.outer.sock.sendall(str(json.dumps(data) + '\n').encode('utf-8'))
            respone = self.outer.sock.recv(1024).decode('utf-8')

            start_timeout = time.time()
            while respone == '\r\n' and time.time() - start_timeout <= TIMEOUT_SECONDS:
                respone = self.outer.sock.recv(1024).decode('utf-8')

            if respone == '\r\n':
                return False

            return bool(int(respone))

    class Servo:
        def __init__(self, outer_instance):
            self.outer = outer_instance

        def Out(self, pin: int, degree: int):
            if pin != 8 and pin != 9:
                print('\u001b[31m\nUnavailable pin! You can only put 8 or 9 gpio pin\n\033[0m')
                return
            if degree < 0 or degree > 180:
                print("\u001b[31m\nUnavailable degree! You can only put from 0 to 180\n\033[0m")
                return

            data = {
                "type": "servo",
                "pin": self.outer.toGPIO[str(pin)],
                "value": degree
            }

            self.outer.sock.sendall(str(json.dumps(data) + '\n').encode('utf-8'))
            respone = self.outer.sock.recv(1024).decode('utf-8')

            start_timeout = time.time()
            while respone == '\r\n' and time.time() - start_timeout <= TIMEOUT_SECONDS:
                respone = self.outer.sock.recv(1024).decode('utf-8')

            if respone == '\r\n':
                return False

            return bool(int(respone))

    class Pwm:
        def __init__(self, outer_instance):
            self.outer = outer_instance

        def Out(self, pin: int, pulse: int):
            if pin < 0 or pin > 4:
                print('\u001b[31m\nUnavailable pin! You can only put 0-4 pwm pin\n\033[0m')
                return
            if pulse < -255 or pulse > 255:
                print("\u001b[31m\nUnavailable pulse! You can only put from -255 to 255\n\033[0m")
                return

            data = {
                "type": "pwm",
                "pin": self.outer.toPwm[str(pin)],
                "value": pulse
            }

            self.outer.sock.sendall(str(json.dumps(data) + '\n').encode('utf-8'))
            respone = self.outer.sock.recv(1024).decode('utf-8')

            start_timeout = time.time()
            while respone == '\r\n' and time.time() - start_timeout <= TIMEOUT_SECONDS:
                respone = self.outer.sock.recv(1024).decode('utf-8')

            if respone == '\r\n':
                return False

            return bool(int(respone))
