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
        return SketchFile()

    def __init__(self, path=None):
        self._file_contents = {}
        self._file_sizes = {}
        self.file_mapping = {}
        self.symbol_mapping = {}

        self.sketch_meta: sketch_types.SketchMeta = sketch_types.SketchMeta()
        self.sketch_user: sketch_types.SketchUserData = {}
        self.sketch_document: sketch_types.SketchDocument = sketch_types.SketchDocument()

        self.images: Dict[str, np.ndarray] = {}

        if path is not None:
            f = zipfile.ZipFile(path, mode='r')
            for info in f.infolist():
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
        c = zipfile.ZipFile(fn, mode='w', compression=zipfile.ZIP_DEFLATED)

        _contents = self._convert_objects_to_json()
        print('Saving dict with %d entries.' % len(_contents))
        for fname, fcont in _contents.items():
            c.writestr(fname, fcont)

        c.close()

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

    def _convert_objects_to_json(self):
        _contents = {}
        _contents['meta.json'] = sketch_io.PyToSketch.write(self.sketch_meta)  # meta.json
        _contents['document.json'] = sketch_io.PyToSketch.write(self.sketch_document)  # document.json
        _contents['user.json'] = sketch_io.PyToSketch.write(self.sketch_user)  # user.json


        for page in self.sketch_pages:
            _contents['pages/' + page.do_objectID + '.json'] = sketch_io.PyToSketch.write(page)

        for name, image in self.images.items():
            bio = BytesIO()
            img = Image.fromarray(image)
            img.save(bio, format='png')
            _contents[name] = bio.getvalue()
            bio.close()


        _fsizes = {}
        for k,v in _contents.items():
            _fsizes[k] = len(v)

        return _contents


if __name__ == '__main__':
    # file = SketchFile.from_file('test.sketch')
    file = SketchFile.from_file('simple.sketch')
    print('Done1')
    # file2 = SketchFile.from_file('Mockup.template.sketch')
    file.save_to('simple2.sketch')
