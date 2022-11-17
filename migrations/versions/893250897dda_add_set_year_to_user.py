"""add set_year to user

Revision ID: 893250897dda
Revises: af874f00b129
Create Date: 2022-11-17 15:08:29.208165

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '893250897dda'
down_revision = 'af874f00b129'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('set_year', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('set_year')

    # ### end Alembic commands ###