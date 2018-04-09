# python-sketch-api
Python API to access and modify files from the "Sketch" software (https://www.sketchapp.com/), based on a Python object structure with typing hints.
Allows reading binary "plists", and consequently allows you to query information about text layers!

Includes all relevant data, even metadata and saving information.


CURRENTLY ONLY SUPPORTS READING!


# Examples
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
