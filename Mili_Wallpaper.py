import sys
import os
import json
from threading import Thread
import time
import random

import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QRectF
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QBitmap
from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QRegion
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import  QColor
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QCursor
from PyQt5.QtGui import  QPainterPath
from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSlider
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QVBoxLayout

import Window_settings
import win32gui
import win32con
import pywintypes
from Tray import TrayIcon
import ProgramLog

LOG = ProgramLog.Logging(".\Log\login.log")

"""ffplay播放视频"""
class StartWallpaper:
    def __init__(self, _file, width, height, volume, _PATH):
        self._file = _file
        self.width = width
        self.height = height
        self.volume = volume
        if _PATH:
            self.StartPathFile()
        else:
            pass

    def StartPathFile(self):
        os.popen(
            f"cd {os.path.split(__file__)[0]}/ && ffplay -x {self.width} -y {self.height} -i {self._file} -volume {self.volume} -loop 0 -threads 16 -noborder -window_title FFPlay：{self._file}"
        )

"""设置窗口句柄缓存"""
def SetUid(UID:int):
    with open("./Log/uid", "w+", encoding="utf-8") as wfp:
        wfp.write(str(UID))

"""获取窗口句柄缓存"""
def GetUid():
    if os.path.exists("./Log/uid"):
        return open("./Log/uid", "r", encoding="utf-8").read()
    else:
        open("./Log/uid", "w", encoding="utf-8")
        return False

"""杀死ffplay窗口"""
def KillAll():
    try:
        win32gui.PostMessage(GetUid(), win32con.WM_CLOSE, 0, 0)
    except pywintypes.error:
        pass

"""ffplay视频播放进程"""
def StartPathVideo(file, width, height, volume, _PATH=True):
    KillAll()
    StartTread = Thread(target=StartWallpaper(
        _file=file,
        width=width,
        height=height,
        volume=volume,
        _PATH=_PATH
    ))
    StartTread.start()
    StartTread.join()
    SleepTime = json.loads(open(".\Log\PlayerSettings.json", "r", encoding="utf-8").read())['SleepTime']
    Window_settings.main(f"FFPlay：{file}", int(SleepTime))
    SetUid(Window_settings._id_)
    LOG.record("正常运行", "启动ffplay视频播放进程")

