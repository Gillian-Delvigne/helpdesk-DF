"""ticket status as enum

Revision ID: 794318362016
Revises: 0c0805d7894d
Create Date: 2026-08-27 19:54:30.709864

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '794318362016'
down_revision = '0c0805d7894d'
branch_labels = None
depends_on = None

STATUS_VALUES = ['NEW', 'IN_PROGRESS', 'BLOCKED', 'RESOLVED', 'CLOSED']
ENUM_NAME = 'ticketstatusenum'


def _enum(create_type: bool) -> postgresql.ENUM:
    return postgresql.ENUM(*STATUS_VALUES, name=ENUM_NAME, create_type=create_type)


def upgrade():
    # Le type est créé une seule fois, explicitement : le laisser se créer
    # implicitement à chaque alter_column provoquerait un "type already exists"
    # dès la 2e colonne convertie (3 colonnes partagent ce même type ici).
    _enum(create_type=True).create(op.get_bind(), checkfirst=True)

    with op.batch_alter_table('tickets', schema=None) as batch_op:
        batch_op.alter_column(
            'status',
            existing_type=sa.VARCHAR(length=255),
            type_=_enum(create_type=False),
            postgresql_using='status::ticketstatusenum',
            existing_nullable=False,
        )

    with op.batch_alter_table('ticketstatushistories', schema=None) as batch_op:
        batch_op.alter_column(
            'oldstatus',
            existing_type=sa.VARCHAR(length=50),
            type_=_enum(create_type=False),
            postgresql_using='oldstatus::ticketstatusenum',
            existing_nullable=False,
        )
        batch_op.alter_column(
            'newstatus',
            existing_type=sa.VARCHAR(length=50),
            type_=_enum(create_type=False),
            postgresql_using='newstatus::ticketstatusenum',
            existing_nullable=False,
        )

    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table('ticketstatushistories', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('ticketid', new_column_name='ticketid ')
        batch_op.create_foreign_key(
            batch_op.f('ticketstatushistories_ticketid _fkey'),
            'tickets', ['ticketid '], ['ticketid'],
        )
        batch_op.alter_column(
            'newstatus',
            existing_type=_enum(create_type=False),
            type_=sa.VARCHAR(length=50),
            existing_nullable=False,
        )
        batch_op.alter_column(
            'oldstatus',
            existing_type=_enum(create_type=False),
            type_=sa.VARCHAR(length=50),
            existing_nullable=False,
        )

    with op.batch_alter_table('tickets', schema=None) as batch_op:
        batch_op.alter_column(
            'status',
            existing_type=_enum(create_type=False),
            type_=sa.VARCHAR(length=255),
            existing_nullable=False,
        )

    _enum(create_type=False).drop(op.get_bind(), checkfirst=True)

    # ### end Alembic commands ###
