#!/usr/bin/env python3
# V 0.9.8

import sys
from PyQt6.QtWidgets import (QMainWindow,QFormLayout,QStyleFactory,QWidget,QTextEdit,QFileDialog,QSizePolicy,QFrame,QBoxLayout,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QApplication,QDialog,QMessageBox,QLineEdit,QSpinBox,QComboBox,QCheckBox,QMenu,QStatusBar,QTabWidget) 
from PyQt6.QtCore import (Qt,pyqtSignal,QCoreApplication,QObject,pyqtSlot,QFile,QIODevice,QPoint,QMimeDatabase,QFileSystemWatcher)
from PyQt6.QtGui import (QAction,QColor,QFont,QIcon,QPalette,QPainter)
from PyQt6.Qsci import (QsciLexerCustom,QsciScintilla,QsciLexerPython,QsciLexerBash,QsciLexerJavaScript)
from PyQt6 import QtPrintSupport
import os
import re
import json
from cfgpyeditor import *

WINW = 600
WINH = 300

# home dir
MY_HOME = os.path.expanduser('~')
# this program working directory
main_dir = os.getcwd()
#
ICON_PATH = os.path.join(main_dir,"icons")

_base_config = {"singleinstance":1, "fontfamily":"Monospace", "fontsize":10, "autoclose":1, "autocomplch":3, "usetab":1, "tabwidth":4, "dark":1, "printfont":"Monospace", "printfontsize":10, "reloaddoc":1}

_config_file = os.path.join(main_dir, "config.json")
if not os.path.exists(_config_file):
    try:
        _ff = open(_config_file, "w")
        json.dump(_base_config, _ff, indent = 4)
        _ff.close()
    except:
        sys.exit(0)

my_config = None
try:
    _ff = open(_config_file, "r")
    my_config = json.load(_ff)
    _ff.close()
except:
    sys.exit()

# single instance mode
SINGLEINSTANCE=my_config["singleinstance"]
# font famity to use for the editor
FONTFAMILY=my_config["fontfamily"]
# font size for the editor
FONTSIZE=my_config["fontsize"]
# 0: no - 1: close automatically: " ' ( [ { - 2: close also: ¡ ¿
AUTOCLOSE=my_config["autoclose"]
# amount of characters to show a list for autocompletation
AUTOCOMPLETITION_CHARS=my_config["autocomplch"]
# indentation using tab (instead of spaces): False or True
USETAB=my_config["usetab"]
# the width of the indentation - minimun 2
TABWIDTH=my_config["tabwidth"]
# use dark theme for the editor: 0 no - 1 yes - 2 yes and buttons and tabwidget (workaround)
DARKTHEME=my_config["dark"]
# for printing
PRINT_FONT=my_config["printfont"]
PRINT_FONT_SIZE=my_config["printfontsize"]
# for reloading the files previously loaded but not closed by the user
USE_RELOAD_DOC=my_config["reloaddoc"]

PROG_REGISTERED = 0
if "-a" in sys.argv:
    SINGLEINSTANCE = 0

if SINGLEINSTANCE:
    from PyQt6.QtDBus import QDBusConnection, QDBusInterface, QDBusReply
    if not QDBusConnection.sessionBus().registerService('org.QtDBus.pyeditor6'):
        SINGLEINSTANCE = 0
        PROG_REGISTERED = 1
   

class confWin(QDialog):
    def __init__(self, parent=None):
        super(confWin, self).__init__(None)
        self.setWindowTitle("Configurator")
        self.setGeometry(0,0,300,100)
        self.window = parent
        self.setWindowModality(Qt.WindowModality.WindowModal)
        #
        self.vbox = QVBoxLayout()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # 
        self.vbox.setContentsMargins(2,2,2,2)
        self.setLayout(self.vbox)
        #
        self.tab_w = QTabWidget()
        self.tab_w.setContentsMargins(0,0,0,0)
        self.tab_w.setMovable(False)
        self.tab_w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # self.tab_w.setWidgetResizable(True)
        self.vbox.addWidget(self.tab_w, stretch = 10)
        ######
        ### panel tab
        p_widget = QWidget()
        self.tab_w.insertTab(0, p_widget, "Settings")
        p_box = QVBoxLayout()
        p_box.setContentsMargins(0,0,0,0)
        p_widget.setLayout(p_box)
        #
        pform = QFormLayout()
        p_box.addLayout(pform)
        #
        self.font_family = QLineEdit()
        self.font_family.setText(FONTFAMILY)
        pform.addRow("Font name - editor ", self.font_family)
        #
        self.font_size = QSpinBox()
        self.font_size.setMaximum(100)
        self.font_size.setValue(FONTSIZE)
        pform.addRow("Font size - editor ", self.font_size)
        #
        self.autoclose = QComboBox()
        self.autoclose.setToolTip("Close some symbols automatically")
        self.autoclose.setEditable(False)
        self.autoclose.addItems(["No","Yes"])
        self.autoclose.setCurrentIndex(AUTOCLOSE)
        pform.addRow("Autoclose ", self.autoclose)
        #
        self.autocompletition = QSpinBox()
        self.autocompletition.setToolTip("Amount of characters that trigger the word autocompletition")
        self.autocompletition.setMaximum(10)
        self.autocompletition.setValue(AUTOCOMPLETITION_CHARS)
        pform.addRow("Autocompletition ", self.autocompletition)
        #
        self.usetab = QComboBox()
        self.usetab.setToolTip("Use tab or spaces")
        self.usetab.setEditable(False)
        self.usetab.addItems(["No","Yes"])
        self.usetab.setCurrentIndex(USETAB)
        pform.addRow("Use tab ", self.usetab)
        #
        self.tabwidth = QComboBox()
        self.tabwidth.setToolTip("Amount of characters for the tab")
        self.tabwidth.setEditable(False)
        self.tabwidth.addItems(["2","3","4","5","6","7","8"])
        self.tabwidth.setCurrentIndex(TABWIDTH)
        pform.addRow("Tab width ", self.tabwidth)
        #
        self.darktheme = QComboBox()
        self.darktheme.setToolTip("Use the dark theme or the default")
        self.darktheme.setEditable(False)
        self.darktheme.addItems(["Default","Dark"])
        self.darktheme.setCurrentIndex(DARKTHEME)
        pform.addRow("Editor theme ", self.darktheme)
        #
        self.print_font_family = QLineEdit()
        self.print_font_family.setText(PRINT_FONT)
        pform.addRow("Font name - printer ", self.print_font_family)
        #
        self.print_font_size = QSpinBox()
        self.print_font_size.setMaximum(100)
        self.print_font_size.setValue(PRINT_FONT_SIZE)
        pform.addRow("Font size - printer ", self.print_font_size)
        #
        self.single_app = QComboBox()
        self.single_app.setToolTip("Single application mode")
        self.single_app.setEditable(False)
        self.single_app.addItems(["No","Yes"])
        self.single_app.setCurrentIndex(SINGLEINSTANCE)
        pform.addRow("Single application ", self.single_app)
        #
        self.reload_doc = QComboBox()
        self.reload_doc.setToolTip("Reload the files not closed")
        self.reload_doc.setEditable(False)
        self.reload_doc.addItems(["No","Yes"])
        self.reload_doc.setCurrentIndex(USE_RELOAD_DOC)
        pform.addRow("Reload the files at start ", self.reload_doc)
        #
        box_btn = QHBoxLayout()
        self.vbox.addLayout(box_btn)
        btn_accept = QPushButton("Accept")
        btn_accept.clicked.connect(self.on_accept)
        box_btn.addWidget(btn_accept)
        btn_cancel = QPushButton("Cancel")
        box_btn.addWidget(btn_cancel)
        btn_cancel.clicked.connect(self.close)
        #
        self.exec()
        self.adjustSize()
        self.updateGeometry()
        
    def on_accept(self):
        global FONTFAMILY
        global FONTSIZE
        global AUTOCLOSE
        global AUTOCOMPLETITION_CHARS
        global USETAB
        global TABWIDTH
        global DARKTHEME
        global PRINT_FONT
        global PRINT_FONT_SIZE
        global SINGLEINSTANCE
        global USE_RELOAD_DOC
        global my_config
        try:
            FONTFAMILY = self.font_family.text()
            my_config["fontfamily"] = FONTFAMILY
            #
            FONTSIZE = self.font_size.value()
            my_config["fontsize"] = FONTSIZE
            #
            AUTOCLOSE = self.autoclose.currentIndex()
            my_config["autoclose"] = AUTOCLOSE
            #
            AUTOCOMPLETITION_CHARS = self.autocompletition.value()
            my_config["autocomplch"] = AUTOCOMPLETITION_CHARS
            #
            USETAB = self.usetab.currentIndex()
            my_config["usetab"] = USETAB
            #
            TABWIDTH = self.tabwidth.currentIndex()
            my_config["tabwidth"] = TABWIDTH
            #
            DARKTHEME = self.darktheme.currentIndex()
            my_config["dark"] = DARKTHEME
            #
            PRINT_FONT = self.print_font_family.text()
            my_config["printfont"] = PRINT_FONT
            #
            PRINT_FONT_SIZE = self.print_font_size.value()
            my_config["printfontsize"] = PRINT_FONT_SIZE
            #
            SINGLEINSTANCE = self.single_app.currentIndex()
            my_config["singleinstance"] = SINGLEINSTANCE
            #
            USE_RELOAD_DOC = self.reload_doc.currentIndex()
            my_config["reloaddoc"] = USE_RELOAD_DOC
            #
            # write the configuration back
            _ff = open(_config_file,"w")
            json.dump(my_config, _ff, indent = 4)
            _ff.close()
        except Exception as E:
            MyDialog("Error", str(E), self)
        self.close()
        
        
class firstMessage(QWidget):
    def __init__(self, *args):
        super().__init__()
        title = args[0]
        message = args[1]
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("icons/program.svg"))
        box = QBoxLayout(QBoxLayout.TopToBottom)
        box.setContentsMargins(5,5,5,5)
        self.setLayout(box)
        label = QLabel(message)
        box.addWidget(label)
        button = QPushButton("Close")
        box.addWidget(button)
        button.clicked.connect(self.close)
        self.show()
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
WINM = "False"
if not os.path.exists("pyeditor.cfg"):
    try:
        with open("pyeditor.cfg", "w") as ifile:
            ifile.write("{};{};False".format(WINW, WINH))
    except:
        app = QApplication(sys.argv)
        fm = firstMessage("Error", "The file pyeditor.cfg cannot be created.")
        sys.exit(app.exec())

