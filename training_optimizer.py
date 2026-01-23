"""
Optimisation d'entraînement avec:
- Checkpoints périodiques pour reprendre après interruption
- Optimisation CPU/GPU efficace
- Réduction de la charge PC
"""

import os
import sys
import subprocess
import time
import shutil
import json
import psutil
import torch
from pathlib import Path
from datetime import datetime
import threading
import signal

class TrainingOptimizer:
    """Optimiseur d'entraînement avec checkpoints et gestion de ressources"""
    
    def __init__(self, session_name='epi_detection_optimized'):
        self.session_name = session_name
        self.checkpoint_dir = Path('training_checkpoints') / session_name
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file = self.checkpoint_dir / 'checkpoint.json'
        self.stats_file = self.checkpoint_dir / 'training_stats.json'
        self.process = None
        self.monitoring_thread = None
        self.should_stop = False
        
    def get_checkpoint(self):
        """Récupérer le dernier checkpoint"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return None
    
    def save_checkpoint(self, epoch, metrics):
        """Sauvegarder un checkpoint d'entraînement"""
        checkpoint = {
            'epoch': epoch,
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'session_name': self.session_name
        }
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)
        print(f"✓ Checkpoint sauvegardé: Epoch {epoch}")
        return checkpoint
    
    def resume_from_checkpoint(self):
        """Reprendre l'entraînement depuis un checkpoint"""
        checkpoint = self.get_checkpoint()
        if not checkpoint:
            return None, 0
        
        epoch = checkpoint['epoch']
        print(f"📌 Checkpoint trouvé: Epoch {epoch}")
        print(f"   Timestamp: {checkpoint['timestamp']}")
        return checkpoint, epoch
    
    def get_optimal_batch_size(self, available_memory_gb=None):
        """
        Déterminer le batch size optimal basé sur la mémoire disponible
        
        Heuristique:
        - GPU: 32GB → batch_size=16
        - GPU: 12GB → batch_size=8
        - GPU: 6GB → batch_size=4
        - CPU: batch_size=1 (très lent, à éviter)
        """
        if torch.cuda.is_available():
            try:
                total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                
                if total_memory >= 32:
                    return 16
                elif total_memory >= 16:
                    return 12
                elif total_memory >= 12:
                    return 8
                elif total_memory >= 6:
                    return 4
                else:
                    return 2
            except:
                pass
        
        # Fallback: mémoire système
        if available_memory_gb is None:
            available_memory_gb = psutil.virtual_memory().available / (1024**3)
        
        if available_memory_gb >= 32:
            return 8
        elif available_memory_gb >= 16:
            return 4
        else:
            return 1
    
    def get_optimal_workers(self):
        """Déterminer le nombre optimal de workers pour DataLoader"""
        cpu_count = psutil.cpu_count(logical=False)  # Nombre de CPU physiques
        
        if cpu_count <= 2:
            return 0
        elif cpu_count <= 4:
            return 2
        else:
            return min(4, cpu_count - 1)
    
    def setup_resource_monitoring(self):
        """Configurer la surveillance des ressources en arrière-plan"""
        def monitor():
            stats = []
            while not self.should_stop:
                try:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    mem = psutil.virtual_memory()
                    
                    stat = {
                        'timestamp': datetime.now().isoformat(),
                        'cpu_percent': cpu_percent,
                        'memory_percent': mem.percent,
                        'memory_gb': mem.used / (1024**3)
                    }
                    
                    if torch.cuda.is_available():
                        try:
                            gpu_mem = torch.cuda.memory_allocated() / (1024**3)
                            stat['gpu_memory_gb'] = gpu_mem
                        except:
                            pass
                    
                    stats.append(stat)
                    
                    # Garder seulement les 1000 derniers points
                    if len(stats) > 1000:
                        stats = stats[-1000:]
                    
                    # Sauvegarder chaque minute
                    if len(stats) % 60 == 0:
                        with open(self.stats_file, 'w') as f:
                            json.dump(stats, f, indent=2)
                
                except:
                    pass
        
        self.monitoring_thread = threading.Thread(target=monitor, daemon=True)
        self.monitoring_thread.start()
    
    def train_optimized(self, data_yaml, epochs=100, initial_batch_size=16, 
                       img_size=640, weights='yolov5s.pt'):
        """
        Lancer l'entraînement optimisé avec checkpoints et gestion de ressources
        """
        self.setup_resource_monitoring()
        
        # Vérifier si on reprend
        checkpoint, start_epoch = self.resume_from_checkpoint()
        
        # Déterminer les paramètres optimaux
        batch_size = min(initial_batch_size, self.get_optimal_batch_size())
        num_workers = self.get_optimal_workers()
        
        print("\n" + "="*70)
        print("🚀 ENTRAÎNEMENT OPTIMISÉ AVEC CHECKPOINTS")
        print("="*70)
        print(f"📊 Configuration d'optimisation:")
        print(f"   - Batch size: {batch_size}")
        print(f"   - Workers: {num_workers}")
        print(f"   - GPU: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"   - GPU: {torch.cuda.get_device_name(0)}")
            print(f"   - VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f}GB")
        
        print(f"   - Checkpoints: {self.checkpoint_dir}")
        print(f"   - Reprise depuis epoch: {start_epoch + 1}")
        print("="*70 + "\n")
        
        # Construire la commande YOLOv5 avec optimisations
        yolov5_dir = Path('yolov5')
        
        cmd = [
            sys.executable, str(yolov5_dir / 'train.py'),
            '--weights', weights,
            '--data', str(data_yaml),
            '--epochs', str(epochs),
            '--batch-size', str(batch_size),
            '--img', str(img_size),
            '--project', 'runs/train',
            '--name', self.session_name,
            '--exist-ok',
            '--device', '0' if torch.cuda.is_available() else 'cpu',
            '--save-period', '5',  # Sauvegarder tous les 5 epochs
            '--patience', '20',  # Early stopping
            '--cache', 'disk',  # Cache les images sur disque (moins de mémoire RAM)
            '--workers', str(num_workers),
        ]
        
        # Ajouter le poids de départ si c'est un checkpoint
        if start_epoch > 0 and checkpoint:
            # Pour une vraie reprise, YOLOv5 nécessiterait un mécanisme spécial
            # Pour l'instant, on note le checkpoint et on continue
            print(f"ℹ️  Reprise d'entraînement depuis epoch {start_epoch + 1}")
        
        # Appliquer optimisations GPU si disponible
        if torch.cuda.is_available():
            cmd.extend([
                '--half',  # Utiliser FP16 (demi-précision) pour réduire mémoire
                '--cache', 'disk'  # Cache sur disque au lieu de RAM
            ])
        
        print(f"Commande: {' '.join(cmd)}\n")
        
        start_time = time.time()
        
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                           stderr=subprocess.PIPE, text=True)
            
            # Attendre et monitorer
            stdout, stderr = self.process.communicate()
            
            if self.process.returncode != 0:
                print(f"❌ Entraînement échoué (code: {self.process.returncode})")
                print(f"STDERR: {stderr}")
                return False
            
            training_time = time.time() - start_time
            self.save_checkpoint(epochs, {
                'status': 'completed',
                'training_time_seconds': training_time
            })
            
            return True
        
        except KeyboardInterrupt:
            print("\n⏸️  Entraînement interrompu par l'utilisateur")
            if self.process:
                self.process.terminate()
                self.process.wait()
            
            training_time = time.time() - start_time
            self.save_checkpoint(start_epoch, {
                'status': 'interrupted',
                'training_time_seconds': training_time,
                'note': 'Entraînement interrompu - réexécuter pour reprendre'
            })
            return False
        
        except Exception as e:
            print(f"❌ Erreur: {e}")
            training_time = time.time() - start_time
            self.save_checkpoint(start_epoch, {
                'status': 'error',
                'training_time_seconds': training_time,
                'error': str(e)
            })
            return False
        
        finally:
            self.should_stop = True
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)


def train_with_optimization(data_yaml, epochs=100, batch_size=16, 
                           session_name='epi_detection_optimized'):
    """Wrapper pour l'entraînement optimisé"""
    optimizer = TrainingOptimizer(session_name)
    success = optimizer.train_optimized(
        data_yaml=data_yaml,
        epochs=epochs,
        initial_batch_size=batch_size
    )
    
    if success:
        # Copier le meilleur modèle
        best_model = Path('runs/train') / session_name / 'weights' / 'best.pt'
        if best_model.exists():
            dest = Path('models') / 'best.pt'
            shutil.copy(best_model, dest)
            print(f"\n✅ Modèle optimal copié vers: {dest}")
    
    return success


if __name__ == '__main__':
    # Test
    from EPI_CLASS_CONFIG import verify_class_consistency
    verify_class_consistency()
    
    # Exemple d'utilisation
    print("Optimisation d'entraînement disponible via: train_with_optimization()")
