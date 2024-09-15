import csv
import time
import os

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets, uic, QtGui
from pymeasure.instruments import Instrument, list_resources
from pymeasure.instruments.keithley import Keithley2400


class keithleyGUI(QtWidgets.QWidget):
    def __init__(self):
        super(keithleyGUI, self).__init__()
        self.writer = None
        uic.loadUi("main.ui", self)
        self.setWindowIcon(QtGui.QIcon('logo.png'))

        self.runExpButton.clicked.connect(self.runExp)
        self.abortExpButton.clicked.connect(self.abortExp)
        self.browseButton.clicked.connect(self.browseDataSavingDir)
        self.detectButton.clicked.connect(self.findDevice)
        self.saveCurrentPreferencesButton.clicked.connect(self.saveCurrentPreferences)
        self.applyReadPreferencesButton.clicked.connect(self.applyPreferences)

        self.jtPlot.setBackground('w')
        self.jtPlot.showGrid(x=True, y=True)
        self.jtPlot.setLabel("left", "Current density(mA/cm²)")
        self.jtPlot.setLabel("bottom", "T(S)")

        self.jvPlot.setBackground('w')
        self.jvPlot.showGrid(x=True, y=True)
        self.jvPlot.setLabel("left", "Current density(mA/cm²)")
        self.jvPlot.setLabel("bottom", "U(V)")

        self.itPlot.setBackground('w')
        self.itPlot.showGrid(x=True, y=True)
        self.itPlot.setLabel("left", "I(mA)")
        self.itPlot.setLabel("bottom", "T(S)")

        self.ivPlot.setBackground('w')
        self.ivPlot.showGrid(x=True, y=True)
        self.ivPlot.setLabel("left", "I(mA)")
        self.ivPlot.setLabel("bottom", "U(V)")

        self.ptPlot.setBackground('w')
        self.ptPlot.showGrid(x=True, y=True)
        self.ptPlot.setLabel("left", "P(mW)")
        self.ptPlot.setLabel("bottom", "T(S)")

        self.pvPlot.setBackground('w')
        self.pvPlot.showGrid(x=True, y=True)
        self.pvPlot.setLabel("left", "P(mW)")
        self.pvPlot.setLabel("bottom", "U(V)")

        self.ptMaxPlot.setBackground('w')
        self.ptMaxPlot.showGrid(x=True, y=True)
        self.ptMaxPlot.setLabel("left", "P(mW)")
        self.ptMaxPlot.setLabel("bottom", "T(S)")

        self.jtDataLine = self.jtPlot.plot(pen=pg.mkPen('b'))
        self.jvDataLine = self.jvPlot.plot(pen=pg.mkPen('b'))
        self.itDataLine = self.itPlot.plot(pen=pg.mkPen('b'))
        self.ivDataLine = self.ivPlot.plot(pen=pg.mkPen('b'))
        self.ptDataLine = self.ptPlot.plot(pen=pg.mkPen('b'))
        self.pvDataLine = self.pvPlot.plot(pen=pg.mkPen('b'))
        self.ptMaxDataLine = self.ptMaxPlot.plot(pen=pg.mkPen('b'))

        self.Voc = self.findChild(QtWidgets.QLabel, "VocOut")
        self.Isc = self.findChild(QtWidgets.QLabel, "IscOut")
        self.Jsc = self.findChild(QtWidgets.QLabel, "JscOut")
        self.Pmax = self.findChild(QtWidgets.QLabel, "PmaxOut")
        self.Vmax = self.findChild(QtWidgets.QLabel, "VmaxOut")
        self.Jmax = self.findChild(QtWidgets.QLabel, "JmaxOut")
        self.Imax = self.findChild(QtWidgets.QLabel, "ImaxOut")
        self.FF = self.findChild(QtWidgets.QLabel, "FFOut")
        self.PCE = self.findChild(QtWidgets.QLabel, "PCEOut")
        self.Rs = self.findChild(QtWidgets.QLabel, "RsOut")
        self.Rsh = self.findChild(QtWidgets.QLabel, "RshOut")
        self.Voc_4 = self.findChild(QtWidgets.QLabel, "VocOut_4")
        self.Isc_4 = self.findChild(QtWidgets.QLabel, "IscOut_4")
        self.Jsc_4 = self.findChild(QtWidgets.QLabel, "JscOut_4")
        self.Pmax_4 = self.findChild(QtWidgets.QLabel, "PmaxOut_4")
        self.Vmax_4 = self.findChild(QtWidgets.QLabel, "VmaxOut_4")
        self.Jmax_4 = self.findChild(QtWidgets.QLabel, "JmaxOut_4")
        self.Imax_4 = self.findChild(QtWidgets.QLabel, "ImaxOut_4")
        self.FF_4 = self.findChild(QtWidgets.QLabel, "FFOut_4")
        self.PCE_4 = self.findChild(QtWidgets.QLabel, "PCEOut_4")
        self.Rs_4 = self.findChild(QtWidgets.QLabel, "RsOut_4")
        self.Rsh_4 = self.findChild(QtWidgets.QLabel, "RshOut_4")
        self.Voc_5 = self.findChild(QtWidgets.QLabel, "VocOut_5")
        self.Isc_5 = self.findChild(QtWidgets.QLabel, "IscOut_5")
        self.Jsc_5 = self.findChild(QtWidgets.QLabel, "JscOut_5")
        self.Pmax_5 = self.findChild(QtWidgets.QLabel, "PmaxOut_5")
        self.Vmax_5 = self.findChild(QtWidgets.QLabel, "VmaxOut_5")
        self.Jmax_5 = self.findChild(QtWidgets.QLabel, "JmaxOut_5")
        self.Imax_5 = self.findChild(QtWidgets.QLabel, "ImaxOut_5")
        self.FF_5 = self.findChild(QtWidgets.QLabel, "FFOut_5")
        self.PCE_5 = self.findChild(QtWidgets.QLabel, "PCEOut_5")
        self.Rs_5 = self.findChild(QtWidgets.QLabel, "RsOut_5")
        self.Rsh_5 = self.findChild(QtWidgets.QLabel, "RshOut_5")

        self.running = False

    def runExp(self):
        try:
            # 自检输入参数
            self.checkupStatus = True
            self.checkup()
            if self.checkupStatus == False:
                return

            self.keithley = Keithley2400(self.keithleyAddress.currentText(), timeout=20000)
            self.keithley.reset()
        #    self.keithley.write("ROUT:TERM REAR")  # 设置为后面板
            self.keithley.write("SYST:RSEN ON")  # 启用四线法
            self.guiSwitch(False)
            self.running = True

            self.expProgress(100, 0)

            if self.sweepMode.currentText() == "基础电压扫描":
                self.BasicSweep()
                # 检查是否需要进行同步扫描
                if self.running:
                    reply = QtWidgets.QMessageBox.question(
                        self, '同步扫描', '是否进行同步扫描？',
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                        QtWidgets.QMessageBox.No
                    )
                    if reply == QtWidgets.QMessageBox.Yes:
                        self.BasicSweep(reverse=True)

            elif self.sweepMode.currentText() == "MMPT":
                self.mppTracking()

            elif self.sweepMode.currentText() == "std渐进法":
                self.StdSweep()
                # 检查是否需要进行同步扫描
                if self.running:
                    reply = QtWidgets.QMessageBox.question(
                        self, '同步扫描', '是否进行同步扫描？',
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                        QtWidgets.QMessageBox.No
                    )
                    if reply == QtWidgets.QMessageBox.Yes:
                        self.StdSweep(reverse=True)

            elif self.sweepMode.currentText() == "k渐进法":
                self.KSweep()
                # 检查是否需要进行同步扫描
                if self.running:
                    reply = QtWidgets.QMessageBox.question(
                        self, '同步扫描', '是否进行同步扫描？',
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                        QtWidgets.QMessageBox.No
                    )
                    if reply == QtWidgets.QMessageBox.Yes:
                        self.KSweep(reverse=True)

            self.guiSwitch(True)

            if not self.running:
                pass
            else:
                QtWidgets.QMessageBox.information(self, "结束实验", "实验结束")
                self.running = False


        except Exception as e:
                print(f"Error during measurement: {e}")

    def abortExp(self):
        try:
            # 预留，报错处理
            QtWidgets.QMessageBox.information(self, "中止实验", "实验中止")
            self.running = False

        except Exception as e:
            print(f"Error during measurement: {e}")

    def BasicSweep(self, reverse=False):
        # region 初始化参数，图表，实验数据，计数器
        startVolt = self.basicStartVoltageIn.value()  # 初始电压
        endVolt = self.basicEndVoltageIn.value()  # 终止电压
        stepVolt = self.basicStepIn.value()  # 电压步长
        holdTime = self.basicDurationIn.value()  # 每个电压停留时间
        tolerance = self.VarianceIn.value()  # 稳定电流的标准差
        NPLC = self.NPLCIn.value()
        area = self.AreaIn.value()  # 获取面积输入值

        if reverse:
            startVolt, endVolt = endVolt, startVolt
            stepVolt = -stepVolt

        self.Voc.setText("  V")
        self.Isc.setText("  mA")
        self.Jsc.setText("  mA/cm²")
        self.Pmax.setText("  mW")
        self.Vmax.setText("  V")
        self.Jmax.setText("  mA/cm²")
        self.Imax.setText("  mA")
        self.FF.setText("  %")
        self.PCE.setText("  %")
        self.Rs.setText("  Ω")
        self.Rsh.setText("  Ω")

        current_values = []
        voltage_values = []
        power_values = []
        time_values = []
        currentDensity_values = []
        currentDensity_stable_values = []
        current_stable_values = []
        power_stable_values = []
        voltage_stable_values = []
        time_stable_values = []
        expCount = 0
        tolerance_index = 10**(-3)
        # endregion
        if startVolt != endVolt:
            voltages = np.arange(startVolt, endVolt + stepVolt, stepVolt)
        else:
            voltages = [startVolt]

        self.expProgress(len(voltages), expCount)

        # 初始化csv，进度条
        self.plotInital()
        self.csvInit()
        self.keithley.enable_source()

        measurement_start_time = time.time()
        # 分段电压扫描
        for voltage in voltages:
            if not self.running:  # 检查运行标志
                break

            section_measurement_start_time = time.time()

            count = 0

            while ((time.time() - section_measurement_start_time) < holdTime) and self.running:
                elapsed_time = time.time() - measurement_start_time  # 已过去的时间

                self.keithley.apply_voltage(compliance_current=1.05)
                self.keithley.source_voltage = voltage
                self.keithley.measure_current(nplc=NPLC)
                current = -self.keithley.current * 1000  # 转换为mA与一象限
                currentDensity = current / area  # 计算电流密度
                power = voltage * current  # mW
                voltage_values.append(voltage)
                current_values.append(current)
                power_values.append(power)
                time_values.append(elapsed_time)
                currentDensity_values.append(currentDensity)

                # 更新绘图数据
                self.jtDataLine.setData(time_values, currentDensity_values)
                self.itDataLine.setData(time_values, current_values)
                self.ptDataLine.setData(time_values, power_values)
                self.pvDataLine.setData(voltage_values, power_values)
                QtWidgets.QApplication.processEvents()  # GUI更新

                # 更新csv
                with open(self.csvFilePath, 'a', encoding='utf8', newline='') as csvFile:
                    self.writer = csv.DictWriter(csvFile, fieldnames=['Time', 'Current', 'Voltage', 'Power','Current_Density'])
                    currentExpData = {'Time': elapsed_time, 'Current': current, 'Voltage': voltage, 'Power': power, 'Current_Density': currentDensity}
                    self.writer.writerow(currentExpData)

                if not self.running:  # 检查运行标志
                    break

                section_elapsed_time = time.time() - section_measurement_start_time

                if section_elapsed_time <= self.minimumDurationIn.value():
                    count += 1

                if section_elapsed_time >= self.minimumDurationIn.value():
                    if count == 0:
                        recent_data = [currentDensity]
                    else:
                        recent_data = currentDensity_values[-count:]
                    variance = np.std(recent_data)
                    print(variance)
                    if variance <= (tolerance * tolerance_index):
                        #计算稳定后数据
                        currentDensity_mean = np.mean(recent_data)
                        if count == 0:
                            current_mean = current
                        else:
                            current_mean = np.mean(current_values[-count:])
                        power_stable = voltage * current_mean
                        current_stable_values.append(current_mean)
                        currentDensity_stable_values.append(currentDensity_mean)
                        power_stable_values.append(power_stable)
                        voltage_stable_values.append(voltage)
                        time_stable_values.append(elapsed_time)

                        # 更新绘图数据
                        self.ivDataLine.setData(voltage_stable_values, current_stable_values)
                        self.jvDataLine.setData(voltage_values, currentDensity_values)
                        QtWidgets.QApplication.processEvents()  # GUI更新
                        break  # 如果标准差足够小，跳出循环并进入下一个电压段

            expCount = expCount + 1  # 更新进度条
            self.expProgress(len(voltages), expCount)
        self.keithley.shutdown()
        self.calculateResults(voltage_values, current_values, area)

    def mppTracking(self):
        # region 初始化参数，图表，实验数据，计数器
        startVolt = self.mppStartVoltageIn.value()  # 初始电压
        stepVolt = self.mppDisturbanceIn.value()  # 电压步长
        holdTime = self.mppDurationIn.value()  # 每个电压停留时间
        NPLC = self.NPLCIn.value()
        stepConvergence = self.mppConvergenceIn.value() * 0.01
        area = self.AreaIn.value()  # 获取面积输入值

        current_values = []
        voltage_values = []
        power_values = []
        time_values = []
        power_max_values = []
        time_max_values = []
        currentDensity_values = []

        voltage = startVolt
        # endregion
        self.mppIfCheckOut.setText("")
        self.mppResultVoltageOut.setText("")
        self.mppResultCurrentOut.setText("")
        self.mppResultPowerOut.setText("")

        # 初始化csv，进度条
        self.plotInital()
        self.csvInit()
        self.keithley.enable_source()

        measurement_start_time = time.time()
        while ((time.time() - measurement_start_time) < holdTime) and self.running:
            check = False
            #分别扫描voltage、voltage_P、voltage_N，扫描时间X3
            voltage_P = voltage + stepVolt
            voltage_N = voltage - stepVolt

            elapsed_time = time.time() - measurement_start_time  # 已过去的时间

            self.keithley.apply_voltage(compliance_current=1.05)
            self.keithley.source_voltage = voltage
            self.keithley.measure_current(nplc=NPLC)

            current = -self.keithley.current  # 读取电流
            power = voltage * current  # 计算功率
            currentDensity = current / area  # 计算电流密度

            voltage_values.append(voltage)
            current_values.append(current)
            power_values.append(power)
            time_values.append(elapsed_time)

            # 更新绘图数据
            self.jtDataLine.setData(time_values, currentDensity_values)
            self.jvDataLine.setData(voltage_values, currentDensity_values)
            self.itDataLine.setData(time_values, current_values)
            self.ivDataLine.setData(voltage_values, current_values)
            self.ptDataLine.setData(time_values, power_values)
            self.pvDataLine.setData(voltage_values, power_values)
            QtWidgets.QApplication.processEvents()  # GUI更新

            # 更新csv
            with open(self.csvFilePath, 'a', encoding='utf8', newline='') as csvFile:
                self.writer = csv.DictWriter(csvFile, fieldnames=['Time', 'Current','Voltage', 'Power', 'Current Density'])
                currentExpData = {'Time': elapsed_time, 'Current': current, 'Voltage': voltage,
                                  'Power': power, 'Current Density': currentDensity}
                self.writer.writerow(currentExpData)

            self.keithley.apply_voltage(compliance_current=1.05)
            self.keithley.source_voltage = voltage_P
            self.keithley.measure_current(nplc=NPLC)
            current = -self.keithley.current  # 读取电流
            power_P = voltage_P * current  # 计算功率

            self.keithley.apply_voltage(compliance_current=1.05)
            self.keithley.source_voltage = voltage_N
            self.keithley.measure_current(nplc=NPLC)
            current = -self.keithley.current  # 读取电流
            power_N = voltage_N * current  # 计算功率

            if not self.running:  # 检查运行标志
                break

            if power > power_P:
                if power > power_N:
                    voltage = voltage
                    time_max_values.append(elapsed_time)
                    power_max_values.append(power)
                    self.ptMaxDataLine.setData(time_max_values, power_max_values)
                    QtWidgets.QApplication.processEvents()  # GUI更新

                    stepVolt = stepVolt*stepConvergence
                    if stepVolt*stepConvergence <= 0.01:
                        stepVolt = 0.01
                        check = True
                else:
                    voltage = voltage_N
            else:
                voltage = voltage_P

        if self.running == True:
            if -0.5 <= (startVolt - voltage) <= 0.5 and check == True:
                self.mppIfCheckOut.setText("是")
                self.mppResultVoltageOut.setText(str(round(voltage, 4)) + " V")
                self.mppResultCurrentOut.setText(str(round(current, 4)) + " A")
                self.mppResultPowerOut.setText(str(round(power, 4)) + " W")
            elif check == True:
                self.mppIfCheckOut.setText("否")
                QtWidgets.QMessageBox.information(self, "电压偏离过大", "电压偏离过大")
            elif check == False:
                self.mppIfCheckOut.setText("否")
                QtWidgets.QMessageBox.information(self, "超时", "扫描超时")

        self.keithley.shutdown()

    def StdSweep(self, reverse=False):
        # region 初始化参数，图表，实验数据，计数器
        startVolt = self.basicStartVoltageIn_4.value()  # 初始电压
        endVolt = self.basicEndVoltageIn_4.value()  # 终止电压
        stepVolt = self.basicStepIn_4.value()  # 电压步长
        holdTime = self.basicDurationIn_4.value()  # 每个电压停留时间
        tolerance = self.VarianceIn.value()  # 稳定电流的标准差
        NPLC = self.NPLCIn.value()
        area = self.AreaIn.value()  # 获取面积输入值

        if reverse:
            startVolt, endVolt = endVolt, startVolt
            stepVolt = -stepVolt

        self.Voc_4.setText("  V")
        self.Isc_4.setText("  mA")
        self.Jsc_4.setText("  mA/cm²")
        self.Pmax_4.setText("  mW")
        self.Vmax_4.setText("  V")
        self.Jmax_4.setText("  mA/cm²")
        self.Imax_4.setText("  mA")
        self.FF_4.setText("  %")
        self.PCE_4.setText("  %")
        self.Rs_4.setText("  Ω")
        self.Rsh_4.setText("  Ω")

        current_values = []
        voltage_values = []
        power_values = []
        time_values = []
        currentDensity_values = []
        currentDensity_stable_values = []
        current_stable_values = []
        power_stable_values = []
        voltage_stable_values = []
        time_stable_values = []
        expCount = 0
        tolerance_index = 10**(-3)
        # endregion
        if startVolt != endVolt:
            voltages = np.arange(startVolt, endVolt + stepVolt, stepVolt)
        else:
            voltages = [startVolt]

        self.expProgress(len(voltages), expCount)

        # 初始化csv，进度条
        self.plotInital()
        self.csvInit()
        self.keithley.enable_source()

        measurement_start_time = time.time()
        # 分段电压扫描
        for voltage in voltages:
            if not self.running:  # 检查运行标志
                break

            section_measurement_start_time = time.time()

            count = 0
            first_stable_time = None  # 记录第一次满足稳定性要求的时间
            while ((time.time() - section_measurement_start_time) < holdTime) and self.running:
                elapsed_time = time.time() - measurement_start_time  # 已过去的时间

                self.keithley.apply_voltage(compliance_current=1.05)
                self.keithley.source_voltage = voltage
                self.keithley.measure_current(nplc=NPLC)
                current = -self.keithley.current * 1000  # 转换为mA与一象限
                currentDensity = current / area  # 计算电流密度
                power = voltage * current  # mW
                voltage_values.append(voltage)
                current_values.append(current)
                power_values.append(power)
                time_values.append(elapsed_time)
                currentDensity_values.append(currentDensity)

                # 更新绘图数据
                self.jtDataLine.setData(time_values, currentDensity_values)
                self.itDataLine.setData(time_values, current_values)
                self.ptDataLine.setData(time_values, power_values)
                self.pvDataLine.setData(voltage_values, power_values)
                QtWidgets.QApplication.processEvents()  # GUI更新

                # 更新csv
                with open(self.csvFilePath, 'a', encoding='utf8', newline='') as csvFile:
                    self.writer = csv.DictWriter(csvFile, fieldnames=['Time', 'Current', 'Voltage', 'Power','Current_Density'])
                    currentExpData = {'Time': elapsed_time, 'Current': current, 'Voltage': voltage, 'Power': power, 'Current_Density': currentDensity}
                    self.writer.writerow(currentExpData)

                if not self.running:  # 检查运行标志
                    break

                # 初始化变量

                stable_duration = self.durationTimeIn.value  # 稳定性要求的持续时间
                stable_window = self.duarionWindowIn.value
                is_stable = False

                # 在 while 循环中检测稳定性
                section_elapsed_time = time.time() - section_measurement_start_time

                # 更新经过时间
                elapsed_time = time.time() - measurement_start_time

                if section_elapsed_time < stable_window:
                    count += 1

                if section_elapsed_time >= stable_window:
                    # 获取当前时间，并计算 60 秒前的时间戳
                    if count <= 1:
                        recent_data = [currentDensity]
                    else:
                        time_threshold = elapsed_time - stable_window

                        # 过滤出最近 60 秒内的电流密度数据
                        recent_data = [currentDensity_values[i] for i in range(len(time_values)) if
                                       time_values[i] >= time_threshold]

                    # 计算这些数据的标准差
                    variance = np.std(recent_data)
                    print(variance)

                    if variance <= (tolerance * tolerance_index):
                        if not first_stable_time:
                            # 记录第一次满足稳定性要求的时间
                            first_stable_time = elapsed_time
                            print(f"First stable detected at: {first_stable_time}s")
                        elif elapsed_time - first_stable_time >= stable_duration:
                            # 如果持续满足稳定性 30 秒，计算 30 秒内的数据的平均值
                            stable_data_start_time = elapsed_time - stable_duration
                            stable_data = [currentDensity_values[i] for i in range(len(time_values)) if
                                           time_values[i] >= stable_data_start_time]
                            stable_currents = [current_values[i] for i in range(len(time_values)) if
                                               time_values[i] >= stable_data_start_time]

                            # 计算 30 秒内的平均值
                            currentDensity_mean = np.mean(stable_data)
                            current_mean = np.mean(stable_currents)
                            power_stable = voltage * current_mean

                            # 存储稳定数据
                            current_stable_values.append(current_mean)
                            currentDensity_stable_values.append(currentDensity_mean)
                            power_stable_values.append(power_stable)
                            voltage_stable_values.append(voltage)
                            time_stable_values.append(elapsed_time)

                            print(
                                f"Stable for 30s. Averaged data: Current Density Mean: {currentDensity_mean}, Current Mean: {current_mean}")

                            # 更新绘图数据
                            self.ivDataLine.setData(voltage_stable_values, current_stable_values)
                            self.jvDataLine.setData(voltage_values, currentDensity_values)
                            QtWidgets.QApplication.processEvents()  # GUI更新
                            break

                            # 满足条件，跳出循环，进入下一个电压段
            expCount = expCount + 1  # 更新进度条
            self.expProgress(len(voltages), expCount)
        self.keithley.shutdown()
        self.calculateResults(voltage_values, current_values, area)

    def KSweep(self, reverse=False):
        # region 初始化参数，图表，实验数据，计数器
        startVolt = self.basicStartVoltageIn_5.value()  # 初始电压
        endVolt = self.basicEndVoltageIn_5.value()  # 终止电压
        stepVolt = self.basicStepIn_5.value()  # 电压步长
        holdTime = self.basicDurationIn_5.value()  # 每个电压停留时间
        R_value = self.RIn.value()
        NPLC = self.NPLCIn.value()
        area = self.AreaIn.value()  # 获取面积输入值

        if reverse:
            startVolt, endVolt = endVolt, startVolt
            stepVolt = -stepVolt

        self.Voc.setText("  V")
        self.Isc.setText("  mA")
        self.Jsc.setText("  mA/cm²")
        self.Pmax.setText("  mW")
        self.Vmax.setText("  V")
        self.Jmax.setText("  mA/cm²")
        self.Imax.setText("  mA")
        self.FF.setText("  %")
        self.PCE.setText("  %")
        self.Rs.setText("  Ω")
        self.Rsh.setText("  Ω")

        current_values = []
        voltage_values = []
        power_values = []
        time_values = []
        currentDensity_values = []
        currentDensity_stable_values = []
        current_stable_values = []
        power_stable_values = []
        voltage_stable_values = []
        time_stable_values = []
        expCount = 0
        tolerance_index = 10**(-3)
        # endregion
        if startVolt != endVolt:
            voltages = np.arange(startVolt, endVolt + stepVolt, stepVolt)
        else:
            voltages = [startVolt]

        self.expProgress(len(voltages), expCount)

        # 初始化csv，进度条
        self.plotInital()
        self.csvInit()
        self.keithley.enable_source()

        measurement_start_time = time.time()
        # 分段电压扫描
        for voltage in voltages:
            if not self.running:  # 检查运行标志
                break

            section_measurement_start_time = time.time()

            count = 0

            while ((time.time() - section_measurement_start_time) < holdTime) and self.running:
                elapsed_time = time.time() - measurement_start_time  # 已过去的时间

                self.keithley.apply_voltage(compliance_current=1.05)
                self.keithley.source_voltage = voltage
                self.keithley.measure_current(nplc=NPLC)
                current = -self.keithley.current * 1000  # 转换为mA与一象限
                currentDensity = current / area  # 计算电流密度
                power = voltage * current  # mW
                voltage_values.append(voltage)
                current_values.append(current)
                power_values.append(power)
                time_values.append(elapsed_time)
                currentDensity_values.append(currentDensity)

                # 更新绘图数据
                self.jtDataLine.setData(time_values, currentDensity_values)
                self.itDataLine.setData(time_values, current_values)
                self.ptDataLine.setData(time_values, power_values)
                self.pvDataLine.setData(voltage_values, power_values)
                QtWidgets.QApplication.processEvents()  # GUI更新

                # 更新csv
                with open(self.csvFilePath, 'a', encoding='utf8', newline='') as csvFile:
                    self.writer = csv.DictWriter(csvFile, fieldnames=['Time', 'Current', 'Voltage', 'Power','Current_Density'])
                    currentExpData = {'Time': elapsed_time, 'Current': current, 'Voltage': voltage, 'Power': power, 'Current_Density': currentDensity}
                    self.writer.writerow(currentExpData)

                if not self.running:  # 检查运行标志
                    break

                # 初始化变量
                # 初始化实验开始时间和其他变量
                measurement_start_time = time.time()
                section_measurement_start_time = measurement_start_time
                first_stable_time = None
                stable_duration = 30  # 持续稳定时间的要求
                count = 0
                R_value = 0.01  # 设定的阈值，您可以根据实际需求调整

                # 在 while 循环中检测稳定性
                while self.running:
                    section_elapsed_time = time.time() - section_measurement_start_time

                    # 更新经过时间
                    elapsed_time = time.time() - measurement_start_time

                    if section_elapsed_time < 60:
                        count += 1

                    if section_elapsed_time >= 60:
                        # 获取当前时间，并计算 60 秒前的时间戳
                        if count <= 1:
                            recent_data = [currentDensity]
                            recent_times = [elapsed_time]
                        else:
                            time_threshold = elapsed_time - 60

                            # 过滤出最近 60 秒内的电流密度数据和对应的时间
                            recent_data = [currentDensity_values[i] for i in range(len(time_values)) if
                                           time_values[i] >= time_threshold]
                            recent_times = [time_values[i] for i in range(len(time_values)) if
                                            time_values[i] >= time_threshold]

                        # 使用最小二乘法拟合斜率
                        if len(recent_data) > 1:  # 确保有足够的数据点进行斜率计算
                            slope, intercept = np.polyfit(recent_times, recent_data, 1)  # 拟合一元线性方程
                            slope_abs = abs(slope)

                            # 计算 60 秒内的平均电流密度
                            currentDensity_mean = np.mean(recent_data)

                            # 计算斜率绝对值与平均电流密度的比值
                            stability_metric = slope_abs / currentDensity_mean
                            print(f"Slope/Mean Current Density: {stability_metric}")

                        # 判断是否满足稳定性
                        if stability_metric < R_value:  # 判断斜率绝对值与平均电流密度的比值是否小于阈值
                            if not first_stable_time:
                                # 记录第一次满足稳定性要求的时间
                                first_stable_time = elapsed_time
                                print(f"First stable detected at: {first_stable_time}s")
                            elif elapsed_time - first_stable_time >= stable_duration:
                                # 如果持续满足稳定性 30 秒，记录并处理稳定数据
                                stable_data_start_time = elapsed_time - stable_duration
                                stable_data = [currentDensity_values[i] for i in range(len(time_values)) if
                                               time_values[i] >= stable_data_start_time]
                                stable_currents = [current_values[i] for i in range(len(time_values)) if
                                                   time_values[i] >= stable_data_start_time]

                                # 计算 30 秒内的平均值
                                currentDensity_mean = np.mean(stable_data)
                                current_mean = np.mean(stable_currents)
                                power_stable = voltage * current_mean

                                # 存储稳定数据
                                current_stable_values.append(current_mean)
                                currentDensity_stable_values.append(currentDensity_mean)
                                power_stable_values.append(power_stable)
                                voltage_stable_values.append(voltage)
                                time_stable_values.append(elapsed_time)

                                print(
                                    f"Stable for 30s. Averaged data: Current Density Mean: {currentDensity_mean}, Current Mean: {current_mean}")

                                # 更新绘图数据
                                self.ivDataLine.setData(voltage_stable_values, current_stable_values)
                                self.jvDataLine.setData(voltage_values, currentDensity_values)
                                QtWidgets.QApplication.processEvents()  # GUI更新

                                # 满足条件，跳出循环，进入下一个电压段
                                break
                        else:
                            # 如果未能持续满足稳定性要求，重置第一次稳定时间
                            first_stable_time = None
                            # 满足条件，跳出循环，进入下一个电压段
            expCount = expCount + 1  # 更新进度条
            self.expProgress(len(voltages), expCount)
        self.keithley.shutdown()
        self.calculateResults(voltage_values, current_values, area)

    def csvInit(self):
        currentTime = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
        self.csvFilePath = self.dataSavingPath.currentText() + "/keithley_data" + currentTime + ".csv"
        with open(self.csvFilePath, 'a', encoding='utf8', newline='') as csvFile:
            self.writer = csv.DictWriter(csvFile, fieldnames=['Time', 'Current', 'Voltage', 'Power','Current_Density'])
            self.writer.writeheader()  # 将字段写入csv格式文件首行

    def csvResults(self, voc, isc, jsc, pmax, vmax, jmax, imax, ff, pce, rs, rsh):
        # 获取CSV文件保存路径
        currentTime = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
        results_csv_path = self.dataSavingPath.currentText() + "/results" + currentTime + ".csv"

        with open(results_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Parameter", "Value"])
            writer.writerow(["Voc (V)", voc])
            writer.writerow(["Isc (mA)", isc])
            writer.writerow(["Jsc (mA/cm^2)", jsc])
            writer.writerow(["Pmax (mW)", pmax])
            writer.writerow(["Vmax (V)", vmax])
            writer.writerow(["Jmax (mA/cm^2)", jmax])
            writer.writerow(["Imax (mA)", imax])
            writer.writerow(["FF (%)", ff])
            writer.writerow(["PCE (%)", pce])
            writer.writerow(["Rs", rs])
            writer.writerow(["Rsh", rsh])

    def expProgress(self, range, expCount):
        self.progressBar.setRange(0, range)
        self.progressBar.setValue(expCount)

    def browseDataSavingDir(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "选择文件夹", "./")
        self.dataSavingPath.setItemText(0, directory)

    def findDevice(self):
        try:
            resources = list_resources()
            keithley_addresses = []
            for resource in resources:
                if 'USB' in resource:  # 检查是否为USB设备
                    instrument = Instrument(resource, name='Keithley', timeout=20000)  # 创建一个通用的仪器对象
                    idn_response = instrument.id  # 读取设备的标识串
                    if "KEITHLEY" in idn_response:  # 确认设备类型
                        keithley_addresses.append(resource)
                elif 'GPIB' in resource:  # 检查是否为GPIB设备
                    instrument = Instrument(resource, name='Keithley', timeout=20000)  # 创建一个通用的仪器对象
                    idn_response = instrument.id  # 读取设备的标识串
                    if "KEITHLEY" in idn_response:  # 确认设备类型
                        keithley_addresses.append(resource)

            self.keithleyAddress.clear()
            self.keithleyAddress.addItems(keithley_addresses)
            if len(keithley_addresses) == 0:
                QtWidgets.QMessageBox.information(self, "error", "keithley未连接")
        except Exception as e:
            QtWidgets.QMessageBox.information(self, "error", "keithley连接错误")
            print(e)

    def checkup(self):
        if self.sweepMode.currentText() == "基础电压扫描":
            if self.basicDurationIn.value() == 0:
                QtWidgets.QMessageBox.information(self, "error", "电压停留时间不能为零")
            elif self.AreaIn.value() == 0:
                QtWidgets.QMessageBox.information(self, "error", "电池面积不能为零")
                self.checkupStatus = False
            elif self.dataSavingPath.currentText() == '':
                QtWidgets.QMessageBox.information(self, "error", "数据保存路径不能为空")
                self.checkupStatus = False
            elif self.keithleyAddress.currentText() == '':
                QtWidgets.QMessageBox.information(self, "error", "Keithley地址不能为空")
                self.checkupStatus = False
            elif (self.basicEndVoltageIn.value() - self.basicStartVoltageIn.value()) * self.basicStepIn.value() < 0:
                QtWidgets.QMessageBox.information(self, "error", "步长设置错误")
                self.checkupStatus = False
            elif (not (self.basicStartVoltageIn.value() == self.basicEndVoltageIn.value())) and (
                    self.basicStepIn.value() == 0):
                QtWidgets.QMessageBox.information(self, "error", "步长设置错误")
                self.checkupStatus = False
            elif (self.basicStartVoltageIn.value() == self.basicEndVoltageIn.value()) and (
                    not (self.basicStepIn.value() == 0)):
                QtWidgets.QMessageBox.information(self, "error", "步长设置错误")
                self.checkupStatus = False
        if self.sweepMode.currentText() == "std渐进法":
            if self.basicDurationIn_4.value() == 0:
                QtWidgets.QMessageBox.information(self, "error", "电压停留时间不能为零")
                self.checkupStatus = False
            elif self.AreaIn.value() == 0:
                QtWidgets.QMessageBox.information(self, "error", "电池面积不能为零")
                self.checkupStatus = False
            elif self.dataSavingPath.currentText() == '':
                QtWidgets.QMessageBox.information(self, "error", "数据保存路径不能为空")
                self.checkupStatus = False
            elif self.keithleyAddress.currentText() == '':
                QtWidgets.QMessageBox.information(self, "error", "Keithley地址不能为空")
                self.checkupStatus = False
            elif (self.basicEndVoltageIn_4.value() - self.basicStartVoltageIn_4.value()) * self.basicStepIn_4.value() < 0:
                QtWidgets.QMessageBox.information(self, "error", "步长设置错误")
                self.checkupStatus = False
            elif (self.basicStartVoltageIn_4.value() != self.basicEndVoltageIn_4.value()) and (
                    self.basicStepIn_4.value() == 0):
                QtWidgets.QMessageBox.information(self, "error", "步长设置错误")
                self.checkupStatus = False
            elif (self.basicStartVoltageIn_4.value() == self.basicEndVoltageIn_4.value()) and (
                    self.basicStepIn_4.value() != 0):
                QtWidgets.QMessageBox.information(self, "error", "步长设置错误")
                self.checkupStatus = False
        if self.sweepMode.currentText() == "k渐进法":
            if self.basicDurationIn_5.value() == 0:
                QtWidgets.QMessageBox.information(self, "error", "电压停留时间不能为零")
                self.checkupStatus = False
                self.checkupStatus = False
            elif self.AreaIn.value() == 0:
                QtWidgets.QMessageBox.information(self, "error", "电池面积不能为零")
                self.checkupStatus = False
            elif self.dataSavingPath.currentText() == '':
                QtWidgets.QMessageBox.information(self, "error", "数据保存路径不能为空")
                self.checkupStatus = False
            elif self.keithleyAddress.currentText() == '':
                QtWidgets.QMessageBox.information(self, "error", "Keithley地址不能为空")
                self.checkupStatus = False
            elif (self.basicEndVoltageIn_5.value() - self.basicStartVoltageIn_5.value()) * self.basicStepIn_5.value() < 0:
                QtWidgets.QMessageBox.information(self, "error", "步长设置错误")
                self.checkupStatus = False
            elif (self.basicStartVoltageIn_5.value() != self.basicEndVoltageIn_5.value()) and (
                    self.basicStepIn_5.value() == 0):
                QtWidgets.QMessageBox.information(self, "error", "步长设置错误")
                self.checkupStatus = False
            elif (self.basicStartVoltageIn_5.value() == self.basicEndVoltageIn_5.value()) and (
                    self.basicStepIn_5.value() != 0):
                QtWidgets.QMessageBox.information(self, "error", "步长设置错误")
                self.checkupStatus = False
        if self.sweepMode.currentText() == "MMPT":
            if self.mppDisturbanceIn.value() == 0:
                QtWidgets.QMessageBox.information(self, "error", "扰动电压不能为零")
                self.checkupStatus = False


        if self.checkupStatus == False:
            return

        if os.path.exists(self.dataSavingPath.currentText()) == False:
            QtWidgets.QMessageBox.information(self, "error", "数据保存路径设置错误")
            self.checkupStatus = False
            return
        try:
            self.keithley = Keithley2400(self.keithleyAddress.currentText())
        except Exception as e:
            QtWidgets.QMessageBox.information(self, "error", "keithley设置错误")
            print(e)
            self.checkupStatus = False
            return

    def guiSwitch(self, trigger):
        if not type(trigger) == bool:
            return
        self.runExpButton.setEnabled(trigger)
        self.sweepMode.setEnabled(trigger)
        self.sweepMode.setEnabled(trigger)
        self.keithleyAddress.setEnabled(trigger)
        self.detectButton.setEnabled(trigger)
        self.dataSavingPath.setEnabled(trigger)
        self.browseButton.setEnabled(trigger)
        self.VarianceIn.setEnabled(trigger)
        self.AreaIn.setEnabled(trigger)
        self.NPLCIn.setEnabled(trigger)
        self.saveCurrentPreferencesButton.setEnabled(trigger)
        self.applyReadPreferencesButton.setEnabled(trigger)
        self.RIn.setEnabled(trigger)

    def saveCurrentPreferences(self):
        directory, _ = QtWidgets.QFileDialog.getSaveFileName(self, "文件保存", "/", "CSV Files (*.csv)")

        if not directory:  # 检查用户是否选择了路径
            return

        # 不同模块的参数组
        preferences = {
            "basicStartVoltageIn": self.basicStartVoltageIn.value(),
            "basicEndVoltageIn": self.basicEndVoltageIn.value(),
            "basicStepIn": self.basicStepIn.value(),
            "minimumDurationIn": self.minimumDurationIn.value(),
            "basicDurationIn": self.basicDurationIn.value(),
            "basicStartVoltageIn_4": self.basicStartVoltageIn_4.value(),
            "basicEndVoltageIn_4": self.basicEndVoltageIn_4.value(),
            "basicStepIn_4": self.basicStepIn_4.value(),
            "minimumDurationIn_4": self.minimumDurationIn_4.value(),
            "basicDurationIn_4": self.basicDurationIn_4.value(),
            "basicStartVoltageIn_5": self.basicStartVoltageIn_5.value(),
            "basicEndVoltageIn_5": self.basicEndVoltageIn_5.value(),
            "basicStepIn_5": self.basicStepIn_5.value(),
            "minimumDurationIn_5": self.minimumDurationIn_5.value(),
            "basicDurationIn_5": self.basicDurationIn_5.value(),
            "mppStartVoltageIn": self.mppStartVoltageIn.value(),
            "mppDisturbanceIn": self.mppDisturbanceIn.value(),
            "mppConvergenceIn": self.mppConvergenceIn.value(),
            "mppDurationIn": self.mppDurationIn.value(),
            "NPLCIn": self.NPLCIn.value(),
            "VarianceIn": self.VarianceIn.value(),
            "AreaIn": self.AreaIn.value(),
            "dataSavingPath": self.dataSavingPath.currentText(),
            "keithleyAddress": self.keithleyAddress.currentText()
        }

        # 将字典写入CSV文件
        with open(directory, "w", encoding="utf-8", newline="") as f:
            csv_writer = csv.writer(f)
            for key, value in preferences.items():
                csv_writer.writerow([key, value])

    def applyPreferences(self):
        directory, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件", "/", "CSV Files (*.csv)")

        if not directory:  # 检查用户是否选择了路径
            return

        # 读取CSV文件并将数据应用到界面
        preference = pd.read_csv(directory, header=None, index_col=0, squeeze=True)

        # 应用不同模块的设置
        self.basicStartVoltageIn.setValue(float(preference["basicStartVoltageIn"]))
        self.basicEndVoltageIn.setValue(float(preference["basicEndVoltageIn"]))
        self.basicStepIn.setValue(float(preference["basicStepIn"]))
        self.minimumDurationIn.setValue(float(preference["minimumDurationIn"]))
        self.basicDurationIn.setValue(float(preference["basicDurationIn"]))

        self.basicStartVoltageIn_4.setValue(float(preference["basicStartVoltageIn_4"]))
        self.basicEndVoltageIn_4.setValue(float(preference["basicEndVoltageIn_4"]))
        self.basicStepIn_4.setValue(float(preference["basicStepIn_4"]))
        self.basicDurationIn_4.setValue(float(preference["basicDurationIn_4"]))
        self.minimumDurationIn_4.setValue(float(preference["minimumDurationIn_4"]))

        self.basicStartVoltageIn_5.setValue(float(preference["basicStartVoltageIn_5"]))
        self.basicEndVoltageIn_5.setValue(float(preference["basicEndVoltageIn_5"]))
        self.basicStepIn_5.setValue(float(preference["basicStepIn_5"]))
        self.basicDurationIn_5.setValue(float(preference["basicDurationIn_5"]))
        self.basicDurationIn_5.setValue(float(preference["basicDurationIn_5"]))

        self.mppStartVoltageIn.setValue(float(preference["mppStartVoltageIn"]))
        self.mppDisturbanceIn.setValue(float(preference["mppDisturbanceIn"]))
        self.mppConvergenceIn.setValue(float(preference["mppConvergenceIn"]))
        self.mppDurationIn.setValue(float(preference["mppDurationIn"]))

        self.NPLCIn.setValue(float(preference["NPLCIn"]))
        self.VarianceIn.setValue(float(preference["VarianceIn"]))
        self.AreaIn.setValue(float(preference["AreaIn"]))

        # 清除并设置路径和地址
        self.dataSavingPath.clear()
        self.dataSavingPath.addItem(preference["dataSavingPath"])

        self.keithleyAddress.clear()
        self.keithleyAddress.addItem(preference["keithleyAddress"])

    def calculateResults(self, voltage_values, current_values, area):
        # 将电流转换为电流密度
        J_values = [i / area for i in current_values]

        # 计算Voc
        voc = None
        for i in range(1, len(J_values)):
            if (J_values[i - 1] * J_values[i]) <= 0:
                voc = np.interp(0, [J_values[i - 1], J_values[i]], [voltage_values[i - 1], voltage_values[i]])
                break

        # 计算Jsc和Isc
        jsc = None
        for i in range(1, len(voltage_values)):
            if (voltage_values[i - 1] * voltage_values[i]) <= 0:
                jsc = np.interp(0, [voltage_values[i - 1], voltage_values[i]], [J_values[i - 1], J_values[i]])
                break
        isc = jsc * area if jsc else None

        # 计算Pmax, Vmax, Jmax, Imax
        power_values = [v * i for v, i in zip(voltage_values, current_values)]
        pmax_idx = np.argmax(power_values)
        pmax = power_values[pmax_idx]
        vmax = voltage_values[pmax_idx]
        jmax = J_values[pmax_idx]
        imax = jmax * area

        # 计算FF和PCE
        ff = (pmax / (voc * isc)) * 100  if voc and isc else None
        pce = (pmax / area) if area else None

        # 计算Rs和Rsh
        rs = None
        rsh = None

        # 计算Rs
        if len(voltage_values) > 8:
            # 检查是否存在至少两个小于0的电流值和六个大于0的电流值
            negative_currents = np.where(np.array(J_values) < 0)[0]
            positive_currents = np.where(np.array(J_values) > 0)[0]

            if len(negative_currents) >= 2 and len(positive_currents) >= 6:
                # 计算 Rs
                rs_fit_indices = np.hstack([negative_currents[:2], positive_currents[-6:]])
                rs_fit_voltages = np.array(voltage_values)[rs_fit_indices]
                rs_fit_currents = np.array(J_values)[rs_fit_indices]
                rs_slope, rs_intercept = np.polyfit(rs_fit_voltages, rs_fit_currents, 1)
                rs = -1000 / (rs_slope * area)

                # 计算 Rsh
                voltage_array = np.array(voltage_values)
                current_array = np.array(J_values)

                # 获取小于0的电压和大于0的电压的索引
                negative_voltage_indices = np.where(voltage_array < 0)[0]
                positive_voltage_indices = np.where(voltage_array > 0)[0]

                # 判断条件：小于0的电压数量大于等于2且大于0的电压数量大于等于6
                if len(negative_voltage_indices) >= 2 and len(positive_voltage_indices) >= 6:
                    # 选择最接近0的两个负电压和最接近0的六个正电压
                    closest_negative_indices = negative_voltage_indices[
                        np.argsort(np.abs(voltage_array[negative_voltage_indices]))[:2]]
                    closest_positive_indices = positive_voltage_indices[
                        np.argsort(voltage_array[positive_voltage_indices])[:6]]

                    # 合并索引
                    rsh_fit_indices = np.hstack([closest_negative_indices, closest_positive_indices])
                    rsh_fit_voltages = voltage_array[rsh_fit_indices]
                    rsh_fit_currents = current_array[rsh_fit_indices]

                    # 使用电流和电压进行线性拟合来计算Rsh
                    rsh_slope, rsh_intercept = np.polyfit(rsh_fit_currents, rsh_fit_voltages, 1)
                    rsh = -1000 / (rsh_slope * area)

        self.csvResults(voc, isc, jsc, pmax, vmax, jmax, imax, ff, pce, rs, rsh)
        try:
        # 更新GUI标签
            self.Voc.setText(f"{'%.4f'% voc} V")
            self.Isc.setText(f"{'%.4f'% isc} mA")
            self.Jsc.setText(f"{'%.4f'% jsc} mA/cm²")
            self.Pmax.setText(f"{'%.4f'% pmax} mW")
            self.Vmax.setText(f"{'%.4f'% vmax} V")
            self.Jmax.setText(f"{'%.4f'% jmax} mA/cm²")
            self.Imax.setText(f"{'%.4f'% imax} mA")
            self.FF.setText(f"{'%.4f'% ff} %")
            self.PCE.setText(f"{'%.4f'% pce} %")
            self.Rs.setText(f"{'%.4f'% rs} Ω")
            self.Rsh.setText(f"{'%.4f'% rsh} Ω")
            self.Voc_4.setText(f"{'%.6f' % voc} V")
            self.Isc_4.setText(f"{'%.4f' % isc} mA")
            self.Jsc_4.setText(f"{'%.4f' % jsc} mA/cm²")
            self.Pmax_4.setText(f"{'%.4f' % pmax} mW")
            self.Vmax_4.setText(f"{'%.4f' % vmax} V")
            self.Jmax_4.setText(f"{'%.4f' % jmax} mA/cm²")
            self.Imax_4.setText(f"{'%.4f' % imax} mA")
            self.FF_4.setText(f"{'%.4f' % ff} %")
            self.PCE_4.setText(f"{'%.4f' % pce} %")
            self.Rs_4.setText(f"{'%.4f' % rs} Ω")
            self.Rsh_4.setText(f"{'%.4f' % rsh} Ω")
            self.Voc_5.setText(f"{'%.4f' % voc} V")
            self.Isc_5.setText(f"{'%.4f' % isc} mA")
            self.Jsc_5.setText(f"{'%.4f' % jsc} mA/cm²")
            self.Pmax_5.setText(f"{'%.4f' % pmax} mW")
            self.Vmax_5.setText(f"{'%.4f' % vmax} V")
            self.Jmax_5.setText(f"{'%.4f' % jmax} mA/cm²")
            self.Imax_5.setText(f"{'%.4f' % imax} mA")
            self.FF_5.setText(f"{'%.4f' % ff} %")
            self.PCE_5.setText(f"{'%.4f' % pce} %")
            self.Rs_5.setText(f"{'%.4f' % rs} Ω")
            self.Rsh_5.setText(f"{'%.4f' % rsh} Ω")
            # 保存结果到CSV
        except Exception as e:
            QtWidgets.QMessageBox.information(self, "error", "数据结果输出错误")
            print(e)

    def plotInital(self):
        self.jtDataLine.setData([], [])
        self.jvDataLine.setData([], [])
        self.itDataLine.setData([], [])
        self.ivDataLine.setData([], [])
        self.ptDataLine.setData([], [])
        self.pvDataLine.setData([], [])

def run():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication([])
    keithley_gui = keithleyGUI()
    keithley_gui.show()
    app.exec()


if __name__ == "__main__":
    run()
