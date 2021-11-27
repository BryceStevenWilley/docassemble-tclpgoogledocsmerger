from docassemble.base.util import DAGoogleAPI, DAFile
from docassemble.base.functions import currency
import apiclient

api = DAGoogleAPI()
#__all__ = ['download_drive_file_as_docx', 'download_drive_docx_file']

def download_drive_file_as_docx(file_id, filename):
    the_file = DAFile()
    the_file.set_random_instance_name()
    if not filename[-5:].lower() == ".docx":
        filename = filename + ".docx"
    the_file.initialize(filename=filename)
    service = api.drive_service()
    with open(the_file.path(), 'wb') as fh:
        response = service.files().export_media(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        downloader = apiclient.http.MediaIoBaseDownload(fh, response)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
    the_file.commit()
    return the_file

def download_drive_docx_file(file_id, filename):
    the_file = DAFile()
    the_file.set_random_instance_name()
    if not filename[-5:].lower() == ".docx":
        filename = filename + ".docx"
    the_file.initialize(filename=filename)
    service = api.drive_service()
    with open(the_file.path(), 'wb') as fh:
        response = service.files().get_media(fileId=file_id)
        downloader = apiclient.http.MediaIoBaseDownload(fh, response)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
    the_file.commit()
    return the_file
  
def get_folder_id(folder_name):
  service = api.drive_service()
  resp = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)",
                              q=f"mimeType='application/vnd.google-apps.folder' and sharedWithMe and name='{str(folder_name)}'").execute()
  folder_id = None
  for item in resp.get('files', []):
    folder_id = item['id']
  return folder_id

def get_files_in_folder(folder_name=None, folder_id=None):
    if folder_name is None and folder_id is None:
      raise Exception("Need to provide a folder name or an ID, you provided neither")
    if folder_id is None:
      folder_id = get_folder_id(folder_name)
      if folder_id is None:
        raise Exception(f"The folder {folder_name} was not found")
    service = api.drive_service()
    items = list()
    while True:
        response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="trashed=false and '" + str(folder_id) + "' in parents").execute()
        for the_file in response.get('files', []):
            items.append(the_file)
        page_token = response.get('nextPageToken', None)
        if page_token is None or len(items) > 80:
            break
    return [item['name'] for item in items]