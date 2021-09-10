import _thread
import time

import serial
import socket


class Socket:
    def __init__(self, device_Serial_Port='/dev/ttyUSB0', device_Socket_Port=12345, bit_rate=9600):

        if device_Serial_Port == "":
            self.Device_Serial_Port = '/dev/ttyUSB0'
        else:
            self.Device_Serial_Port = device_Serial_Port

        if device_Socket_Port == "":
            self.port = 12345
        else:
            self.port = int(device_Socket_Port)

        if bit_rate == "":
            self.Bit_rate = 9600
        else:
            self.Bit_rate = int(bit_rate)

        self.ws = socket.socket()  # 创建 socket 对象
        self.host = socket.gethostname()
        self.ip = self.get_host_ip()
        self.ws.bind((self.ip, self.port))  # 绑定端口
        self.ws.listen(5)  # 等待客户端连接
        self.connectingAddr = []
        # self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

        while True:
            c, addr = self.ws.accept()  # 建立客户端连接
            self.connectingAddr.append(addr)
            try:
                _thread.start_new_thread(self.sendBetToC, ("Thread-sendBet-" + str(addr), c, addr))
                _thread.start_new_thread(self.recvDataFromC, ("Thread-recvDataFromC-" + str(addr), c, addr))
            except:
                print("线程启动异常")
                self.socketClose(c, addr)

    def sendBetToC(self, threadName, c, addr):
        print(threadName + ": 数据发送")
        ser = serial.Serial(self.Device_Serial_Port, self.Bit_rate, timeout=1)
        while True:
            time.sleep(0.001)
            if addr in self.connectingAddr:

                res = ser.readline()
                try:
                    c.send(res)
                except:
                    self.socketClose(c, addr)
                    ser.close()
                    break
            else:
                ser.close()
                break
        print(threadName + ": 线程结束")

    def recvDataFromC(self, threadName, c, addr):
        print(threadName + ": 数据接受")
        while True:
            try:
                data = c.recv(1024)
            except:
                self.socketClose(c, addr)
                break
            if data == b'':
                self.socketClose(c, addr)
                break
        print(threadName + ": 线程结束")

    def socketClose(self, c, addr):
        c.close()
        try:
            self.connectingAddr.remove(addr)
        except:
            pass

    def get_host_ip(self):
        """
        查询本机ip地址
        :return: ip
        """
        try:
            s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s1.connect(('8.8.8.8', 80))
            ip = s1.getsockname()[0]
        finally:
            s1.close()

        return ip


if __name__ == '__main__':
    import sys, getopt


    def main(argv):
        Device_Serial_Port = ''
        Device_Socket_Port = ''
        Bit_rate = ''
        try:
            opts, args = getopt.getopt(argv, "hc:p:b:", ["cfile=", "pfile=", "bfile="])
        except getopt.GetoptError:
            print('SocketCore.py -c <设备串口> -p <设备端口> -b <串口比特率>')
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print('Help: SocketCore.py -c <设备串口> -p <设备端口> -b <串口比特率>')
                sys.exit()
            elif opt in ("-c", "--cfile"):
                Device_Serial_Port = arg
            elif opt in ("-p", "--pfile"):
                Device_Socket_Port = arg
            elif opt in ("-b", "--bfile"):
                Bit_rate = arg
        return Device_Serial_Port, Device_Socket_Port, Bit_rate


    Device_Serial_Port, Device_Socket_Port, Bit_rate = main(sys.argv[1:])
    socket = Socket(Device_Serial_Port, Device_Socket_Port, Bit_rate)
