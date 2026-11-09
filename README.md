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


## Week 3: Semantic Image Search and Backend Enhancements

PixelAI now creates a Gemini embedding for each generated image caption and stores it in `data/vector_store.json`. Natural-language search embeds the user's query and ranks indexed captions with cosine similarity. The search screen reports the number of indexed captions and can backfill embeddings for older images that already have captions. If embedding generation is temporarily unavailable, keyword matching is used as a fallback and the UI displays a warning.

### Week 3 architecture

See [`docs/architecture.svg`](docs/architecture.svg) for the architecture diagram and [`docs/architecture.mmd`](docs/architecture.mmd) for the editable Mermaid source.

### Embedding configuration

Set `GEMINI_API_KEY` and optionally `GEMINI_EMBEDDING_MODEL=gemini-embedding-001`. The same Gemini key is used for captions, image editing and embeddings. Embeddings are stored locally as JSON vectors keyed by image ID; this is a lightweight vector store, not Chroma or FAISS.

### Re-index older captions

Open Library. If any images have captions but no saved vectors, use **Index N existing caption(s)** to generate and save missing embeddings. New uploads are captioned and embedded automatically.

### Week 3 tests

Run `pytest -q` from the project folder. Unit tests cover cosine similarity and search ranking basics. Live Gemini calls require a valid API key and access to the configured models.

### Data and error handling

The JSON vector store is written atomically to reduce the risk of partial writes. Invalid JSON is handled by starting with an empty index; the UI can then re-index captions. SQLite stores version numbers per source image and has an index on version lookup. Keep the original image separate from generated versions.

### Deployment warning

This prototype stores the database, images and vector JSON on local disk. A hosting service with ephemeral storage can lose these files on restart/redeploy. For a persistent public deployment, move image files to object storage and SQLite/vector data to a persistent database or managed vector service. Add your API key through hosting secrets, never commit it.
