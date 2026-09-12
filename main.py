import os
import requests
from google import genai
from gtts import gTTS
from moviepy.editor import AudioFileClip, ImageClip, CompositeAudioClip
import moviepy.audio.fx.all as afx
import boto3
from dotenv import load_dotenv

load_dotenv()


def upload_to_s3(local_file_path):
    bucket = os.getenv("S3_BUCKET_NAME")
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-2")

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=region,
    )

    file_name = os.path.basename(local_file_path)
    s3_key = f"rendered_videos/{file_name}"

    print(f"Uploading {file_name} to AWS S3 bucket: {bucket}...")
    s3.upload_file(local_file_path, bucket, s3_key)
    print(f"Asset successfully uploaded to s3://{bucket}/{s3_key}")
# --- 1. Setup API Configuration ---
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("[ERROR] GOOGLE_API_KEY not found. Please export it first.")
    exit(1)
    
client = genai.Client(api_key=api_key)

# --- 2. Core Functions ---
def generate_asmr_script(topic):
    print(f"[AI Processing] Asking Gemini to write ASMR script for: {topic}...")
    try:
        prompt = f"Write a soothing, 1-minute ASMR script for: {topic}. Only provide the spoken dialogue. Do NOT include any sound effect tags, stage directions, or character names."
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"[ERROR] Gemini API call failed: {e}")
        return "Hello. The rain is falling. You are safe. Relax."

def generate_audio(script_text, output_filename="temp_voice.mp3"):
    print("[Audio Processing] Synthesizing voice...")
    tts = gTTS(text=script_text, lang='en', slow=True)
    tts.save(output_filename)
    return output_filename

def download_sfx(output_filename="temp_rain.mp3"):
    print("[Audio Processing] Downloading ambient rain sound effect...")
    # Using the Internet Archive which allows Python downloads
    url = "https://archive.org/download/GOLD_TAPE_46_Thunderstorm_Rain/G46-08-Rain%20Distant%20Thunder.mp3"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            with open(output_filename, 'wb') as f:
                f.write(response.content)
            print("[Audio Processing] Successfully downloaded background audio layer.")
            return output_filename
        else:
            print(f"[WARNING] Server returned status code: {response.status_code}")
    except Exception as e:
        print(f"[WARNING] Could not retrieve background audio: {e}")
        
    print("[WARNING] Proceeding without ambient sound layer.")
    return None
def generate_image(prompt, output_filename="temp_bg.jpg"):
    print(f"[Image Processing] Generating image...")
    formatted_prompt = prompt.replace(" ", "%20")
    url = f"https://image.pollinations.ai/prompt/{formatted_prompt}"
    
    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        with open(output_filename, 'wb') as f:
            f.write(response.content)
        return output_filename
    return None

def render_video(voice_path, sfx_path, image_path, output_filename):
    print(f"[Video Processing] Assembling assets and mixing audio tracks...")
    
    voice_clip = AudioFileClip(voice_path)
    final_audio = voice_clip
    
    if sfx_path:
        rain_clip = AudioFileClip(sfx_path)
        # Loop the rain to match the voice track perfectly, dropped to 30% volume
        rain_loop = afx.audio_loop(rain_clip, duration=voice_clip.duration).volumex(0.3)
        final_audio = CompositeAudioClip([voice_clip, rain_loop])
    
    image_clip = ImageClip(image_path).set_duration(voice_clip.duration)
    video_clip = image_clip.set_audio(final_audio)
    
    video_clip.write_videofile(
        output_filename, 
        fps=1, 
        codec="libx264", 
        audio_codec="aac",
        logger=None
    )

# --- 3. Pipeline Execution ---
if __name__ == "__main__":
    print("--- Booting up ASMR_Pipeline_V3 (Layered Audio - Fixed) ---")
    
    video_topic = "A quiet library in the rain"
    art_prompt = "A cozy old library with dark wood shelves and a window covered in rain droplets"
    
    os.makedirs("final_videos", exist_ok=True)
    
    # Step 1: Text Synthesis
    script = generate_asmr_script(video_topic)
    print("\n--- Generated Script ---")
    print(script)
    print("------------------------\n")
    
    # Step 2: Content Generation
    voice_file = generate_audio(script, "temp_voice.mp3")
    sfx_file = download_sfx("temp_rain.mp3")
    image_file = generate_image(art_prompt, "temp_bg.jpg")
    
    # Step 3: Video Assembly & Workspace Cleanup
    if voice_file and image_file:
        final_output = "final_videos/video_3_perfected_audio.mp4"
        render_video(voice_file, sfx_file, image_file, final_output)
        
        # Clean up transient workspace assets
        os.remove(voice_file)
        os.remove(image_file)
        if sfx_file and os.path.exists(sfx_file):
            os.remove(sfx_file)
            
        print(f"\n[SUCCESS] Render complete! High-quality video saved to: {final_output}")
	# Replace 'final_video.mp4' with the variable or path of your rendered output
        upload_to_s3(final_output)
