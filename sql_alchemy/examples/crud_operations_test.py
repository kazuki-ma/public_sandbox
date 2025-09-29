"""Test cases for CRUD operations."""

import pytest
from examples.crud_operations import UserCRUD, PostCRUD, CommentCRUD, TagCRUD


class TestUserCRUD:
    """Test User CRUD operations."""

    def test_create_user(self, db_session):
        """Test creating a new user."""
        user = UserCRUD.create_user(
            db_session,
            username="new_user",
            email="new@example.com",
            password="password123",
            full_name="New User"
        )

        assert user.id is not None
        assert user.username == "new_user"
        assert user.email == "new@example.com"
        assert user.full_name == "New User"
        assert user.is_active is True
        assert user.is_superuser is False

    def test_get_user(self, db_session, sample_user):
        """Test getting a user by ID."""
        user = UserCRUD.get_user(db_session, sample_user.id)

        assert user is not None
        assert user.id == sample_user.id
        assert user.username == sample_user.username

    def test_get_user_by_email(self, db_session, sample_user):
        """Test getting a user by email."""
        user = UserCRUD.get_user_by_email(db_session, sample_user.email)

        assert user is not None
        assert user.email == sample_user.email
        assert user.id == sample_user.id

    def test_get_users(self, db_session, sample_user):
        """Test getting multiple users with pagination."""
        # Create additional users
        UserCRUD.create_user(db_session, "user2", "user2@example.com", "pass2")
        UserCRUD.create_user(db_session, "user3", "user3@example.com", "pass3")

        users = UserCRUD.get_users(db_session, skip=0, limit=2)
        assert len(users) == 2

        all_users = UserCRUD.get_users(db_session)
        assert len(all_users) >= 3

    def test_update_user(self, db_session, sample_user):
        """Test updating user data."""
        updated_user = UserCRUD.update_user(
            db_session,
            sample_user.id,
            full_name="Updated Name",
            bio="New bio"
        )

        assert updated_user is not None
        assert updated_user.full_name == "Updated Name"
        assert updated_user.bio == "New bio"

    def test_delete_user(self, db_session):
        """Test deleting a user."""
        user = UserCRUD.create_user(
            db_session,
            username="to_delete",
            email="delete@example.com",
            password="pass123"
        )
        user_id = user.id

        # Delete the user
        result = UserCRUD.delete_user(db_session, user_id)
        assert result is True

        # Verify user is deleted
        deleted_user = UserCRUD.get_user(db_session, user_id)
        assert deleted_user is None

    def test_delete_nonexistent_user(self, db_session):
        """Test deleting a non-existent user."""
        result = UserCRUD.delete_user(db_session, 999999)
        assert result is False


class TestPostCRUD:
    """Test Post CRUD operations."""

    def test_create_post(self, db_session, sample_user):
        """Test creating a new post."""
        post = PostCRUD.create_post(
            db_session,
            title="New Test Post",
            content="This is the content of the new test post.",
            author_id=sample_user.id,
            slug="new-test-post",
            summary="Test summary"
        )

        assert post.id is not None
        assert post.title == "New Test Post"
        assert post.content == "This is the content of the new test post."
        assert post.author_id == sample_user.id
        assert post.is_published is False

    def test_get_post(self, db_session, sample_post):
        """Test getting a post by ID."""
        post = PostCRUD.get_post(db_session, sample_post.id)

        assert post is not None
        assert post.id == sample_post.id
        assert post.title == sample_post.title

    def test_get_posts(self, db_session, sample_user):
        """Test getting multiple posts with pagination."""
        # Create additional posts
        for i in range(5):
            PostCRUD.create_post(
                db_session,
                title=f"Post {i}",
                content=f"Content {i}",
                author_id=sample_user.id
            )

        posts = PostCRUD.get_posts(db_session, skip=0, limit=3)
        assert len(posts) == 3

        all_posts = PostCRUD.get_posts(db_session, skip=0, limit=100)
        assert len(all_posts) >= 5

    def test_get_posts_by_author(self, db_session, sample_user, sample_post):
        """Test getting posts by a specific author."""
        # Create another post by the same author
        PostCRUD.create_post(
            db_session,
            title="Another Post",
            content="Another content",
            author_id=sample_user.id
        )

        posts = PostCRUD.get_posts_by_author(db_session, sample_user.id)
        assert len(posts) >= 2
        assert all(post.author_id == sample_user.id for post in posts)

    def test_update_post(self, db_session, sample_post):
        """Test updating post data."""
        updated_post = PostCRUD.update_post(
            db_session,
            sample_post.id,
            title="Updated Title",
            is_published=True
        )

        assert updated_post is not None
        assert updated_post.title == "Updated Title"
        assert updated_post.is_published is True

    def test_delete_post(self, db_session, sample_user):
        """Test deleting a post."""
        post = PostCRUD.create_post(
            db_session,
            title="To Delete",
            content="Will be deleted",
            author_id=sample_user.id
        )
        post_id = post.id

        # Delete the post
        result = PostCRUD.delete_post(db_session, post_id)
        assert result is True

        # Verify post is deleted
        deleted_post = PostCRUD.get_post(db_session, post_id)
        assert deleted_post is None

    def test_add_tag_to_post(self, db_session, sample_post, sample_tag):
        """Test adding a tag to a post."""
        post = PostCRUD.add_tag_to_post(
            db_session,
            sample_post.id,
            sample_tag.id
        )

        assert post is not None
        assert len(post.tags) == 1
        assert post.tags[0].id == sample_tag.id


