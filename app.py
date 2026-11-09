import os
from pathlib import Path
import streamlit as st
from services.db import init_db, add_image, list_images, get_image, add_version, list_versions, update_caption
from services.storage import save_upload, save_version
from services.gemini_service import caption_image, edit_image
from services.search import search_images

ROOT = Path(__file__).parent
st.set_page_config(page_title="PixelAI — Creative Workspace", page_icon="✳️", layout="wide", initial_sidebar_state="collapsed")
init_db()

# -----------------------------------------------------------------------------
# Visual system: a fresh editorial / creative-workspace direction, intentionally
# different from the original dark sidebar dashboard.
# -----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --ink:#17211d; --muted:#6d7972; --paper:#f6f7f2; --card:#ffffff; --line:#e4e9e2; --lime:#d7f36a; --green:#244d3c; }
.stApp { background:var(--paper); color:var(--ink); font-family:'DM Sans',sans-serif; }
[data-testid="stHeader"] { background:transparent; }
.block-container { max-width:1420px; padding-top:1.5rem; padding-bottom:4rem; }
[data-testid="stSidebar"] { display:none; }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; color:var(--ink) !important; letter-spacing:-.04em; }
p, label, .stCaption { color:var(--muted); }
.brand-row { display:flex; align-items:center; justify-content:space-between; padding:0 0 1.2rem; border-bottom:1px solid var(--line); margin-bottom:1.4rem; }
.brand-mark { font-family:'Manrope',sans-serif; font-size:1.28rem; font-weight:800; letter-spacing:-.06em; color:var(--ink); }
.brand-mark span { display:inline-flex; align-items:center; justify-content:center; width:29px; height:29px; border-radius:9px; background:var(--lime); margin-right:8px; font-size:1rem; }
.brand-note { color:var(--muted); font-size:.82rem; }
.hero { background:var(--green); color:white; border-radius:24px; padding:2rem 2.2rem; position:relative; overflow:hidden; margin:.4rem 0 1.4rem; }
.hero:after { content:'✳'; position:absolute; right:3rem; top:-2.2rem; font-size:12rem; color:rgba(215,243,106,.13); transform:rotate(12deg); }
.hero h1 { color:white !important; font-size:2.4rem; margin:0 0 .35rem; }
.hero p { color:#d4e2d8; max-width:650px; margin:0; }
.eyebrow { text-transform:uppercase; letter-spacing:.16em; font-size:.68rem; font-weight:800; color:#d7f36a; margin-bottom:.65rem; }
.metric { background:white; border:1px solid var(--line); border-radius:17px; padding:1rem 1.2rem; min-height:94px; }
.metric-label { color:var(--muted); font-size:.78rem; }
.metric-value { font-family:'Manrope',sans-serif; font-size:1.65rem; font-weight:800; color:var(--ink); margin-top:.1rem; }
.section-kicker { color:#668071; font-size:.72rem; font-weight:800; text-transform:uppercase; letter-spacing:.14em; margin-bottom:.35rem; }
.panel { background:white; border:1px solid var(--line); border-radius:20px; padding:1.15rem 1.25rem; }
.image-card { background:white; border:1px solid var(--line); border-radius:18px; padding:.65rem; height:100%; }
.image-card-title { font-weight:800; color:var(--ink); font-size:.95rem; margin:.55rem 0 .15rem; }
.image-card-copy { color:var(--muted); font-size:.78rem; min-height:2.2rem; }
.pill { display:inline-block; padding:.32rem .7rem; border-radius:99px; background:#edf4e7; color:#365c46; font-size:.72rem; font-weight:700; }
.stButton > button { border-radius:12px; border:1px solid #dce4da; font-weight:700; min-height:2.7rem; }
.stButton > button[kind="primary"] { background:#244d3c; border-color:#244d3c; color:white; }
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] { border-radius:12px !important; }
[data-testid="stFileUploader"] { background:#fbfcf8; border:1.5px dashed #b9c8b9; border-radius:16px; padding:.5rem; }
[data-testid="stRadio"] > div { gap:.4rem; }
[data-testid="stRadio"] label { background:white; border:1px solid var(--line); padding:.45rem .9rem; border-radius:999px; }
[data-testid="stRadio"] label:has(input:checked) { background:var(--lime); border-color:var(--lime); }
hr { border-color:var(--line); }
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# Header and horizontal navigation
head_l, head_r = st.columns([2, 1])
with head_l:
    st.markdown('<div class="brand-row"><div class="brand-mark"><span>✳</span>pixelai</div><div class="brand-note">A little more imagination. A lot less editing work.</div></div>', unsafe_allow_html=True)
with head_r:
    pass
pages = ["Library", "Create", "History", "About"]
if "active_page" not in st.session_state:
    st.session_state.active_page = "Library"
nav = st.radio("Workspace", pages, horizontal=True, label_visibility="collapsed", index=pages.index(st.session_state.active_page))
st.session_state.active_page = nav


def get_api_key():
    key = os.getenv("GEMINI_API_KEY")
    try:
        key = key or st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass
    return key


def require_key():
    if not get_api_key():
        st.error("Gemini API key not found. Add GEMINI_API_KEY to your .env file, then restart the app.")
        return False
    return True


def fmt_name(item):
    return f"{item['filename']}  ·  #{item['id']}"

records = list_images()
all_versions = sum(len(list_versions(x["id"])) for x in records)

if nav == "Library":
    st.markdown('<section class="hero"><div class="eyebrow">Your visual home</div><h1>Make room for good ideas.</h1><p>Keep your images together, find them with a sentence, and send any image into the studio when inspiration strikes.</p></section>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    for col, label, value in [(m1, "Images in your library", len(records)), (m2, "Edits created", all_versions), (m3, "Workspace", "Personal")]:
        with col:
            st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)
    st.write("")
    upload_col, search_col = st.columns([.9, 1.4], gap="large")
    with upload_col:
        st.markdown('<div class="section-kicker">01 / Add to your collection</div><h3>Bring an image in</h3>', unsafe_allow_html=True)
        with st.container(border=True):
            up = st.file_uploader("Choose a photo", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")
            st.caption("PNG, JPG or WebP · Gemini will write a searchable description.")
            if up and st.button("＋ Add image to library", type="primary", use_container_width=True):
                if require_key():
                    try:
                        data = up.getvalue()
                        path = save_upload(data, up.name)
                        image_id = add_image(up.name, str(path), "", up.type or "image/jpeg")
                        with st.spinner("Looking closely at your image…"):
                            caption = caption_image(data, up.type or "image/jpeg")
                        update_caption(image_id, caption)
                        st.success("Added to your library.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Could not add this image: {exc}")
    with search_col:
        st.markdown('<div class="section-kicker">02 / Find something</div><h3>Search by what you remember</h3>', unsafe_allow_html=True)
        query = st.text_input("Search library", placeholder="Try: a dog in a park, sunset, product photo…", label_visibility="collapsed")
        st.caption("Search uses the image descriptions generated when you upload.")
    current = search_images(query, records) if query else records
    st.markdown(f'<div class="section-kicker">YOUR COLLECTION · {len(current)} RESULT(S)</div>', unsafe_allow_html=True)
    if not current:
        st.info("Nothing here yet. Add your first image above to get started." if not records else "No images match that description. Try a broader phrase.")
    else:
        cols = st.columns(3, gap="large")
        for idx, item in enumerate(current):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.image(item["path"], use_container_width=True)
                    st.markdown(f'<div class="image-card-title">{item["filename"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="image-card-copy">{(item["caption"] or "No description available yet.")[:145]}</div>', unsafe_allow_html=True)
                    st.caption(f"Added {item['created_at'][:10]}")
                    if st.button("Open in studio →", key=f"open_{item['id']}", use_container_width=True):
                        st.session_state["selected_id"] = item["id"]
                        st.session_state["go_create"] = True
                        st.rerun()

elif nav == "Create":
    st.markdown('<div class="section-kicker">CREATIVE WORKSPACE / 01</div><h1>What are we changing today?</h1><p>Choose an image, describe the result you want, and let Gemini handle the edit.</p>', unsafe_allow_html=True)
    if st.session_state.pop("go_create", False):
        st.info("Image selected from your library. Your edit workspace is ready.")
    records = list_images()
    if not records:
        st.warning("Your library is empty. Go to Library and add an image first.")
    else:
        ids = [x["id"] for x in records]
        selected = st.session_state.get("selected_id", ids[0])
        if selected not in ids:
            selected = ids[0]
        left, right = st.columns([.85, 1.35], gap="large")
        with left:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown('<div class="section-kicker">STEP 1 · SELECT</div><h3>Your starting image</h3>', unsafe_allow_html=True)
            selected = st.selectbox("Choose from library", ids, index=ids.index(selected), format_func=lambda x: fmt_name(next(r for r in records if r["id"] == x)))
            st.session_state["selected_id"] = selected
            item = get_image(selected)
            st.image(item["path"], use_container_width=True)
            st.caption(item["caption"] or "No image description available.")
            st.markdown('</div>', unsafe_allow_html=True)
        with right:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown('<div class="section-kicker">STEP 2 · DESCRIBE</div><h3>Give your image a new direction</h3>', unsafe_allow_html=True)
            presets = {
                "Write my own instruction": "",
                "Polish the photo": "Improve lighting, sharpness and visual quality while preserving the subject and composition.",
                "Dreamy golden hour": "Give the scene a warm, dreamy golden-hour look with soft natural light. Preserve the main subject and composition.",
                "Minimal studio background": "Replace the background with a clean, elegant neutral studio background. Keep the main subject unchanged.",
                "Vibrant editorial colours": "Make the colours richer and more vibrant with a polished editorial photography look. Keep all objects and details unchanged.",
                "Remove a distracting object": "Remove the distracting object I describe and naturally reconstruct the area behind it."
            }
            preset = st.selectbox("Start with an idea", list(presets.keys()))
            prompt = st.text_area("Your editing instruction", value=presets[preset], height=150, placeholder="Example: Replace the cloudy sky with a clear blue sky, keeping the buildings untouched.")
            st.caption("Be specific about what should change and what should stay the same.")
            run = st.button("✳ Generate new version", type="primary", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if run:
                if not prompt.strip():
                    st.warning("Write an editing instruction first.")
                elif require_key():
                    try:
                        with st.spinner("Creating your new version… this may take a minute."):
                            result = edit_image(Path(item["path"]).read_bytes(), item["mime_type"], prompt.strip())
                            output_path = save_version(result, selected)
                            version_no = add_version(selected, str(output_path), prompt.strip())
                        st.session_state["latest_edit"] = str(output_path)
                        st.session_state["latest_edit_source"] = selected
                        st.success(f"Version {version_no} saved. Your original is still safe.")
                    except Exception as exc:
                        st.error(f"The edit could not be generated: {exc}")
        latest = st.session_state.get("latest_edit")
        if latest and Path(latest).exists() and st.session_state.get("latest_edit_source") == selected:
            st.markdown('<div class="section-kicker">STEP 3 · REVIEW YOUR RESULT</div><h3>Original vs. new version</h3>', unsafe_allow_html=True)
            a, b = st.columns(2, gap="large")
            with a:
                st.image(item["path"], caption="Original", use_container_width=True)
            with b:
                st.image(latest, caption="AI-edited version", use_container_width=True)
                st.download_button("↓ Download edited image", Path(latest).read_bytes(), file_name=Path(latest).name, mime="image/png", use_container_width=True)

elif nav == "History":
    st.markdown('<div class="section-kicker">YOUR CREATIVE TRAIL</div><h1>Every version, in one place.</h1><p>Review earlier edits and download any version without losing the original.</p>', unsafe_allow_html=True)
    records = list_images()
    if not records:
        st.info("Your library is empty. Add an image to start building its history.")
    else:
        chosen = st.selectbox("Select an image", [x["id"] for x in records], format_func=lambda x: fmt_name(next(r for r in records if r["id"] == x)))
        item = get_image(chosen)
        versions = list_versions(chosen)
        original_col, detail_col = st.columns([.85, 1.35], gap="large")
        with original_col:
            st.markdown('<div class="section-kicker">ORIGINAL</div>', unsafe_allow_html=True)
            st.image(item["path"], use_container_width=True)
            st.markdown(f"**{item['filename']}**")
            st.caption(f"Added {item['created_at']}")
        with detail_col:
            st.markdown(f'<div class="section-kicker">{len(versions)} SAVED EDIT(S)</div><h3>Version timeline</h3>', unsafe_allow_html=True)
            if not versions:
                st.info("No edits saved for this image yet. Head to Create to make the first one.")
            for version in versions:
                with st.container(border=True):
                    vcol, tcol = st.columns([.75, 1.25], gap="large")
                    with vcol:
                        st.image(version["path"], use_container_width=True)
                    with tcol:
                        st.markdown(f"**Version {version['version_no']}**  ·  {version['created_at'][:16]}")
                        st.write(version["prompt"])
                        st.download_button("↓ Download this version", Path(version["path"]).read_bytes(), file_name=Path(version["path"]).name, mime="image/png", key=f"download_{version['id']}")

else:
    st.markdown('<section class="hero"><div class="eyebrow">About the project</div><h1>PixelAI is your image-making sidekick.</h1><p>A simple AI-powered image library where you can describe photos, find them in plain language, and create new versions with natural-language instructions.</p></section>', unsafe_allow_html=True)
    a, b = st.columns(2, gap="large")
    with a:
        st.markdown("### What it can do")
        st.markdown("- Upload JPG, PNG and WebP images.\n- Generate image descriptions with Gemini Vision.\n- Search your collection using words and phrases.\n- Edit an image using a natural-language prompt.\n- Preserve originals and keep a version history.")
    with b:
        st.markdown("### How it is built")
        st.markdown("- **Frontend:** Streamlit\n- **AI:** Google Gemini API\n- **Metadata:** SQLite\n- **Image storage:** Local folders\n- **Image processing:** Pillow")
        st.info("This is a local, single-user project prototype. Production deployment would require authentication, cloud storage, access controls and stronger semantic search.")
    st.markdown("### API configuration")
    st.code("GEMINI_API_KEY=your_key_here\nGEMINI_VISION_MODEL=gemini-2.5-flash\nGEMINI_IMAGE_MODEL=gemini-3.1-flash-image", language="bash")

st.markdown("<br><div style='border-top:1px solid #e4e9e2;padding-top:1rem;color:#829087;font-size:.75rem'>PIXELAI · MADE FOR YOUR NEXT GOOD IDEA</div>", unsafe_allow_html=True)
