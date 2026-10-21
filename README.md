# FM-SLAM: FastSAM-Enhanced Visual SLAM for Dynamic Scenes

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Overview

FM-SLAM is a robust RGB-D visual SLAM system designed for dynamic environments. It leverages **FastSAM** (Fast Segment Anything Model) for accurate dynamic object segmentation, achieving both high localization accuracy and real-time performance.

**Key Features:**
- 🎯 **High Accuracy**: 95.2% ATE improvement over ORB-SLAM2 baseline
- ⚡ **Real-time Performance**: 67 FPS on CPU-only tracking
- 🎭 **Two-Phase Architecture**: Offline segmentation + Online tracking
- 🔧 **Easy Integration**: Minimal modification to ORB-SLAM2 core

## Architecture

FM-SLAM employs a two-phase architecture:

1. **Offline Phase**: FastSAM generates high-quality dynamic object masks
2. **Online Phase**: ORB-SLAM2 with early feature filtering for real-time tracking

This design ensures both segmentation accuracy (FastSAM) and runtime efficiency (pre-generated masks).

## Installation

### Prerequisites

- Ubuntu 18.04 or 20.04
- C++11 Compiler
- CMake >= 3.0
- OpenCV >= 3.2
- Eigen3
- Pangolin
- Python 3.x (for mask generation)

### Dependencies

```bash
# Install ORB-SLAM2 dependencies
sudo apt-get install libeigen3-dev libopencv-dev
```

### Build

```bash
cd FM-SLAM
chmod +x build.sh
./build.sh
```

## Mask Generation with FastSAM

### Install FastSAM

```bash
pip install ultralytics
```

### Download FastSAM Model

```bash
# Download FastSAM-x model
wget https://github.com/CASIA-IVA-Lab/FastSAM/releases/download/v1.0.0/FastSAM-x.pt
```

### Generate Masks

```bash
python scripts/generate_masks_fastsam.py \
    --model FastSAM-x.pt \
    --dataset /path/to/dataset \
    --output /path/to/masks
```

The script will:
- Detect and segment persons (COCO class 0)
- Generate binary masks (0=static, 255=dynamic)
- Save masks with same filenames as RGB images

## Running FM-SLAM

### RGB-D Mode (TUM Dataset)

```bash
./Examples/RGB-D/rgbd_tum \
    Vocabulary/ORBvoc.txt \
    Examples/RGB-D/TUM3.yaml \
    /path/to/dataset \
    /path/to/dataset/associations.txt \
    /path/to/masks
```

### Without Masks (Baseline ORB-SLAM2)

```bash
./Examples/RGB-D/rgbd_tum \
    Vocabulary/ORBvoc.txt \
    Examples/RGB-D/TUM3.yaml \
    /path/to/dataset \
    /path/to/dataset/associations.txt
```

## Datasets

We evaluate FM-SLAM on:
- **TUM RGB-D**: Freiburg3 sequences (walking & sitting)
- **Bonn RGB-D**: Crowd sequences

Download datasets:
- TUM: https://vision.in.tum.de/data/datasets/rgbd-dataset
- Bonn: http://www.ipb.uni-bonn.de/data/rgbd-dynamic-dataset/

## Experimental Results

### Accuracy (ATE in meters, median of 5 runs)

| Sequence | ORB-SLAM2 | FM-SLAM | Improvement |
|----------|-----------|---------|-------------|
| walking_xyz | 0.672 | **0.016** | 97.7% |
| walking_rpy | 0.775 | **0.034** | 95.6% |
| walking_halfsphere | 0.353 | **0.021** | 94.0% |
| walking_static | 0.222 | **0.017** | 92.3% |

**Average: 95.2% improvement**

### Runtime Performance

| Component | Time (ms) | Notes |
|-----------|-----------|-------|
| ORB Extraction | 7.0 | Standard |
| Feature Filtering | <0.1 | Negligible overhead |
| Tracking | 7.9 | Standard |
| **Total (Online)** | **14.9** | **67 FPS** |
| FastSAM (Offline) | 56.0 | GPU RTX 4060 |

### Feature Retention Rate

| Sequence | Features Filtered | Features Kept | Retention |
|----------|------------------|---------------|-----------|
| walking_xyz | 165/frame | 835/frame | 83.5% |
| walking_rpy | 188/frame | 812/frame | 81.2% |
| walking_halfsphere | 181/frame | 819/frame | 81.9% |
| walking_static | 173/frame | 827/frame | 82.7% |

**Average: 82.3% retention** - no over-filtering issue

## Repository Structure

```
FM-SLAM/
├── src/                          # Core SLAM implementation
├── include/                      # Header files
├── Examples/                     # Example programs
├── Thirdparty/                   # Third-party libraries
├── Vocabulary/                   # ORB vocabulary
├── scripts/                      # Mask generation script
│   └── generate_masks_fastsam.py
├── experimental_results/         # Experimental data
│   ├── raw_data.json            # 165 runs ATE data
│   ├── feature_retention*.csv   # Feature statistics
│   ├── runtime_breakdown*.csv   # Runtime analysis
│   └── experimental_raw_logs.tar.gz  # Full logs
├── docs/                         # Documentation
├── config_dbscan.yaml           # DBSCAN parameters
├── CMakeLists.txt
└── README.md
```

## Experimental Data

All experimental results (165 SLAM runs) are provided in `experimental_results/`:

- `raw_data.json`: ATE results for all experiments
- `feature_retention_all_sequences.csv`: Feature filtering statistics
- `runtime_breakdown_summary.csv`: Runtime performance breakdown
- `experimental_raw_logs.tar.gz`: Complete logs (extract for details)

See `experimental_results/README.md` for detailed data description and reproduction guide.

## Citation

If you use FM-SLAM in your research, please cite:

```bibtex
@article{fm-slam2026,
  title={FM-SLAM: FastSAM-Enhanced Visual SLAM for Dynamic Scenes},
  author={[Your Name]},
  journal={[Journal Name]},
  year={2026}
}
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

Portions of the code are derived from [ORB-SLAM2](https://github.com/raulmur/ORB_SLAM2) (GPLv3).

## Acknowledgments

- **ORB-SLAM2**: Raúl Mur-Artal, José M.M. Montiel, and Juan D. Tardós
- **FastSAM**: CASIA-IVA-Lab

## Contact

For questions or issues, please open an issue on GitHub or contact [your-email@domain.com].

---

**Note**: This is a research project. For production use, additional testing and optimization are recommended.