if not os.access("pyeditor.cfg", os.R_OK):
    app = QApplication(sys.argv)
    fm = firstMessage("Error", "The file pyeditor.cfg cannot be read.")
    sys.exit(app.exec())

try:
    with open("pyeditor.cfg", "r") as ifile:
        fcontent = ifile.readline()
    aw, ah, am = fcontent.split(";")
    WINW = aw
    WINH = ah
    WINM = am.strip()
except:
    app = QApplication(sys.argv)
    fm = firstMessage("Error", "The file pyeditor.cfg cannot be read.\nRebuilded.")
    try:
        with open("pyeditor.cfg", "w") as ifile:
            ifile.write("{};{};False".format(WINW, WINH))
    except:
        pass
    sys.exit(app.exec())
#######################

class textLexer(QsciLexerCustom):
    def __init__(self, __myFont, parent):
        super(textLexer, self).__init__(parent)
        self.__myFont = __myFont
        # Default text settings
        self.setDefaultColor(QColor("#000000ff"))
        self.setDefaultPaper(QColor("#ffffffff"))
        self.setDefaultFont(self.__myFont)
        # Initialize fonts per style
        self.setFont(self.__myFont, 0)
        # Initialize colors per style
        self.setColor(QColor("#000000ff"), 0)   # Style 0: black
        # Initialize paper colors per style
        self.setPaper(QColor("#ffffffff"), 0)   # Style 0: white
    
    def language(self):
        return "TextStyle"
    
    def description(self, style):
        if style == 0:
            return "textStyle"
    
    def styleText(self, start, end):
        self.startStyling(start)
        self.setStyling(end - start, 0)
    
    
class MyQsciScintilla(QsciScintilla):
    keyPressed = pyqtSignal(str)
    def __init__(self):
        super(MyQsciScintilla, self).__init__()
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 1)
        # indicators
        self.indicatorDefine(QsciScintilla.IndicatorStyle.FullBoxIndicator,0, )
        self.setIndicatorForegroundColor(QColor(SELECTIONBACKGROUNDCOLOR), 0)
        self.setIndicatorHoverStyle(QsciScintilla.IndicatorStyle.FullBoxIndicator, 0)
        self.setIndicatorDrawUnder(True, 0)
        self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, 0)
        self.SendScintilla(QsciScintilla.SCI_SETINDICATORVALUE, 0, 0xffff)
        
        
    def contextMenuEvent(self, e):
        menu = self.createStandardContextMenu()
        if not self.isReadOnly():
            menu.addSeparator()
            #
            customAction1 = QAction("Uppercase")
            customAction1.triggered.connect(self.on_customAction1)
            menu.addAction(customAction1)
            #
            customAction2 = QAction("Lowercase")
            customAction2.triggered.connect(self.on_customAction2)
            menu.addAction(customAction2)
            #
            customAction3 = QAction("Swapcase")
            customAction3.triggered.connect(self.on_customAction3)
            menu.addAction(customAction3)
            # 
            menu.addSeparator()
            #
            customAction4 = QAction("Eol view/hide")
            customAction4.triggered.connect(self.on_customAction4)
            menu.addAction(customAction4)
            #
            customAction5 = QAction("Wordwrap")
            customAction5.triggered.connect(self.on_customAction5)
            menu.addAction(customAction5)
        #
        menu.exec(e.globalPos()+QPoint(5,5))
        
    def on_customAction1(self):
        if not self.hasSelectedText():
            return
        #
        self.replaceSelectedText(self.selectedText().upper())
        
    def on_customAction2(self):
        if not self.hasSelectedText():
            return
        #
        self.replaceSelectedText(self.selectedText().lower())
        
    def on_customAction3(self):
        if not self.hasSelectedText():
            return
        #
        self.replaceSelectedText(self.selectedText().swapcase())
        
    def on_customAction4(self):
        self.setEolVisibility(not self.eolVisibility())
    
    def on_customAction5(self):
        if self.wrapMode():
            self.setWrapMode(QsciScintilla.WrapMode.WrapNone)
        else:
            self.setWrapMode(QsciScintilla.WrapMode.WrapWord)
    
    def keyPressEvent(self, e):
        QsciScintilla.keyPressEvent(self, e)
        self.keyPressed.emit(e.text())
    
    def mousePressEvent(self, e):
        QsciScintilla.mousePressEvent(self, e)
        self.keyPressed.emit(None)
        

