"""
Script de benchmark pour comparer les performances des différents backends
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import cv2
import time
import numpy as np
from app.logger import logger
from app.hardware_optimizer import HardwareOptimizer, OPENVINO_AVAILABLE, ONNX_AVAILABLE, TORCH_AVAILABLE


def run_benchmark(detector, image, num_iterations=50, warmup=5):
    """
    Exécuter un benchmark sur un détecteur
    
    Args:
        detector: Instance du détecteur
        image: Image de test
        num_iterations: Nombre d'itérations
        warmup: Nombre d'itérations de préchauffage
        
    Returns:
        dict avec les métriques de performance
    """
    # Warmup
    logger.info(f"Préchauffage ({warmup} itérations)...")
    for _ in range(warmup):
        detector.detect(image)
    
    # Benchmark
    logger.info(f"Benchmark ({num_iterations} itérations)...")
    inference_times = []
    total_times = []
    
    for i in range(num_iterations):
        start = time.perf_counter()
        detections, stats = detector.detect(image)
        total_time = (time.perf_counter() - start) * 1000
        
        total_times.append(total_time)
        inference_times.append(stats.get('inference_ms', total_time))
        
        if (i + 1) % 10 == 0:
            logger.info(f"  {i + 1}/{num_iterations} itérations...")
    
    # Calculer les statistiques
    avg_inference = np.mean(inference_times)
    avg_total = np.mean(total_times)
    fps = 1000 / avg_total if avg_total > 0 else 0
    
    return {
        'avg_inference_ms': round(avg_inference, 2),
        'avg_total_ms': round(avg_total, 2),
        'min_total_ms': round(np.min(total_times), 2),
        'max_total_ms': round(np.max(total_times), 2),
        'std_total_ms': round(np.std(total_times), 2),
        'fps': round(fps, 2)
    }


def main():
    logger.info("=" * 70)
    logger.info("BENCHMARK D'ACCÉLÉRATION MATÉRIELLE")
    logger.info("=" * 70)
    
    # Vérifier les backends disponibles
    logger.info("\nBackends disponibles:")
    logger.info(f"  OpenVINO: {'✓' if OPENVINO_AVAILABLE else '✗'}")
    logger.info(f"  ONNX Runtime: {'✓' if ONNX_AVAILABLE else '✗'}")
    logger.info(f"  PyTorch: {'✓' if TORCH_AVAILABLE else '✗'}")
    
    # Charger une image de test
    test_images = list(Path('images').glob('*.jpg'))
    if not test_images:
        logger.error("Aucune image de test trouvée dans le dossier 'images/'")
        sys.exit(1)
    
    test_image_path = test_images[0]
    logger.info(f"\nImage de test: {test_image_path}")
    
    image = cv2.imread(str(test_image_path))
    if image is None:
        logger.error(f"Impossible de charger l'image: {test_image_path}")
        sys.exit(1)
    
    logger.info(f"Résolution: {image.shape[1]}x{image.shape[0]}")
    
    # Benchmarks
    results = {}
    
    # Test OpenVINO
    if OPENVINO_AVAILABLE:
        logger.info("\n" + "=" * 70)
        logger.info("BENCHMARK OPENVINO")
        logger.info("=" * 70)
        try:
            optimizer = HardwareOptimizer(preferred_backend='openvino')
            if optimizer.backend_used == 'openvino':
                info = optimizer.get_backend_info()
                logger.info(f"Device: {info.get('device_info', {}).get('device', 'Unknown')}")
                
                results['openvino'] = run_benchmark(optimizer, image)
                logger.info(f"\nRésultats OpenVINO:")
                for key, value in results['openvino'].items():
                    logger.info(f"  {key}: {value}")
            else:
                logger.warning("OpenVINO non disponible, utilisé: " + optimizer.backend_used)
        except Exception as e:
            logger.error(f"Erreur benchmark OpenVINO: {e}")
    
    # Test ONNX
    if ONNX_AVAILABLE:
        logger.info("\n" + "=" * 70)
        logger.info("BENCHMARK ONNX RUNTIME")
        logger.info("=" * 70)
        try:
            optimizer = HardwareOptimizer(preferred_backend='onnx')
            if optimizer.backend_used == 'onnx':
                info = optimizer.get_backend_info()
                logger.info(f"Providers: {info.get('provider_info', {}).get('providers', [])}")
                
                results['onnx'] = run_benchmark(optimizer, image)
                logger.info(f"\nRésultats ONNX Runtime:")
                for key, value in results['onnx'].items():
                    logger.info(f"  {key}: {value}")
            else:
                logger.warning("ONNX non disponible, utilisé: " + optimizer.backend_used)
        except Exception as e:
            logger.error(f"Erreur benchmark ONNX: {e}")
    
    # Test PyTorch
    if TORCH_AVAILABLE:
        logger.info("\n" + "=" * 70)
        logger.info("BENCHMARK PYTORCH")
        logger.info("=" * 70)
        try:
            optimizer = HardwareOptimizer(preferred_backend='pytorch')
            if optimizer.backend_used == 'pytorch':
                info = optimizer.get_backend_info()
                logger.info(f"Device: {info.get('device', 'Unknown')}")
                
                results['pytorch'] = run_benchmark(optimizer, image)
                logger.info(f"\nRésultats PyTorch:")
                for key, value in results['pytorch'].items():
                    logger.info(f"  {key}: {value}")
        except Exception as e:
            logger.error(f"Erreur benchmark PyTorch: {e}")
    
    # Comparaison
    if len(results) > 1:
        logger.info("\n" + "=" * 70)
        logger.info("COMPARAISON DES BACKENDS")
        logger.info("=" * 70)
        
        # Tableau comparatif
        logger.info(f"\n{'Backend':<15} {'FPS':<10} {'Latence (ms)':<15} {'Accélération':<12}")
        logger.info("-" * 70)
        
        baseline_fps = results.get('pytorch', {}).get('fps', 1)
        
        for backend, metrics in sorted(results.items(), key=lambda x: x[1]['fps'], reverse=True):
            fps = metrics['fps']
            latency = metrics['avg_total_ms']
            speedup = fps / baseline_fps if baseline_fps > 0 else 1.0
            
            logger.info(f"{backend:<15} {fps:<10.2f} {latency:<15.2f} {speedup:<12.2f}x")
        
        # Recommandation
        best_backend = max(results.items(), key=lambda x: x[1]['fps'])
        logger.info(f"\n✓ Meilleur backend: {best_backend[0].upper()} ({best_backend[1]['fps']:.2f} FPS)")
        logger.info(f"\nPour utiliser ce backend, ajoutez dans config.py:")
        logger.info(f"  PREFERRED_BACKEND = '{best_backend[0]}'")
    
    logger.info("\n" + "=" * 70)


if __name__ == '__main__':
    main()