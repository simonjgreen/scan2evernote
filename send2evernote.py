#! /usr/bin/python
from evernote.api.client import EvernoteClient

import hashlib
import binascii
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
import os, os.path
import argparse
import magic
mime = magic.Magic(mime=True)

#Put your dev token here
dev_token = ""
client = EvernoteClient(token=dev_token, sandbox=False)
userStore = client.get_user_store()
user = userStore.getUser()

parser = argparse.ArgumentParser(description='Send the specified file to a new Evernote note')
parser.add_argument('path', help='Path of file to send')
parser.add_argument('--batch', help='Treat PATH as a directory of files and attach all files in that directory to a single note', dest='batch', action='store_true')
parser.set_defaults(batch=False)
args = parser.parse_args()
path = args.path
batch = args.batch

noteStore = client.get_note_store()

note = Types.Note()
note.notebookGuid = 'e8fb1f59-effa-47bc-8da9-829cffca636a'
note.title = 'New Scan'
note.content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
note.content += '<en-note>'

note.resources = []
if batch is True:
    for root, _, files in os.walk(path):
        for f in sorted(files):
            fullpath = os.path.join(root, f)
            image = open(fullpath, 'rb').read()
            
            md5 = hashlib.md5()
            md5.update(image)
            hash = md5.digest()
            
            data = Types.Data()
            data.size = len(image)
            data.bodyHash = hash
            data.body = image
            
            resource = Types.Resource()
            resource.mime = 'image/pdf'
            resource.data = data
            
            note.resources.append(resource)
            
            hash_hex = binascii.hexlify(hash)
            
            note.content += '<en-media type="image/pdf" hash="' + hash_hex + '"/>'
else:
    image = open(path, 'rb').read()
    
    md5 = hashlib.md5()
    md5.update(image)
    hash = md5.digest()
    
    data = Types.Data()
    data.size = len(image)
    data.bodyHash = hash
    data.body = image
    
    resource = Types.Resource()
    resource.mime = mime.from_file(path)
    resource.data = data
    
    note.resources.append(resource)
    
    hash_hex = binascii.hexlify(hash)
    
    note.content += '<en-media type="'+mime.from_file(path)+'" hash="' + hash_hex + '"/>'


note.content += '</en-note>'
note = noteStore.createNote(note)