class CustomMainWindow(QMainWindow):
    
    def __init__(self):
        super(CustomMainWindow, self).__init__()
        self.setContentsMargins(0,0,0,0)
        self.setWindowIcon(QIcon("icons/program.svg"))
        self.resize(int(WINW), int(WINH))
        self.setWindowTitle("pyeditor6")
        #
        if SINGLEINSTANCE:
            # return True on success
            QDBusConnection.sessionBus().registerObject('/', self, QDBusConnection.RegisterOption.ExportAllSlots)
        else:
            try:
                # for registering a new interface if the previous one has been removed
                import dbus
                from dbus.mainloop.pyqt6 import DBusQtMainLoop
                mainloop = DBusQtMainLoop(set_as_default=True)
                bus = dbus.SessionBus()
                dbus.set_default_main_loop(mainloop)
                bus.add_signal_receiver(self.interfaces_removed,
                                    signal_name=None,
                                    dbus_interface=None,
                                    bus_name=None, 
                                    path=None)
            except:
                pass
        #
        # Create frame and layout
        # ---------------------------
        #
        self.__frm = QFrame(self)
        self.__frm.setContentsMargins(0,0,0,0)
        # self.__frm.setStyleSheet("QWidget { background-color: #ffeaeaea }")
        self.__lyt = QVBoxLayout()
        self.__lyt.setContentsMargins(2,2,2,2)
        self.__frm.setLayout(self.__lyt)
        self.setCentralWidget(self.__frm)
        # ------------------
        self.btn_box0 = QHBoxLayout()
        self.__lyt.addLayout(self.btn_box0)
        #
        self.btn_h = QPushButton("History")
        self.btn_h.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.btn_box0.addWidget(self.btn_h, alignment=Qt.AlignmentFlag.AlignLeft)
        self.btn_h_menu = QMenu()
        self.btn_h.setMenu(self.btn_h_menu)
        self.btn_h_menu.triggered.connect(self.on_h_menu)
        #
        self.btn_new = QPushButton()
        self.btn_new.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.DocumentNew, QIcon(os.path.join(ICON_PATH, "document-new.png"))))
        self.btn_new.setToolTip("New document")
        self.btn_new.clicked.connect(self.on_new)
        self.btn_box0.addWidget(self.btn_new, stretch=1)
        #
        self.btn_open = QPushButton()
        self.btn_open.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.DocumentOpen, QIcon(os.path.join(ICON_PATH, "document-open.png"))))
        self.btn_open.setToolTip("Open a new document")
        self.btn_open.clicked.connect(self.on_open)
        self.btn_box0.addWidget(self.btn_open, stretch=1)
        # # disabled: the ancestor document is been marked as modified wrongly
        # self.btn_clone = QPushButton()
        # self.btn_clone.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.DocumentNew, QIcon(os.path.join(ICON_PATH, "document-new.png"))))
        # self.btn_clone.setToolTip("Clone the current document")
        # self.btn_clone.clicked.connect(self.on_clone)
        # self.btn_box0.addWidget(self.btn_clone, stretch=1)
        #
        self.btn_box0.addStretch(20)
        #
        self.config_btn = QPushButton()
        self.config_btn.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.DocumentProperties, QIcon(os.path.join(ICON_PATH, "configurator.png"))))
        self.config_btn.setToolTip("Settings")
        self.config_btn.clicked.connect(self.config_btn_action)
        self.btn_box0.addWidget(self.config_btn, stretch=1)
        #
        self.__btn = QPushButton()
        self.__btn.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.WindowClose, QIcon(os.path.join(ICON_PATH, "application-exit.png"))))
        self.__btn.setToolTip("Exit")
        self.__btn.clicked.connect(self.__btn_action)
        self.btn_box0.addWidget(self.__btn, stretch=1)
        # the history of opened files
        self.pageNameHistory = []
        try:
            if not os.path.exists("pyeditorh.txt"):
                ff = open("pyeditorh.txt", "w")
                ff.close()
            #
            with open("pyeditorh.txt", "r") as ff:
                self.pageNameHistory = ff.readlines()
        except Exception as E:
            MyDialog("Error", str(E)+"\nExiting...", self)
            self.close()
            sys.exit()
        #
        self.pageName = ""
        afilename = ""
            
        # if len(sys.argv) > 1:
            # for el in sys.argv[1:]:
                # if el not in ["-p", "-b", "-j", "-t", "-a"]:
                    # afilename = el
                    # break
        #
        # if afilename:
            # afilename = os.path.realpath(afilename)
        #
        if len(sys.argv) > 1:
            if sys.argv[1] in ["-p", "-b", "-j", "-t"]:
                if len(sys.argv) > 2:
                    afilename = os.path.realpath(sys.argv[2])
            else:
                afilename = os.path.realpath(sys.argv[1])
        #
        if not os.path.exists(afilename):
            MyDialog("Info", "The file\n{}\ndoes not exist.".format(afilename), self)
            afilename = ""
            sys.exit()
        if not os.access(afilename, os.R_OK):
            MyDialog("Info", "The file\n{}\nis not readable.".format(afilename), self)
            afilename = ""
            sys.exit()
        # for el in self.pageNameHistory[::-1]:
        for el in self.pageNameHistory:
            if el.rstrip("\n") == self.pageName:
                continue
            self.btn_h_menu.addAction(el.rstrip("\n"))
        #
        # if self.pageName:
        if afilename:
            # populate the menu - opened doc at last position
            # save into the list once
            if afilename+"\n" in self.pageNameHistory:
                self.pageNameHistory.remove(afilename+"\n")
            else:
                self.btn_h_menu.addAction(afilename)
            self.pageNameHistory.append(afilename+"\n")
        #########
        ### tabwidget
        self.frmtab = QTabWidget()
        self.frmtab_tab_text_color = self.frmtab.tabBar().tabTextColor(0)
        self.frmtab.setContentsMargins(0,0,0,0)
        self.__lyt.addWidget(self.frmtab)
        self.frmtab.setTabPosition(QTabWidget.TabPosition.East)
        self.frmtab.setTabBarAutoHide(False)
        # self.frmtab.setTabsClosable(True)
        self.frmtab.setMovable(True)
        # self.frmtab.tabCloseRequested.connect(self.on_tab_close)
        self.frmtab.currentChanged.connect(self.on_tab_changed)
        # the current editor
        self.current_editor = None
        # set the default editor style from command line
        self.isargument = 0
        use_mimetype = 1
        if len(sys.argv) > 1:
            # if sys.argv[1] == "-p":
            if "-p" in sys.argv:
                self.isargument = 1
                use_mimetype = 0
            # elif sys.argv[1] == "-b":
            elif "-b" in sys.argv:
                self.isargument = 2
                use_mimetype = 0
            # elif sys.argv[1] == "-j":
            elif "-j" in sys.argv:
                self.isargument = 3
                use_mimetype = 0
            # elif sys.argv[1] == "-t":
            elif "-t" in sys.argv:
                self.isargument = 4
                use_mimetype = 0
        # or from config file
        if self.isargument == 0:
            if EDITORTYPE == "python":
                self.isargument = 1
                use_mimetype = 0
            elif EDITORTYPE == "bash":
                self.isargument = 2
                use_mimetype = 0
            elif EDITORTYPE == "javascript":
                self.isargument = 3
                use_mimetype = 0
            elif EDITORTYPE == "text":
                self.isargument = 4
                use_mimetype = 0
            elif EDITORTYPE == "":
                use_mimetype = 1
        # check from the mimetype of the file
        if use_mimetype:
            if afilename:
                self.isargument = self.set_mimetype(afilename)
            else:
                self.isargument = 4
        #
        _i = 0
        if USE_RELOAD_DOC:
            # reopen the files from the previous session
            _previous_files = []
            try:
                _f = open(os.path.join(main_dir, "file_opened"), "r")
                _previous_files = _f.readlines()
                _f.close()
            except:
                pass
            #
            try:
                os.remove(os.path.join(main_dir, "file_opened"))
            except Exception as E:
                MyDialog("Error", str(E), self)
            #
            if len(_previous_files) > 0:
                for _file in _previous_files:
                    _filename = _file.strip("\n")
                    if _filename == "":
                        continue
                    if os.path.exists(_filename) and os.access(_filename, os.R_OK):
                        pop_tab = ftab(_filename, self.isargument, self)
                        self.frmtab.addTab(pop_tab, os.path.basename(_filename))
                        self.frmtab.setTabToolTip(_i, _filename)
                        if not os.access(_filename, os.W_OK):
                            self.frmtab.tabBar().setTabTextColor(_i, QColor("#009900"))
                        self.setWindowTitle("pyeditor6 - {}".format(os.path.basename(_filename) or "Unknown"))
                        self.frmtab.setCurrentIndex(_i)
                        _i += 1
        #
        if _i == 0:
            pop_tab = ftab(afilename, self.isargument, self)
            self.frmtab.addTab(pop_tab, os.path.basename(afilename) or "Unknown")
            self.frmtab.setTabToolTip(0, afilename or "Unknown")
            if afilename:
                if not os.access(afilename, os.W_OK):
                    self.frmtab.tabBar().setTabTextColor(self.frmtab.count()-1, QColor("#009900"))
            #
            self.setWindowTitle("pyeditor6 - {}".format(os.path.basename(afilename) or "Unknown"))
        #
        if DARKTHEME == 2:
            self.setStyleSheet("QPushButton, QComboBox {border: 0px solid #D1CFCF; background: #717171;} QPushButton:hover {border: 1px solid #cecece;}")
            self.frmtab.setStyleSheet("QTabWidget {background-color: #353535;}")
        #
        self.show()
    
    def interfaces_removed(self, *args):
        try:
            if len(args) > 0:
                # if args[0] == "org.QtDBus.pyeditor6":
                if "org.QtDBus.pyeditor6" in args:
                    if QDBusConnection.sessionBus().registerService('org.QtDBus.pyeditor6'):
                        QDBusConnection.sessionBus().registerObject('/', self, QDBusConnection.RegisterOption.ExportAllSlots)
        except:
            pass
    
    @pyqtSlot(str, result=str)
    def ping(self, arg):
        self.on_single_instance(arg)
        return arg
    
    def config_btn_action(self):
        confwin = confWin(self.window)
        
    def get_mimetype(self, afile):
        file_type = QMimeDatabase().mimeTypeForFile(afile, QMimeDatabase.MatchMode.MatchDefault).name()
        return file_type
        
    def set_mimetype(self, afile):
        if os.path.exists(afile):
            file_type = self.get_mimetype(afile)
            if file_type == "text/x-python3" or file_type == "text/x-python":
                return 1
            elif file_type == "application/x-shellscript":
                return 2
            elif file_type == "application/javascript":
                return 3
            elif file_type == "text/plain":
                return 4
            elif file_type == "application/octet-stream":
                return 4
        # else:
            # return 4
        
    def on_tab_changed(self, idx):
        # self.sender().tabText(idx)
        self.setWindowTitle("pyeditor6 - {}".format(self.frmtab.tabText(idx)))
    
    # open a file from the history
    def on_h_menu(self, action):
        fileName = os.path.realpath(action.text())
        if not os.path.exists(fileName) or not os.access(fileName, os.R_OK):
            MyDialog("Info", "The file\n{}\ndoes not exist.".format(fileName), self)
            return
        #
        is_found = 0
        for tt in range(self.frmtab.count()):
            # if self.frmtab.tabText(tt) == os.path.basename(fileName.strip("\n")):
            if self.frmtab.tabToolTip(tt) == fileName.strip("\n"):
                is_found = 1
                break
        if is_found:
            MyDialog("Info", "File already opened.", self)
        else:
            self.on_open_f(fileName.strip("\n"))
        
    def on_clone(self):
        _current_tab = self.frmtab.currentWidget()
        pop_tab = ftab("", self.isargument, self)
        pop_tab.on_set_text(_current_tab.on_get_text())
        self.frmtab.addTab(pop_tab, "Unknown")
        self.frmtab.setCurrentIndex(self.frmtab.count()-1)
        self.frmtab.setTabToolTip(self.frmtab.count()-1, "Unknown")
    
    def on_new(self):
        ret = retDialogBox("Question", "Create a new document?", self)
        if ret.getValue() == 0:
            return
        #
        fileName = ""
        pop_tab = ftab(fileName, self.isargument, self)
        #pop_tab = ftab(fileName, 4, self)
        self.frmtab.addTab(pop_tab, os.path.basename(fileName) or "Unknown")
        self.frmtab.setCurrentIndex(self.frmtab.count()-1)
        self.frmtab.setTabToolTip(self.frmtab.count()-1, fileName or "Unknown")
    
    def on_open(self):
        ret = retDialogBox("Question", "Open a new document?", self)
        if ret.getValue() == 0:
            return
        #
        fileName, _ = QFileDialog.getOpenFileName(self, "Select the file", os.path.expanduser('~'), "All Files (*)")
        if fileName:
            if os.path.exists(fileName) and os.path.isfile(fileName) and os.access(fileName, os.R_OK):
                self.on_open_f(fileName)
            else:
                MyDialog("Error", "Problem with the file.\nIt doesn't exist or it isn't readable.", self)
    
    def bring_to_top(self):
        flags = self.windowFlags()
        flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        # self.show()
        flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
    
    def on_single_instance(self,filename):
        if filename == "":
            return
        _pages = self.frmtab.count()
        for i in range(_pages):
            _text = self.frmtab.tabBar().tabToolTip(i)
            if _text == filename:
                self.frmtab.tabBar().setCurrentIndex(i)
                self.bring_to_top()
                return
        #
        self.on_open_f(filename)
        self.bring_to_top()
        
    # related to on_open
    def on_open_f(self, fileName):
        if fileName:
            if not os.path.isfile(fileName):
                MyDialog("Info", "Not a file.", self)
                return
            #
            file_type = self.set_mimetype(fileName)
            pop_tab = ftab(fileName, file_type, self)
            self.frmtab.addTab(pop_tab, os.path.basename(fileName) or "Unknown")
            self.frmtab.setCurrentIndex(self.frmtab.count()-1)
            self.frmtab.setTabToolTip(self.frmtab.count()-1, fileName or "Unknown")
            #
            if not os.access(fileName, os.W_OK):
                self.frmtab.tabBar().setTabTextColor(self.frmtab.count()-1, QColor("#009900"))
            #
            if not fileName+"\n" in self.pageNameHistory:
                self.btn_h_menu.addAction(fileName)
                self.pageNameHistory.append(fileName+"\n")
    
    def __btn_action(self):
        self.close()
    
    def closeEvent(self, event):
        isModified = False
        #
        for tt in range(self.frmtab.count()):
            if self.frmtab.widget(tt).isModified:
                isModified = True
                break
        #
        if isModified:
            ret = retDialogBox("Question", "A document has been modified. \nDo you want to proceed anyway?", self)
            if ret.getValue() == 0:
                event.ignore()
                return
        #
        else:
            ret = retDialogBox("Question", "Exit?", self)
            if ret.getValue() == 0:
                event.ignore()
                return
        # 
        self.on_close()
        
    def on_close(self):
        # save the history
        try:
            with open("pyeditorh.txt", "w") as ff:
                for el in self.pageNameHistory[-HISTORYLIMIT:]:
                    ff.write(el)
        except Exception as E:
            MyDialog("Error", "Cannot save the file history.", self)
        #
        new_w = self.size().width()
        new_h = self.size().height()
        if new_w != int(WINW) or new_h != int(WINH):
            # WINW = width
            # WINH = height
            # WINM = maximized
            isMaximized = self.isMaximized()
            # close without update the file
            if isMaximized == True:
                QApplication.quit()
                return
            #
            try:
                ifile = open("pyeditor.cfg", "w")
                ifile.write("{};{};False".format(new_w, new_h))
                ifile.close()
            except Exception as E:
                MyDialog("Error", str(E), self)
        #
        QApplication.quit()
    
    # #
    # def on_tab_close(self, idx):
        # if self.frmtab.widget(idx).isModified:
            # MyDialog("Info", "Save the file first.", self)
            # return
        # else:
            # if self.frmtab.count() > 1:
                # self.frmtab.removeTab(idx)
                # return
            # self.on_open_f("")
    
    
