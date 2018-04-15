# python-sketch-api
Python API to access and modify files from the "Sketch" software (https://www.sketchapp.com/), based on a Python object structure with typing hints.
Allows reading binary "plists", and consequently allows you to query information about text layers!

Includes all relevant data, even metadata and saving information.


# Examples

## Writing

    main_file = SketchFile.from_file('Icons.sketch')

    symbol_hello = main_file.search_symbols_by_name('HALLO')[0]
    symbol_comp = main_file.search_symbols_by_name('Comp')[0]
    symbol_add = main_file.search_symbols_by_name('Add')[0]

    for s in [symbol_hello, symbol_comp, symbol_add]:
        print(s.name, s.do_objectID, s.symbolID, s.originalObjectID)

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

    pts = [sketch_types.Point(300, 200), sketch_types.Point(500,200), sketch_types.Point(50,23)]
    l_path = sketch_types.SJShapePathLayer.create('Test Path', pts)

    test_artboard.add_layer(l_path)

    # source_str = sketch_io.PyToSketch.write(test_page)

    print()

    main_file.save_to('created.sketch')

## Reading


    file = SketchFile.from_file('MyFile.sketch')


    file.sketch_pages

    [<sketch_types.SketchPage at 0x10d64f908>,
     <sketch_types.SketchPage at 0x10d64fb70>,
     <sketch_types.SketchPage at 0x10d658e80>,
     <sketch_types.SketchPage at 0x10d656128>,
     <sketch_types.SketchPage at 0x10f03a4e0>,
     <sketch_types.SketchPage at 0x10f09f470>,
     <sketch_types.SketchPage at 0x10f0b07b8>,
     <sketch_types.SketchPage at 0x10d6560f0>,
     <sketch_types.SketchPage at 0x10f167da0>,
     <sketch_types.SketchPage at 0x10f239ba8>,
     <sketch_types.SketchPage at 0x10f31eeb8>,
     <sketch_types.SketchPage at 0x10f525748>,
     <sketch_types.SketchPage at 0x10f52a278>]

    file.sketch_pages[0].layers[1]
    Out[4]: <sketch_types.SJTextLayer at 0x10d64fdd8>

    file.sketch_pages[0].layers[1].attributedString.get_font_family()
    Out[5]: 'OpenSans-Bold'

    file.sketch_document.userInfo
    Out[7]: {'com.invisionlabs.sync': {'metadata': '{"hasSynced":0,"hasProjectIdChanged":0,"projectId":10489170,"publicLink":"","resolution":2,"syncAll":false}'}}

    file.sketch_document.assets.colors
    Out[8]: 
    [<sketch_types.SJColor at 0x10d6bc2e8>,
     <sketch_types.SJColor at 0x10d6bc358>,
     <sketch_types.SJColor at 0x10d6bc390>,
     <sketch_types.SJColor at 0x10d6bc4e0>]

    file.sketch_meta.pagesAndArtboards[file.sketch_pages[0].do_objectID].name
    Out[13]: '- Introduction v0.3.0'
