import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# The specific permission we need: uploading YouTube videos
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def authenticate_youtube():
    creds = None
    # token.json stores your login so you don't have to authenticate every time
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If there are no valid credentials, we need to log in (happens on the very first run)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("\n------------------------------------------------------------")
            print("[Auth] No saved token found. Please manually authorize the app.")
            print("[Auth] 1. Copy the long 'https://...' link below.")
            print("[Auth] 2. Paste it into your web browser and log in.")
            print("[Auth] 3. When the browser fails to load 'localhost', copy that full localhost link.")
            print("[Auth] 4. Paste that localhost link back here into the terminal.")
            print("------------------------------------------------------------\n")
            
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            
            # FIXED: open_browser=False prevents the terminal from hanging, port=8080 gives a reliable callback URL
            creds = flow.run_local_server(port=8080, open_browser=False)
            
        # Save the credentials for the next run so it stays fully automated
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            print("\n[Auth] Token saved successfully!")
            
    return build('youtube', 'v3', credentials=creds)

def upload_video(youtube, video_path, title, description):
    print(f"\n[Uploading] Preparing to upload: {video_path}...")
    
    # Set up the video details
    request_body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['ASMR', 'Rain Sounds', 'Library', 'Relaxation', 'Sleep'],
            'categoryId': '24' # 24 is the Entertainment category
        },
        'status': {
            'privacyStatus': 'private' # ALWAYS start as private while testing!
        }
    }

    # Load the video file
    media_file = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    # Execute the upload
    print("[Uploading] Pushing file to YouTube (this may take a minute depending on your internet speed)...")
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    response = request.execute()
    print(f"\n[SUCCESS] Video uploaded successfully! 🚀")
    print(f"Video ID: {response.get('id')}")
    print(f"Watch it here: https://www.youtube.com/watch?v={response.get('id')}")

if __name__ == "__main__":
    print("--- Booting up YouTube Uploader ---")
    
    # We will upload the awesome video you just rendered
    video_to_upload = "final_videos/video_3_perfected_audio.mp4"
    
    if not os.path.exists(video_to_upload):
        print(f"[ERROR] Could not find the video at {video_to_upload}.")
        exit(1)
        
    try:
        yt_service = authenticate_youtube()
        upload_video(
            youtube=yt_service,
            video_path=video_to_upload,
            title="A Quiet Library in the Rain (ASMR)",
            description="Welcome to the quiet library. Listen to the gentle rain, relax, and drift to sleep. Generated entirely by AI."
        )
    except Exception as e:
        print(f"\n[ERROR] The script encountered an issue: {e}")
