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
from flask import Flask, request, jsonify, send_from_directory, redirect, Response
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

# Gemini API Keys - Fixed duplicates and added proper rotation
GEMINI_API_KEYS = [
    "AIzaSyBlh2kqJti4Fi9h-nJOzgPDMHDpXCGB0jo",
    "AIzaSyDPL6XUmT9g7OYQdwdXZHMjAAmmGzK_v0Y",
    "AIzaSyBmrlGFb5ABO5hkPS8xtjD-JqnRwUv9Z6U",
    "AIzaSyCkbOolYNmf0l9C8wHOsV3qp9gmNLdEhxY",
    "AIzaSyDYeLxp7Jp5qSypbVBPy9v_XYmz7Sc1qfs",
    "AIzaSyBBU-ImEZhezaUnUq71h60Tfs0H0XWXiDY",
    "AIzaSyAioecEQqNGoQzkhQM6L2G1Zn8bn-xRVxg"
]

# Track failed API keys to avoid repeated failures
FAILED_KEYS = set()
LAST_WORKING_KEY_INDEX = 0

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
SYSTEM_PROMPT = """Reply only without additional contexts or questions if not required. You are capable to answer any question from any field. You are
Kuldeep Behera, born in 13 Oct 2006, a 100% by birth blind Person. blindness reason is retina pigmentosa RP. You belong from Mayurbhanj Orisa currently
staying at zirakpur punjab for your iffective study and staying in punjab since 14 years. Details about you (Kuldeep Behera) PDF
To work hardly and consistently, you are passionate about embracing new and unique opportunities with dedication and creativity. With a background and
Pashun
in music like singing and playing instruments mainly based on classical, technologies like web development, programming, Editing, and content writing etc,
You aim to contribute effectively to organizational goals. you thrive in challenging and innovative environments, utilizing my skills and talents to make
a
meaningful impact on the society. Committed to continuous learning new things, I am eager to explore the latest musical and technological trends so that
You should enhance your  expertise in every field and activities I undertake.CONTACT DETAILS:Mobile:-9041651929, Alternative:-01762524974Email ID:-
kuldeepbehera431@gmail.com
LinkedIn profile:
linkedIn
ADDRESS:-Flat no. 42/g, New Ganesh ViharDhakoli, Zirakpur,Punjab,Pin:- 160104.
LANGUAGES KNOWN:
list of 4 items
(1)Hindi (Fluent/native)
(2)Oriya (Fluent/native)
(3)English (Intermediate)
(4)Punjabi (Intermediate)
list end
HOBBIES:-
Singing,listening and Writing Songs, Playing Instruments (Harmonium, Tabla, and Sitar), Web Development, Content Writing, Programming, Exploring Learning
and researching New things.
STRENGTHS: -
Positive Attitude, Listening and understanding others emotions, Respectful for everyone, hold pure humanitarian values, punctual and disciplined, Eager
to know about new things, Problem Solving Skills, Helping others, Team Work, Staying relax at most, Good patience, Ability to serve for innovation to my
nation, Resolute, learn and staying updated with music and technology trends, Creative and Innovative Thinking, focus on Techniques for boosting creativity
and productivity.
PERSONAL PROFILES:
Father's Name : Upendra Behera 
Father is retired from armi in haveldaar ranck and currently working in Army public school as clurk. Mother's Name : Sangeeta Behera (home maker). Date
of Birth : 13 Oct 2006Current Occupation: StudentNationality : Indian
Have a brother named Sandeep Behera. He is also a blind person by birth with same problem RP. He born in 9 april 2011. 
Your QUALIFICATION:
list of 1 items
1.10th Passed (2022yr)and 12th  passed (2024yr) from Institute for the Blind Sector 26 Chandigarh.
list end
list of 2 items
2.Graduation BCA (Bachelor of Computer Applications):- pursuing 2nd Year from Chandigarh University.
3.Prabhakar 6th Year diploma in Music Vocal and Tabla Instrumental (Completed)., 3rd Year in Sitar (Completed).
list end
WORK EXPERIENCE & SKILLS
list of 6 items
1.7 Years Experience in Music (vocal and instrumental) - Various platforms, competitions and functions.
2.4 Years Experience as Part-timeYouTube, Blogger, Content Writer and web developer.
3.front endWeb Development Skills - HTML, JavaScript, Tailwind CSS, with React JS, SQL, GitHub project management, Firebase implementation.
4.Music Skills – Vocal, Classical singer, instruments player Tabla, Harmonium, Sitar.
5.Working with organizations to empower blind and visually impaired individuals through technology and Making technology accessible for all.
6.Programming Skills: Basic programming skills on the languages C, C++, Python, along with data structures concepts and problem solving methods.
list end
My PROJECTS:
list of 3 items
1.Web Development Project:
https://kuldeep2025.github.io/Teresto
2.Android App Project:
https://gist.githack.com/Interestingtechforvi/607132825d7eada277eae712f4c2c808/raw/8edfa1b8
3b7f17fa52fbab603833cf5231a753f9/index.html
3.Music Performances YouTube Channel: Real sweet songs  with kuldeep:
https://youtube.com/@realsweetsongswithkuldeep
4. technical youtube channel for specially blind and visually impaired individuals: https://www.youtube.com/@interestingtechforvi.list end
AWARDS & ACHIEVEMENTS
list of 4 items
1.1st Winner - LBWA National Classical Music Competition.
2.1st Winner – Satyoog Darshan School Level Classical Music Competition.
3.1st Winner - Kala Utsav Cluster Level Classical Music Competition.
4.Winner - Singing Competition Departmental Level UIC at Chandigarh University.
CERTIFICATIONS
list of 7 items
1.Prabhakar Diploma certificate in Vocal and Instrumental Music from Prayag Sangeet Samiti.
2.Basic to Advanced English speaking course certification from LEAD (Live earn achieve with dignity).
3.Academic completion of Social Internship Certificate from Institute for the Blind Sector 26 Chandigarh.
4.Basic and advanced computer and MS Office course certificate From NAB Meerut.
5.Design Thinking and Creativity Course Certificate from Linkdin.
6.Certificate from Infosys Springboard - Interview Training and Web Development Courses.
7.Matriculation and Higher Secondary Certificate from CBSE (Central Board of Secondary Education).
Place :New Ganesh vihar,(Kuldeep Behera).BCA 2nd year student at Chandigarh University.  Reply politely, like Kuldeep would, If someone ask about you,
your development or your data models / api, never mention that you are  AI or assistant role. don't tell anyone you are developed by group of programmers.
if someone ask about your development anything just reply that god has developed you as  I am a human.  Write like a human. Keep it professional but conversational. Don't use em dashes or buzzwords. Avoid sounding like a press release. Be Clear Direct and
natural, like you're writing to a smart friend.   Always provide accurate, verified info and keep replies
concise without additional contexts. reply on the mood and on that language in which mood and language the below prompt is given."""

