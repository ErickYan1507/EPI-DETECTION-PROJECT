import numpy as np

def test_resize_logic():
    """Test the resize logic with image 360x641"""
    # Simulate the original image
    image_h, image_w = 360, 641
    target_w, target_h = 480, 360
    
    aspect_ratio = image_w / image_h  # 641/360 = 1.78
    target_aspect = target_w / target_h  # 480/360 = 1.33
    
    print(f"Image: {image_h}x{image_w}")
    print(f"Target: {target_h}x{target_w}")
    print(f"Aspect ratio: {aspect_ratio:.2f}")
    print(f"Target aspect: {target_aspect:.2f}")
    
    if aspect_ratio > target_aspect:
        new_h = int(target_w / aspect_ratio)
        new_w = target_w
    else:
        new_w = int(target_h * aspect_ratio)
        new_h = target_h
    
    print(f"\nResized dimensions: {new_h}x{new_w}")
    print(f"Canvas dimensions: {target_h}x{target_w}")
    
    # Verify resized fits in canvas
    if new_w <= target_w and new_h <= target_h:
        print("[PASS] Resized image fits in canvas")
        return True
    else:
        print("[FAIL] Resized image EXCEEDS canvas!")
        return False

if __name__ == "__main__":
    test_resize_logic()
