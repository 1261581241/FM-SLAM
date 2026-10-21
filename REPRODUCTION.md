# Experimental Reproduction Guide

This guide provides step-by-step instructions to reproduce all experiments in the FM-SLAM paper using **FastSAM**.

## Prerequisites

### Hardware Requirements
- **CPU**: Multi-core processor (Intel i7 or equivalent)
- **GPU**: NVIDIA GPU with CUDA support (for FastSAM)
  - Tested on: RTX 4060 (8GB VRAM)
  - Minimum: GTX 1060 (6GB VRAM)
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: ~50GB free space

### Software Requirements
- Ubuntu 18.04/20.04
- CUDA 11.0+ and cuDNN
- Python 3.7+
- Required packages:
  ```bash
  pip install ultralytics opencv-python numpy torch evo
  ```

## Step 1: Download Datasets

### TUM RGB-D Dataset

Download the Freiburg3 sequences:

```bash
# Create dataset directory
mkdir -p Dataset
cd Dataset

# Walking sequences
wget https://vision.in.tum.de/rgbd/dataset/freiburg3/rgbd_dataset_freiburg3_walking_xyz.tgz
wget https://vision.in.tum.de/rgbd/dataset/freiburg3/rgbd_dataset_freiburg3_walking_rpy.tgz
wget https://vision.in.tum.de/rgbd/dataset/freiburg3/rgbd_dataset_freiburg3_walking_halfsphere.tgz
wget https://vision.in.tum.de/rgbd/dataset/freiburg3/rgbd_dataset_freiburg3_walking_static.tgz

# Sitting sequences
wget https://vision.in.tum.de/rgbd/dataset/freiburg3/rgbd_dataset_freiburg3_sitting_xyz.tgz
wget https://vision.in.tum.de/rgbd/dataset/freiburg3/rgbd_dataset_freiburg3_sitting_rpy.tgz
wget https://vision.in.tum.de/rgbd/dataset/freiburg3/rgbd_dataset_freiburg3_sitting_halfsphere.tgz

# Extract all
for file in *.tgz; do tar -xzf $file; done
cd ..
```

### Bonn RGB-D Dynamic People Dataset

Download from: http://www.ipb.uni-bonn.de/data/rgbd-dynamic-dataset/

```bash
cd Dataset
# Download bonn_crowd, bonn_crowd2, bonn_crowd3
# Place them in Dataset/ directory
cd ..
```

## Step 2: Build FM-SLAM

```bash
# Extract ORB vocabulary
cd Vocabulary
tar -xzf ORBvoc.txt.tar.gz
cd ..

# Build
chmod +x build.sh
./build.sh
```

## Step 3: Generate Association Files

Each TUM sequence needs an association file that matches RGB images with depth images by timestamp.

### Generate for all sequences:

```bash
# Walking sequences
python scripts/create_associations.py --dataset Dataset/rgbd_dataset_freiburg3_walking_xyz
python scripts/create_associations.py --dataset Dataset/rgbd_dataset_freiburg3_walking_rpy
python scripts/create_associations.py --dataset Dataset/rgbd_dataset_freiburg3_walking_halfsphere
python scripts/create_associations.py --dataset Dataset/rgbd_dataset_freiburg3_walking_static

# Sitting sequences
python scripts/create_associations.py --dataset Dataset/rgbd_dataset_freiburg3_sitting_xyz
python scripts/create_associations.py --dataset Dataset/rgbd_dataset_freiburg3_sitting_rpy
python scripts/create_associations.py --dataset Dataset/rgbd_dataset_freiburg3_sitting_halfsphere
```

This will create `associations.txt` in each dataset directory.

**Note**: Bonn sequences may have different file structures. Check the dataset documentation if needed.

## Step 4: Download FastSAM Model

```bash
# Download FastSAM-x model
wget https://github.com/CASIA-IVA-Lab/FastSAM/releases/download/v1.0.0/FastSAM-x.pt
```

## Step 5: Generate Masks with FastSAM

### Option A: Batch Processing (All Sequences)

Generate masks for all sequences at once:

```bash
python scripts/batch_generate_masks.py \
    --model FastSAM-x.pt \
    --dataset-root Dataset \
    --output-root masks \
    --conf 0.25
```

**Expected time**: ~2-3 hours for all 10 sequences on RTX 4060

### Option B: Single Sequence

Generate masks for one sequence:

```bash
python scripts/generate_masks_fastsam.py \
    --model FastSAM-x.pt \
    --dataset Dataset/rgbd_dataset_freiburg3_walking_xyz \
    --output masks/rgbd_dataset_freiburg3_walking_xyz
```

### Mask Generation Output

For each sequence, you'll get:
```
masks/
├── rgbd_dataset_freiburg3_walking_xyz/
│   ├── 1305031102.175304.png  (binary mask)
│   ├── 1305031102.211214.png
│   └── ...
│   └── timing_log.json  (inference timing)
```

## Step 6: Run Ablation Study

Run the complete ablation study (M0-M3, 5 runs each):

```bash
./scripts/run_ablation_study.sh \
    /path/to/Dataset \
    /path/to/masks \
    ./ablation_results
```

**Expected time**: ~8-10 hours for 4 sequences × 4 methods × 5 runs

### What This Does

