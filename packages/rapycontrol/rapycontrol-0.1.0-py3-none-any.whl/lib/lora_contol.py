import serial
import time

class Lora:
    def __init__(self, port="/dev/serial0", baudrate=9600, timeout=1):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout
        )

    def send(self, data):
        if isinstance(data, str):
            data = data.encode()
        self.ser.write(data)
        print(f"[SEND] {data}")

    def receive(self):
        if self.ser.in_waiting > 0:
            data = self.ser.readline().decode(errors="ignore").strip()
            print(f"[RECV] {data}")
            return data
        return None

    def set_frequency(self, frequency):
        cmd = f"AT+FREQ={frequency}\r\n"
        self.send(cmd)
        time.sleep(0.1)
        return self.receive()

    def set_power(self, power):
        cmd = f"AT+POWER={power}\r\n"
        self.send(cmd)
        time.sleep(0.1)
        return self.receive()

    def get_status(self):
        cmd = "AT+STATUS\r\n"
        self.send(cmd)
        time.sleep(0.1)
        return self.receive()
