"""First init

Revision ID: cd0cec22e308
Revises: 
Create Date: 2024-02-07 02:48:27.739602

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd0cec22e308'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('anime',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('image_link', sa.String(), nullable=False),
    sa.Column('desc', sa.String(), nullable=False),
    sa.Column('director', sa.String(), nullable=False),
    sa.Column('studio', sa.String(), nullable=False),
    sa.Column('release_year', sa.Integer(), nullable=False),
    sa.Column('characters', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_review',
    sa.Column('anime_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('review', sa.String(), nullable=False),
    sa.Column('stars', sa.Integer(), nullable=False),
    sa.CheckConstraint('stars >= 1 AND stars <= 10', name='check_stars_range'),
    sa.ForeignKeyConstraint(['anime_id'], ['anime.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('anime_id', 'user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_review')
    op.drop_table('user')
    op.drop_table('anime')
    # ### end Alembic commands ###
