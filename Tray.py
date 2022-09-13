"""
用于创建系统托盘
"""
import os

from PyQt5 import QtCore, QtGui, QtWidgets
import win32gui, win32con
import pywintypes

def GetUid():
    if os.path.exists("./Log/uid"):
        return open("./Log/uid", "r", encoding="utf-8").read()
    else:
        open("./Log/uid", "w", encoding="utf-8")
        return False


class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, MainWindow, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.ui = MainWindow
        self.createMenu()

    def createMenu(self):
        self.menu = QtWidgets.QMenu()
        self.OpenGui = QtWidgets.QAction("打开界面", self, triggered=self.show_window)
        self.startWallpaperButton = QtWidgets.QAction("启动壁纸", self, triggered=self.StartWallpaperCommand)
        self.KillWallpaperButton = QtWidgets.QAction("关闭壁纸", self, triggered=self.KillALL)
        self.quitAction = QtWidgets.QAction("退出", self, triggered=self.quit)

        self.menu.addAction(self.OpenGui)
        self.menu.addAction(self.startWallpaperButton)
        self.menu.addAction(self.KillWallpaperButton)
        self.menu.addAction(self.quitAction)
        self.setContextMenu(self.menu)

        # 设置图标
        self.setIcon(QtGui.QIcon(".\image\icon.jpg"))
        self.icon = self.MessageIcon()

        # 把鼠标点击图标的信号和槽连接
        self.activated.connect(self.onIconClicked)

    def KillALL(self):
        try:
            win32gui.PostMessage(GetUid(), win32con.WM_CLOSE, 0, 0)
        except pywintypes.error:
            pass

    def StartWallpaperCommand(self):
        self.ui.StartWallpaper()

    def show_window(self):
        # 若是最小化，则先正常显示窗口，再变为活动窗口（暂时显示在最前面）
        self.ui.showNormal()
        self.ui.activateWindow()

    def quit(self):
        self.setVisible(False)  # 托盘图标会自动消失
        QtWidgets.qApp.quit()

    # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
    def onIconClicked(self, reason):
        if reason == 2 or reason == 3:
            if self.ui.isMinimized() or not self.ui.isVisible():
                # 若是最小化，则先正常显示窗口，再变为活动窗口（暂时显示在最前面）
                self.ui.showNormal()
                self.ui.activateWindow()
                self.ui.setWindowFlags(QtCore.Qt.Window)
                self.ui.show()
            else:
                # 若不是最小化，则最小化
                self.ui.showMinimized()
                self.ui.setWindowFlags(QtCore.Qt.SplashScreen)
                self.ui.show()
                # self.ui.show()