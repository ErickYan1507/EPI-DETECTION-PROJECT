# test_local_yolov5_load.py
import os, sys
repo = r"D:\projet\EPI-DETECTION-PROJECT\yolov5"
print("repo exists:", os.path.exists(repo))
print("hubconf:", os.path.join(repo, "hubconf.py"), os.path.exists(os.path.join(repo, "hubconf.py")))

# Essayer d'importer hubconf directement
import importlib.util
spec = importlib.util.spec_from_file_location("yolov5_hubconf", os.path.join(repo, "hubconf.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print("module keys:", [k for k in dir(mod) if not k.startswith('_')][:60])

# Si 'custom' existe, afficher sa signature
import inspect
if hasattr(mod, 'custom'):
    print("custom found, signature:", inspect.signature(mod.custom))
else:
    print("Aucune fonction 'custom' dans hubconf.py")