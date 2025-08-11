# This file is being used by database-infrastructure. database-infrastructure can't import files from tests directory
# TODO Can we move this to tests directory?
# from ..src.point import Point
from .point import Point

# TODO Should be defined one time in the repo in the tests directory/folder
TEST_SCHEMA_NAME = "test"

# TODO test_mysql_table has point/coordinate and our REDIS class do not support point yet
# TEST_TABLE_NAME = "test_mysql_table"
# TEST_VIEW_NAME = "test_mysql_view"
# TEST_ID_COLUMN_NAME = "test_mysql_id"

TEST_TABLE_NAME = "test_gender_table"
TEST_VIEW_NAME = "test_gender_view"
TEST_ID_COLUMN_NAME = "test_gender_id"

TEST_ENTITY_TYPE_ID = 22  # TODO: use entity-local
TEST_POINT = Point(
    0, 0
)  # TODO Change the default point to something real taken from location-local
