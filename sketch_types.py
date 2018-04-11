import base64
import secrets
from enum import Enum
from typing import NewType, Union, List, Dict

from biplist import readPlistFromString, writePlistToString


class SJRect:
    def __init__(self):
        self._class: str = 'rect'
        self.constrainProportions: bool = None
        self.x: float = None
        self.y: float = None
        self.width: float = None
        self.height: float = None


SJObjectId = NewType('SJObjectId', str)


def get_object_id():
    p = '00CC4CF3-9934-4ED2-9A53-5DD12A47F9B7'.split('-')
    o = None
    for part in p:
        x = int(len(part) / 2)
        o.append(secrets.token_hex(x))

    return '-'.join(o).upper()


class SJIDBase:
    def __init__(self):
        self.do_objectID: SJObjectId = None  # get_object_id()


SJStringRect = NewType('SJStringRect', str)


class SJColorNoClass:
    def __init__(self, r=None, g=None, b=None, a=1.0):
        self.red: float = r
        self.green: float = g
        self.blue: float = b
        self.alpha: float = a


class SJColor(SJColorNoClass):
    def __init__(self, r=None, g=None, b=None, a=1.0):
        super().__init__(r, g, b, a)
        self._class: str = 'color'


class SJColorPalette:
    WHITE = SJColor(r=1.0, g=1.0, b=1.0)
    BLACK = SJColor(r=None, g=None, b=None)


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
        self.absoluteSize: int = None
        self.fileFormat: ExportOptionsFormat = 'png'
        self.name: str = None
        self.namingScheme: int = None
        self.scale: int = None
        self.visibleScaleType: int = None


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
        self.isEnabled: bool = None
        self.color: SJColor = None
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
        self.isEnabled: bool = None
        self.dashPattern: FloatList = None
        self.lineCapStyle: BorderLineCapStyle = None
        self.lineJoinStyle: BorderLineJoinStyle = None


class SJFill:
    def __init__(self):
        self._class: str = 'fill'
        self.isEnabled: bool = None
        self.color: SJColor = None
        self.fillType: FillTypeEnum = None
        self.image: SJImageDataReference = None
        self.noiseIndex: float = None
        self.noiseIntensity: float = None
        self.patternFillType: PatternFillTypeEnum = None
        self.patternTileScale: float = None
        self.gradient: SJGradient = None
        self.do_objectID: SJObjectId = None


SJShadow__class = Enum('SJShadow__class', {"shadow": "shadow", "innerShadow": "innerShadow"})


class SJGradientStop:
    def __init__(self):
        self._class: str = 'gradientStop'
        self.position: float = None
        self.color: SJColor = None


class SJGradient:
    def __init__(self):
        self._class: str = 'gradient'
        self.elipseLength: int = None
        setattr(self, 'from', None)
        # self.from: PointString = None
        self.to: PointString = None
        self.gradientType: GradientTypeEnum = None
        self.stops: List[SJGradientStop] = None


class SJContextSettings:
    def __init__(self):
        self._class: str = 'graphicsContextSettings'
        self.blendMode: BlendModeEnum = None
        self.opacity: float = None


class SJShadow:
    def __init__(self):
        self._class: SJShadow__class = 'shadow'
        self.isEnabled: bool = None
        self.blurRadius: float = None
        self.color: SJColor = None
        self.contextSettings: SJContextSettings = None
        self.offsetX: float = None
        self.offsetY: float = None
        self.spread: float = None


SJBorderList = List[SJBorder]
SJShadowList = List[SJBorder]
SJFillList = List[SJFill]


class SJBlur:
    def __init__(self):
        self._class: str = 'blur'
        self.isEnabled: bool = None
        self.center: PointString = None
        self.motionAngle: float = None
        self.radius: int = None
        self.type: BlurTypeEnum = None


class SJColorControls:
    def __init__(self):
        self._class: str = 'colorControls'
        self.isEnabled: bool = None
        self.brightness: int = None
        self.contrast: int = None
        self.contrast: int = None
        self.hue: int = None
        self.saturation: int = None


class SJStyle:
    def __init__(self):
        self._class: str = 'style'
        self.sharedObjectID: str = None
        self.borderOptions: SJBorderOptions = None
        self.borders: SJBorderList = None
        self.shadows: SJShadowList = None
        self.innerShadows: SJShadowList = None
        self.fills: SJFillList = None
        self.textStyle: SJTextStyle = None
        self.miterLimit: float = 10.0
        self.startDecorationType: LineDecorationTypeEnum = LineDecorationTypeEnum._None
        self.endDecorationType: LineDecorationTypeEnum = LineDecorationTypeEnum._None
        self.blur: SJBlur = None
        self.contextSettings: SJContextSettings = None
        self.colorControls: SJColorControls = None
        self.do_objectID: SJObjectId = None


