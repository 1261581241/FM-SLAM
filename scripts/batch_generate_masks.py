#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch generate masks for all experimental sequences using FastSAM
Processes TUM Freiburg3 and Bonn RGB-D datasets
"""
import cv2
import numpy as np
import torch
import os
import sys
import time
import json
import argparse
from pathlib import Path

try:
    from ultralytics import FastSAM
except ImportError:
    print("Error: FastSAM not found. Install with: pip install ultralytics")
    sys.exit(1)


# Sequence configurations
SEQUENCES = [
    'rgbd_dataset_freiburg3_walking_xyz',
    'rgbd_dataset_freiburg3_walking_static',
    'rgbd_dataset_freiburg3_walking_rpy',
    'rgbd_dataset_freiburg3_walking_halfsphere',
    'rgbd_dataset_freiburg3_sitting_xyz',
    'rgbd_dataset_freiburg3_sitting_halfsphere',
    'rgbd_dataset_freiburg3_sitting_rpy',
    'rgbd_bonn_crowd',
    'rgbd_bonn_crowd2',
    'rgbd_bonn_crowd3',
]


def generate_masks_for_sequence(model, dataset_root, sequence, output_root, conf_threshold=0.25):
    """
    Generate masks for one sequence

    Args:
        model: FastSAM model
        dataset_root: Dataset root directory
        sequence: Sequence name
        output_root: Output root directory
        conf_threshold: Detection confidence threshold
    """
    rgb_folder = os.path.join(dataset_root, sequence, 'rgb')
    output_folder = os.path.join(output_root, sequence)

    if not os.path.exists(rgb_folder):
        print(f"Warning: RGB folder not found for {sequence}, skipping")
        return 0

    os.makedirs(output_folder, exist_ok=True)

    # Get all RGB images
    rgb_files = sorted([f for f in os.listdir(rgb_folder)
                       if f.endswith(('.png', '.jpg', '.jpeg'))])

    if not rgb_files:
        print(f"Warning: No images found in {rgb_folder}")
        return 0

    print(f"\n{'='*60}")
    print(f"Processing: {sequence}")
    print(f"Images: {len(rgb_files)}")
    print(f"Output: {output_folder}")
    print(f"{'='*60}")

    processed = 0
    timing_log = []

    for idx, filename in enumerate(rgb_files, 1):
        rgb_path = os.path.join(rgb_folder, filename)
        mask_path = os.path.join(output_folder, filename)

        # Skip if mask already exists
        if os.path.exists(mask_path):
            if idx % 100 == 0:
                print(f"  [{idx}/{len(rgb_files)}] Skipping existing masks...")
            continue

        # Run FastSAM inference
        t_start = time.time()

        results = model.predict(
            rgb_path,
            conf=conf_threshold,
            device='cuda' if torch.cuda.is_available() else 'cpu',
            retina_masks=True,
            imgsz=640,
            verbose=False
        )

        t_end = time.time()
        inference_time = (t_end - t_start) * 1000  # ms

        # Extract person masks (class 0 in COCO)
        result = results[0]
        h, w = result.orig_shape
        mask = np.zeros((h, w), dtype=np.uint8)

        num_detections = 0
        if result.masks is not None:
            masks = result.masks.data
            boxes = result.boxes.data
            clss = boxes[:, 5]

            # Find person detections
            person_indices = torch.where(clss == 0)[0]
            num_detections = len(person_indices)

            if num_detections > 0:
                person_masks = masks[person_indices]
                # Combine all person masks
                combined_mask = torch.any(person_masks, dim=0)
                mask = (combined_mask.cpu().numpy() * 255).astype(np.uint8)

        # Save mask
        cv2.imwrite(mask_path, mask)
        processed += 1

        # Log timing
        timing_log.append({
            'frame_id': idx - 1,
            'filename': filename,
            'inference_time_ms': round(inference_time, 2),
            'num_persons': num_detections
        })

        if idx % 100 == 0 or idx == len(rgb_files):
            avg_time = sum(t['inference_time_ms'] for t in timing_log[-100:]) / min(100, len(timing_log))
            print(f"  [{idx}/{len(rgb_files)}] Processed, Avg time: {avg_time:.1f}ms")

    # Save timing log
    timing_file = os.path.join(output_folder, 'timing_log.json')
    with open(timing_file, 'w') as f:
        json.dump(timing_log, f, indent=2)

    print(f"✓ {sequence}: {processed} masks generated")
    print(f"  Timing log saved: {timing_file}")

    return processed


def main():
    parser = argparse.ArgumentParser(
        description='Batch generate masks for all sequences using FastSAM'
    )
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Path to FastSAM-x.pt model'
    )
    parser.add_argument(
        '--dataset-root',
        type=str,
        required=True,
        help='Root directory containing all dataset sequences'
    )
    parser.add_argument(
        '--output-root',
        type=str,
        required=True,
        help='Root directory for output masks'
    )
    parser.add_argument(
        '--sequences',
        nargs='+',
        default=SEQUENCES,
        help='Sequences to process (default: all)'
    )
    parser.add_argument(
        '--conf',
        type=float,
        default=0.25,
        help='Confidence threshold (default: 0.25)'
    )

    args = parser.parse_args()

    # Validate model file
    if not os.path.exists(args.model):
        print(f"Error: Model file not found: {args.model}")
        print("\nDownload FastSAM-x.pt from:")
        print("https://github.com/CASIA-IVA-Lab/FastSAM/releases/download/v1.0.0/FastSAM-x.pt")
        sys.exit(1)

    # Load FastSAM model
    print("="*60)
    print("FastSAM Batch Mask Generation")
    print("="*60)
    print(f"Model: {args.model}")
    print(f"Dataset root: {args.dataset_root}")
    print(f"Output root: {args.output_root}")
    print(f"Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    print(f"Sequences: {len(args.sequences)}")
    print("="*60)

    print("\nLoading FastSAM model...")
    model = FastSAM(args.model)
    print("✓ Model loaded")

    # Process each sequence
    total_processed = 0
    start_time = time.time()

    for seq in args.sequences:
        processed = generate_masks_for_sequence(
            model,
            args.dataset_root,
            seq,
            args.output_root,
            args.conf
        )
        total_processed += processed

    elapsed_time = time.time() - start_time

    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"Total sequences: {len(args.sequences)}")
    print(f"Total masks generated: {total_processed}")
    print(f"Total time: {elapsed_time/60:.1f} minutes")
    print(f"Average time per mask: {elapsed_time/total_processed:.2f}s")
    print("="*60)
    print("\n✓ All done!")


if __name__ == '__main__':
    main()
