import sys

from chicraccoon.enotebackup import EnoteBackup

def cmd_list(backup_path):
    with EnoteBackup(backup_path) as backup:
        for f in backup.list_files():
            print('{kind} {f.filename} ({f.size} bytes, mtime {f.mtime})'.format(
                f=f,
                kind='d' if f.is_dir else 'f'))

def cmd_extract_file(backup_path, file_path, dest_path):
    with EnoteBackup(backup_path) as backup:
        f = backup.find_file(file_path)
        if f is None:
            print('file not found')
            return

        print('saving {} to {}'.format(file_path, dest_path))
        with open(dest_path, 'wb') as dest_file:
            dest_file.write(backup.extract_file(f))

def cmd_extract_image(backup_path, file_path, dest_path):
    if '%' not in dest_path:
        print('destination path must include % (placeholder for layer number)')

    with EnoteBackup(backup_path) as backup:
        f = backup.find_file(file_path)
        if f is None:
            print('file not found')
            return

        image = backup.extract_image(f)

        for i, layer in enumerate(image.list_layers()):
            layer_path = dest_path.replace('%', str(i))
            print('saving layer {} to {}'.format(i, layer_path))
            layer.to_pil().save(layer_path)

def main():
    if len(sys.argv) == 1:
        print('USAGE:')
        print('{} <command> <command-args>'.format(sys.argv[0]))
        print('where the command and arguments are one of')
        print('  - list <path/to/enote.bkup>')
        print('  - extract_file <path/to/enote.bkup> <path/to/file/in/backup> <path/to/destination.raw>')
        print('  - extract_image <path/to/enote.bkup> <path/to/file/in/backup> <path/to/destination_%.png>')
        return

    command = sys.argv[1]
    if command == 'list':
        cmd_list(sys.argv[2])
    elif command == 'extract_file':
        cmd_extract_file(sys.argv[2], sys.argv[3], sys.argv[4])
    elif command == 'extract_image':
        cmd_extract_image(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print('unknown command {}'.format(command))

if __name__ == '__main__':
    main()
