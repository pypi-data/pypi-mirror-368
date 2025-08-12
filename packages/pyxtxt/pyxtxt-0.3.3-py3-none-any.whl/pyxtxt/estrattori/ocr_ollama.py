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
    'confidence_threshold': 0.7,  # Minimum confidence for text extraction
    'context': 'general'  # Context hint: general, cookbook, document, diagram, etc.
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
    - context: Content context ('general', 'cookbook', 'document', 'handwriting', 'technical')
    - temperature: Response creativity 0.0-1.0 (default: 0.1)
    - max_tokens: Maximum response length (default: 1500)
    - confidence_threshold: Text extraction confidence 0.0-1.0 (default: 0.7)
    
    Examples:
        set_ollama_config(language='italian', style='detailed')
        set_ollama_config(context='document', caption_length='long')
        set_ollama_config(context='handwriting', temperature=0.2)
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
        'confidence_threshold': 0.7,
        'context': 'general'
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
            # Reset buffer position if it has read method
            if hasattr(file_buffer, 'seek'):
                file_buffer.seek(0)
            image_data = file_buffer.read()
            image = Image.open(BytesIO(image_data))
            
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
                prompt = f"""Look carefully at this image and extract ALL text that you can see, including:
- Titles, headings, and main text content  
- Small print, captions, labels, and annotations
- Numbers, measurements, quantities, and symbols
- Menu items, ingredient lists, cooking instructions
- Any text in boxes, speech bubbles, or decorative elements

IMPORTANT: 
- Read carefully and include even small or partially visible text
- Preserve the original formatting and line breaks where possible
- {lang_hint}Process the text from left to right, top to bottom
- If you cannot find any readable text at all, respond with 'NO_TEXT_FOUND'

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
                
                # Context-specific hints (only when explicitly set)
                context_hint = ""
                context = config.get('context', 'general').lower()
                if context == 'cookbook' or context == 'recipe':
                    context_hint = """
   - If this appears to be a recipe/cookbook page, include: ingredients, cooking steps, quantities, cooking times
   - Mention any photos of prepared dishes or cooking techniques shown
   - Note any special formatting like ingredient lists, step numbers, or cooking tips"""
                elif context == 'document':
                    context_hint = """
   - Focus on document structure: headers, paragraphs, sections, page numbers
   - Note any official formatting, letterheads, signatures, or stamps"""
                elif context == 'handwriting' or context == 'notes':
                    context_hint = """
   - Pay special attention to handwritten text which may be harder to read
   - Note any sketches, diagrams, or informal formatting typical of personal notes"""
                elif context == 'technical' or context == 'diagram':
                    context_hint = """
   - Focus on technical elements: labels, measurements, specifications, diagrams
   - Include any mathematical formulas, technical symbols, or engineering notations"""

                prompt = f"""Analyze this image and provide:
1. All visible text exactly as written (preserve formatting, line breaks, bullet points)
2. Image description following these guidelines:
   - {style_instruction}
   - {length_instruction}
   - {lang_hint}Focus on key visual elements, layout, and context{context_hint}

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
    def xtxt_image_ocr_only(file_input):
        """Traditional OCR: extract only visible text using Ollama"""
        # Handle both file paths and buffers
        if isinstance(file_input, str):
            with open(file_input, 'rb') as f:
                return xtxt_image_ocr_ollama(f, mode="ocr")
        else:
            return xtxt_image_ocr_ollama(file_input, mode="ocr")
    
    def xtxt_image_describe(file_input):
        """OCR + Description: text + image context using Ollama"""
        # Handle both file paths and buffers  
        if isinstance(file_input, str):
            with open(file_input, 'rb') as f:
                return xtxt_image_ocr_ollama(f, mode="describe")
        else:
            return xtxt_image_ocr_ollama(file_input, mode="describe")
    
    # Register OCR-only version as default
    # Note: Will override traditional EasyOCR if both modules are loaded
    image_formats = [
        "image/jpeg", "image/jpg", "image/png", 
        "image/bmp", "image/tiff", "image/webp"
    ]
    
    for format_type in image_formats:
        register_extractor(format_type, xtxt_image_ocr_only, name="OCR-Ollama")