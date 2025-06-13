import os
import cv2
import numpy as np
import random

def expand_image(original_path, mask_path, original_image, mask_image, num_expansions, output_original_dir, output_mask_dir):
    """
    对单个原始图像和缺陷遮罩进行多次扩充，并将结果存储在不同的目录中。

    Args:
        original_path (str): 原始图像的完整文件路径。
        mask_path (str): 缺陷遮罩的完整文件路径。
        original_image (np.ndarray): 原始图像数组。
        mask_image (np.ndarray): 缺陷遮罩数组。
        num_expansions (int): 扩充的次数。
        output_original_dir (str): 存放扩充后原始图像的目录。
        output_mask_dir (str): 存放扩充后缺陷遮罩的目录。
    """
    original_height, original_width = original_image.shape[:2]
    mask_height, mask_width = mask_image.shape[:2]

    if (original_width != mask_width) or (original_height != mask_height):
        raise ValueError("原始图像和遮罩的尺寸必须相同。")

    h, w = original_height, original_width
    l = 512

    for i in range(num_expansions):
        new_width, new_height = w, h

        expanded_original = None
        expanded_mask = None

        if h < w:
            # 在高度方向上扩充
            padding_h = l - h
            padding_top = random.randint(0, padding_h)
            padding_bottom = padding_h - padding_top

            new_height = l
            expanded_original = np.full((new_height, new_width, 3), (127, 127, 127), dtype=np.uint8)
            expanded_original[padding_top:padding_top+h, :] = original_image

            expanded_mask = np.full((new_height, new_width, 3), (127, 127, 127), dtype=np.uint8)
            expanded_mask[padding_top:padding_top+h, :] = mask_image

        elif w < h:
            # 在宽度方向上扩充
            padding_w = l - w
            padding_left = random.randint(0, padding_w)
            padding_right = padding_w - padding_left

            new_width = l
            expanded_original = np.full((new_height, new_width, 3), (127, 127, 127), dtype=np.uint8)
            expanded_original[:, padding_left:padding_left+w] = original_image

            expanded_mask = np.full((new_height, new_width, 3), (127, 127, 127), dtype=np.uint8)
            expanded_mask[:, padding_left:padding_left+w] = mask_image
        else:
            # 如果宽度和高度相等，则不进行扩充
            expanded_original = original_image
            expanded_mask = mask_image

        base_name, ext = os.path.splitext(os.path.basename(original_path))
        output_original_name = os.path.join(output_original_dir, f"{base_name}_expanded_{i+1}{ext}")
        output_mask_name = os.path.join(output_mask_dir, f"{base_name}_expanded_{i+1}_mask{ext}")

        cv2.imwrite(output_original_name, cv2.cvtColor(expanded_original, cv2.COLOR_RGB2BGR))
        cv2.imwrite(output_mask_name, cv2.cvtColor(expanded_mask, cv2.COLOR_RGB2BGR))
        print(f"已扩充并储存: {output_original_name} 和 {output_mask_name}")

def batch_expand_images(original_dir, mask_suffix="_mask", num_expansions=1, output_original_dir="expanded_originals", output_mask_dir="expanded_masks"):
    """
    批量扩充指定目录下的原始图像及其对应的缺陷遮罩，并将结果分开储存。

    Args:
        original_dir (str): 存放原始图像的目录。
        mask_suffix (str, optional): 缺陷遮罩文件名的后缀。默认为 "_mask"。
        num_expansions (int, optional): 每个图对需要扩充的次数。默认为 1。
        output_original_dir (str, optional): 存放扩充后原始图像的目录。默认为 "expanded_originals"。
        output_mask_dir (str, optional): 存放扩充后缺陷遮罩的目录。默认为 "expanded_masks"。
    """
    if not os.path.exists(output_original_dir):
        os.makedirs(output_original_dir)
    if not os.path.exists(output_mask_dir):
        os.makedirs(output_mask_dir)

    original_files = [f for f in os.listdir(original_dir) if os.path.isfile(os.path.join(original_dir, f))]

    for original_file in original_files:
        name, ext = os.path.splitext(original_file)
        if not name.isdigit():  # 判断文件名（不含副文件名）是否为数字
            continue

        original_path = os.path.join(original_dir, original_file)
        mask_file = name + mask_suffix + ext
        mask_path = os.path.join(original_dir, mask_file)

        if os.path.exists(mask_path):
            try:
                original_image = cv2.imread(original_path)
                mask_image = cv2.imread(mask_path)
                if original_image is None or mask_image is None:
                    raise FileNotFoundError(f"无法读取图像文件 {original_path} 或 {mask_path}")
                original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
                mask_image = cv2.cvtColor(mask_image, cv2.COLOR_BGR2RGB)
                print(f"正在处理: {original_file} 和 {mask_file}")
                expand_image(original_path, mask_path, original_image, mask_image, num_expansions, output_original_dir, output_mask_dir)
            except FileNotFoundError:
                print(f"错误: 找不到文件 {original_path} 或 {mask_path}")
            except ValueError as e:
                print(f"错误处理 {original_file} 和 {mask_file}: {e}")
            except Exception as e:
                print(f"处理 {original_file} 和 {mask_file} 时发生未预期的错误: {e}")
        else:
            print(f"警告: 找不到对应的遮罩文件 {mask_file}")

if __name__ == "__main__":
    original_images_path = input("请输入存放原始图像的目录路径: ")
    num_expand = int(input("请输入每个图像需要扩充的次数: "))
    output_original = input("请输入存放扩充后原图的目录路径 (默认: expanded_originals): ") or "expanded_originals"
    output_mask = input("请输入存放扩充后掩码的目录路径 (默认: expanded_masks): ") or "expanded_masks"

    batch_expand_images(original_images_path, num_expansions=num_expand, output_original_dir=output_original, output_mask_dir=output_mask)



