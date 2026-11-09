# PixelAI — AI-Powered Image Editing Platform

PixelAI is a Streamlit image workspace that lets you upload images, generate searchable descriptions with Gemini, request edits using natural language, and preserve each edit as a separate version.

## What's in this version

This is the **redesigned UI edition**. It replaces the original dark sidebar dashboard with a fresh editorial-style workspace:
- Warm off-white canvas, forest-green hero panels and lime accents.
- Horizontal navigation across Library, Create, History and About.
- A library dashboard with collection metrics, upload area and image cards.
- A two-column editing studio with the source image beside the prompt controls.
- A version timeline for reviewing and downloading earlier edits.

## Features

- Upload JPG, JPEG, PNG and WebP images.
- Generate image descriptions with Gemini Vision.
- Search stored image descriptions using natural-language-style text queries.
- Edit an image with a written instruction using a Gemini image model.
- Save every generated edit separately; the original remains unchanged.
- Browse and download previous versions.

## Tech stack

- Python + Streamlit
- Google Gemini API (`google-genai`)
- SQLite for image and version metadata
- Local folders for image files
- Pillow for image conversion and storage

## Setup (Windows / VS Code)

1. Extract the ZIP and open the `PixelAI_AI_Image_Editing_Platform` folder in VS Code.
2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and add your Gemini API key:

   ```env
   GEMINI_API_KEY=your_gemini_api_key
   GEMINI_VISION_MODEL=gemini-2.5-flash
   GEMINI_IMAGE_MODEL=gemini-3.1-flash-image
   ```

5. Start the app:

   ```powershell
   streamlit run app.py
   ```

Open the local URL printed in the terminal (usually `http://localhost:8501`).

## Project structure

```text
PixelAI_AI_Image_Editing_Platform/
├── app.py
├── services/
│   ├── db.py
│   ├── gemini_service.py
│   ├── search.py
│   └── storage.py
├── data/
│   ├── uploads/
│   └── versions/
├── docs/PROJECT_REPORT.md
├── tests/test_search.py
├── .env.example
└── requirements.txt
```

## Important notes

- The project uses the Gemini API directly. An OpenRouter key is not interchangeable with a Gemini API key.
- The image-editing model must be available to your Google AI Studio / Gemini API account and region. If a model is unavailable, update `GEMINI_IMAGE_MODEL` to a supported image-generation/editing model.
- The search implementation currently matches terms against generated captions and filenames. It is not an embedding-based vector database.
- This is a local, single-user prototype. Images and the SQLite database are stored on the machine running Streamlit.
- The source code has been syntax-checked, but API calls must be tested with your own key and model access.

## Suggested demo flow

1. Upload an image in **Library**.
2. Wait for Gemini to generate its description.
3. Search for an object, scene or colour mentioned in the description.
4. Open the image in **Create** and enter an edit instruction.
5. Compare the original and generated image.
6. Open **History** and download a previous version.

## Tests

Run the lightweight search tests with:

```powershell
python -m unittest discover -s tests -v
```
