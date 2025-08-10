from pathlib import Path
import sys

from PyQt5 import QtWidgets, QtCore, QtGui


def _resolve_asset_path(file_name: str) -> Path:
    """Resolve icon path for both dev and PyInstaller (_MEIPASS) modes."""
    base_dir = getattr(sys, "_MEIPASS", None)
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent
    else:
        base_dir = Path(base_dir) / "qthvym"
    return base_dir / "data" / "passwordedit" / file_name


class PasswordEdit(QtWidgets.QWidget):
    """
    A composite password entry widget implemented with pure PyQt5.

    Structure:
    - QLineEdit for text input (default echo mode: Password)
    - QToolButton to toggle between hidden/visible states

    Minimal API parity with qtwidgets.PasswordEdit as used by qthvym:
    - text(), setText()
    - setPlaceholderText()
    - setEchoMode()
    - setReadOnly()
    - setEnabled()
    - setFont()
    - setStyleSheet()
    - setFocus()
    - textChanged signal (proxied from the internal QLineEdit)
    """

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)

        self.setObjectName("PasswordEdit")
        # Optional style "class" hook for QSS
        self.setProperty("class", "PasswordEdit")

        self.line_edit = QtWidgets.QLineEdit(self)
        self.line_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.line_edit.setClearButtonEnabled(True)

        self.toggle_button = QtWidgets.QToolButton(self)
        self.toggle_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.toggle_button.setAutoRaise(True)
        self.toggle_button.setFocusPolicy(QtCore.Qt.NoFocus)

        # Icons
        eye_icon_path = _resolve_asset_path("eye.svg")
        hidden_icon_path = _resolve_asset_path("hidden.svg")
        self._icon_eye = QtGui.QIcon(str(eye_icon_path))
        self._icon_hidden = QtGui.QIcon(str(hidden_icon_path))

        # Start with password hidden
        self._is_visible = False
        self._apply_visibility_icon()

        # Sizing
        self.toggle_button.setIconSize(QtCore.QSize(18, 18))
        self.toggle_button.setFixedSize(QtCore.QSize(26, 22))

        # Layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.line_edit, 1)
        layout.addWidget(self.toggle_button, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # Connections
        self.toggle_button.clicked.connect(self._toggle_visibility)

    # -----------------------------
    # Visibility handling
    # -----------------------------
    def _toggle_visibility(self) -> None:
        self._is_visible = not self._is_visible
        self.line_edit.setEchoMode(
            QtWidgets.QLineEdit.Normal if self._is_visible else QtWidgets.QLineEdit.Password
        )
        self._apply_visibility_icon()

    def _apply_visibility_icon(self) -> None:
        if self._is_visible:
            self.toggle_button.setIcon(self._icon_hidden)
            self.toggle_button.setToolTip("Hide password")
            self.toggle_button.setAccessibleName("Hide password")
        else:
            self.toggle_button.setIcon(self._icon_eye)
            self.toggle_button.setToolTip("Show password")
            self.toggle_button.setAccessibleName("Show password")

    # -----------------------------
    # API parity (forwarders/proxies)
    # -----------------------------
    def text(self) -> str:
        return self.line_edit.text()

    def setText(self, text: str) -> None:
        self.line_edit.setText(text)

    def setPlaceholderText(self, text: str) -> None:
        self.line_edit.setPlaceholderText(text)

    def setEchoMode(self, mode: QtWidgets.QLineEdit.EchoMode) -> None:  # type: ignore[name-defined]
        self.line_edit.setEchoMode(mode)
        self._is_visible = mode == QtWidgets.QLineEdit.Normal
        self._apply_visibility_icon()

    def setReadOnly(self, read_only: bool) -> None:
        self.line_edit.setReadOnly(read_only)

    def setEnabled(self, enabled: bool) -> None:  # type: ignore[override]
        super().setEnabled(enabled)
        self.line_edit.setEnabled(enabled)
        self.toggle_button.setEnabled(enabled)

    def setFont(self, font: QtGui.QFont) -> None:  # type: ignore[override]
        super().setFont(font)
        self.line_edit.setFont(font)

    def setStyleSheet(self, style: str) -> None:  # type: ignore[override]
        # Apply to container and inner line edit so existing QSS still affects text field
        super().setStyleSheet(style)
        self.line_edit.setStyleSheet(style)

    def setFocus(self) -> None:  # type: ignore[override]
        self.line_edit.setFocus()

    # Signals proxy
    @property
    def textChanged(self):  # QtCore.pyqtBoundSignal
        return self.line_edit.textChanged

    @property
    def editingFinished(self):  # QtCore.pyqtBoundSignal
        return self.line_edit.editingFinished

    # Hints
    def sizeHint(self) -> QtCore.QSize:  # type: ignore[override]
        return self.line_edit.sizeHint()


