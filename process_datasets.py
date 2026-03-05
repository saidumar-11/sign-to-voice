import os
import shutil
from pathlib import Path
from config import AMERICAN_LABELS, RUSSIAN_LABELS

def setup_dirs(base_dir, num_classes):
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir, exist_ok=True)
    for i in range(num_classes):
        os.makedirs(os.path.join(base_dir, str(i)), exist_ok=True)

def process_asl(asl_temp_dir, out_dir):
    print("Processing ASL dataset...")
    # Setup out_dir for classes 0 to 25 (A-Z)
    setup_dirs(out_dir, 26)
    
    splits = ['train', 'valid', 'test']
    for split in splits:
        labels_dir = os.path.join(asl_temp_dir, split, 'labels')
        images_dir = os.path.join(asl_temp_dir, split, 'images')
        if not os.path.exists(labels_dir): continue
        
        for label_file in os.listdir(labels_dir):
            if not label_file.endswith('.txt'): continue
                
            label_path = os.path.join(labels_dir, label_file)
            with open(label_path, 'r') as f:
                lines = f.readlines()
                if not lines: continue
            
            # Use the first line's class id
            class_id = int(lines[0].split()[0])
            if 0 <= class_id <= 25:
                # Find corresponding image
                image_name = label_file.replace('.txt', '.jpg')
                src_image_path = os.path.join(images_dir, image_name)
                
                # Some might have .jpeg or .png, fallback logic
                if not os.path.exists(src_image_path):
                    src_image_path = os.path.join(images_dir, label_file.replace('.txt', '.jpeg'))
                if not os.path.exists(src_image_path):
                    src_image_path = os.path.join(images_dir, label_file.replace('.txt', '.png'))
                
                if os.path.exists(src_image_path):
                    dst_image_path = os.path.join(out_dir, str(class_id), f"{split}_{image_name}")
                    shutil.copy2(src_image_path, dst_image_path)
    print("ASL dataset processed successfully.")

def process_rsl(rsl_temp_dir, out_dir):
    print("Processing RSL dataset...")
    # Reverse lookup for RUSSIAN_LABELS
    reverse_russian = {v: k for k, v in RUSSIAN_LABELS.items()}
    
    # We only create directories for labels that actually exist
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    
    for folder in os.listdir(rsl_temp_dir):
        folder_path = os.path.join(rsl_temp_dir, folder)
        if not os.path.isdir(folder_path): continue
            
        label = folder.strip().upper()
        if label in reverse_russian:
            class_idx = reverse_russian[label]
            class_dir = os.path.join(out_dir, str(class_idx))
            os.makedirs(class_dir, exist_ok=True)
            
            for img_file in os.listdir(folder_path):
                if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    src_path = os.path.join(folder_path, img_file)
                    dst_path = os.path.join(class_dir, img_file)
                    shutil.copy2(src_path, dst_path)
    print("RSL dataset processed successfully.")

if __name__ == '__main__':
    base_path = Path(__file__).parent
    
    asl_temp_dir = base_path / 'asl_temp'
    rsl_temp_dir = base_path / 'rsl_temp' / 'dataset_rsl'
    
    asl_out_dir = base_path / 'data_asl'
    rsl_out_dir = base_path / 'data_russian'
    
    if asl_temp_dir.exists():
        process_asl(str(asl_temp_dir), str(asl_out_dir))
    else:
        print(f"ASL temp dir not found: {asl_temp_dir}")
        
    if rsl_temp_dir.exists():
        process_rsl(str(rsl_temp_dir), str(rsl_out_dir))
    else:
        print(f"RSL temp dir not found: {rsl_temp_dir}")
