# TODO: This is an example file which you should delete/edit after implementing
from database_mysql_local.generic_crud import GenericCRUD
from logger_local.MetaLogger import MetaLogger, Logger
from python_sdk_remote.utilities import our_get_env
from src.google_sheet import GoogleSheet
from fields_local.fields_local import FieldsLocal
from storage_local.aws_s3_storage_local.Storage import Storage
from google_account_local.google_account_local import GoogleAccountLocal
from email_address_local.email_address import EmailAddressesLocal
from user_external_local.user_externals_local import UserExternalsLocal
from data_source_local.data_source_type import DataSourceType
from data_source_local.data_source_field import DataSourceTypeField

from src.constants_src_google_sheet_local import ConstantsSrcGOOGLE_SHEETS

logger = Logger.create_logger(object=ConstantsSrcGOOGLE_SHEETS.GOOGLE_SHEETS_CODE_LOGGER_OBJECT)


class GoogleSheetsLocal():
    def __init__(self, user_external_id: int, storage_id: int, data_source_type_id: int = None, data_source_type_name: str = None, is_test_data: bool = False) -> None:
        if data_source_type_id is None and data_source_type_name is None:
            raise Exception("Either data_source_type_id or data_source_type_name must be filled in")
        
        self.dataSourceTypeName = data_source_type_name
        self.dataSourceTypeId = data_source_type_id
        self.dataSourceTypeLocal = DataSourceType(is_test_data=is_test_data)
        self.dataSourceTypeFieldLocal = DataSourceTypeField(is_test_data=is_test_data)
        self.fields_local = FieldsLocal(is_test_data=is_test_data)
        self.storage_local = Storage(is_test_data=is_test_data)
        google_sheet_id = self.storage_local.select_one_value_by_where(
            select_clause_value="google_drive_document_id",
            where="storage_id=%s AND is_google_sheet=TRUE",
            params=(storage_id,)
        )
        # TODO insert this id into the storage database 
        google_sheet_id="1Hup6jWEUV6x79VPT4ULC7gbCG8VBVKlJsjAh-lXTU7w"
        self.user_external_local = UserExternalsLocal(is_test_data=is_test_data)
        self.email = our_get_env(key="GOOGLE_USER_EXTERNAL_USERNAME")
        self.google_account_local = GoogleAccountLocal(is_test_data=is_test_data)
        self.google_account_local.authenticate(email=self.email)
        self.google_sheet = GoogleSheet(google_sheet_id=google_sheet_id, user_external_id=user_external_id, is_test_data=is_test_data)
    
    def get_columns_data(self):
        for name in self.google_sheet.get_column_names():
            print("\n", name, self.fields_local.get_field_id_by_field_name(name), self.fields_local.get_table_name_by_field_id(self.fields_local.get_field_id_by_field_name(name)))

    def insert_new_data_source_type(self):
        dataToInsert = {
            "name":self.dataSourceTypeName,
            "system_id":6,
            "subsystem_id":602,
        }
        self.dataSourceTypeId = self.dataSourceTypeLocal.insert(data_dict=dataToInsert)

        for field in self.google_sheet.get_column_names():
            dataToInsert = {
                "data_source_type_id":self.dataSourceTypeId,
                "external_field_name":field,
                "field_id":self.fields_local.get_field_id_by_field_name(field),
            }
            self.dataSourceTypeFieldLocal.insert(data_dict=dataToInsert)
        return self.dataSourceTypeId

    def sync_sheet_into_database(self):
        # if not self.dataSourceTypeId:
        #     self.__insert_new_data_source_type()

        #creates a list of data_dicts for every entry in every table that needs data inserted into the database
        dataToInsertIntoDatabases = []
        for entry in self.google_sheet.get_data_rows():
            data_dict = {}
            for value, field in zip(entry, self.google_sheet.get_column_names()):
                field_id = self.fields_local.get_field_id_by_field_name(field_name=field)
                table_id = self.fields_local.get_table_id_by_field_id(field_id=field_id)
                if table_id in data_dict.keys():
                    data_dict[table_id].update({field: value})
                else:
                    data_dict[table_id] = {field: value}
            dataToInsertIntoDatabases.append(data_dict)
        print(dataToInsertIntoDatabases)

        


