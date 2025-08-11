"""
NovaLang Entity Definitions
Define your entities here - they will be automatically converted to database tables!
"""

from entity_system import create_entity, startup_database, shutdown_database, entity_manager


def setup_entities():
    """Define all your entities here (like SpringBoot @Entity classes)."""
    
    print("\n📋 Setting up entities...")
    
    # ===== USER ENTITY =====
    user_entity = (create_entity('User', 'users')
                  .add_field('name', 'string', nullable=False, max_length=100)
                  .add_field('email', 'string', nullable=False, unique=True, max_length=255)
                  .add_field('password_hash', 'string', nullable=False, max_length=255)
                  .add_field('is_active', 'boolean', nullable=False, default=True)
                  .add_field('role', 'string', nullable=False, default='user', max_length=50)
                  .add_timestamps())
    
    # ===== POST ENTITY =====
    post_entity = (create_entity('Post', 'posts')
                  .add_field('title', 'string', nullable=False, max_length=200)
                  .add_field('content', 'text', nullable=False)
                  .add_field('author_id', 'int', nullable=False)
                  .add_field('published', 'boolean', nullable=False, default=False)
                  .add_field('views', 'int', nullable=False, default=0)
                  .add_field('category', 'string', nullable=True, max_length=100)
                  .add_timestamps())
    
    # ===== COMMENT ENTITY =====
    comment_entity = (create_entity('Comment', 'comments')
                     .add_field('content', 'text', nullable=False)
                     .add_field('post_id', 'int', nullable=False)
                     .add_field('author_id', 'int', nullable=False)
                     .add_field('parent_id', 'int', nullable=True)  # For nested comments
                     .add_field('is_approved', 'boolean', nullable=False, default=True)
                     .add_timestamps())
    
    # ===== CATEGORY ENTITY =====
    category_entity = (create_entity('Category', 'categories')
                      .add_field('name', 'string', nullable=False, unique=True, max_length=100)
                      .add_field('description', 'text', nullable=True)
                      .add_field('slug', 'string', nullable=False, unique=True, max_length=100)
                      .add_field('color', 'string', nullable=True, max_length=7)  # Hex color
                      .add_timestamps())
    
    # ===== TAG ENTITY =====
    tag_entity = (create_entity('Tag', 'tags')
                 .add_field('name', 'string', nullable=False, unique=True, max_length=50)
                 .add_field('slug', 'string', nullable=False, unique=True, max_length=50)
                 .add_field('usage_count', 'int', nullable=False, default=0)
                 .add_timestamps())
    
    # ===== SESSION ENTITY =====
    session_entity = (create_entity('Session', 'sessions')
                     .add_field('user_id', 'int', nullable=False)
                     .add_field('token', 'string', nullable=False, unique=True, max_length=255)
                     .add_field('ip_address', 'string', nullable=True, max_length=45)
                     .add_field('user_agent', 'text', nullable=True)
                     .add_field('expires_at', 'datetime', nullable=False)
                     .add_field('is_active', 'boolean', nullable=False, default=True)
                     .add_timestamps())
    
    print(f"✅ Defined {len(entity_manager.entities)} entities:")
    for name, entity in entity_manager.entities.items():
        field_count = len(entity.fields)
        print(f"   • {name} -> {entity.table_name} ({field_count} fields)")


def seed_sample_data():
    """Insert some sample data (like SpringBoot @PostConstruct)."""
    print("\n🌱 Seeding sample data...")
    
    try:
        # Create sample users
        user1_id = entity_manager.insert('User', {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password_hash': 'hashed_password_123',
            'role': 'admin'
        })
        
        user2_id = entity_manager.insert('User', {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'password_hash': 'hashed_password_456',
            'role': 'user'
        })
        
        # Create sample categories
        tech_cat_id = entity_manager.insert('Category', {
            'name': 'Technology',
            'description': 'Posts about technology and programming',
            'slug': 'technology',
            'color': '#3498db'
        })
        
        lifestyle_cat_id = entity_manager.insert('Category', {
            'name': 'Lifestyle',
            'description': 'Posts about lifestyle and personal experiences',
            'slug': 'lifestyle',
            'color': '#e74c3c'
        })
        
        # Create sample tags
        tag1_id = entity_manager.insert('Tag', {
            'name': 'Programming',
            'slug': 'programming',
            'usage_count': 5
        })
        
        tag2_id = entity_manager.insert('Tag', {
            'name': 'NovaLang',
            'slug': 'novalang',
            'usage_count': 10
        })
        
        # Create sample posts
        post1_id = entity_manager.insert('Post', {
            'title': 'Getting Started with NovaLang',
            'content': 'NovaLang is an amazing programming language that makes backend development simple and fun!',
            'author_id': user1_id,
            'published': True,
            'views': 150,
            'category': 'Technology'
        })
        
        post2_id = entity_manager.insert('Post', {
            'title': 'My Journey in Programming',
            'content': 'This is my personal story about how I started programming and fell in love with code.',
            'author_id': user2_id,
            'published': True,
            'views': 89,
            'category': 'Lifestyle'
        })
        
        # Create sample comments
        entity_manager.insert('Comment', {
            'content': 'Great article! Very helpful for beginners.',
            'post_id': post1_id,
            'author_id': user2_id
        })
        
        entity_manager.insert('Comment', {
            'content': 'Thanks for sharing your experience!',
            'post_id': post2_id,
            'author_id': user1_id
        })
        
        print("✅ Sample data inserted successfully!")
        
        # Show what was created
        users = entity_manager.find_all('User')
        posts = entity_manager.find_all('Post')
        comments = entity_manager.find_all('Comment')
        categories = entity_manager.find_all('Category')
        tags = entity_manager.find_all('Tag')
        
        print(f"   • Users: {len(users)}")
        print(f"   • Posts: {len(posts)}")
        print(f"   • Comments: {len(comments)}")
        print(f"   • Categories: {len(categories)}")
        print(f"   • Tags: {len(tags)}")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")


def list_all_data():
    """Display all data from all entities."""
    print("\n📊 Current Database Contents:")
    print("=" * 50)
    
    for entity_name in entity_manager.entities.keys():
        records = entity_manager.find_all(entity_name)
        entity = entity_manager.entities[entity_name]
        
        print(f"\n📋 {entity_name} (table: {entity.table_name})")
        print("-" * 30)
        
        if not records:
            print("   (no records)")
        else:
            for i, record in enumerate(records, 1):
                print(f"   {i}. ID: {record.get('id', 'N/A')}")
                for key, value in record.items():
                    if key != 'id':
                        # Truncate long values
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:50] + "..."
                        print(f"      {key}: {value}")
                print()


if __name__ == "__main__":
    # This runs when you execute: python entities.py
    setup_entities()
    
    if startup_database():
        seed_sample_data()
        list_all_data()
        shutdown_database()
    else:
        print("❌ Failed to start database")