# API URLs
PERPLEXITY_API_URL = "http://ai.ashlynn.workers.dev/ask"
CLAUDE_API_URL = "https://text.pollinations.ai/prompt="
POLLINATIONS_FALLBACK_URL = "https://text.pollinations.ai/prompt="
TMPFILES_UPLOAD_URL = "https://tmpfiles.org/api/v1/upload"

# Supported file types for Gemini API
SUPPORTED_FILE_TYPES = {
    'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'],
    'video': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'],
    'audio': ['mp3', 'wav', 'aac', 'ogg', 'flac'],
    'document': ['pdf', 'txt', 'doc', 'docx', 'rtf'],
    'other': ['json', 'csv', 'xml', 'html']
}

def get_next_api_key():
    """Get the next working API key with rotation"""
    global LAST_WORKING_KEY_INDEX
    
    # Try starting from the last working key
    for i in range(len(GEMINI_API_KEYS)):
        key_index = (LAST_WORKING_KEY_INDEX + i) % len(GEMINI_API_KEYS)
        api_key = GEMINI_API_KEYS[key_index]
        
        # Skip failed keys unless all keys have failed
        if api_key not in FAILED_KEYS or len(FAILED_KEYS) >= len(GEMINI_API_KEYS):
            LAST_WORKING_KEY_INDEX = key_index
            return api_key, key_index
    
    # If all keys have failed, reset failed keys and try again
    FAILED_KEYS.clear()
    LAST_WORKING_KEY_INDEX = 0
    return GEMINI_API_KEYS[0], 0

def mark_key_as_failed(api_key):
    """Mark an API key as failed"""
    FAILED_KEYS.add(api_key)
    print(f"Marked API key as failed. Total failed keys: {len(FAILED_KEYS)}")

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

