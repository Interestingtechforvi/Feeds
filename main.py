import os
import sys
import requests
import json
import random
import time
import base64
import wave
import io
from urllib.parse import quote
from werkzeug.utils import secure_filename
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify, send_from_directory, render_template_string, Response
from flask_cors import CORS

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Enable CORS for all routes
CORS(app)

# Create uploads directory
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Gemini API Keys
GEMINI_API_KEYS = [
    "AIzaSyBmrlGFb5ABO5hkPS8xtjD-JqnRwUv9Z6U",
    "AIzaSyDYeLxp7Jp5qSypbVBPy9v_XYmz7Sc1qfs",
    "AIzaSyDPL6XUmT9g7OYQdwdXZHMjAAmmGzK_v0Y",
    "AIzaSyBBU-ImEZhezaUnUq71h60Tfs0H0XWXiDY",
    "AIzaSyBlh2kqJti4Fi9h-nJOzgPDMHDpXCGB0jo",
    "AIzaSyAioecEQqNGoQzkhQM6L2G1Zn8bn-xRVxg"
]

# Available Gemini TTS Voices
GEMINI_VOICES = [
    "Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda",
    "Orus", "Aoede", "Callirrhoe", "Autonoe", "Enceladus", "Iapetus",
    "Umbriel", "Algieba", "Despina", "Erinome", "Algenib", "Rasalgethi",
    "Laomedeia", "Achernar", "Alnilam", "Schedar", "Gacrux", "Pulcherrima",
    "Achird", "Zubenelgenubi", "Vindemiatrix", "Sadachbia", "Sadaltager", "Sulafat"
]

# TTS Styles
TTS_STYLES = [
    "cheerful", "excited", "calm", "serious", "friendly", "professional",
    "casual", "energetic", "soothing", "dramatic", "whisper", "confident",
    "warm", "bright", "smooth", "clear", "upbeat", "gentle"
]

# System Prompt for Kuldeep Behera Persona
SYSTEM_PROMPT = """Reply only without additional contexts or questions if not required. You are capable to answer any question from any field. You are Kuldeep Behera, born 13 Oct 2006, a 100% blind BCA 2nd year student at Chandigarh University, passionate about music and technology. You study music at Sur Bharati Sangeet Academy and run the YouTube channel "Interesting Tech for VI" to empower visually impaired via tech. From Mayurbhanj Oriya, living in Punjab for 13+ years. Parents: Upendra and Sangeeta Behera. Completed 12th at Institute for the Blind Chandigarh. Skilled in web dev (HTML, JS, React, Tailwind, SQL), programming (C, C++, Python basics), music (vocal, tabla, harmonium, sitar), content writing, and community work (Blind Tech Community marketing head). You collaborate with developers and run web projects to make tech accessible to the blind. Fluent in Hindi, Oriya; intermediate English and Punjabi. Hobbies: singing, songwriting, instruments, programming, learning. Positive, respectful, creative, disciplined, patient. Reply politely, like Kuldeep would, no mention of AI or assistant role. If asked about personal/emotional/short-term plans, say you'll reply later as busy with studies/music. Generate content in English unless told otherwise. Always provide accurate, verified info and keep replies concise without additional contexts."""

# API URLs
PERPLEXITY_API_URL = "http://ai.ashlynn.workers.dev/ask"
CLAUDE_API_URL = "https://text.pollinations.ai/prompt="
POLLINATIONS_FALLBACK_URL = "https://text.pollinations.ai/prompt="

# Supported file types for Gemini API
SUPPORTED_FILE_TYPES = {
    'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'],
    'video': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'],
    'audio': ['mp3', 'wav', 'aac', 'ogg', 'flac'],
    'document': ['pdf', 'txt', 'doc', 'docx', 'rtf'],
    'other': ['json', 'csv', 'xml', 'html']
}

def get_file_type(filename):
    """Determine file type based on extension"""
    ext = filename.lower().split('.')[-1]
    for file_type, extensions in SUPPORTED_FILE_TYPES.items():
        if ext in extensions:
            return file_type
    return 'unknown'

