# TODO Rename this file according to our standards in python-package-template so it will have unique filename  # noqa E501
from logger_local.LoggerComponentEnum import LoggerComponentEnum

# TODO Remove the word CIRCLES and use the naming convention of the python-package-template  # noqa E501
CIRCLES_NUMBER_GENERATOR_COMPONENT_ID = 177
CIRCLES_NUMBER_GENERATOR_COMPONENT_NAME = "circles_number_generator"

OBJECT_TO_INSERT_CODE = {
    'component_id': CIRCLES_NUMBER_GENERATOR_COMPONENT_ID,
    'component_name': CIRCLES_NUMBER_GENERATOR_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'tal.g@circ.zone'
}

OBJECT_TO_INSERT_TEST = {
    'component_id': CIRCLES_NUMBER_GENERATOR_COMPONENT_ID,
    'component_name': CIRCLES_NUMBER_GENERATOR_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'tal.g@circ.zone'
}

DEFAULT_SQL_SELECT_LIMIT = 100
