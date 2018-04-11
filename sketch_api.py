import json
import zipfile
from io import BytesIO
from typing import List, Dict

import numpy as np
from PIL import Image, ImageFile

import sketch_io
import sketch_types


class SketchFile:
    @staticmethod
    def from_file(path):
        return SketchFile(path)

    @staticmethod
    def create_empty():
        s = SketchFile()
        s.sketch_document.do_objectID = '2BA3B680-72DD-403D-8CAA-BE5E324D648B'
        # s.sketch_document.do_objectID = sketch_types.get_object_id()

        ent = sketch_types.SketchUserDataEntry()
        delattr(ent,'zoomValue')
        delattr(ent,'scrollOrigin')
        ent.pageListHeight = 110
        s.sketch_user['16FC7444-C1AC-4FA3-9003-F6C778254BFF'] = ent
        return s

    def __init__(self, path=None):
        self._file_contents = {}
        self._file_sizes = {}
        self.file_mapping = {}
        self.symbol_mapping = {}

        self.sketch_meta: sketch_types.SketchMeta = sketch_types.SketchMeta()
        self.sketch_user: sketch_types.SketchUserData = {}
        self.sketch_document: sketch_types.SketchDocument = sketch_types.SketchDocument()
        self.sketch_pages: List[sketch_types.SketchPage] = []

        self.images: Dict[str, np.ndarray] = {}

        if path is not None:
            f = zipfile.ZipFile(path, mode='r')
            print(f.start_dir)
            # print(f.compression)
            for info in f.infolist():

                # print(info.filename, info.compress_type)
                fc = f.read(info.filename)
                self._file_sizes[info.filename] = len(fc)
                if info.filename.endswith(".json"):
                    j = json.loads(fc)

                    self._file_contents[info.filename] = j

                    if 'pages/' in info.filename:
                        if len(j['layers']) > 0 and j['layers'][0]['_class'] == 'symbolMaster':
                            self._symbol_file = info.filename
                            # p(j)
                            for s in j['layers']:
                                if 'symbolID' not in s:
                                    continue
                                if s['name'] in self.symbol_mapping:
                                    print('Duplicate symbol', s['name'], 'in', path)
                                self.symbol_mapping[s['name']] = s['symbolID']

                        self.file_mapping[j['name']] = info.filename

                elif 'images/' in info.filename or '.png' in info.filename:
                    try:
                        img: ImageFile = Image.open(BytesIO(fc))
                        img = np.array(img)
                        img.setflags(write=True)
                        self.images[info.filename] = img
                        self._file_contents[info.filename] = img
                    except OSError as e:
                        print('Couldnt load image from file %s' % info.filename)


                else:
                    self._file_contents[info.filename] = fc

            f.close()

            self._read_json_to_objects()

    def save_to(self, fn):
        c = zipfile.ZipFile(fn, mode='w', compression=0)

        _contents = self._convert_objects_to_json()
        print('Saving dict with %d entries.' % len(_contents))
        for fname, fcont in _contents.items():
            c.writestr(fname, fcont,compress_type=8)

        c.close()

        return _contents

    def _read_json_to_objects(self):
        self._parser = sketch_io.SketchToPy()
        self.sketch_meta: sketch_types.SketchMeta = self._parser.parse_meta(self._file_contents['meta.json'])
        self.sketch_document: sketch_types.SketchDocument = self._parser.parse_document(
            self._file_contents['document.json'])
        self.sketch_user: sketch_types.SketchUserData = self._parser.parse_user(self._file_contents['user.json'])
        self.sketch_pages: List[sketch_types.SketchPage] = []

        for p, v in self._file_contents.items():
            if 'pages/' in p:
                self.sketch_pages.append(self._parser.parse_page(v, p))

    def get_object_by_id(self, idx: sketch_types.SJObjectId):
        return self._parser._object_maps[idx]

    def get_objects_by_class(self, cls: str):
        return self._parser._class_maps[cls]

    def _img_to_str(self, img):
        bio = BytesIO()
        img = Image.fromarray(img,mode='RGB')
        img.save(bio, format='png')
        val = bio.getvalue()
        bio.close()
        return val

    def _convert_objects_to_json(self):
        _contents = {}
        _contents['meta.json'] = sketch_io.PyToSketch.write(self.sketch_meta)  # meta.json
        _contents['document.json'] = sketch_io.PyToSketch.write(self.sketch_document)  # document.json
        _contents['user.json'] = sketch_io.PyToSketch.write(self.sketch_user)  # user.json

        for page in self.sketch_pages:
            _contents['pages/' + page.do_objectID + '.json'] = sketch_io.PyToSketch.write(page)

        for name, image in self.images.items():
            _contents[name] = self._img_to_str(image)

        preview = np.zeros((200, 200, 3))

        _contents['previews/preview.png'] = self._img_to_str(preview)

        _fsizes = {}
        for k, v in _contents.items():
            _fsizes[k] = len(v)

        return _contents

    def add_page(self, name: str, idx: sketch_types.SJObjectId = None):
        pg = sketch_types.SketchPage()
        pg.do_objectID = sketch_types.get_object_id() if idx is None else idx
        pg.name = name

        self.sketch_pages.append(pg)
        ref = sketch_types.MSJSONFileReference()
        ref._ref = 'pages/%s' % pg.do_objectID

        self.sketch_document.pages.append(ref)

        self.sketch_user[pg.do_objectID] = sketch_types.SketchUserDataEntry()

        mapping = sketch_types.SJPageArtboardMappingEntry()
        mapping.artboards = {}
        mapping.name = name

        self.sketch_meta.pagesAndArtboards[pg.do_objectID] = mapping


