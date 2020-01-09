"""empty message

Revision ID: 9306c96f148f
Revises: c16424940f9c
Create Date: 2020-01-09 16:45:44.637911

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9306c96f148f'
down_revision = 'c16424940f9c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'seeking_venue')
    # ### end Alembic commands ###