"""启动壁纸GUI"""
class StartWallpaperGui(QWidget):
    def __init__(self, _file):
        super().__init__()
        LOG.record("正常运行", f"启动壁纸GUI界面 | 文件：{_file}")
        self.file = _file
        self.setWindowTitle("Start Wallpaper|启动壁纸")
        self.setWindowIcon(QIcon(f"./image/icon.jpg"))
        self.resize(960, 540)

        """圆角窗口"""
        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, 10, 10)
        polygon = path.toFillPolygon().toPolygon()
        region = QRegion(polygon)
        self.setMask(region)

        self.cap = cv2.VideoCapture(_file) # cv2读取视频

        QLabel(f"文件名：{os.path.split(_file)[-1]}", self).setGeometry(int((960 - 500) / 2), 400, 500, 40)

        self.Bg = QLabel("", self)
        self.Bg.setGeometry(0, 0, 960, 540)
        self.Bg.setStyleSheet(f"background-color: lavenderblush")

        VLayout = QVBoxLayout(self)

        # Video MSEC 视频当前秒
        self.VideoMSEC = QLabel(f"视频当前进度(秒)：{self.cap.get(0)}", self)
        VLayout.addWidget(self.VideoMSEC)

        # Video Width 视频宽度
        VideoWidth = QLabel(f"视频宽度：{self.cap.get(3)}", self)
        VLayout.addWidget(VideoWidth)

        # Video Height 视频高度
        VideoHeight = QLabel(f"视频高度：{self.cap.get(4)}", self)
        VLayout.addWidget(VideoHeight)

        # Video FPS 视频针
        VideoFPS = QLabel(f"FPS：{self.cap.get(5)}", self)
        VLayout.addWidget(VideoFPS)

        # FOURCC
        VideoFOURCC = QLabel(f"Video FOURCC：{self.cap.get(6)}", self)
        VLayout.addWidget(VideoFOURCC)

        # FRAME_COUNT 视频文件帧数
        VideoFRAME_COUNT = QLabel(f"视频文件帧数：{self.cap.get(7)}", self)
        VLayout.addWidget(VideoFRAME_COUNT)

        # FORMAT
        VideoFORMAT = QLabel(f"Video FORMAT：{self.cap.get(8)}", self)
        VLayout.addWidget(VideoFORMAT)

        # MODE
        VideoMODE = QLabel(f"Video MODE：{self.cap.get(9)}", self)
        VLayout.addWidget(VideoMODE)

        # BRIGHTNESS 亮度
        VideoBRIGHTNESS = QLabel(f"亮度|BRIGHTNESS：{self.cap.get(10)}", self)
        VLayout.addWidget(VideoBRIGHTNESS)

        # CONTRAST 对比度
        VideoCONTRAST = QLabel(f"对比度|CONTRAST：{self.cap.get(11)}", self)
        VLayout.addWidget(VideoCONTRAST)

        self.setLayout(VLayout)

        self.timer_camera = QTimer()
        self.PlayLabel = QLabel(self)
        self.PlayLabel.setStyleSheet("background-color: black;border-radius: 10px; border: 2px groove gray;border-style: outset; color:white")
        self.PlayLabel.setGeometry(int((960 - 480) / 2), 0, 480, 270)
        self.Paly()

        VolumeTitleLabel = QLabel("音量：", self)
        VolumeTitleLabel.setStyleSheet("background-color: black;border-radius: 2px; border: 2px groove gray;border-style: outset; color:white")
        VolumeTitleLabel.setGeometry(250, 300, 40, 40)

        self.volume = QSlider(Qt.Horizontal, self)
        self.volume.setMinimum(0)
        self.volume.setMaximum(100)
        self.volume.setValue(50)
        self.volume.setTickInterval(5)
        self.volume.setTickPosition(QSlider.TicksBelow)
        self.volume.setGeometry(300, 300, 300, 40)
        self.volume.valueChanged.connect(self.VolumeValue)

        self.volumeValueLabel = QLabel(str(self.volume.value()), self)
        self.volumeValueLabel.setStyleSheet('color:blue')
        self.volumeValueLabel.setGeometry(620, 300, 40, 40)

        self.Button_Yes = QPushButton("确定", self)
        self.Button_Yes.setStyleSheet('background-color: blue;border-radius: 10px; border: 2px groove gray;border-style: outset; color:white')
        self.Button_Yes.setGeometry(680, 300, 40, 40)
        self.Button_Yes.clicked.connect(self.Start)

        self.QuitButton = QPushButton("", self)
        self.QuitButton.setMask(QBitmap("/image/Quits.png"))
        self.QuitButton.setIcon(QIcon("./image/Quits.png"))
        self.QuitButton.setIconSize(QSize(40, 40))
        self.QuitButton.setGeometry(900, 10, 40, 40)
        self.QuitButton.clicked.connect(self.hide)

    def VolumeValue(self):
        self.volumeValueLabel.setText(str(self.volume.value()))
        LOG.record("正常运行", f"设置音量 | {self.volume.value()}")

    """启动进程"""
    def Start(self):
        desktop = QApplication.desktop()
        StartPathVideo(
            self.file,
            width=desktop.width(),
            height=desktop.height(),
            volume=self.volume.value()
        )
        self.timer_camera.stop()
        self.hide()

    """定时任务"""
    def Paly(self):
        self.timer_camera.start(int(self.cap.get(5)))
        self.timer_camera.timeout.connect(self.OpenFrame)

    def OpenFrame(self):
        global vedio_img
        ret, image = self.cap.read()
        if ret:
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                vedio_img = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
            elif len(image.shape) == 1:
                vedio_img = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_Indexed8)
            else:
                vedio_img = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)

            self.VideoMSEC.setText(f"视频当前进度(秒)：{int(self.cap.get(0))}")
            self.PlayLabel.setPixmap(QPixmap(vedio_img))
            self.PlayLabel.setScaledContents(True)  # 自适应窗口
        else:
            self.cap.release()
            self.cap = cv2.VideoCapture(self.file)
            # self.timer_camera.stop()

