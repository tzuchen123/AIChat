"""create initial tables

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-03-03 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("idx_email", "users", ["email"])
    op.create_index("idx_username", "users", ["username"])

    # --- conversations ---
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_conversations_user_id",
            ondelete="CASCADE",
        ),
    )
    op.create_index("idx_user_id", "conversations", ["user_id"])

    # --- messages ---
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("user", "assistant", name="role_enum"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            name="fk_messages_conversation_id",
            ondelete="CASCADE",
        ),
    )
    op.create_index("idx_conversation_id", "messages", ["conversation_id"])
    op.create_index(
        "idx_conv_created", "messages", ["conversation_id", "created_at"]
    )


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_index("idx_conv_created", table_name="messages")
    op.drop_index("idx_conversation_id", table_name="messages")
    op.drop_table("messages")
    # Drop ENUM type (no-op on MySQL; required on PostgreSQL)
    sa.Enum(name="role_enum").drop(op.get_bind(), checkfirst=True)

    op.drop_index("idx_user_id", table_name="conversations")
    op.drop_table("conversations")

    op.drop_index("idx_username", table_name="users")
    op.drop_index("idx_email", table_name="users")
    op.drop_table("users")
