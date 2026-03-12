# 🚀 Démarrage rapide - Accélération matérielle

## Installation en 3 étapes

### 1️⃣ Installer les dépendances

```powershell
python scripts/install_openvino.py
```

### 2️⃣ Convertir les modèles

```powershell
python scripts/convert_to_openvino.py --model models/best.pt
```

### 3️⃣ Activer dans config.py

```python
PREFERRED_BACKEND = 'openvino'
USE_OPENVINO = True
```

## ✅ Vérification

```powershell
# Tester le système
python scripts/benchmark_acceleration.py

# Démarrer l'application
python run_app.py
```

## 📊 Résultats attendus

- **FPS**: 5 → 12-18 (2-3x plus rapide)
- **CPU**: 70% → 40% (réduction de 30%)
- **Latence**: 200ms → 80ms (2.5x plus rapide)

## 🆘 Problèmes?

Consultez [ACCELERATION_GUIDE.md](ACCELERATION_GUIDE.md) pour le guide complet.

---

**Optimisé pour Intel Core i3 + GPU intégré Intel** 🎯