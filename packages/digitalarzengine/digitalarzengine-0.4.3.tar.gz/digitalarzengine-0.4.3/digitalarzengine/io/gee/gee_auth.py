import logging
import traceback

import ee


class GEEAuth:
    def __init__(self, is_initialized):
        self.is_initialized = is_initialized

    @classmethod
    def gee_init_browser(cls):
        # authentication via browser
        ee.Authenticate()
        ee.Initialize()
        print("GEE initialized")
        return cls(True)

    @classmethod
    def geo_init_personal(cls, service_account, config_file):
        """
        :param service_account: like atherashraf@gmail.com
        :param config_file:  for authtication downloaded from google developer console
        service account (https://console.cloud.google.com/iam-admin/serviceaccounts)
        https://developers.google.com/earth-engine/guides/command_line#acl
        earthengine --service_account_file=service_account_creds.json

        :return:
        """
        # authentication via service account
        try:
            # current_dir = os.path.dirname(os.path.realpath(__file__))
            # service_account = 'atherashraf@gmail.com'
            # config_file = os.path.join(current_dir, '../core/config', 'goolgle-earth-engine-629c01dbea69.json')
            credentials = ee.ServiceAccountCredentials(service_account, config_file)
            ee.Initialize(credentials)
            return cls(True)
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            return cls(False)

    @classmethod
    def gee_init_users(cls, google_user):
        # refresh_token = google_account.serverAuthCode  # .extra_data['serverAuthCode']
        id_token = google_user.extra_data['tokenId']
        access_token = google_user.extra_data['accessId']
        # from api.models import SocialApp
        # app = SocialApp.objects.filter(name='Google App').first()
        # credentials = google.oauth2.credentials.Credentials(
        #     access_token,
        #     refresh_token=id_token,
        #     token_uri='https://oauth2.googleapis.com/token',
        #     client_id=app.client_id,
        #     client_secret=app.secret
        # )
        # ee.Initialize(credentials)

        print("GEE initialized")

        return cls(False)
