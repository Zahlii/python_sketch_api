from enum import Enum

import sketch_types

with open('sketch_types.py', 'r') as f:
    lines = f.readlines()


type_map_ext = {}

def get_type(cls, field):
    if cls in type_map_ext and field in type_map_ext[cls]:
        return type_map_ext[cls][field]

    is_right = False
    for l in lines:
        if 'class %s(' % cls in l or 'class %s:' % cls in l:
            is_right = True

            if '(' in l and ')' in l:  # extends
                tt = get_type(l.split('(')[1].split(')')[0].strip(), field)
                if tt is not None:
                    if cls not in type_map_ext:
                        type_map_ext[cls] = {}
                    type_map_ext[cls][field] = tt
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
            tt = get_full_type(dtype)
            if cls not in type_map_ext:
                type_map_ext[cls] = {}
            type_map_ext[cls][field] = tt
            return tt

    if cls not in type_map_ext:
        type_map_ext[cls] = {}
    type_map_ext[cls][field] = None
    return None


def get_full_type(ttype):
    if ttype in ['int', 'str', 'bool', 'float', 'list', 'dict']:
        return ttype

    for l in lines:
        if 'class' in l and ' ' + ttype in l and ':' in l:
            return ttype
        if ttype + ' ' in l and '=' in l and ':' not in l:
            return l.split('=')[1].strip()

    return ttype


def parse_meta(meta_contents):
    # pprint(meta_contents)

    meta = js_to_py(sketch_types.SketchMeta, meta_contents, p='meta.json')
    return meta


type_map = {}


def _eval(ttype):
    if ttype in type_map:
        return type_map[ttype]
    else:
        r = eval(ttype)
        type_map[ttype] = r
        return r


def str_to_type(ttype):
    ttype = ttype.strip()
    if ttype in ['str', 'list', 'dict', 'float', 'int']:
        return _eval(ttype)
    ftype = 'sketch_types.' + ttype if 'sketch_types.' not in ttype else ttype
    return _eval(ftype)


def js_to_py_dict(ft, js, d, p):
    if 'Dict' not in ft:
        return js
    else:
        is_union = False

        if 'Union' in ft:
            keytype, valtype = ft.split('Dict[')[1].replace(']]', ']').split(',', 1)
            keytype = str_to_type(keytype)
            dn = {}

            for sk, sv in js.items():
                # print(valtype)
                skk = keytype(sk)
                dn[skk] = js_to_union(valtype, sv, d=d + 1, p=p + '.' + sk)
                # dn[skk] = js_to_py(valtype, sv, d=d + 1, p=p + '.' + sk)

            return dn
        else:
            keytype, valtype = ft.split('Dict[')[1].replace(']', '').split(',')
            keytype = str_to_type(keytype)
            valtype = str_to_type(valtype)

            dn = {}

            for sk, sv in js.items():
                # print(valtype)
                skk = keytype(sk)

                # dn[skk] = js_to_union(valtype, sv, d=d + 1, p=p + '.' + sk)
                dn[skk] = js_to_py(valtype, sv, d=d + 1, p=p + '.' + sk)

            return dn


def js_to_py_list(ft, js, d, p):
    if 'List' not in ft:
        return js
    else:
        keytype = ft.split('List[')[1].split(']')[0]
        keytype = str_to_type(keytype)

        dret = []
        for _, v in enumerate(js):
            dret.append(js_to_py(keytype, v, d=d + 1, p=p + '[%d]' % _))

        return dret


def js_to_union(ft, js, d, p):
    avtypes = ft.split('Union[')[1].split(']')[0].split(',')
    for av in avtypes:
        if av == 'str':
            if type(js) is str:
                return js
            continue
        av = str_to_type(av)
        test = av().__dict__
        if '_class' in js and '_class' in test and js['_class'] == test['_class']:
            return js_to_py(av, js, d, p)
        elif 'symbolID' in test:
            return js_to_py(av, js, d, p)
    print('Unknown value %s for union type %s at %s' % (js, ft, p))
    return js


def js_to_py(cls, js, d=0, p=''):
    x = str(cls)
    if 'typing.Union' in x:
        return js_to_union(x, js, d, p)
    if 'NewType' in x:
        return cls(js)
    if 'dict' in x or 'Dict' in x:
        return js_to_py_dict(x, js, d, p)
    elif cls is list:
        ret = js
    elif 'Enum' in x or 'enum' in x:
        return cls(js)
    elif 'float' in x:
        return float(js)
    elif 'int' in x:
        return int(js)
    else:
        ret = cls()

        for k, v in ret.__dict__.items():
            # print('>',k,v)
            ft = get_type(cls.__name__, k)
            # print(k, 'TYPE', ft)

            prop = p + '.' + k
            if k in js:
                vn = js[k]
                if do_types_match(v, vn, ft):
                    ret.__dict__[k] = vn
                    # print('\t' * d + 'COPY', k)
                else:
                    # print(v,vn)
                    if 'Dict[' in ft:
                        if type(vn) is dict:
                            ret.__dict__[k] = js_to_py_dict(ft, vn, d=d + 1, p=prop)
                        else:
                            print('Couldnt match dict property %s to type %s' % (prop, ft))
                        continue
                    if 'List[' in ft:
                        if type(vn) is list:
                            ret.__dict__[k] = js_to_py_list(ft, vn, d=d + 1, p=prop)
                        else:
                            print('Couldnt match list property %s to type %s' % (prop, ft))
                        continue
                    ret.__dict__[k] = js_to_py(str_to_type(ft), vn, d=d + 1, p=prop)
            else:
                pass  # print('Couldnt find expected property %s' % prop)
    return ret


def do_types_match(obj1, obj2, ft=None):
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
                if not do_types_match(i, j):
                    return False
                return True
    elif t1 is dict:
        for k, v in obj1.items():
            if k in t2 and do_types_match(v, obj2[k]):
                return True
            else:
                return False
    else:
        return True


def parse_document(doc_contents):
    meta = js_to_py(sketch_types.SketchDocument, doc_contents, p='doc.json')
    return meta


def parse_user(user_contents):
    return js_to_py(sketch_types.SketchUserData, user_contents, p='user.json')


def parse_page(page_contents, file):
    return js_to_py(sketch_types.SketchPage, page_contents, p=file)
