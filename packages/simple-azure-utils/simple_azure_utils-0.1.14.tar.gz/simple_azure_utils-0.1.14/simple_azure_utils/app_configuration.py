import json
import os
import logging
from .service_principal import ServicePrincipal
from azure.identity import DefaultAzureCredential
from azure.appconfiguration import AzureAppConfigurationClient
from azure.keyvault.secrets import SecretClient


class AppConfiguration:
    """Class for loading Azure App Configurations """

    def __init__(self, app_config_name, settings_path=None):
        self.app_config_name = self.get_app_conf_name(app_config_name)
        self.settings_path = self.get_settings_path(settings_path)

    def load_app_conf_client(self, app_conf_name=None, settings_path=None):
        app_conf_name = self.get_app_conf_name(app_conf_name)
        app_conf_url = f"https://{app_conf_name}.azconfig.io"

        settings_path = self.get_settings_path(default_value=settings_path)
        service_principal = ServicePrincipal(settings_path=settings_path)
        service_principal.load_service_principal_into_environment()
        credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
        client = AzureAppConfigurationClient(base_url=app_conf_url, credential=credential)
        return client

    def load_app_conf(self, app_conf_name=None, settings_path=None, label=None, key=None):
        app_conf_client = self.load_app_conf_client(app_conf_name, settings_path)
        config_list = app_conf_client.list_configuration_settings(label_filter=label, key_filter=key)
        app_config = []
        for config in config_list:
            if 'application/vnd.microsoft.appconfig.keyvaultref' in config.content_type:
                secret = self.load_key_vault_secret(config, settings_path)
                config.value = secret
            app_config.append(config)
        return app_config

    def load_key_vault_secret(self, config, settings_path):
        kv_uri = json.loads(config.value)['uri'].rsplit('/', 2)[0]
        secret_name = json.loads(config.value)['uri'].rsplit('/', 2)[2]

        settings_path = self.get_settings_path(default_value=settings_path)
        service_principal = ServicePrincipal(settings_path=settings_path)
        service_principal.load_service_principal_into_environment()
        credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)

        client = SecretClient(vault_url=kv_uri, credential=credential)
        secret = client.get_secret(secret_name).value
        return secret

    def load_app_conf_into_env(self, app_conf_name=None, settings_path=None, label=None, key=None):
        app_config = self.load_app_conf(app_conf_name, settings_path, label=label, key=key)
        for conf in app_config:
            os.environ[conf.key] = conf.value

    def get_app_conf_name(self, default_value):
        if default_value is not None:
            return default_value
        else:
            return self.app_config_name

    def get_settings_path(self, default_value):
        if default_value is not None:
            return default_value
        else:
            try:
                return self.settings_path
            except AttributeError:
                return None


# some helper functions for loading settings/secrets
def load_setting(setting_name, default_value=None, app_config_name=None, settings_path=None,
                 save_new_setting=False, label=None):
    # if default value is provided, just use that
    if default_value is not None:
        return default_value

    # if the file doesn't have a secret check the environment
    if os.getenv(setting_name) is not None:
        logging.debug(f'Loading {setting_name} from environment')
        return os.environ[setting_name]

    # if a default value is not provided, try to load from file
    if settings_path is not None:
        setting_value = _load_secret_from_file(setting_name, settings_path)
        if setting_value is not None:
            return setting_value

    # if an app config name was provided, try to load from azure
    if app_config_name is not None:
        app_config = AppConfiguration(app_config_name)
        app_config_setting = app_config.load_app_conf(app_config_name,
                                                      settings_path,
                                                      label=label,
                                                      key=setting_name)
        if len(app_config_setting) == 1:
            setting_value = app_config_setting[0].value
        else:
            logging.warning(f'Unable to load setting from app config: {app_config_name}, '
                            f'key: {setting_name}, label: {label} ')
            setting_value = None
        if setting_value is not None:

            # if we could load the secret from azure check if we want to save it to our settings file
            if save_new_setting is True and settings_path is not None:
                new_setting = {setting_name: setting_value}
                _prepare_settings_file(settings_path, new_setting)
            return setting_value

    logging.error(f'Unable to load settings {setting_name}')


