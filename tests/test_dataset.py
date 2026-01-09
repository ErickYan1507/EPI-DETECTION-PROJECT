"""Tests for dataset integrity and training utilities."""

import pytest
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from train import (
    count_images,
    count_labels,
    check_dataset_structure,
    detect_num_classes,
    create_data_yaml
)


class TestDatasetIntegrity:
    """Unit tests for dataset utilities."""
    
    @pytest.fixture
    def dataset_path(self):
        """Provide dataset path."""
        return 'dataset'
    
    def test_count_images_train(self, dataset_path):
        """Test counting training images."""
        count = count_images(dataset_path, 'train')
        assert count > 0, "Training images count should be > 0"
        assert count >= 128, "Should have at least 128 training images"
    
    def test_count_images_val(self, dataset_path):
        """Test counting validation images."""
        count = count_images(dataset_path, 'val')
        assert count > 0, "Validation images count should be > 0"
        assert count >= 128, "Should have at least 128 validation images"
    
    def test_count_labels_train(self, dataset_path):
        """Test counting training labels."""
        count = count_labels(dataset_path, 'train')
        assert count > 0, "Training labels count should be > 0"
    
    def test_count_labels_val(self, dataset_path):
        """Test counting validation labels."""
        count = count_labels(dataset_path, 'val')
        assert count > 0, "Validation labels count should be > 0"
    
    @pytest.mark.integration
    def test_check_dataset_structure(self, dataset_path):
        """Test full dataset structure check."""
        result = check_dataset_structure(dataset_path)
        assert result is True, "Dataset structure check should pass"
    
    @pytest.mark.integration
    def test_dataset_image_label_parity(self, dataset_path):
        """Test that images and labels are in reasonable proportion."""
        train_imgs = count_images(dataset_path, 'train')
        train_labels = count_labels(dataset_path, 'train')
        val_imgs = count_images(dataset_path, 'val')
        val_labels = count_labels(dataset_path, 'val')
        
        # Allow up to 10% mismatch (some images might have multiple objects)
        train_ratio = train_labels / train_imgs if train_imgs > 0 else 0
        val_ratio = val_labels / val_imgs if val_imgs > 0 else 0
        
        assert 0.5 <= train_ratio <= 1.5, f"Train image/label ratio {train_ratio} is invalid"
        assert 0.5 <= val_ratio <= 1.5, f"Val image/label ratio {val_ratio} is invalid"
    
    @pytest.mark.integration
    def test_detect_num_classes(self, dataset_path):
        """Test class detection from labels."""
        num_classes = detect_num_classes(dataset_path)
        assert num_classes > 0, "Should detect at least 1 class"
        assert num_classes <= 10, "Should detect reasonable number of classes"
    
    @pytest.mark.integration
    def test_create_data_yaml(self, dataset_path):
        """Test YAML file creation."""
        class_names = ['helmet', 'vest', 'glasses', 'person', 'boots']
        yaml_path = create_data_yaml(dataset_path, class_names)
        
        assert yaml_path.exists(), "YAML file should be created"
        
        # Verify content
        content = yaml_path.read_text()
        assert 'path:' in content
        assert 'train:' in content
        assert 'val:' in content
        assert 'nc:' in content
        assert 'names:' in content


class TestDatasetValidation:
    """Tests for dataset file validation."""
    
    @pytest.fixture
    def dataset_path(self):
        """Provide dataset path."""
        return 'dataset'
    
    def test_image_files_readable(self, dataset_path):
        """Test that image files are readable."""
        from PIL import Image
        
        img_path = Path(dataset_path) / 'images' / 'train'
        if not img_path.exists():
            pytest.skip("Train images directory not found")
        
        image_files = list(img_path.glob('*.[jp][pn][g]*')) + list(img_path.glob('*.jpeg'))
        assert len(image_files) > 0, "Should have image files"
        
        # Test first 5 images
        for img_file in image_files[:5]:
            try:
                img = Image.open(img_file)
                assert img.size[0] > 0 and img.size[1] > 0, f"Image {img_file} has invalid size"
            except Exception as e:
                pytest.fail(f"Cannot read image {img_file}: {e}")
    
    def test_label_files_valid_format(self, dataset_path):
        """Test that label files have valid YOLO format."""
        lbl_path = Path(dataset_path) / 'labels' / 'train'
        if not lbl_path.exists():
            pytest.skip("Train labels directory not found")
        
        label_files = list(lbl_path.glob('*.txt'))
        assert len(label_files) > 0, "Should have label files"
        
        # Test first 5 label files
        for lbl_file in label_files[:5]:
            lines = lbl_file.read_text().strip().split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    parts = line.split()
                    assert len(parts) >= 5, f"Line {i} in {lbl_file} has < 5 values"
                    try:
                        cls = int(parts[0])
                        coords = [float(p) for p in parts[1:5]]
                        assert all(0 <= c <= 1 for c in coords), f"Coordinates not normalized in {lbl_file}:{i}"
                    except ValueError as e:
                        pytest.fail(f"Invalid label format in {lbl_file}:{i}: {e}")
