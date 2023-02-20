from PyQt6.QtWidgets import QMainWindow, QFileDialog


def newFile(
    window: QMainWindow,
    dialog_title: str,
    suggested_file_name: str,
    allowed_file_type: str,
) -> str:
    file_name, _ = QFileDialog.getSaveFileName(
        window,
        dialog_title,
        suggested_file_name,
        allowed_file_type,
    )
    if not file_name:
        return ""
    return file_name


def openFile(
    window: QMainWindow,
    dialog_title: str,
    directory: str,
    allowed_file_type: str,
):
    file_name, _ = QFileDialog.getOpenFileName(
        window,
        dialog_title,
        directory,
        allowed_file_type,
    )
    if not file_name:
        return ""
    return file_name
