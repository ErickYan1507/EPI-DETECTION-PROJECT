import torch
import cv2

print('Testing YOLOv5 model...')

model = torch.hub.load('ultralytics/yolov5', 'custom', path='models/best.pt', force_reload=False)
print('Model loaded successfully')

img = cv2.imread('c.jpg')
if img is None:
    print('Image not found')
else:
    print(f'Image shape: {img.shape}')
    try:
        results = model(img)
        print('Detection successful!')
        print(f'Results: {results}')
    except Exception as e:
        print(f'Error: {e}')
