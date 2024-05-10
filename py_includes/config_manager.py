from PyQt5.QtWidgets import QLineEdit, QComboBox, QCheckBox
from configparser import ConfigParser
import os
from cryptography.fernet import Fernet

class ConfigManager:
    def __init__(self, filename='configs\\settings.ini'):
        self.config_path = filename
        key = b'59BhRzNFJEILmsaAkB4n2XMv2z1t4Mg1JOycKuzL8to='
        self.cipher_suite = Fernet(key)

    def load_settings_into_ui(self, ui_components):
        """
        Loads settings from the configuration file if it exists and sets UI components based on the settings.
        ui_components should be a dictionary of QLineEdit widgets (or similar) with keys matching the config settings keys.
        """
        config = ConfigParser()
        if os.path.exists(self.config_path):
            config.read(self.config_path)
            if 'DEFAULT' in config:
                for key, widget in ui_components.items():
                    value = config['DEFAULT'].get(key, '')
                    if key in ['Username', 'Password'] and value:
                        value = self.decrypt_data(value)
                    if isinstance(widget, QLineEdit):
                        widget.setText(value)
                    elif isinstance(widget, QCheckBox):
                        value = True if value == "True" else False
                        widget.setChecked(value)
                    elif isinstance(widget, QComboBox):
                        index = widget.findText(value)
                        if index >= 0:
                            widget.setCurrentIndex(index)
        return {}
    
    def prepare_and_save_settings_from_ui(self, ui_components):
        """
        Prepares a settings dictionary from UI components and saves it to the configuration file.
        """
        settings = {}
        for key, widget in ui_components.items():
            if isinstance(widget, QLineEdit):
                value = widget.text()
            elif isinstance(widget, QCheckBox):
                value = widget.isChecked()
            elif isinstance(widget, QComboBox):
                value = widget.currentText()  # Get the current text from the combo box
            if key in ['Username', 'Password']:
                value = self.encrypt_data(value)
            settings[key] = value
        self.save_settings(settings)

    def save_settings(self, settings):
        """
        Saves the provided settings dictionary to the configuration file under the 'DEFAULT' section.
        """
        config = ConfigParser()
        config['DEFAULT'] = settings
        with open(self.config_path, 'w') as configfile:
            config.write(configfile)
        print("Settings saved!")

    def encrypt_data(self, data):
        """
        Encrypts data using Fernet symmetric encryption.
        """
        return self.cipher_suite.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data):
        """
        Decrypts data that was encrypted with Fernet symmetric encryption.
        """
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()