#!/bin/bash
# Run ablation study experiments (M0-M3) on all walking sequences
# This script reproduces the ablation study results in the paper

set -e  # Exit on error

# Configuration
SLAM_EXECUTABLE="./Examples/RGB-D/rgbd_tum"
VOCABULARY="./Vocabulary/ORBvoc.txt"
CAMERA_PARAMS="./Examples/RGB-D/TUM3.yaml"
DATASET_ROOT="${1:-/path/to/Dataset}"
MASK_ROOT="${2:-/path/to/masks}"
OUTPUT_ROOT="${3:-./ablation_results}"

# Check if vocabulary is extracted
if [ ! -f "$VOCABULARY" ]; then
    echo "Error: ORB vocabulary not found!"
    echo "Please extract it first:"
    echo "  cd Vocabulary && tar -xzf ORBvoc.txt.tar.gz"
    exit 1
fi

# Check if SLAM executable exists
if [ ! -f "$SLAM_EXECUTABLE" ]; then
    echo "Error: SLAM executable not found!"
    echo "Please build the project first:"
    echo "  ./build.sh"
    exit 1
fi

# Sequences to test
SEQUENCES=(
    "rgbd_dataset_freiburg3_walking_xyz"
    "rgbd_dataset_freiburg3_walking_rpy"
    "rgbd_dataset_freiburg3_walking_halfsphere"
    "rgbd_dataset_freiburg3_walking_static"
)

# Methods
# M0: Baseline (no mask)
# M1: Flow+RANSAC
# M2: Flow+RANSAC+DBSCAN
# M3: FastSAM

echo "========================================"
echo "FM-SLAM Ablation Study"
echo "========================================"
echo "Dataset root: $DATASET_ROOT"
echo "Mask root: $MASK_ROOT"
echo "Output root: $OUTPUT_ROOT"
echo "Sequences: ${#SEQUENCES[@]}"
echo "========================================"

# Create output directories
for seq in "${SEQUENCES[@]}"; do
    for method in M0 M1 M2 M3; do
        mkdir -p "$OUTPUT_ROOT/${seq}/$method"
    done
done

# Run experiments
TOTAL_RUNS=0
SUCCESS_RUNS=0

