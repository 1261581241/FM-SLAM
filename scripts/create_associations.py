#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate association files for TUM RGB-D sequences
Associates RGB and depth images by timestamp
"""
import os
import sys
import argparse


def read_file_list(filename):
    """
    Read list of timestamps and data from file
    Format: timestamp data
    """
    file_list = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split()
            if len(parts) >= 2:
                timestamp = float(parts[0])
                data = ' '.join(parts[1:])
                file_list.append((timestamp, data))
    return file_list


def associate(first_list, second_list, offset=0.0, max_difference=0.02):
    """
    Associate two lists of (timestamp, data) by timestamp

    Args:
        first_list: List of (timestamp, data)
        second_list: List of (timestamp, data)
        offset: Time offset
        max_difference: Maximum time difference (seconds)

    Returns:
        List of matches: (timestamp1, data1, timestamp2, data2)
    """
    matches = []

    for a_stamp, a_data in first_list:
        best_match = None
        best_diff = max_difference

        for b_stamp, b_data in second_list:
            diff = abs((a_stamp + offset) - b_stamp)
            if diff < best_diff:
                best_diff = diff
                best_match = (b_stamp, b_data)

        if best_match:
            matches.append((a_stamp, a_data, best_match[0], best_match[1]))

    return matches


def create_association_file(dataset_path, output_path, offset=0.0, max_diff=0.02):
    """
    Create association file for RGB-D sequence

    Args:
        dataset_path: Path to sequence directory
        output_path: Output association file path
        offset: Time offset
        max_diff: Maximum time difference
    """
    rgb_file = os.path.join(dataset_path, 'rgb.txt')
    depth_file = os.path.join(dataset_path, 'depth.txt')

    if not os.path.exists(rgb_file):
        print(f"Error: {rgb_file} not found")
        return False

    if not os.path.exists(depth_file):
        print(f"Error: {depth_file} not found")
        return False

    # Read timestamps
    print(f"Reading {rgb_file}...")
    rgb_list = read_file_list(rgb_file)
    print(f"  Found {len(rgb_list)} RGB images")

    print(f"Reading {depth_file}...")
    depth_list = read_file_list(depth_file)
    print(f"  Found {len(depth_list)} depth images")

    # Associate
    print(f"Associating (max_diff={max_diff}s)...")
    matches = associate(rgb_list, depth_list, offset, max_diff)
    print(f"  Found {len(matches)} matches")

    # Write output
    with open(output_path, 'w') as f:
        f.write("# timestamp_rgb rgb_file timestamp_depth depth_file\n")
        for rgb_stamp, rgb_file, depth_stamp, depth_file in matches:
            f.write(f"{rgb_stamp:.6f} {rgb_file} {depth_stamp:.6f} {depth_file}\n")

    print(f"✓ Association file created: {output_path}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Generate association file for TUM RGB-D sequence'
    )
    parser.add_argument(
        '--dataset',
        type=str,
        required=True,
        help='Path to dataset sequence directory'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output association file (default: <dataset>/associations.txt)'
    )
    parser.add_argument(
        '--offset',
        type=float,
        default=0.0,
        help='Time offset (default: 0.0)'
    )
    parser.add_argument(
        '--max-diff',
        type=float,
        default=0.02,
        help='Maximum time difference in seconds (default: 0.02)'
    )

    args = parser.parse_args()

    if not args.output:
        args.output = os.path.join(args.dataset, 'associations.txt')

    success = create_association_file(
        args.dataset,
        args.output,
        args.offset,
        args.max_diff
    )

    if success:
        print("\n✓ Done!")
        print(f"\nUse with FM-SLAM:")
        print(f"  ./Examples/RGB-D/rgbd_tum Vocabulary/ORBvoc.txt \\")
        print(f"      Examples/RGB-D/TUM3.yaml {args.dataset} \\")
        print(f"      {args.output}")
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
