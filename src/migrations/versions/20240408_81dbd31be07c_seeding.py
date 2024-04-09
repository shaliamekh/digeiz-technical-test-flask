"""seeding

Revision ID: 81dbd31be07c
Revises: eb0b43f8ee04
Create Date: 2024-04-08 13:05:03.582821

"""

from typing import Sequence, Union

from alembic import op

from drivers.rest.config import EnvType, get_config_cls

# revision identifiers, used by Alembic.
revision: str = "81dbd31be07c"
down_revision: Union[str, None] = "eb0b43f8ee04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

config = get_config_cls()


def upgrade() -> None:
    if config().ENV in (EnvType.LOCAL, EnvType.TEST):
        op.execute(
            """
            INSERT INTO mall(id, name)
            VALUES (nextval('mall_id_seq'), 'Test Mall'),
                   (nextval('mall_id_seq'), 'Another Test Mall');
            """
        )
        op.execute(
            """
            INSERT INTO wall(id, name, mall_id)
            VALUES (nextval('wall_id_seq'), 'Test Wall', 2),
                   (nextval('wall_id_seq'), 'Another Test Wall', 2),
                   (nextval('wall_id_seq'), 'Wall for Import', 2);
            """
        )
        op.execute(
            """
            INSERT INTO footfall(id, start_datetime, end_datetime, people_in, people_out, is_active, origin, wall_id)
            VALUES (nextval('footfall_id_seq'), '2024-04-06T08:00:00.0+01:00', '2024-04-06T09:00:00.0+01:00', 200, 150, true, 'raw', 2);
            """
        )


def downgrade() -> None:
    if config().ENV in (EnvType.LOCAL, EnvType.TEST):
        op.execute("TRUNCATE public.footfall, public.wall, public.mall CASCADE")
