import os
from django.core.files.storage import FileSystemStorage
from app import settings
from urllib.parse import urljoin

class CkeditorCustomStorage(FileSystemStorage):
    # def get_folder_name(self):
    #     return datetime.now().strftime('%Y/%m/%d')

    def get_valid_name(self, name):
        return name

    def _save(self, name, content):
        folder_name = ''
        name = os.path.join(folder_name, self.get_valid_name(name))
        return super()._save(name, content)

    location = os.path.join(settings.MEDIA_ROOT, 'ckeditor5/')
    base_url = urljoin(settings.MEDIA_URL, 'ckeditor5/')
