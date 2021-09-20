"""Production migration

Revision ID: a7a9b739b11b
Revises: 
Create Date: 2021-09-09 00:44:00.078782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7a9b739b11b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Election',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start', sa.String(length=24), nullable=False),
    sa.Column('end', sa.String(length=24), nullable=False),
    sa.Column('individual', sa.Boolean(), nullable=False),
    sa.Column('votesNum', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Participant',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('individual', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ElectionParticipation',
    sa.Column('idParticipant', sa.Integer(), nullable=False),
    sa.Column('idElection', sa.Integer(), nullable=False),
    sa.Column('ord_number', sa.Integer(), nullable=False),
    sa.Column('result', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['idElection'], ['Election.id'], ),
    sa.ForeignKeyConstraint(['idParticipant'], ['Participant.id'], ),
    sa.PrimaryKeyConstraint('idParticipant', 'idElection')
    )
    op.create_table('Vote',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pollNumber', sa.Integer(), nullable=False),
    sa.Column('guid', sa.String(length=36), nullable=False),
    sa.Column('jmbg', sa.String(length=13), nullable=False),
    sa.Column('myElectionId', sa.Integer(), nullable=False),
    sa.Column('valid', sa.Boolean(), nullable=False),
    sa.Column('reason', sa.String(length=256), nullable=True),
    sa.ForeignKeyConstraint(['myElectionId'], ['Election.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Vote')
    op.drop_table('ElectionParticipation')
    op.drop_table('Participant')
    op.drop_table('Election')
    # ### end Alembic commands ###