import os
import os.path
import json
import sqlite3
import struct
import sys

from PIL import Image

from chicraccoon.enotebackup import EnoteBackup

def grayscale_to_mask(image):
    pixels = image.tobytes()
    new_pixels = []
    for pixel in pixels:
        new_pixels.append(0)
        new_pixels.append(0)
        new_pixels.append(0)
        new_pixels.append(255 - pixel)
    return Image.frombuffer('RGBA', image.size, bytes(new_pixels),
        'raw', 'RGBA', 0, 1)

class LocalNotebook:
    def __init__(self, path):
        self.path = path
        self.d = {
            'forms': {},
            'pages': {},
            'notebooks': {},
            'images': {}
        }

        if not os.path.exists(path):
            os.mkdir(path)

        if os.path.exists(self._path('data.json')):
            with open(self._path('data.json')) as f:
                self.d = json.load(f)

    def save(self):
        with open(self._path('data.json'), 'w') as f:
            json.dump(self.d, f)

    def _path(self, *parts):
        return os.path.join(self.path, *parts)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.save()

    def regenerate_object(self, kind, id_, backup):
        pass
        # assert False

    def load_page_order(self, id_, backup):
        filename = 'PAGE/N{id:06X}/PAGE_ORDER.bin'.format(id=id_)
        data = backup.extract_file(backup.find_file(filename))
        return [x for (x, ) in struct.iter_unpack('<L', data)]

    def update_metadata(self, kind, db, backup):
        table_name = {
            'forms': 'forms',
            'pages': 'pages',
            'notebooks': 'notes'
            }[kind]
        singular = {
            'forms': 'form',
            'pages': 'page',
            'notebooks': 'notebook'
            }[kind]

        self.d[kind] = {}

        # SQL prepared statements don't support placeholders in the
        # FROM clause
        cursor = db.execute('SELECT * FROM {}'.format(table_name))
        objects = cursor.fetchmany()

        while objects:
            for obj in objects:
                id_ = obj['id']

                if kind == 'forms':
                    self.d[kind][id_] = {
                        'notebook': obj['owner_id']
                    }
                elif kind == 'pages':
                    self.d[kind][id_] = {
                        'form': obj['form_id']
                    }
                elif kind == 'notebooks':
                    self.d[kind][id_] = {
                        'pages': self.load_page_order(id_, backup)
                    }

            objects = cursor.fetchmany()

        # uforms (imported forms) have owner_id = 0, just like built-in forms
        # which is kinda inconvenient, so we fix that
        if kind == 'forms':
            cursor = db.execute('SELECT * FROM uforms')
            uforms = cursor.fetchmany()
            while uforms:
                for uform in uforms:
                    self.d[kind][uform['form_id']]['notebook'] = -1
                uforms = cursor.fetchmany()

    def _image_path(self, basename, layer):
        basename = basename[:-4] # removing '.raw'
        return self._path('images', '{}_{}.png'.format(basename, layer))

    def convert_image(self, basename, image):
        for i, layer in enumerate(image.list_layers()):
            image = grayscale_to_mask(layer.to_pil())
            image.save(self._image_path(basename, i))

    def update_images(self, backup):
        try:
            os.mkdir(self._path('images'))
        except FileExistsError:
            pass

        seen_images = set()
        for f in backup.list_files():
            filename = f.filename.decode('utf-8').lower()

            if f.is_dir:
                try:
                    os.mkdir(self._path('images', filename))
                except FileExistsError:
                    pass
                continue

            if not filename.endswith('.raw'):
                continue

            seen_images.add(filename)
            if filename not in self.d['images']:
                self.d['images'][filename] = {
                    'mtime': 0,
                    'layers': 0
                }

            if f.mtime > self.d['images'][filename]['mtime']:
                print('file {} updated, converting'.format(filename))
                image = backup.extract_image(f)
                self.d['images'][filename]['mtime'] = f.mtime
                self.d['images'][filename]['layers'] = image.layer_count()
                self.convert_image(filename, image)
            else:
                print('file {} not updated, skipping'.format(filename))

        files_to_delete = []
        for filename in self.d['images']:
            if filename not in seen_images:
                print('file {} deleted, deleting'.format(filename))
                for i in range(self.d['images'][filename]['layers']):
                    os.remove(self._image_path(filename, i))
                files_to_delete.append(filename)
        for filename in files_to_delete:
            del self.d['images'][filename]


    def update(self, backup):
        with open(self._path('tmp.sqlite3'), 'wb') as f:
            f.write(backup.extract_file(backup.find_file('enotes.db3')))

        db = sqlite3.connect(self._path('tmp.sqlite3'))
        db.row_factory = sqlite3.Row

        self.update_metadata('forms', db, backup)
        self.update_metadata('notebooks', db, backup)
        self.update_metadata('pages', db, backup)

        db.close()
        os.remove(self._path('tmp.sqlite3'))

        self.update_images(backup)

def main():
    if len(sys.argv) != 3:
        print('USAGE:')
        print('{} <notebook-directory> <path/to/enote.bkup>'.format(sys.argv[0]))
        return

    notebook_dir = sys.argv[1]
    backup_path = sys.argv[2]

    with LocalNotebook(notebook_dir) as notebook:
        with EnoteBackup(backup_path) as backup:
            notebook.update(backup)

if __name__ == '__main__':
    main()
