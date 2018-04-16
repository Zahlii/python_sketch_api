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

        self._raw = {}

        self.sketch_meta: sketch_types.SketchMeta = sketch_types.SketchMeta()
        self.sketch_user: sketch_types.SketchUserData = {}
        self.sketch_document: sketch_types.SketchDocument = sketch_types.SketchDocument()
        self.sketch_pages: List[sketch_types.SketchPage] = []

        self.images: Dict[str, np.ndarray] = {}

        self.preview = np.zeros((100, 100, 3)) + 255  # all white

        if path is not None:
            f = zipfile.ZipFile(path, mode='r')
            # print(f.start_dir)
            # print(f.compression)
            for info in f.infolist():

                # print(info.filename, info.compress_type)
                fc = f.read(info.filename)

                self._raw[info.filename] = fc

                self._file_sizes[info.filename] = len(fc)
                if info.filename.endswith(".json"):
                    j = json.loads(fc)

                    self._file_contents[info.filename] = j

                elif 'images/' in info.filename or '.png' in info.filename:
                    try:
                        img = self.str_to_img(fc)

                        if 'preview' in info.filename:
                            self.preview = img
                        else:
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

        assert len(
            self.sketch_pages) > 0, 'At least one content page is required for sketch to correctly read the file.'

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

    def set_preview(self, img: np.ndarray):
        self.preview = img

    def get_preview(self):
        return self.preview

    def _convert_objects_to_json(self):
        _contents = {}
        _contents['meta.json'] = sketch_io.PyToSketch.write(self.sketch_meta)  # meta.json
        _contents['document.json'] = sketch_io.PyToSketch.write(self.sketch_document)  # document.json
        _contents['user.json'] = sketch_io.PyToSketch.write(self.sketch_user)  # user.json

        for page in self.sketch_pages:
            _contents['pages/' + page.do_objectID + '.json'] = sketch_io.PyToSketch.write(page)

        for name, image in self.images.items():
            _contents[name] = self.img_to_str(image)


        _contents['previews/preview.png'] = self.img_to_str(self.preview)

        _fsizes = {}
        for k, v in _contents.items():
            _fsizes[k] = len(v)

        return _contents

    def get_available_symbols(self):
        m = []
        for p in self.sketch_pages:
            for l in p.layers:
                if l._class == 'symbolMaster':
                    m.append(l)

        return m

    def search_symbols_by_name(self, name: str):
        m = self.get_available_symbols()
        search = []
        for s in m:
            if name in s.name:
                search.append(s)
        return search

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

    # xed = SketchFile.from_file('/Users/niklas.fruehauf/Downloads/Mockup.template (1).sketch')
    # sym  = xed.search_symbols_by_name('NEW Component')

    # for s in sym:
    #    print(s.name)

    # exit()

    main_file = SketchFile.from_file('Icons.sketch')

    text_layers: List[sketch_types.SJTextLayer] = main_file.get_objects_by_class('text')

    for t in text_layers:
        txt = t.get_text()
        print(txt, t.get_font_family())
        if 'sij' in txt:
            break

    symbol_hello = main_file.search_symbols_by_name('HALLO')[0]
    symbol_comp = main_file.search_symbols_by_name('Comp')[0]
    symbol_add = main_file.search_symbols_by_name('Add')[0]

    # for s in [symbol_hello, symbol_comp, symbol_add]:
    #   print(s.name, s.do_objectID, s.symbolID, s.originalObjectID)

    target_page = main_file.sketch_pages[1]

    if main_file.has_page('Test2'):
        main_file.remove_page('Test2')

    test_page = main_file.add_page('Test2')

    test_artboard = sketch_types.SJArtboardLayer.create('Artboard 123424525245', 500, 500)
    test_page.add_artboard(test_artboard)

    rect = sketch_types.SJShapeRectangleLayer.create('Rect ABC', 10, 10, 100, 100)
    test_artboard.add_layer(rect)

    l = sketch_types.SJSymbolInstanceLayer.create(symbol_hello, 50, 50)
    l.add_symbol_override(symbol_hello.get_layer_by_type('symbolInstance')[0].do_objectID, symbol_add)
    l.add_text_override(symbol_hello.get_layer_by_type('text')[0].do_objectID, 'FUCKYEAH')

    l3 = sketch_types.SJSymbolInstanceLayer.create(symbol_hello, 80, 80)
    l3.add_symbol_override(symbol_hello.get_layer_by_type('symbolInstance')[0].do_objectID, symbol_add)
    l3.add_text_override(symbol_hello.get_layer_by_type('text')[0].do_objectID, 'FUCKYEAH2')

    l_group = sketch_types.SJGroupLayer.create('Group Me', [l, l3])

    test_artboard.add_layer(l_group)

    pts = [sketch_types.Point(300, 200), sketch_types.Point(500, 200), sketch_types.Point(50, 23)]
    l_path = sketch_types.SJShapePathLayer.create('Test Path', pts)

    test_artboard.add_layer(l_path)

    l_text = sketch_types.SJTextLayer.create('Sample Text', 20,350, text='Hello World', font_family='sovantaDTBETA-Regular', font_size=52)

    test_artboard.add_layer(l_text)

    # source_str = sketch_io.PyToSketch.write(test_page)

    print()

    main_file.save_to('created.sketch')
