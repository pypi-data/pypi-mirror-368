import datetime
from loguru import logger

class Dates:
    def __init__(self):
        pass

    def is_token_expired(self, dt_access_token, dt_download):
            """
            Check if the provided access token has expired.

            Parameters:
            -----------
            access_token: str
                The access token to be checked for expiration.

            Returns:
            --------
            bool
                True if the token has expired, False otherwise.
            """

            # Check if the current time is 9 minutes or more past the expiration time
            return dt_download > dt_access_token + datetime.timedelta(minutes=9)