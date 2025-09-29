"""Usage example demonstrating SQLAlchemy with sample data."""

from config import DatabaseConfig
from examples.crud_operations import UserCRUD, PostCRUD, CommentCRUD, TagCRUD


def main():
    """Main function demonstrating CRUD operations."""
    # Initialize database
    db_config = DatabaseConfig()
    db_config.create_tables()

    # Get a database session
    db = next(db_config.get_session())

    try:
        print("Creating sample data...")

        # Create users
        user1 = UserCRUD.create_user(
            db,
            username="john_doe",
            email="john@example.com",
            password="hashed_password_123",
            full_name="John Doe"
        )
        print(f"Created user: {user1}")

        user2 = UserCRUD.create_user(
            db,
            username="jane_smith",
            email="jane@example.com",
            password="hashed_password_456",
            full_name="Jane Smith"
        )
        print(f"Created user: {user2}")

        # Create tags
        tech_tag = TagCRUD.create_tag(db, name="Technology", slug="technology")
        python_tag = TagCRUD.create_tag(db, name="Python", slug="python")
        print(f"Created tags: {tech_tag.name}, {python_tag.name}")

        # Create posts
        post1 = PostCRUD.create_post(
            db,
            title="Introduction to SQLAlchemy",
            content="SQLAlchemy is a powerful ORM for Python...",
            author_id=user1.id,
            slug="introduction-to-sqlalchemy",
            summary="Learn the basics of SQLAlchemy"
        )
        print(f"Created post: {post1.title}")

        post2 = PostCRUD.create_post(
            db,
            title="Advanced Database Patterns",
            content="Let's explore advanced patterns in database design...",
            author_id=user2.id,
            slug="advanced-database-patterns",
            summary="Database design patterns for complex applications"
        )
        print(f"Created post: {post2.title}")

        # Add tags to posts
        PostCRUD.add_tag_to_post(db, post1.id, python_tag.id)
        PostCRUD.add_tag_to_post(db, post1.id, tech_tag.id)
        PostCRUD.add_tag_to_post(db, post2.id, tech_tag.id)

        # Create comments
        comment1 = CommentCRUD.create_comment(
            db,
            content="Great article! Very helpful.",
            author_id=user2.id,
            post_id=post1.id
        )
        print(f"Created comment on post {post1.id}")

        # Create a reply to the comment
        reply1 = CommentCRUD.create_comment(
            db,
            content="Thank you! Glad you found it helpful.",
            author_id=user1.id,
            post_id=post1.id,
            parent_id=comment1.id
        )
        print(f"Created reply to comment {comment1.id}")

        # Query examples
        print("\n--- Query Examples ---")

        # Get all users
        users = UserCRUD.get_users(db)
        print(f"Total users: {len(users)}")

        # Get posts by author
        john_posts = PostCRUD.get_posts_by_author(db, user1.id)
        print(f"Posts by {user1.username}: {len(john_posts)}")

        # Get comments for a post
        post1_comments = CommentCRUD.get_post_comments(db, post1.id)
        print(f"Comments on post '{post1.title}': {len(post1_comments)}")

        # Get posts by tag
        tech_posts = TagCRUD.get_posts_by_tag(db, tech_tag.id)
        print(f"Posts with '{tech_tag.name}' tag: {len(tech_posts)}")

        # Update example
        updated_post = PostCRUD.update_post(
            db,
            post1.id,
            title="Introduction to SQLAlchemy (Updated)",
            is_published=True
        )
        print(f"\nUpdated post title: {updated_post.title}")

        # Delete example (commented out to preserve data)
        # deleted = CommentCRUD.delete_comment(db, reply1.id)
        # print(f"Deleted reply: {deleted}")

        print("\n--- Relationship Examples ---")

        # Access relationships
        post_with_author = PostCRUD.get_post(db, post1.id)
        print(f"Post '{post_with_author.title}' by {post_with_author.author.username}")

        # Access tags through post
        print(f"Tags for '{post_with_author.title}': {[tag.name for tag in post_with_author.tags]}")

        # Access posts through user
        user_with_posts = UserCRUD.get_user(db, user1.id)
        print(f"{user_with_posts.username}'s posts: {[post.title for post in user_with_posts.posts]}")

    finally:
        db.close()
        print("\nDatabase session closed.")


if __name__ == "__main__":
    main()