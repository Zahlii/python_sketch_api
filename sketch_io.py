import copy
import json
from json import JSONEncoder
from typing import Dict, Any, List

import sketch_types
from sketch_types import SJObjectId

with open('sketch_types.py', 'r') as f:
    lines = f.readlines()


class SketchToPy:
    type_map_ext = {}
    type_map = {}

    @classmethod
    def _get_type(cls, cls_name, field):
        if cls_name in cls.type_map_ext and field in cls.type_map_ext[cls_name]:
            return cls.type_map_ext[cls_name][field]

        is_right = False
        for l in lines:
            if 'class %s(' % cls_name in l or 'class %s:' % cls_name in l:
                is_right = True

                if '(' in l and ')' in l:  # extends
                    tt = cls._get_type(l.split('(')[1].split(')')[0].strip(), field)
                    if tt is not None:
                        if cls_name not in cls.type_map_ext:
                            cls.type_map_ext[cls_name] = {}
                        cls.type_map_ext[cls_name][field] = tt
                        return tt
            elif 'class ' in l and ':' in l:
                is_right = False

            if is_right and 'self.%s' % field in l:
                if ':' not in l:
                    if '[]' in l:
                        return 'list'
                    if '{}' in l:
                        return 'dict'
                dtype = l.split(':')[1].split('=')[0].strip()
                tt = cls.get_full_type(dtype)
                if cls_name not in cls.type_map_ext:
                    cls.type_map_ext[cls_name] = {}
                cls.type_map_ext[cls_name][field] = tt
                return tt

        if cls_name not in cls.type_map_ext:
            cls.type_map_ext[cls_name] = {}
        cls.type_map_ext[cls_name][field] = None
        return None

    @classmethod
    def get_full_type(cls, ttype):
        if ttype in ['int', 'str', 'bool', 'float', 'list', 'dict']:
            return ttype

        for l in lines:
            if 'class' in l and ' ' + ttype in l and ':' in l:
                return ttype
            if ttype + ' ' in l and '=' in l and ':' not in l:
                return l.split('=')[1].strip()

        return ttype

    def __init__(self):
        self._object_maps: Dict[SJObjectId, Any] = {}
        self._class_maps: Dict[str, List[Any]] = {}

        self._observed_fields_map: Dict[str, set] = {}

    def parse_meta(self, meta_contents):
        # pprint(meta_contents)
        meta = self.js_to_py(sketch_types.SketchMeta, meta_contents, p='meta.json')
        return meta

    @classmethod
    def _eval(cls, ttype):
        if ttype in cls.type_map:
            return cls.type_map[ttype]
        else:
            r = eval(ttype)
            cls.type_map[ttype] = r
            return r

    @classmethod
    def str_to_type(cls, ttype):
        ttype = ttype.strip()
        if ttype in ['str', 'list', 'dict', 'float', 'int', 'bool']:
            return cls._eval(ttype)
        ftype = 'sketch_types.' + ttype if 'sketch_types.' not in ttype else ttype
        return cls._eval(ftype)

    def js_to_py_dict(self, ft, js, d, p):
        if 'Dict[' not in ft:
            return js
        else:
            is_union = False

            if 'Union' in ft:
                keytype, valtype = ft.split('Dict[')[1].replace(']]', ']').split(',', 1)
                keytype = self.str_to_type(keytype)
                dn = {}

                for sk, sv in js.items():
                    # print(valtype)
                    skk = keytype(sk)
                    dn[skk] = self.js_to_union(valtype, sv, d=d + 1, p=p + '.' + sk)
                    # dn[skk] = js_to_py(valtype, sv, d=d + 1, p=p + '.' + sk)

                return dn
            else:
                keytype, valtype = ft.split('Dict[')[1].replace(']', '').split(',')
                keytype = self.str_to_type(keytype)
                valtype = self.str_to_type(valtype)

                dn = {}

                for sk, sv in js.items():
                    # print(valtype)
                    skk = keytype(sk)

                    # dn[skk] = js_to_union(valtype, sv, d=d + 1, p=p + '.' + sk)
                    dn[skk] = self.js_to_py(valtype, sv, d=d + 1, p=p + '.' + sk)

                return dn

    def js_to_py_list(self, ft, js, d, p):
        if 'List' not in ft:
            return js
        else:
            keytype = ft.split('List[')[1].split(']')[0]
            keytype = self.str_to_type(keytype)

            dret = []
            for _, v in enumerate(js):
                dret.append(self.js_to_py(keytype, v, d=d + 1, p=p + '[%d]' % _))

            return dret

    def js_to_union(self, ft, js, d, p):
        avtypes = ft.split('Union[')[1].split(']')[0].split(',')
        for av in avtypes:
            av = av.strip()
            if av == 'str':
                if type(js) is str:
                    return js
                continue
            if av == 'dict' and type(js) is dict:
                return js
            avt = self.str_to_type(av)
            if 'typing.Dict' in str(avt) and type(js) == dict:
                if '_class' in js:
                    continue
                if 'symbolID' in js:
                    continue
                else:
                    return self.js_to_py(avt, js, d, p)

            test = avt().__dict__
            if '_class' in js and '_class' in test and js['_class'] == test['_class']:
                return self.js_to_py(avt, js, d, p)
            elif 'symbolID' in test and 'SymbolOverride' in av:
                return self.js_to_py(avt, js, d, p)
        print('Unknown value %s for union type %s at %s' % (js, ft, p))
        return js

    def js_to_py(self, cls, js, d=0, p=''):
        x = str(cls)

        if 'typing.Union' in x:
            return self.js_to_union(x, js, d, p)
        if 'NewType' in x:
            return cls(js)
        if 'dict' in x or 'Dict' in x:
            return self.js_to_py_dict(x, js, d, p)
        elif cls is list:
            ret = js
        elif 'Enum' in x or 'enum' in x:
            return cls(js)
        elif 'float' in x:
            return float(js)
        elif 'int' in x and not 'sketch_types' in x:
            return int(js)
        elif 'str' in x:
            return js
        elif 'bool' in x:
            return bool(js)
        else:
            ret = cls()

            available_keys = set(js.keys())
            optional_keys = set(ret.__dict__.keys())

            if x in self._observed_fields_map:
                self._observed_fields_map[x] = self._observed_fields_map[x].intersection(available_keys)
            else:
                self._observed_fields_map[x] = available_keys

            for bcls in cls.__bases__:
                if bcls is object:
                    continue
                z = bcls()
                optional_keys = optional_keys.union(set(z.__dict__.keys()))

            required_keys = set([r for r in optional_keys if ret.__dict__[r] is not None])
            # optional_keys = set([r for r in required_keys if ret.__dict__[r] is not None])

            missing_keys = required_keys.difference(available_keys)
            unknown_keys = available_keys.difference(optional_keys)

            if len(missing_keys) > 0:
                pass
                #print('Missing some properties required by type file, but not found in sketch file in %s [%s]: %s' % (
                #    p, x, missing_keys))

            if len(unknown_keys) > 0:
                print('Found unknown props in sketch file in %s with type %s' % (p, x))
                for uk in unknown_keys:
                    jsuk = js[uk]
                    print('\t%s => %s: \n\t\t%s' % (uk, type(jsuk), jsuk))
                return

            for k, v in ret.__dict__.items():
                # print('>',k,v)
                ft = self._get_type(cls.__name__, k)
                # print(k, 'TYPE', ft)

                prop = p + '.' + k
                if k in js:
                    vn = js[k]

                    if self._do_types_match(v, vn, ft):
                        ret.__dict__[k] = vn
                        # print('\t' * d + 'COPY', k)
                    else:
                        # print(v,vn)
                        if 'Dict[' in ft:
                            if type(vn) is dict:
                                ret.__dict__[k] = self.js_to_py_dict(ft, vn, d=d + 1, p=prop)
                            else:
                                print('Couldnt match dict property %s to type %s' % (prop, ft))
                            continue
                        if 'List[' in ft:
                            if type(vn) is list:
                                ret.__dict__[k] = self.js_to_py_list(ft, vn, d=d + 1, p=prop)
                            else:
                                print('Couldnt match list property %s to type %s' % (prop, ft))
                            continue
                        ret.__dict__[k] = self.js_to_py(self.str_to_type(ft), vn, d=d + 1, p=prop)

                else:
                    pass  # print('Couldnt find expected property %s' % prop)

        if 'do_objectID' in js:
            self._object_maps[js['do_objectID']] = ret
        if '_class' in js:
            c = js['_class']
            if c not in self._class_maps:
                self._class_maps[c] = []
            self._class_maps[c].append(ret)
        return ret

    @classmethod
    def _do_types_match(cls, obj1, obj2, ft=None):
        t1 = type(obj1)
        t2 = type(obj2)

        if t1 == float and t2 == int or t2 == float and t1 == int:
            return True

        if t1 != t2:
            return False

        if t1 is list:

            if min(len(obj1), len(obj2)) == 0:
                if 'List' in ft and len(obj2) > 0:
                    exp_type = ft.split('List[')[1].split(']')[0].strip()
                    return type(obj2[0]).__name__ == exp_type
                else:
                    return True
            else:
                for i, j in zip(obj1, obj2):
                    if not cls._do_types_match(i, j):
                        return False
                    return True
        elif t1 is dict:
            for k, v in obj1.items():
                if k in t2 and cls._do_types_match(v, obj2[k]):
                    return True
                else:
                    return False
        else:
            return True

    def parse_document(self, doc_contents):
        meta = self.js_to_py(sketch_types.SketchDocument, doc_contents, p='doc.json')
        return meta

    def parse_user(self, user_contents):
        return self.js_to_py(sketch_types.SketchUserData, user_contents, p='user.json')

    def parse_page(self, page_contents, file):
        return self.js_to_py(sketch_types.SketchPage, page_contents, p=file)