class ftab(QWidget):
    def __init__(self, afilename, editortype, parent):
        super().__init__()
        self.parent = parent
        self.setContentsMargins(1,1,1,1)
        self.isargument = editortype
        self.isModified = False
        # default font
        self.__myFont = QFont()
        self.__myFont.setFamily(FONTFAMILY)
        self.__myFont.setPointSize(FONTSIZE)
        #
        # default italic font
        self.__myFontI = QFont()
        self.__myFontI.setFamily(FONTFAMILY)
        self.__myFontI.setPointSize(FONTSIZE)
        self.__myFontI.setStyle(QFont.Style.StyleItalic)
        # default bold font
        self.__myFontB = QFont()
        self.__myFontB.setFamily(FONTFAMILY)
        self.__myFontB.setPointSize(FONTSIZE)
        self.__myFontB.setWeight(QFont.Weight.Bold)
        #
        self.pageName = None
        if afilename:
            filePath = os.path.realpath(afilename)
            if os.path.exists(filePath) and os.path.isfile(filePath) and os.access(filePath, os.R_OK):
                self.pageName = filePath
        #
        self.his_searched = []
        #
        self.search_is_open = 0
        #
        self.sufftype = ""
        #
        self.pop_tab(afilename)
        #
        self._afilename = afilename
        if USE_RELOAD_DOC:
            try:
                with open(os.path.join(main_dir,"file_opened"), "a") as _f:
                    _f.write("{}\n".format(afilename))
            except:
                pass
        # restore the right value
        self.__editor.setModified(False)
        # 
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.fileChanged.connect(self.on_file_changed)
        # the file is saved by the user
        self.save_from_this = 0
        #
        if self.pageName:
            self.add_filewatcher(self.pageName)
    
    def add_filewatcher(self, _file):
        self.file_watcher.addPath(_file)
    
    def on_file_changed(self, _file):
        if self.save_from_this == 1:
            self.save_from_this = 0
            return
        if self.isModified == False and self.save_from_this == 0:
            self.__editor.setModified(True)
            self.isModified = True
            curr_idx = None
            _pages = self.parent.frmtab.count()
            for i in range(_pages):
                _text = self.parent.frmtab.tabBar().tabToolTip(i)
                if _text == _file:
                    curr_idx = i
                    break
            if curr_idx != None:
                self.parent.frmtab.tabBar().setTabTextColor(curr_idx, QColor(255,0,0))
    
    def on_get_text(self):
        return self.__editor.text()
        
    def on_set_text(self, _text):
        self.__editor.setText(_text)
    
    # def __is_modified(self):
        # # return self.isModified
        # return self.__editor.isModified()
    
    def pop_tab(self, afilename):
        self.__lyt = QVBoxLayout()
        self.__lyt.setContentsMargins(1,1,1,1)
        self.setLayout(self.__lyt)
        # document buttons
        self.btn_box = QHBoxLayout()
        self.__lyt.addLayout(self.btn_box)
        #
        self.combo_tab = QComboBox()
        self.combo_tab.addItems(["Spaces", "Tab"])
        self.btn_box.addWidget(self.combo_tab)
        #
        self.combo_space = QComboBox()
        self.combo_space.addItems(["2","3","4","5","6","7","8"])
        self.btn_box.addWidget(self.combo_space)
        #
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["p", "b", "j", "t"])
        self.btn_box.addWidget(self.lang_combo)
        #
        # self.combo_eol = QComboBox()
        # self.combo_eol.addItems(["L","W"])
        # self.btn_box.addWidget(self.combo_eol)
        #
        self.btn_ro = QPushButton()
        self.btn_ro.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.FormatJustifyFill, QIcon(os.path.join(ICON_PATH, "readonly.png"))))
        self.btn_ro.setToolTip("Read only")
        self.btn_ro.clicked.connect(self.on_read_only)
        self.btn_box.addWidget(self.btn_ro, stretch=1)
        #  
        self.btn_search = QPushButton()
        self.btn_search.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.EditFind, QIcon(os.path.join(ICON_PATH, "edit-find-replace.png"))))
        self.btn_search.setToolTip("Search or replace")
        self.btn_search.clicked.connect(self.on_search)
        self.btn_box.addWidget(self.btn_search, stretch=1)
        #
        # self.btn_box2.addStretch(stretch=20)
        #
        self.btn_comment = QPushButton()
        self.btn_comment.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.FormatIndentMore, QIcon(os.path.join(ICON_PATH, "commentout.png"))))
        self.btn_comment.setToolTip("Comment out")
        self.btn_comment.clicked.connect(self.on_btn_comment)
        self.btn_box.addWidget(self.btn_comment, stretch=1)
        #
        self.btn_uncomment = QPushButton()
        self.btn_uncomment.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.FormatIndentLess, QIcon(os.path.join(ICON_PATH, "uncomment.png"))))
        self.btn_uncomment.setToolTip("Uncomment")
        self.btn_uncomment.clicked.connect(self.on_btn_uncomment)
        self.btn_box.addWidget(self.btn_uncomment, stretch=1)
        #
        self.btn_hl = QPushButton()
        self.btn_hl.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.FormatTextBold, QIcon(os.path.join(ICON_PATH, "highlight.png"))))
        self.btn_hl.setToolTip("Highlight")
        self.btn_hl.setCheckable(True)
        self.btn_hl.clicked.connect(self.on_btn_hl)
        self.btn_box.addWidget(self.btn_hl, stretch=0)
        #
        self.btn_print = QPushButton()
        self.btn_print.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.DocumentPrint, QIcon(os.path.join(ICON_PATH, "document-print.png"))))
        self.btn_print.setToolTip("Print")
        self.btn_print.clicked.connect(self.on_btn_print)
        self.btn_box.addWidget(self.btn_print, stretch=0)
        #
        self.btn_box.addStretch(stretch=20)
        #
        self.btn_save = QPushButton()
        self.btn_save.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.DocumentSave, QIcon(os.path.join(ICON_PATH, "document-save.png"))))
        self.btn_save.setToolTip("Save this document")
        self.btn_save.clicked.connect(self.on_save)
        self.btn_box.addWidget(self.btn_save, stretch=1)
        #
        self.btn_save_as = QPushButton()
        self.btn_save_as.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.DocumentSaveAs, QIcon(os.path.join(ICON_PATH, "document-save-as.png"))))
        self.btn_save_as.setToolTip("Save this document with a new name")
        self.btn_save_as.clicked.connect(self.on_save_as)
        self.btn_box.addWidget(self.btn_save_as, stretch=1)
        #
        self.__btn_close = QPushButton()
        self.__btn_close.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.WindowClose, QIcon(os.path.join(ICON_PATH, "application-exit.png"))))
        self.__btn_close.setToolTip("Close this document")
        self.__btn_close.clicked.connect(self.__btn_action_close)
        self.btn_box.addWidget(self.__btn_close, stretch=1)
        #
        ####
        # self.btn_box2 = QHBoxLayout()
        # self.__lyt.addLayout(self.btn_box2)
        # self.btn_search = QPushButton()
        # self.btn_search.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.EditFind, QIcon(os.path.join(ICON_PATH, "edit-find-replace.png"))))
        # self.btn_search.setToolTip("Search or replace")
        # self.btn_search.clicked.connect(self.on_search)
        # self.btn_box.addWidget(self.btn_search, stretch=1)
        # #
        # # self.btn_box2.addStretch(stretch=20)
        # #
        # self.btn_comment = QPushButton()
        # self.btn_comment.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.FormatIndentMore, QIcon(os.path.join(ICON_PATH, "commentout.png"))))
        # self.btn_comment.setToolTip("Comment out")
        # self.btn_comment.clicked.connect(self.on_btn_comment)
        # self.btn_box.addWidget(self.btn_comment, stretch=1)
        # #
        # self.btn_uncomment = QPushButton()
        # self.btn_uncomment.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.FormatIndentLess, QIcon(os.path.join(ICON_PATH, "uncomment.png"))))
        # self.btn_uncomment.setToolTip("Uncomment")
        # self.btn_uncomment.clicked.connect(self.on_btn_uncomment)
        # self.btn_box.addWidget(self.btn_uncomment, stretch=1)
        # #
        # self.btn_hl = QPushButton()
        # self.btn_hl.setIcon(QIcon().fromTheme(QIcon.ThemeIcon.FormatTextBold, QIcon(os.path.join(ICON_PATH, "highlight.png"))))
        # self.btn_hl.setToolTip("Highlight")
        # self.btn_hl.setCheckable(True)
        # self.btn_hl.clicked.connect(self.on_btn_hl)
        # self.btn_box.addWidget(self.btn_hl, stretch=0)
        #
        # self.btn_box2.addStretch(stretch=20)
        # ----------------------------------------
        # self.__editor = QsciScintilla()
        self.__editor = MyQsciScintilla()
        # load the file passed as argument
        filenotfound = 0
        try:
            if self.pageName and os.path.exists(self.pageName) and os.path.isfile(self.pageName) and os.access(self.pageName, os.R_OK):
                fd = QFile(self.pageName)
                fd.open(QIODevice.OpenModeFlag.ReadOnly)
                self.__editor.read(fd)
                fd.close()
            else:
                filenotfound = 1
        except Exception as E:
            MyDialog("Error", str(E), self.parent)
        #
        self.__editor.setLexer(None)            # We install lexer later
        self.__editor.setUtf8(True)             # Set encoding to UTF-8
        # Brace matchingself.frmtab.
        self.__editor.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        #####
        self.__editor.setAutoCompletionThreshold(AUTOCOMPLETITION_CHARS)
        self.__editor.setAutoCompletionCaseSensitivity(True)
        self.__editor.setAutoCompletionReplaceWord(False)
        self.__editor.setAutoCompletionUseSingle(QsciScintilla.AutoCompletionUseSingle.AcusNever)
        self.__editor.autoCompleteFromDocument()
        self.__editor.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsDocument)
        if USEWORDAUTOCOMLETION:
            self.__editor.setAutoCompletionWordSeparators(["."])
        # # End-of-line mode
        # # --------------------
        # if ENDOFLINE == "unix":
            # self.__editor.setEolMode(QsciScintilla.EolUnix)
        # elif ENDOFLINE == "windows":
            # self.__editor.setEolMode(QsciScintilla.EolWindows)
            # self.combo_eol.setCurrentIndex(1)
        #
        self.__editor.setEolVisibility(False)
        # Indentation
        # ---------------
        self.__editor.setIndentationsUseTabs(USETAB)
        self.__editor.setTabWidth(TABWIDTH+2)
        self.combo_tab.currentIndexChanged.connect(self.on_combo_tab)
        self.combo_tab.setCurrentIndex(USETAB)
        self.combo_space.currentIndexChanged.connect(self.on_combo_space)
        self.combo_space.setCurrentIndex(max(TABWIDTH+2, 2)-2)
        # self.combo_eol.currentIndexChanged.connect(self.on_eol)
        self.__editor.setIndentationGuides(True)
        self.__editor.setTabIndents(True)
        self.__editor.setAutoIndent(True)
        self.__editor.setBackspaceUnindents(True)
        # a character has been typed
        # self.__editor.SCN_CHARADDED.connect(filenotfoundself.on_k)
        self.__editor.keyPressed.connect(self.on_k)
        # the text has been modified
        self.__editor.modificationChanged.connect(self.on_text_changed)
        # Caret
        # ---------
        self.__editor.setCaretLineVisible(True)
        self.__editor.setCaretWidth(CARETWIDTH)
        # Margins
        # -----------
        # Margin 0 = Line nr margin
        self.__editor.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.__editor.setMarginWidth(0, "00000")
        #######################
        # # self.__lexer = MyLexer(self.__editor)
        # self.__lexer = QsciLexerPython(self.__editor)
        self.__lexer = textLexer(self.__myFont, self.__editor)
        self.__lexer.setDefaultFont(self.__myFont)
        self.__editor.setLexer(self.__lexer)
        #
        # font
        self.__lexer.setFont(QFont(FONTFAMILY, FONTSIZE))
        ##################
        # 
        # ! Add editor to layout !
        # -------------------------
        self.__lyt.addWidget(self.__editor, stretch=1)
        # 
        self.__editor.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        #
        # python
        if self.isargument == 1:
            self.lang_combo.setCurrentIndex(0)
            self.on_lang_combo(0)
            self.lpython()
        # bash
        elif self.isargument == 2:
            self.lang_combo.setCurrentIndex(1)
            self.on_lang_combo(1)
            self.lbash()
        # javascript
        elif self.isargument == 3:
            self.lang_combo.setCurrentIndex(2)
            self.on_lang_combo(2)
            self.ljavascript()
        # text
        elif self.isargument == 4:
            self.lang_combo.setCurrentIndex(3)
            self.on_lang_combo(3)
            self.ltext()
        #
        if STATUSBAR:
            self.statusBar = QStatusBar()
            self.__lyt.addWidget(self.statusBar)
            self.statusBar.showMessage("line: {0}/{1} column: {2}".format("-", "-", "-"))
        # set the theme colours
        self.on_theme()
        #
        self.lang_combo.currentIndexChanged.connect(self.on_lang_combo)
        #
        self.show()
        # 
        if filenotfound and afilename:
            MyDialog("Error", "The file\n\n{}\n\ndoesn't exist or it isn't readable.".format(afilename), self.parent)
        # file is not writable
        if self.pageName and not os.access(self.pageName, os.W_OK):
            self.__editor.setReadOnly(True)
            self.btn_ro.setStyleSheet("QPushButton {color: #009900;}")
            #
            self.combo_tab.setEnabled(False)
            self.combo_space.setEnabled(False)
            self.lang_combo.setEnabled(False)
            self.btn_save.setEnabled(False)
            self.btn_save_as.setEnabled(False)
            self.btn_comment.setEnabled(False)
            self.btn_uncomment.setEnabled(False)
            self.btn_hl.setEnabled(False)
        
    def on_btn_hl(self):
        if self.btn_hl.isChecked():
            if self.__editor.hasSelectedText():
                htext = self.__editor.selectedText()
                #
                lines = self.__editor.lines()
                #
                for line in range(lines):
                    ret = [m.start() for m in re.finditer(htext, self.__editor.text(line))]
                    # 
                    if ret:
                        self.__editor.fillIndicatorRange(     
                        line, # line from
                        ret[0], # column from
                        line, # line to
                        ret[0]+len(htext), # column to
                        0 )
        else:
            lines = self.__editor.lines()
            for line in range(lines):
                self.__editor.clearIndicatorRange(line, 0, line, len(self.__editor.text(line)), 0)
    
    def handle_paint_request(self, printer):
        painter = QPainter(printer)
        painter.setViewport(self.chart_view.rect())
        painter.setWindow(self.chart_view.rect())                        
        self.chart_view.render(painter)
        painter.end()
    
    def on_btn_print(self):
        _editor = QTextEdit()
        font = QFont(PRINT_FONT, PRINT_FONT_SIZE)
        _editor.setFont(font)
        _editor.setPlainText(self.__editor.text())
        dlg = QtPrintSupport.QPrintDialog()
        if dlg.exec():
            _printer = dlg.printer()
            _editor.print(_printer)
        
    def on_combo_tab(self, idx):
        self.__editor.setIndentationsUseTabs(bool(idx))
        if idx:
            self.combo_space.setEnabled(False)
        else:
            self.combo_space.setEnabled(True)
        
    def on_combo_space(self, idx):
        self.__editor.setTabWidth(int(idx)+2)
    
    # def on_eol(self, idx):
        # self.combo_eol.setCurrentIndex(idx)
    
    def on_theme(self):
        if DARKTHEME:
            self.__editor.setMarginsForegroundColor(QColor(DMARGINFOREGROUND))
            self.__editor.setMarginsBackgroundColor(QColor(DMARGINBACKGROUND))
            self.__editor.setMarginsFont(self.__myFont)
            # Caret
            self.__editor.setCaretForegroundColor(QColor(DCARETFORE))
            self.__editor.setCaretLineBackgroundColor(QColor(DCARETBACK))
        else:
            self.__editor.setMarginsForegroundColor(QColor(MARGINFOREGROUND))
            self.__editor.setMarginsBackgroundColor(QColor(MARGINBACKGROUND))
            self.__editor.setMarginsFont(self.__myFont)
            # Caret
            self.__editor.setCaretForegroundColor(QColor(CARETFORE))
            self.__editor.setCaretLineBackgroundColor(QColor(CARETBACK))
            #
        # editor background color
        if DARKTHEME:
            self.__lexer.setPaper(QColor(DEDITORBACKCOLOR))
        else:
            self.__lexer.setPaper(QColor(EDITORBACKCOLOR))
        # Brace matching
        if DARKTHEME:
            self.__editor.setMatchedBraceBackgroundColor(QColor(DMATCHEDBRACECOLOR))
            # selected word colour
            self.__editor.setSelectionBackgroundColor(QColor(DSELECTIONBACKGROUNDCOLOR))
        else:
            self.__editor.setMatchedBraceBackgroundColor(QColor(MATCHEDBRACECOLOR))
            # selected word colour
            self.__editor.setSelectionBackgroundColor(QColor(SELECTIONBACKGROUNDCOLOR))
    
    def on_text_changed(self, _bool):
        if _bool == True:
            # if self.isModified == False:
            self.isModified = True
            curr_idx = self.parent.frmtab.currentIndex()
            self.parent.frmtab.tabBar().setTabTextColor(curr_idx, QColor(255,0,0))
            # self.parent.frmtab.tabBar().setTabText(curr_idx, self.parent.frmtab.tabBar().tabText(curr_idx)+" *")
        elif _bool == False:
            # if self.isModified == True:
            self.isModified = False
            curr_idx = self.parent.frmtab.currentIndex()
            # _text = self.parent.frmtab.tabBar().tabText(curr_idx).rstrip(" *")
            # self.parent.frmtab.tabBar().setTabText(curr_idx, _text)
            self.parent.frmtab.tabBar().setTabTextColor(curr_idx, self.parent.frmtab_tab_text_color)
        
    def lpython(self):
        if not CUSTOMCOLORS:
            return
        if DARKTHEME:
            # Default
            self.__lexer.setColor(QColor(PDDEFAULT), 0)
            # Comment
            self.__lexer.setFont(self.__myFontI, 1)
            self.__lexer.setColor(QColor(PDCOMMENT), 1)
            # Number
            self.__lexer.setColor(QColor(PDNUMBER), 2)
            # Double-quoted string
            self.__lexer.setFont(self.__myFont, 3)
            self.__lexer.setColor(QColor(PDDOUBLEQ), 3)
            # Single-quoted string
            self.__lexer.setFont(self.__myFont, 4)
            self.__lexer.setColor(QColor(PDSINGELQ), 4)
            # Keyword
            self.__lexer.setFont(self.__myFontB, 5)
            self.__lexer.setColor(QColor(PDKEYW), 5)
            # Triple single-quoted string
            self.__lexer.setColor(QColor(PDTRIPLESQ), 6)
            # Triple double-quoted string
            self.__lexer.setColor(QColor(PDTRIPLEDQ), 7)
            # Class name
            self.__lexer.setFont(self.__myFontB, 8)
            self.__lexer.setColor(QColor(PDCLASSNAME), 8)
            # Function or method name
            self.__lexer.setFont(self.__myFontB, 9)
            self.__lexer.setColor(QColor(PDFUNCTION), 9)
            # Operator
            self.__lexer.setColor(QColor(PDOPERATOR), 10)
            # Identifier
            self.__lexer.setColor(QColor(PDIDENTIFIER), 11)
            # Comment block
            self.__lexer.setColor(QColor(PDCOMMENTB), 12)
            # Unclosed string
            self.__lexer.setColor(QColor(PDUNCLOSEDSTRING), 13)
            # Highlighted identifier
            self.__lexer.setColor(QColor(PDHIGHLIGHTED), 14)
            # Decorator
            self.__lexer.setFont(self.__myFontB, 15)
            self.__lexer.setColor(QColor(PDDECORATOR), 15)
        else:
            # Default
            self.__lexer.setColor(QColor(PDEFAULT), 0)
            # Comment
            self.__lexer.setFont(self.__myFontI, 1)
            self.__lexer.setColor(QColor(PCOMMENT), 1)
            # Number
            self.__lexer.setColor(QColor(PNUMBER), 2)
            # Double-quoted string
            self.__lexer.setFont(self.__myFont, 3)
            self.__lexer.setColor(QColor(PDOUBLEQ), 3)
            # Single-quoted string
            self.__lexer.setFont(self.__myFont, 4)
            self.__lexer.setColor(QColor(PSINGELQ), 4)
            # Keyword
            self.__lexer.setFont(self.__myFontB, 5)
            self.__lexer.setColor(QColor(PKEYW), 5)
            # Triple single-quoted string
            self.__lexer.setColor(QColor(PTRIPLESQ), 6)
            # Triple double-quoted string
            self.__lexer.setColor(QColor(PTRIPLEDQ), 7)
            # Class name
            self.__lexer.setFont(self.__myFontB, 8)
            self.__lexer.setColor(QColor(PCLASSNAME), 8)
            # Function or method name
            self.__lexer.setColor(QColor(PFUNCTION), 9)
            # Operator
            self.__lexer.setColor(QColor(POPERATOR), 10)
            # Identifier
            self.__lexer.setColor(QColor(PIDENTIFIER), 11)
            # Comment block
            self.__lexer.setColor(QColor(PCOMMENTB), 12)
            # Unclosed string
            self.__lexer.setColor(QColor(PUNCLOSEDSTRING), 13)
            # Highlighted identifier
            self.__lexer.setColor(QColor(PHIGHLIGHTED), 14)
            # Decorator
            self.__lexer.setFont(self.__myFontB, 15)
            self.__lexer.setColor(QColor(PDECORATOR), 15)
    
    def lbash(self):
        if not CUSTOMCOLORS:
            return
        if DARKTHEME:
            # Default
            self.__lexer.setColor(QColor(BDDEFAULT), 0)
            # Error
            self.__lexer.setColor(QColor(BDERROR), 1)
            # Comment
            self.__lexer.setFont(self.__myFontI, 2)
            self.__lexer.setColor(QColor(BDCOMMENT), 2)
            # Number
            self.__lexer.setColor(QColor(BDNUMBER), 3)
            # Keyword
            self.__lexer.setFont(self.__myFontB, 4)
            self.__lexer.setColor(QColor(BDKEYW), 4)
            # Double-quoted string
            self.__lexer.setFont(self.__myFont, 5)
            self.__lexer.setColor(QColor(BDDOUBLEQ), 5)
            # Single-quoted string
            self.__lexer.setFont(self.__myFont, 6)
            self.__lexer.setColor(QColor(BDSINGELQ), 6)
            # Operator
            self.__lexer.setColor(QColor(BDOPERATOR), 7)
            # Identifier
            self.__lexer.setColor(QColor(BDIDENTIFIER), 8)
            # Scalar
            self.__lexer.setColor(QColor(BDSCALAR), 9)
            # Parameter expansion
            self.__lexer.setColor(QColor(BDPAREXP), 10)
            # Backticks
            self.__lexer.setColor(QColor(BDBACKTICK), 11)
            # Here document delimiter
            self.__lexer.setColor(QColor(BDHDOCDEL), 12)
            # Single-quoted here document
            self.__lexer.setColor(QColor(BDSQHEREDOC), 13)
        else:
            # Default
            self.__lexer.setColor(QColor(BDEFAULT), 0)
            # Error
            self.__lexer.setColor(QColor(BERROR), 1)
            # Comment
            self.__lexer.setFont(self.__myFontI, 2)
            self.__lexer.setColor(QColor(BCOMMENT), 2)
            # Number
            self.__lexer.setColor(QColor(BNUMBER), 3)
            # Keyword
            self.__lexer.setFont(self.__myFontB, 4)
            self.__lexer.setColor(QColor(BKEYW), 4)
            # Double-quoted string
            self.__lexer.setFont(self.__myFont, 5)
            self.__lexer.setColor(QColor(BDOUBLEQ), 5)
            # Single-quoted string
            self.__lexer.setFont(self.__myFont, 6)
            self.__lexer.setColor(QColor(BSINGELQ), 6)
            # Operator
            self.__lexer.setColor(QColor(BOPERATOR), 7)
            # Identifier
            self.__lexer.setColor(QColor(BIDENTIFIER), 8)
            # Scalar
            self.__lexer.setColor(QColor(BSCALAR), 9)
            # Parameter expansion
            self.__lexer.setColor(QColor(BPAREXP), 10)
            # Backticks
            self.__lexer.setColor(QColor(BBACKTICK), 11)
            # Here document delimiter
            self.__lexer.setColor(QColor(BHDOCDEL), 12)
            # Single-quoted here document
            self.__lexer.setColor(QColor(BSQHEREDOC), 13)
    
    def ljavascript(self):
        if not CUSTOMCOLORS:
            return
        if DARKTHEME:
            # Default
            self.__lexer.setColor(QColor(JDDEFAULT), 0)
            # C comment
            # C++ comment
            # JavaDoc style C comment
            # JavaDoc style pre-processor comment
            # JavaDoc style C++ co    mment
            # Pre-processor C comment
            # JavaDoc style pre-processor comment
            self.__lexer.setFont(self.__myFontI, 1)
            self.__lexer.setColor(QColor(JDCOMMENT), 1)
            self.__lexer.setFont(self.__myFont, 2)
            self.__lexer.setColor(QColor(JDCOMMENT), 2)
            self.__lexer.setFont(self.__myFont, 3)
            self.__lexer.setColor(QColor(JDCOMMENT), 3)
            self.__lexer.setFont(self.__myFont, 15)
            self.__lexer.setColor(QColor(JDCOMMENT), 15)
            self.__lexer.setColor(QColor(JDCOMMENT), 23)
            self.__lexer.setColor(QColor(JDCOMMENT), 24)
            # Number
            self.__lexer.setColor(QColor(JDNUMBER), 4)
            # Keyword
            # JavaDoc keyword
            self.__lexer.setFont(self.__myFontB, 5)
            self.__lexer.setColor(QColor(JDKEYW), 5)
            self.__lexer.setFont(self.__myFontB, 17)
            self.__lexer.setColor(QColor(JDKEYW), 17)
            # Double-quoted string
            self.__lexer.setFont(self.__myFont, 6)
            self.__lexer.setColor(QColor(JDDOUBLEQ), 6)
            # Single-quoted string
            self.__lexer.setFont(self.__myFont, 7)
            self.__lexer.setColor(QColor(JDSINGELQ), 7)
            # IDL UUID
            self.__lexer.setColor(QColor(JDUUID), 8)
            # Pre-processor block
            self.__lexer.setColor(QColor(JDPREPB), 9)
            # Operator
            self.__lexer.setColor(QColor(JDOPERATOR), 10)
            # Identifier
            self.__lexer.setColor(QColor(JDIDENTIFIER), 11)
            # Unclosed string
            self.__lexer.setColor(QColor(JDUNCLOSEDS), 12)
            # C# verbatim string
            self.__lexer.setColor(QColor(JDCVERBS), 13)
            # Regular expression
            self.__lexer.setColor(QColor(JDREGESPR), 14)
            # Secondary keywords and identifiers
            self.__lexer.setColor(QColor(JDSECKI), 16)
            # JavaDoc keyword error
            self.__lexer.setColor(QColor(JDJAVADOCERROR), 18)
            # Global classes and typedefs
            self.__lexer.setFont(self.__myFontB, 19)
            self.__lexer.setColor(QColor(JDCLASSES), 19)
            # C++ raw string
            self.__lexer.setColor(QColor(JDDEFAULT), 20)
            # Vala triple-quoted verbatim string
            self.__lexer.setColor(QColor(JDDEFAULT), 21)
            # Pike hash-quoted string
            self.__lexer.setColor(QColor(JDPIKEHQS), 22)
            # User-defined literal
            self.__lexer.setColor(QColor(JDUSERDLIT), 25)
            # Task marker
            self.__lexer.setColor(QColor(JDTASKMARKER), 26)
            # Escape sequence
            self.__lexer.setColor(QColor(JDESCAPES), 27)
        else:
            # Default
            self.__lexer.setColor(QColor(JDEFAULT), 0)
            # C comment
            # C++ comment
            # JavaDoc style C comment
            # JavaDoc style pre-processor comment
            # JavaDoc style C++ comment
            # Pre-processor C comment
            # JavaDoc style pre-processor comment
            self.__lexer.setFont(self.__myFontI, 1)
            self.__lexer.setColor(QColor(JCOMMENT), 1)
            self.__lexer.setFont(self.__myFont, 2)
            self.__lexer.setColor(QColor(JCOMMENT), 2)
            self.__lexer.setFont(self.__myFont, 3)
            self.__lexer.setColor(QColor(JCOMMENT), 3)
            self.__lexer.setFont(self.__myFont, 15)
            self.__lexer.setColor(QColor(JCOMMENT), 15)
            self.__lexer.setColor(QColor(JCOMMENT), 23)
            self.__lexer.setColor(QColor(JCOMMENT), 24)
            # Number
            self.__lexer.setColor(QColor(JNUMBER), 4)
            # Keyword
            # JavaDoc keyword
            self.__lexer.setFont(self.__myFontB, 5)
            self.__lexer.setColor(QColor(JKEYW), 5)
            self.__lexer.setFont(self.__myFontB, 17)
            self.__lexer.setColor(QColor(JKEYW), 17)
            # Double-quoted string
            self.__lexer.setFont(self.__myFont, 6)
            self.__lexer.setColor(QColor(JDOUBLEQ), 6)
            # Single-quoted string
            self.__lexer.setFont(self.__myFont, 7)
            self.__lexer.setColor(QColor(JSINGELQ), 7)
            # IDL UUID
            self.__lexer.setColor(QColor(JUUID), 8)
            # Pre-processor block
            self.__lexer.setColor(QColor(JPREPB), 9)
            # Operator
            self.__lexer.setColor(QColor(JOPERATOR), 10)
            # Identifier
            self.__lexer.setColor(QColor(JIDENTIFIER), 11)
            # Unclosed string
            self.__lexer.setColor(QColor(JUNCLOSEDS), 12)
            # C# verbatim string
            self.__lexer.setColor(QColor(JCVERBS), 13)
            # Regular expression
            self.__lexer.setColor(QColor(JREGESPR), 14)
            # Secondary keywords and identifiers
            self.__lexer.setColor(QColor(JSECKI), 16)
            # JavaDoc keyword error
            self.__lexer.setColor(QColor(JJAVADOCERROR), 18)
            # Global classes and typedefs
            self.__lexer.setFont(self.__myFontB, 19)
            self.__lexer.setColor(QColor(JCLASSES), 19)
            # C++ raw string
            self.__lexer.setColor(QColor(JDEFAULT), 20)
            # Vala triple-quoted verbatim string
            self.__lexer.setColor(QColor(JDEFAULT), 21)
            # Pike hash-quoted string
            self.__lexer.setColor(QColor(JPIKEHQS), 22)
            # User-defined literal
            self.__lexer.setColor(QColor(JUSERDLIT), 25)
            # Task marker
            self.__lexer.setColor(QColor(JTASKMARKER), 26)
            # Escape sequence
            self.__lexer.setColor(QColor(JESCAPES), 27)
    
    def ltext(self):
        if DARKTHEME:
            # Default
            self.__lexer.setColor(QColor(PDDEFAULT), 0)
        else:
            # Default
            self.__lexer.setColor(QColor(PDEFAULT), 0)
    
    #
    def on_lang_combo(self, idx):
        if idx == 0:
            self.STRCOMM = "# "
            self.sufftype = ".py"
            self.__lexer = QsciLexerPython(self.__editor)
            self.__lexer.setDefaultFont(self.__myFont)
            self.__editor.setLexer(self.__lexer)
            #
            self.__editor.setAutoCompletionCaseSensitivity(True)
            # set the styles
            self.lpython()
            # set the theme colours
            self.on_theme()
        elif idx == 1:
            self.STRCOMM = "# "
            self.sufftype = ".sh"
            self.__lexer = QsciLexerBash(self.__editor)
            self.__lexer.setDefaultFont(self.__myFont)
            self.__editor.setLexer(self.__lexer)
            #
            self.__editor.setAutoCompletionCaseSensitivity(True)
            # set the styles
            self.lbash()
            # set the theme colours
            self.on_theme()
        elif idx == 2:
            self.STRCOMM = "// "
            self.sufftype = ".js"
            self.__lexer = QsciLexerJavaScript(self.__editor)
            self.__lexer.setDefaultFont(self.__myFont)
            self.__editor.setLexer(self.__lexer)
            # 
            self.__editor.setAutoCompletionCaseSensitivity(True)
            # set the styles
            self.ljavascript()
            # set the theme colours
            self.on_theme()
        elif idx == 3:
            self.STRCOMM = "// "
            self.sufftype = ".txt"
            self.__lexer = textLexer(self.__myFont, self.__editor)
            self.__editor.setLexer(self.__lexer)
            self.__editor.setAutoCompletionCaseSensitivity(True)
            self.ltext()
            # set the theme colours
            self.on_theme()
    
    #
    def on_read_only(self):
        # if self.isModified:
        if self.__editor.isModified():
            MyDialog("Info", "Save this document first.", self.parent)
            return
        #
        if self.pageName:
            if not os.access(self.pageName, os.W_OK):
                MyDialog("Info", "This document cannot be written.", self.parent)
                return
        #
        if not self.__editor.isReadOnly():
            self.__editor.setReadOnly(True)
            self.sender().setStyleSheet("QPushButton {color: #009900;}")
            curr_idx = self.parent.frmtab.currentIndex()
            self.parent.frmtab.tabBar().setTabTextColor(curr_idx, QColor("#009900"))
            self.combo_tab.setEnabled(False)
            self.combo_space.setEnabled(False)
            self.lang_combo.setEnabled(False)
            self.btn_save.setEnabled(False)
            self.btn_save_as.setEnabled(False)
            self.btn_comment.setEnabled(False)
            self.btn_uncomment.setEnabled(False)
            self.btn_hl.setEnabled(False)
        else:
            self.__editor.setReadOnly(False)
            self.sender().setStyleSheet("")
            curr_idx = self.parent.frmtab.currentIndex()
            self.parent.frmtab.tabBar().setTabTextColor(curr_idx, self.parent.frmtab_tab_text_color)
            self.combo_tab.setEnabled(True)
            self.combo_space.setEnabled(True)
            self.lang_combo.setEnabled(True)
            self.btn_save.setEnabled(True)
            self.btn_save_as.setEnabled(True)
            self.btn_comment.setEnabled(True)
            self.btn_uncomment.setEnabled(True)
            self.btn_hl.setEnabled(True)
    
    #
    def on_save_as(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "File Name...", os.path.join(os.path.expanduser("~"), self.pageName or "document{}".format(self.sufftype)), "All Files (*)")
        if fileName:
            # the previous existent or saved document will remain the current document
            if not self.pageName:
                self.pageName = fileName
            self.on_save(fileName)
    
    #
    def on_save(self, fileName=None):
        if not self.pageName:
            self.pageName = os.path.join(os.path.expanduser("~"), "document{}".format(self.sufftype))
            self.on_save_as()
            return
        #
        issaved = 0
        if fileName:
            _pageName = fileName
        else:
            _pageName = self.pageName
        try:
            # fd = QFile(self.pageName)
            fd = QFile(_pageName)
            fd.open(QIODevice.OpenModeFlag.WriteOnly)
            ret = self.__editor.write(fd)
            if _pageName == self.pageName:
                issaved = ret
            fd.close()
        except Exception as E:
            MyDialog("Error", str(E), self.parent)
        #
        self.save_from_this = 1
        if issaved:
            self.isModified = False
            self.__editor.setModified(False)
            #
            if not self.pageName+"\n" in self.parent.pageNameHistory:
                self.parent.btn_h_menu.addAction(self.pageName+"\n")
                self.parent.pageNameHistory.append(self.pageName+"\n")
            curr_idx = self.parent.frmtab.currentIndex()
            # # the file is only saved with a new name - it will not used
            # if not self.pageName:
            self.parent.frmtab.setTabText(curr_idx, os.path.basename(self.pageName))
            self.parent.frmtab.setTabToolTip(curr_idx, self.pageName)
            self.parent.setWindowTitle("pyeditor6 - {}".format(os.path.basename(self.pageName)))
            self.parent.frmtab.tabBar().setTabTextColor(curr_idx, self.parent.frmtab_tab_text_color)
        # else:
            # MyDialog("Error", "Problem while saving the file.", self.parent)
        
    #
    def on_search(self):
        if self.search_is_open:
            return
        ret_text = self.__editor.selectedText()
        ret = searchDialog(self, ret_text, self.__editor)
    
    #
    def on_btn_comment(self):
        if self.__editor.isReadOnly():
            return
        #
        line_from, _, line_to, _ = self.__editor.getSelection()
        # lines selected
        if line_from != -1 and line_to != -1:
            for line in range(line_from, line_to + 1):
                if self.__editor.text(line) == "":
                    continue
                #
                i = 0
                try:
                    while self.__editor.text(line)[i] == " " or self.__editor.text(line)[i] == "\t":
                        i += 1
                except:
                    return
                #
                self.__editor.insertAt(self.STRCOMM, line, i)
        # no selection
        else:
            line, idx = self.__editor.getCursorPosition()
            if self.__editor.text(line) == "":
                return
            #
            i = 0
            try:
                while self.__editor.text(line)[i] == " " or self.__editor.text(line)[i] == "\t":
                    i += 1
            except:
                return
            #
            self.__editor.insertAt(self.STRCOMM, line, i)
    
    #
    def on_btn_uncomment(self):
        if self.__editor.isReadOnly():
            return
        #
        line_from, _, line_to, _ = self.__editor.getSelection()
        # lines selected
        if line_from != -1 and line_to != -1:
            for line in range(line_from, line_to + 1):
                if self.__editor.text(line) == "":
                    continue
                #
                i = 0
                while self.__editor.text(line)[i] == " " or self.__editor.text(line)[i] == "\t":
                    i += 1
                if self.__editor.text(line)[i:i+len(self.STRCOMM)] == self.STRCOMM:
                    self.__editor.setCursorPosition(line, i)
                    self.__editor.setSelection(line, i, line, i+len(self.STRCOMM))
                    self.__editor.removeSelectedText()
        # no selection
        else:
            line, idx = self.__editor.getCursorPosition()
            if self.__editor.text(line) == "":
                return
            #
            i = 0
            while self.__editor.text(line)[i] == " " or self.__editor.text(line)[i] == "\t":
                i += 1
            #
            if self.__editor.text(line)[i:i+len(self.STRCOMM)] == self.STRCOMM:
                self.__editor.setCursorPosition(line, i)
                self.__editor.setSelection(line, i, line, i+len(self.STRCOMM))
                self.__editor.removeSelectedText()
    
    
    # insert a character if a certain one has been typed
    def on_k(self, id):
        # ctrl++ ctrl+- - find a better way
        if id == "+" or id == "-":
            return
        if self.__editor.isReadOnly():
            return
        # 40 ( - 39 ' - 34 " - 91 [ - 123 { - 161 ¡ - ¿
        if AUTOCLOSE:
            # if id == 40:
            if id == "(":
                self.__editor.insert(")")
            # elif id == 39:
            elif id == "'":
                self.__editor.insert("'")
            # elif id == 34:
            elif id == '"':
                self.__editor.insert('"')
            # elif id == 91:
            elif id == "[":
                self.__editor.insert(']')
            # elif id == 123:
            elif id == "{":
                self.__editor.insert('}')
        if AUTOCLOSE == 2:
            # if id == 161:
            if id == "¡":
                self.__editor.insert('!')
            #
            elif id == "¿":
                self.__editor.insert('?')
        #
        if STATUSBAR:
            line, column = self.__editor.getCursorPosition()
            lines = self.__editor.lines()
            self.statusBar.showMessage("line: {0}/{1} column: {2}".format(line+1, lines, column))
        # # the document has been modified
        # # if not self.isModified:
        # if not self.__editor.isModified():
            # if id == '':
                # return
            # # self.isModified = True
            # curr_idx = self.parent.frmtab.currentIndex()
            # self.parent.frmtab.tabBar().setTabTextColor(curr_idx, QColor(255,0,0))
    
    # def wheelEvent(self, e):
        # if e.modifiers() & Qt.KeyboardModifier.CTRL:
            # if e.angleDelta().y() < 0:
                # self.__editor.zoomOut()
            # else:
                # self.__editor.zoomIn()
    
    def remove_doc_from_list_opened(self):
        try:
            _files = []
            _f = open(os.path.join(main_dir, "file_opened"), "r")
            _files = _f.readlines()
            _f.close()
            #
            for _ff in _files:
                if _ff.strip("\n") == self._afilename:
                    _files.remove(_ff)
            #
            if len(_files) > 0:
                _f = open(os.path.join(main_dir, "file_opened"), "w")
                for ff in _files:
                    _f.write(ff)
                _f.close()
        except Exception as E:
            MyDialog("Error", str(E), self.parent)
    
    def __btn_action_close(self):
        # if self.isModified:
        if self.isModified or self.__editor.isModified():
            ret = retDialogBox("Question", "This document has been modified. \nDo you want to proceed anyway?", self)
            if ret.getValue() == 0:
                return
        #
        else:
            ret = retDialogBox("Question", "Close this document?", self)
            if ret.getValue() == 0:
                return
        #
        if USE_RELOAD_DOC:
            self.remove_doc_from_list_opened()
        #
        if self.parent.frmtab.count() > 1:
            curr_idx = self.parent.frmtab.currentIndex()
            self.parent.frmtab.removeTab(curr_idx)
            return
        else:
            self.__editor.setText("")
            self.isModified = False
            curr_idx = self.parent.frmtab.currentIndex()
            self.parent.frmtab.setTabText(curr_idx, "Unknown")
            self.parent.frmtab.tabBar().setTabTextColor(curr_idx, self.parent.frmtab_tab_text_color)
            self.parent.setWindowTitle("pyeditor6 - Unknown")
            self.statusBar.showMessage("line: -/- column: -")

