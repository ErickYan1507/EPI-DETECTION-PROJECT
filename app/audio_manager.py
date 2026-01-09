from app.logger import logger

class AudioManager:
    def __init__(self):
        self.enabled = True
        
    def play_sound(self, sound_name):
        if self.enabled:
            logger.info(f"Playing sound: {sound_name}")

_audio_manager = None

def get_audio_manager():
    global _audio_manager
    if _audio_manager is None:
        _audio_manager = AudioManager()
    return _audio_manager
