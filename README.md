

Markdown
# autonomous-media-pipeline

A lightweight Python pipeline that generates short-form ambient/ASMR videos from a single prompt and syncs the finished renders to AWS S3.

Built to automate the repetitive parts of content assembly: generating scripts, fetching/creating voice and background audio, combining everything into a video clip, and offloading storage to the cloud.

---

## What It Does

1. **Script Generation**: Calls the Gemini API (`google-genai`) to generate a calm, paced spoken script based on a theme.
2. **Audio & Asset Synthesis**:
   - Uses `gTTS` for voice narration.
   - Downloads an ambient audio layer (e.g., rain sounds).
   - Generates or pulls a matching visual backdrop.
3. **Video Assembly**: Uses `moviepy` to layer the voice over ambient audio (lowering background audio volume so speech stays audible), aligns durations, and exports an `.mp4`.
4. **Cloud Upload & Local Teardown**: Uses `boto3` to upload the final render to an Amazon S3 bucket (`rendered_videos/`), then purges temporary audio and image files to keep the local disk clean.

---

## Tech Stack

- Python 3.10+
- `google-genai` (Google Gemini API)
- `moviepy` & `gTTS`
- `boto3` (AWS S3)
- `python-dotenv`

---

## Setup & Running

### 1. Clone & install dependencies
bash
git clone https://github.com/Rigoberto-Castellanos/autonomous-media-pipeline.git
cd autonomous-media-pipeline

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


### 2. Configure environment variables
Create a `.env` file in the root directory:
bash
cp .env.example .env


Add your API keys:
env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-2
S3_BUCKET_NAME=your_bucket_name
GOOGLE_API_KEY=your_gemini_api_key


### 3. Run
bash
python main.py

Finished renders will output locally to `final_videos/` and upload automatically to your S3 bucket.

---

## Notes & Future Improvements

- **Audio leveling**: Currently adjusts ambient track volume to avoid drowning out the TTS track; looking into dynamic audio ducking via ffmpeg filters.
- **Video formats**: Output is set up for 1080x1920 portrait (Reels/Shorts format).
- **Background workers**: Future plan is to move execution off the local machine onto an AWS Lambda or Celery task worker triggered via webhook.
