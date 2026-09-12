import os
import requests
from gtts import gTTS
from moviepy.editor import AudioFileClip, ImageClip

def generate_audio(script_text, output_filename="audio.mp3"):
    print("[Audio Processing] Synthesizing voice...")
    # gTTS is free and keyless. It proves the audio pipeline mechanics work!
    tts = gTTS(text=script_text, lang='en', slow=True)
    tts.save(output_filename)
    print(f"[Audio Processing] Saved audio to {output_filename}")
    return output_filename

def generate_image(prompt, output_filename="background.jpg"):
    print(f"[Image Processing] Generating image for: {prompt}...")
    # Pollinations.ai generates images via URL for free without an API key
    formatted_prompt = prompt.replace(" ", "%20")
    url = f"https://image.pollinations.ai/prompt/{formatted_prompt}"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(output_filename, 'wb') as f:
                f.write(response.content)
            print(f"[Image Processing] Saved image to {output_filename}")
            return output_filename
    except Exception as e:
        print(f"[ERROR] Failed to generate image: {e}")
    return None

def render_video(audio_path, image_path, output_filename="final_video.mp4"):
    print("[Video Processing] Assembling video... this might take a minute.")
    
    # Load the audio and image files
    audio_clip = AudioFileClip(audio_path)
    image_clip = ImageClip(image_path)
    
    # Set the image to display for the exact duration of the audio
    video_clip = image_clip.set_duration(audio_clip.duration)
    
    # Attach the audio to the video
    video_clip = video_clip.set_audio(audio_clip)
    
    # Render the final MP4 file (fps=1 is fine for a static image video)
    video_clip.write_videofile(
        output_filename, 
        fps=1, 
        codec="libx264", 
        audio_codec="aac",
        logger=None # Hides the massive moviepy progress bars
    )
    print(f"[Video Processing] Success! Saved to {output_filename}")

# --- Test Execution ---
if __name__ == "__main__":
    print("--- Testing Media Generation Pipeline ---")
    sample_text = "Welcome to the quiet library. The rain is falling gently outside. Relax and listen."
    img_prompt = "A cozy old library with dark wood shelves and a window covered in rain droplets"
    
    # 1. Voice
    audio_file = generate_audio(sample_text)
    
    # 2. Art
    image_file = generate_image(img_prompt)
    
    # 3. Render
    if image_file and audio_file:
        os.makedirs("final_videos", exist_ok=True)
        render_video(audio_file, image_file, "final_videos/my_first_asmr_video.mp4")
        print("\n--- Pipeline Finished Successfully! ---")
