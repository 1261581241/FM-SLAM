#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate dynamic object masks using FastSAM for FM-SLAM
Segments persons (COCO class 0) from RGB-D dataset images
"""
import cv2
import numpy as np
import torch
import os
import sys
import argparse
from pathlib import Path

try:
    from ultralytics import FastSAM
except ImportError:
    print("Error: FastSAM not found. Install with: pip install ultralytics")
    sys.exit(1)


def generate_masks(model_path, rgb_folder, output_folder, conf_threshold=0.25):
    """
    Generate binary masks for dynamic objects (persons)

    Args:
        model_path: Path to FastSAM-x.pt model
        rgb_folder: Path to RGB images folder
        output_folder: Path to save masks
        conf_threshold: Confidence threshold for detection
    """
    # Load FastSAM model
    print(f"Loading FastSAM model from {model_path}...")
    model = FastSAM(model_path)

    # Get all RGB images
    rgb_files = sorted([f for f in os.listdir(rgb_folder)
                       if f.endswith(('.png', '.jpg', '.jpeg'))])

    if not rgb_files:
        print(f"Error: No image files found in {rgb_folder}")
        return

    print(f"Found {len(rgb_files)} images")
    os.makedirs(output_folder, exist_ok=True)

    # Process each image
    for idx, filename in enumerate(rgb_files, 1):
        rgb_path = os.path.join(rgb_folder, filename)
        mask_path = os.path.join(output_folder, filename)

        # Run FastSAM inference
        results = model.predict(
            rgb_path,
            conf=conf_threshold,
            device='cuda' if torch.cuda.is_available() else 'cpu',
            retina_masks=True,
            imgsz=640,
            verbose=False
        )

        # Extract person masks (class 0 in COCO)
        result = results[0]
        h, w = result.orig_shape
        mask = np.zeros((h, w), dtype=np.uint8)

        if result.masks is not None:
            masks = result.masks.data
            boxes = result.boxes.data
            clss = boxes[:, 5]

            # Find person detections
            person_indices = torch.where(clss == 0)[0]

            if len(person_indices) > 0:
                person_masks = masks[person_indices]
                # Combine all person masks
                combined_mask = torch.any(person_masks, dim=0)
                mask = (combined_mask.cpu().numpy() * 255).astype(np.uint8)

        # Save mask
        cv2.imwrite(mask_path, mask)

        if (idx % 100 == 0) or (idx == len(rgb_files)):
            print(f"Processed {idx}/{len(rgb_files)} images")

    print(f"\n✓ All masks saved to {output_folder}")
    print(f"  Mask format: Binary (0=static, 255=dynamic)")


def main():
    parser = argparse.ArgumentParser(
        description='Generate dynamic object masks using FastSAM for FM-SLAM'
    )
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Path to FastSAM-x.pt model file'
    )
    parser.add_argument(
        '--dataset',
        type=str,
        required=True,
        help='Path to RGB-D dataset root directory'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output directory for masks'
    )
    parser.add_argument(
        '--rgb-folder',
        type=str,
        default='rgb',
        help='RGB images folder name (default: rgb)'
    )
    parser.add_argument(
        '--conf',
        type=float,
        default=0.25,
        help='Confidence threshold (default: 0.25)'
    )

    args = parser.parse_args()

    # Validate paths
    if not os.path.exists(args.model):
        print(f"Error: Model file not found: {args.model}")
        print("\nDownload FastSAM-x.pt from:")
        print("https://github.com/CASIA-IVA-Lab/FastSAM/releases/download/v1.0.0/FastSAM-x.pt")
        sys.exit(1)

    rgb_folder = os.path.join(args.dataset, args.rgb_folder)
    if not os.path.exists(rgb_folder):
        print(f"Error: RGB folder not found: {rgb_folder}")
        sys.exit(1)

    # Generate masks
    print("="*60)
    print("FastSAM Mask Generation for FM-SLAM")
    print("="*60)
    print(f"Model: {args.model}")
    print(f"Dataset: {args.dataset}")
    print(f"RGB folder: {rgb_folder}")
    print(f"Output: {args.output}")
    print(f"Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    print("="*60)

    generate_masks(args.model, rgb_folder, args.output, args.conf)

    print("\n✓ Done! Use these masks with FM-SLAM:")
    print(f"  ./Examples/RGB-D/rgbd_tum Vocabulary/ORBvoc.txt \\")
    print(f"      Examples/RGB-D/TUM3.yaml {args.dataset} \\")
    print(f"      associations.txt {args.output}")


if __name__ == '__main__':
    main()
