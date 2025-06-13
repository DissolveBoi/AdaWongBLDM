import os
import cv2
import numpy as np
import random

# 全局计数器，用于生成唯一的图片编号
processed_image_count = 0

def process_image_pair(
    original_path,
    mask_path,
    output_original_dir,
    output_mask_dir,
    num_augmentations,
    num_crops_per_aug,
    defect_threshold,
    expansion_target_size=512,
    crop_size=512
):
    """
    对单个原始图像和遮罩进行完整的“扩充-裁剪”数据增强流程。

    Args:
        original_path (str): 原始图像的完整文件路径。
        mask_path (str): 缺陷遮罩的完整文件路径。
        output_original_dir (str): 存放最终裁剪后原始图像的目录。
        output_mask_dir (str): 存放最终裁剪后缺陷遮罩的目录。
        num_augmentations (int): 对每个原始图像对执行“扩充”操作的次数。
        num_crops_per_aug (int): 对每次扩充后的图像尝试进行随机裁剪的次数。
        defect_threshold (float): 缺陷面积占裁剪区域的最小比例，超过则保存。
        expansion_target_size (int, optional): 扩充操作的目标尺寸。默认为 512。
        crop_size (int, optional): 最终裁剪出的正方形样本的边长。默认为 512。
    """
    global processed_image_count # 声明使用全局变量
    try:
        original_image = cv2.imread(original_path)
        mask_image = cv2.imread(mask_path)

        if original_image is None or mask_image is None:
            raise FileNotFoundError(f"无法读取图像文件 {original_path} 或 {mask_path}")

        original_height, original_width = original_image.shape[:2]
        if original_image.shape[:2] != mask_image.shape[:2]:
            raise ValueError("原始图像和遮罩的尺寸必须相同。")

        base_name, ext = os.path.splitext(os.path.basename(original_path))
        if ext.lower() not in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            ext = '.png'

        for i in range(num_augmentations):
            h, w = original_height, original_width

            # --- 步骤1: 图像扩充 ---
            padding_h = max(0, expansion_target_size - h)
            padding_w = max(0, expansion_target_size - w)

            if padding_h > 0 or padding_w > 0:
                padding_top = random.randint(0, padding_h)
                padding_left = random.randint(0, padding_w)

                new_height, new_width = h + padding_h, w + padding_w

                expanded_original = np.full((new_height, new_width, 3), (127, 127, 127), dtype=np.uint8)
                expanded_mask = np.full((new_height, new_width, 3), (127, 127, 127), dtype=np.uint8)

                expanded_original[padding_top:padding_top+h, padding_left:padding_left+w] = original_image
                expanded_mask[padding_top:padding_top+h, padding_left:padding_left+w] = mask_image
            else:
                expanded_original = original_image
                expanded_mask = mask_image

            # --- 步骤2: 随机裁剪 ---
            exp_h, exp_w = expanded_original.shape[:2]

            if crop_size > exp_w or crop_size > exp_h:
                print(f"警告: 图像 '{base_name}' 扩充后尺寸({exp_w}x{exp_h})小于裁剪尺寸({crop_size})，跳过。")
                continue

            for _ in range(num_crops_per_aug):
                max_x = exp_w - crop_size
                max_y = exp_h - crop_size

                start_x = random.randint(0, max_x)
                start_y = random.randint(0, max_y)

                cropped_original = expanded_original[start_y:start_y+crop_size, start_x:start_x+crop_size]
                cropped_mask = expanded_mask[start_y:start_y+crop_size, start_x:start_x+crop_size]

                # --- 步骤3: 验证并保存 ---
                is_defect_pixel = np.all(cropped_mask == [255, 255, 255], axis=-1)

                defect_pixels_count = np.sum(is_defect_pixel)
                total_pixels = crop_size * crop_size
                defect_percentage = defect_pixels_count / total_pixels if total_pixels > 0 else 0

                if defect_percentage >= defect_threshold:
                    processed_image_count += 1 # 递增全局计数器
                    # 使用全局计数器进行命名
                    output_original_name = os.path.join(output_original_dir, f"{processed_image_count}{ext}")
                    output_mask_name = os.path.join(output_mask_dir, f"{processed_image_count}_mask{ext}")

                    cv2.imwrite(output_original_name, cropped_original)
                    cv2.imwrite(output_mask_name, cropped_mask)
                    print(f"已保存: {os.path.basename(output_original_name)} (缺陷比例: {defect_percentage:.4f})")

    except Exception as e:
        print(f"处理 {original_path} 时发生严重错误: {e}")

def batch_process_directory(
    input_dir,
    output_original_dir,
    output_mask_dir,
    mask_suffix="_mask",
    num_augmentations=1,
    num_crops_per_aug=5,
    defect_threshold=0.0002,
    expansion_target_size=512,
    crop_size=512
):
    if not os.path.exists(output_original_dir): os.makedirs(output_original_dir)
    if not os.path.exists(output_mask_dir): os.makedirs(output_mask_dir)

    original_files = [f for f in os.listdir(input_dir) if mask_suffix not in f and os.path.isfile(os.path.join(input_dir, f))]

    for original_file in original_files:
        name, ext = os.path.splitext(original_file)
        original_path = os.path.join(input_dir, original_file)
        mask_file = name + mask_suffix + ext
        mask_path = os.path.join(input_dir, mask_file)

        if os.path.exists(mask_path):
            print(f"\n--- 处理: {original_file} ---")
            process_image_pair(
                original_path, mask_path,
                output_original_dir, output_mask_dir,
                num_augmentations, num_crops_per_aug,
                defect_threshold, expansion_target_size, crop_size
            )
        else:
            print(f"警告: 找不到遮罩 {mask_file}，已跳过。")

if __name__ == "__main__":
    print("--- 图像数据处理流水线 (已更新) ---")

    input_images_path = input("请输入存放原始图像和遮罩的目录路径: ")

    try:
        expansion_size = int(input("请输入【扩充目标尺寸】 (默认: 512): ") or "512")
        crop_size = int(input("请输入最终【裁剪尺寸】 (默认: 512): ") or "512")
        num_aug = int(input("请输入每个原始图像的【扩充版本数量】 (默认: 1): ") or "1")
        num_crop = int(input(f"请输入每个扩充版本【尝试裁剪的次数】 (默认: 10): ") or "10")
        threshold_str = input("请输入【缺陷比例阈值】 (例如0.1, 默认: 0.0002): ")
        threshold = float(threshold_str) if threshold_str else 0.0002

    except ValueError:
        print("输入无效，请确保输入的数值为整数或浮点数。程序退出。")
        exit()

    output_original = input("请输入存放裁剪后原图的目录 (默认: augmented_originals): ") or "augmented_originals"
    output_mask = input("请输入存放裁剪后遮罩的目录 (默认: augmented_masks): ") or "augmented_masks"

    batch_process_directory(
        input_dir=input_images_path,
        output_original_dir=output_original,
        output_mask_dir=output_mask,
        num_augmentations=num_aug,
        num_crops_per_aug=num_crop,
        defect_threshold=threshold,
        expansion_target_size=expansion_size,
        crop_size=crop_size
    )

    print("\n--- 所有处理已完成 ---")