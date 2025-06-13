import os
import cv2
import numpy as np
import random

def crop_image(original_path, mask_path, output_original_dir, output_mask_dir, crop_size_ratio=1.0, defect_threshold=0.5, num_crops=1):
    """
    對單個擴充後的原始圖像和缺陷遮罩進行多次隨機正方形裁剪，並將結果儲存在不同的目錄中。
    (使用 OpenCV 和 NumPy 重寫)

    Args:
        original_path (str): 擴充後的原始圖像檔案路徑。
        mask_path (str): 擴充後的缺陷遮罩檔案路徑。
        output_original_dir (str): 存放裁剪後原始圖像的目錄。
        output_mask_dir (str): 存放裁剪後缺陷遮罩的目錄。
        crop_size_ratio (float, optional): 正方形裁剪尺寸相對於較短邊的比例。預設為 1.0。
        defect_threshold (float, optional): 缺陷面積佔裁剪區域的最小比例，超過此比例則認為裁剪有效。預設為 0.5。
        num_crops (int, optional): 對每個圖像對進行裁剪的次數。預設為 1。
    """
    try:
        # 使用 OpenCV 讀取圖像，預設為 BGR 格式
        original_image = cv2.imread(original_path)
        mask_image = cv2.imread(mask_path)

        if original_image is None:
            raise FileNotFoundError(f"無法讀取原始圖像: {original_path}")
        if mask_image is None:
            raise FileNotFoundError(f"無法讀取遮罩圖像: {mask_path}")

        # OpenCV 的 shape 是 (height, width, channels)
        original_height, original_width, _ = original_image.shape
        mask_height, mask_width, _ = mask_image.shape

        if (original_width != mask_width) or (original_height != mask_height):
            raise ValueError("原始圖像和遮罩的尺寸必須相同。")

        shorter_side = min(original_width, original_height)
        crop_size = int(shorter_side * crop_size_ratio)

        if crop_size > original_width or crop_size > original_height:
            print(f"警告: 裁剪尺寸 ({crop_size}) 大於圖像尺寸，將使用較短邊的長度作為裁剪尺寸。")
            crop_size = shorter_side

        valid_crop_counter = 0
        for i in range(num_crops):
            max_x = original_width - crop_size
            max_y = original_height - crop_size

            if max_x < 0 or max_y < 0:
                print(f"警告: 圖像尺寸小於裁剪尺寸 ({crop_size})，無法進行裁剪。")
                break

            start_x = random.randint(0, max_x)
            start_y = random.randint(0, max_y)
            end_x = start_x + crop_size
            end_y = start_y + crop_size

            # 使用 NumPy 的陣列切片進行裁剪
            cropped_original = original_image[start_y:end_y, start_x:end_x]
            cropped_mask = mask_image[start_y:end_y, start_x:end_x]

            # 將遮罩轉換為灰階圖像以便計算
            # 假設缺陷為白色 (255, 255, 255)
            # 使用 np.all 來檢查所有通道是否都為 255
            is_defect_pixel = np.all(cropped_mask == [255, 255, 255], axis=-1)
            
            # 使用 NumPy 高效計算缺陷比例
            defect_pixels_count = np.sum(is_defect_pixel)
            total_pixels = crop_size * crop_size
            defect_percentage = defect_pixels_count / total_pixels if total_pixels > 0 else 0

            print(f"本次裁剪 #{i+1} 的缺陷比例為: {defect_percentage:.6f}")

            if defect_percentage >= defect_threshold:
                if not os.path.exists(output_original_dir):
                    os.makedirs(output_original_dir)
                if not os.path.exists(output_mask_dir):
                    os.makedirs(output_mask_dir)

                base_name, ext = os.path.splitext(os.path.basename(original_path))
                # 確保副檔名是 OpenCV 支援的格式，例如 .png
                if ext.lower() not in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
                    ext = '.png'

                output_original_name = os.path.join(output_original_dir, f"{base_name}_cropped_{valid_crop_counter+1}{ext}")
                output_mask_name = os.path.join(output_mask_dir, f"{base_name}_cropped_{valid_crop_counter+1}_mask{ext}")

                # 使用 OpenCV 儲存圖像
                cv2.imwrite(output_original_name, cropped_original)
                cv2.imwrite(output_mask_name, cropped_mask)
                print(f"有效裁剪 #{valid_crop_counter+1} 已儲存至: {output_original_name} 和 {output_mask_name}")
                valid_crop_counter += 1

    except FileNotFoundError as e:
        print(f"錯誤: {e}")
    except ValueError as e:
        print(f"錯誤: {e}")
    except Exception as e:
        print(f"發生未預期的錯誤: {e}")

