"""Comment model definition."""

from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from config import Base


class Comment(Base):
    """Comment model for posts."""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    is_approved = Column(Boolean, default=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete='CASCADE'), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id", ondelete='CASCADE'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

    # Self-referential relationship for nested comments
    parent = relationship("Comment", remote_side=[id], backref="replies")

    def __repr__(self):
        return f"<Comment(id={self.id}, author_id={self.author_id}, post_id={self.post_id})>"