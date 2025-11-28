from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import PostCreate, PostResponse
from app.db import create_db_and_tables, Post, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select

"""
A context manager that creates the database and tables if they don't exist and yields the app object on application boot/shutdown.
"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), # Receive a file object to this endpoint
    caption: str = Form(...), # Receive a caption from the form data
    session: AsyncSession = Depends(get_async_session) # Dependency injection: Receive a session object from the dependency graph
):
    # Instantiate the data to be stored in the database
    post = Post(
        caption=caption,
        url="dummy_url",
        file_type="dummy_file_type",
        file_name="dummy_file_name"
    )
    # Add the post to the database
    session.add(post)
    # Commit the transaction to the database asynchronously
    await session.commit()
    # Refresh the post object to get the updated id asynchronously
    await session.refresh(post)
    return post

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