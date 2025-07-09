import os
from dotenv import load_dotenv
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def get_gdrive_service():
    """Google Driveの認証を行い、driveオブジェクトを返す"""
    load_dotenv()
    settings = {
        'client_config_file': 'client_secrets.json',
    }
    gauth = GoogleAuth(settings=settings)
    gauth.LocalWebserverAuth()
    return GoogleDrive(gauth)

def list_drive_files(drive, folder_id):
    """指定されたGoogle Driveフォルダ内のファイル名リストを取得する"""
    if not folder_id or 'Your_' in folder_id:
        # ログは呼び出し元で行うため、ここでは空リストを返す
        return []
    try:
        file_list = drive.ListFile({
            'q': f"'{folder_id}' in parents and trashed=false",
            # 'maxResults': 1000  # フォルダ内のファイル上限
        }).GetList()
        # ファイル名だけでなく、ファイルオブジェクト全体を返すように変更
        return file_list
    except Exception as e:
        print(f"Google Driveのファイルリスト取得中にエラー: {e}")
        return []