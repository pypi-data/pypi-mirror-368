import serial
import binascii
import math
from time import sleep
import random
from operator import eq
from threading import Thread
from serial.tools.list_ports import comports
from pyaidrone.parse import *
from pyaidrone.packet import *
from pyaidrone.deflib import *


class AIDrone(Parse,  Packet):
    def __init__(self, receiveCallback = None):
        self.serial = None
        self.isThreadRun = False
        self.parse = Parse(AIDRONE)
        self.makepkt = Packet(AIDRONE)
        self.receiveCallback = receiveCallback
        self.makepkt.clearPacket()
        self.posX = 0
        self.posY = 0
        self.rot = 0        
        # --- 영상 스트리밍 관련 기본값 ---
        self.stream_host = "192.168.4.1"
        self.stream_port = 80
        self.stream_path = "/?action=stream"
        self._cap = None

    def receiveHandler(self):
        while self.isThreadRun:
            readData = self.serial.read(self.serial.in_waiting or 1)
            packet = self.parse.packetArrange(readData)
            if not eq(packet, "None"):
                if self.receiveCallback != None:
                    self.receiveCallback(packet)
            self.serial.write(self.makepkt.getPacket())

        
    def Open(self, portName = "None"):
        if eq(portName, "None"):
            nodes = comports()
            for node in nodes:
                if "CH340" in node.description:
                    portName = node.device
            
            if eq(portName, "None"):
                print("Can't find Serial Port")
                exit()
                return False
        try:
            self.serial = serial.Serial(port=portName, baudrate=115200, timeout=1)
            if self.serial.isOpen():
                self.isThreadRun = True
                self.thread = Thread(target=self.receiveHandler, args=(), daemon=True)
                self.thread.start()
                print("Connected to", portName)                   
                return True
            else:
                print("Can't open " + portName)
                exit()
                return False
        except:
            print("Can't open " + portName)
            exit()
            return False
			

    def Close(self):
        self.isThreadRun = False
        sleep(0.2)
        pkt = self.makepkt.getPacket()
        if (pkt[15]&0x80) == 0x80:
            self.makepkt.clearPacket()
            self.setOption(0x8000)
            self.serial.write(self.makepkt.getPacket())
            sleep(0.2)
        self.serial.write(self.makepkt.clearPacket())
        sleep(0.2)
        if self.serial != None:
            if self.serial.isOpen() == True:
                self.serial.close()

    def setOption(self, option):
        data = option.to_bytes(2, byteorder="little", signed=False)
        self.makepkt.makePacket(14, data)


    def takeoff(self):
        alt = 70
        data = alt.to_bytes(2, byteorder="little", signed=False)
        self.makepkt.makePacket(12, data)
        alt = 0x2F 
        data = alt.to_bytes(2, byteorder="little", signed=False)
        self.setOption(0x2F)


    def landing(self):
        alt = 0
        data = alt.to_bytes(2, byteorder="little", signed=False)
        self.makepkt.makePacket(12, data)


    def altitude(self, alt):
        data = alt.to_bytes(2, byteorder="little", signed=False)
        self.makepkt.makePacket(12, data)


    def velocity(self, dir=0, vel=100):
        if dir > 3:
            return
        if dir==1 or dir==3:
            vel *= -1; 
        data = vel.to_bytes(2, byteorder="little", signed=True)
        if dir==0 or dir==1:
            self.makepkt.makePacket(8, data)
        else:
            self.makepkt.makePacket(6, data)
        self.setOption(0x0F)


    def move(self, dir=0, dist=100):
        if dir > 3:
            return
        if dir==1 or dir==3:
            dist *= -1; 
        if dir==0 or dir==1:
            self.posX += dist
            data = self.posX.to_bytes(2, byteorder="little", signed=True)
            self.makepkt.makePacket(8, data)
        else:
            self.posY += dist
            data = self.posY.to_bytes(2, byteorder="little", signed=True)
            self.makepkt.makePacket(6, data)
        self.setOption(0x2F)
    
	
    def rotation(self, rot=90):
        self.rot += rot               
        data = self.rot.to_bytes(2, byteorder="little", signed=True)
        self.makepkt.makePacket(10, data)



    def motor(self, what, speed):
        speed = DefLib.constrain(speed, 100, 0)
        data = speed.to_bytes(2, byteorder="little", signed=True)
        self.makepkt.makePacket(what*2+6, data)
        self.setOption(0x8000)


    def emergency(self):
        self.setOption(0x00)
        self.serial.write(self.makepkt.getPacket())
        
    # aiDrone.py — AIDrone 클래스 안에 아래 3개 메서드 추가
    def setStreamAddress(self, host: str, port: int = 80, path: str = "/?action=stream"):
        """MJPG-Streamer 주소 구성 요소를 저장합니다."""
        if not isinstance(host, str) or len(host.strip()) == 0:
            raise ValueError("host가 올바르지 않습니다.")
        self.stream_host = host.strip()
        self.stream_port = int(port)
        if not path.startswith("/"):
            path = "/" + path
        self.stream_path = path
        return self._build_stream_url()

    def _build_stream_url(self):
        """내부 사용: 저장된 host/port/path로 URL 생성."""
        if self.stream_port in (80, None):
            return f"http://{self.stream_host}{self.stream_path}"
        return f"http://{self.stream_host}:{self.stream_port}{self.stream_path}"

    def streamon(self, host: str = None, port: int = None, path: str = None, return_url: bool = False):
        """
        MJPG-Streamer 스트림을 엽니다.
        - 인자를 주면 해당 값으로 주소를 덮어쓰고, 안 주면 저장된 값 사용.
        - return_url=True 이면 URL 문자열만 반환(캡처는 열지 않음).
        - 기본 URL 예: http://192.168.4.1/?action=stream
        """
        if host is not None or port is not None or path is not None:
            self.setStreamAddress(host or self.stream_host,
                                  self.stream_port if port is None else port,
                                  self.stream_path if path is None else path)

        url = self._build_stream_url()
        if return_url:
            return url

        # OpenCV는 여기서만 임포트(필요할 때만)
        try:
            import cv2 as cv
        except Exception as e:
            raise RuntimeError(f"OpenCV(cv2) 임포트 실패: {e}")

        # 이전 cap이 열려 있으면 정리
        self.streamoff()

        self._cap = cv.VideoCapture(url)
        if not self._cap.isOpened():
            self._cap.release()
            self._cap = None
            raise RuntimeError(f"스트림 열기 실패: {url}")
        return self._cap

    def streamoff(self):
        """열려 있는 스트림을 닫습니다."""
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None


        
    



