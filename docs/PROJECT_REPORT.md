# PixelAI — Project Report

## 1. Overview

PixelAI is an AI-powered image editing platform designed around a simple workflow: add an image, understand what is in it, describe an edit in everyday language, and keep the result as a new version. The interface is organized as a visual library, a creation studio and a version-history workspace.

## 2. Problem statement

Traditional image-editing tools often require users to know which controls, layers or filters to use. PixelAI explores a more accessible approach: users describe the desired change in natural language and an AI model performs the edit.

## 3. Objectives

- Provide a simple image library.
- Automatically describe uploaded images.
- Allow users to find images using text queries.
- Support natural-language image editing.
- Preserve the original and maintain an edit history.

## 4. Technology

| Component | Technology | Responsibility |
|---|---|---|
| User interface | Streamlit | Library, editing workspace and history |
| Image understanding | Gemini Vision | Generates factual image descriptions |
| Image editing | Gemini image model | Applies the user's natural-language instruction |
| Metadata | SQLite | Stores image records and version information |
| File handling | Pillow + local folders | Stores uploads and generated versions |

## 5. Workflow

1. The user uploads an image.
2. The application stores a local copy and creates a database record.
3. Gemini Vision generates a short description, which is saved with the image metadata.
4. The user selects an image and enters an editing instruction.
5. The image and instruction are sent to the configured Gemini image model.
6. The returned image is stored as a new version; the original is not overwritten.
7. The user can review and download previous versions from History.

## 6. Interface design

The redesigned interface uses a light editorial visual style, horizontal navigation, collection metrics, image cards, a side-by-side editing workspace and a version timeline. The goal is to make the main workflow visible without relying on a crowded sidebar.

## 7. Current limitations

- Local single-user storage; no authentication or cloud synchronization.
- Search uses caption/filename text matching, not vector embeddings.
- Image editing depends on model availability, API quotas and account/region access.
- The project has not been independently security-audited or production-deployed.

## 8. Future improvements

- Add user authentication and cloud object storage.
- Add embedding-based semantic search and filters.
- Add before/after comparison controls and undo/restore actions.
- Add deployment, usage limits and better error monitoring.

## 9. Conclusion

PixelAI demonstrates how a hosted multimodal model can be integrated into a practical image workflow. It combines image understanding, natural-language editing and version preservation in a single interface.
