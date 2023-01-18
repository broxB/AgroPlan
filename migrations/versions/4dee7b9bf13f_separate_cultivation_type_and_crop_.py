"""separate cultivation and crop class, add field_type and split yield in crop, rename enums to be more specific

Revision ID: 4dee7b9bf13f
Revises: 36ffc0998323
Create Date: 2023-01-12 13:48:13.244427

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4dee7b9bf13f"
down_revision = "36ffc0998323"
branch_labels = None
depends_on = None


"""
"flask seed new" is encouraged because these are deep database changes
"""


def upgrade():
    # change column name "set_year" to "year"
    with op.batch_alter_table("user") as batch_op:
        batch_op.alter_column("set_year", new_column_name="year")

    # change var_yield MutableList to single float columns and add field_type
    with op.batch_alter_table("crop", recreate="always") as batch_op:
        batch_op.add_column(
            sa.Column(
                "field_type",
                sa.Enum(
                    "grassland",
                    "cropland",
                    "exchanged_land",
                    "fallow_grassland",
                    "fallow_cropland",
                    name="fieldtype",
                ),
                nullable=True,
            )
        )

        batch_op.drop_column("nmin_depth")
        batch_op.add_column(
            sa.Column(
                "nmin_depth",
                sa.Enum(
                    "nmin_0",
                    "nmin_30",
                    "nmin_60",
                    "nmin_90",
                    name="nmintype",
                ),
                nullable=True,
            )
        )

        batch_op.add_column(sa.Column("pos_yield", sa.Float(asdecimal=True), nullable=True))
        batch_op.add_column(sa.Column("neg_yield", sa.Float(asdecimal=True), nullable=True))
        batch_op.drop_column("var_yield")

    # change crop_class to cultivation_type and adapt table unique constraint with it, turn nmin MutableList into single columns
    with op.batch_alter_table("cultivation") as batch_op:
        batch_op.alter_column("crop_class", new_column_name="cultivation_type")
        batch_op.drop_constraint("uq_cultivation_field_id", type_="unique")

        batch_op.add_column(sa.Column("nmin_30", sa.Integer, nullable=True))
        batch_op.add_column(sa.Column("nmin_60", sa.Integer, nullable=True))
        batch_op.add_column(sa.Column("nmin_90", sa.Integer, nullable=True))
        batch_op.drop_column("nmin")

    with op.batch_alter_table("cultivation", recreate="always") as batch_op:
        batch_op.create_unique_constraint(
            batch_op.f("uq_cultivation_field_id"), columns=["field_id", "cultivation_type"]
        )
    # change CropClass to CultivationType names
    op.execute(
        "UPDATE cultivation SET cultivation_type = REPLACE(cultivation_type, 'second_crop', 'main_second_crop')"
    )
    # update CropType names
    op.execute("UPDATE crop SET type = REPLACE(type, 'non_legume', 'catch_non_legume')")
    # update ResidueType names
    op.execute("UPDATE cultivation SET residues = REPLACE(residues, 'stayed', 'main_stayed')")
    op.execute("UPDATE cultivation SET residues = REPLACE(residues, 'removed', 'main_removed')")
    op.execute(
        "UPDATE cultivation SET residues = REPLACE(residues, 'no_residues', 'main_no_residues')"
    )
    op.execute(
        "UPDATE cultivation SET residues = REPLACE(residues, 'frozen', 'catch_frozen') WHERE residues LIKE 'frozen'"
    )
    op.execute(
        "UPDATE cultivation SET residues = REPLACE(residues, 'not_frozen_fall', 'catch_not_frozen_fall')"
    )
    op.execute(
        "UPDATE cultivation SET residues = REPLACE(residues, 'not_frozen_spring', 'catch_not_frozen_spring')"
    )
    op.execute(
        "UPDATE cultivation SET residues = REPLACE(residues, 'catch_crop_used', 'catch_used')"
    )
    # update LegumeType names
    for num in range(0, 110, 10):
        op.execute(
            f"UPDATE cultivation SET legume_rate = REPLACE(legume_rate, 'crop_{num}', 'main_crop_{num}')"
        )
    # update FertType names
    op.execute("UPDATE fertilizer SET type = REPLACE(type, 'digestate', 'org_digestate')")
    op.execute("UPDATE fertilizer SET type = REPLACE(type, 'slurry', 'org_slurry')")
    op.execute("UPDATE fertilizer SET type = REPLACE(type, 'manure', 'org_manure')")
    op.execute("UPDATE fertilizer SET type = REPLACE(type, 'dry_manure', 'org_dry_manure')")
    op.execute("UPDATE fertilizer SET type = REPLACE(type, 'compost', 'org_compost')")

    # update MeasureType names
    op.execute("UPDATE fertilization SET measure = REPLACE(measure, 'fall', 'org_fall')")
    op.execute("UPDATE fertilization SET measure = REPLACE(measure, 'spring', 'org_spring')")


def downgrade():
    with op.batch_alter_table("user") as batch_op:
        batch_op.alter_column("year", new_column_name="set_year")

    with op.batch_alter_table("crop", recreate="always") as batch_op:
        batch_op.drop_column("field_type")

        batch_op.add_column(sa.Column("var_yield", sa.PickleType, nullable=True))
        batch_op.drop_column("pos_yield")
        batch_op.drop_column("neg_yield")

        batch_op.drop_column("nmin_depth")
        batch_op.add_column(sa.Column("nmin_depth", sa.Integer, nullable=True))

    # change cultivation_type to crop_class and adapt table unique constraint with it
    with op.batch_alter_table("cultivation", schema=None) as batch_op:
        batch_op.alter_column("cultivation_type", new_column_name="crop_class")
        batch_op.drop_constraint("uq_cultivation_field_id", type_="unique")

        batch_op.add_column(sa.Column("nmin", sa.PickleType, nullable=True))
        batch_op.drop_column("nmin_30")
        batch_op.drop_column("nmin_60")
        batch_op.drop_column("nmin_90")

    with op.batch_alter_table("cultivation", recreate="always") as batch_op:
        batch_op.create_unique_constraint(
            batch_op.f("uq_cultivation_field_id"), columns=["field_id", "crop_class"]
        )
    # change CropClass to CultivationType names
    op.execute(
        "UPDATE cultivation SET crop_class = REPLACE(crop_class, 'main_second_crop', 'second_crop')"
    )
    # update CropType names
    op.execute("UPDATE crop SET type = REPLACE(type, 'catch_non_legume', 'non_legume')")
    # update ResidueType names
    op.execute("UPDATE cultivation SET residues = REPLACE(residues, 'main_stayed', 'stayed')")
    op.execute("UPDATE cultivation SET residues = REPLACE(residues, 'main_removed', 'removed')")
    op.execute(
        "UPDATE cultivation SET residues = REPLACE(residues, 'main_no_residues', 'no_residues')"
    )
    op.execute("UPDATE cultivation SET residues = REPLACE(residues, 'catch_frozen', 'frozen')")
    op.execute(
        "UPDATE cultivation SET residues = REPLACE(residues, 'catch_not_frozen_fall', 'not_frozen_fall')"
    )
    op.execute(
        "UPDATE cultivation SET residues = REPLACE(residues, 'catch_not_frozen_spring', 'not_frozen_spring')"
    )
    op.execute(
        "UPDATE cultivation SET residues = REPLACE(residues, 'catch_used', 'catch_crop_used')"
    )
    # update LegumeType names
    for num in range(0, 110, 10):
        op.execute(
            f"UPDATE cultivation SET legume_rate = REPLACE(legume_rate, 'main_crop_{num}', 'crop_{num}')"
        )
    # update FertType names
    op.execute("UPDATE fertilizer SET class = REPLACE(class, 'org_digestate', 'digestate')")
    op.execute("UPDATE fertilizer SET class = REPLACE(class, 'org_slurry', 'slurry')")
    op.execute("UPDATE fertilizer SET class = REPLACE(class, 'org_manure', 'manure')")
    op.execute("UPDATE fertilizer SET class = REPLACE(class, 'org_dry_manure', 'dry_manure')")
    op.execute("UPDATE fertilizer SET class = REPLACE(class, 'org_compost', 'compost')")

    # update MeasureType names
    op.execute("UPDATE fertilization SET measure = REPLACE(measure, 'org_fall', 'fall')")
    op.execute("UPDATE fertilization SET measure = REPLACE(measure, 'org_spring', 'spring')")
