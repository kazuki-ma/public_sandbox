"""CRUD operations examples for SQLAlchemy models."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import User, Post, Comment, Tag
from config import Base


class UserCRUD:
    """CRUD operations for User model."""

    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str, **kwargs) -> User:
        """Create a new user."""
        user = User(
            username=username,
            email=email,
            hashed_password=password,  # In production, hash the password first
            **kwargs
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get list of users with pagination."""
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
        """Update user data."""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user."""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False


class PostCRUD:
    """CRUD operations for Post model."""

    @staticmethod
    def create_post(db: Session, title: str, content: str, author_id: int, **kwargs) -> Post:
        """Create a new post."""
        post = Post(
            title=title,
            content=content,
            author_id=author_id,
            **kwargs
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        return post

    @staticmethod
    def get_post(db: Session, post_id: int) -> Optional[Post]:
        """Get post by ID with author and comments."""
        return db.query(Post).filter(Post.id == post_id).first()

    @staticmethod
    def get_posts(db: Session, skip: int = 0, limit: int = 10) -> List[Post]:
        """Get list of posts with pagination."""
        return db.query(Post).offset(skip).limit(limit).all()

    @staticmethod
    def get_posts_by_author(db: Session, author_id: int) -> List[Post]:
        """Get all posts by a specific author."""
        return db.query(Post).filter(Post.author_id == author_id).all()

    @staticmethod
    def update_post(db: Session, post_id: int, **kwargs) -> Optional[Post]:
        """Update post data."""
        post = db.query(Post).filter(Post.id == post_id).first()
        if post:
            for key, value in kwargs.items():
                setattr(post, key, value)
            db.commit()
            db.refresh(post)
        return post

    @staticmethod
    def delete_post(db: Session, post_id: int) -> bool:
        """Delete post."""
        post = db.query(Post).filter(Post.id == post_id).first()
        if post:
            db.delete(post)
            db.commit()
            return True
        return False

    @staticmethod
    def add_tag_to_post(db: Session, post_id: int, tag_id: int) -> Optional[Post]:
        """Add a tag to a post."""
        post = db.query(Post).filter(Post.id == post_id).first()
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if post and tag:
            post.tags.append(tag)
            db.commit()
            db.refresh(post)
            return post
        return None


class CommentCRUD:
    """CRUD operations for Comment model."""

    @staticmethod
    def create_comment(
        db: Session,
        content: str,
        author_id: int,
        post_id: int,
        parent_id: Optional[int] = None
    ) -> Comment:
        """Create a new comment."""
        comment = Comment(
            content=content,
            author_id=author_id,
            post_id=post_id,
            parent_id=parent_id
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def get_comment(db: Session, comment_id: int) -> Optional[Comment]:
        """Get comment by ID."""
        return db.query(Comment).filter(Comment.id == comment_id).first()

    @staticmethod
    def get_post_comments(db: Session, post_id: int) -> List[Comment]:
        """Get all comments for a specific post."""
        return db.query(Comment).filter(
            Comment.post_id == post_id,
            Comment.parent_id == None
        ).all()

    @staticmethod
    def get_comment_replies(db: Session, parent_id: int) -> List[Comment]:
        """Get all replies to a specific comment."""
        return db.query(Comment).filter(Comment.parent_id == parent_id).all()

    @staticmethod
    def update_comment(db: Session, comment_id: int, content: str) -> Optional[Comment]:
        """Update comment content."""
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if comment:
            comment.content = content
            db.commit()
            db.refresh(comment)
        return comment

    @staticmethod
    def delete_comment(db: Session, comment_id: int) -> bool:
        """Delete comment."""
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if comment:
            db.delete(comment)
            db.commit()
            return True
        return False


class TagCRUD:
    """CRUD operations for Tag model."""

    @staticmethod
    def create_tag(db: Session, name: str, **kwargs) -> Tag:
        """Create a new tag."""
        tag = Tag(name=name, **kwargs)
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag

    @staticmethod
    def get_tag(db: Session, tag_id: int) -> Optional[Tag]:
        """Get tag by ID."""
        return db.query(Tag).filter(Tag.id == tag_id).first()

    @staticmethod
    def get_tag_by_name(db: Session, name: str) -> Optional[Tag]:
        """Get tag by name."""
        return db.query(Tag).filter(Tag.name == name).first()

    @staticmethod
    def get_tags(db: Session) -> List[Tag]:
        """Get all tags."""
        return db.query(Tag).all()

    @staticmethod
    def get_posts_by_tag(db: Session, tag_id: int) -> List[Post]:
        """Get all posts with a specific tag."""
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        return tag.posts if tag else []