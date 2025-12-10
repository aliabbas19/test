"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('profile_image', sa.String(), server_default='default.png'),
        sa.Column('class_name', sa.String(), nullable=True),
        sa.Column('section_name', sa.String(), nullable=True),
        sa.Column('session_revocation_token', sa.Integer(), server_default='0'),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('phone_number', sa.String(), nullable=True),
        sa.Column('father_education', sa.String(), nullable=True),
        sa.Column('mother_education', sa.String(), nullable=True),
        sa.Column('is_profile_complete', sa.Boolean(), server_default='false'),
        sa.Column('is_muted', sa.Boolean(), server_default='false'),
        sa.Column('profile_reset_required', sa.Boolean(), server_default='false'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('idx_user_class_section', 'users', ['class_name', 'section_name'], unique=False)

    # Videos table
    op.create_table(
        'videos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('filepath', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('video_type', sa.String(), nullable=False),
        sa.Column('is_approved', sa.Boolean(), server_default='false'),
        sa.Column('is_archived', sa.Boolean(), server_default='false'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_videos_id', 'videos', ['id'], unique=False)
    op.create_index('ix_videos_user_id', 'videos', ['user_id'], unique=False)
    op.create_index('ix_videos_is_approved', 'videos', ['is_approved'], unique=False)
    op.create_index('ix_videos_is_archived', 'videos', ['is_archived'], unique=False)
    op.create_index('idx_video_user_approved_archived', 'videos', ['user_id', 'is_approved', 'is_archived'], unique=False)

    # Video likes table
    op.create_table(
        'video_likes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('video_id', 'user_id', name='uq_video_like')
    )
    op.create_index('idx_video_like_unique', 'video_likes', ['video_id', 'user_id'], unique=True)

    # Comments table
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('is_pinned', sa.Boolean(), server_default='false'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['comments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_comments_id', 'comments', ['id'], unique=False)

    # Rating criteria table
    op.create_table(
        'rating_criteria',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('video_type', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index('ix_rating_criteria_id', 'rating_criteria', ['id'], unique=False)

    # Dynamic video ratings table
    op.create_table(
        'dynamic_video_ratings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('criterion_id', sa.Integer(), nullable=False),
        sa.Column('is_awarded', sa.Boolean(), server_default='false'),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['criterion_id'], ['rating_criteria.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('video_id', 'criterion_id', name='uq_video_criterion')
    )
    op.create_index('ix_dynamic_video_ratings_id', 'dynamic_video_ratings', ['id'], unique=False)

    # Messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('receiver_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('is_read', sa.Boolean(), server_default='false'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['receiver_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_messages_id', 'messages', ['id'], unique=False)
    op.create_index('ix_messages_sender_id', 'messages', ['sender_id'], unique=False)
    op.create_index('ix_messages_receiver_id', 'messages', ['receiver_id'], unique=False)
    op.create_index('idx_message_receiver_read', 'messages', ['receiver_id', 'is_read'], unique=False)

    # Posts table
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_posts_id', 'posts', ['id'], unique=False)

    # Suspensions table
    op.create_table(
        'suspensions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reason', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_suspensions_id', 'suspensions', ['id'], unique=False)

    # Star bank table
    op.create_table(
        'star_bank',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('banked_stars', sa.Integer(), server_default='0', nullable=False),
        sa.Column('last_updated_week_start_date', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )

    # Telegram settings table
    op.create_table(
        'telegram_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bot_token', sa.String(), nullable=True),
        sa.Column('chat_id', sa.String(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_telegram_settings_id', 'telegram_settings', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('telegram_settings')
    op.drop_table('star_bank')
    op.drop_table('suspensions')
    op.drop_table('posts')
    op.drop_table('messages')
    op.drop_table('dynamic_video_ratings')
    op.drop_table('rating_criteria')
    op.drop_table('comments')
    op.drop_table('video_likes')
    op.drop_table('videos')
    op.drop_table('users')