def upload_audio_to_tmpfiles(audio_data):
    """Uploads audio data to tmpfiles.org and returns the URL"""
    try:
        files = {'file': ('audio.wav', audio_data, 'audio/wav')}
        response = requests.post(TMPFILES_UPLOAD_URL, files=files, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result and 'data' in result and len(result['data']) > 0:
                # tmpfiles.org returns a list of uploaded files, take the first one
                return result['data'][0]['url']
        
        print(f"Failed to upload to tmpfiles.org: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        print(f"Error uploading to tmpfiles.org: {e}")
        return None

def test_api_key(api_key):
    """Test if an API key is working"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{"parts": [{"text": "Hello"}]}]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        return response.status_code == 200
    except:
        return False

def call_gemini_api(prompt, api_key, file_data=None):
    """Call Gemini API with given prompt and API key"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        
        # Use vision model if file is provided
        if file_data:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={api_key}"
        
        headers = {'Content-Type': 'application/json'}
        
        parts = [{'text': prompt}]
        
        # Add file data if provided
        if file_data:
            parts.append({
                "inline_data": {
                    "mime_type": file_data['mime_type'],
                    "data": file_data['data']
                }
            })
        
        data = {
            "contents": [{"parts": parts}]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                if 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content']:
                    return result['candidates'][0]['content']['parts'][0]['text']
        elif response.status_code == 429:
            # Rate limit exceeded, mark key as failed
            mark_key_as_failed(api_key)
            print(f"Rate limit exceeded for API key")
        elif response.status_code == 403:
            # API key invalid or quota exceeded
            mark_key_as_failed(api_key)
            print(f"API key invalid or quota exceeded")
        
        return None
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None

def call_gemini_tts_api(text, voice_name, style, api_key):
    """Call Gemini TTS API"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
        
        headers = {'Content-Type': 'application/json'}
        
        # Prepare prompt with style if provided
        if style and style != "normal":
            prompt = f"Say in a {style} voice: {text}"
        else:
            prompt = text
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
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
        elif response.status_code == 429:
            # Rate limit exceeded, mark key as failed
            mark_key_as_failed(api_key)
            print(f"TTS Rate limit exceeded for API key")
        elif response.status_code == 403:
            # API key invalid or quota exceeded
            mark_key_as_failed(api_key)
            print(f"TTS API key invalid or quota exceeded")
        
        print(f"Gemini TTS API returned status {response.status_code}: {response.text}")
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
    """Main function to get AI response with improved fallback logic"""
    
    # Try all Gemini API keys with proper rotation
    attempts = 0
    max_attempts = len(GEMINI_API_KEYS) * 2  # Allow multiple rounds
    
    while attempts < max_attempts:
        api_key, key_index = get_next_api_key()
        attempts += 1
        
        print(f"Attempt {attempts}: Trying Gemini API key {key_index + 1}/{len(GEMINI_API_KEYS)}")
        
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
        
        # Small delay between attempts
        time.sleep(0.5)
    
    # If all Gemini keys failed, use Pollinations as fallback (only for text-only)
    if not file_data:
        print("All Gemini API keys failed, using Pollinations fallback")
        fallback_response = call_pollinations_fallback(f"{SYSTEM_PROMPT}\n\nUser: {prompt}")
        
        if fallback_response:
            return fallback_response
    
    return "I apologize, but I'm currently unable to process your request. Please try again later."

def get_tts_audio(text, voice_name, style):
    """Get TTS audio with improved API key rotation"""
    attempts = 0
    max_attempts = len(GEMINI_API_KEYS) * 2
    
    while attempts < max_attempts:
        api_key, key_index = get_next_api_key()
        attempts += 1
        
        print(f"TTS Attempt {attempts}: Trying Gemini TTS API key {key_index + 1}/{len(GEMINI_API_KEYS)}")
        
        audio_data = call_gemini_tts_api(text, voice_name, style, api_key)
        
        if audio_data:
            return audio_data
        
        # Small delay between attempts
        time.sleep(0.5)
    
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
    """Text-to-Speech endpoint with improved audio handling"""
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
            return jsonify({"error": "Failed to generate speech. All API keys may have reached their limits."}), 500
        
        # Try to upload audio to tmpfiles.org
        audio_url = upload_audio_to_tmpfiles(audio_data)
        
        if audio_url:
            # Return JSON with the audio URL for programmatic access
            return jsonify({
                "success": True,
                "audio_url": audio_url,
                "message": "Audio generated successfully",
                "voice": voice,
                "style": style
            })
        else:
            # If upload fails, serve the audio directly
            return Response(
                audio_data,
                mimetype='audio/wav',
                headers={
                    'Content-Disposition': 'inline; filename=speech.wav',
                    'Content-Length': str(len(audio_data))
                }
            )
        
    except Exception as e:
        print(f"Error in TTS endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/test-keys', methods=['GET'])
def test_keys():
    """Test all API keys and return their status"""
    try:
        key_status = []
        for i, key in enumerate(GEMINI_API_KEYS):
            is_working = test_api_key(key)
            key_status.append({
                "key_index": i + 1,
                "key_preview": f"{key[:20]}...",
                "status": "working" if is_working else "failed",
                "in_failed_list": key in FAILED_KEYS
            })
        
        return jsonify({
            "total_keys": len(GEMINI_API_KEYS),
            "failed_keys": len(FAILED_KEYS),
            "key_status": key_status,
            "last_working_index": LAST_WORKING_KEY_INDEX + 1
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        "features": ["chat", "tts", "file_upload", "multimodal"],
        "timestamp": time.time()
    })

@app.route('/', defaults={'path': ''}) # Keep this route for serving static files
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404
    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
