"""empty message

Revision ID: b453e4284863
Revises: 875ed4281cd0
Create Date: 2020-05-01 17:54:16.528133

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b453e4284863'
down_revision = '875ed4281cd0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show', sa.Column('artist_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'show', 'artist', ['artist_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'show', type_='foreignkey')
    op.drop_column('show', 'artist_id')
    # ### end Alembic commands ###