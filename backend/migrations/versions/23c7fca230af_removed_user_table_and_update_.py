"""removed user table and update subscription table accordingly

Revision ID: 23c7fca230af
Revises: 8b2e3c0b1a8a
Create Date: 2025-11-15 21:24:53.980508

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "23c7fca230af"
down_revision = "8b2e3c0b1a8a"
branch_labels = None
depends_on = None


def upgrade():
    # Add new user fields to subscriptions as nullable, copy data from users,
    # then make user_email NOT NULL and remove users table.
    with op.batch_alter_table("subscriptions", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("user_email", sa.String(length=120), nullable=True)
        )
        batch_op.add_column(
            sa.Column("user_tg_id", sa.String(length=120), nullable=True)
        )
        batch_op.add_column(
            sa.Column("user_tg_username", sa.String(length=120), nullable=True)
        )

    # Populate the new columns from the users table
    op.execute(
        """
        UPDATE subscriptions
        SET user_email = users.email,
            user_tg_id = users.telegram_user_id,
            user_tg_username = users.telegram_username
        FROM users
        WHERE subscriptions.user_id = users.id
        """
    )

    # Make user_email non-nullable now that data has been copied
    op.alter_column(
        "subscriptions",
        "user_email",
        existing_type=sa.String(length=120),
        nullable=False,
    )

    # Remove the old foreign key and user_id column, then drop users table
    with op.batch_alter_table("subscriptions", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("subscriptions_user_id_fkey"), type_="foreignkey"
        )
        batch_op.drop_column("user_id")

    op.drop_table("users")

    # ### end Alembic commands ###


def downgrade():
    # Recreate users table, insert distinct users from subscriptions,
    # repopulate subscriptions.user_id, then remove user_* columns.
    op.create_table(
        "users",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("email", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column(
            "telegram_user_id",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "telegram_username",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "updated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("users_pkey")),
        sa.UniqueConstraint(
            "email",
            name=op.f("users_email_key"),
            postgresql_include=[],
            postgresql_nulls_not_distinct=False,
        ),
        sa.UniqueConstraint(
            "telegram_user_id",
            name=op.f("users_telegram_user_id_key"),
            postgresql_include=[],
            postgresql_nulls_not_distinct=False,
        ),
    )

    # Insert distinct users from subscriptions (avoid NULL emails)
    op.execute(
        """
        INSERT INTO users (email, telegram_user_id, telegram_username, created_at, updated_at)
        SELECT DISTINCT user_email, user_tg_id, user_tg_username, now(), now()
        FROM subscriptions
        WHERE user_email IS NOT NULL
        """
    )

    # Add user_id column (nullable), populate it by joining on email, then add FK and make NOT NULL
    with op.batch_alter_table("subscriptions", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=True)
        )

    op.execute(
        """
        UPDATE subscriptions
        SET user_id = users.id
        FROM users
        WHERE subscriptions.user_email = users.email
        """
    )

    with op.batch_alter_table("subscriptions", schema=None) as batch_op:
        batch_op.create_foreign_key(
            batch_op.f("subscriptions_user_id_fkey"), "users", ["user_id"], ["id"]
        )
        batch_op.alter_column("user_id", existing_type=sa.INTEGER(), nullable=False)
        batch_op.drop_column("user_tg_username")
        batch_op.drop_column("user_tg_id")
        batch_op.drop_column("user_email")

    # ### end Alembic commands ###
