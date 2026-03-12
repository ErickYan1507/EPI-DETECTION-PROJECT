from __future__ import annotations

from typing import List

import numpy as np

from app.logger import logger


class InsightFaceReIdentifier:
    """Face embedding extractor backed by InsightFace."""

    def __init__(
        self,
        enabled: bool = True,
        model_name: str = "buffalo_l",
        det_size: tuple[int, int] = (640, 640),
        ctx_id: int = 0,
        max_faces: int = 5,
    ) -> None:
        self.enabled = bool(enabled)
        self.available = False
        self.max_faces = int(max_faces)
        self._app = None

        if not self.enabled:
            logger.info("InsightFace disabled by configuration.")
            return

        try:
            from insightface.app import FaceAnalysis

            # Use CPU by default for compatibility.
            # If GPU runtime is configured for InsightFace on the host,
            # it can be enabled by changing provider setup there.
            self._app = FaceAnalysis(name=model_name, providers=["CPUExecutionProvider"])
            self._app.prepare(ctx_id=ctx_id, det_size=det_size)
            self.available = True
            logger.info(f"InsightFace initialized (model={model_name}, det_size={det_size})")
        except Exception as exc:
            self.available = False
            logger.warning(f"InsightFace unavailable: {exc}")

    def extract_embeddings(self, frame_bgr: np.ndarray) -> List[list[float]]:
        if not self.available or self._app is None:
            return []
        if frame_bgr is None or frame_bgr.size == 0:
            return []

        try:
            faces = self._app.get(frame_bgr)
        except Exception as exc:
            logger.debug(f"InsightFace inference failed: {exc}")
            return []

        if not faces:
            return []

        # Deterministic order: highest detection score first.
        faces_sorted = sorted(faces, key=lambda f: float(getattr(f, "det_score", 0.0)), reverse=True)
        embeddings: List[list[float]] = []

        for face in faces_sorted[: self.max_faces]:
            emb = np.asarray(getattr(face, "embedding", None), dtype=np.float32).flatten()
            if emb.size == 0:
                continue
            embeddings.append(emb.tolist())

        return embeddings
