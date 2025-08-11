import random
import string
import sys

from logger_local.MetaLogger import MetaLogger


from .Connector import get_connection
from .constants import OBJECT_TO_INSERT_CODE


# after 100 times of trying to generate a random number that does not already exist in the database, raise an exception
MAX_NUMBER_OF_TRIES = 100
DEFAULT_LENGTH = 20


# TODO Shall move NumberGenerator and IdentityGenerator to database-mysql (new name database-sql) ?

class NumberGenerator(metaclass=MetaLogger, object=OBJECT_TO_INSERT_CODE):
    @staticmethod
    # TODO: Add new parameters to define new logic region: Region, entity_type: EntityType
    def get_random_number(schema_name: str, view_name: str, number_column_name: str = "number") -> int:
        connector = get_connection()
        cursor = connector.cursor()

        random_number = None

        # Try 100 times to get a random number that does not already exist in the database
        for _ in range(MAX_NUMBER_OF_TRIES):
            random_number = random.randint(1, sys.maxsize)

            query_get = (f"SELECT `{number_column_name}` FROM `{schema_name}`.`{view_name}` "
                         f"WHERE `{number_column_name}` = %s LIMIT 1")
            cursor.execute(query_get, (random_number,))

            # row =
            cursor.fetchone()

        if random_number is None:  # Failed 100 times.
            error_message = f"Could not generate a random {number_column_name} that does not already exist in the database"
            raise Exception(error_message)
        return random_number

    @staticmethod
    def generate_random_string(length: int) -> str:
        letters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(letters) for _ in range(length))
        return random_string

    # TODO: reuse get_random_number with generator function as parameter
    @staticmethod
    def get_random_identifier(schema_name: str, view_name: str, identifier_column_name: str,
                              length: int = DEFAULT_LENGTH) -> str:
        connector = get_connection()
        cursor = connector.cursor()

        random_identifier = None

        for _ in range(MAX_NUMBER_OF_TRIES):
            random_identifier = NumberGenerator.generate_random_string(length=length)

            query_get = (f"SELECT `{identifier_column_name}` FROM `{schema_name}`.`{view_name}` "
                         f"WHERE `{identifier_column_name}` = %s LIMIT 1")
            cursor.execute(query_get, (random_identifier,))
            # row =
            cursor.fetchone()

        if random_identifier is None:
            error_message = "Could not generate a random identifier that does not already exist in the database"
            raise Exception(error_message)

        return random_identifier
