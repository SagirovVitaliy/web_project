"""added the remaining tables

Revision ID: 8092d3e20977
Revises: 4eb8bd3f89a5
Create Date: 2020-09-29 01:34:01.873155

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8092d3e20977'
down_revision = '4eb8bd3f89a5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('email',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email_value', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email_value')
    )
    op.create_table('phone',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone_value', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone_value')
    )
    op.create_table('task_status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_value', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('role_value', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tag', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['tag'], ['user.tag'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('task', sa.Column('finish_role', sa.String(), nullable=True))
    op.add_column('task', sa.Column('finish_tag', sa.String(), nullable=True))
    op.add_column('task', sa.Column('status', sa.String(), nullable=True))
    op.create_foreign_key(None, 'task', 'task_status', ['status'], ['task_value'], ondelete='CASCADE')
    op.create_foreign_key(None, 'task', 'tag', ['finish_tag'], ['tag'], ondelete='CASCADE')
    op.create_foreign_key(None, 'task', 'user', ['finish_role'], ['role'], ondelete='CASCADE')
    op.create_foreign_key(None, 'user', 'user_role', ['role'], ['role_value'], ondelete='CASCADE')
    op.create_foreign_key(None, 'user', 'email', ['email'], ['email_value'], ondelete='CASCADE')
    op.create_foreign_key(None, 'user', 'phone', ['phone'], ['phone_value'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.drop_column('task', 'status')
    op.drop_column('task', 'finish_tag')
    op.drop_column('task', 'finish_role')
    op.drop_table('tag')
    op.drop_table('user_role')
    op.drop_table('task_status')
    op.drop_table('phone')
    op.drop_table('email')
    # ### end Alembic commands ###