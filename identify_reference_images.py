#!/usr/bin/env python3
"""
Identify and organize reference images vs individual photos
"""

import os
from PIL import Image
import imagehash
import json
from collections import defaultdict

def identify_reference_images():
    """Identify which images are references (duplicated) vs individual photos"""

    image_dir = 'excel_images'
    image_hashes = {}
    hash_to_images = defaultdict(list)

    # Calculate hash for each image
    for img_file in os.listdir(image_dir):
        if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(image_dir, img_file)
            try:
                img = Image.open(img_path)
                # Use perceptual hash for similarity
                img_hash = str(imagehash.average_hash(img))
                image_hashes[img_file] = img_hash
                hash_to_images[img_hash].append(img_file)
            except Exception as e:
                print(f"Error processing {img_file}: {e}")

    # Identify reference images (appear multiple times or are small)
    reference_images = []
    individual_photos = []

    for hash_val, img_list in hash_to_images.items():
        if len(img_list) > 5:  # If image appears more than 5 times, it's likely a reference
            reference_images.extend(img_list)
        else:
            individual_photos.extend(img_list)

    # Also check image dimensions
    small_images = []
    large_images = []

    for img_file in os.listdir(image_dir):
        if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(image_dir, img_file)
            try:
                img = Image.open(img_path)
                width, height = img.size

                if width < 300 or height < 300:  # Small images are likely references
                    small_images.append({
                        'file': img_file,
                        'size': (width, height),
                        'area': width * height
                    })
                else:
                    large_images.append({
                        'file': img_file,
                        'size': (width, height),
                        'area': width * height
                    })
            except Exception as e:
                print(f"Error checking size of {img_file}: {e}")

    # Sort by area to identify patterns
    small_images.sort(key=lambda x: x['area'])
    large_images.sort(key=lambda x: x['area'])

    print(f"\n=== Image Analysis Results ===")
    print(f"Total images: {len(image_hashes)}")
    print(f"Unique image hashes: {len(hash_to_images)}")
    print(f"Reference images (duplicated): {len(set(reference_images))}")
    print(f"Individual photos: {len(individual_photos)}")
    print(f"Small images (<300px): {len(small_images)}")
    print(f"Large images (>=300px): {len(large_images)}")

    # Show samples of small images (likely references)
    if small_images:
        print(f"\n=== Small Images (Likely References) ===")
        for i, img_info in enumerate(small_images[:10]):
            print(f"{img_info['file']}: {img_info['size']} ({img_info['area']} pixels)")

    # Show samples of large images (likely individual photos)
    if large_images:
        print(f"\n=== Large Images (Likely Individual Photos) ===")
        for i, img_info in enumerate(large_images[:5]):
            print(f"{img_info['file']}: {img_info['size']} ({img_info['area']} pixels)")

    # Create mapping based on image numbers
    # Assuming images are numbered sequentially
    image_numbers = []
    for img_file in os.listdir(image_dir):
        if img_file.startswith('image') and img_file[-4:] in ['.png', '.jpg', 'jpeg']:
            try:
                num = int(img_file.replace('image', '').replace('.png', '').replace('.jpg', '').replace('.jpeg', ''))
                image_numbers.append(num)
            except:
                pass

    image_numbers.sort()

    # Based on typical Excel export patterns:
    # First ~20-30 images might be references (skin, hair, eye)
    # Rest are individual photos

    reference_range = list(range(1, 25))  # First 24 images as references
    photo_range = list(range(25, max(image_numbers) + 1))  # Rest as photos

    mapping = {
        'reference_images': {
            'skin_colors': [f'image{i}.png' for i in range(1, 8)],  # 7 skin colors
            'hair_types': [f'image{i}.png' for i in range(8, 18)],  # 10 hair types
            'eye_colors': [f'image{i}.png' for i in range(18, 25)],  # 7 eye colors
        },
        'individual_photos': [f'image{i}.png' for i in photo_range if i in image_numbers][:132]  # 132 participants
    }

    # Save mapping
    with open('image_type_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)

    print(f"\n=== Mapping Created ===")
    print(f"Reference skin colors: {len(mapping['reference_images']['skin_colors'])}")
    print(f"Reference hair types: {len(mapping['reference_images']['hair_types'])}")
    print(f"Reference eye colors: {len(mapping['reference_images']['eye_colors'])}")
    print(f"Individual photos: {len(mapping['individual_photos'])}")

    return mapping

if __name__ == "__main__":
    identify_reference_images()