def _prepare_settings_file(settings_path, new_settings, exit_on_missing_settings=False):
    logging.debug(f'Preparing and validating settings file {settings_path}')

    settings_file_does_not_exist = False if os.path.exists(settings_path) else True
    if settings_file_does_not_exist:
        logging.warning(f'Settings file not found, generating settings file {settings_path}')
        _generate_settings_file(settings_path, new_settings, exit_on_missing_settings=exit_on_missing_settings)
    _add_missing_settings_to_settings_file(new_settings, settings_path,
                                           exit_on_missing_settings=exit_on_missing_settings)


def _load_settings_from_file(settings_path):
    with open(settings_path, 'r') as f:
        raw_settings = f.read()
        json_settings = json.loads(raw_settings)
        return json_settings


def _add_missing_settings_to_settings_file(new_settings, settings_path,
                                           exit_on_missing_settings=False):
    logging.debug(f'Checking if expected settings are in the settings file {settings_path}')
    settings = _load_settings_from_file(settings_path=settings_path)
    added_new_setting = False
    for expected_setting, expected_settings_value in new_settings.items():
        if expected_setting not in settings:
            logging.warning(f'Adding {expected_setting} to settings')
            settings[expected_setting] = expected_settings_value
            added_new_setting = True
    if added_new_setting is True:
        with open(settings_path, 'w') as f:
            f.write(json.dumps(settings, indent=2))
        logging.warning(f'Updated settings file {settings_path} with new settings')
        if exit_on_missing_settings:
            exit()


def _generate_settings_file(settings_path, settings_template, exit_on_missing_settings=False):
    with open(settings_path, 'w+') as f:
        if 'README' in settings_template:
            del settings_template['README']
        f.write(json.dumps(settings_template, indent=2))
    logging.warning(f'Generated settings file {settings_path} with new settings')
    if exit_on_missing_settings:
        exit()


def _load_secret_from_file(secret_name, settings_path):
    if os.path.exists(settings_path) is False:
        logging.debug(f'settings_path: {settings_path} set but file does not exist')
        return None
    with open(settings_path, 'r') as f:
        raw_settings = f.read()
        settings = json.loads(raw_settings)
        if secret_name not in settings:
            logging.debug(f'secret_name: {secret_name} not found in file: {settings_path}')
            return None
        return settings[secret_name]


class SettingLoader:
    """A generic class for loading settings from Env Variables, Local Files, and Azure App Configurations """

    def __init__(self, app_config_name=None, settings_path=None,
                 save_new_setting=False, label=None):

        self.app_config_name = self.get_app_conf_name(app_config_name)
        self.settings_path = self.get_settings_path(settings_path)
        self.save_new_setting = self.get_save_new_setting(save_new_setting)
        self.label = self.get_label(label)

    def get_app_conf_name(self, default_value):
        if default_value is not None:
            return default_value
        else:
            try:
                return self.app_config_name
            except AttributeError:
                return None

    def get_settings_path(self, default_value):
        if default_value is not None:
            return default_value
        else:
            try:
                return self.settings_path
            except AttributeError:
                return None

    def get_save_new_setting(self, default_value):
        if default_value is not None:
            return default_value
        else:
            try:
                return self.save_new_setting
            except AttributeError:
                return None

    def get_label(self, default_value):
        if default_value is not None:
            return default_value
        else:
            try:
                return self.label
            except AttributeError:
                return None

    def load_setting(self, setting_name, default_value=None, app_config_name=None, settings_path=None,
                     save_new_setting=False, label=None):

        app_config_name = self.get_app_conf_name(app_config_name)
        settings_path = self.get_settings_path(settings_path)
        save_new_setting = self.get_save_new_setting(save_new_setting)
        label = self.get_label(label)

        setting_value = load_setting(setting_name,
                                     default_value=default_value,
                                     app_config_name=app_config_name,
                                     settings_path=settings_path,
                                     save_new_setting=save_new_setting,
                                     label=label)
        return setting_value

    def load_setting_into_env(self, setting_name, default_value=None, app_config_name=None, settings_path=None,
                              save_new_setting=False, label=None):
        setting_value = self.load_setting(setting_name,
                                          default_value=default_value,
                                          app_config_name=app_config_name,
                                          settings_path=settings_path,
                                          save_new_setting=save_new_setting,
                                          label=label)
        os.environ[setting_name] = setting_value
        return setting_value
