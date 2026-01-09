import torch

model = torch.hub.load('ultralytics/yolov5', 'custom', path='models/best.pt', force_reload=False)
print('Class names:', model.names)
print('Number of classes:', len(model.names))