# simple dialog message
# type - message - parent
class MyDialog(QMessageBox):
    def __init__(self, *args):
        super(MyDialog, self).__init__(args[-1])
        if args[0] == "Info":
            self.setIcon(QMessageBox.Icon.Information)
            self.setStandardButtons(QMessageBox.StandardButton.Ok)
        elif args[0] == "Error":
            self.setIcon(QMessageBox.Icon.Critical)
            self.setStandardButtons(QMessageBox.StandardButton.Ok)
        elif args[0] == "Question":
            self.setIcon(QMessageBox.Icon.Question)
            self.setStandardButtons(QMessageBox.StandardButton.Ok|QMessageBox.StandardButton.Cancel)
        self.setWindowIcon(QIcon("icons/program.svg"))
        self.setWindowTitle(args[0])
        self.resize(DIALOGWIDTH,300)
        self.setText(args[1])
        retval = self.exec()
    
    # def event(self, e):
        # result = QMessageBox.event(self, e)
        # #
        # self.setMinimumHeight(0)
        # self.setMaximumHeight(16777215)
        # self.setMinimumWidth(0)
        # self.setMaximumWidth(16777215)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # # 
        # return result

class searchDialog(QDialog):
    def __init__(self, parent, ret_text, editor):
        super(searchDialog, self).__init__(parent)
        self.parent = parent
        self.editor = editor
        # this dialog is open
        self.parent.search_is_open = 1
        self.setWindowIcon(QIcon("icons/program.svg"))
        self.setWindowTitle("Search...")
        # self.setWindowModality(Qt.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.resize(DIALOGWIDTH, 50)
        #
        vbox = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        vbox.setContentsMargins(5,5,5,5)
        self.setLayout(vbox)
        #
        # self.line_edit = QLineEdit()
        self.line_edit = QComboBox()
        self.line_edit.setEditable(True)
        if ret_text and len(ret_text) < 35:
            # self.line_edit.setText(ret_text)
            if ret_text in self.parent.his_searched:
                self.parent.his_searched.remove(ret_text)
            self.parent.his_searched.insert(0, ret_text)
        self.line_edit.addItems(self.parent.his_searched)
        #
        vbox.addWidget(self.line_edit)
        #
        self.chk_sens = QCheckBox("Case sensitive")
        vbox.addWidget(self.chk_sens)
        #
        self.chk_word = QCheckBox("Word matching")
        vbox.addWidget(self.chk_word)
        #
        self.chk = QCheckBox("Substitutions")
        self.chk.stateChanged.connect(self.on_chk)
        vbox.addWidget(self.chk)
        #
        self.line_edit_sub = QLineEdit()
        self.line_edit_sub.setEnabled(False)
        self.line_edit.currentTextChanged.connect(self.le_cur_changed)
        vbox.addWidget(self.line_edit_sub)
        ### button box
        hbox = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        vbox.addLayout(hbox)
        #
        self.button4 = QPushButton("Previous")
        self.button4.clicked.connect(lambda:self.on_find(0))
        hbox.addWidget(self.button4)
        #
        self.button2 = QPushButton("Next")
        self.button2.clicked.connect(lambda:self.on_find(1))
        hbox.addWidget(self.button2)
        #
        button3 = QPushButton("Close")
        button3.clicked.connect(self.close_)
        hbox.addWidget(button3)
        #
        self.first_found = False
        self.is_reverse = False
        #
        self.Value = 0
        #
        self._curr_pos = None
        self._curr_pos2 = None
        self.show()
        
    def le_cur_changed(self, new_text):
        self.first_found = False
    
    # ftype is 1 next 0 previous
    def on_find(self, ftype):
        line_edit_text = self.line_edit.currentText()
        if line_edit_text == "":
            return
        #
        if not line_edit_text in self.parent.his_searched:
            self.parent.his_searched.insert(0, line_edit_text)
        # substitutions
        if ftype and self.chk.isChecked():
            pline, pcol = self.editor.getCursorPosition()
            ret = self.editor.findFirst(line_edit_text, False, self.chk_sens.isChecked(), self.chk_word.isChecked(), False, True, 0, 0, False)
            while ret:
                self.editor.replace(self.line_edit_sub.text())
                ret = self.editor.findNext()
            # else:
                # self.editor.cancelFind()
            #
            self.editor.setCursorPosition(pline, pcol)
            #
            return
        # find next
        if ftype:
            if self.is_reverse == True:
                self._curr_pos = None
                self._curr_pos2 = None
                self.is_reverse = False
            self._curr_pos = self.editor.getCursorPosition()
            if self._curr_pos2 == None:
                ret = self.editor.findFirst(line_edit_text, False, self.chk_sens.isChecked(), self.chk_word.isChecked(), False, True)
                self._curr_pos2 = self.editor.getCursorPosition()
            else:
                self.editor.findNext()
                self._curr_pos2 = self.editor.getCursorPosition()
            if self._curr_pos == self._curr_pos2:
                ret = retDialogBox("Question", "You have reached the end of the document.\nDo you want to search from the beginning?", self)
                if ret.getValue() == 0:
                    return
                #
                self.editor.setCursorPosition(0,0)
                self.editor.findFirst(line_edit_text, False, self.chk_sens.isChecked(), self.chk_word.isChecked(), False, True)
                self._curr_pos = None
                self._curr_pos2 = None
        # find previous
        else:
            if self.is_reverse == False:
                self._curr_pos = None
                self._curr_pos2 = None
                self.is_reverse = True
            self._curr_pos = self.editor.getCursorPosition()
            if self._curr_pos2 == None:
                ret = self.editor.findFirst(line_edit_text, False, self.chk_sens.isChecked(), self.chk_word.isChecked(), False, False)
                self.editor.findNext()
                self._curr_pos2 = self.editor.getCursorPosition()
            else:
                self.editor.findNext()
                self._curr_pos2 = self.editor.getCursorPosition()
            if self._curr_pos == self._curr_pos2:
                ret = retDialogBox("Question", "You have reached the beginning of the document.\nDo you want to search from the end?", self)
                if ret.getValue() == 0:
                    return
                #
                self.editor.setCursorPosition(self.editor.lines()-1,len(self.editor.text(self.editor.lines()-1))-1)
                self.editor.findFirst(line_edit_text, False, self.chk_sens.isChecked(), self.chk_word.isChecked(), False, False)
                self._curr_pos = None
                self._curr_pos2 = self.editor.getCursorPosition()
            
    def on_chk(self, idx):
        if idx:
            self.line_edit_sub.setEnabled(True)
            self.button4.setEnabled(False)
            self.setWindowTitle("Replace")
            self.button2.setText("Find all")
        else:
            self.line_edit_sub.setEnabled(False)
            self.button4.setEnabled(True)
            self.setWindowTitle("Search...")
            self.button2.setText("Next")
        
    
    def getValue(self):
        return self.Value
    
    def close_(self):
        self.parent.search_is_open = 0
        self.close()


