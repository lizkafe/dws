from PIL import Image
import numpy as np
from skimage.metrics import structural_similarity as ssim


def embedding_capacity(B: int, M: int, N: int) -> float:

    total_pixels = M * N
    ec_bpp = B / total_pixels
    return ec_bpp

def calculate_psnr(original, modified):
    original = np.array(original)
    modified = np.array(modified)

    mse = np.mean((original.astype(np.float32) - modified.astype(np.float32)) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * np.log10((255 ** 2) / mse)

def calculate_mse(original, modified):
    original = np.array(original)
    modified = np.array(modified)
    MSE =  np.mean((original.astype(np.float32) - modified.astype(np.float32)) ** 2)
    return MSE

def calculate_rmse(original, modified):
    original = np.array(original)
    modified = np.array(modified)

    return np.sqrt(calculate_mse(original, modified))

def calculate_ssim(original, modified):
    
    original = np.array(original)
    modified = np.array(modified)
    ssim_value = ssim(original, modified, data_range=255)
      
    return ssim_value


def arnold_transform(img, iterations=1):
    n = img.shape[0]
    result = img.copy()
    for _ in range(iterations):
        temp = np.zeros_like(result)
        for i in range(n):
            for j in range(n):
                ni = (i + j) % n
                nj = (i + 2 * j) % n
                temp[ni, nj] = result[i, j]
        result = temp
    return result

def arnold_inverse_transform(img, iterations=1):
    n = img.shape[0]
    result = img.copy()
    for _ in range(iterations):
        temp = np.zeros_like(result)
        for i in range(n):
            for j in range(n):
                ni = (2 * i - j) % n
                nj = (-i + j) % n
                temp[ni, nj] = result[i, j]
        result = temp
    return result

def dct2(block):
    return np.round(np.dot(np.dot(dct_matrix, block), dct_matrix.T), 6)

def idct2(block):
    return np.round(np.dot(np.dot(dct_matrix.T, block), dct_matrix), 6)


dct_matrix = np.array([
    [0.3535, 0.3535, 0.3535, 0.3535, 0.3535, 0.3535, 0.3535, 0.3535],
    [0.4903, 0.4157, 0.2777, 0.0975, -0.0975, -0.2777, -0.4157, -0.4903],
    [0.4619, 0.1913, -0.1913, -0.4619, -0.4619, -0.1913, 0.1913, 0.4619],
    [0.4157, -0.0975, -0.4903, -0.2777, 0.2777, 0.4903, 0.0975, -0.4157],
    [0.3535, -0.3535, -0.3535, 0.3535, 0.3535, -0.3535, -0.3535, 0.3535],
    [0.2777, -0.4903, 0.0975, 0.4157, -0.4157, -0.0975, 0.4903, -0.2777],
    [0.1913, -0.4619, 0.4619, -0.1913, -0.1913, 0.4619, -0.4619, 0.1913],
    [0.0975, -0.2777, 0.4157, -0.4903, 0.4903, -0.4157, 0.2777, -0.0975]
], dtype=np.float32)

def embed():
    container_path = input("Введите путь к изображению-контейнеру (PNG, оттенки серого): ")
    watermark_path = input("Введите путь к ЦВЗ (бинарное изображение): ")
    output_path = input("Введите имя для стегоизображения: ")

 
    container = Image.open(container_path).convert('L')
    contain_arr = np.array(container).astype(np.int32)
    n, m = contain_arr.shape
    if n != m:
        raise ValueError("Изображение-контейнер должно быть квадратным!")

    watermark = Image.open(watermark_path).convert('1')
    bin_arr = np.array(watermark, dtype=np.uint8)
    bin_arr = np.where(bin_arr > 0, 1, 0)
    a, b = bin_arr.shape
    if a != n // 8 or b != m // 8:
        raise ValueError("Встраиваемое изображение должно быть в 8 раз меньше контейнера!")

    
    contain_arr = contain_arr - 128

    arnold_iter = 1
    new_bin_arr = arnold_transform(bin_arr, arnold_iter)

   
    t = 80
    k = 12
    z = 2

    
    for h in range(a):
        for w in range(b):
            i = h * 8
            j = w * 8
            block = contain_arr[i:i+8, j:j+8].astype(np.float32)
            dct_block = dct2(block)

            
            x, y = 4, 1

           
            if h > 0:
                neighbor_block = contain_arr[(h-1)*8:(h-1)*8+8, w*8:w*8+8].astype(np.float32)
                neighbor_dct = dct2(neighbor_block)
                delta = dct_block[x, y] - neighbor_dct[x, y]

                bit = new_bin_arr[h, w]
                
                if bit == 1:
                    if delta > (t - k):
                        while delta > (t - k):
                            
                            ac_coeff = [
                                dct_block[1, 0], dct_block[2, 0], dct_block[3, 0],
                                dct_block[0, 1], dct_block[1, 1], dct_block[2, 1],
                                dct_block[0, 2], dct_block[1, 2], dct_block[0, 3],
                            ]
                            med = np.median(ac_coeff)
                            dc = dct_block[0, 0]
                            if abs(dc) > 1000 or abs(dc) < 1:
                                modif = abs(z * med)
                            else:
                                modif = abs(z * (dc - med) / dc)
                            dct_block[x, y] -= modif
                            delta = dct_block[x, y] - neighbor_dct[x, y]
                    elif k > delta > -t/2:
                        while delta < k:
                            ac_coeff = [
                                dct_block[1, 0], dct_block[2, 0], dct_block[3, 0],
                                dct_block[0, 1], dct_block[1, 1], dct_block[2, 1],
                                dct_block[0, 2], dct_block[1, 2], dct_block[0, 3],
                            ]
                            med = np.median(ac_coeff)
                            dc = dct_block[0, 0]
                            if abs(dc) > 1000 or abs(dc) < 1:
                                modif = abs(z * med)
                            else:
                                modif = abs(z * (dc - med) / dc)
                            dct_block[x, y] += modif
                            delta = dct_block[x, y] - neighbor_dct[x, y]
                    elif delta < -t/2:
                        while delta > (-t - k):
                            ac_coeff = [
                                dct_block[1, 0], dct_block[2, 0], dct_block[3, 0],
                                dct_block[0, 1], dct_block[1, 1], dct_block[2, 1],
                                dct_block[0, 2], dct_block[1, 2], dct_block[0, 3],
                            ]
                            med = np.median(ac_coeff)
                            dc = dct_block[0, 0]
                            if abs(dc) > 1000 or abs(dc) < 1:
                                modif = abs(z * med)
                            else:
                                modif = abs(z * (dc - med) / dc)
                            dct_block[x, y] -= modif
                            delta = dct_block[x, y] - neighbor_dct[x, y]
                else:  
                    if delta > t/2:
                        while delta <= (t + k):
                            ac_coeff = [
                                dct_block[1, 0], dct_block[2, 0], dct_block[3, 0],
                                dct_block[0, 1], dct_block[1, 1], dct_block[2, 1],
                                dct_block[0, 2], dct_block[1, 2], dct_block[0, 3],
                            ]
                            med = np.median(ac_coeff)
                            dc = dct_block[0, 0]
                            if abs(dc) > 1000 or abs(dc) < 1:
                                modif = abs(z * med)
                            else:
                                modif = abs(z * (dc - med) / dc)
                            dct_block[x, y] += modif
                            delta = dct_block[x, y] - neighbor_dct[x, y]
                    elif -k < delta < t/2:
                        while delta >= -k:
                            ac_coeff = [
                                dct_block[1, 0], dct_block[2, 0], dct_block[3, 0],
                                dct_block[0, 1], dct_block[1, 1], dct_block[2, 1],
                                dct_block[0, 2], dct_block[1, 2], dct_block[0, 3],
                            ]
                            med = np.median(ac_coeff)
                            dc = dct_block[0, 0]
                            if abs(dc) > 1000 or abs(dc) < 1:
                                modif = abs(z * med)
                            else:
                                modif = abs(z * (dc - med) / dc)
                            dct_block[x, y] -= modif
                            delta = dct_block[x, y] - neighbor_dct[x, y]
                    elif delta < (k - t):
                        while delta <= (k - t):
                            ac_coeff = [
                                dct_block[1, 0], dct_block[2, 0], dct_block[3, 0],
                                dct_block[0, 1], dct_block[1, 1], dct_block[2, 1],
                                dct_block[0, 2], dct_block[1, 2], dct_block[0, 3],
                            ]
                            med = np.median(ac_coeff)
                            dc = dct_block[0, 0]
                            if abs(dc) > 1000 or abs(dc) < 1:
                                modif = abs(z * med)
                            else:
                                modif = abs(z * (dc - med) / dc)
                            dct_block[x, y] += modif
                            delta = dct_block[x, y] - neighbor_dct[x, y]

            
            contain_arr[i:i+8, j:j+8] = np.round(idct2(dct_block))

    
    contain_arr = np.clip(contain_arr + 128, 0, 255).astype(np.uint8)
    result_img = Image.fromarray(contain_arr)
    result_img.save(output_path)
    print("Встраивание прошло успешно!")
    ssim = calculate_ssim(container, result_img)
    mse = calculate_mse(container, result_img)
    rmse = calculate_rmse(container, result_img)
    psnr = calculate_psnr(container, result_img)
    print(f"Характеристики встраивания:\n SSIM: {ssim}\n MSE: {mse}\n RMSE: {rmse}\n PSNR: {psnr}")
    return result_img

def extract():
    container_path = input("Введите путь к стегоизображению: ")
    output_path = input("Введите путь для сохранения извлеченного водяного знака: ")

    container = Image.open(container_path).convert('L')
    contain_arr = np.array(container).astype(np.int32)
    n, m = contain_arr.shape
    if n != m:
        raise ValueError("Изображение-контейнер должно быть квадратным!")

    a = n // 8
    b = m // 8
    contain_arr = contain_arr - 128

    t = 80
    k = 12
    z = 2

    extracted_wm = np.zeros((a, b), dtype=np.uint8)

    for h in range(a):
        for w in range(b):
            i = h * 8
            j = w * 8
            block = contain_arr[i:i+8, j:j+8].astype(np.float32)
            dct_block = dct2(block)

           
            x, y = 4, 1

            
            if h > 0:
                neighbor_block = contain_arr[(h-1)*8:(h-1)*8+8, w*8:w*8+8].astype(np.float32)
                neighbor_dct = dct2(neighbor_block)
                delta = dct_block[x, y] - neighbor_dct[x, y]

                if (delta < -t) or (0 < delta < t):
                    extracted_wm[h, w] = 1
                elif (delta > t) or ((delta < 0) and (delta > -t)):
                    extracted_wm[h, w] = 0

    
    arnold_iter = 1
    ready_wm = arnold_inverse_transform(extracted_wm, arnold_iter)

    
    ready_wm_img = Image.fromarray((ready_wm*255).astype(np.uint8))
    ready_wm_img.save(output_path)
    print("Извлечение завершено. Водяной знак сохранён в", output_path)
    return ready_wm_img
