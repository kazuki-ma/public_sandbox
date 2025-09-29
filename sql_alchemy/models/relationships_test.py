"""Test cases for model relationships."""

import pytest
from models import User, Post, Comment, Tag
from examples.crud_operations import PostCRUD, CommentCRUD


class TestRelationships:
    """Test relationships between models."""

    def test_user_posts_relationship(self, db_session, sample_user):
        """Test one-to-many relationship between User and Posts."""
        # Create multiple posts for the user
        post1 = PostCRUD.create_post(
            db_session, "Post 1", "Content 1", sample_user.id
        )
        post2 = PostCRUD.create_post(
            db_session, "Post 2", "Content 2", sample_user.id
        )

        # Refresh the user to get updated relationships
        db_session.refresh(sample_user)

        assert len(sample_user.posts) == 2
        assert post1 in sample_user.posts
        assert post2 in sample_user.posts

    def test_post_author_relationship(self, db_session, sample_post, sample_user):
        """Test many-to-one relationship between Post and User."""
        assert sample_post.author is not None
        assert sample_post.author.id == sample_user.id
        assert sample_post.author.username == sample_user.username

    def test_post_comments_relationship(self, db_session, sample_post, sample_user):
        """Test one-to-many relationship between Post and Comments."""
        # Create multiple comments
        comment1 = CommentCRUD.create_comment(
            db_session, "Comment 1", sample_user.id, sample_post.id
        )
        comment2 = CommentCRUD.create_comment(
            db_session, "Comment 2", sample_user.id, sample_post.id
        )

        # Refresh the post to get updated relationships
        db_session.refresh(sample_post)

        assert len(sample_post.comments) == 2
        assert comment1 in sample_post.comments
        assert comment2 in sample_post.comments

    def test_comment_replies_relationship(self, db_session, sample_post, sample_user):
        """Test self-referential relationship for nested comments."""
        # Create parent comment
        parent_comment = CommentCRUD.create_comment(
            db_session, "Parent comment", sample_user.id, sample_post.id
        )

        # Create replies
        reply1 = CommentCRUD.create_comment(
            db_session, "Reply 1", sample_user.id, sample_post.id, parent_comment.id
        )
        reply2 = CommentCRUD.create_comment(
            db_session, "Reply 2", sample_user.id, sample_post.id, parent_comment.id
        )

        # Refresh parent comment
        db_session.refresh(parent_comment)

        assert len(parent_comment.replies) == 2
        assert reply1.parent_id == parent_comment.id
        assert reply2.parent_id == parent_comment.id

    def test_post_tags_many_to_many(self, db_session, sample_post, sample_user):
        """Test many-to-many relationship between Posts and Tags."""
        # Create tags
        tag1 = Tag(name="Python", slug="python")
        tag2 = Tag(name="SQLAlchemy", slug="sqlalchemy")
        db_session.add_all([tag1, tag2])
        db_session.commit()

        # Add tags to post
        sample_post.tags.append(tag1)
        sample_post.tags.append(tag2)
        db_session.commit()

        # Refresh to get updated relationships
        db_session.refresh(sample_post)
        db_session.refresh(tag1)

        assert len(sample_post.tags) == 2
        assert tag1 in sample_post.tags
        assert tag2 in sample_post.tags
        assert sample_post in tag1.posts

    def test_cascade_delete_user_posts(self, db_session):
        """Test cascade delete: deleting user should delete their posts."""
        # Create user with posts
        user = User(
            username="cascade_test",
            email="cascade@test.com",
            hashed_password="test"
        )
        db_session.add(user)
        db_session.commit()

        post = Post(
            title="Cascade Test Post",
            content="Test content",
            author_id=user.id
        )
        db_session.add(post)
        db_session.commit()

        post_id = post.id

        # Delete user
        db_session.delete(user)
        db_session.commit()

        # Check if post is also deleted
        deleted_post = db_session.query(Post).filter_by(id=post_id).first()
        assert deleted_post is None

    def test_cascade_delete_post_comments(self, db_session, sample_user):
        """Test cascade delete: deleting post should delete its comments."""
        # Create post
        post = Post(
            title="Post with comments",
            content="Content",
            author_id=sample_user.id
        )
        db_session.add(post)
        db_session.commit()

        # Create comment
        comment = Comment(
            content="Test comment",
            author_id=sample_user.id,
            post_id=post.id
        )
        db_session.add(comment)
        db_session.commit()

        comment_id = comment.id

        # Delete post
        db_session.delete(post)
        db_session.commit()

        # Check if comment is also deleted
        deleted_comment = db_session.query(Comment).filter_by(id=comment_id).first()
        assert deleted_comment is None