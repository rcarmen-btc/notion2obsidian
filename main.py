#!/bin/python

import re
import sys
from pathlib import Path
import pandas as pd


class NotionFile:

    mds_unique_code = {}
    data = None
    dir = None 
    
    def __init__(self, path: Path) -> None:

        self.path = path
        self.name = path.name
        self.extension  = path.suffix
        self.mds_unique_code[path] = re.findall('.+ ([0-9a-z]{5})[.].+', path.name)

        for p in path.parent.iterdir():
            if self.name.split('.')[0] == p.name:
                print(p.name)
                self.dir = NotionDir(p)
                # print(self.name, p)
            

        if self.extension == '.md':
            with open(str(self.path)) as f:
                self.data = f.read()
        elif self.extension == '.csv':
            df = pd.read_csv(str(self.path))
            d = df.to_dict()
            l = df.values.tolist()
            data = []
            data.append([i for i in d])
            for line in l:
                data.append(line)
            # print(data)
        


class MD:
    
    def __init__(self, file: NotionFile, root_path: Path) -> None:
        
        self.file = file
        self.root_path = root_path

        self.files = []

        if file.dir != None:
            with open(file.path) as f:
                title = re.findall('[^#]+',f.readline())[0].strip()
            self.files.append(ObsidianDir(root_path, title, file.dir.files))
            with open(root_path.joinpath(title).joinpath(title+'.md'), 'x') as f:
                f.write(file.data)
        else:
            print(file.path)
            with open(file.path) as f:
                title = re.findall('[^#]+',f.readline())[0].strip()
            with open(root_path.joinpath(title+'.md'), 'x') as f:
                f.write(file.data)

    

class ObsidianDir:
    
    def __init__(self, path: Path, name: str, notion_files: list) -> None:

        self.path = path.joinpath(name)
        print(self.path)
        try:
            self.path.mkdir(parents=True)    
            print('Create new directory')
        except(FileExistsError):
            print('Directory is already exists')

        self.files = []
        for file in notion_files:
            if file.extension == '.md':
                md = MD(file, self.path)
            # if file.extension == '.md' and file.dir != None:
            #     with open(file.path) as f:
            #         title = re.findall('[^#]+',f.readline())[0].strip()
            #     self.files.append(ObsidianDir(self.path, title, file.dir.files))
            #     with open(self.path.joinpath(title).joinpath(title+'.md'), 'x') as f:
            #         f.write(file.data)
            # elif file.extension == '.md':
            #     print(file.path)
            #     with open(file.path) as f:
            #         title = re.findall('[^#]+',f.readline())[0].strip()
            #     with open(self.path.joinpath(title+'.md'), 'x') as f:
            #         f.write(file.data)


class NotionDir:
    
    def __init__(self, path: Path) -> None:

        self.path = path
        self.files = [NotionFile(i) for i in path.iterdir() if i.is_file()]
        # self.dirs = [NotionDir(i) for i in path.iterdir() if i.is_dir()]


    def notion2obsidian(self, path: Path, name: str):

        od = ObsidianDir(path, name, self.files)
        
        


def main():
    root = NotionDir(Path(sys.argv[1]))
    root.notion2obsidian(Path('/home/riser/python-projects/notion2obsidian'), 'obsidian')

    
if __name__ == '__main__':
    main()