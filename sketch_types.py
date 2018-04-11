import base64
import secrets
from enum import Enum
from typing import NewType, Union, List, Dict

from biplist import readPlistFromString, writePlistToString


class SJRect:
    def __init__(self):
        self._class: str = 'rect'
        self.constrainProportions: bool = False
        self.x: float = 0
        self.y: float = 0
        self.width: float = 300
        self.height: float = 300


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


# Rect encoded as a string, ie {{0, 0}, {10, 30}}
SJStringRect = NewType('SJStringRect', str)


class SJColorNoClass:
    def __init__(self, r=0.0, g=0.0, b=0.0, a=1.0):
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
        self.thickness: float = None
        self.contextSettings: SJContextSettings = None
        self.offsetX: int = None
        self.offsetY: int = None
        self.spread: int = None
        self.blurRadius: int = None


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


class SJContextSettings:
    def __init__(self):
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


class SJBlur:
    def __init__(self):
        self._class: str = 'blur'
        self.isEnabled: bool = True
        self.center: PointString = '{0, 0}'
        self.motionAngle: float = 0.0
        self.radius: int = 0
        self.type: BlurTypeEnum = BlurTypeEnum.GaussianBlur


class SJColorControls:
    def __init__(self):
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
        self.MSAttributedStringFontAttribute: KeyValueArchive = KeyValueArchive()
        self.kerning: int = None
        self.MSAttributedStringColorAttribute: SJColor = None
        self.paragraphStyle: KeyValueArchive = KeyValueArchive()
        self.MSAttributedStringColorDictionaryAttribute: SJColorNoClass = None
        self.MSAttributedStringTextTransformAttribute: int = None
        self.strikethroughStyle: int = None
        self.underlineStyle: int = None


class SJTextStyle:
    def __init__(self):
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
        self.objects: List = [] # TODO not clear


class ExportOptions:
    def __init__(self):
        self._class: str = 'exportOptions'
        self.exportFormats: List[ExportFormat] = []
        self.includedLayerIds: List = []
        self.layerOptions: int = 0
        self.shouldTrim: bool = False


class RulerData:
    def __init__(self):
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
    def __init__(self):
        self._class: str = 'curvePoint'
        self.do_objectID: SJObjectId = None
        self.cornerRadius: float = 1.0
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
        self.hasClickThrough: bool = True
        self.layers: SJLayerList = []
        self.style: SJStyle = SJStyle()
        self.isFlippedHorizontal: bool = False
        self.isFlippedVertical: bool = False
        self.rotation: int = 0
        self.shouldBreakMaskChain: bool = False
        self.resizingType: ResizingType = ResizingType.Stretch
        self.exportOptions: ExportOptions = ExportOptions()
        self.includeInCloudUpload: bool = True
        self.backgroundColor: SJColor = None
        self.hasBackgroundColor: bool = None
        self.horizontalRulerData: RulerData = RulerData()
        self.verticalRulerData: RulerData = RulerData()
        self.includeBackgroundColorInExport: bool = None
        self.resizingConstraint: int = 63
        self.frame: SJRect = SJRect()
        self.originalObjectID: SJObjectId = None
        self.userInfo: dict = None
        self.resizesContent: bool = None
        self.isFlowHome: bool = None
        self.layout: SJLayoutGrid = None


