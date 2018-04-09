import sketch_io
import sketch_types
import zipfile
import json


class SketchFile:
    @staticmethod
    def from_file(path):
        return SketchFile(path)

    @staticmethod
    def create_empty():
        return SketchFile()

    def __init__(self, path=None):
        self.contents = {}
        self.file_mapping = {}
        self.symbol_mapping = {}

        self.sketch_meta: sketch_types.SketchMeta = sketch_types.SketchMeta()
        self.sketch_user: sketch_types.SketchUserData = {}
        self.sketch_document: sketch_types.SketchDocument = sketch_types.SketchDocument()

        if path is not None:
            f = zipfile.ZipFile(path, mode='r')
            for info in f.infolist():
                fc = f.read(info.filename)

                if info.filename.endswith(".json"):
                    j = json.loads(fc)

                    self.contents[info.filename] = j
                    self.file_mapping['preview'] = info.filename

                    if 'pages/' in info.filename:
                        if len(j['layers']) > 0 and j['layers'][0]['_class'] == 'symbolMaster':
                            self.symbol_file = info.filename
                            # p(j)
                            for s in j['layers']:
                                if 'symbolID' not in s:
                                    continue
                                if s['name'] in self.symbol_mapping:
                                    print('Duplicate symbol', s['name'], 'in', path)
                                self.symbol_mapping[s['name']] = s['symbolID']

                        self.file_mapping[j['name']] = info.filename

                else:
                    self.contents[info.filename] = fc

            f.close()

            self._read_contents_to_objects()

    def save_to(self, fn):
        c = zipfile.ZipFile(fn, mode='w')
        for fname, fcont in self.contents.items():
            # print(fname, type(fcont))
            if fname.endswith(".json"):
                c.writestr(fname, json.dumps(fcont))
            else:
                c.writestr(fname, fcont)

        c.close()

    def _read_contents_to_objects(self):
        self.sketch_meta = sketch_io.parse_meta(self.contents['meta.json'])

        self.sketch_document = sketch_io.parse_document(self.contents['document.json'])

        self.sketch_user = sketch_io.parse_user(self.contents['user.json'])

        self.sketch_pages = []

        for p, v in self.contents.items():
            if 'pages/' in p:
                self.sketch_pages.append(sketch_io.parse_page(v, p))


if __name__ == '__main__':
    file = SketchFile.from_file('Mockup.template.sketch')