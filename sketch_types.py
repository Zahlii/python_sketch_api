import secrets
from enum import Enum

from typing import NewType, Union, List, Dict


class SJRect:
    def __init__(self):
        self._class: str = 'rect'
        self.constrainProportions: bool = False
        self.x: float = 0.0
        self.y: float = 0.0
        self.width: float = 0.0
        self.height: float = 0.0


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
        self.do_objectID: SJObjectId = get_object_id()


SJStringRect = NewType('SJStringRect', str)


class SJColor:
    def __init__(self, r=0.0, g=0.0, b=0.0, a=1.0):
        self._class: str = 'color'
        self.red: float = r
        self.green: float = g
        self.blue: float = b
        self.alpha: float = a


class SJColorPalette:
    WHITE = SJColor(r=255.0, g=255.0, b=255.0)
    BLACK = SJColor(r=0.0, g=0.0, b=0.0)


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
    _None: -1
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
        self.fillType: FillTypeEnum = FillTypeEnum.Solid
        self.position: BorderPositionEnum = BorderPositionEnum.Outside
        self.thickness: float = 1.0


FloatList = List[float]


class SJBorderOptions:
    def __init__(self):
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
        self.noiseIndex: float = 0.0
        self.noiseIntensity: float = 0.0
        self.patternFillType: PatternFillTypeEnum = PatternFillTypeEnum.Fill
        self.patternTileScale: float = 0.0


SJShadow__class = Enum('SJShadow__class', {"shadow": "shadow", "innerShadow": "innerShadow"})


class SJShadow_contextSettings:
    def __init__(self):
        self._class: str = 'graphicsContextSettings'
        self.blendMode: BlendModeEnum = BlendModeEnum.Color
        self.opacity: float = 1.0


class SJShadow:
    def __init__(self):
        self.SJShadow__class: str = 'shadow'
        self.isEnabled: bool = False
        self.blurRadius: float = 0.0
        self.color: SJColor = SJColorPalette.BLACK
        self.contextSettings: SJShadow_contextSettings = {}
        self.offsetX: float = 0.0
        self.offsetY: float = 0.0
        self.spread: float = 0.0


SJBorderList = List[SJBorder]
SJShadowList = List[SJBorder]
SJFillList = List[SJFill]


class SJStyle:
    def __init__(self):
        self._class: str = 'style'
        self.sharedObjectID: str = ''
        self.borderOptions: SJBorderOptions = SJBorderOptions()
        self.borders: SJBorderList = []
        self.shadows: SJShadowList = []
        self.innerShadows: SJShadowList = []
        self.fills: SJFillList = []
        self.textStyle: SJTextStyle = SJTextStyle()
        self.miterLimit: float = 10.0
        self.startDecorationType: LineDecorationTypeEnum = LineDecorationTypeEnum._None
        self.endDecorationType: LineDecorationTypeEnum = LineDecorationTypeEnum._None


class SJTextStyle:
    def __init__(self):
        self._class: str = 'textStyle'


