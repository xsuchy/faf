# Copyright (C) 2014  ABRT Team
# Copyright (C) 2014  Red Hat, Inc.
#
# This file is part of faf.
#
# faf is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# faf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with faf.  If not, see <http://www.gnu.org/licenses/>.


"""add_semver_to_build

Revision ID: 27d8ea04cd10
Revises: 82081a3c76b
Create Date: 2014-12-11 20:26:38.313396

"""

# revision identifiers, used by Alembic.
revision = '27d8ea04cd10'
down_revision = '82081a3c76b'

from alembic import op
import sqlalchemy as sa

from pyfaf.storage import custom_types

metadata = sa.MetaData()


def upgrade():
    op.add_column('builds', sa.Column('semver', custom_types.Semver(), nullable=True))

    build = sa.Table("builds", metadata,
                     sa.Column("id", sa.Integer),
                     sa.Column("base_package_name", sa.String(length=64)),
                     sa.Column("projrelease_id", sa.Integer),
                     sa.Column("epoch", sa.Integer),
                     sa.Column("version", sa.String(length=64)),
                     sa.Column("release", sa.String(length=64)),
                     sa.Column("semver", custom_types.Semver()),
                     )

    for b in op.get_bind().execute(sa.select([build.c.id, build.c.version])):
        bid, bver = b
        bver = custom_types.to_semver(bver)
        op.get_bind().execute((build.update()
                               .where(build.c.id == bid)
                               .values(semver=sa.func.to_semver(bver))))

    op.alter_column('builds', sa.Column('semver', custom_types.Semver(), nullable=False))


def downgrade():
    op.drop_column('builds', 'semver')