"""主窗口"""
class Mili_Wallpaper(QWidget):
    def __init__(self):
        super().__init__()
        LOG.record("正常运行", "主界面启动")
        self.DIR = os.path.split(__file__)[0]
        self._file = False
        self.anim = None
        self.main()

    """UI"""
    def main(self):
        self.setWindowTitle("Mili Wallpaper")
        self.setWindowIcon(QIcon(f"{self.DIR}/image/icon.jpg"))
        self.setMinimumSize(960, 540)
        self.setMaximumSize(False, False)
        Center = QDesktopWidget().frameGeometry().center()
        self.move(int(960 - Center.x() / 2), int(540 - Center.y() / 2))

        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, 10, 10)
        polygon = path.toFillPolygon().toPolygon()
        region = QRegion(polygon)
        self.setMask(region)

        self.QuitButton = QPushButton("", self)
        self.QuitButton.setGeometry(900, 10, 40, 40)
        self.QuitButton.setMask(QBitmap("./image/Quits.png"))
        self.QuitButton.setIcon(QIcon("./image/Quits.png"))
        self.QuitButton.setIconSize(QSize(40, 40))
        self.QuitButton.setStyleSheet("background-color: red;")
        self.QuitButton.clicked.connect(self.KillWindow)

        self.TrayButton = QPushButton("", self)
        self.TrayButton.setGeometry(850, 10, 40, 40)
        self.TrayButton.setMask(QBitmap("./image/_.png"))
        self.TrayButton.setIcon(QIcon("./image/_.png"))
        self.TrayButton.setIconSize(QSize(40, 40))
        self.TrayButton.clicked.connect(self._Tray)

        self.StartWallpaperButton =  QPushButton("", self)
        self.StartWallpaperButton.setGeometry(10, 500, 60, 40)
        self.StartWallpaperButton.setMask(QBitmap("./image/StartWallpaper.png"))
        self.StartWallpaperButton.setIcon(QIcon("./image/StartWallpaper.png"))
        self.StartWallpaperButton.setIconSize(QSize(60, 40))
        self.StartWallpaperButton.setStyleSheet("background-color: blue; color: red;")
        self.StartWallpaperButton.clicked.connect(self.StartWallpaper)

        self.SelfFileButton = QPushButton("", self)
        self.SelfFileButton.setGeometry(80, 500, 60, 40)
        self.SelfFileButton.setMask(QBitmap("./image/SelfFile.png"))
        self.SelfFileButton.setIcon(QIcon("./image/SelfFile.png"))
        self.SelfFileButton.setIconSize(QSize(60, 40))
        self.SelfFileButton.clicked.connect(self.SelectFile)

        self.KillWallpaperButton  = QPushButton("", self)
        self.KillWallpaperButton.setGeometry(150, 500, 60, 40)
        self.KillWallpaperButton.setMask(QBitmap("./image/KillWallpaper.png"))
        self.KillWallpaperButton.setIcon(QIcon("./image/KillWallpaper.png"))
        self.KillWallpaperButton.setIconSize(QSize(60, 40))
        self.KillWallpaperButton.clicked.connect(KillAll)

    """关闭所有窗口"""
    def KillWindow(self):
        self.StartWallpaperGui.close()
        self.close()
        LOG.record("正常运行", "关闭所有窗口，程序退出")

    """托盘"""
    def _Tray(self):
        self.tray = TrayIcon(self)
        self.tray.show()
        self.hide()
        LOG.record("正常运行", "启动系统托盘")

    """选择文件"""
    def SelectFile(self):
        LOG.record("正常运行", "选择视频文件")
        fileName,fileType = QFileDialog.getOpenFileName(self, "选取文件夹", "C:/")
        if os.path.isfile(fileName):
            # print(fileName, fileType)
            self._file = fileName
            LOG.record("正常运行", f"选择成功 | {fileName}___{fileType}")
            return fileName
        else:
            return False

    """启动壁纸"""
    def StartWallpaper(self):
        if self._file:
            self.StartWallpaperGui = StartWallpaperGui(self._file)
            self.StartWallpaperGui.show()
        else:
            LOG.record("正常运行", "未识别到视频，启动选择视频界面")
            if self.SelectFile():
                self.StartWallpaper()
            else:
                pass

    """退出程序动画，渐渐透明"""
    def closeEvent(self, event):
        if self.anim == None:
            self.anim = QPropertyAnimation(self, b"windowOpacity")  # 设置动画对象
            self.anim.setDuration(1000)  # 设置动画时长
            self.anim.setStartValue(1)  # 设置初始属性，1.0为不透明
            self.anim.setEndValue(0)  # 设置结束属性，0为完全透明
            self.anim.finished.connect(self.close)  # 动画结束时，关闭窗口
            self.anim.start()  # 开始动画
            event.ignore()  # 忽略事件

    """重写移动事假，更改鼠标图标"""
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    Window = Mili_Wallpaper()
    # 设置背景图片
    palette1 = QPalette()
    palette1.setBrush(Window.backgroundRole(), QBrush(QPixmap('./image/bg.png')))
    Window.setPalette(palette1)
    Window.setAutoFillBackground(True)
    Window.show()
    app.exec_()
