from PyQt5.QtCore import QTimer, QCoreApplication
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog, QComboBox, QCheckBox
import threading
import random
import datetime
import socket
from .config_manager import ConfigManager
from .video_processor import VideoProcessor
from .shell_hook_event_filter import ShellHookEventFilter

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Screenshots to YouTube Uploader'
        self.processing_thread = None  # Thread handle
        self.is_processing = False  # State flag
        self.config_manager = ConfigManager()
        self.video_processor = VideoProcessor(self, self.config_manager)
        self.initUI()
        self.hide()
        self.loadSettings()
        if self.isProgramEnabled.isChecked():
            self.startProcessing()

    def initUI(self):
        self.setWindowTitle(self.title)
        layout = QVBoxLayout()

        # Base Path
        self.basePathLabel = QLabel('Base Path')
        self.basePathInput = QLineEdit(self)
        self.basePathBrowse = QPushButton('Browse')
        self.basePathBrowse.clicked.connect(self.openBasePathDialog)
        basePathLayout = QHBoxLayout()
        basePathLayout.addWidget(self.basePathInput)
        basePathLayout.addWidget(self.basePathBrowse)

        # Username
        self.usernameLabel = QLabel('Username')
        self.usernameInput = QLineEdit(self)
        usernameLayout = QHBoxLayout()
        usernameLayout.addWidget(self.usernameInput)

        # Password
        self.passwordLabel = QLabel('Password')
        self.passwordInput = QLineEdit(self)
        self.passwordInput.setEchoMode(QLineEdit.Password)
        passwordLayout = QHBoxLayout()
        passwordLayout.addWidget(self.passwordInput)

        # Playlist
        self.playlistLabel = QLabel('Playlist')
        self.playlistInput = QLineEdit(self)
        hostname = socket.gethostname()
        random_number = random.randint(100, 999)
        self.playlistInput.setText(f"{hostname} {random_number}")
        playlistLayout = QHBoxLayout()
        playlistLayout.addWidget(self.playlistInput)

        # Privacy Status
        self.privacyStatusLabel = QLabel('Privacy Status')
        self.privacyStatusInput = QComboBox(self)
        self.privacyStatusInput.addItems(['private', 'public', 'unlisted'])
        
        # Hidden items
        self.dailyLimitReachedUpto = QLineEdit(self)
        self.dailyLimitReachedUpto.hide()
        self.processedUptoDate = QLineEdit(self)
        self.processedUptoDate.hide()
        self.isProgramEnabled = QCheckBox(self)
        self.isProgramEnabled.hide()

        # Save Settings Button
        self.saveSettingsButton = QPushButton('Save Settings')
        self.saveSettingsButton.clicked.connect(self.saveSettings)

        # Start Processing Button
        self.startProcessingButton = QPushButton('Start Processing')
        self.startProcessingButton.clicked.connect(self.toggleProcessing)

        # Add widgets to layout
        layout.addWidget(self.basePathLabel)
        layout.addLayout(basePathLayout)
        layout.addWidget(self.usernameLabel)
        layout.addLayout(usernameLayout)
        layout.addWidget(self.passwordLabel)
        layout.addLayout(passwordLayout)
        layout.addWidget(self.playlistLabel)
        layout.addLayout(playlistLayout)
        layout.addWidget(self.privacyStatusLabel)
        layout.addWidget(self.privacyStatusInput)
        layout.addWidget(self.saveSettingsButton)
        layout.addWidget(self.startProcessingButton)

        self.setLayout(layout)
        
        # Create a single dictionary for UI component references
        self.ui_components = {
            'BasePath': self.basePathInput,
            'Username': self.usernameInput,
            'Password': self.passwordInput,
            'Playlist': self.playlistInput,
            'PrivacyStatus': self.privacyStatusInput,
            'DailyLimitReachedUpto': self.dailyLimitReachedUpto,
            'ProcessedUptoDate': self.processedUptoDate,
            'IsProgramEnabled': self.isProgramEnabled,
        }
        
        # Initialize and install the shell hook event filter
        self.filter = ShellHookEventFilter(self)  # Pass self to give the filter access to this window
        QCoreApplication.instance().installNativeEventFilter(self.filter)

    def loadSettings(self):
        self.config_manager.load_settings_into_ui(self.ui_components)

    def saveSettings(self):
        self.config_manager.prepare_and_save_settings_from_ui(self.ui_components)
        self.saveSettingsButton.setText('Settings Saved ✓✓✓')
        QTimer.singleShot(5000, lambda: self.saveSettingsButton.setText('Save Settings'))

    def checkBasePathStructure(self, base_path):
        # Implement the logic to check the directory structure here
        # For example, check if certain subdirectories exist
        print("Checking base path structure...")

    def disableControls(self):
        self.basePathLabel.setEnabled(False)
        self.basePathInput.setEnabled(False)
        self.basePathBrowse.setEnabled(False)
        self.usernameLabel.setEnabled(False)
        self.usernameInput.setEnabled(False)
        self.passwordLabel.setEnabled(False)
        self.passwordInput.setEnabled(False)
        self.playlistLabel.setEnabled(False)
        self.playlistInput.setEnabled(False)
        self.privacyStatusLabel.setEnabled(False)
        self.privacyStatusInput.setEnabled(False)
        self.saveSettingsButton.setEnabled(False)
        # self.startProcessingButton.setEnabled(False)

    def enableControls(self):
        self.basePathLabel.setEnabled(True)
        self.basePathInput.setEnabled(True)
        self.basePathBrowse.setEnabled(True)
        self.usernameLabel.setEnabled(True)
        self.usernameInput.setEnabled(True)
        self.passwordLabel.setEnabled(True)
        self.passwordInput.setEnabled(True)
        self.playlistLabel.setEnabled(True)
        self.playlistInput.setEnabled(True)
        self.privacyStatusLabel.setEnabled(True)
        self.privacyStatusInput.setEnabled(True)
        self.saveSettingsButton.setEnabled(True)
        self.startProcessingButton.setEnabled(True)

    def openBasePathDialog(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.basePathInput.setText(dir_path)

    def toggleProcessing(self):
        if self.is_processing:
            self.stopProcessing()
        else:
            self.startProcessing()

    def startProcessing(self):
        # Disable all relevant controls
        self.disableControls()
        self.is_processing = True
        self.isProgramEnabled.setChecked(True)
        self.saveSettings()
        
        # Start the processing thread
        self.startProcessingButton.setText('Stop Processing')
        self.processing_thread = threading.Thread(target=self.video_processor.process_screenshots_and_upload_videos, args=())
        self.processing_thread.daemon = True
        self.processing_thread.start()
        print("Starting processing...")

    def stopProcessing(self):
        self.is_processing = False
        self.isProgramEnabled.setChecked(False)
        self.config_manager.prepare_and_save_settings_from_ui(self.ui_components)
        self.startProcessingButton.setText('Waiting to stop processing.....')
        self.startProcessingButton.setEnabled(False)

    def isDailyLimitReached(self):
        if self.dailyLimitReachedUpto.text() == "":
            return False
        
        daily_limit_reached_upto_time = int(self.dailyLimitReachedUpto.text())
        daily_limit_reached_upto_time = datetime.datetime.fromtimestamp(daily_limit_reached_upto_time)

        current_datetime = datetime.datetime.now()

        if daily_limit_reached_upto_time > current_datetime:
            return True
        else:
            return False

    def getDailyLimitReachedTest(self):
        if self.dailyLimitReachedUpto.text() == "":
            return ""
        
        daily_limit_reached_upto_time = int(self.dailyLimitReachedUpto.text())
        daily_limit_reached_upto_time = datetime.datetime.fromtimestamp(daily_limit_reached_upto_time)

        current_datetime = datetime.datetime.now()

        if daily_limit_reached_upto_time > current_datetime:
            time_diff = daily_limit_reached_upto_time - current_datetime
            total_seconds = time_diff.days * 86400 + time_diff.seconds
            return total_seconds
        else:
            return ""

