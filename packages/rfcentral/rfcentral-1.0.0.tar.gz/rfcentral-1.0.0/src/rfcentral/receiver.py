from threading import Thread
from serial import Serial
import struct
import zlib
from datetime import datetime
from .displayer import ConsoleOutput
from .common import GeneralUtil
from .model import FrequencyPowerTime
from .broker import DataBroker
class Receiver(Thread):
    NEW_LINE =  b'\n'

    def __init__(self, console:ConsoleOutput, port:str) -> None:
        Thread.__init__(self)
        self.console = console
        self.port = port
        self.ser = Serial(port=port, baudrate=115200)



    def checksum_calculator(self,data:bytes)->int:
        checksum = zlib.crc32(data)
        return checksum

    def is_header(self,packet:bytes)->bool:
        return len(packet) == 4

    def extract_length_checksum(self, packet:bytes)->int:
        sum  = 0
        if len(packet) == 4:
            values = struct.unpack("!I", packet)
            sum:int = values[0]
        return sum

    def is_last_packet(self,packet:bytes)->bool:
        return packet.find(Receiver.NEW_LINE) != -1

    def remove_index(self,packets: list[bytes])->list[bytes]:
        val:list[bytes] = []
        for packet in packets:
            val.append(packet[1:])
        return val

    def  assemble_into_bytes(self, packets:list[bytes])->bytes:
        data:bytes = b''
        for packet in packets:
            data = data+packet
        return data

    def is_correct_checksum(self,checksum:int, data:bytes)->bool:
        val:bool = False
        obtained_checksum:int = 0
        obtained_checksum = self.checksum_calculator(data)
        return checksum == obtained_checksum

    def ascending_sort(self,packet:bytes):
        #if len(packet) != 0: Alan FIXME check for exception
        index:int = packet[0]
        return index
        #else:
        #    return None
    def build_row_data(self, packets:list[bytes], sum:int)->str|None:
         packets.sort(key=self.ascending_sort)
         assembled_packets = self.remove_index(packets=packets)
         data_bytes = self.assemble_into_bytes(assembled_packets)
         correct_checksum = self.is_correct_checksum(sum, data_bytes)
         if correct_checksum:
             row_data:str = data_bytes.decode()
             # remove the the NEW_LINE ( char terminator)
             row_data = row_data[:len(row_data)-1]
             return row_data
         else:
             print('\a')
             print('\a')
             print('\a')
             print('\a')
             print(f'\033[91m{str(data_bytes)} \033[0m')
             return None

    def receive(self)->None:
        sum = 0
        packets:list[bytes] = []
        while True:
            if self.ser.in_waiting >0:
                packet = self.ser.read_all()
                if packet and isinstance(packet,bytes):
                  if self.is_header(packet):
                      sum = self.extract_length_checksum(packet)
                  else:
                      packets.append(packet)
                      if(self.is_last_packet(packet=packet)):
                          result = self.build_row_data(packets=packets,sum=sum)
                          sum = 0
                          packets = []
                          if result :
                              lst =GeneralUtil.get_freq_power(result)
                              if lst :
                                   now = datetime.now()
                                   date_time = now.strftime("%m-%d-%Y %H:%M:%S")
                                   self.console.display(lst[0],lst[1],date_time=date_time)
                                   model = FrequencyPowerTime(float(lst[0]), float(lst[1]), date_time=date_time)
                                   DataBroker.q.put(model)

    def run(self)->None:
        self.receive()


def main()->None:
    out = ConsoleOutput(60.666)
    receiver = Receiver(out, "COM4")
    receiver.start()

if __name__ == '__main__':
    main()