class TestCommentCRUD:
    """Test Comment CRUD operations."""

    def test_create_comment(self, db_session, sample_user, sample_post):
        """Test creating a new comment."""
        comment = CommentCRUD.create_comment(
            db_session,
            content="Test comment",
            author_id=sample_user.id,
            post_id=sample_post.id
        )

        assert comment.id is not None
        assert comment.content == "Test comment"
        assert comment.author_id == sample_user.id
        assert comment.post_id == sample_post.id

    def test_create_reply(self, db_session, sample_user, sample_post, sample_comment):
        """Test creating a reply to a comment."""
        reply = CommentCRUD.create_comment(
            db_session,
            content="Test reply",
            author_id=sample_user.id,
            post_id=sample_post.id,
            parent_id=sample_comment.id
        )

        assert reply.id is not None
        assert reply.parent_id == sample_comment.id

    def test_get_post_comments(self, db_session, sample_user, sample_post):
        """Test getting comments for a post."""
        # Create multiple comments
        CommentCRUD.create_comment(
            db_session, "Comment 1", sample_user.id, sample_post.id
        )
        CommentCRUD.create_comment(
            db_session, "Comment 2", sample_user.id, sample_post.id
        )

        comments = CommentCRUD.get_post_comments(db_session, sample_post.id)
        assert len(comments) >= 2

    def test_update_comment(self, db_session, sample_comment):
        """Test updating a comment."""
        updated = CommentCRUD.update_comment(
            db_session,
            sample_comment.id,
            "Updated content"
        )

        assert updated is not None
        assert updated.content == "Updated content"

    def test_delete_comment(self, db_session, sample_user, sample_post):
        """Test deleting a comment."""
        comment = CommentCRUD.create_comment(
            db_session, "To delete", sample_user.id, sample_post.id
        )
        comment_id = comment.id

        result = CommentCRUD.delete_comment(db_session, comment_id)
        assert result is True

        deleted = CommentCRUD.get_comment(db_session, comment_id)
        assert deleted is None


class TestTagCRUD:
    """Test Tag CRUD operations."""

    def test_create_tag(self, db_session):
        """Test creating a new tag."""
        tag = TagCRUD.create_tag(
            db_session,
            name="TestTag",
            slug="test-tag",
            description="Test description"
        )

        assert tag.id is not None
        assert tag.name == "TestTag"
        assert tag.slug == "test-tag"

    def test_get_tag_by_name(self, db_session, sample_tag):
        """Test getting a tag by name."""
        tag = TagCRUD.get_tag_by_name(db_session, sample_tag.name)

        assert tag is not None
        assert tag.id == sample_tag.id

    def test_get_posts_by_tag(self, db_session, sample_tag, sample_post):
        """Test getting posts with a specific tag."""
        sample_post.tags.append(sample_tag)
        db_session.commit()

        posts = TagCRUD.get_posts_by_tag(db_session, sample_tag.id)
        assert len(posts) >= 1
        assert sample_post in posts