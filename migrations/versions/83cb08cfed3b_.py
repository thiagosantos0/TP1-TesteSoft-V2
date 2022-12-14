"""empty message

Revision ID: 83cb08cfed3b
Revises: 293bea2f2739
Create Date: 2022-11-05 21:00:25.949684

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83cb08cfed3b'
down_revision = '293bea2f2739'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('aluno_prova', sa.Column('data_entrega', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('prova', sa.Column('tempo', sa.Date(), nullable=False))
    op.add_column('prova', sa.Column('temporizada', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('prova', 'temporizada')
    op.drop_column('prova', 'tempo')
    op.drop_column('aluno_prova', 'data_entrega')
    # ### end Alembic commands ###
