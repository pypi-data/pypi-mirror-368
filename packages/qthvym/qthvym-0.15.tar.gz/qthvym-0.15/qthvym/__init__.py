"""QT5 UI Elements For HVYM, By: Fibo Metavinci"""

__version__ = "0.15"

from PyQt5.QtWidgets import QApplication, QMainWindow, QSplashScreen, QLabel, QGridLayout, QWidget, QCheckBox, QFormLayout, QSystemTrayIcon, QComboBox, QTextEdit, QLineEdit, QDialogButtonBox, QSpacerItem, QSizePolicy, QMenu, QAction, QStyle, qApp, QVBoxLayout, QPushButton, QDialog, QDesktopWidget, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QImage
from qthvym.passwordedit import PasswordEdit
from qthvym.ui_helpers import (
    prepare_dialog_for_dynamic_sizing,
    center_on_screen,
    apply_app_stylesheet_if_env,
)
from pathlib import Path
import pyperclip
import tempfile
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from PIL import Image, ImageDraw
import copy
import sys
import os

BRAND = "HEAVYMETA®"
VERSION = "0.01"
ABOUT = f"""
Command Line Interface for {BRAND} Standard NFT Data
Version: {VERSION}
ALL RIGHTS RESERVED 2024
"""
HOME = os.path.expanduser('~')
FILE_PATH = Path(__file__).parent 
HVYM_LOGO_IMG = os.path.join(FILE_PATH,'data', 'logo.png')
HVYM_IMG = os.path.join(FILE_PATH,'data', 'hvym.png')
XRO_LOGO_IMG = os.path.join(FILE_PATH,'data', 'xro_logo.png')
OPUS_LOGO_IMG = os.path.join(FILE_PATH,'data', 'opus_logo.png')
STELLAR_LOGO_IMG = os.path.join(FILE_PATH,'data', 'stellar_logo.png')
ICP_LOGO_IMG = os.path.join(FILE_PATH,'data', 'dfinity_logo.png')
DEFAULT_WIDTH = 400
HVYM_BG_RGB = (152, 49, 74)
HVYM_FG_RGB = (175, 232, 197)
XRO_BG_RGB = (249, 194, 10)
XRO_FG_RGB = (127, 36, 103)
OPUS_BG_RGB = (249, 194, 10)
OPUS_FG_RGB = (119, 36, 127)
STELLAR_BG_RGB = (0, 0, 0)
STELLAR_FG_RGB = (236, 240, 243)
ICP_BG_RGB = (136, 100, 212)
ICP_FG_RGB = (70, 14, 189)
APP = QApplication(sys.argv)
apply_app_stylesheet_if_env()

MIN_WIDTH = 550
MIN_HEIGHT = 450

def basic_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(image_factory=StyledPilImage, 
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(back_color=HVYM_BG_RGB, front_color=HVYM_FG_RGB),
        embeded_image_path=HVYM_IMG)
    qr = None
    with tempfile.NamedTemporaryFile(suffix='.png', delete=True) as f:
        img.save(f, format='PNG') 
        qr = QImage(f.name)

    return qr


def custom_qr_code(data, cntrImg, back_color=HVYM_BG_RGB, front_color=HVYM_FG_RGB):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(image_factory=StyledPilImage, 
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(back_color=back_color, front_color=front_color),
        embeded_image_path=cntrImg)
    qr = None
    with tempfile.NamedTemporaryFile(suffix='.png', delete=True) as f:
        img.save(f, format='PNG') 
        qr = QImage(f.name)

    return qr


class MsgDialog(QDialog):
    def __init__(self, msg, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)

        QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        layout = QVBoxLayout()
        message = QLabel(msg)
        message.setWordWrap(True)
        space = QLabel(' ')
        layout.addWidget(message)
        layout.addWidget(space)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


class IconMsgBox(QDialog):
    def __init__(self, msg, icon=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)

        QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        layout = QVBoxLayout()
        message = QLabel(msg)
        message.setWordWrap(True)
        img = None
        if icon != None:
            img = QLabel()
            img.setPixmap(QPixmap(icon).scaledToHeight(32, Qt.SmoothTransformation))
        space = QLabel(' ')
        if img:
             layout.addWidget(img, alignment=Qt.AlignLeft)
        layout.addWidget(message, alignment=Qt.AlignLeft)
        layout.addWidget(space)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        prepare_dialog_for_dynamic_sizing(self, layout, allow_resize=True)


