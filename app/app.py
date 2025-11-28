from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import PostCreate, PostResponse, UserRead, UserCreate, UserUpdate
from app.db import create_db_and_tables, Post, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import shutil
import uuid
import os
import tempfile
from app.users import fastapi_users, current_active_user, auth_backend

"""
A context manager that creates the database and tables if they don't exist and yields the app object on application boot/shutdown.
"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), # Receive a file object to this endpoint
    caption: str = Form(...), # Receive a caption from the form data
    session: AsyncSession = Depends(get_async_session) # Dependency injection: Receive a session object from the dependency graph
):

    temp_file_path = None
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        upload_result = imagekit.upload_file(
            file=open(temp_file_path, "rb"),
            file_name=file.filename,
            options=UploadFileRequestOptions(
                use_unique_file_name=True,
                tags=["backend-upload"]
            )
        )

        if upload_result.response_metadata.http_status_code == 200:
            # Instantiate the data to be stored in the database
            post = Post(
                caption=caption,
                url=upload_result.url,
                file_type="video" if file.content_type.startswith("video/") else "image",
                file_name=upload_result.name
            )
            # Add the post to the database
            session.add(post)
            # Commit the transaction to the database asynchronously
            await session.commit()
            # Refresh the post object to get the updated id asynchronously
            await session.refresh(post)
            return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()

@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session)
    ):

    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    # FastAPI returns a cursor object that contains the results of the query. We need to convert it to a list of posts.
    posts = [row[0] for row in result.all()] 

    posts_data = []
    for post in posts:
        posts_data.append({
            "id": str(post.id),
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at.isoformat(),
            "updated_at": post.updated_at.isoformat(),
        })
    
    return {"posts": posts_data}


@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        post_uuid = uuid.UUID(post_id)
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        await session.delete(post)
        await session.commit()
        return {"success": True, "message": "Post deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





# ===============================
# Initial Setup for Learning Purposes
# ===============================

# # Persistent dummy data
# text_posts = {
#     1: {"title": "Hello World", "content": "This is a test post"},
#     2: {"title": "Hello World 2", "content": "This is a test post 2"},
#     3: {"title": "Exploring Python Dictionaries", "content": "A short example showing how dictionaries can store structured data."},
#     4: {"title": "Why Dummy Data Matters", "content": "Dummy data helps with testing, prototyping, and debugging applications."},
#     5: {"title": "Hello From a New Post", "content": "Just another placeholder post to expand the dataset."},
#     6: {"title": "Learning to Store Data", "content": "Using Python data structures effectively can make development smoother."}
# }

# @app.get("/posts")
# def get_all_posts(limit: int = None):
#     if limit:
#         if limit > len(text_posts):
#             raise HTTPException(status_code=400, detail="Limit is greater than the number of posts")
#         return list(text_posts.values())[:limit]
#     return list(text_posts.values())

# @app.get("/posts/{post_id}")
# def get_post(post_id: int) -> PostResponse:
#     if post_id not in text_posts:
#         raise HTTPException(status_code=404, detail="Post not found")
#     return text_posts[post_id]

# """
# Breaking down a FastAPI endpoint
#     1. The endpoint decorator - @app.post("/posts"): Registers the function underneath as a HTTP POST request handler for the path "/posts"
#     2. Parameter (post: PostCreate):
#         - Defines the expected request body schema using Pydantic models
#         - When a request comes in, FastAPI will automatically validate the request body against the schema, creates a PostCreate object and injects it into the function as the post parameter.
#     3. Response:
#         - Inside the function we handle the incoming PostCreate Object and return a dictionary with the post data.
#         - Additionally, we can also validate the response from the post function to be validated against the PostCreate schema or a different response schema by adding a return type annotation to the function.
#         - For example:
#             @app.post("/posts")
#             def create_post(post: PostCreate) -> PostCreate:
#                 new_post = {
#                     "title": post.title,
#                     "content": post.content,
#                 }
# """
# @app.post("/posts")
# def create_post(post: PostCreate) -> PostResponse:
#     new_post = {
#         "title": post.title,
#         "content": post.content,
#     }
#     text_posts[len(text_posts) + 1] = new_post
#     return new_post