class _SJArtboardBase(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self.frame: SJRect = SJRect()


class SJSimpleGrid:
    def __init__(self):
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


SJSymbolInstanceLayer_overrides = Dict[SJObjectId, Union[str, SJImageDataReference, dict]]


class SJLayoutGrid:
    def __init__(self):
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

        self.overrides: SJSymbolInstanceLayer_overrides = []
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


class SJGroupLayer(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'group'


class SJShapeGroupLayer(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'shapeGroup'

        self.hasClippingMask: bool = False
        self.windingRule: int = 0  # TODO enum
        self.clippingMaskMode: MaskModeEnum = MaskModeEnum.Alpha


class SJShapeLayer(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = None
        self.points: SJCurvePointList = []
        self.edited: bool = True
        self.isClosed: bool = True
        self.pointRadiusBehaviour: int = 0
        self.booleanOperation: BooleanOperation = BooleanOperation.Union
        self.fixedRadius: int = 0
        self.hasConvertedToNewRoundCorners: bool = True


class SJShapeRectangleLayer(SJShapeLayer):
    def __init__(self):
        super().__init__()
        self._class: str = 'rectangle'
        self.path: SJPath = SJPath()


class SJShapeOvalLayer(SJShapeLayer):
    def __init__(self):
        super().__init__()
        self._class: str = 'oval'
        self.path: SJPath = SJPath()


class SJShapePathLayer(SJShapeLayer):
    def __init__(self):
        super().__init__()
        self._class: str = 'shapePath'
        self.path: SJPath = SJPath()


EncodedBase64BinaryPlist = NewType('EncodedBase64BinaryPlist', str)



class SJPath:
    def __init__(self):
        self._class: str = 'path'
        self.isClosed: bool = True
        self.points: SJCurvePointList = []
        self.pointRadiusBehaviour: int = 0


class KeyValueArchive:
    def __init__(self):
        self._archive: EncodedBase64BinaryPlist = EncodedBase64BinaryPlist('')
        self._raw: {} = None  # cached copy of dict

    def get_archive(self):
        if self._raw is not None:
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


class MSAttributedString:
    def __init__(self):
        self._class: str = 'MSAttributedString'
        self.archivedAttributedString: KeyValueArchive = KeyValueArchive()

    def get_text(self):
        return self.archivedAttributedString.get_val(2)

    def set_text(self, string):
        self.archivedAttributedString.set_val(2, string)

    def get_color(self):
        r = self.archivedAttributedString.get_val(25)
        a = self.archivedAttributedString.get_val(26)
        b = self.archivedAttributedString.get_val(27)
        g = self.archivedAttributedString.get_val(28)
        ret = SJColor()
        ret.alpha = a
        ret.red = r
        ret.green = g
        ret.blue = b

        return ret

    def set_color(self, color: SJColor):
        self.archivedAttributedString.set_val(25, color.red)
        self.archivedAttributedString.set_val(26, color.alpha)
        self.archivedAttributedString.set_val(27, color.blue)
        self.archivedAttributedString.set_val(28, color.green)

    def get_font_size(self):
        return self.archivedAttributedString.get_val(16)

    def set_font_size(self, size: float):
        self.archivedAttributedString.set_val(16, size)

    def set_font_family(self, family: str):
        self.archivedAttributedString.set_val(17, family)

    def get_font_family(self):
        return self.archivedAttributedString.get_val(17)


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
        self._class: str = 'document'
        self.colorSpace: int = 0
        self.currentPageIndex: int = 0
        self.foreignSymbols: List = []
        self.assets: SJAssetCollection = SJAssetCollection()

        self.layerTextStyles: SJSharedTextStyleContainer = SJSharedTextStyleContainer()
        self.layerStyles: SJSharedStyleContainer = SJSharedStyleContainer()
        self.layerSymbols: SJSharedSymbolContainer = SJSharedSymbolContainer()

        self.pages: MSJSONFileReferenceList = []
        self.userInfo: dict = None  # TODO


# pages/doObjectID.json
class SketchPage(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'page'

    def get_ref(self):
        return 'pages/%s.json' % self.do_objectID


class SketchUserDataEntry:
    def __init__(self):
        self.scrollOrigin: PointString = '{0, 0}'
        self.zoomValue: int = 1
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
        self.pagesAndArtboards: SJPageArtboardMapping = {}
        self.fonts: StrList = []

        self.autosaved: int = 0
        self.created: SketchCreateMeta = SketchCreateMeta()
        self.saveHistory: StrList = ['NONAPPSTORE.51160']  # Entries are variant.build