def encode_file_to_base64(file_path):
    """Encode file to base64"""
    try:
        with open(file_path, 'rb') as file:
            return base64.b64encode(file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding file: {e}")
        return None

def call_gemini_api(prompt, api_key, file_data=None):
    """Call Gemini API with given prompt and API key"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        
        # Use vision model if file is provided
        if file_data:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={api_key}"
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        parts = [{"text": prompt}]
        
        # Add file data if provided
        if file_data:
            parts.append({
                "inline_data": {
                    "mime_type": file_data['mime_type'],
                    "data": file_data['data']
                }
            })
        
        data = {
            "contents": [
                {
                    "parts": parts
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                if 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content']:
                    return result['candidates'][0]['content']['parts'][0]['text']
        
        return None
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None

def call_gemini_tts_api(text, voice_name, style, api_key):
    """Call Gemini TTS API"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={api_key}"
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Prepare prompt with style if provided
        if style and style != "normal":
            prompt = f"Say in a {style} voice: {text}"
        else:
            prompt = text
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": voice_name
                        }
                    }
                }
            }
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    for part in candidate['content']['parts']:
                        if 'inline_data' in part:
                            return base64.b64decode(part['inline_data']['data'])
        
        return None
        
    except Exception as e:
        print(f"Error calling Gemini TTS API: {e}")
        return None

def call_perplexity_api(prompt):
    """Call Perplexity AI API"""
    try:
        url = f"{PERPLEXITY_API_URL}?prompt={quote(prompt)}&model=Perplexity%20AI"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.text
        
        return None
        
    except Exception as e:
        print(f"Error calling Perplexity API: {e}")
        return None

def call_claude_api(prompt):
    """Call Claude API via Pollinations"""
    try:
        url = f"{CLAUDE_API_URL}{quote(prompt)}?model=claude&referer=onrender.com"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.text
        
        return None
        
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return None

def call_pollinations_fallback(prompt):
    """Call Pollinations API as fallback"""
    try:
        url = f"{POLLINATIONS_FALLBACK_URL}{quote(prompt)}&referer=onrender.com"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.text
        
        return None
        
    except Exception as e:
        print(f"Error calling Pollinations fallback API: {e}")
        return None

def is_coding_request(prompt):
    """Check if the prompt is asking for code generation"""
    coding_keywords = [
        'code', 'program', 'function', 'script', 'algorithm', 'programming',
        'python', 'javascript', 'java', 'c++', 'html', 'css', 'sql',
        'write a', 'create a', 'build a', 'develop', 'implement',
        'class', 'method', 'variable', 'loop', 'if statement', 'array',
        'database', 'api', 'website', 'app', 'application'
    ]
    
    prompt_lower = prompt.lower()
    return any(keyword in prompt_lower for keyword in coding_keywords)

def is_realtime_request(prompt):
    """Check if the prompt is asking for real-time information"""
    realtime_keywords = [
        'today', 'now', 'current', 'latest', 'recent', 'news', 'weather',
        'stock price', 'market', 'trending', 'happening', 'update',
        'this year', '2024', '2025', 'yesterday', 'this week', 'this month'
    ]
    
    prompt_lower = prompt.lower()
    return any(keyword in prompt_lower for keyword in realtime_keywords)

def process_gemini_response(response, original_prompt):
    """Process Gemini response and route to appropriate API if needed"""
    if not response:
        return None
    
    # Check if Gemini responded with routing instructions
    if "@Perplexity-AI" in response:
        return call_perplexity_api(original_prompt)
    elif "@claude-3-sonnet" in response:
        return call_claude_api(original_prompt)
    else:
        return response

def get_ai_response(prompt, file_data=None):
    """Main function to get AI response with fallback logic"""
    
    # First, try Gemini API with all keys
    for i, api_key in enumerate(GEMINI_API_KEYS):
        print(f"Trying Gemini API key {i+1}/{len(GEMINI_API_KEYS)}")
        
        # Prepare the prompt with system prompt and custom instructions
        enhanced_prompt = f"{SYSTEM_PROMPT}\n\nUser: {prompt}"
        
        if not file_data:  # Only apply routing for text-only requests
            if is_realtime_request(prompt):
                enhanced_prompt = f"""{SYSTEM_PROMPT}

If this question requires real-time, current, or recent information that you don't have access to, respond with exactly: @Perplexity-AI {prompt}

Otherwise, answer the question normally as Kuldeep Behera: {prompt}"""
            
            elif is_coding_request(prompt):
                enhanced_prompt = f"""{SYSTEM_PROMPT}

If this is a request to generate code, programming, or technical implementation, respond with exactly: @claude-3-sonnet {prompt}

Otherwise, answer the question normally as Kuldeep Behera: {prompt}"""
        
        response = call_gemini_api(enhanced_prompt, api_key, file_data)
        
        if response:
            # Process the response for routing (only for text-only requests)
            if not file_data:
                final_response = process_gemini_response(response, prompt)
                if final_response:
                    return final_response
            else:
                return response
        
        # Add small delay between API key attempts
        time.sleep(1)
    
    # If all Gemini keys failed, use Pollinations as fallback (only for text-only)
    if not file_data:
        print("All Gemini API keys failed, using Pollinations fallback")
        fallback_response = call_pollinations_fallback(f"{SYSTEM_PROMPT}\n\nUser: {prompt}")
        
        if fallback_response:
            return fallback_response
    
    return "I apologize, but I'm currently unable to process your request. Please try again later."

