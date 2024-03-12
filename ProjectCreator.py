import sys
import os
import json
import datetime


from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                               QLineEdit, QFileDialog, QComboBox, QMessageBox, QProgressBar)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import (QIcon, QPixmap)



class HierarchyMaker(QWidget):
    def __init__(self):
        super().__init__()
        settings = self.load_settings()
        self.current_language = self.get_language(settings)
        self.translations = self.load_translations(self.current_language)
        self.project_directory = self.get_project_directory(settings)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.locale_subjects = dict()
        self.direction_subjects = list()
        self.setup_ui()
        self.apply_settings()
        self.change_language(self.current_language)

    @staticmethod
    def get_settings_file():
        home_dir = os.path.expanduser('~')
        filename = 'HierarchyMaker.json'
        return os.path.join(home_dir, filename)

    def save_settings(self):
        settings = {
            'language': self.current_language,
            'projectDirectory': self.project_directory
        }
        try:
            with open(self.get_settings_file(), 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            QMessageBox.warning(self, self.translate_key('saving_settings_warning'), str(e))

    def load_settings(self):
        settings = {
            'language': 'English',
            'projectDirectory': os.path.expanduser("~"),
        }
        try:
            with open(self.get_settings_file(), 'r') as f:
                settings.update(json.load(f))
        except FileNotFoundError:
            pass
        return settings

    def apply_settings(self):
        self.langComboBox.setCurrentText(self.current_language)

    @staticmethod
    def get_language(settings):
        return settings.get('language', 'English')

    @staticmethod
    def get_project_directory(settings):
        return settings.get('projectDirectory', os.path.expanduser("~"))

    @staticmethod
    def load_language_codes():
        path = 'locales/language_codes.json'
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @classmethod
    def load_language_names(cls):
        language_codes = cls.load_language_codes()
        return list(language_codes.keys())

    @classmethod
    def load_translations(cls, language_name):
        language_codes = cls.load_language_codes()
        language_code = language_codes.get(language_name, "en")
        path = f'locales/{language_code}.json'
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def translate_key(self, text_key):
        return self.translations.get(text_key, text_key)

    def setup_ui(self):
        # Update Logo
        self.logoLabel = QLabel(self)
        self.logoPixmap = QPixmap('images/logo.png')
        scaledLogoPixmap = self.logoPixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logoLabel.setPixmap(scaledLogoPixmap)
        self.logoLabel.setFixedSize(scaledLogoPixmap.size())
        self.layout.addWidget(self.logoLabel)

        # Language selection
        self.languageLabel = QLabel()
        self.locale_subjects['language_label'] = self.languageLabel
        self.langComboBox = QComboBox()
        self.langComboBox.addItems(self.load_language_names())
        self.langComboBox.currentTextChanged.connect(self.change_language)
        langLayout = QHBoxLayout()
        langLayout.addWidget(self.languageLabel)
        langLayout.addWidget(self.langComboBox)
        self.direction_subjects.append(langLayout)
        self.layout.addLayout(langLayout)

        # Project selection
        self.projNameLabel = QLabel()
        self.locale_subjects['project_name_label'] = self.projNameLabel
        self.projNameLineEdit = QLineEdit()
        self.createProjButton = QPushButton()
        self.createProjButton.clicked.connect(self.create_project)
        self.locale_subjects['create_project'] = self.createProjButton
        createProjLayout = QHBoxLayout()
        createProjLayout.addWidget(self.projNameLabel)
        createProjLayout.addWidget(self.projNameLineEdit)
        createProjLayout.addWidget(self.createProjButton)
        self.direction_subjects.append(createProjLayout)
        self.layout.addLayout(createProjLayout)

        # New project info
        self.newProjLabel = QLabel()
        self.newProjLabel.setVisible(False)
        self.locale_subjects['new_project_label'] = self.newProjLabel
        #self.direction_subjects.append(self.newProjLabel)
        self.newProjPath = QLineEdit()
        self.newProjPath.setReadOnly(True)
        self.newProjPath.setVisible(False)
        #self.direction_subjects.append(self.newProjPath)
        self.layout.addWidget(self.newProjLabel)
        self.layout.addWidget(self.newProjPath)


    @staticmethod
    def get_current_date():
        return datetime.datetime.now().strftime('%Y-%m-%d')

    def create_project(self):
        project_folder = self.projNameLineEdit.text()

        if not project_folder:
            QMessageBox.warning(self, self.translate_key('error_title'), self.translate_key('define_project_name'))
            return

        current_date = self.get_current_date()
        date_name_folder_path = os.path.join(self.project_directory, 'projects', current_date)
        if not os.path.exists(date_name_folder_path):
            os.makedirs(date_name_folder_path)


        project_folder_path = os.path.join(date_name_folder_path, project_folder)
        if os.path.exists(project_folder_path):
            error_message = f'{self.translate_key('folder')} {project_folder} {self.translate_key('already_exists')} at {current_date}.'
            QMessageBox.warning(self, self.translate_key('error_title'), error_message)
            return
        else:
            os.makedirs(project_folder_path)

        os.makedirs(os.path.join(project_folder_path, 'images'))

        self.newProjPath.setText(project_folder_path)
        self.newProjLabel.setVisible(True)
        self.newProjPath.setVisible(True)

        QMessageBox.information(self, self.translate_key('success_title'), self.translate_key('success_message'))


    def change_language(self, language):
        self.current_language = language
        self.translations = self.load_translations(language)

        # Update texts
        self.setWindowTitle(self.translate_key('title'))

        for locale_key in self.locale_subjects:
            self.locale_subjects[locale_key].setText(self.translate_key(locale_key))

        # Update layout
        is_rtl = (language == 'עברית')
        for direction_subject in self.direction_subjects:
            direction_subject.setDirection(QHBoxLayout.RightToLeft if is_rtl else QHBoxLayout.LeftToRight)

        self.save_settings()


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)
    app = QApplication(sys.argv)
    window = HierarchyMaker()
    window.show()
    sys.exit(app.exec())
