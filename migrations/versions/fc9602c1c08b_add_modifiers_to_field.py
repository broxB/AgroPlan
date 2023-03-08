"""add modifiers to field

Revision ID: fc9602c1c08b
Revises: 5cba76e733fe
Create Date: 2023-02-24 22:06:34.509044

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc9602c1c08b'
down_revision = '5cba76e733fe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('modifier',
    sa.Column('modifier_id', sa.Integer(), nullable=False),
    sa.Column('field_id', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('modification', sa.Enum('n', 'p2o5', 'k2o', 'mgo', 'sulphur', 'cao', 'nh4', name='nutrienttype'), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['field_id'], ['field.field_id'], name=op.f('fk_modifier_field_id_field')),
    sa.PrimaryKeyConstraint('modifier_id', name=op.f('pk_modifier'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('modifier')
    # ### end Alembic commands ###