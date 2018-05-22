import math

import base64
import secrets
from biplist import readPlistFromString, writePlistToString
from enum import Enum
from typing import NewType, Union, List, Dict

from . import sketch_api

SJObjectId = NewType('SJObjectId', str)


def get_object_id():
    p = '00CC4CF3-9934-4ED2-9A53-5DD12A47F9B7'.split('-')
    o = []
    for part in p:
        x = int(len(part) / 2)
        o.append(secrets.token_hex(x))

    return '-'.join(o).upper()


class SJIDBase:
    def __init__(self):
        self.do_objectID: SJObjectId = None  # get_object_id()


# Rect encoded as test_artboard string, ie {{0, 0}, {10, 30}}
SJStringRect = NewType('SJStringRect', str)


class SJRect(SJIDBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'rect'
        self.constrainProportions: bool = False
        self.x: float = 0
        self.y: float = 0
        self.width: float = 300
        self.height: float = 300


class SJColorNoClass(SJIDBase):
    def __init__(self, r=0.0, g=0.0, b=0.0, a=1.0):
        super().__init__()
        self.red: float = r
        self.green: float = g
        self.blue: float = b
        self.alpha: float = a


class SJColor(SJColorNoClass):
    def __init__(self, r=0.0, g=0.0, b=0.0, a=1.0):
        super().__init__(r, g, b, a)
        self._class: str = 'color'


class SJColorPalette:
    WHITE = SJColor(r=1.0, g=1.0, b=1.0)
    BLACK = SJColor(r=0, g=0, b=0)


class ResizingType(Enum):
    Stretch = 0
    PinToCorner = 1
    ResizeObject = 2
    FloatInPlace = 3


class LayerListExpandedType(Enum):
    Collapsed = 0
    ExpandedTemp = 1
    Expanded = 2


# https://github.com/turbobabr/sketch-constants/blob/master/src/index.js
class FillTypeEnum(Enum):
    Solid = 0
    Gradient = 1
    Pattern = 4
    Noise = 5


class GradientTypeEnum(Enum):
    Linear = 0
    Radial = 1
    Circular = 2


class PatternFillTypeEnum(Enum):
    Tile = 0
    Fill = 1
    Stretch = 2
    Fit = 3


class NoiseFillTypeEnum(Enum):
    Original = 0
    Black = 1
    White = 2
    Color = 3


class BorderLineCapStyle(Enum):
    Butt = 0
    Round = 1
    Square = 2


class BorderLineJoinStyle(Enum):
    Miter = 0
    Round = 1
    Bevel = 2


class LineDecorationTypeEnum(Enum):
    _None = 0
    OpenedArrow = 1
    ClosedArrow = 2
    Bar = 3


class BlurTypeEnum(Enum):
    GaussianBlur = 0
    MotionBlur = 1
    ZoomBlur = 2
    BackgroundBlur = 3


class BorderPositionEnum(Enum):
    Center = 0
    Inside = 1
    Outside = 2


class MaskModeEnum(Enum):
    Outline = 0
    Alpha = 1


class BooleanOperation(Enum):
    _None = -1
    Union = 0
    Subtract = 1
    Intersect = 2
    Difference = 3


class BlendModeEnum(Enum):
    Normal = 0
    Darken = 1
    Multiply = 2
    ColorBurn = 3
    Lighten = 4
    Screen = 5
    ColorDodge = 6
    Overlay = 7
    SoftLight = 8
    HardLight = 9
    Difference = 10
    Exclusion = 11
    Hue = 12
    Saturation = 13
    Color = 14
    Luminosity = 15


class ExportOptionsFormat(Enum):
    PNG = 'png'
    JPG = 'jpg'
    TIFF = 'tiff'
    PDF = 'pdf'
    EPS = 'eps'
    SVG = 'svg'


class ExportFormat:
    def __init__(self):
        self._class: str = 'exportFormat'
        self.absoluteSize: int = 1
        self.fileFormat: ExportOptionsFormat = 'png'
        self.name: str = ''
        self.namingScheme: int = 0
        self.scale: int = 1
        self.visibleScaleType: int = 0


class TextAlignmentEnum(Enum):
    Left = 0
    Right = 1
    Center = 2
    Justified = 3


class CurveMode(Enum):
    Straight = 1
    Mirrored = 2
    Disconnected = 4
    Asymmetric = 3


class SJBorder:
    def __init__(self):
        self._class: str = 'border'
        self.isEnabled: bool = True
        self.color: SJColor = SJColorPalette.BLACK
        self.fillType: FillTypeEnum = None
        self.position: BorderPositionEnum = None
        self.thickness: int = None
        self.contextSettings: SJContextSettings = None
        self.offsetX: int = None
        self.offsetY: int = None
        self.spread: int = None
        self.blurRadius: int = None


FloatList = List[float]


class SJBorderOptions(SJIDBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'borderOptions'
        self.isEnabled: bool = True
        self.dashPattern: FloatList = []
        self.lineCapStyle: BorderLineCapStyle = BorderLineCapStyle.Round
        self.lineJoinStyle: BorderLineJoinStyle = BorderLineJoinStyle.Round


class SJFill:
    def __init__(self):
        self._class: str = 'fill'
        self.isEnabled: bool = True
        self.color: SJColor = SJColorPalette.WHITE
        self.fillType: FillTypeEnum = FillTypeEnum.Solid
        self.image: SJImageDataReference = None
        self.noiseIndex: float = 0
        self.noiseIntensity: float = 0
        self.patternFillType: PatternFillTypeEnum = PatternFillTypeEnum.Fill
        self.patternTileScale: float = 0
        self.gradient: SJGradient = None
        self.do_objectID: SJObjectId = None


class SJGradientStop:
    def __init__(self):
        self._class: str = 'gradientStop'
        self.position: float = 0
        self.color: SJColor = SJColorPalette.WHITE


class SJGradient:
    def __init__(self):
        self._class: str = 'gradient'
        self.elipseLength: int = 0
        setattr(self, 'from', '{0, 0}')
        # self.from: PointString = None
        self.to: PointString = '{0, 0}'
        self.gradientType: GradientTypeEnum = GradientTypeEnum.Linear
        self.stops: List[SJGradientStop] = []


class SJContextSettings(SJIDBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'graphicsContextSettings'
        self.blendMode: BlendModeEnum = BlendModeEnum.Color
        self.opacity: float = 1.0


class SJShadow:
    def __init__(self):
        self._class: str = 'shadow'
        self.isEnabled: bool = None
        self.blurRadius: float = None
        self.color: SJColor = None
        self.contextSettings: SJContextSettings = SJContextSettings()
        self.offsetX: float = None
        self.offsetY: float = None
        self.spread: float = None


class SJInnerShadow(SJShadow):
    def __init__(self):
        super().__init__()
        self._class: str = 'innerShadow'


SJBorderList = List[SJBorder]
SJShadowList = List[SJShadow]
SJInnerShadowList = List[SJInnerShadow]
SJFillList = List[SJFill]


class SJBlur(SJIDBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'blur'
        self.isEnabled: bool = True
        self.center: PointString = '{0, 0}'
        self.motionAngle: float = 0.0
        self.radius: int = 0
        self.type: BlurTypeEnum = BlurTypeEnum.GaussianBlur


class SJColorControls(SJIDBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'colorControls'
        self.isEnabled: bool = True
        self.brightness: int = 0
        self.contrast: int = 0
        self.hue: int = 0
        self.saturation: int = 0


class SJStyle:
    def __init__(self):
        self._class: str = 'style'
        self.sharedObjectID: str = None
        self.borderOptions: SJBorderOptions = None
        self.borders: SJBorderList = None
        self.shadows: SJShadowList = None
        self.innerShadows: SJInnerShadowList = None
        self.fills: SJFillList = None
        self.textStyle: SJTextStyle = None
        self.miterLimit: int = 10
        self.startDecorationType: LineDecorationTypeEnum = LineDecorationTypeEnum._None
        self.endDecorationType: LineDecorationTypeEnum = LineDecorationTypeEnum._None
        self.blur: SJBlur = None
        self.contextSettings: SJContextSettings = None
        self.colorControls: SJColorControls = None
        self.do_objectID: SJObjectId = None


class SJTextStyleAttribute:
    def __init__(self):
        self.MSAttributedStringFontAttribute: SJFontDescriptor = None
        self.kerning: int = None
        self.MSAttributedStringColorAttribute: SJColor = None
        self.paragraphStyle: SJParagraphStyle = None
        self.MSAttributedStringColorDictionaryAttribute: SJColorNoClass = None
        self.MSAttributedStringTextTransformAttribute: int = None
        self.strikethroughStyle: int = None
        self.underlineStyle: int = None


class SJTextStyle(SJIDBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'textStyle'
        self.verticalAlignment: TextAlignmentEnum = 0  # TODO enum?
        self.encodedAttributes: SJTextStyleAttribute = SJTextStyleAttribute()


class SJSharedStyle(SJIDBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'sharedStyle'
        self.name: str = None
        self.value: SJStyle = None


SJSharedStyleList = List[SJSharedStyle]
SJSharedTextStyleList = List[SJSharedStyle]


class SJSharedTextStyleContainer:
    def __init__(self):
        self._class: str = 'sharedTextStyleContainer'
        self.objects: SJSharedStyleList = []


class SJSharedStyleContainer:
    def __init__(self):
        self._class: str = 'sharedStyleContainer'
        self.objects: SJSharedTextStyleList = []


class SJSharedSymbolContainer:
    def __init__(self):
        self._class: str = 'symbolContainer'
        self.objects: List = []  # TODO not clear


class ExportOptions(SJIDBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'exportOptions'
        self.exportFormats: List[ExportFormat] = []
        self.includedLayerIds: List = []
        self.layerOptions: int = 0
        self.shouldTrim: bool = False


class RulerData(SJIDBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'rulerData'
        self.base: int = 0
        self.guides: FloatList = []


class SJImageDataReference_data:
    def __init__(self):
        self._data: str = None


class SJImageDataReference_sha1:
    def __init__(self):
        self._data: str = None


class SJImageDataReference:
    def __init__(self):
        self._class: str = 'MSJSONOriginalDataReference'
        self._ref: str = ''
        self._ref_class: str = 'MSImageData'
        self.data: SJImageDataReference_data = None
        self.sha1: SJImageDataReference_sha1 = None


PointString = NewType('PointString', str)


class SJCurvePoint:
    @staticmethod
    def create(x, y):
        p = SJCurvePoint()
        pstring = '{%f, %f}' % (x, y)
        p.curveFrom = pstring
        p.curveTo = pstring
        p.point = pstring
        return p

    def __init__(self):
        self._class: str = 'curvePoint'
        self.do_objectID: SJObjectId = None
        self.cornerRadius: float = 0.0
        self.curveFrom: PointString = '{0, 0}'
        self.curveMode: CurveMode = CurveMode.Straight
        self.curveTo: PointString = '{0, 0}'
        self.hasCurveFrom: bool = True
        self.hasCurveTo: bool = True
        self.point: PointString = '{0, 0}'


SJCurvePointList = List[SJCurvePoint]


class _SJLayerBase(SJIDBase):
    def __init__(self):
        super().__init__()
        self.name: str = ''
        self.nameIsFixed: bool = False
        self.isVisible: bool = True
        self.isLocked: bool = False
        self.layerListExpandedType: LayerListExpandedType = LayerListExpandedType.Collapsed
        self.hasClickThrough: bool = None
        self.layers: SJLayerList = None
        self.style: SJStyle = None
        self.isFlippedHorizontal: bool = False
        self.isFlippedVertical: bool = False
        self.rotation: int = 0
        self.shouldBreakMaskChain: bool = False
        self.resizingType: ResizingType = ResizingType.Stretch
        self.exportOptions: ExportOptions = ExportOptions()
        self.includeInCloudUpload: bool = None
        self.backgroundColor: SJColor = None
        self.hasBackgroundColor: bool = None
        self.horizontalRulerData: RulerData = None
        self.verticalRulerData: RulerData = None
        self.includeBackgroundColorInExport: bool = None
        self.resizingConstraint: int = 63
        self.frame: SJRect = SJRect()
        self.originalObjectID: SJObjectId = None
        self.userInfo: dict = None
        self.resizesContent: bool = None
        self.isFlowHome: bool = None
        self.layout: SJLayoutGrid = None

    def add_layer(self, r):
        # sketch_api._link_to_parent(r, self)
        if self.layers is None:
            self.layers = []

        self.layers.append(r)

    def remove_layer(self, r):
        self.layers.remove(r)

    def get_layer_by_type(self, class_str):
        return [x for x in self.layers if x._class == class_str]


class _SJArtboardBase(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self.frame: SJRect = SJRect()


class SJSimpleGrid(SJIDBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'simpleGrid'
        self.isEnabled: bool = True
        self.gridSize: int = 0
        self.thickGridTimes: int = 0


class SJSymbolMaster(_SJArtboardBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'symbolMaster'
        self.includeBackgroundColorInInstance: bool = False
        self.symbolID: SJObjectId = ''
        self.changeIdentifier: int = 0
        self.grid: SJSimpleGrid = None

    def find_text_layer_by_text(self, param, file):
        path = []

        def search(layers):
            if layers is None:
                return
            for l in layers:
                if l._class == 'text' and param in l.get_text():
                    return l
                if l._class == 'symbolInstance':
                    sid = l.symbolID
                    new_reference = file.get_symbol_by_id(sid)
                    res = search(new_reference.layers)
                    if res:
                        path.append(l)
                        return res
                if l.layers is not None and len(l.layers) > 0:
                    res = search(l.layers)
                    if res:
                        return res

        res = search(self.layers)
        path.append(res)
        return path

    def find_all_text_layers(self, file):
        p = []

        def search(layers, path):
            opath = path.copy()
            if layers is None:
                return
            for l in layers:
                path = opath.copy()
                path.append(l)
                if l._class == 'text':
                    yield path
                if l._class == 'symbolInstance':
                    sid = l.symbolID
                    new_reference = file.get_symbol_by_id(sid)
                    yield from search(new_reference.layers, path)
                if l.layers is not None and len(l.layers) > 0:
                    yield from search(l.layers, path)

        yield from search(self.layers, p)


SJSymbolInstanceLayer_overrides = Dict[SJObjectId, Union[str, SJImageDataReference, dict]]


class SJLayoutGrid(SJIDBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'layoutGrid'
        self.isEnabled: bool = True
        self.columnWidth: float = 0
        self.drawHorizontal: bool = False
        self.drawHorizontalLines: bool = False
        self.drawVertical: bool = False
        self.gutterHeight: int = 0
        self.gutterWidth: int = 0
        self.guttersOutside: bool = False
        self.horizontalOffset: int = 0
        self.numberOfColumns: int = 0
        self.rowHeightMultiplication: int = 0
        self.totalWidth: int = 0


class SJOverride:
    def __init__(self):
        self._class: str = 'overrideValue'
        self.overrideName: SJObjectId = ''
        self.value: str = ''
        self.do_objectID: SJObjectId = None


class SJSymbolInstanceLayer(_SJLayerBase):
    @staticmethod
    def create(symbol: SJSymbolMaster, x, y):
        l = SJSymbolInstanceLayer()
        l.do_objectID = get_object_id()
        l.symbolID = symbol.symbolID
        l.name = symbol.name
        l.frame.x = x
        l.frame.y = y
        l.frame.width = symbol.frame.width
        l.frame.height = symbol.frame.height
        return l

    def add_symbol_override(self, target_symbol_id, new_symbol: SJSymbolMaster):
        ov = SJOverride()
        ov.do_objectID = get_object_id()

        ov.overrideName = target_symbol_id + '_symbolID'

        ov.value = new_symbol.symbolID
        self.overrideValues.append(ov)

        self.overrides[target_symbol_id] = {
            'symbolID': new_symbol.symbolID
        }

    def add_text_override(self, target_text_ids: List[_SJLayerBase], new_text: str):
        ov = SJOverride()
        ov.do_objectID = get_object_id()

        target_text_ids = [t for t in target_text_ids if t._class in ['symbolInstance', 'text']]

        key = '/'.join([t.do_objectID for t in target_text_ids]) + '_stringValue'

        ov.overrideName = key
        ov.value = new_text
        self.overrideValues.append(ov)

        def get_dict(ids):
            if len(ids) == 1:
                return {ids[0].do_objectID: new_text}

            ret = {}

            i = ids.pop(0)
            ret[i.do_objectID] = get_dict(ids)
            return ret

        if len(target_text_ids) == 1:
            self.overrides[target_text_ids[0].do_objectID] = new_text
        else:
            main_id = target_text_ids.pop(0).do_objectID
            d = get_dict(target_text_ids)
            self.overrides[main_id] = d

    def __init__(self):
        super().__init__()
        self._class: str = 'symbolInstance'

        self.horizontalSpacing: float = 0
        self.verticalSpacing: float = 0
        self.masterInfluenceEdgeMinXPadding: float = None
        self.masterInfluenceEdgeMaxXPadding: float = None
        self.masterInfluenceEdgeMinYPadding: float = None
        self.masterInfluenceEdgeMaxYPadding: float = None
        self.symbolID: SJObjectId = ''

        self.overrides: SJSymbolInstanceLayer_overrides = {}
        self.overrideValues: List[SJOverride] = []
        self.scale: int = 1

        self.changeIdentifier: int = None
        self.includeBackgroundColorInInstance: bool = None

        # TODO investigate, maybe this occurs elsewhere
        self.path: SJPath = None


class SJPresetDict:
    def __init__(self):
        self.height: int = None
        self.width: int = None
        self.offersLandScapeVariant: int = None  # TODO enum?
        self.name: str = None
        self.allowResizedMatching: int = None


class SJArtboardLayer(_SJArtboardBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'artboard'
        self.presetDictionary: SJPresetDict = None

    @staticmethod
    def create(name, w, h):
        a = SJArtboardLayer()
        a.do_objectID = get_object_id()
        a.name = name
        a.frame.width = w
        a.frame.height = h

        return a


class SJTextLayer(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'text'
        self.attributedString: MSAttributedString = MSAttributedString()
        self.glyphBounds: SJStringRect = '{}{}'
        self.lineSpacingBehaviour: int = 0
        self.dontSynchroniseWithSymbol: bool = False
        self.automaticallyDrawOnUnderlyingPath: bool = False
        self.textBehaviour: int = 0

    @staticmethod
    def create(name: str, x, y, width, height, text: str = '', font_family: str = None, font_size: float = None):
        l_text = SJTextLayer()
        l_text.name = name
        l_text.do_objectID = get_object_id()
        l_text.lineSpacingBehaviour = 2
        l_text.frame.width = width
        l_text.frame.height = height
        l_text.frame.x = x
        l_text.frame.y = y
        l_text.set_text(text)

        l_text.glyphBounds = '{{0, 0}, {120, 20}}'

        if font_family is not None or font_size is not None:
            l_text.set_font(font_family, font_size)

        return l_text

    def get_color(self):
        return self.attributedString.get_color()

    def set_color(self, color: SJColor):
        self.attributedString.set_color(color)

    def get_font(self):
        return self.attributedString.get_font()

    def set_font(self, font_family: str = None, font_size: float = 12):
        return self.attributedString.set_font(font_size=font_size, font_family=font_family)

    def get_text(self):
        return self.attributedString.string

    def set_text(self, text: str):
        self.attributedString.set_text(text)


class SJGroupLayer(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'group'

    @staticmethod
    def create(name: str, layer_list: List[_SJLayerBase]):
        assert len(layer_list) >= 1, 'Group layers need at least one sub-layers'

        main_group = SJGroupLayer()
        main_group.name = name

        min_x = math.inf
        min_y = math.inf
        max_x = -math.inf
        max_y = -math.inf

        for l in layer_list:
            x = l.frame.x
            y = l.frame.y

            if x < min_x:
                min_x = x
            if y < min_y:
                min_y = y

            x += l.frame.width
            y += l.frame.height

            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y

        main_group.frame.x = min_x
        main_group.frame.y = min_y
        main_group.frame.width = max_x - min_x
        main_group.frame.height = max_y - min_y
        main_group.layers = []

        for l in layer_list:
            l.frame.x -= min_x
            l.frame.y -= min_y

            main_group.layers.append(l)

        # sketch_api._link_to_parent(main_group.layers, main_group)

        return main_group


class SJShapeGroupLayer(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'shapeGroup'

        self.hasClippingMask: bool = False
        self.windingRule: int = 0  # TODO enum
        self.clippingMaskMode: MaskModeEnum = MaskModeEnum.Alpha

    @staticmethod
    def create(name, x, y, w, h):
        r = SJShapeGroupLayer()
        r.do_objectID = get_object_id()
        r.name = name
        r.isVisible = True
        r.frame = SJRect()
        r.frame.x = x
        r.frame.y = y
        r.frame.width = w
        r.frame.height = h

        b = SJBorder()
        b.fillType = FillTypeEnum.Solid
        b.isEnabled = True
        b.position = BorderPositionEnum.Inside
        b.thickness = 1
        b.color = SJColorPalette.BLACK

        r.style.borders = [b]
        return r


class SJShapeLayer(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = None
        self.points: SJCurvePointList = []
        self.edited: bool = True
        self.isClosed: bool = True
        self.pointRadiusBehaviour: int = 0
        self.booleanOperation: BooleanOperation = BooleanOperation.Union
        self.fixedRadius: int = None
        self.hasConvertedToNewRoundCorners: bool = None


class SJShapeRectangleLayer(SJShapeLayer):
    @staticmethod
    def create(name, x, y, w, h) -> SJShapeGroupLayer:
        r = SJShapeGroupLayer.create(name, x, y, w, h)

        l = SJShapeRectangleLayer()
        l.do_objectID = get_object_id()
        l.frame.x = 0
        l.frame.y = 0
        l.frame.width = w
        l.frame.height = h
        l.path = SJPath()
        l.path.pointRadiusBehaviour = 1

        p1 = SJCurvePoint.create(0, 0)
        l.path.points.append(p1)

        p1 = SJCurvePoint.create(1, 0)
        l.path.points.append(p1)

        p1 = SJCurvePoint.create(1, 1)
        l.path.points.append(p1)

        p1 = SJCurvePoint.create(0, 1)
        l.path.points.append(p1)

        l.points = l.path.points

        r.layers.append(l)

        # sketch_api._link_to_parent(r.layers, r)
        return r

    def __init__(self):
        super().__init__()
        self._class: str = 'rectangle'
        self.path: SJPath = None


class SJShapeOvalLayer(SJShapeLayer):
    def __init__(self):
        super().__init__()
        self._class: str = 'oval'
        self.path: SJPath = None


class Point:
    @staticmethod
    def from_str(s: PointString):
        x, y = s.replace('{', '').replace('}', '').split(',')
        return float(x), float(y)

    def __init__(self, x: float, y: float):
        self.x: float = x
        self.y: float = y

    def to_str(self) -> PointString:
        return PointString('{%f, %f}' % (self.x, self.y))


class SJShapePathLayer(SJShapeLayer):
    def __init__(self):
        super().__init__()
        self._class: str = 'shapePath'
        self.path: SJPath = None

    @staticmethod
    def create(name: str, points: List[Point]):
        min_x = math.inf
        max_x = -math.inf
        min_y = math.inf
        max_y = -math.inf

        for pt in points:
            min_x = min(min_x, pt.x)
            max_x = max(max_x, pt.x)
            min_y = min(min_y, pt.y)
            max_y = max(max_y, pt.y)

        w = max_x - min_x
        h = max_y - min_y

        group_layer = SJShapeGroupLayer.create(name, min_x, min_y, w, h)

        path_layer = SJShapePathLayer()
        path_layer.name = name
        path_layer.frame.x = 0
        path_layer.frame.y = 0

        path_layer.frame.width = w
        path_layer.frame.height = h

        path_layer.path = SJPath()

        l = len(points) - 1

        for i, pt in enumerate(points):
            x = (pt.x - min_x) / w
            y = (pt.y - min_y) / h
            curve_point = SJCurvePoint.create(x, y)
            curve_point.hasCurveFrom = i < l
            curve_point.hasCurveTo = i > 0
            path_layer.path.points.append(curve_point)

        path_layer.points = path_layer.path.points

        group_layer.layers.append(path_layer)

        # sketch_api._link_to_parent(group_layer.layers, group_layer)

        return group_layer


EncodedBase64BinaryPlist = NewType('EncodedBase64BinaryPlist', str)


class SJPath:
    def __init__(self):
        self._class: str = 'path'
        self.isClosed: bool = True
        self.points: SJCurvePointList = []
        self.pointRadiusBehaviour: int = 0


class SJTabStop:
    def __init__(self):
        self._class: str = 'textTab'
        self.alignment: TextAlignmentEnum = TextAlignmentEnum.Left
        self.location: int = None
        self.options: dict = None


class SJParagraphStyle:
    def __init__(self):
        self._class: str = 'paragraphStyle'
        self.alignment: TextAlignmentEnum = TextAlignmentEnum.Left
        self.allowsDefaultTighteningForTruncation: int = None
        self.minimumLineHeight: int = None
        self.maximumLineHeight: int = None
        self.tabStops: List[SJTabStop] = None


class SJFontDescriptorAttributes:
    def __init__(self):
        self.name: str = None
        self.size: float = None


class SJFontDescriptor:
    def __init__(self):
        self._class: str = 'fontDescriptor'
        self.attributes: SJFontDescriptorAttributes = SJFontDescriptorAttributes()


class KeyValueArchive:

    def __init__(self):
        sample = 'YnBsaXN0MDDUAQIDBAUGaWpYJHZlcnNpb25YJG9iamVjdHNZJGFyY2hpdmVyVCR0b3ASAAGGoK8QIAcIDxAeHyAhIiotMzY6QkN' \
                 'ERUZKTlpbXF1eX2BhYmRlVSRudWxs0wkKCwwNDlhOU1N0cmluZ1YkY2xhc3NcTlNBdHRyaWJ1dGVzgAKAH4ADXmphaGJsYmhkYm' \
                 'hkc2lq0xESChMYHVdOUy5rZXlzWk5TLm9iamVjdHOkFBUWF4AEgAWABoAHpBkaGxyACIAMgBSAHoAdXxAQTlNQYXJhZ3JhcGhTd' \
                 'HlsZV8QH01TQXR0cmlidXRlZFN0cmluZ0ZvbnRBdHRyaWJ1dGVfECpNU0F0dHJpYnV0ZWRTdHJpbmdDb2xvckRpY3Rpb25hcnlB' \
                 'dHRyaWJ1dGVWTlNLZXJu1CMKJCUmJygoWk5TVGFiU3RvcHNcTlNUZXh0QmxvY2tzW05TVGV4dExpc3RzgACAC4AJgAnSEgorLKC' \
                 'ACtIuLzAxWiRjbGFzc25hbWVYJGNsYXNzZXNXTlNBcnJheaIwMlhOU09iamVjdNIuLzQ1XxAQTlNQYXJhZ3JhcGhTdHlsZaI0Mt' \
                 'IKNzg5XxAaTlNGb250RGVzY3JpcHRvckF0dHJpYnV0ZXOAE4AN0xESCjs+QaI8PYAOgA+iP0CAEIARgBJfEBNOU0ZvbnRTaXplQ' \
                 'XR0cmlidXRlXxATTlNGb250TmFtZUF0dHJpYnV0ZSNAMAAAAAAAAF8QEE9wZW5TYW5zLVJlZ3VsYXLSLi9HSF8QE05TTXV0YWJs' \
                 'ZURpY3Rpb25hcnmjR0kyXE5TRGljdGlvbmFyedIuL0tMXxAQTlNGb250RGVzY3JpcHRvcqJNMl8QEE5TRm9udERlc2NyaXB0b3L' \
                 'TERIKT1QdpFBRUlOAFYAWgBeAGKRVVldYgBmAGoAbgByAHVNyZWRVYWxwaGFUYmx1ZVVncmVlbiM/0BAQEBvrlCM/8AAAAAAAAC' \
                 'M/1NTU1NrClyM/0tLS0t4kXNIuL0ljokkyEADSLi9mZ18QEk5TQXR0cmlidXRlZFN0cmluZ6JoMl8QEk5TQXR0cmlidXRlZFN0c' \
                 'mluZ18QD05TS2V5ZWRBcmNoaXZlctFrbFRyb290gAEACAARABoAIwAtADIANwBaAGAAZwBwAHcAhACGAIgAigCZAKAAqACzALgA' \
                 'ugC8AL4AwADFAMcAyQDLAM0AzwDiAQQBMQE4AUEBTAFZAWUBZwFpAWsBbQFyAXMBdQF6AYUBjgGWAZkBogGnAboBvQHCAd8B4QH' \
                 'jAeoB7QHvAfEB9AH2AfgB+gIQAiYCLwJCAkcCXQJhAm4CcwKGAokCnAKjAqgCqgKsAq4CsAK1ArcCuQK7Ar0CvwLDAskCzgLUAt' \
                 '0C5gLvAvgC/QMAAwIDBwMcAx8DNANGA0kDTgAAAAAAAAIBAAAAAAAAAG0AAAAAAAAAAAAAAAAAAANQ'

        self._archive: EncodedBase64BinaryPlist = EncodedBase64BinaryPlist(sample)
        self._raw: dict = None  # cached copy of dict

    def get_archive(self):
        if hasattr(self, '_raw') and self._raw is not None:
            return self._raw

        bstr = base64.b64decode(self._archive)
        a = readPlistFromString(bstr)
        self._raw = a
        return a

    def set_val(self, k: int, v):
        archive = self.get_archive()
        archive['$objects'][k] = v
        dt = writePlistToString(archive)
        bstr = base64.b64encode(dt)
        self._archive = bstr

    def get_val(self, val: int):
        return self.get_archive()['$objects'][val]


NSColorArchive = NewType('NSColorArchive', KeyValueArchive)

_ = [
    {
        '_class': 'stringAttribute',
        'location': 0,
        'length': 1,
        'attributes': {
            'MSAttributedStringColorAttribute': {
                '_class': 'color',
                'alpha': 1,
                'blue': 0,
                'green': 0,
                'red': 0
            },
            'MSAttributedStringFontAttribute': {
                '_class': 'fontDescriptor',
                'attributes': {
                    'name': 'sovantaDTBETA-Regular',
                    'size': 16
                }
            }
        }
    },
    {
        '_class': 'stringAttribute',
        'location': 1,
        'length': 1,
        'attributes': {
            'MSAttributedStringFontAttribute': {
                '_class': 'fontDescriptor',
                'attributes': {
                    'name': 'sovantaDTBETA-Regular',
                    'size': 16
                }
            },
            'MSAttributedStringColorAttribute': {
                '_class': 'color',
                'alpha': 1,
                'blue': 0,
                'green': 0,
                'red': 0
            },
            'kerning': 0.009600000000000001
        }
    },
    {
        '_class': 'stringAttribute',
        'location': 2,
        'length': 1,
        'attributes': {
            'MSAttributedStringColorAttribute': {
                '_class': 'color',
                'alpha': 1,
                'blue': 0,
                'green': 0,
                'red': 0
            },
            'MSAttributedStringFontAttribute': {
                '_class': 'fontDescriptor',
                'attributes': {
                    'name': 'sovantaDTBETA-Regular',
                    'size': 16
                }
            }
        }
    },
    {
        '_class': 'stringAttribute',
        'location': 3,
        'length': 1,
        'attributes': {
            'MSAttributedStringFontAttribute': {
                '_class': 'fontDescriptor',
                'attributes': {
                    'name': 'sovantaDTBETA-Regular',
                    'size': 16
                }
            },
            'MSAttributedStringColorAttribute': {
                '_class': 'color',
                'alpha': 1,
                'blue': 0,
                'green': 0,
                'red': 0
            },
            'kerning': 0.0112
        }
    },
    {
        '_class': 'stringAttribute',
        'location': 4,
        'length': 2,
        'attributes': {
            'MSAttributedStringColorAttribute': {
                '_class': 'color',
                'alpha': 1,
                'blue': 0,
                'green': 0,
                'red': 0
            },
            'MSAttributedStringFontAttribute': {
                '_class': 'fontDescriptor',
                'attributes': {
                    'name': 'sovantaDTBETA-Regular',
                    'size': 16
                }
            }
        }
    },
    {
        '_class': 'stringAttribute',
        'location': 6,
        'length': 1,
        'attributes': {
            'MSAttributedStringFontAttribute': {
                '_class': 'fontDescriptor',
                'attributes': {
                    'name': 'sovantaDTBETA-Regular',
                    'size': 16
                }
            },
            'MSAttributedStringColorAttribute': {
                '_class': 'color',
                'alpha': 1,
                'blue': 0,
                'green': 0,
                'red': 0
            },
            'kerning': 0.0112
        }
    },
    {
        '_class': 'stringAttribute',
        'location': 7,
        'length': 8,
        'attributes': {
            'MSAttributedStringColorAttribute': {
                '_class': 'color',
                'alpha': 1,
                'blue': 0,
                'green': 0,
                'red': 0
            },
            'MSAttributedStringFontAttribute': {
                '_class': 'fontDescriptor',
                'attributes': {
                    'name': 'sovantaDTBETA-Regular',
                    'size': 16
                }
            }
        }
    }
]


class MSStringAttributeField:
    def __init__(self):
        self.MSAttributedStringColorAttribute: SJColor = None
        self.MSAttributedStringFontAttribute: SJFontDescriptor = None
        self.paragraphStyle: SJParagraphStyle = None
        self.kerning: int = None
        self.MSAttributedStringTextTransformAttribute: int = None
        self.strikethroughStyle: int = None  # TODO ENUM
        self.underlineStyle: int = None  # TODO ENUM


class MSStringAttribute:
    def __init__(self):
        self._class: str = 'stringAttribute'
        self.location: int = 0
        self.length: int = 1
        self.attributes: MSStringAttributeField = MSStringAttributeField()


class MSAttributedString:
    def __init__(self):
        self._class: str = 'MSAttributedString'
        # self.archivedAttributedString: KeyValueArchive = KeyValueArchive()
        self.attributes: List[MSStringAttribute] = [MSStringAttribute()]
        self.string: str = None

    def set_text(self,text: str):
        self.string = text
        self.attributes[0].length = len(self.string)

    def set_font(self, font_family: str, font_size: float = 12):
        fD = SJFontDescriptor()
        fD.attributes.name = font_family
        fD.attributes.size = font_size
        self.attributes[0].attributes.MSAttributedStringFontAttribute = fD

    def get_font(self):
        return self.attributes[0].attributes.MSAttributedStringFontAttribute if len(self.attributes) > 0 else None

    def get_color(self):
        return self.attributes[0].attributes.MSAttributedStringColorAttribute if len(self.attributes) > 0 else None

    def set_color(self, color: SJColor):
        self.attributes[0].attributes.MSAttributedStringColorAttribute = color

    def get_alignment(self):
        ps = self.attributes[0].attributes.paragraphStyle
        return ps.alignment if ps is not None else None


class MSJSONFileReference:
    def __init__(self):
        self._class: str = 'MSJSONFileReference'
        self._ref_class: str = 'MSImmutablePage'
        self._ref: str = ''  # i.e. pages/doObjectID


class SJImageLayer(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'bitmap'
        self.clippingMask: SJStringRect = SJStringRect('{{0, 0}, {1, 1}}')
        self.fillReplacesImage: bool = None
        self.image: MSJSONFileReference = None
        self.intendedDPI: int = None


SJLayer = Union[
    SJImageLayer, SJSymbolMaster, SJArtboardLayer, SJTextLayer, SJGroupLayer, SJShapeGroupLayer, SJShapeOvalLayer, SJShapeRectangleLayer, SJShapePathLayer, SJSymbolInstanceLayer]
SJLayerList = List[SJLayer]


class SJImageCollection:
    def __init__(self):
        self._class: str = 'imageCollection'
        self.images: dict = {}  # TODO


SJColorList = List[SJColor]


class SJAssetCollection:
    def __init__(self):
        self._class: str = 'assetCollection'
        self.colors: SJColorList = []
        self.gradients: List[SJGradient] = []  # TODO
        self.images: List = []  # TODO
        self.imageCollection: SJImageCollection = SJImageCollection()


MSJSONFileReferenceList = List[MSJSONFileReference]


# document.json
class SketchDocument(SJIDBase):
    def __init__(self):
        super().__init__()
        # TODO document
        self._parent: sketch_api.SketchFile = None

        self._class: str = 'document'
        self.colorSpace: int = 0
        self.currentPageIndex: int = 0
        self.foreignSymbols: List = []
        self.assets: SJAssetCollection = SJAssetCollection()

        self.layerTextStyles: SJSharedTextStyleContainer = SJSharedTextStyleContainer()
        self.layerStyles: SJSharedStyleContainer = SJSharedStyleContainer()
        self.layerSymbols: SJSharedSymbolContainer = SJSharedSymbolContainer()

        self.foreignLayerStyles: List = []
        self.foreignTextStyles: List = []

        self.pages: MSJSONFileReferenceList = []
        self.userInfo: dict = None  # TODO


# pages/doObjectID.json
class SketchPage(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'page'
        self._parent: sketch_api.SketchFile = None

    def get_ref(self):
        return 'pages/%s' % self.do_objectID

    def add_artboard(self, artboard: SJArtboardLayer):
        self.layers.append(artboard)
        x = self._parent.sketch_meta.pagesAndArtboards[self.do_objectID]
        m = SJArtboardDescription()
        m.name = artboard.name
        # sketch_api._link_to_parent(m, artboard)
        x.artboards[artboard.do_objectID] = m
        return artboard

    def remove_artboard(self, artboard: SJArtboardLayer):
        self.layers.remove(artboard)
        del self._parent.sketch_meta.pagesAndArtboards[self.do_objectID].artboards[artboard.do_objectID]


class SketchUserDataEntry:
    def __init__(self):
        self._parent: sketch_api.SketchFile = None
        self.scrollOrigin: PointString = None
        self.zoomValue: float = None
        self.pageListHeight: int = None
        self.exportableLayerSelection: List[SJObjectId] = None
        self.cloudShare: bool = None  # TODO check true type


class SJArtboardDescription:
    def __init__(self):
        self.name: str = ''


SJPageArtboardMappingEntryDict = Dict[SJObjectId, SJArtboardDescription]


class SJPageArtboardMappingEntry:
    def __init__(self):
        self.name: str = ''
        self.artboards: SJPageArtboardMappingEntryDict = {}


# user.json
SketchUserData = Dict[SJObjectId, SketchUserDataEntry]
SJPageArtboardMapping = Dict[SJObjectId, SJPageArtboardMappingEntry]  # PageID => Artboards


class SketchCreateMeta:
    def __init__(self):
        self.compatibilityVersion: int = 93
        self.build: int = 51160
        self.app: str = 'com.bohemiancoding.sketch3'
        self.autosaved: int = None
        self.variant: str = 'NONAPPSTORE'
        self.commit: str = '3ddf4a853aaf3543a90063fa41305860bd6d6e7a'
        self.version: int = 101
        self.appVersion: str = '49.2'


StrList = List[str]


# meta.json
class SketchMeta(SketchCreateMeta):
    def __init__(self):
        super().__init__()
        self._parent: sketch_api.SketchFile = None
        self.pagesAndArtboards: SJPageArtboardMapping = {}
        self.fonts: StrList = []

        self.autosaved: int = 0
        self.created: SketchCreateMeta = SketchCreateMeta()
        self.saveHistory: StrList = []  # Entries are variant.build