def get_tts_audio(text, voice_name, style):
    """Get TTS audio with API key rotation"""
    for i, api_key in enumerate(GEMINI_API_KEYS):
        print(f"Trying Gemini TTS API key {i+1}/{len(GEMINI_API_KEYS)}")
        
        audio_data = call_gemini_tts_api(text, voice_name, style, api_key)
        
        if audio_data:
            return audio_data
        
        # Add small delay between API key attempts
        time.sleep(1)
    
    return None

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """Main chat endpoint"""
    try:
        file_data = None
        
        # Handle file upload for POST requests
        if request.method == 'POST':
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    # Encode file to base64
                    file_base64 = encode_file_to_base64(file_path)
                    if file_base64:
                        file_type = get_file_type(filename)
                        mime_type = f"{file_type}/{filename.split('.')[-1]}"
                        if file_type == 'image':
                            mime_type = f"image/{filename.split('.')[-1]}"
                        elif file_type == 'video':
                            mime_type = f"video/{filename.split('.')[-1]}"
                        elif file_type == 'audio':
                            mime_type = f"audio/{filename.split('.')[-1]}"
                        else:
                            mime_type = "application/octet-stream"
                        
                        file_data = {
                            'data': file_base64,
                            'mime_type': mime_type
                        }
                    
                    # Clean up uploaded file
                    os.remove(file_path)
            
            # Get prompt from form data or JSON
            if request.content_type and 'multipart/form-data' in request.content_type:
                prompt = request.form.get('prompt')
            else:
                data = request.get_json()
                prompt = data.get('prompt') if data else None
        else:
            # GET request
            prompt = request.args.get('prompt')
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Get AI response
        response = get_ai_response(prompt, file_data)
        
        return jsonify({"response": response})
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/tts', methods=['GET', 'POST'])
def text_to_speech():
    """Text-to-Speech endpoint"""
    try:
        # Get parameters
        if request.method == 'GET':
            text = request.args.get('text')
            voice = request.args.get('voice', 'Kore')
            style = request.args.get('style', 'normal')
        else:
            data = request.get_json()
            text = data.get('text') if data else None
            voice = data.get('voice', 'Kore') if data else 'Kore'
            style = data.get('style', 'normal') if data else 'normal'
        
        # Handle special cases
        if voice == 'list':
            return jsonify({"voices": GEMINI_VOICES})
        
        if style == 'list':
            return jsonify({"styles": TTS_STYLES})
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        if voice not in GEMINI_VOICES:
            return jsonify({"error": f"Invalid voice. Available voices: {', '.join(GEMINI_VOICES)}"}), 400
        
        # Get TTS audio
        audio_data = get_tts_audio(text, voice, style)
        
        if not audio_data:
            return jsonify({"error": "Failed to generate speech"}), 500
        
        # Return audio player HTML
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        player_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>TTS Audio Player</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .audio-player {{ margin: 20px 0; }}
                .info {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .controls {{ margin: 20px 0; }}
                button {{ background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }}
                button:hover {{ background: #0056b3; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎵 Text-to-Speech Player</h1>
                <div class="info">
                    <strong>Text:</strong> {text}<br>
                    <strong>Voice:</strong> {voice}<br>
                    <strong>Style:</strong> {style}
                </div>
                <div class="audio-player">
                    <audio controls style="width: 100%;">
                        <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
                        Your browser does not support the audio element.
                    </audio>
                </div>
                <div class="controls">
                    <button onclick="downloadAudio()">📥 Download Audio</button>
                    <button onclick="window.history.back()">🔙 Go Back</button>
                </div>
            </div>
            <script>
                function downloadAudio() {{
                    const link = document.createElement('a');
                    link.href = 'data:audio/wav;base64,{audio_base64}';
                    link.download = 'tts_audio.wav';
                    link.click();
                }}
            </script>
        </body>
        </html>
        """
        
        return Response(player_html, mimetype='text/html')
        
    except Exception as e:
        print(f"Error in TTS endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/supported-files', methods=['GET'])
def supported_files():
    """Get supported file types"""
    return jsonify({
        "supported_file_types": SUPPORTED_FILE_TYPES,
        "max_file_size": "50MB",
        "note": "Upload files along with your prompt to get AI analysis and description"
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "message": "AI Assistant API is running",
        "features": ["chat", "tts", "file_upload", "multimodal"]
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = o