def compare_dict(source, target, path=''):
    if type(source) != dict:
        if source != target:
            print('Base Mismatch at %s: %s vs %s' % (path,source,target))
        return
    keys1 = set(source.keys())
    keys2 = set(target.keys())

    missing_keys = keys2.difference(keys1)
    too_many_keys = keys1.difference(keys2)

    if len(missing_keys) > 0:
        print('Source is missing keys in %s: %s' % (path, missing_keys))
    if len(too_many_keys) > 0:
        print('Source had unneded keys in %s: %s' % (path, too_many_keys))

    for k in keys1.intersection(keys2):
        v = source[k]

        p = path + '.' + k

        if type(v) is str and '{' in v and ("'" in v or '"' in v):
            v = json.loads(v)
        t = target[k]

        if type(v) is dict:
            compare_dict(v, t, p)
        elif type(v) is list:
            if len(v) < len(t):
                print('Source has less list elements in %s' % p)
            elif len(v) > len(t):
                print('Source has more list elements in %s' % p)
            else:
                for i, (ve,te) in enumerate(zip(v,t)):
                    compare_dict(ve,te,p + '[%s]' % i)
        elif '.png' not in k:
            if v != t:
                print('Property mismatch in %s: %s vs %s' % (p,v,t))
            if type(v) != type(t):
                print('Type mismatch in %s: %s vs %s' % (p,v,t))


if __name__ == '__main__':
    #
    """import glob

    sk = glob.glob('*.sketch')

    global_map = {}

    for f in sk:
        print(f)
        file2 = SketchFile.from_file(f)

        req = file2._parser._observed_fields_map
        for k,v in req.items():
            if k in global_map:
                global_map[k] = v.intersection(global_map[k])
            else:
                global_map[k] = v

    import pprint
    pprint.pprint(global_map)"""

    fe = SketchFile.from_file('EMPTY.sketch')

    _target_contents = fe._file_contents


    f = SketchFile.create_empty()
    f.add_page('Page 1', sketch_types.SJObjectId('6B1FB396-B173-463F-B3F7-D72AAC85F9A6'))
    _contents = f.save_to('EMPTY_PROGRAMMED.sketch')

    compare_dict(_contents, _target_contents)

    # fe2 = SketchFile.from_file('EMPTY_PROGRAMMED.sketch')