def batch_crop_images(expanded_original_dir, expanded_mask_dir, output_original_dir="cropped_originals", output_mask_dir="cropped_masks", defect_threshold=0.5, num_crops=5):
    """
    批量對指定目錄下的擴充後原始圖像及其對應的缺陷遮罩進行隨機正方形裁剪，並將結果分開儲存。

    Args:
        expanded_original_dir (str): 存放擴充後原始圖像的目錄。
        expanded_mask_dir (str): 存放擴充後缺陷遮罩的目錄。
        output_original_dir (str, optional): 存放裁剪後原始圖像的目錄。預設為 "cropped_originals"。
        output_mask_dir (str, optional): 存放裁剪後缺陷遮罩的目錄。預設為 "cropped_masks"。
        defect_threshold (float, optional): 缺陷面積佔裁剪區域的最小比例。預設為 0.5。
        num_crops (int, optional): 對每個圖像對進行裁剪的次數。預設為 5。
    """
    if not os.path.exists(output_original_dir):
        os.makedirs(output_original_dir)
    if not os.path.exists(output_mask_dir):
        os.makedirs(output_mask_dir)

    # 尋找原始圖像檔案（不包含 "mask"）
    original_files = [f for f in os.listdir(expanded_original_dir) if os.path.isfile(os.path.join(expanded_original_dir, f)) and "_mask" not in f]

    for original_file in original_files:
        base_name, ext = os.path.splitext(original_file)
        
        # 假設原始檔案名可能包含 "_expanded_"
        # 尋找對應的遮罩檔案，其名稱格式為 {base_name}_mask{ext}
        mask_file_name_parts = base_name.split("_expanded_")
        if len(mask_file_name_parts) > 1:
            mask_base_name = mask_file_name_parts[0] + "_expanded_" + mask_file_name_parts[1]
            mask_file = mask_base_name + "_mask" + ext
        else:
            # 如果檔名不含 "_expanded_"，則直接添加 "_mask"
            mask_file = base_name + "_mask" + ext

        original_path = os.path.join(expanded_original_dir, original_file)
        mask_path = os.path.join(expanded_mask_dir, mask_file)

        if os.path.exists(mask_path):
            print(f"正在對 {original_file} 和 {mask_file} 進行裁剪...")
            crop_image(original_path, mask_path, output_original_dir, output_mask_dir, defect_threshold=defect_threshold, num_crops=num_crops)
        else:
            print(f"警告: 在 {expanded_mask_dir} 中找不到對應的擴充後遮罩檔案 {mask_file}")


if __name__ == "__main__":
    expanded_original_path = input("請輸入存放擴充後原始圖像的目錄路徑: ")
    expanded_mask_path = input("請輸入存放擴充後掩碼圖像的目錄路徑: ")
    try:
        threshold_str = input("請輸入缺陷比例的閾值 (预设 0.0002): ")
        threshold = float(threshold_str) if threshold_str else 0.0002
        
        num_crop_str = input("請輸入每個擴充後樣本需要裁剪的次數 (預設: 10): ")
        num_crop = int(num_crop_str) if num_crop_str else 10
    except ValueError:
        print("輸入無效，請確保閾值是浮點數，裁剪次數是整數。")
        exit()

    output_original = input("請輸入存放裁剪後原圖的目錄路徑 (預設: cropped_originals): ") or "cropped_originals"
    output_mask = input("請輸入存放裁剪後掩碼的目錄路徑 (預設: cropped_masks): ") or "cropped_masks"

    batch_crop_images(
        expanded_original_path, 
        expanded_mask_path, 
        output_original_dir=output_original, 
        output_mask_dir=output_mask, 
        defect_threshold=threshold, 
        num_crops=num_crop
    )