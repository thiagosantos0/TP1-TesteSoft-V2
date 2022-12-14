"""empty message

Revision ID: 31b3ff6d90ac
Revises: 293bea2f2739
Create Date: 2022-11-05 21:19:02.591797

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '31b3ff6d90ac'
down_revision = '293bea2f2739'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('aluno_prova', 'data_entrega',
               existing_type=mysql.DATETIME(),
               type_=sa.Date(),
               existing_nullable=True,
               existing_server_default=sa.text('current_timestamp()'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('aluno_prova', 'data_entrega',
               existing_type=sa.Date(),
               type_=mysql.DATETIME(),
               existing_nullable=True,
               existing_server_default=sa.text('current_timestamp()'))
    # ### end Alembic commands ###
