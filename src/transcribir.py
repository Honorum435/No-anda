"""Transcribe audio a texto con faster-whisper LOCAL (gratis), en espanol.

Sirve para DICTAR consultas (o casos) sin teclear. El modelo se descarga la primera vez
y corre en CPU (int8) para andar tambien en la PC del papa, sin GPU.
"""
import tempfile
from pathlib import Path

MODELO_WHISPER = "base"  # "base" = rapido en CPU; "small" mas preciso pero mas lento
_modelo = None


def _cargar():
    global _modelo
    if _modelo is None:
        from faster_whisper import WhisperModel
        _modelo = WhisperModel(MODELO_WHISPER, device="cpu", compute_type="int8")
    return _modelo


def transcribir(audio_bytes):
    """Devuelve el texto transcripto (espanol) de un audio en bytes (WAV/etc.)."""
    if not audio_bytes:
        return ""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        ruta = f.name
    try:
        segmentos, _ = _cargar().transcribe(ruta, language="es")
        return " ".join(s.text.strip() for s in segmentos).strip()
    finally:
        try:
            Path(ruta).unlink()
        except Exception:
            pass
