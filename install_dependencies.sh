#!/bin/bash
# Installation script for Rubi Robot dependencies
# Run these commands in your terminal

echo "========================================="
echo "Installing Rubi Robot Dependencies"
echo "========================================="

# Method 1: Using conda (recommended)
echo ""
echo "OPTION 1: Install using conda (recommended)"
echo "-----------------------------------------"
echo "Run these commands one by one:"
echo ""
echo "1. Activate the rubi_robot environment:"
echo "   conda activate rubi_robot"
echo ""
echo "2. Install all dependencies:"
echo "   conda install -c conda-forge opencv pytorch torchvision torchaudio ultralytics numpy -y"
echo ""
echo "3. Verify installation:"
echo "   python -c \"import cv2; import torch; from ultralytics import YOLO; import numpy; print('✅ All dependencies installed successfully')\""

echo ""
echo "========================================="

# Method 2: Using pip
echo ""
echo "OPTION 2: Install using pip"
echo "--------------------------"
echo "Run these commands one by one:"
echo ""
echo "1. Activate the rubi_robot environment:"
echo "   conda activate rubi_robot"
echo ""
echo "2. Install all dependencies:"
echo "   pip install opencv-python torch ultralytics numpy"
echo ""
echo "3. Verify installation:"
echo "   python -c \"import cv2; import torch; from ultralytics import YOLO; import numpy; print('✅ All dependencies installed successfully')\""

echo ""
echo "========================================="
echo "After installation, run:"
echo "python test_robot.py"
echo "to test if YOLO detection now works correctly."
echo "========================================="