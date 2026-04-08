import numpy as np
from PIL import Image
def calculate_ber_ncc():
    orig_path = input("Введите путь к исходному водяному знаку (бинарное PNG): ")
    ext_path = input("Введите путь к извлечённому водяному знаку (бинарное PNG): ")

    w_orig = np.array(Image.open(orig_path).convert('1'), dtype=np.uint8)
    w_ext = np.array(Image.open(ext_path).convert('1'), dtype=np.uint8)

    w_orig = (w_orig > 0).astype(np.uint8)
    w_ext = (w_ext > 0).astype(np.uint8)

    if w_orig.shape != w_ext.shape:
        raise ValueError("Размеры исходного и извлеченного водяного знака не совпадают")
    errors = np.sum(w_orig != w_ext)
    total_bits = w_orig.size
    ber = errors / total_bits
    print(f"BER: {ber}")

       
    w_orig = (w_orig > 0).astype(np.float64)
    w_ext = (w_ext > 0).astype(np.float64)

    if w_orig.shape != w_ext.shape:
        raise ValueError("Размеры исходного и извлеченного водяного знака не совпадают")
    numerator = np.sum(w_orig * w_ext)
    denominator = np.sqrt(np.sum(w_orig ** 2)) * np.sqrt(np.sum(w_ext ** 2))
    ncc = numerator / denominator if denominator != 0 else 0.0
    print(f"NCC: {ncc}")
    return ncc
