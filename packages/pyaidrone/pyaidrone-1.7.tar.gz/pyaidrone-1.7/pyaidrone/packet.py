from pyaidrone.deflib import *

class Packet:
    def __init__(self, model = AIDRONE):
        self.model = model
        self.packet = bytearray(20) 
        if self.model == AIDRONE:
            self.packet[0:5] = [0x26, 0xA8, 0x14, 0xB1, 0x14]

    def getPacket(self):
        return self.packet


    def makePacket(self, start, data):
        for n in range(start, start+len(data)):
            self.packet[n] = data[n-start]
        self.packet[5] = DefLib.checksum(self.packet)
#        DefLib._print(self.packet)
        return self.packet
       

    def clearPacket(self):
        for n in range(5, 20):
            self.packet[n] = 0
        if self.model == AIDRONE:
            self.packet[5] = self.packet[14] = 0x01
            self.packet[16] = self.packet[18] = 0x64
        return self.packet
