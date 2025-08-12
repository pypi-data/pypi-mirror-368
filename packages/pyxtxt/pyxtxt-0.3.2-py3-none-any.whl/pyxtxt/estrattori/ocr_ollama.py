# pyxtxt/extractors/image_ocr_ollama.py
from . import register_extractor
from io import BytesIO
import base64

try:
    import ollama
    from PIL import Image
except ImportError:
    ollama = None
    Image = None

# Global configuration for Ollama model and parameters
OLLAMA_MODEL = "gemma3:4b"  # Default multimodal model
OLLAMA_CONFIG = {
    'language': 'auto',  # Language hint for caption generation
    'caption_length': 'medium',  # short, medium, long
    'style': 'descriptive',  # descriptive, technical, simple, detailed
    'temperature': 0.1,  # Response creativity (0.0-1.0)
    'max_tokens': 1500,  # Maximum response length
    'confidence_threshold': 0.7  # Minimum confidence for text extraction
}

def set_ollama_model(model_name: str):
    """
    Set the Ollama model to use for OCR.
    
    Recommended multimodal models:
    - gemma3:4b (default, balanced speed/quality)
    - gemma3:12b (higher quality, slower)
    - gemma3:27b (best quality, very slow)
    - llava:7b (alternative vision model)
    - llava:13b (higher quality LLAVA)
    """
    global OLLAMA_MODEL
    OLLAMA_MODEL = model_name
    print(f"✅ Ollama OCR model set to: {model_name}")

def get_ollama_model():
    """Get current Ollama model name"""
    return OLLAMA_MODEL

def set_ollama_config(**kwargs):
    """
    Configure Ollama LLM parameters for better caption generation.
    
    Parameters:
    - language: Language hint ('auto', 'italian', 'english', 'spanish', etc.)
    - caption_length: Caption length ('short', 'medium', 'long')
    - style: Caption style ('descriptive', 'technical', 'simple', 'detailed')
    - temperature: Response creativity 0.0-1.0 (default: 0.1)
    - max_tokens: Maximum response length (default: 1500)
    - confidence_threshold: Text extraction confidence 0.0-1.0 (default: 0.7)
    
    Examples:
        set_ollama_config(language='italian', style='detailed')
        set_ollama_config(caption_length='long', temperature=0.3)
    """
    global OLLAMA_CONFIG
    for key, value in kwargs.items():
        if key in OLLAMA_CONFIG:
            OLLAMA_CONFIG[key] = value
            print(f"✅ Ollama config updated: {key} = {value}")
        else:
            print(f"⚠️ Unknown config parameter: {key}")

def get_ollama_config():
    """Get current Ollama configuration"""
    return OLLAMA_CONFIG.copy()

def reset_ollama_config():
    """Reset Ollama configuration to defaults"""
    global OLLAMA_CONFIG
    OLLAMA_CONFIG = {
        'language': 'auto',
        'caption_length': 'medium', 
        'style': 'descriptive',
        'temperature': 0.1,
        'max_tokens': 1500,
        'confidence_threshold': 0.7
    }
    print("✅ Ollama configuration reset to defaults")

if ollama and Image:
    def xtxt_image_ocr_ollama(file_buffer, mode="ocr", model=None):
        """
        Extract text from images using Ollama with multimodal models.
        
        Args:
            file_buffer: Image file buffer
            mode: "ocr" (text only) or "describe" (text + description)  
            model: Override default model (optional)
        """
        try:
            # Use specified model or global default
            current_model = model or OLLAMA_MODEL
            
            # Convert buffer to PIL Image
            image = Image.open(BytesIO(file_buffer.read()))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert image to base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Get current configuration
            config = OLLAMA_CONFIG
            
            # Build language hint
            lang_hint = ""
            if config['language'] != 'auto':
                lang_hint = f"Text language: {config['language']}. "
            
            # Different prompts based on mode
            if mode == "ocr":
                prompt = f"""Extract ALL visible text from this image exactly as it appears. 
Rules:
- Only return text that is actually written/printed in the image
- Preserve reading order (left to right, top to bottom)  
- Maintain line breaks and formatting
- Include numbers, symbols, special characters
- Do NOT add descriptions, interpretations, or context
- {lang_hint}If no text is visible, return 'NO_TEXT_FOUND'

Extracted text:"""
            
            else:  # mode == "describe"
                # Build style-specific prompts
                style_prompts = {
                    'descriptive': "Provide a clear, descriptive explanation",
                    'technical': "Use technical terminology and precise descriptions", 
                    'simple': "Use simple, easy-to-understand language",
                    'detailed': "Provide comprehensive details about all visual elements"
                }
                
                length_hints = {
                    'short': "Keep descriptions brief (1-2 sentences)",
                    'medium': "Provide moderate detail (2-4 sentences)",
                    'long': "Give comprehensive descriptions (4-8 sentences)"
                }
                
                style_instruction = style_prompts.get(config['style'], style_prompts['descriptive'])
                length_instruction = length_hints.get(config['caption_length'], length_hints['medium'])
                
                prompt = f"""Analyze this image and provide:
1. All visible text exactly as written
2. Image description following these guidelines:
   - {style_instruction}
   - {length_instruction}
   - {lang_hint}Focus on key visual elements, layout, and context

Format:
TEXT: [all visible text here, or NO_TEXT_FOUND if none]
DESCRIPTION: [image description following the guidelines above]"""
            
            # Send request to Ollama with configured parameters
            response = ollama.generate(
                model=current_model,
                prompt=prompt,
                images=[img_base64],
                options={
                    'temperature': config['temperature'],
                    'top_p': 0.9,
                    'num_predict': config['max_tokens']
                }
            )
            
            # Extract and clean response
            extracted_content = response.get('response', '').strip()
            
            # Handle no-text case for OCR mode
            if mode == "ocr" and ('NO_TEXT_FOUND' in extracted_content or len(extracted_content) < 3):
                return ""
            
            return extracted_content
            
        except Exception as e:
            print(f"⚠️ Error extracting from image with Ollama {current_model}: {e}")
            return ""
    
    # Wrapper functions for each mode
    def xtxt_image_ocr_only(file_buffer):
        """Traditional OCR: extract only visible text using Ollama"""
        return xtxt_image_ocr_ollama(file_buffer, mode="ocr")
    
    def xtxt_image_describe(file_buffer):
        """OCR + Description: text + image context using Ollama"""
        return xtxt_image_ocr_ollama(file_buffer, mode="describe")
    
    # Register OCR-only version as default
    # Note: Will override traditional EasyOCR if both modules are loaded
    image_formats = [
        "image/jpeg", "image/jpg", "image/png", 
        "image/bmp", "image/tiff", "image/webp"
    ]
    
    for format_type in image_formats:
        register_extractor(format_type, xtxt_image_ocr_only, name="OCR-Ollama")