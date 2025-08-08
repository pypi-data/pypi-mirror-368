import os
from pathlib import Path

import qrcode


def generate_qr_code(data: str, path: Path, filename: str) -> Path:
    """
    生成二维码并保存为图片
    :param data: 要编码的数据
    :param path: 保存图片的路径
    :param filename: 保存的图片文件名
    :return: 图片路径
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    os.makedirs(path, exist_ok=True)

    img.save(path / filename)

    return path / filename
