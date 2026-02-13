import pandas as pd

# Charger les résultats
df = pd.read_csv('runs/train/epi_detection_session_003/results.csv')

# Métriques finales
print('=== MÉTRIQUES FINALES ===')
print(f'mAP_0.5: {df["     metrics/mAP_0.5"].iloc[-1]:.4f}')
print(f'mAP_0.5:0.95: {df["metrics/mAP_0.5:0.95"].iloc[-1]:.4f}')
print(f'Precision: {df["   metrics/precision"].iloc[-1]:.4f}')
print(f'Recall: {df["      metrics/recall"].iloc[-1]:.4f}')

# Analyse overfitting
train_loss = df['      train/box_loss'] + df['      train/obj_loss'] + df['      train/cls_loss']
val_loss = df['        val/box_loss'] + df['        val/obj_loss'] + df['        val/cls_loss']

print('\n=== ANALYSE OVERFITTING ===')
print(f'Train loss final: {train_loss.iloc[-1]:.4f}')
print(f'Val loss final: {val_loss.iloc[-1]:.4f}')
print(f'Ratio train/val: {train_loss.iloc[-1]/val_loss.iloc[-1]:.2f}')

# Évolution des métriques
print('\n=== ÉVOLUTION ===')
print(f'mAP_0.5 max: {df["     metrics/mAP_0.5"].max():.4f} (epoch {df["     metrics/mAP_0.5"].idxmax()})')
print(f'mAP_0.5:0.95 max: {df["metrics/mAP_0.5:0.95"].max():.4f} (epoch {df["metrics/mAP_0.5:0.95"].idxmax()})')