import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QHBoxLayout
from configparser import ConfigParser

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Screenshot to YouTube Uploader'
        self.initUI()

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
        
        # Client Secrets Path
        self.clientSecretsPathLabel = QLabel('Client Secrets Path')
        self.clientSecretsPathInput = QLineEdit(self)
        self.clientSecretsPathBrowse = QPushButton('Browse')
        self.clientSecretsPathBrowse.clicked.connect(self.openClientSecretsPathDialog)
        clientSecretsPathLayout = QHBoxLayout()
        clientSecretsPathLayout.addWidget(self.clientSecretsPathInput)
        clientSecretsPathLayout.addWidget(self.clientSecretsPathBrowse)
        
        # Category ID
        self.categoryIdLabel = QLabel('Category ID')
        self.categoryIdInput = QLineEdit(self)
        
        # Privacy Status
        self.privacyStatusLabel = QLabel('Privacy Status')
        self.privacyStatusInput = QLineEdit(self)
        
        # Save Settings Button
        self.saveSettingsButton = QPushButton('Save Settings')
        self.saveSettingsButton.clicked.connect(self.saveSettings)
        
        # Start Processing Button
        self.startProcessingButton = QPushButton('Start Processing')
        self.startProcessingButton.clicked.connect(self.startProcessing)
        
        # Add widgets to layout
        layout.addWidget(self.basePathLabel)
        layout.addLayout(basePathLayout)
        layout.addWidget(self.clientSecretsPathLabel)
        layout.addLayout(clientSecretsPathLayout)
        layout.addWidget(self.categoryIdLabel)
        layout.addWidget(self.categoryIdInput)
        layout.addWidget(self.privacyStatusLabel)
        layout.addWidget(self.privacyStatusInput)
        layout.addWidget(self.saveSettingsButton)
        layout.addWidget(self.startProcessingButton)
        
        self.setLayout(layout)

    def openBasePathDialog(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.basePathInput.setText(dir_path)
    
    def openClientSecretsPathDialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            self.clientSecretsPathInput.setText(file_path)
            
    def saveSettings(self):
        config = ConfigParser()
        config['DEFAULT'] = {
            'BasePath': self.basePathInput.text(),
            'ClientSecretsPath': self.clientSecretsPathInput.text(),
            'CategoryID': self.categoryIdInput.text(),
            'PrivacyStatus': self.privacyStatusInput.text()
        }
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)
        print("Settings saved!")

    def startProcessing(self):
        # Placeholder for starting the processing logic
        print("Starting processing...")

        # Here you would implement the logic to process directories and upload videos
        
        print("Processing complete!")

def main():
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
