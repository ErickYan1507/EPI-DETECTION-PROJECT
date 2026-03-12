import torch
model = torch.hub.load('ultralytics/yolov5', 'custom', path='models/best.pt')
print("Classes du modèle:", model.names)
print("Nombre de classes:", len(model.names))