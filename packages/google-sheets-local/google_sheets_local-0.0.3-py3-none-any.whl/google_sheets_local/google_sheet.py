from logger_local.MetaLogger import Logger
from python_sdk_remote.utilities import our_get_env
from user_external_local.user_externals_local import UserExternalsLocal
from user_external_local.token__user_external import TokenUserExternals
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import hashlib
import os
import time
import json
from profile_local.profiles_local import ProfilesLocal

from src.constants_src_google_sheet_local import ConstantsSrcGOOGLE_SHEETS

from api_management_local.api_management_local import APIManagementsLocal

logger = Logger.create_logger(object=ConstantsSrcGOOGLE_SHEETS.GOOGLE_SHEETS_CODE_LOGGER_OBJECT)
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/contacts",
    "openid",
    'https://www.googleapis.com/auth/spreadsheets',
]
SLEEP_TIME = 5
TIMEOUT = 120

class GoogleSheet():
    def __init__(self, google_sheet_id, user_external_id, is_test_data: bool = False) -> None:
        self.profile_local = ProfilesLocal(is_test_data=is_test_data)
        self.user_external = UserExternalsLocal(is_test_data=is_test_data)
        self.token_user_external= TokenUserExternals(is_test_data=is_test_data)
        self.apiManager = APIManagementsLocal(is_test_data=is_test_data)
        self.user_email_address = our_get_env(
            "GOOGLE_USER_EXTERNAL_USERNAME", raise_if_empty=False,
            raise_if_not_found=False, default=None
        )
        self.google_client_id = our_get_env("GOOGLE_CLIENT_ID", raise_if_empty=True)
        self.google_client_secret = our_get_env(
            "GOOGLE_CLIENT_SECRET", raise_if_empty=True
        )
        self.google_port_for_authentication = int(
            our_get_env("GOOGLE_PORT_FOR_AUTHENTICATION", raise_if_empty=True)
        )
        self.google_redirect_uris = our_get_env(
            "GOOGLE_REDIRECT_URIS", raise_if_empty=True
        )
        self.google_auth_uri = our_get_env("GOOGLE_AUTH_URI", raise_if_empty=True)
        self.google_token_uri = our_get_env("GOOGLE_TOKEN_URI", raise_if_empty=True)
        self.user_username = self.user_external.select_one_value_by_where(
            select_clause_value="username",
            where="user_external_id=%s",
            params=(user_external_id,),
        )
        self.user_profile_id = self.user_external.select_one_value_by_where(
            select_clause_value="main_profile_id",
            where="user_external_id=%s",
            params=(user_external_id,),
        )

        auth_details = self.user_external.get_auth_details_by_profile_id_system_id_username(
                        system_id=ConstantsSrcGOOGLE_SHEETS.GOOGLE_SYSTEM_ID,
                        username=self.user_username,
                        profile_id=self.user_profile_id
                    )
        if auth_details == None:
            self.__authorize()
            auth_details = self.user_external.get_auth_details_by_profile_id_system_id_username(
            profile_id=self.user_profile_id,
            username=self.user_username,
            system_id=ConstantsSrcGOOGLE_SHEETS.GOOGLE_SYSTEM_ID,
        )

        refresh_token = auth_details.get("refresh_token")
        access_token = auth_details.get("access_token")
        user_external_id = auth_details.get("user_external_id")
        oauth_state = auth_details.get("oauth_state")
        expiry = auth_details.get("expiry")
        self.creds = Credentials(
                        token=access_token,
                        refresh_token=refresh_token,
                        token_uri=self.google_token_uri,
                        client_id=self.google_client_id,
                        client_secret=self.google_client_secret,
                    )
        range='Sheet1'
        #endpoint_url = f"https://sheets.googleapis.com/v4/spreadsheets/{google_sheet_id}/values/{range}"

        #value = self.apiManager.get_api(api_type_id=19, user_external_id=user_external_id, endpoint_url=endpoint_url, data={})
        #print(value)

        service = build("sheets", "v4", credentials=self.creds)
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=google_sheet_id, range=range)
            .execute()
        )
        self.values = result.get("values", [])


    def get_column_names(self) -> list[str]:
        return self.values[0]
    
    def get_data_rows(self) -> list[list[str]]:
        return self.values[1:]
    
    def __authorize(self) -> int:
        """
        Initiate the OAuth 2.0 authorization flow with Google.

        This private method:
        1. Creates an OAuth flow with the configured client credentials
        2. Generates a state parameter and authorization URL
        3. Displays the URL for the user to visit
        4. Polls the database for the authorization code
        5. Exchanges the code for OAuth tokens

        Args:
            oauth_state (str, optional): An existing OAuth state to use.
                Defaults to None, in which case a new state is generated.

        Returns:
            int: The user_external_id of the created/updated record

        Raises:
            Exception: If profile ID is not found for the email
                      or if the auth code is not found in the database
                      within the timeout period
        """
        client_config = {
            "installed": {
                "client_id": self.google_client_id,
                "client_secret": self.google_client_secret,
                "redirect_uris": self.google_redirect_uris,
                "auth_uri": self.google_auth_uri,
                "token_uri": self.google_token_uri,
            }
        }
        state = hashlib.sha256(os.urandom(1024)).hexdigest()
        flow = InstalledAppFlow.from_client_config(
            client_config, SCOPES, redirect_uri=self.google_redirect_uris, state=state
        )
        auth_url, _ = flow.authorization_url(
            access_type="offline", prompt="consent"
        ) 

        main_profile_id = self.profile_local.get_profile_id_by_email_address(
            email_address=self.user_email_address
        )

        user_external_data_dict = {
            "oauth_state": state,
            "username": self.user_email_address,
            "system_id": ConstantsSrcGOOGLE_SHEETS.GOOGLE_SYSTEM_ID,
            "is_refresh_token_valid": True,
        }

        if main_profile_id:
            user_external_data_dict["main_profile_id"] = main_profile_id
        else:
            exception_message = f"Profile ID not found for email {self.user_email_address}"
            logger.error(exception_message)
            raise Exception(exception_message)

        data_dict_compare_user_external = {
            "main_profile_id": main_profile_id,
            # TODO Shall this be self.user_email_address
            "username": self.user_email_address,
            "system_id": ConstantsSrcGOOGLE_SHEETS.GOOGLE_SYSTEM_ID,
        }

        user_external_id =self.user_external.upsert(
            data_dict=user_external_data_dict,
            data_dict_compare=data_dict_compare_user_external,
        )

        token__user_external_id = \
        self.token_user_external.insert_or_update_user_external_access_token(
                user_external_id=user_external_id,
                username=self.user_email_address,
                profile_id=main_profile_id,
                access_token=None,
                expiry=None,
        )

        logger.info(
            f"token__user_external_id: {token__user_external_id}",
        )

        print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ')
        # TODO Can we add the profile name to the bellow message?
        print(f'google-account-local-python-package: Please open the browser in the right profile (i.e, play1@circ.zone) and go to this URL and authorize the application: {auth_url}', flush=True)  # flash=True is for GHA
        print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ')
        # TODO How can we check if we are in GHA or not?
        # webbrowser.open(auth_url) - doesn't work in GHA

        # TODO user_external_id = UserExternal.insert()
        # TODO "oauth_state": oauth_state

        # If the url is
        # http://localhost:54219/?state=yp8FP2BF7cI9xExjUB70Oyaol0oDNG&code=4/0AdLIrYclkHjKFCb_yJn625Htr8FejaRjFawe7mldEqWINitBz6VD_E0ZOWx0K5d4eocYZg&scope=email%20openid%20https://www.googleapis.com/auth/contacts.readonly%20https://www.googleapis.com/auth/userinfo.email&authuser=0&prompt=consent
        # the auth_code is 4/0AdLIrYclkHjKFCb_yJn625Htr8FejaRjFawe7mldEqWINitBz6VD_E0ZOWx0K5d4eocYZg
        # is found after the code= in the url
        auth_code = None
        # Trying every 5 seconds to get the auth code from the database with a timeout of 50 seconds.
        print(f'Waiting for {TIMEOUT} seconds, for you to choose account {self.user_email_address} in this URL {auth_url}', flush=True)  # flash=True is for GHA  # noqa
        for i in range(TIMEOUT // SLEEP_TIME):
            # selecting by primary key is faster, so we don't select by state
            # auth_code = self.select_one_value_by_column_and_value(
            #     select_clause_value="access_token",
            #     column_value=user_external_inserted_id,
            # )

            auth_code = self.user_external.get_access_token(
                system_id=ConstantsSrcGOOGLE_SHEETS.GOOGLE_SYSTEM_ID,
                username=self.user_email_address,
                profile_id=main_profile_id,
            )

            if auth_code:
                logger.info(
                    f"Auth code found in the database after {i + 1} times out of {TIMEOUT // SLEEP_TIME}."
                )
                break
            time.sleep(SLEEP_TIME)
            logger.info(
                f"Failed to get the auth code from the database for the {i + 1} time out of {TIMEOUT // SLEEP_TIME}."
            )

        if not auth_code:
            # TODO Add the UserContext.username() in the begging of the Exception text
            logger.error(
                f"Auth code not found in the database after {TIMEOUT} seconds. "
                f"Please check if you have chosen the correct Google account {self.user_email_address} in the browser opened."
            )
            raise Exception("Auth code not found in the database, you probably didn't choose the Google Account to use in the browser opened.")
        # TODO How can we check that the user choose the expected Google Account or not?
        flow.fetch_token(code=auth_code)
        self.creds = flow.credentials

        self.__save_credentials(
            user_external_id=user_external_id,
            state=state,
            creds=self.creds,
        )

        return user_external_id
        # self.creds = flow.run_local_server(port=self.port)

    def __save_credentials(self, user_external_id: int, state: str, creds: Credentials):
        """
        Save the credentials to a file.

        Args:
            user_external_id (int): The user_external_id to associate with the credentials.
            creds (Credentials): The credentials to save.
        """
        creds_dict = json.loads(creds.to_json())

        access_token = creds_dict.get("token")
        refresh_token = creds_dict.get("refresh_token")
        expiry = creds_dict.get("expiry")

        token_user_external_data_dict = {
            "user_external_id": user_external_id,
            "access_token": access_token,
            "expiry": expiry,
            "oauth_state": state,
        }

        data_dict_compare = {
            "user_external_id": user_external_id,
        }

        token__user_external_id = self.token_user_external.upsert(
            data_dict=token_user_external_data_dict,
            data_dict_compare=data_dict_compare,
        )
        logger.info(
            f"Token data dict: {token_user_external_data_dict}/n Token user_external inserted ID: {token__user_external_id}",
            object=token_user_external_data_dict,
        )

        updated_rows = self.user_external.update_refresh_token_by_user_external_id(
            user_external_id=user_external_id,
            refresh_token=refresh_token,
        )

        logger.info(
            f"Updated {updated_rows} rows in user_external table with refresh token.",
            object={"user_external_id": user_external_id},
            )