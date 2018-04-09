import sketch_types

with open('sketch_types.py', 'r') as f:
    lines = f.readlines()


def get_type(cls, field):
    is_right = False
    for l in lines:
        if 'class %s(' % cls in l or 'class %s:' % cls in l:
            is_right = True

            if '(' in l and ')' in l:  # extends
                tt = get_type(l.split('(')[1].split(')')[0].strip(), field)
                if tt is not None:
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

            return get_full_type(dtype)

    return None


def get_full_type(ttype):
    if ttype in ['int', 'str', 'bool', 'float', 'list','dict']:
        return ttype
    for l in lines:
        if 'class' in l and ' ' + ttype in l:
            return ttype
        if ttype + ' ' in l and '=' in l:
            return l.split('=')[1].strip()

    return ttype


def parse_meta(meta_contents):
    # pprint(meta_contents)

    meta = js_to_py(sketch_types.SketchMeta, meta_contents,p='meta.json')
    return meta


def str_to_type(ttype):
    if ttype in ['str','list','dict']:
        return eval(ttype)
    ftype = 'sketch_types.' + ttype if 'sketch_types.' not in ttype else ttype
    return eval(ftype)


def js_to_py_dict(ft, js, d, p):
    if 'Dict' not in ft:
        return js
    else:
        keytype, valtype = ft.split('Dict[')[1].replace(']', '').split(',')
        keytype = str_to_type(keytype)
        valtype = str_to_type(valtype)

        dn = {}

        for sk, sv in js.items():
            # print(valtype)
            skk = keytype(sk)
            dn[skk] = js_to_py(valtype, sv, d=d + 1, p=p + '.' + sk)

        return dn


def js_to_py(cls, js, d=0, p=''):
    if issubclass(cls, dict):
        return js_to_py_dict(str(cls),js,d,p)
    elif cls is list:
        ret = []
    else:
        ret = cls()

        for k, v in ret.__dict__.items():
            # print('>',k,v)
            ft = get_type(cls.__name__, k)
            # print(k, 'TYPE', ft)

            prop = p + '.' + k
            if k in js:
                vn = js[k]
                if do_types_match(v, vn):
                    ret.__dict__[k] = vn
                    print('\t' * d + 'COPY', k)
                else:
                    # print(v,vn)
                    if 'Dict[' in ft:
                        if type(vn) is dict:
                            ret.__dict__[k] = js_to_py_dict(ft, vn, d=d + 1, p=prop)
                        else:
                            print('Couldnt match property %s to type %s' % (prop, ft))
                        continue
                    if 'List[' in ft:
                        if type(vn) is list:
                            print('LIST', vn)
                        continue
                    ret.__dict__[k] = js_to_py(str_to_type(ft), vn, d=d + 1, p=prop)
            else:
                print('Couldnt find required property %s' % prop)
    return ret


def do_types_match(obj1, obj2):
    t1 = type(obj1)
    t2 = type(obj2)

    if t1 != t2:
        return False

    if t1 is list:
        if min(len(obj1), len(obj2)) == 0:
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
    meta = js_to_py(sketch_types.SketchDocument, doc_contents,p='doc.json')
    return meta