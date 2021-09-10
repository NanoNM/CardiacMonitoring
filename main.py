import _thread
import threading
import json

from PyQt5.Qt import *
import numpy as np
import pyqtgraph as pq
import serial
from qtpy import QtWidgets
import heartpy as hp
import socket

from UI.main import Ui_MainWindow


# ,Ui_wintest.Ui_MainWindow


class Pane(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.s = ''
        self.setupUi(self)
        self.data900 = []
        self.data900Timer = 0
        self.dataIndex = 0
        self.betLow = 1000
        self.betHeight = 0
        self.betAvgArray = []
        self.betAvg = 0
        # self.plot_sth()
        self.data1 = np.random.normal(size=600)
        self.curve1 = self.graphicsView.plot(self.data1, name="mode1")
        # 设定定时器
        self.timer = pq.QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)

        # 定时器信号绑定 update_data 函数

        self.settings = {
            "betLine": "",
            "betPort": "",
        }
        self.getSettingsFile()
        self.betConnect.clicked.connect(self.onBetConnectClicked)
        self.betDisconnect.clicked.connect(self.onBetDisconnectClick)
        # self.ser = serial.Serial('COM5', 9600, timeout=1)

    # def plot_sth(self):
    #     self.graphicsView.plot([1, 2, 3, 4, 5], pen='r', symbol='o')
    def onBetConnectClicked(self):
        self.dataReset()
        self.s = socket.socket()
        print(self.s)
        self.settings["betLine"] = self.betlineEdit.text()
        self.settings["betPort"] = self.betPort.text()
        self.setSettingsFile()
        self.timer.start(0)
        self.s.connect((self.betlineEdit.text(), int(self.betPort.text())))

        # print(self.betlineEdit.text())

    def onBetDisconnectClick(self):
        self.timer.stop()
        self.s.close()
        pass

    def getSettingsFile(self):
        try:
            with open("./Settings.json", 'r+', encoding='utf-8') as file:
                last = file.read()
                last = json.loads(last)
                self.settings["betLine"] = last["betLine"]
                self.settings["betPort"] = last["betPort"]
                self.betlineEdit.setText(self.settings["betLine"])
                self.betPort.setText(self.settings["betPort"])
        except:
            self.setSettingsFile()
            # if settings_file.readlines() == "":
            #     settings_file.writelines(self.settings)

    def setSettingsFile(self):
        with open("./Settings.json", 'w', encoding='utf-8') as file:
            file.write(json.dumps(self.settings, ensure_ascii=False))
            # if settings_file.readlines() == "":
            #     settings_file.writelines(self.settings)
    def update_data(self):
        response = self.s.recv(5)
        string = response.decode('utf-8', 'ignore')
        try:
            y = int(string)
        except ValueError as e:
            y = 0
            pass
        self.data900Timer += 1
        if self.data900Timer > 300:
            if self.data900Timer < 1000:
                self.data900.append(y)
            else:
                try:
                    self.dataCalculation(self.data900)
                except hp.heartpy.exceptions.BadSignalWarning as e:
                    print(e)
                finally:
                    self.data900Timer = 0
                    self.data900.clear()

        # if len(self.data900) == 1100:

        # self.data1[:-1] = self.data1[1:]
        # self.data1[:-1] = y
        # self.data1[1] = y
        self.dataSet(y)

        #
        # print(self.data1)
        # 数据填充到绘制曲线中
        self.curve1.setData(self.data1)

    def dataSet(self, data):
        if self.dataIndex < len(self.data1):
            self.data1[self.dataIndex] = data
        else:
            self.dataIndex = 0
            self.data1[self.dataIndex] = data
        self.dataIndex += 1

    def dataReset(self):
        self.dataIndex = 0

    def dataCalculation(self, data):
        data = np.array(self.data900)
        # 高通滤波
        I = hp.filter_signal(data, cutoff=0.75, sample_rate=500.0, order=3, filtertype='highpass')
        # 低通滤波
        I = hp.filter_signal(I, cutoff=15, sample_rate=500.0, order=3, filtertype='lowpass')
        # 带通滤波
        I = hp.filter_signal(I, cutoff=[0.75, 15], sample_rate=200.0, order=3, filtertype='bandpass')
        wd, m = hp.process(I, 100.0)

        if m['bpm'] != 'nan':
            bet = int(m['bpm'])
            # bet = bet * 2
            if bet < self.betLow:
                self.betLow = bet
            if bet > self.betHeight:
                self.betHeight = bet
            self.betAvgArray.append(bet)
            self.betAvg = sum(self.betAvgArray) / len(self.betAvgArray)

            self.lcdNumber.display(bet)
            self.lcdNumber_2.display(self.betHeight)
            self.lcdNumber_3.display(self.betLow)
            self.lcdNumber_4.display(self.betAvg)
        else:
            self.lcdNumber.display(int(0))
        pass


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    window = Pane()
    window.show()

    sys.exit(app.exec_())
