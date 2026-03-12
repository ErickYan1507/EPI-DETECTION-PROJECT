# Guide d'accélération matérielle - Projet EPI Detection

Ce guide explique comment activer et utiliser l'accélération matérielle pour optimiser les performances de détection EPI sur votre système Intel Core i3 avec GPU intégré.

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Installation](#installation)
3. [Conversion des modèles](#conversion-des-modèles)
4. [Configuration](#configuration)
5. [Benchmarking](#benchmarking)
6. [Dépannage](#dépannage)

---

## 🎯 Vue d'ensemble

Le projet supporte maintenant trois backends d'inférence avec sélection automatique:

| Backend | Avantages | Utilisation recommandée |
|---------|-----------|-------------------------|
| **Intel OpenVINO** | • 2-4x plus rapide sur CPU Intel<br>• Support GPU Intel intégré<br>• Optimisations AVX2/AVX-512 | **Recommandé pour Intel Core i3** |
| **ONNX Runtime** | • Support DirectML (GPU Intel/AMD)<br>• Compatible multi-plateformes<br>• Bonne performance CPU | Fallback si OpenVINO indisponible |
| **PyTorch** | • Baseline de référence<br>• Support CUDA (NVIDIA) | Compatibilité maximale |

### Gains de performance attendus

Sur Intel Core i3 avec GPU intégré:
- **FPS caméra**: 5 → 12-18 FPS (2.4-3.6x plus rapide)
- **Latence image**: ~200ms → ~80-120ms (1.7-2.5x plus rapide)
- **Utilisation CPU**: 70-80% → 40-50% (-30-40%)

---

## 🔧 Installation

### Étape 1: Installer les dépendances

Exécutez le script d'installation automatique:

```powershell
python scripts/install_openvino.py
```

Ou installez manuellement:

```powershell
# Intel OpenVINO Runtime
pip install openvino openvino-dev

# ONNX et ONNX Runtime
pip install onnx onnxruntime

# DirectML pour GPU Intel/AMD (Windows uniquement)
pip install onnxruntime-directml
```

### Étape 2: Vérifier les drivers GPU Intel

1. Visitez: https://www.intel.com/content/www/us/en/download-center/home.html
2. Téléchargez les derniers drivers Intel Graphics
3. Installez et redémarrez votre ordinateur

### Étape 3: Vérifier l'installation

```python
# Tester OpenVINO
python -c "from openvino.runtime import Core; print('OpenVINO OK')"

# Tester ONNX Runtime
python -c "import onnxruntime; print('Providers:', onnxruntime.get_available_providers())"
```

---

## 🔄 Conversion des modèles

### Convertir tous les modèles

```powershell
# Convertir best.pt (modèle principal)
python scripts/convert_to_openvino.py --model models/best.pt

# Convertir d'autres modèles
python scripts/convert_to_openvino.py --model models/epi_detection_session_003.pt
python scripts/convert_to_openvino.py --model models/epi_detection_session_004.pt
```

### Options de conversion

```powershell
python scripts/convert_to_openvino.py --help

Options:
  --model MODEL         Chemin vers le modèle PyTorch (.pt)
  --img-size IMG_SIZE   Taille d'entrée (défaut: 640)
  --precision {FP32,FP16}  Précision (défaut: FP16 pour GPU)
```

### Résultat

La conversion crée:
```
models/
├── onnx/
│   └── best.onnx              # Modèle ONNX (intermédiaire)
└── openvino/
    ├── best.xml               # Modèle OpenVINO IR
    └── best.bin               # Poids du modèle
```

---

## ⚙️ Configuration

### Activer OpenVINO

Éditez `config.py`:

```python
# Backend préféré
PREFERRED_BACKEND = 'openvino'  # ou 'auto' pour sélection automatique

# Device OpenVINO
OPENVINO_DEVICE = 'AUTO'  # AUTO | GPU | CPU

# Activer OpenVINO
USE_OPENVINO = True
```

### Variables d'environnement (optionnel)

Créez/éditez `.env`:

```bash
# Backend d'inférence
PREFERRED_BACKEND=openvino

# Device OpenVINO
OPENVINO_DEVICE=AUTO

# Optimisations CPU
OMP_NUM_THREADS=4  # Nombre de threads (0 = auto)
```

### Configuration avancée

```python
# Dans config.py

# Pour GPU Intel uniquement
OPENVINO_DEVICE = 'GPU'

# Pour CPU multi-thread uniquement
OPENVINO_DEVICE = 'CPU'
CPU_NUM_THREADS = '4'  # ou '0' pour auto-detect
```

---

## 📊 Benchmarking

### Exécuter le benchmark

```powershell
python scripts/benchmark_acceleration.py
```

### Résultat exemple

```
==================================================================
BENCHMARK D'ACCÉLÉRATION MATÉRIELLE
==================================================================

Backends disponibles:
  OpenVINO: ✓
  ONNX Runtime: ✓
  PyTorch: ✓

Image de test: images/test.jpg
Résolution: 1920x1080

==================================================================
BENCHMARK OPENVINO
==================================================================
Device: GPU

Résultats OpenVINO:
  avg_inference_ms: 65.4
  avg_total_ms: 82.1
  fps: 12.18

==================================================================
COMPARAISON DES BACKENDS
==================================================================

Backend         FPS        Latence (ms)    Accélération
------------------------------------------------------------------
openvino        12.18      82.10           2.43x
onnx            9.45       105.82          1.89x
pytorch         5.01       199.60          1.00x

✓ Meilleur backend: OPENVINO (12.18 FPS)
```

---

## 🚀 Utilisation

### Démarrer l'application

```powershell
python run_app.py
```

L'application sélectionnera automatiquement le meilleur backend disponible.

### Vérifier le backend utilisé

Consultez les logs au démarrage:

```
[INFO] OpenVINO Runtime 2024.0.0 disponible
[INFO] Devices OpenVINO disponibles: ['CPU', 'GPU']
[INFO] Device sélectionné: GPU
[INFO] ✓ Backend OpenVINO initialisé avec succès
```

### API - Obtenir les infos backend

```python
# GET /api/hardware-info
{
  "backend": "openvino",
  "device": "GPU",
  "available_backends": {
    "openvino": true,
    "onnx": true,
    "pytorch": true
  }
}
```

---

## 🔍 Dépannage

### Problème: OpenVINO ne détecte pas le GPU

**Solution**:
1. Vérifiez les drivers Intel Graphics
2. Testez la détection GPU:
   ```python
   from openvino.runtime import Core
   core = Core()
   print("Devices:", core.available_devices)
   ```
3. Si seul 'CPU' apparaît, mettez à jour les drivers

### Problème: "ImportError: No module named 'openvino'"

**Solution**:
```powershell
pip install --upgrade openvino openvino-dev
```

### Problème: Performance ONNX plus lente que PyTorch

**Solution**:
1. Vérifiez que DirectML est disponible:
   ```python
   import onnxruntime as ort
   print(ort.get_available_providers())
   # Doit inclure 'DmlExecutionProvider'
   ```
2. Si absent, installez:
   ```powershell
   pip install onnxruntime-directml
   ```

### Problème: Première inférence très lente

**Comportement normal**: OpenVINO compile le modèle au premier chargement (JIT compilation).
- Première inférence: ~2-5 secondes
- Inférences suivantes: rapides

**Solution**: Le cache de compilation est automatique dans `./cache/`

### Problème: Erreur de conversion ONNX → OpenVINO

**Solution**:
```powershell
# Vérifier les versions
python -c "import openvino; print(openvino.runtime.get_version())"

# Réinstaller si nécessaire
pip uninstall openvino openvino-dev
pip install openvino openvino-dev
```

---

## 📈 Optimisations supplémentaires

### 1. Quantification INT8 (CPU uniquement)

Pour CPU très lent, quantifier en INT8:

```powershell
python scripts/optimize_models.py --quantize int8
```

Gain: 2-4x plus rapide sur CPU, précision légèrement réduite

### 2. Batch processing pour vidéos

Dans `config.py`:

```python
VIDEO_BATCH_SIZE = 4  # Traiter 4 frames à la fois
```

### 3. Async inference pour caméra

```python
USE_ASYNC_INFERENCE = True  # Inférence asynchrone
```

---

## 📚 Ressources

- [Documentation OpenVINO](https://docs.openvino.ai/)
- [ONNX Runtime Performance Tuning](https://onnxruntime.ai/docs/performance/)
- [Intel GPU Drivers](https://www.intel.com/content/www/us/en/download-center/home.html)

---

## ✅ Checklist de mise en production

- [ ] Drivers GPU Intel à jour
- [ ] OpenVINO installé et testé
- [ ] Modèles convertis (`.xml` + `.bin`)
- [ ] Benchmark exécuté (>10 FPS attendu)
- [ ] `PREFERRED_BACKEND='openvino'` dans config
- [ ] Application redémarrée
- [ ] Logs vérifiés (backend = openvino, device = GPU)

---

**Auteur**: Système d'accélération matérielle EPI Detection  
**Version**: 1.0  
**Dernière mise à jour**: 2026-01-09