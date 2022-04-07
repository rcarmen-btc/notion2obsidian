#!/bin/python

import re
from pathlib import Path
import pandas as pd
import shutil


class NotionDir:
    
    def __init__(self, path: Path) -> None:

        self.path = path
        self.files = [NotionFile(i) for i in path.iterdir() if i.is_file()]


    def notion2obsidian(self, path: Path, name: str):

        od = ObsidianDir(path, name, self.files)


class NotionFile:

    mds_unique_code = {}
    data = None
    dir = None 
    
    def replace_links(self, data: str):
        
        self.data = data
        links_inc = re.findall('(\[.+?\]\(.+?\))', data)
        if len(links_inc) == 0:
            return
        links_cor = []
        for link in links_inc:
            tmp = re.findall('\[.+?\]\(.+/(.+)%.+?.\)', link)
            if len(tmp) != 0:
                links_cor.append('[['+ tmp[0] + ']]')
        inc_cor = dict(zip(links_inc, links_cor))

        for i, c in inc_cor.items():
            self.data = self.data.replace(i, c).replace('%20', ' ')
        print(self.data)


    def __init__(self, path: Path) -> None:

        self.path = path
        self.name = path.name
        self.extension  = path.suffix
        self.mds_unique_code[path] = re.findall('.+ ([0-9a-z]{5})[.].+', path.name)

        for p in path.parent.iterdir():
            if self.name.split('.')[0] == p.name:
                self.dir = NotionDir(p)

        if self.extension == '.md':
            with open(str(self.path)) as f:
                self.replace_links(f.read())
        elif self.extension == '.csv':
            df = pd.read_csv(str(self.path))
            d = df.to_dict()
            l = df.values.tolist()
            data = []
            data.append([i for i in d])
            for line in l:
                data.append(line)
        

class ObsidianDir:
    
    def __init__(self, path: Path, name: str, notion_files: list) -> None:

        self.path = path.joinpath(name)
        try:
            self.path.mkdir(parents=True)    
            print('Create new directory')
        except(FileExistsError):
            print('Directory is already exists')

        self.files = []
        for file in notion_files:
            if file.extension == '.md':
                md = MD(file, self.path)
            elif file.extension == '.csv':
                csv = CSV(file, self.path)
            else:
                shutil.copyfile(file.path, self.path.joinpath(file.name))
                

class CSV:
    
    def __init__(self, file: NotionFile, root_path: Path) -> None:
        
        self.file = file
        self.root_path = root_path

        self.files = []

        title = re.findall('(.+) [0-9a-z]{5}[.].+', file.name)[0]

        if file.dir != None:
            self.files.append(ObsidianDir(root_path, title, file.dir.files))
            with open(root_path.joinpath(title).joinpath(title+'.md'), 'x') as f:
                f.write('\n')
        else:
            with open(root_path.joinpath(title+'.md'), 'x') as f:
                f.write('\n')


class MD:
    
    def __init__(self, file: NotionFile, root_path: Path) -> None:
        
        self.file = file
        self.root_path = root_path

        self.files = []

        with open(file.path) as f:
            title = re.findall('[^#]+',f.readline())[0].strip()

        if file.dir != None:
            self.files.append(ObsidianDir(root_path, title, file.dir.files))
            with open(root_path.joinpath(title).joinpath(title+'.md'), 'x') as f:
                f.write(file.data)
        else:
            with open(root_path.joinpath(title+'.md'), 'x') as f:
                f.write(file.data)


def main():
    
    notion = input('Enter path to notion folder: ')
    # res = input('Enter path to result storage: ')
    name = input('Enter storage name: ')
    root = NotionDir(Path(notion))
    root.notion2obsidian(Path(''), name)
    
    
if __name__ == '__main__':
    main()