import dropbox
import os
import sys
from datetime import datetime

if len(sys.argv) < 2:
    print("Usage: " + str(sys.argv[0])+" file_to_upload [dest_path]")
    sys.exit("no filename added")

# Config second argument dest.path

if len(sys.argv) < 3:
    dest_path = '/backup/'
else:
    dest_path = str(sys.argv[2])
    if dest_path[0] != '/':
        dest_path = '/'+dest_path
    if dest_path[len(dest_path)-1] != '/':
        dest_path = dest_path+'/'


now = datetime.now()

# Get token
f_t = open('.\\token.env', "r")
TOKEN = f_t.read().rstrip()

file_path = str(sys.argv[1])
dest_fpath = dest_path+now.strftime("%Y-%m-%d_%H%M%S")+'_' + str(sys.argv[1])


dbx = dropbox.Dropbox(TOKEN)
f = open(file_path, "rb")
file_size = os.path.getsize(file_path)

CHUNK_SIZE = 4 * 1024 * 1024

if file_size <= CHUNK_SIZE:

    dbx.files_upload(f.read(), dest_fpath)
else:
    upload_session_start_result = dbx.files_upload_session_start(
        f.read(CHUNK_SIZE))
    cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                               offset=f.tell())
    commit = dropbox.files.CommitInfo(path=dest_fpath)
    while f.tell() < file_size:
        if ((file_size - f.tell()) <= CHUNK_SIZE):
            print(dbx.files_upload_session_finish(
                f.read(CHUNK_SIZE), cursor, commit))
        else:
            dbx.files_upload_session_append(f.read(CHUNK_SIZE),
                                            cursor.session_id,
                                            cursor.offset)
            cursor.offset = f.tell()
f.close()
