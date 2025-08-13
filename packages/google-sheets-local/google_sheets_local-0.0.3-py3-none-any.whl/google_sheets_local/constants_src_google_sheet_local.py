# TODO Please rename the filename from entity_constants.py to your entity. If your entity is country please change the file name to country_constants.py
from logger_local.LoggerComponentEnum import LoggerComponentEnum

GOOGLE_SHEETS_MESSAGE_INFORU_API_TYPE_ID = 8

GOOGLE_SHEETS_CODE_COMPONENT_ID = 298
GOOGLE_SHEETS_CODE_COMPONENT_NAME = "GOOGLE_SHEETS local Python package"
GOOGLE_SHEETS_CODE_DEVELOPER_EMAIL = "tal.g@circ.zone"
GOOGLE_SHEETS_COMPONENT_NAME = 'google-sheets-local'
WHATSAPP_DEVELOPER_EMAIL = 'zvi.n@circ.zone'


# Please change everywhere there is "GoogleSheets" to your entity name i.e. "Country"  (Please pay attention the C is in uppercase)
class ConstantsSrcGOOGLE_SHEETS:
    """This is a class of all the constants of GoogleSheets"""

    # TODO Please update your email
    DEVELOPER_EMAIL_ADDRESS = 'zvi.n@circ.zone'
    GOOGLE_SYSTEM_ID = 6

    # TODO Please change everywhere in the code "GOOGLE_SHEETS" to "COUNTRY_LOCAL_PYTHON" in case your entity is Country.
    # TODO Please send a message in the Slack to #request-to-open-component-id and get your COMPONENT_ID
    # For example COUNTRY_COMPONENT_ID = 34324
    # TODO search for the CODE_COMPONENT_ID and TEST_COMPONENT_ID in component.component_table (if needed INSERT new record)    
    GOOGLE_SHEETS_CODE_COMPONENT_ID = -32523
    GOOGLE_SHEETS_TEST_COMPONENT_ID = -322523
    # TODO Please write your own COMPONENT_NAME
    GOOGLE_SHEETS_CODE_COMPONENT_NAME = 'GoogleSheets local Python package'
    GOOGLE_SHEETS_CODE_LOGGER_OBJECT = {
        'component_id': GOOGLE_SHEETS_CODE_COMPONENT_ID,
        'component_name': GOOGLE_SHEETS_COMPONENT_NAME,
        'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
        'developer_email': DEVELOPER_EMAIL_ADDRESS
    }
    # GOOGLE_SHEETS_LOCAL_PYTHON_TEST_LOGGER_OBJECT = {
    #     'componentId': GOOGLE_SHEETS_TEST_COMPONENT_ID,
    #     'componentName': GOOGLE_SHEETS_COMPONENT_NAME,
    #     'componentCategory': LoggerComponentEnum.ComponentCategory.Unit_Test.value,
    #     'testingFramework': LoggerComponentEnum.testingFramework.pytest.value,  # TODO Please add the framework you use
    #     'developerEmailAddress': DEVELOPER_EMAIL_ADDRESS
    # }

    UNKNOWN_GOOGLE_SHEET_ID = 0


    # TODO Please update if you need default values i.e. for testing
    # DEFAULT_XXX_NAME = None
    # DEFAULT_XXX_NAME = None

    GOOGLE_SHEET_SCHEMA_NAME = '<entity>_schema'
    GOOGLE_SHEET_TABLE_NAME = '<entity>_table'
    GOOGLE_SHEET_VIEW_NAME = '<entity>_view'
    GOOGLE_SHEET_ML_TABLE_NAME = '<entity>_ml_table'  # TODO In case you don't use ML table, delete this
    GOOGLE_SHEET_ML_VIEW_NAME = '<entity>_ml_view'
    GOOGLE_SHEET_COLUMN_NAME = '<entity>_id'


def get_logger_object(category: str = LoggerComponentEnum.ComponentCategory.Code):
    if category == LoggerComponentEnum.ComponentCategory.Code:
        return {
            'component_id': GOOGLE_SHEETS_CODE_COMPONENT_ID,
            'component_name': GOOGLE_SHEETS_CODE_COMPONENT_NAME,
            'component_category': LoggerComponentEnum.ComponentCategory.Code,
            'developer_email': WHATSAPP_DEVELOPER_EMAIL
        }
    elif category == LoggerComponentEnum.ComponentCategory.Unit_Test:
        return {
            'component_id': GOOGLE_SHEETS_CODE_COMPONENT_ID,
            'component_name': GOOGLE_SHEETS_CODE_COMPONENT_NAME,
            'component_category': LoggerComponentEnum.ComponentCategory.Unit_Test,
            'developer_email': WHATSAPP_DEVELOPER_EMAIL
        }