for seq in "${SEQUENCES[@]}"; do
    echo ""
    echo "========================================"
    echo "Sequence: $seq"
    echo "========================================"

    DATASET_PATH="$DATASET_ROOT/$seq"
    # Try dataset directory first, then Examples/RGB-D/associations/
    ASSOCIATION_FILE="$DATASET_PATH/associations.txt"

    if [ ! -f "$ASSOCIATION_FILE" ]; then
        ASSOCIATION_FILE="./Examples/RGB-D/associations/fr3_$(echo $seq | cut -d'_' -f4-).txt"
    fi

    if [ ! -f "$ASSOCIATION_FILE" ]; then
        echo "Warning: Association file not found!"
        echo "  Tried: $DATASET_PATH/associations.txt"
        echo "  Tried: ./Examples/RGB-D/associations/fr3_$(echo $seq | cut -d'_' -f4-).txt"
        echo "  Please run: python scripts/create_associations.py --dataset $DATASET_PATH"
        echo "Skipping $seq"
        continue
    fi

    # Run 5 times for each method
    for run in {1..5}; do

        # M0: Baseline (no mask)
        echo ""
        echo "[$seq] M0 Run $run (Baseline)..."
        OUTPUT_DIR="$OUTPUT_ROOT/${seq}/M0"
        TOTAL_RUNS=$((TOTAL_RUNS + 1))

        $SLAM_EXECUTABLE \
            "$VOCABULARY" \
            "$CAMERA_PARAMS" \
            "$DATASET_PATH" \
            "$ASSOCIATION_FILE" \
            > "$OUTPUT_DIR/run${run}.log" 2>&1 && \
        mv CameraTrajectory.txt "$OUTPUT_DIR/CameraTrajectory_run${run}.txt" 2>/dev/null && \
        SUCCESS_RUNS=$((SUCCESS_RUNS + 1)) && \
        echo "  ✓ M0 Run $run completed" || \
        echo "  ✗ M0 Run $run failed"

        sleep 2

        # M1: Flow+RANSAC masks
        if [ -d "$MASK_ROOT/${seq}_M1" ]; then
            echo "[$seq] M1 Run $run (Flow+RANSAC)..."
            OUTPUT_DIR="$OUTPUT_ROOT/${seq}/M1"
            TOTAL_RUNS=$((TOTAL_RUNS + 1))

            $SLAM_EXECUTABLE \
                "$VOCABULARY" \
                "$CAMERA_PARAMS" \
                "$DATASET_PATH" \
                "$ASSOCIATION_FILE" \
                "$MASK_ROOT/${seq}_M1" \
                > "$OUTPUT_DIR/run${run}.log" 2>&1 && \
            mv CameraTrajectory.txt "$OUTPUT_DIR/CameraTrajectory_run${run}.txt" 2>/dev/null && \
            SUCCESS_RUNS=$((SUCCESS_RUNS + 1)) && \
            echo "  ✓ M1 Run $run completed" || \
            echo "  ✗ M1 Run $run failed"

            sleep 2
        fi

        # M2: Flow+RANSAC+DBSCAN masks
        if [ -d "$MASK_ROOT/${seq}_M2" ]; then
            echo "[$seq] M2 Run $run (Flow+RANSAC+DBSCAN)..."
            OUTPUT_DIR="$OUTPUT_ROOT/${seq}/M2"
            TOTAL_RUNS=$((TOTAL_RUNS + 1))

            $SLAM_EXECUTABLE \
                "$VOCABULARY" \
                "$CAMERA_PARAMS" \
                "$DATASET_PATH" \
                "$ASSOCIATION_FILE" \
                "$MASK_ROOT/${seq}_M2" \
                > "$OUTPUT_DIR/run${run}.log" 2>&1 && \
            mv CameraTrajectory.txt "$OUTPUT_DIR/CameraTrajectory_run${run}.txt" 2>/dev/null && \
            SUCCESS_RUNS=$((SUCCESS_RUNS + 1)) && \
            echo "  ✓ M2 Run $run completed" || \
            echo "  ✗ M2 Run $run failed"

            sleep 2
        fi

        # M3: FastSAM masks
        if [ -d "$MASK_ROOT/$seq" ]; then
            echo "[$seq] M3 Run $run (FastSAM)..."
            OUTPUT_DIR="$OUTPUT_ROOT/${seq}/M3"
            TOTAL_RUNS=$((TOTAL_RUNS + 1))

            $SLAM_EXECUTABLE \
                "$VOCABULARY" \
                "$CAMERA_PARAMS" \
                "$DATASET_PATH" \
                "$ASSOCIATION_FILE" \
                "$MASK_ROOT/$seq" \
                > "$OUTPUT_DIR/run${run}.log" 2>&1 && \
            mv CameraTrajectory.txt "$OUTPUT_DIR/CameraTrajectory_run${run}.txt" 2>/dev/null && \
            SUCCESS_RUNS=$((SUCCESS_RUNS + 1)) && \
            echo "  ✓ M3 Run $run completed" || \
            echo "  ✗ M3 Run $run failed"

            sleep 2
        fi
    done
done

# Summary
echo ""
echo "========================================"
echo "Experiment Summary"
echo "========================================"
echo "Total runs: $TOTAL_RUNS"
echo "Successful runs: $SUCCESS_RUNS"
echo "Failed runs: $((TOTAL_RUNS - SUCCESS_RUNS))"
echo "Success rate: $(awk "BEGIN {printf \"%.1f\", 100*$SUCCESS_RUNS/$TOTAL_RUNS}")%"
echo "========================================"
echo ""
echo "Results saved in: $OUTPUT_ROOT"
echo ""
echo "Next steps:"
echo "1. Evaluate ATE: python scripts/evaluate_ate.py --results $OUTPUT_ROOT"
echo "2. Generate tables: python scripts/generate_tables.py --results $OUTPUT_ROOT"
