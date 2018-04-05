# based on https://github.com/Zahlii/colab-tf-utils, only deleted keras functionality

_res = get_ipython().run_cell("""
!pip install tqdm
""")


from tqdm import tqdm

from collections import namedtuple
from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from tqdm import tqdm


# Represents a Folder or File in your Google Drive
GDriveItem = namedtuple('GDriveItem', ['name', 'fid'])


class GDriveSync:
    """
    Simple up/downloading functionality to move local files into the cloud and vice versa.
    Provides progress bars for both up- and download.
    """

    def __init__(self):
        auth.authenticate_user()
        # prompt the user to access his Google Drive via the API

        self.drive_service = build('drive', 'v3')
        self.default_folder = self.find_items('Colab Notebooks')[0]

    def update_file_to_folder(self, local_file, folder: GDriveItem = None):
        """
        Update a local file, optionally to a specific folder in Google Drive.
        Deletes the old file if present.
        Warning: Deletes all files with the same name in your Google Drive regardless of the folder structure.
        :param local_file: Path to the local file
        :param folder: (Option) GDriveItem which should be the parent.
        :return:
        """
        old_files = self.find_items(local_file)
        for old_file in old_files:
            self.delete_file(old_file)
        self.upload_file_to_folder(local_file, folder)

    def find_items(self, name):
        """
        Find folders or files based on their name. This always searches the full Google Drive tree!
        :param name: Term to be searched. All files containing this search term are returned.
        :return:
        """
        folder_list = self.drive_service.files().list(
            q='name contains "%s"' % name).execute()
        folders = []
        for folder in folder_list['files']:
            folders.append(GDriveItem(folder['name'], folder['id']))

        return folders

    def upload_file_to_folder(self, local_file, folder: GDriveItem = None):
        """
        Upload a local file, optionally to a specific folder in Google Drive
        :param local_file: Path to the local file
        :param folder: (Option) GDriveItem which should be the parent.
        :return:
        """
        file_metadata = {
            'title': local_file,
            'name': local_file
        }

        if folder is not None:
            file_metadata['parents'] = [folder.fid]

        media = MediaFileUpload(local_file, resumable=True)
        created = self.drive_service.files().create(body=file_metadata,
                                                    media_body=media,
                                                    fields='id')

        response = None
        last_progress = 0

        if folder is not None:
            d = 'Uploading file %s to folder %s' % (local_file, folder.name)
        else:
            d = 'Uploading file %s' % local_file

        pbar = tqdm(total=100, desc=d)
        while response is None:
            status, response = created.next_chunk()
            if status:
                p = status.progress() * 100
                dp = p - last_progress
                pbar.update(dp)
                last_progress = p

        pbar.update(100 - last_progress)

    def download_file_to_folder(self, remote_file: GDriveItem, path):
        """
        Download a GDriveItem to a local folder
        :param remote_file:
        :param path:
        :return:
        """
        request = self.drive_service.files().get_media(fileId=remote_file.fid)

        last_progress = 0

        pbar = tqdm(total=100, desc='Downloading file %s to %s' %
                    (remote_file.name, path))

        with open(path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    p = status.progress() * 100
                    dp = p - last_progress
                    pbar.update(dp)
                    last_progress = p

        pbar.update(100 - last_progress)

    def delete_file(self, file: GDriveItem):
        """
        Delete a remote GDriveItem
        :param file:
        :return:
        """
        request = self.drive_service.files().delete(fileId=file.fid)
        request.execute()
