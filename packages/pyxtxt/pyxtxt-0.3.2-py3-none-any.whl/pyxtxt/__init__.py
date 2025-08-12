from .core import xtxt, extxt_available_formats, xtxt_from_url

# Import OCR-Ollama functions if available
try:
    from .estrattori.ocr_ollama import (
        set_ollama_model, get_ollama_model, xtxt_image_describe,
        set_ollama_config, get_ollama_config, reset_ollama_config
    )
    __all__ = [
        "xtxt", "extxt_available_formats", "xtxt_from_url", 
        "set_ollama_model", "get_ollama_model", "xtxt_image_describe",
        "set_ollama_config", "get_ollama_config", "reset_ollama_config"
    ]
except ImportError:
    __all__ = ["xtxt", "extxt_available_formats", "xtxt_from_url"]
