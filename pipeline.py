import os
import sys
import subprocess
import urllib.request
import replicate
import time
import pickle
from huggingface_hub import InferenceClient
from pydub import AudioSegment

# YouTube API Imports
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ------------------------------------------------------------
# AUTHENTICATION & CONFIGURATION CONTROL PANEL
# ------------------------------------------------------------
HF_TOKEN = "YOUR_HUGGINGFACE_TOKEN_HERE"
os.environ["REPLICATE_API_TOKEN"] = "YOUR_REPLICATE_API_TOKEN_HERE"

CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

DURATION_MINUTES = 5

def generate_visual_base():
    print("\n[1/5] Synthesizing Outdoor Background Canvas...")
    client_hf = InferenceClient(token=HF_TOKEN)
    prompt = (
        "Cinematic 4k shot standing completely outside on a beautiful, peaceful city street "
        "during a calm daytime rain shower. No windows, no glass, pure outdoor scenery. "
        "Serene, safe, bright lighting, completely peaceful atmosphere."
    )
    image = client_hf.text_to_image(prompt, model="black-forest-labs/FLUX.1-schnell")
    image.save("base_frame.jpg")
    print(" -> Canvas saved successfully.")

def animate_rain_physics():
    print("\n[2/5] Invoking Minimax Physics Engine for Native Rain...")
    minimax_prompt = (
        "Camera perfectly locked. Static outdoor shot. Beautiful and peaceful rain "
        "falling straight down from the sky. No windows, no glass. Completely outdoor, "
        "serene, calm atmosphere. High definition cinematic video."
    )
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            print(f" -> Uplinking to Replicate cluster (Attempt {attempt + 1}/{max_retries})...")
            output = replicate.run(
                "minimax/video-01",
                input={
                    "prompt": minimax_prompt,
                    "first_frame_image": open("base_frame.jpg", "rb")
                }
            )
            break 
        except Exception as e:
            print(f" -> Network timeout. Retrying in 5 seconds...")
            time.sleep(5)
            if attempt == max_retries - 1:
                print("[ERROR] Replicate servers are completely unresponsive. Try again later.")
                sys.exit(1)
    
    print(" -> Downloading native AI video asset...")
    with open("ai_rain_clip.mp4", "wb") as f:
        f.write(output.read())
    print("[SUCCESS] Minimax physics render complete.")

def generate_max_volume_audio():
    print("\n[3/5] Downloading high-fidelity audio and applying MAX gain...")
    archive_url = "https://actions.google.com/sounds/v1/weather/rain_heavy_loud.ogg"
    temp_ogg = "raw_digital_rain.ogg"
    final_audio = "final_audio.mp3"
    target_length_ms = DURATION_MINUTES * 60 * 1000
    
    if not os.path.exists(temp_ogg):
        urllib.request.urlretrieve(archive_url, temp_ogg)
        
    raw_audio = AudioSegment.from_file(temp_ogg)
    
    slice_point = 8000 if len(raw_audio) > 15000 else 0 
    base_sound = raw_audio[slice_point:] + 30 
    
    shift_point = min(30000, len(base_sound) // 2)
    shifted_layer = base_sound[shift_point:] + base_sound[:shift_point] - 3 
    thick_soundscape = base_sound.overlay(shifted_layer) + 10
    
    compiled_audio = thick_soundscape
    while len(compiled_audio) < target_length_ms:
        compiled_audio = compiled_audio.append(thick_soundscape, crossfade=2000)
    
    compiled_audio[:target_length_ms].export(final_audio, format="mp3", bitrate="192k")
    print(f"[SUCCESS] High-volume continuous track generated.")

def compile_final_video():
    print("\n[4/5] Assembling Final Loop...")
    cmd = [
        "ffmpeg", 
        "-stream_loop", "-1", "-i", "ai_rain_clip.mp4",
        "-i", "final_audio.mp3",
        "-c:v", "copy",       
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(DURATION_MINUTES * 60), 
        "-shortest", 
        "final_asmr_master.mp4"
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print(" -> Master file saved as: final_asmr_master.mp4")

def get_authenticated_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print("[ERROR] Missing client_secrets.json for YouTube API.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, YOUTUBE_SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('youtube', 'v3', credentials=creds)

def upload_to_youtube(video_path):
    print("\n[5/5] Initializing YouTube API uplink...")
    try:
        youtube = get_authenticated_service()
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": "Cozy Deep Sleep Rain ASMR: Pure Outdoor Thunderstorm",
                    "description": "Continuous pure rain sounds for deep sleep, intense focus, and insomnia relief. High-fidelity outdoor ambient noise.",
                    "tags": ["asmr", "rain", "sleep", "thunderstorm", "white noise", "ambient"],
                    "categoryId": "24"
                },
                "status": {"privacyStatus": "private"}
            },
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
        )
        response = request.execute()
        print(f"\n🚀 [PIPELINE COMPLETE] Video uploaded securely!")
        print(f" -> Watch it here: https://youtu.be/{response.get('id')}")
    except Exception as e:
        print(f"[ERROR] YouTube API uplink failed: {e}")

if __name__ == "__main__":
    print("--- Booting Autonomous AI Director (Pure Minimax Engine) ---")
    
    # NOTE: Since you already generated the video on your last run, 
    # we can skip straight to Step 5! 
    # 
    # generate_visual_base()
    # animate_rain_physics()
    # generate_max_volume_audio()
    # compile_final_video()
    
    upload_to_youtube("final_asmr_master.mp4")
