"""se agrego una columna de idiomas a la tabla post

Revision ID: 6dc1b3956870
Revises: 24a21464975f
Create Date: 2024-01-13 17:48:37.266604

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6dc1b3956870'
down_revision = '24a21464975f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('Idioma', sa.String(length=5), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('Idioma')

    # ### end Alembic commands ###