class ChoiceDialog(QDialog):
    def __init__(self, msg, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        message = QLabel(msg)
        message.setWordWrap(True)
        space = QLabel(' ')
        layout.addWidget(message)
        layout.addWidget(space)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


class IconChoiceMsgBox(QDialog):
    def __init__(self, msg, icon=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        message = QLabel(msg)
        message.setWordWrap(True)
        img = None
        if icon != None:
            img = QLabel()
            img.setPixmap(QPixmap(icon).scaledToHeight(32, Qt.SmoothTransformation))
        space = QLabel(' ')
        if img:
             layout.addWidget(img, alignment=Qt.AlignLeft)
        layout.addWidget(message, alignment=Qt.AlignLeft)
        layout.addWidget(space)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


class OptionsDialog(QDialog):
    def __init__(self, msg, options, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)
        self.combobox = QComboBox()

        for option in options:
              self.combobox.addItem(option)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        message = QLabel(msg)
        message.setWordWrap(True)
        space = QLabel(' ')
        layout.addWidget(message)
        layout.addWidget(self.combobox)
        layout.addWidget(space)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def value(self):
          return self.combobox.currentText()

class IconOptionsMsgBox(QDialog):
    def __init__(self, msg, options, icon=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)

        self.combobox = QComboBox()

        for option in options:
              self.combobox.addItem(option)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        message = QLabel(msg)
        message.setWordWrap(True)
        img = None
        if icon != None:
            img = QLabel()
            img.setPixmap(QPixmap(icon).scaledToHeight(32, Qt.SmoothTransformation))
        space = QLabel(' ')
        if img:
             layout.addWidget(img, alignment=Qt.AlignLeft)
             
        layout.addWidget(message, alignment=Qt.AlignLeft)
        layout.addWidget(self.combobox)
        layout.addWidget(space)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def value(self):
          return self.combobox.currentText()
    

class TextEditDialog(QDialog):
    def __init__(self, msg, defaultTxt=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QFormLayout()
        space = QLabel(' ')
        self.setLayout(layout)
        message = QLabel(msg)
        message.setWordWrap(True)
        layout.addRow(message)
        self.text_edit = QTextEdit(self)
        layout.addRow(self.text_edit)
        layout.addRow(space)
        layout.addRow(self.buttonBox)

        if defaultTxt != None:
              self.text_edit.setPlainText(defaultTxt)


class IconEditTextMsgBox(QDialog):
    def __init__(self, msg, defaultTxt=None, icon=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QFormLayout()
        self.setLayout(layout)
        message = QLabel(msg)
        message.setWordWrap(True)
        img = None
        if icon != None:
            img = QLabel()
            img.setPixmap(QPixmap(icon).scaledToHeight(32, Qt.SmoothTransformation))
        space = QLabel(' ')
        if img:
             layout.addRow(img)
        layout.addRow(message)
        self.text_edit = QTextEdit(self)
        layout.addRow(self.text_edit)
        layout.addRow(space)
        layout.addRow(self.buttonBox)

        if defaultTxt != None:
              self.text_edit.setPlainText(defaultTxt)

    def value(self):
        return self.text_edit.toPlainText()
    

class IconCopyTextMsgBox(QDialog):
    def __init__(self, msg, defaultTxt=None, icon=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)

        self.copyBtn = QPushButton("Copy")
        self.okBtn = QPushButton("OK")
        self.copyBtn.clicked.connect(self.copy)
        self.okBtn.clicked.connect(self.close)

        layout = QFormLayout()
        self.setLayout(layout)
        message = QLabel(msg)
        message.setWordWrap(True)
        img = None
        if icon != None:
            img = QLabel()
            img.setPixmap(QPixmap(icon).scaledToHeight(32, Qt.SmoothTransformation))
        space = QLabel(' ')
        if img:
             layout.addRow(img)
        layout.addRow(message)
        self.text_edit = QTextEdit(self)
        layout.addRow(self.text_edit)
        layout.addRow(space)
        layout.addRow(self.copyBtn)
        layout.addRow(self.okBtn)

        if defaultTxt != None:
              self.text_edit.setPlainText(defaultTxt)

    def value(self):
        return self.text_edit.toPlainText()
    
    def copy(self):
         pyperclip.copy(self.text_edit.toPlainText())


class IconUserTextMsgBox(QDialog):
    def __init__(self, msg, icon=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QFormLayout()
        self.setLayout(layout)
        message = QLabel(msg)
        message.setWordWrap(True)
        self.acct_lbl = QLabel("Account")
        img = None
        if icon != None:
            img = QLabel()
            img.setPixmap(QPixmap(icon).scaledToHeight(32, Qt.SmoothTransformation))
        space = QLabel(' ')
        if img:
             layout.addRow(img)
        layout.addRow(message)
        self.acct = QLineEdit(self)
        self.pw = PasswordEdit(self)
        layout.addRow(self.acct_lbl)
        layout.addRow(self.acct)
        layout.addRow(space)
        layout.addRow(self.buttonBox)

    def value(self):
        return self.acct.text()


class IconPasswordTextMsgBox(QDialog):
    def __init__(self, msg, icon=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QFormLayout()
        self.setLayout(layout)
        prepare_dialog_for_dynamic_sizing(self, layout, allow_resize=True)
        message = QLabel(msg)
        message.setWordWrap(True)
        self.pw_lbl = QLabel("Password")
        img = None
        if icon != None:
            img = QLabel()
            img.setPixmap(QPixmap(icon).scaledToHeight(32, Qt.SmoothTransformation))
        space = QLabel(' ')
        if img:
             layout.addRow(img)
        layout.addRow(message)
        self.pw = PasswordEdit(self)
        layout.addRow(self.pw_lbl)
        layout.addRow(self.pw)
        layout.addRow(space)
        layout.addRow(self.buttonBox)

    def value(self):
        return self.pw.text()
    

class IconUserPasswordTextMsgBox(QDialog):
    def __init__(self, msg, defaultTxt=None, icon=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QFormLayout()
        self.setLayout(layout)
        message = QLabel(msg)
        message.setWordWrap(True)
        self.acct_lbl = QLabel("Account")
        self.pw_lbl = QLabel("Password")
        img = None
        if icon != None:
            img = QLabel()
            img.setPixmap(QPixmap(icon).scaledToHeight(32, Qt.SmoothTransformation))
        space = QLabel(' ')

        if img:
             layout.addRow(img)
        
        layout.addRow(message)

        self.acct = QLineEdit(self)
        self.pw = PasswordEdit(self)
        layout.addRow(self.acct_lbl)
        layout.addRow(self.acct)
        layout.addRow(self.pw_lbl)
        layout.addRow(self.pw)
        layout.addRow(space)
        layout.addRow(self.buttonBox)

        if defaultTxt != None:
              self.acct.setText(defaultTxt)

    def value(self):
        return {'user': self.acct.text(), 'pw': self.pw.text()}
    

class LineEditDialog(QDialog):
    def __init__(self, msg, defaultTxt=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QFormLayout()
        self.setLayout(layout)
        message = QLabel(msg)
        layout.addRow(message)
        self.text_edit = QLineEdit(self)
        layout.addRow(self.text_edit)
        layout.addRow(self.buttonBox)

        if defaultTxt != None:
              self.text_edit.setText(defaultTxt)

    def value(self):
         return self.edit_text.text()


class IconLineEditMsgBox(QDialog):
    def __init__(self, msg, defaultTxt=None, icon=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QFormLayout()
        self.setLayout(layout)
        message = QLabel(msg)
        img = None
        if icon != None:
            img = QLabel()
            img.setPixmap(QPixmap(icon).scaledToHeight(32, Qt.SmoothTransformation))
        space = QLabel(' ')
        if img:
             layout.addWidget(img)
        layout.addRow(message)
        self.text_edit = QLineEdit(self)
        layout.addRow(self.text_edit)
        layout.addRow(self.buttonBox)

        if defaultTxt != None:
              self.text_edit.setText(defaultTxt)

    def value(self):
        return self.text_edit.text()

class IconLineCopyMsgBox(QDialog):
    def __init__(self, msg, defaultTxt=None, icon=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)

        self.copyBtn = QPushButton("Copy")
        self.okBtn = QPushButton("OK")
        self.copyBtn.clicked.connect(self.copy)
        self.okBtn.clicked.connect(self.close)

        layout = QFormLayout()
        self.setLayout(layout)
        message = QLabel(msg)
        message.setWordWrap(True)
        img = None
        if icon != None:
            img = QLabel()
            img.setPixmap(QPixmap(icon).scaledToHeight(32, Qt.SmoothTransformation))
        space = QLabel(' ')
        if img:
             layout.addWidget(img)
        layout.addRow(message)
        self.text_edit = QLineEdit(self)
        layout.addRow(self.text_edit)
        layout.addRow(space)
        layout.addRow(self.copyBtn)
        layout.addRow(self.okBtn)

        if defaultTxt != None:
              self.text_edit.setText(defaultTxt)

    def value(self):
        return self.text_edit.text()

    def copy(self):
         pyperclip.copy(self.text_edit.text())

class ImageMsgBox(QDialog):
    def __init__(self, msg, img, width=DEFAULT_WIDTH, icon=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)

        layout = QFormLayout()
        self.setLayout(layout)
        message = QLabel(msg)
        message.setWordWrap(True)
        ico = None
        if icon is not None:
            ico = QLabel()
            ico.setPixmap(QPixmap(str(icon)).scaledToHeight(32, Qt.SmoothTransformation))
        space = QLabel(' ')
        if ico:
            layout.addWidget(ico)

        imgLabel = QLabel()
        imgLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        imgLabel.setScaledContents(False)

        # Robust image load (absolute path + QImageReader)
        try:
            from PyQt5.QtGui import QImageReader
            from pathlib import Path as _Path
            img_path = _Path(str(img))
            if not img_path.is_absolute():
                img_path = (_Path.cwd() / img_path).resolve()
            reader = QImageReader(str(img_path))
            if reader.canRead():
                image = reader.read()
                pix = QPixmap.fromImage(image)
            else:
                pix = QPixmap(str(img_path))
        except Exception:
            pix = QPixmap(str(img))

        if not pix.isNull():
            pix = pix.scaledToWidth(width, Qt.SmoothTransformation)
            imgLabel.setPixmap(pix)
        else:
            imgLabel.setText(f"Failed to load image: {img}")

        layout.addWidget(message)
        layout.addRow(space)
        layout.addWidget(imgLabel)
        prepare_dialog_for_dynamic_sizing(self, layout, allow_resize=True)

    def value(self):
        return None

class QrMsgBox(QDialog):
    def __init__(self, msg, data, width=DEFAULT_WIDTH, icon=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)

        layout = QFormLayout()
        self.setLayout(layout)
        message = QLabel(msg)
        message.setWordWrap(True)
        ico = None
        if icon:
            ico = QLabel()
            ico.setPixmap(QPixmap(icon).scaledToHeight(32, Qt.SmoothTransformation))
        space = QLabel(' ')
        if ico:
            layout.addWidget(ico)
        qr_label = QLabel()
        qr_code_img = basic_qr_code(data) 
        pixmap = QPixmap.fromImage(qr_code_img).scaledToWidth(width, Qt.SmoothTransformation)
        qr_label.setPixmap(pixmap)
        layout.addWidget(message)
        layout.addRow(space)
        layout.addWidget(qr_label)

    def value(self):
        return None
    
class QrCopyMsgBox(QDialog):
    def __init__(self, msg, data, width=DEFAULT_WIDTH, icon=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)
        self.copyBtn = QPushButton("Copy")
        self.okBtn = QPushButton("OK")
        self.copyBtn.clicked.connect(self.copy)
        self.okBtn.clicked.connect(self.close)

        layout = QFormLayout()
        self.setLayout(layout)
        message = QLabel(msg)
        message.setWordWrap(True)
        ico = None
        if icon:
            ico = QLabel()
            ico.setPixmap(QPixmap(icon).scaledToHeight(32, Qt.SmoothTransformation))
        space = QLabel(' ')
        if ico:
            layout.addWidget(ico)
        qr_label = QLabel()
        qr_code_img = basic_qr_code(data) 
        pixmap = QPixmap.fromImage(qr_code_img).scaledToWidth(width, Qt.SmoothTransformation)
        qr_label.setPixmap(pixmap)
        self.text_edit = QLineEdit(self)
        self.text_edit.setText(data)
        layout.addWidget(message)
        layout.addRow(space)
        layout.addWidget(qr_label)
        layout.addRow(self.text_edit)
        layout.addRow(space)
        layout.addRow(self.copyBtn)
        layout.addRow(self.okBtn)

    def value(self):
        return None
    
    def copy(self):
         pyperclip.copy(self.text_edit.text())
         QApplication.processEvents() 


class CustomQrMsgBox(QDialog):
    def __init__(self, msg, data, width=DEFAULT_WIDTH, cntrImg=HVYM_IMG, back_color=HVYM_BG_RGB, front_color=HVYM_FG_RGB, id=None, icon=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)
        self.needStyle = []
        self.needStyle.append(self)
        layout = QFormLayout()
        self.setLayout(layout)
        message = QLabel(msg)
        message.setWordWrap(True)
        self.needStyle.append(message)
        ico = None
        if icon:
            ico = QLabel()
            ico.setPixmap(QPixmap(icon).scaledToHeight(32, Qt.SmoothTransformation))

        if ico:
            layout.addWidget(ico)
        qr_label = QLabel()
        self.needStyle.append(qr_label)
        qr_code_img = custom_qr_code(data, cntrImg, front_color, back_color)
        pixmap = QPixmap.fromImage(qr_code_img).scaledToWidth(width, Qt.SmoothTransformation)
        qr_label.setPixmap(pixmap)

        if id != None:
            for w in self.needStyle:
                w.setObjectName(id)

        layout.addWidget(message)
        layout.addWidget(qr_label)

    def value(self):
        return None
    
    
class CustomQrCopyMsgBox(QDialog):
    def __init__(self, msg, data, width=DEFAULT_WIDTH, cntrImg=HVYM_IMG, back_color=HVYM_BG_RGB, front_color=HVYM_FG_RGB, id=None, icon=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(BRAND)
        self.needStyle = []
        self.needStyle.append(self)
        self.copyBtn = QPushButton("Copy")
        self.needStyle.append(self.copyBtn)
        self.okBtn = QPushButton("OK")
        self.needStyle.append(self.okBtn)
        self.copyBtn.clicked.connect(self.copy)
        self.okBtn.clicked.connect(self.close)
        layout = QFormLayout()
        self.setLayout(layout)
        message = QLabel(msg)
        message.setWordWrap(True)
        self.needStyle.append(message)
        ico = None
        if icon:
            ico = QLabel()
            ico.setPixmap(QPixmap(icon).scaledToHeight(32, Qt.SmoothTransformation))

        if ico:
            layout.addWidget(ico)

        space = QLabel(' ')
        self.needStyle.append(space)
        qr_label = QLabel()
        self.needStyle.append(qr_label)
        self.text_edit = QLineEdit(self)
        self.text_edit.setText(data)
        self.needStyle.append(self.text_edit)
        qr_code_img = custom_qr_code(data, cntrImg, front_color, back_color)
        pixmap = QPixmap.fromImage(qr_code_img).scaledToWidth(width, Qt.SmoothTransformation)
        qr_label.setPixmap(pixmap)

        if id != None:
            for w in self.needStyle:
                w.setObjectName(id)

        layout.addRow(message)
        layout.addRow(qr_label)
        layout.addRow(self.text_edit)
        layout.addRow(space)
        layout.addRow(self.copyBtn)
        layout.addRow(self.okBtn)

    def value(self):
        return None
    
    def copy(self):
         pyperclip.copy(self.text_edit.text())


class FileDialog(QFileDialog):
    def __init__(self, msg, filterTypes=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(msg)
        self.setDirectory(HOME)
        self.setFileMode(QFileDialog.AnyFile)
        if filterTypes != None:
            self.setNameFilters(filterTypes)

    def value(self):
         return self.selectedFiles()
    
    
class FolderDialog(QFileDialog):
    def __init__(self, msg, parent=None):
        super().__init__(parent)
        self.setWindowTitle(msg)
        self.setDirectory(HOME)
        self.setFileMode(QFileDialog.DirectoryOnly)

    def value(self):
         return self.getExistingDirectory(self, 'Select Folder')
   

class HVYMMainWindow(QMainWindow):
    """
         App for user input
         Used as main data conduit
         passing output from dialogs
         to this main window
    """
    def __init__(self):
      QMainWindow.__init__(self)
      self.FILE_PATH = Path(__file__).parent
      self.HVYM_IMG = os.path.join(self.FILE_PATH, 'data', 'hvym.png')
      self.HVYM_LOGO_IMG = os.path.join(self.FILE_PATH, 'data', 'logo.png')
      self.WIN_ICON = QIcon(self.HVYM_IMG)
      self.STYLE_SHEET = os.path.join(self.FILE_PATH, 'data', 'style.qss')
      self.value = None
      self.setMinimumSize(QSize(80, 80))  # Set sizes
      self.setWindowTitle("System Tray Application")  # Set a title
      # Create a central widget
      central_widget = QWidget(self)
      # Set the central widget
      self.setCentralWidget(central_widget)
      label = QLabel("", self)
      label.setPixmap(QPixmap(self.HVYM_LOGO_IMG))
      label.adjustSize()

      self.setWindowIcon(self.WIN_ICON)
      self.setWindowFlag(Qt.FramelessWindowHint)
      self.setStyleSheet(Path(str(self.STYLE_SHEET)).read_text())
      self._center()
      self.hide()

    def _center(self):
        center_on_screen(self)

    def Close(self):
          self.close()

    def splashScreen(self, message=None, duration = 3000):
      splash_pix = QPixmap( str(self.HVYM_IMG) )
      splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
      if message is not None:
            align = Qt.Alignment(Qt.AlignBottom |
                                    Qt.AlignRight |
                                    Qt.AlignAbsolute)
            splash.showMessage(message, align)
      splash.show()
      QTimer.singleShot(duration, APP.quit)
      sys.exit(APP.exec_())
   
    def MessagePopup(self, message):
          popup = MsgDialog(message, self)
          popup.setWindowIcon(self.WIN_ICON)
          popup.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
          popup.setMaximumSize(MIN_WIDTH+50, MIN_HEIGHT+75)
          popup.exec()
          self.close()

    def IconMessagePopup(self, message, icon):
          popup = IconMsgBox(message, icon, self)
          popup.setWindowIcon(self.WIN_ICON)
          center_on_screen(popup)
          popup.exec()
          self.close()

    def ChoicePopup(self, message):
          result = 'CANCEL'
          popup = ChoiceDialog(message, self)
          popup.setWindowIcon(self.WIN_ICON)
          popup.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
          popup.setMaximumSize(MIN_WIDTH+50, MIN_HEIGHT+75)
          if popup.exec():
                result = 'OK'
          self.value = result
          self.close()

          return result

    def IconChoicePopup(self, message, icon):
          result = 'CANCEL'
          popup = IconChoiceMsgBox(message, icon, self)
          popup.setWindowIcon(self.WIN_ICON)
          popup.setMinimumSize(MIN_WIDTH-50, MIN_HEIGHT-100)
          popup.setMaximumSize(MIN_WIDTH+50, MIN_HEIGHT+75)
          if popup.exec():
                result = 'OK'
          self.value = result
          self.close()

          return result

    def OptionsPopup(self, message, options):
          result = None
          popup = OptionsDialog(message, options, self)
          popup.setWindowIcon(self.WIN_ICON)
          popup.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
          popup.setMaximumSize(MIN_WIDTH+50, MIN_HEIGHT+75)
          if popup.exec():
                result = popup.value()
          self.value = result
          self.close()

          return result
    
    def IconOptionsPopup(self, message, options, icon):
          result = None
          popup = IconOptionsMsgBox(message, options, icon, self)
          popup.setWindowIcon(self.WIN_ICON)
          popup.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
          popup.setMaximumSize(MIN_WIDTH+50, MIN_HEIGHT+75)
          if popup.exec():
                result = popup.value()
          self.value = result
          self.close()

          return result
    
    def EditTextPopup(self, message, defaultText=None):
          result = None
          popup = TextEditDialog(message, defaultText, self)
          popup.setWindowIcon(self.WIN_ICON)
          if popup.exec():
                result = popup.value()
          self.value = result
          self.close()

          return result
    
    def IconEditTextPopup(self, message, defaultText=None, icon=None):
          result = None
          popup = IconEditTextMsgBox(message, defaultText, icon, self)
          popup.setWindowIcon(self.WIN_ICON)
          if popup.exec():
                result = popup.value()
          self.value = result
          self.close()

          return result

    def IconCopyTextPopup(self, message, defaultText=None, icon=None):
          result = None
          popup = IconCopyTextMsgBox(message, defaultText, icon, self)
          popup.setWindowIcon(self.WIN_ICON)
          popup.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
          popup.setMaximumSize(MIN_WIDTH+50, MIN_HEIGHT+75)
          if popup.exec():
                result = popup.value()
          self.value = result
          self.close()

          return result
    
    def EditLinePopup(self, message, defaultText=None):
          result = None
          popup = LineEditDialog(message, defaultText, self)
          popup.setWindowIcon(self.WIN_ICON)
          if popup.exec():
                result = popup.value()
          self.value = result
          self.close()

          return result
    
    def IconEditLinePopup(self, message, defaultText=None, icon=None):
          result = None
          popup = IconLineEditMsgBox(message, defaultText, icon, self)
          popup.setWindowIcon(self.WIN_ICON)
          if popup.exec():
                result = popup.value()
          self.value = result
          self.close()

          return result

    def IconCopyLinePopup(self, message, defaultText=None, icon=None):
          result = None
          popup = IconLineCopyMsgBox(message, defaultText, icon, self)
          popup.setWindowIcon(self.WIN_ICON)
          popup.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
          popup.setMaximumSize(MIN_WIDTH+50, MIN_HEIGHT)
          if popup.exec():
                result = popup.value()
          self.value = result
          self.close()

          return result

    def IconUserPopup(self, message, icon=None):
         result = None
         popup = IconUserTextMsgBox(message, icon, self)
         popup.setWindowIcon(self.WIN_ICON)
         popup.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
         popup.setMaximumSize(MIN_WIDTH+50, MIN_HEIGHT+75)
         if popup.exec():
                result = popup.value()
         self.value = result
         self.close()

         return result

    def IconPasswordPopup(self, message, icon=None):
         result = None
         popup = IconPasswordTextMsgBox(message, icon, self)
         popup.setWindowIcon(self.WIN_ICON)
         center_on_screen(popup)
         if popup.exec():
                result = popup.value()
         self.value = result
         self.close()

         return result

    def IconUserPasswordPopup(self, message, defaultText=None, icon=None):
         result = None
         popup = IconUserPasswordTextMsgBox(message, defaultText, icon, self)
         popup.setWindowIcon(self.WIN_ICON)
         popup.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
         popup.setMaximumSize(MIN_WIDTH+50, MIN_HEIGHT+75)
         if popup.exec():
                result = popup.value()
         self.value = result
         self.close()

         return result

    def IconImagePopup(self, message, img, width=DEFAULT_WIDTH, icon=None):
          result = None
          popup = ImageMsgBox(message, img, width, icon, self)
          popup.setWindowIcon(self.WIN_ICON)
          if popup.exec():
                result = popup.value()
          self.value = result
          self.close()

          return result

    def IconQrPopup(self, message, data, width=DEFAULT_WIDTH, icon=None):
          result = None
          popup = QrMsgBox(message, data, width, icon, self)
          popup.setWindowIcon(self.WIN_ICON)
          if popup.exec():
                result = popup.value()
          self.value = result
          self.close()

          return result
    
    def IconCopyQrPopup(self, message, data, width=DEFAULT_WIDTH, icon=None):
          result = None
          popup = QrCopyMsgBox(message, data, width, icon, self)
          popup.setWindowIcon(self.WIN_ICON)
          if popup.exec():
                result = popup.value()
          self.value = result
          self.close()

          return result

    def IconCustomQrPopup(self, message, data, width=DEFAULT_WIDTH, cntrImg=HVYM_IMG, back_color=HVYM_BG_RGB, front_color=HVYM_FG_RGB, id=None, icon=None):
        result = None
        popup = CustomQrMsgBox(message, data, width, cntrImg, back_color, front_color, id, icon, self)
        popup.setWindowIcon(self.WIN_ICON)
        if popup.exec():
            result = popup.value()
        self.value = result
        self.close()

        return result
    
    def IconCustomQrCopyPopup(self, message, data, width=DEFAULT_WIDTH, cntrImg=HVYM_IMG, back_color=HVYM_BG_RGB, front_color=HVYM_FG_RGB, id=None, icon=None):
        result = None
        popup = CustomQrCopyMsgBox(message, data, width, cntrImg, back_color, front_color, id, icon, self)
        popup.setWindowIcon(self.WIN_ICON)
        if popup.exec():
            result = popup.value()
        self.value = result
        self.close()

        return result

    def FilePopup(self, msg, filters=None):
         result = None
         popup = FileDialog(msg, filters, self)
         popup.setWindowIcon(self.WIN_ICON)
         if popup.exec():
              result = popup.value()
         self.value = result
         self.close()

         return result
    
    def FolderPopup(self, msg):
         result = None
         popup = FolderDialog(msg, self)
         popup.setWindowIcon(self.WIN_ICON)
         if popup:
              result = popup.value()
         self.value = result
         self.close()

         return result
        

class HVYMInteraction(HVYMMainWindow):
    """
         Handler class for user interactions
    """
    def __init__(self):
      HVYMMainWindow.__init__(self)
      self.call = None
      self.value = None

    def splash(self, msg, duration = 3000):
      self.splashScreen(msg, duration)

    def msg_popup(self, msg, icon=str(HVYM_LOGO_IMG)):
      if icon == None:
           self.call = self.MessagePopup(msg)
      else:
           self.call = self.IconMessagePopup(msg, icon)

    def choice_popup(self, msg, icon=str(HVYM_LOGO_IMG)):
      if icon == None:
           self.call = self.ChoicePopup(msg)
      else:
           self.call = self.IconChoicePopup(msg, icon)

    def options_popup(self, msg, options, icon=str(HVYM_LOGO_IMG)):
      if icon == None:
           self.call = self.OptionsPopup(msg, options)
      else:
           self.call = self.IconOptionsPopup(msg, options, icon)
      
    def edit_line_popup(self, msg, defaultText=None, icon=str(HVYM_LOGO_IMG)):
      if icon == None:
           self.call = self.EditLinePopup(msg, defaultText)
      else:
           self.call = self.IconEditLinePopup(msg, defaultText, icon)

    def user_popup(self, msg, icon=str(HVYM_LOGO_IMG)):
      self.call = self.IconUserPopup(msg, icon)

    def password_popup(self, msg, icon=str(HVYM_LOGO_IMG)):
      self.call = self.IconPasswordPopup(msg, icon)

    def user_password_popup(self, msg, defaultText=None, icon=str(HVYM_LOGO_IMG)):
      self.call = self.IconUserPasswordPopup(msg, defaultText, icon)
      
    def copy_line_popup(self, msg, defaultText=None, icon=str(HVYM_LOGO_IMG)):
      self.call = self.IconCopyLinePopup(msg, defaultText, icon)

    def copy_text_popup(self, msg, defaultText=None, icon=str(HVYM_LOGO_IMG)):
      self.call = self.IconCopyTextPopup(msg, defaultText, icon) 

    def file_select_popup(self, msg, filters=None, icon=str(HVYM_LOGO_IMG)):
      self.call = self.FilePopup(msg, filters)

    def folder_select_popup(self, msg, icon=str(HVYM_LOGO_IMG)):
      self.call = self.FolderPopup(msg)

    def img_popup(self, msg, img, width=DEFAULT_WIDTH, icon=str(HVYM_LOGO_IMG)):
      self.call = self.IconImagePopup(msg, img, width, icon)

    def qr_popup(self, msg, data, width=DEFAULT_WIDTH, icon=str(HVYM_LOGO_IMG)):
      self.call = self.IconQrPopup(msg, data, width, icon)

    def qr_copy_popup(self, msg, data, width=DEFAULT_WIDTH, icon=str(HVYM_LOGO_IMG)):
      self.call = self.IconCopyQrPopup(msg, data, width, icon)

    def custom_qr_popup(self, msg, data, width=DEFAULT_WIDTH, cntrImg=HVYM_IMG, back_color=HVYM_BG_RGB, front_color=HVYM_FG_RGB, id=None, icon=str(HVYM_LOGO_IMG)):
      self.call = self.IconCustomQrPopup(msg, data, width, cntrImg, back_color, front_color, icon)

    def xro_qr_popup(self, msg, data):
      self.setObjectName('XRO_QR')
      self.call = self.IconCustomQrCopyPopup(msg, data, DEFAULT_WIDTH, XRO_LOGO_IMG, XRO_BG_RGB, XRO_FG_RGB, 'XRO_QR')

    def opus_qr_popup(self, msg, data):
      self.setObjectName('OPUS_QR')
      self.call = self.IconCustomQrCopyPopup(msg, data, DEFAULT_WIDTH, OPUS_LOGO_IMG, OPUS_BG_RGB, OPUS_FG_RGB, 'OPUS_QR')

    def stellar_qr_popup(self, msg, data):
      self.setObjectName('STELLAR_QR')
      self.call = self.IconCustomQrCopyPopup(msg, data, DEFAULT_WIDTH, STELLAR_LOGO_IMG, STELLAR_BG_RGB, STELLAR_FG_RGB, 'STELLAR_QR')

    def icp_qr_popup(self, msg, data):
      self.call = self.IconCustomQrCopyPopup(msg, data, DEFAULT_WIDTH, ICP_LOGO_IMG, ICP_BG_RGB, ICP_FG_RGB, 'ICP_QR')

      