# dialog - return of the choise yes or no
class retDialogBox(QMessageBox):
    def __init__(self, *args):
        super(retDialogBox, self).__init__(args[-1])
        self.setWindowIcon(QIcon("icons/program.svg"))
        self.setWindowTitle(args[0])
        if args[0] == "Info":
            self.setIcon(QMessageBox.Icon.Information)
        elif args[0] == "Error":
            self.setIcon(QMessageBox.Icon.Critical)
        elif args[0] == "Question":
            self.setIcon(QMessageBox.Icon.Question)
        self.resize(DIALOGWIDTH, 100)
        self.setText(args[1])
        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        #
        self.Value = None
        retval = self.exec()
        #
        if retval == QMessageBox.StandardButton.Yes:
            self.Value = 1
        elif retval == QMessageBox.StandardButton.Cancel:
            self.Value = 0
    
    def getValue(self):
        return self.Value
    
    # def event(self, e):
        # result = QMessageBox.event(self, e)
        # #
        # self.setMinimumHeight(0)
        # self.setMaximumHeight(16777215)
        # self.setMinimumWidth(0)
        # self.setMaximumWidth(16777215)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # #
        # textEdit = self.findChild(QTextEdit)
        # if textEdit != None :
            # textEdit.setMinimumHeight(0)
            # textEdit.setMaximumHeight(16777215)
            # textEdit.setMinimumWidth(0)
            # textEdit.setMaximumWidth(16777215)
            # textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # #
        # return result

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    IS_SINGLEINSTANCE = 1
    if SINGLEINSTANCE:
        if not QDBusConnection.sessionBus().isConnected():
            IS_SINGLEINSTANCE = 0
    
    if PROG_REGISTERED:
        # exit if no file passed
        if len(sys.argv) == 1 or sys.argv[1] in ["-p", "-b", "-j", "-t", "-a"]:
            sys.exit()
        #
        iface = QDBusInterface('org.QtDBus.pyeditor6', '/', '', QDBusConnection.sessionBus())
        #
        if iface.isValid() and len(sys.argv) > 1:
            
            for el in sys.argv[1:]:
                if el not in ["-p", "-b", "-j", "-t", "-a"]:
                    _file = el
                    break
            
            if _file:
                _file = os.path.realpath(_file)
                # msg = iface.call('ping', sys.argv[1] if len(sys.argv) > 1 else "")
                msg = iface.call('ping', _file)
                reply = QDBusReply(msg)
                if reply.isValid():
                    if reply.value() == _file:
                        sys.exit()
    
    if GUISTYLE:
        QApplication.setStyle(QStyleFactory.create(GUISTYLE))
    # # Now use a palette to switch to dark colors
    # if DARKTHEME:
        # # TEXTCOLOR = QColor("#C5C8C6")
        # # TEXTCOLOR = QColor("#969896")
        # TEXTCOLOR = QColor("#ffffff")
        # palette = QPalette()
        # palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        # palette.setColor(QPalette.ColorRole.WindowText, TEXTCOLOR)
        # palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        # palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        # palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0,0,0))
        # palette.setColor(QPalette.ColorRole.ToolTipText, TEXTCOLOR)
        # palette.setColor(QPalette.ColorRole.Text, TEXTCOLOR)
        # palette.setColor(QPalette.ColorRole.Button, QColor(83, 83, 83))
        # palette.setColor(QPalette.ColorRole.ButtonText, TEXTCOLOR)
        # palette.setColor(QPalette.ColorRole.BrightText, QColor(255,0,0))
        # palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        # palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        # palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0,0,0))
        # app.setPalette(palette)
    # # else:
        # # TEXTCOLOR = QColor("#ffffff")
        # # palette = QPalette()
        # # palette.setColor(QPalette.ColorRole.Text, TEXTCOLOR)
        # # palette.setColor(QPalette.ColorRole.WindowText, TEXTCOLOR)
        # # palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        # # palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        
        # # app.setPalette(palette)
    #
    myGUI = CustomMainWindow()
    sys.exit(app.exec())
    
########################