class SJSharedStyle(SJIDBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'sharedStyle'
        self.name: str = ''
        self.value: SJStyle = SJStyle()


SJSharedStyleList = List[SJSharedStyle]


class SJSharedTextStyleContainer:
    def __init__(self):
        self._class: str = 'sharedTextStyleContainer'
        self.objects: SJSharedStyleList = []


class SJSharedStyleContainer:
    def __init__(self):
        self._class: str = 'sharedStyleContainer'
        self.objects: SJSharedStyleList = []


class SJSharedSymbolContainer:
    def __init__(self):
        self._class: str = 'sharedStyleContainer'
        self.objects: SJSharedStyleList = []  # TODO not clear


class ExportOptions:
    def __init__(self):
        self._class: str = 'exportOptions'
        self.exportFormats: List = []
        self.includedLayerIds: List = []
        self.layerOptions: float = 0.0
        self.shouldTrim: bool = True


class RulerData:
    def __init__(self):
        self._class: str = 'rulerData'
        self.base: float = 0.0
        self.guides: FloatList = []


class SJImageDataReference_data:
    def __init__(self):
        self._data: str = ''


class SJImageDataReference_sha1:
    def __init__(self):
        self._data: str = ''


class SJImageDataReference:
    def __init__(self):
        self._class: str = 'MSJSONOriginalDataReference'
        self._ref: str = ''
        self._ref_class: str = 'MSImageData'
        self.data: SJImageDataReference_data = {}
        self.sha1: SJImageDataReference_sha1 = {}


PointString = NewType('PointString',str)


class SJCurvePoint:
    def __init__(self):
        self._class: str = 'curvePoint'
        self.cornerRadius: float = 1.0
        self.curveFrom: PointString = None
        self.curveMode: CurveMode = CurveMode.Straight
        self.curveTo: PointString = None
        self.hasCurveFrom: bool = False
        self.hasCurveTo: bool = True
        self.point: PointString = None


SJCurvePointList = List[SJCurvePoint]


class SJPath:
    def __init__(self):
        self._class: str = 'path'
        self.isClosed: bool = True
        self.points: SJCurvePointList = []


class _SJLayerBase(SJIDBase):
    def __init__(self):
        super().__init__()
        self.name: str = ''
        self.nameIsFixed: bool = False
        self.isVisible: bool = True
        self.isLocked: bool = False
        self.layerListExpandedType: LayerListExpandedType = LayerListExpandedType.Collapsed
        self.hasClickThrough: bool = False
        self.layers: SJLayerList = []
        self.style: SJStyle = SJStyle()
        self.isFlippedHorizontal: bool = False
        self.isFlippedVertical: bool = False
        self.rotation: float = 0.0
        self.shouldBreakMaskChain: bool = False
        self.resizingType: ResizingType = ResizingType.Stretch


class _SJArtboardBase(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self.frame: SJRect = SJRect()
        self.backgroundColor: SJColor = SJColorPalette.WHITE
        self.hasBackgroundColor: bool = True
        self.horizontalRulerData: RulerData = RulerData()
        self.verticalRulerData: RulerData = RulerData()
        self.includeBackgroundColorInExport: bool = False
        self.includeInCloudUpload: bool = True


class SJSymbolMaster(_SJArtboardBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'symbolMaster'
        self.includeBackgroundColorInInstance: bool = False
        self.symbolID: SJObjectId = None


class SJNestedSymbolOverride:
    def __init__(self):
        self.symbolID: SJObjectId = None


SJSymbolInstanceLayer_overrides = Dict[SJObjectId, Union[str, SJNestedSymbolOverride, SJImageDataReference]]


class SJSymbolInstanceLayer(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'symbolInstance'
        self.frame: SJRect = SJRect()
        self.horizontalSpacing: float = 0.0
        self.verticalSpacing: float = 0.0
        self.masterInfluenceEdgeMinXPadding: float = 0.0
        self.masterInfluenceEdgeMaxXPadding: float = 0.0
        self.masterInfluenceEdgeMinYPadding: float = 0.0
        self.masterInfluenceEdgeMaxYPadding: float = 0.0
        self.symbolID: SJObjectId = None
        self.overrides: SJSymbolInstanceLayer_overrides = {}


class SJArtboardLayer(_SJArtboardBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'artboard'


class SJTextLayer(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'text'
        self.attributedString: MSAttributedString = None
        self.glyphBounds: SJStringRect = None


class SJGroupLayer(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'group'


class SJShapeGroupLayer(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'shapeGroup'
        self.style: SJStyle = SJStyle()
        self.hasClippingMask: bool = False


SJShapeLayer__class = Enum('SJShapeLayer__class', {"rectangle": "rectangle", "oval": "oval", "shapePath": "shapePath"})


class SJShapeLayer(SJIDBase):
    def __init__(self):
        super().__init__()
        self.SJShapeLayer__class: str = 'rectangle'


EncodedBase64BinaryPlist = NewType('EncodedBase64BinaryPlist', str)


class KeyValueArchive:
    def __init__(self):
        self._archive: EncodedBase64BinaryPlist = EncodedBase64BinaryPlist('')


NSColorArchive = NewType('NSColorArchive', KeyValueArchive)


class MSAttributedString:
    def __init__(self):
        self._class: str = 'MSAttributedString'
        self.archivedAttributedString: KeyValueArchive = KeyValueArchive()


class MSJSONFileReference:
    def __init__(self):
        self._class: str = 'MSJSonFileReference'
        self._ref_class: str = 'MSImmutablePage'
        self._ref: str = ''  # i.e. pages/doObjectID


SJLayer = Union[SJArtboardLayer, SJTextLayer, SJGroupLayer, SJShapeGroupLayer, SJShapeLayer, SJSymbolInstanceLayer]
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
        self.gradients: List = []  # TODO
        self.images: List = []  # TODO
        self.imageCollection: SJImageCollection = SJImageCollection()


MSJSONFileReferenceList = List[MSJSONFileReference]


# document.json
class SketchDocument(SJIDBase):
    def __init__(self):
        super().__init__()
        # TODO document
        self._class: str = 'document'
        self.colorSpace: int = 0
        self.currentPageIndex: int = 0
        self.foreignSymbols = []
        self.assets = []

        self.layerTextStyles: SJSharedTextStyleContainer = []
        self.layerStyles: SJSharedStyleContainer = []
        self.layerSymbols: SJSharedSymbolContainer = []

        self.pages: MSJSONFileReferenceList
        self.userInfo: dict = None  # TODO


# pages/doObjectID.json
class SketchPage(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'page'
        self.exportOptions: ExportOptions = ExportOptions()
        self.frame = SJRect()
        self.resizingConstraint: int = 0  # TODO
        self.includeInCloudUpload: bool = False  # TODO
        self.horizontalRulerData: RulerData = RulerData()
        self.verticalRulerData: RulerData = RulerData()

    def get_ref(self):
        return 'pages/%s.json' % self.do_objectID


class SketchUserDataEntry:
    def __init__(self):
        self.scrollOrigin: PointString = '{0,0}'
        self.zoomValue: float = 1.0


class SJArtboardDescription:
    def __init__(self):
        self.name: str = ''


SJPageArtboardMappingEntryDict = Dict[SJObjectId, SJArtboardDescription]


class SJPageArtboardMappingEntry:
    def __init__(self):
        self.name: str = ''
        self.artboards: SJPageArtboardMappingEntryDict = []


# user.json
SketchUserData = Dict[SJObjectId, SketchUserDataEntry]
SJPageArtboardMapping = Dict[SJObjectId, SJPageArtboardMappingEntry]  # PageID => Artboards


class SketchCreateMeta:
    def __init__(self):
        self.compatibilityVersion: int = 93
        self.build: int = 51160
        self.app: str = 'com.bohemiancoding.sketch3'
        self.autosaved: int = 0
        self.variant: str = 'NONAPPSTORE'
        self.commit: str = ''
        self.version: int = 101


StrList = List[str]


# meta.json
class SketchMeta(SketchCreateMeta):
    def __init__(self):
        super().__init__()
        self.pagesAndArtboards: SJPageArtboardMapping = {}
        self.fonts: StrList = []

        self.created: SketchCreateMeta = SketchCreateMeta()
        self.saveHistory: StrList = []  # Entries are variant.build
