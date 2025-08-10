import os
from pathlib import Path

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QLayout, QDialog
from PyQt5.QtGui import QClipboard


def center_on_screen(widget) -> None:
    """Center a widget on the current screen using modern APIs."""
    screen = getattr(widget, "screen", None)
    screen = screen() if callable(screen) else screen
    if screen is None:
        screen = QApplication.primaryScreen()
    geo = screen.availableGeometry()
    frame = widget.frameGeometry()
    frame.moveCenter(geo.center())
    widget.move(frame.topLeft())


def prepare_dialog_for_dynamic_sizing(dialog: QDialog, layout: QLayout, allow_resize: bool = True) -> None:
    """Configure a dialog to size to its contents and be resizable.

    - Ensures content drives the minimum size
    - Optionally enables a size grip for user resizing
    - Adjusts the initial size to fit contents
    """
    layout.setSizeConstraint(QLayout.SetMinimumSize)
    if allow_resize:
        dialog.setSizeGripEnabled(True)
        dialog.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
    dialog.adjustSize()


def _default_qss_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "style.qss"


def apply_app_stylesheet(qss_text: str = None) -> None:
    """Apply the default (or provided) QSS to the QApplication instance."""
    app = QApplication.instance()
    if app is None:
        return
    if qss_text is None:
        try:
            qss_text = _default_qss_path().read_text()
        except Exception:
            return
    app.setStyleSheet(qss_text)


def apply_app_stylesheet_if_env() -> None:
    """Apply QSS if HVYM_USE_QSS env flag is truthy (1, true, yes, on)."""
    val = os.environ.get("HVYM_USE_QSS", "0").strip().lower()
    if val in {"1", "true", "yes", "on"}:
        apply_app_stylesheet()


def copy_to_clipboard(text: str, ensure_flush: bool = False) -> bool:
    """Copy text to system clipboard using Qt (non-blocking).

    Returns True on success. If no QApplication is present, falls back to
    pyperclip (which may block on some systems).
    """
    app = QApplication.instance()
    if app is not None:
        cb: QClipboard = app.clipboard()
        cb.setText(text, mode=QClipboard.Clipboard)
        # Also set selection clipboard on X11-like platforms
        try:
            cb.setText(text, mode=QClipboard.Selection)  # type: ignore[attr-defined]
        except Exception:
            pass
        if ensure_flush:
            # Give Qt a turn to propagate clipboard data
            app.processEvents()
        return True
    # Fallback (not preferred)
    try:
        import pyperclip  # type: ignore
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def copy_to_clipboard_async(text: str) -> None:
    """Queue a clipboard copy on the next event loop iteration."""
    app = QApplication.instance()
    if app is None:
        copy_to_clipboard(text)
        return
    QTimer.singleShot(0, lambda: copy_to_clipboard(text))