def del_none(d):
    """
    Delete keys with the value ``None`` in a dictionary, recursively.

    This alters the input so you may wish to ``copy`` the dict first.
    """
    # For Python 3, write `list(d.items())`; `d.items()` won’t work
    # For Python 2, write `d.items()`; `d.iteritems()` won’t work

    if isinstance(d, dict):
        for key, value in list(d.items()):
            if key == '_parent':
                del d[key]
            elif value is None:
                del d[key]
            else:
                del_none(d[key])

    elif isinstance(d, list):
        for i, v in enumerate(d):
            del_none(v)
    elif hasattr(d,'__dict__'):
        d = d.__dict__
        if '_parent' in d:
            del d['_parent']
        return del_none(d)

    return d


class AdvancedEncoder(JSONEncoder):
    def default(self, o):
        try:
            stype = str(type(o))

            if 'mappingproxy' in stype:  # Enum
                return None

            if 'enum' in stype:
                return o.value

            if hasattr(o,'__dict__'):
                return o.__dict__

            return o

        except Exception as e:
            print(e)
            print(str(o))


class PyToSketch:
    @classmethod
    def write(cls, obj):
        obj = copy.deepcopy(obj)
        obj = del_none(obj)
        return json.dumps(obj, cls=AdvancedEncoder, check_circular=False)
