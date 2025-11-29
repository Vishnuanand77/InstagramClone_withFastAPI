# InstagramClone_withFastAPI

Simple Social is a lightweight Instagram-inspired playground that pairs a FastAPI backend with a Streamlit frontend. Users can register/login with JWT auth, upload images or short videos to ImageKit, and browse/delete their own posts from a unified feed.

## Tech Stack
- FastAPI + FastAPI Users for auth, dependency injection, and JWT handling
- Async SQLAlchemy + SQLite for persistent storage
- ImageKit for hosted media, resizing, and caption overlays
- Streamlit for a fast, password-protected web UI
- `uv` + `pyproject.toml` for reproducible Python environments

## Getting Started
### 1. Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or a virtualenv tool of your choice
- ImageKit account (for API keys)

### 2. Environment variables
Create a `.env` file in the project root with your ImageKit credentials:
```
IMAGEKIT_PUBLIC_KEY=pk_xxx
IMAGEKIT_PRIVATE_KEY=sk_xxx
IMAGEKIT_URL=https://ik.imagekit.io/<your_id>
```

### 3. Install dependencies
```
cd "/Users/vishnuanand/Documents/Purdue Files/Instagram_Clone_FastAPI/InstagramClone_withFastAPI"
uv sync
```
If you prefer `pip`, create and activate a virtualenv and run `pip install -e .`.

### 4. Run the backend API
```
uv run python main.py
# or
uv run uvicorn app.app:app --reload --host 0.0.0.0 --port 8000
```
The SQLite database (`test.db`) and tables are created automatically on startup.

### 5. Launch the Streamlit client
In a second terminal (while the API keeps running):
```
uv run streamlit run frontend.py
```
Visit the URL Streamlit prints (typically `http://localhost:8501`). Register a user, log in, and start posting.

## Topics Explored While Building
- Structuring a FastAPI app with a lifespan context to bootstrap async DB connections.
- Using FastAPI dependency injection to share the async SQLAlchemy session and enforce `current_active_user`.
- Integrating FastAPI Users to avoid hand-rolling JWT auth, password hashing, and reset/verify flows.
- Designing async SQLAlchemy models with UUID primary keys and relationships between `User` and `Post`.
- Handling media uploads with `UploadFile`, temp files, and piping them to ImageKit, including text overlays for captions.
- Building a simple but stateful Streamlit UI that handles auth tokens, feeds, uploads, and deletions via REST calls.

## What I Learned
- How JWT auth works end-to-end when FastAPI Users handles token issuance while Streamlit stores tokens in `st.session_state`.
- The ergonomics of async SQLAlchemy sessions—committing, refreshing, and querying without blocking the event loop.
- Practical secrets management using `.env` + `python-dotenv` to keep API keys out of the codebase.
- The tradeoffs of using hosted media storage (ImageKit) versus storing blobs locally, especially for transformations.
- How quickly Streamlit can serve as a full-featured client for a REST API, making backend testing far more visual.

Feel free to open issues or extend the project—ideas include comments, likes, follower graphs, and richer notification flows.