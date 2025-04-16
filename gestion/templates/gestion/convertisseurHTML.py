import os
import codecs

def convert_to_utf8(directory, current_encoding='cp1252'):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.html'):
                filepath = os.path.join(root, filename)
                try:
                    with codecs.open(filepath, 'r', current_encoding) as f:
                        content = f.read()
                    with codecs.open(filepath, 'w', 'utf-8') as f:
                        f.write(content)
                    print(f'Converted {filepath} to UTF-8')
                except Exception as e:
                    print(f'Error converting {filepath}: {e}')

convert_to_utf8('.')  # exécuter dans le répertoire courant