class SJTextStyleAttribute:
    def __init__(self):
        self.MSAttributedStringFontAttribute: KeyValueArchive = None
        self.kerning: int = None
        self.MSAttributedStringColorAttribute: SJColor = None
        self.paragraphStyle: KeyValueArchive = None
        self.MSAttributedStringColorDictionaryAttribute: SJColorNoClass = None
        self.MSAttributedStringTextTransformAttribute: int = None
        self.strikethroughStyle: int = None
        self.underlineStyle: int = None


class SJTextStyle:
    def __init__(self):
        self._class: str = 'textStyle'
        self.verticalAlignment: TextAlignmentEnum = None  # TODO enum?
        self.encodedAttributes: SJTextStyleAttribute = None


class SJSharedStyle(SJIDBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'sharedStyle'
        self.name: str = None
        self.value: SJStyle = None


SJSharedStyleList = List[SJSharedStyle]


class SJSharedTextStyleContainer:
    def __init__(self):
        self._class: str = 'sharedTextStyleContainer'
        self.objects: SJSharedStyleList = None


class SJSharedStyleContainer:
    def __init__(self):
        self._class: str = 'sharedStyleContainer'
        self.objects: SJSharedStyleList = None


class SJSharedSymbolContainer:
    def __init__(self):
        self._class: str = 'sharedStyleContainer'
        self.objects: SJSharedStyleList = None  # TODO not clear


class ExportOptions:
    def __init__(self):
        self._class: str = 'exportOptions'
        self.exportFormats: List[ExportFormat] = None
        self.includedLayerIds: List = None
        self.layerOptions: float = None
        self.shouldTrim: bool = None


class RulerData:
    def __init__(self):
        self._class: str = 'rulerData'
        self.base: float = None
        self.guides: FloatList = None


class SJImageDataReference_data:
    def __init__(self):
        self._data: str = None


class SJImageDataReference_sha1:
    def __init__(self):
        self._data: str = None


class SJImageDataReference:
    def __init__(self):
        self._class: str = 'MSJSONOriginalDataReference'
        self._ref: str = None
        self._ref_class: str = 'MSImageData'
        self.data: SJImageDataReference_data = None
        self.sha1: SJImageDataReference_sha1 = None


PointString = NewType('PointString', str)


class SJCurvePoint:
    def __init__(self):
        self._class: str = 'curvePoint'
        self.do_objectID: SJObjectId = None
        self.cornerRadius: float = None
        self.curveFrom: PointString = None
        self.curveMode: CurveMode = None
        self.curveTo: PointString = None
        self.hasCurveFrom: bool = None
        self.hasCurveTo: bool = None
        self.point: PointString = None


SJCurvePointList = List[SJCurvePoint]


class _SJLayerBase(SJIDBase):
    def __init__(self):
        super().__init__()
        self.name: str = ''
        self.nameIsFixed: bool = None
        self.isVisible: bool = None
        self.isLocked: bool = None
        self.layerListExpandedType: LayerListExpandedType = LayerListExpandedType.Collapsed
        self.hasClickThrough: bool = None
        self.layers: SJLayerList = None
        self.style: SJStyle = None
        self.isFlippedHorizontal: bool = None
        self.isFlippedVertical: bool = None
        self.rotation: float = None
        self.shouldBreakMaskChain: bool = None
        self.resizingType: ResizingType = ResizingType.Stretch
        self.exportOptions: ExportOptions = None
        self.includeInCloudUpload: bool = None
        self.backgroundColor: SJColor = None
        self.hasBackgroundColor: bool = None
        self.horizontalRulerData: RulerData = None
        self.verticalRulerData: RulerData = None
        self.includeBackgroundColorInExport: bool = None
        self.resizingConstraint: int = None
        self.frame: SJRect = None
        self.originalObjectID: SJObjectId = None
        self.userInfo: dict = None
        self.resizesContent: bool = None
        self.isFlowHome: bool = None
        self.layout: SJLayoutGrid = None


class _SJArtboardBase(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self.frame: SJRect = None


class SJSimpleGrid:
    def __init__(self):
        self._class: str = 'simpleGrid'
        self.isEnabled: bool = None
        self.gridSize: int = None
        self.thickGridTimes: int = None


class SJSymbolMaster(_SJArtboardBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'symbolMaster'
        self.includeBackgroundColorInInstance: bool = None
        self.symbolID: SJObjectId = None
        self.changeIdentifier: int = None
        self.grid: SJSimpleGrid = None


SJSymbolInstanceLayer_overrides = Dict[SJObjectId, Union[str, SJImageDataReference, dict]]


class SJLayoutGrid:
    def __init__(self):
        self._class: str = 'layoutGrid'
        self.isEnabled: bool = None
        self.columnWidth: float = None
        self.drawHorizontal: bool = None
        self.drawHorizontalLines: bool = None
        self.drawVertical: bool = None
        self.gutterHeight: int = None
        self.gutterWidth: int = None
        self.guttersOutside: bool = None
        self.horizontalOffset: int = None
        self.numberOfColumns: int = None
        self.rowHeightMultiplication: int = None
        self.totalWidth: int = None


class SJOverride:
    def __init__(self):
        self._class: str = 'overrideValue'
        self.overrideName: SJObjectId = None
        self.value: str = None
        self.do_objectID: SJObjectId = None


class SJSymbolInstanceLayer(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'symbolInstance'

        self.horizontalSpacing: float = None
        self.verticalSpacing: float = None
        self.masterInfluenceEdgeMinXPadding: float = None
        self.masterInfluenceEdgeMaxXPadding: float = None
        self.masterInfluenceEdgeMinYPadding: float = None
        self.masterInfluenceEdgeMaxYPadding: float = None
        self.symbolID: SJObjectId = None

        self.overrides: SJSymbolInstanceLayer_overrides = None
        self.overrideValues: List[SJOverride] = None
        self.scale: int = None

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
        self.attributedString: MSAttributedString = None
        self.glyphBounds: SJStringRect = None
        self.lineSpacingBehaviour: int = None
        self.dontSynchroniseWithSymbol: bool = None
        self.automaticallyDrawOnUnderlyingPath: bool = None
        self.textBehaviour: int = None


class SJGroupLayer(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'group'


class SJShapeGroupLayer(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'shapeGroup'
        self.style: SJStyle = None
        self.hasClippingMask: bool = None
        self.windingRule: int = None  # TODO enum
        self.clippingMaskMode: MaskModeEnum = None


class SJShapeLayer(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = None
        self.points: SJCurvePointList = None
        self.edited: bool = None
        self.isClosed: bool = None
        self.pointRadiusBehaviour: int = None
        self.booleanOperation: BooleanOperation = None
        self.fixedRadius: int = None
        self.hasConvertedToNewRoundCorners: bool = None


class SJShapeRectangleLayer(SJShapeLayer):
    def __init__(self):
        super().__init__()
        self._class: str = 'rectangle'
        self.path: SJPath = None


class SJShapeOvalLayer(SJShapeLayer):
    def __init__(self):
        super().__init__()
        self._class: str = 'oval'
        self.path: SJPath = None


class SJShapePathLayer(SJShapeLayer):
    def __init__(self):
        super().__init__()
        self._class: str = 'shapePath'
        self.path: SJPath = None


EncodedBase64BinaryPlist = NewType('EncodedBase64BinaryPlist', str)


class SJPath:
    def __init__(self):
        self._class: str = 'path'
        self.isClosed: bool = None
        self.points: SJCurvePointList = None
        self.pointRadiusBehaviour: int = None


class KeyValueArchive:
    def __init__(self):
        self._archive: EncodedBase64BinaryPlist = EncodedBase64BinaryPlist('')
        self._raw: str = None  # cached copy of dict

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
        self.archivedAttributedString: KeyValueArchive = None

    def get_text(self):
        return self.archivedAttributedString.get_val(2)

    def set_text(self, string):
        self.archivedAttributedString.set_val(2, string)

    def get_color(self):
        r = self.archivedAttributedString.get_val(25)
        a = self.archivedAttributedString.get_val(26)
        b = self.archivedAttributedString.get_val(27)
        g = self.archivedAttributedString.get_val(28)
        ret = None
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
        self._class: str = 'MSJSonFileReference'
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
        self.colors: SJColorList = None
        self.gradients: List[SJGradient] = None  # TODO
        self.images: List = None  # TODO
        self.imageCollection: SJImageCollection = None


MSJSONFileReferenceList = List[MSJSONFileReference]


# document.json
class SketchDocument(SJIDBase):
    def __init__(self):
        super().__init__()
        # TODO document
        self._class: str = 'document'
        self.colorSpace: int = 0
        self.currentPageIndex: int = 0
        self.foreignSymbols: List = None
        self.assets: SJAssetCollection = None

        self.layerTextStyles: SJSharedTextStyleContainer = None
        self.layerStyles: SJSharedStyleContainer = None
        self.layerSymbols: SJSharedSymbolContainer = None

        self.pages: MSJSONFileReferenceList = None
        self.userInfo: dict = None  # TODO


# pages/doObjectID.json
class SketchPage(_SJLayerBase):
    def __init__(self):
        super().__init__()
        self._class: str = 'page'
        self.exportOptions: ExportOptions = None
        self.frame: SJRect = None
        self.resizingConstraint: int = 0  # TODO
        self.horizontalRulerData: RulerData = None
        self.verticalRulerData: RulerData = None

    def get_ref(self):
        return 'pages/%s.json' % self.do_objectID


class SketchUserDataEntry:
    def __init__(self):
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
        self.artboards: SJPageArtboardMappingEntryDict = None


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
        self.commit: str = ''
        self.version: int = 101
        self.appVersion: str = '49'


StrList = List[str]


# meta.json
class SketchMeta(SketchCreateMeta):
    def __init__(self):
        super().__init__()
        self.pagesAndArtboards: SJPageArtboardMapping = {}
        self.fonts: StrList = None

        self.created: SketchCreateMeta = None
        self.saveHistory: StrList = None  # Entries are variant.build
