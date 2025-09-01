from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from posts.schemas import PostCreate, PostRead, PostUpdate
from posts.models import Post


from core.dependencies import GetSessionmaker

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("/")
async def get_posts(sessionmaker: GetSessionmaker) -> list[PostRead]:

    async with sessionmaker() as session:
        posts = await session.scalars(select(Post))

    return posts.all()


@router.get("/{id}")
async def get_post(id: int, sessionmaker: GetSessionmaker) -> PostRead:
    async with sessionmaker() as session:
        post = await session.scalar(select(Post).where(Post.id ==id))

        if post is None:
            raise HTTPException(status_code=404, detail="Item not found")
    return post


@router.post("/")
async def create_post(post: PostCreate, sessionmaker: GetSessionmaker) -> PostRead:
    async with sessionmaker() as session:
        post = Post(title=post.title, content=post.content, author=post.author)
        session.add(post)
        await session.commit()
        return post
    

@router.put("/{id}")
async def update_post(id: int, post_update: PostUpdate, sessionmaker: GetSessionmaker) -> PostRead:
    async with sessionmaker() as session:
        post = await session.scalar(select(Post).where(Post.id == id))

        if post is None:
            raise HTTPException(status_code=404, detail="Item not found")

        post.title = post_update.title
        post.content = post_update.content
        post.author = post_update.author
        post.edited_at = datetime.now(timezone.utc)
        await session.commit()
        return post
    