import json
import zipfile
from enum import Enum
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
        delattr(ent, 'zoomValue')
        delattr(ent, 'scrollOrigin')
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
            # print(f.start_dir)
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
                        img = self.str_to_img(fc)
                        self.images[info.filename] = img
                        self._file_contents[info.filename] = img
                    except OSError as e:
                        print('Couldnt load image from file %s' % info.filename)


                else:
                    self._file_contents[info.filename] = fc

            f.close()

            self._read_json_to_objects()

        _link_to_parent(self.sketch_meta, self)
        _link_to_parent(self.sketch_document, self)
        _link_to_parent(self.sketch_user, self)
        _link_to_parent(self.sketch_pages, self)

    def save_to(self, fn):

        assert len(self.sketch_pages) > 0, 'At least one content page is required for sketch to correctly read the file.'

        c = zipfile.ZipFile(fn, mode='w', compression=8)

        _contents = self._convert_objects_to_json()
        print('Saving dict with entries: %s' % _contents.keys())
        for fname, fcont in _contents.items():
            c.writestr(fname, fcont, compress_type=8)

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

    def get_object_by_id(self, idx):
        return self._parser._object_maps[idx]

    def get_objects_by_class(self, cls: str):
        return self._parser._class_maps[cls]

    def img_to_str(self, img: np.ndarray):
        bio = BytesIO()
        img = Image.fromarray(img, mode='RGB')
        img.save(bio, format='png')
        val = bio.getvalue()
        bio.close()
        return val

    def str_to_img(self, imgstr: bytes):
        img: ImageFile = Image.open(BytesIO(imgstr))
        img = np.array(img)
        img.setflags(write=True)
        return img

    def _convert_objects_to_json(self):
        _contents = {}
        _contents['meta.json'] = sketch_io.PyToSketch.write(self.sketch_meta)  # meta.json
        _contents['document.json'] = sketch_io.PyToSketch.write(self.sketch_document)  # document.json
        _contents['user.json'] = sketch_io.PyToSketch.write(self.sketch_user)  # user.json

        for page in self.sketch_pages:
            _contents['pages/' + page.do_objectID + '.json'] = sketch_io.PyToSketch.write(page)

        for name, image in self.images.items():
            _contents[name] = self.img_to_str(image)

        preview = np.zeros((200, 200, 3))

        _contents['previews/preview.png'] = self.img_to_str(preview)

        _fsizes = {}
        for k, v in _contents.items():
            _fsizes[k] = len(v)

        return _contents

    def add_page(self, name: str):
        pg = sketch_types.SketchPage()
        pg.do_objectID = sketch_types.get_object_id()
        pg.name = name
        _link_to_parent(pg, self)

        self.sketch_pages.append(pg)
        ref = sketch_types.MSJSONFileReference()
        ref._ref = pg.get_ref()

        self.sketch_document.pages.append(ref)
        self.sketch_user[pg.do_objectID] = sketch_types.SketchUserDataEntry()

        mapping = sketch_types.SJPageArtboardMappingEntry()
        _link_to_parent(mapping, self)
        mapping.artboards = {}
        mapping.name = name

        self.sketch_meta.pagesAndArtboards[pg.do_objectID] = mapping

        return pg

    def remove_page(self, name: str):
        page = self.get_page_by_name(name)
        self.sketch_pages.remove(page)
        pid = page.do_objectID

        for i, ref in enumerate(self.sketch_document.pages):
            if ref._ref == page.get_ref():
                self.sketch_document.pages.pop(i)
                break

        del self.sketch_meta.pagesAndArtboards[pid]
        del self.sketch_user[pid]

    def get_page_by_name(self, name: str):
        for p in self.sketch_pages:
            if p.name == name:
                return p
        return None

    def has_page(self, name: str):
        return self.get_page_by_name(name) is not None


def _link_to_parent(obj, parent=None):
    if type(obj) in [int, str, bool, float]:
        return
    if issubclass(obj.__class__, Enum):
        return

    if type(obj) is list:
        for o in obj:
            _link_to_parent(o, parent)
        return

    if type(obj) is dict:
        if parent is not None:
            obj['_parent'] = parent
        return

    if hasattr(obj, '__dict__'):
        for k, v in obj.__dict__.items():
            if '__' in k or '_parent' in k:
                continue
            _link_to_parent(v, obj)

        if parent is not None:
            setattr(obj, '_parent', parent)


def compare_dict(source, target, path=''):
    if type(source) != dict:
        if source != target:
            print('Base Mismatch at %s: %s vs %s' % (path, source, target))
        return

    if type(source) != type(target):
        print('Base Type Mismatch at %s: %s vs %s' % (path, source, target))
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
                for i, (ve, te) in enumerate(zip(v, t)):
                    compare_dict(ve, te, p + '[%s]' % i)
        elif '.png' not in k:
            if v != t:
                print('Property mismatch in %s: %s vs %s' % (p, v, t))
            if type(v) != type(t):
                print('Type mismatch in %s: %s vs %s' % (p, v, t))


def check_file(path):
    fe = SketchFile.from_file(path)
    _target_contents = fe._file_contents
    _contents = fe.save_to('xyz.sketch')
    compare_dict(_contents, _target_contents)


if __name__ == '__main__':
    fe = SketchFile.create_empty()

    if fe.has_page('Test2'):
        fe.remove_page('Test2')

    pg = fe.add_page('Test2')

    a = sketch_types.SJArtboardLayer.create('Artboard 123424525245',200,200)
    pg.add_artboard(a)

    rect = sketch_types.SJShapeRectangleLayer.create('Rect ABC', 0, 0, 100, 100)
    a.add_layer(rect)

    fe.save_to('created.sketch')