For each sequence:
- **M0** (Baseline): ORB-SLAM2 without any mask
- **M1** (Flow+RANSAC): Uses optical flow + RANSAC masks
- **M2** (M1+DBSCAN): M1 + DBSCAN clustering
- **M3** (FastSAM): Uses FastSAM-generated masks

### Output Structure

```
ablation_results/
├── rgbd_dataset_freiburg3_walking_xyz/
│   ├── M0/
│   │   ├── run1.log
│   │   ├── CameraTrajectory_run1.txt
│   │   ├── ... (run2-5)
│   ├── M1/, M2/, M3/  (same structure)
```

## Step 7: Evaluate Results

Calculate ATE (Absolute Trajectory Error) for all runs:

```bash
python scripts/evaluate_ate.py \
    --results ./ablation_results \
    --groundtruth ./evaluation/Ground_truth \
    --output ate_results.json
```

### Output

This generates:
1. `ate_results.json` - Detailed results with all runs
2. Summary table printed to console

Example output:
```
Summary Table (Median ATE in meters)
============================================================
Sequence                       M0       M1       M2       M3
------------------------------------------------------------
walking_xyz                0.672059 0.421323 0.388498 0.015477
walking_rpy                0.775004 0.653212 0.612345 0.034123
...
```

## Step 8: Generate Paper Tables

You can use the `ate_results.json` to create tables for your paper:

```python
import json

with open('ate_results.json') as f:
    results = json.load(f)

# Print LaTeX table
for seq, methods in results.items():
    seq_name = seq.replace('rgbd_dataset_freiburg3_', '')
    row = f"{seq_name} & "
    row += " & ".join([f"{methods[m]['median']:.6f}" for m in ['M0', 'M1', 'M2', 'M3']])
    row += " \\\\"
    print(row)
```

## Step 9: Supplementary Experiments (Optional)

Run experiments on sitting and bonn_crowd sequences:

```bash
# Similar to ablation study, but for supplementary sequences
# Only compare ORB-SLAM2 (M0) vs FM-SLAM (M3)

for seq in sitting_xyz sitting_rpy sitting_halfsphere bonn_crowd bonn_crowd2 bonn_crowd3; do
    # Run M0 (baseline)
    ./Examples/RGB-D/rgbd_tum \
        Vocabulary/ORBvoc.txt \
        Examples/RGB-D/TUM3.yaml \
        Dataset/rgbd_dataset_freiburg3_$seq \
        Examples/RGB-D/associations/fr3_$seq.txt
    
    # Run M3 (FastSAM)
    ./Examples/RGB-D/rgbd_tum \
        Vocabulary/ORBvoc.txt \
        Examples/RGB-D/TUM3.yaml \
        Dataset/rgbd_dataset_freiburg3_$seq \
        Examples/RGB-D/associations/fr3_$seq.txt \
        masks/rgbd_dataset_freiburg3_$seq
done
```

## Expected Results

After completing all experiments, you should obtain results matching the paper:

### Ablation Study (Median ATE)

| Sequence | M0 (Baseline) | M1 | M2 | M3 (FastSAM) | Improvement |
|----------|--------------|----|----|--------------|-------------|
| walking_xyz | 0.672m | 0.421m | 0.388m | **0.016m** | 97.7% |
| walking_rpy | 0.775m | 0.653m | 0.612m | **0.034m** | 95.6% |
| walking_halfsphere | 0.353m | 0.305m | 0.291m | **0.021m** | 94.0% |
| walking_static | 0.222m | 0.183m | 0.169m | **0.017m** | 92.3% |

### Feature Retention

FastSAM retains **82.3%** of features on average, with no over-filtering issue.

## Troubleshooting

### CUDA Out of Memory

If you encounter GPU memory issues during FastSAM inference:

```python
# Reduce image size in generate_masks_fastsam.py
# Change: imgsz=640
# To: imgsz=512 or imgsz=416
```

### SLAM Tracking Lost

If SLAM tracking is lost:
1. Check that ground truth and associations are correct
2. Verify camera parameters in TUM3.yaml
3. Ensure masks are correctly generated (binary: 0=static, 255=dynamic)

### Slow FastSAM Inference

FastSAM requires GPU. On CPU it's very slow (~10-20s per frame).
- Solution: Use a GPU, or consider pre-generated masks from the paper

## Verification

To verify your reproduction matches the paper:

```bash
# Compare your ate_results.json with paper's experimental_results/raw_data.json
python scripts/compare_results.py \
    --yours ate_results.json \
    --paper experimental_results/raw_data.json
```

Expected differences: ±0.005m (due to random initialization, RANSAC, etc.)

## Time Estimates

| Task | Time | Notes |
|------|------|-------|
| Dataset download | 1-2 hours | Depends on network |
| FastSAM mask generation | 2-3 hours | All 10 sequences on GPU |
| Ablation study (80 runs) | 8-10 hours | 4 seq × 4 methods × 5 runs |
| Supplementary (60 runs) | 6-8 hours | 6 seq × 2 methods × 5 runs |
| **Total** | **~20 hours** | Can run overnight |

## Questions?

If you encounter issues:
1. Check this document first
2. Review README.md
3. Check experimental_results/README.md for data format
4. Open an issue on GitHub

---

**Note**: All experiments use FastSAM for dynamic object segmentation as described in the paper. The two-phase architecture (offline FastSAM + online SLAM) ensures both accuracy and real-time performance.
