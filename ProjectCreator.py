import sys
import os
import json
import datetime


from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                               QLineEdit, QComboBox, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap



class HierarchyMaker(QWidget):
    def __init__(self):
        super().__init__()
        settings = self.load_settings()
        self.current_language = self.get_language(settings)
        self.translations = self.load_translations(self.current_language)
        self.project_path, self.project_folder = self.get_project_path(settings)
        self.images_folder = self.get_images_folder(settings)

        # declare QComponent groups
        self.locale_subjects = dict()
        self.direction_subjects = list()

        # declare QComponents
        self.langComboBox = None
        self.projNameLineEdit = None
        self.newProjPath = None
        self.newProjLabel = None

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
            'projectPath': self.project_path,
            'projectFolder': self.project_folder,
            'imagesFolder': self.images_folder
        }
        try:
            with open(self.get_settings_file(), 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            QMessageBox.warning(self, self.translate_key('saving_settings_warning'), str(e))

    def load_settings(self):
        settings = {
            'language': 'English',
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
    def get_project_path(settings) -> tuple[str, str]:
        return \
            settings.get('projectPath', os.path.expanduser("~")), \
            settings.get('projectFolder', 'projects')

    @staticmethod
    def get_images_folder(settings) -> str:
        return settings.get('imagesFolder', 'images')

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
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Update Logo
        logoLabel = QLabel(self)
        logoPixmap = QPixmap('images/logo.png')
        scaledLogoPixmap = logoPixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                                  Qt.TransformationMode.SmoothTransformation)
        logoLabel.setPixmap(scaledLogoPixmap)
        logoLabel.setFixedSize(scaledLogoPixmap.size())
        layout.addWidget(logoLabel)

        # Language selection
        languageLabel = QLabel()
        langComboBox = QComboBox()
        langComboBox.addItems(self.load_language_names())
        langComboBox.currentTextChanged.connect(self.change_language)
        langLayout = QHBoxLayout()
        langLayout.addWidget(languageLabel)
        langLayout.addWidget(langComboBox)
        layout.addLayout(langLayout)


        # Project selection
        projNameLabel = QLabel()
        projNameLineEdit = QLineEdit()
        createProjButton = QPushButton()
        createProjButton.clicked.connect(self.create_project)
        createProjLayout = QHBoxLayout()
        createProjLayout.addWidget(projNameLabel)
        createProjLayout.addWidget(projNameLineEdit)
        createProjLayout.addWidget(createProjButton)
        layout.addLayout(createProjLayout)

        # New project info
        newProjLabel = QLabel()
        newProjLabel.setVisible(False)
        #self.direction_subjects.append(self.newProjLabel)
        newProjPath = QLineEdit()
        newProjPath.setReadOnly(True)
        newProjPath.setVisible(False)
        #self.direction_subjects.append(self.newProjPath)
        layout.addWidget(newProjLabel)
        layout.addWidget(newProjPath)

        self.locale_subjects['language_label'] = languageLabel
        self.locale_subjects['project_name_label'] = projNameLabel
        self.locale_subjects['create_project'] = createProjButton
        self.locale_subjects['new_project_label'] = newProjLabel

        self.direction_subjects.append(langLayout)
        self.direction_subjects.append(createProjLayout)

        self.langComboBox = langComboBox
        self.projNameLineEdit = projNameLineEdit
        self.newProjPath = newProjPath
        self.newProjLabel = newProjLabel


    @staticmethod
    def get_current_date():
        return datetime.datetime.now().strftime('%Y-%m-%d')

    def create_project(self):
        project_folder = self.projNameLineEdit.text()

        if not project_folder:
            QMessageBox.warning(self, self.translate_key('error_title'), self.translate_key('define_project_name'))
            return

        current_date = self.get_current_date()
        date_name_folder_path = os.path.join(self.project_path, self.project_folder, current_date)
        if not os.path.exists(date_name_folder_path):
            os.makedirs(date_name_folder_path)

        project_folder_path = os.path.join(date_name_folder_path, project_folder)
        if os.path.exists(project_folder_path):
            error_message = f'{self.translate_key("folder")} {project_folder} {self.translate_key("already_exists")} at {current_date}.'
            QMessageBox.warning(self, self.translate_key('error_title'), error_message)
            return
        else:
            os.makedirs(project_folder_path)

        os.makedirs(os.path.join(project_folder_path, self.images_folder))

        self.newProjPath.setText(project_folder_path)
        self.newProjLabel.setVisible(True)
        self.newProjPath.setVisible(True)

        QMessageBox.information(self, self.translate_key('success_title'), self.translate_key('success_message'),
                                QMessageBox.StandardButton.Ok)



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
            direction_subject.setDirection(QHBoxLayout.Direction.RightToLeft if is_rtl else QHBoxLayout.Direction.LeftToRight)

        self.save_settings()


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)
    app = QApplication(sys.argv)
    window = HierarchyMaker()
    window.show()
    sys.exit(app.exec())
