"""
Script de conversion des modèles PyTorch YOLOv5 vers OpenVINO IR
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import torch
import argparse
from app.logger import logger

try:
    from openvino.tools import mo
    from openvino.runtime import Core, serialize
    OPENVINO_AVAILABLE = True
except ImportError:
    OPENVINO_AVAILABLE = False
    logger.error("OpenVINO n'est pas installé. Installez-le avec: pip install openvino openvino-dev")
    sys.exit(1)


def export_to_onnx(pytorch_model_path, onnx_output_path, img_size=640):
    """
    Exporter le modèle PyTorch vers ONNX
    
    Args:
        pytorch_model_path: Chemin vers le modèle .pt
        onnx_output_path: Chemin de sortie .onnx
        img_size: Taille d'entrée de l'image
    """
    logger.info(f"Chargement du modèle PyTorch: {pytorch_model_path}")
    
    # Charger le modèle YOLOv5
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=pytorch_model_path, force_reload=False)
    model.eval()
    
    # Créer un exemple d'entrée
    dummy_input = torch.randn(1, 3, img_size, img_size)
    
    # Exporter vers ONNX
    logger.info(f"Export vers ONNX: {onnx_output_path}")
    torch.onnx.export(
        model,
        dummy_input,
        onnx_output_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['images'],
        output_names=['output'],
        dynamic_axes={
            'images': {0: 'batch'},
            'output': {0: 'batch'}
        }
    )
    
    logger.info(f"✓ Modèle ONNX créé: {onnx_output_path}")
    return onnx_output_path


def convert_onnx_to_openvino(onnx_model_path, output_dir, precision='FP16'):
    """
    Convertir le modèle ONNX vers OpenVINO IR
    
    Args:
        onnx_model_path: Chemin vers le modèle .onnx
        output_dir: Répertoire de sortie pour les fichiers .xml et .bin
        precision: Précision du modèle ('FP32', 'FP16')
    """
    logger.info(f"Conversion ONNX → OpenVINO IR (précision: {precision})")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    model_name = Path(onnx_model_path).stem
    output_model = output_dir / model_name
    
    # Utiliser Model Optimizer pour convertir
    logger.info("Utilisation de Model Optimizer...")
    
    try:
        # OpenVINO 2023.0+ utilise ovc (OpenVINO Converter)
        from openvino.tools.ovc import convert_model
        
        model = convert_model(
            str(onnx_model_path),
            input_shape=[1, 3, 640, 640],
            compress_to_fp16=(precision == 'FP16')
        )
        
        # Sauvegarder le modèle
        serialize(model, str(output_model) + '.xml')
        
        logger.info(f"✓ Modèle OpenVINO créé:")
        logger.info(f"  - {output_model}.xml")
        logger.info(f"  - {output_model}.bin")
        
        return output_model
        
    except Exception as e:
        logger.error(f"Erreur lors de la conversion: {e}")
        logger.info("Tentative avec l'ancienne méthode mo...")
        
        # Fallback sur l'ancienne méthode
        import subprocess
        cmd = [
            'mo',
            '--input_model', str(onnx_model_path),
            '--output_dir', str(output_dir),
            '--model_name', model_name,
            '--data_type', precision
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✓ Modèle OpenVINO créé avec succès")
            return output_model
        else:
            logger.error(f"Erreur Model Optimizer: {result.stderr}")
            raise


def main():
    parser = argparse.ArgumentParser(description='Convertir modèles YOLOv5 vers OpenVINO')
    parser.add_argument('--model', type=str, default='models/best.pt',
                       help='Chemin vers le modèle PyTorch (.pt)')
    parser.add_argument('--img-size', type=int, default=640,
                       help='Taille d\'entrée de l\'image')
    parser.add_argument('--precision', type=str, default='FP16',
                       choices=['FP32', 'FP16'],
                       help='Précision du modèle OpenVINO')
    
    args = parser.parse_args()
    
    # Chemins
    pytorch_model = Path(args.model)
    if not pytorch_model.exists():
        logger.error(f"Modèle non trouvé: {pytorch_model}")
        sys.exit(1)
    
    model_name = pytorch_model.stem
    
    # Créer les répertoires de sortie
    onnx_dir = Path('models/onnx')
    onnx_dir.mkdir(parents=True, exist_ok=True)
    
    openvino_dir = Path('models/openvino')
    openvino_dir.mkdir(parents=True, exist_ok=True)
    
    onnx_output = onnx_dir / f"{model_name}.onnx"
    
    try:
        # Étape 1: PyTorch → ONNX
        logger.info("=" * 60)
        logger.info("ÉTAPE 1: Conversion PyTorch → ONNX")
        logger.info("=" * 60)
        export_to_onnx(pytorch_model, onnx_output, args.img_size)
        
        # Étape 2: ONNX → OpenVINO
        logger.info("\n" + "=" * 60)
        logger.info("ÉTAPE 2: Conversion ONNX → OpenVINO IR")
        logger.info("=" * 60)
        convert_onnx_to_openvino(onnx_output, openvino_dir, args.precision)
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ CONVERSION TERMINÉE AVEC SUCCÈS")
        logger.info("=" * 60)
        logger.info(f"\nModèles créés:")
        logger.info(f"  ONNX: {onnx_output}")
        logger.info(f"  OpenVINO: {openvino_dir / model_name}.xml")
        logger.info(f"            {openvino_dir / model_name}.bin")
        
        logger.info("\nPour utiliser le modèle OpenVINO:")
        logger.info("  1. Mettez PREFERRED_BACKEND='openvino' dans config.py")
        logger.info("  2. Redémarrez l'application Flask")
        
    except Exception as e:
        logger.error(f"\n❌ Erreur lors de la conversion: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()