from typing import NewType
from typing import List, Union, Dict
from enum import IntEnum

class SJRect():
	def __init__(self):
		this._class: str = 'rect'
		this.constrainProportions: bool = None
		this.x: float = None
		this.y: float = None
		this.width: float = None
		this.height: float = None
SJObjectId = NewType('SJObjectId',str)
class SJIDBase():
	def __init__(self):
		this.do_objectID: SJObjectId = None
SJStringRect = NewType('SJStringRect',str)
class SJColor():
	def __init__(self):
		this._class: str = 'color'
		this.red: float = None
		this.green: float = None
		this.blue: float = None
		this.alpha: float = None
BorderPositionEnum = IntEnum('BorderPositionEnum',{"val_0": 0, "val_1": 1, "val_2": 2, "val_3": 3})
BorderLineCapStyle = IntEnum('BorderLineCapStyle',{"val_0": 0, "val_1": 1, "val_2": 2})
BorderLineJoinStyle = IntEnum('BorderLineJoinStyle',{"val_0": 0, "val_1": 1, "val_2": 2})
FillTypeEnum = IntEnum('FillTypeEnum',{"val_0": 0, "val_1": 1, "val_4": 4, "val_5": 5})
PatternFillTypeEnum = IntEnum('PatternFillTypeEnum',{"val_0": 0, "val_1": 1, "val_2": 2, "val_3": 3})
BlendModeEnum = IntEnum('BlendModeEnum',{"val_0": 0, "val_1": 1, "val_2": 2, "val_3": 3, "val_4": 4, "val_5": 5, "val_6": 6, "val_7": 7, "val_8": 8, "val_9": 9, "val_10": 10, "val_11": 11, "val_12": 12, "val_13": 13, "val_14": 14, "val_15": 15})
LineDecorationTypeEnum = IntEnum('LineDecorationTypeEnum',{"val_0": 0, "val_1": 1, "val_2": 2, "val_3": 3})
BooleanOperation = IntEnum('BooleanOperation',{"val_-1": -1, "val_0": 0, "val_1": 1, "val_2": 2, "val_3": 3})
CurveMode = IntEnum('CurveMode',{"val_0": 0, "val_1": 1, "val_2": 2, "val_3": 3, "val_4": 4})
ResizingType = IntEnum('ResizingType',{"Stretch": 0, "PinToCorner": 1, "ResizeObject": 2, "FloatInPlace": 3})
LayerListExpandedType = IntEnum('LayerListExpandedType',{"Collapsed": 0, "ExpandedTemp": 1, "Expanded": 2})
class SJBorder():
	def __init__(self):
		this._class: str = 'border'
		this.isEnabled: bool = None
		this.color: SJColor = None
		this.fillType: FillTypeEnum = None
		this.position: BorderPositionEnum = None
		this.thickness: float = None
class SJBorderOptions():
	def __init__(self):
		this._class: str = 'borderOptions'
		this.isEnabled: bool = None
		this.dashPattern: List[float] = None
		this.lineCapStyle: BorderLineCapStyle = None
		this.lineJoinStyle: BorderLineJoinStyle = None
class SJFill():
	def __init__(self):
		this._class: str = 'fill'
		this.isEnabled: bool = None
		this.color: SJColor = None
		this.fillType: FillTypeEnum = None
		this.image: SJImageDataReference = None
		this.noiseIndex: float = None
		this.noiseIntensity: float = None
		this.patternFillType: PatternFillTypeEnum = None
		this.patternTileScale: float = None
SJShadow__class = Enum('SJShadow__class',{"shadow": "shadow", "innerShadow": "innerShadow"})
class SJShadow_contextSettings():
	def __init__(self):
		this._class: str = 'graphicsContextSettings'
		this.blendMode: BlendModeEnum = None
		this.opacity: float = None
class SJShadow():
	def __init__(self):
		this.SJShadow__class: str = 'shadow'
		this.isEnabled: bool = None
		this.blurRadius: float = None
		this.color: SJColor = None
		this.contextSettings: SJShadow_contextSettings = {}
		this.offsetX: float = None
		this.offsetY: float = None
		this.spread: float = None
class SJStyle():
	def __init__(self):
		this._class: str = 'style'
		this.sharedObjectID: str = None
		this.borderOptions: SJBorderOptions = None
		this.borders: List[SJBorder] = None
		this.shadows: List[SJShadow] = None
		this.innerShadows: List[SJShadow] = None
		this.fills: List[SJFill] = None
		this.textStyle: SJTextStyle = None
		this.miterLimit: float = None
		this.startDecorationType: LineDecorationTypeEnum = None
		this.endDecorationType: LineDecorationTypeEnum = None
class SJTextStyle():
	def __init__(self):
		this._class: str = 'textStyle'
class ExportOptions():
	def __init__(self):
		this._class: str = 'exportOptions'
		this.exportFormats: List = None
		this.includedLayerIds: List = None
		this.layerOptions: float = None
		this.shouldTrim: bool = None
class RulerData():
	def __init__(self):
		this._class: str = 'rulerData'
		this.base: 0 = None
		this.guides: List[float] = None
class SJImageDataReference_data():
	def __init__(self):
		this._data: str = None
class SJImageDataReference_sha1():
	def __init__(self):
		this._data: str = None
class SJImageDataReference():
	def __init__(self):
		this._class: str = 'MSJSONOriginalDataReference'
		this._ref: str = None
		this._ref_class: str = 'MSImageData'
		this.data: SJImageDataReference_data = {}
		this.sha1: SJImageDataReference_sha1 = {}
PointString = NewType('PointString',str)
class SJCurvePoint():
	def __init__(self):
		this._class: str = 'curvePoint'
		this.cornerRadius: float = None
		this.curveFrom: PointString = None
		this.curveMode: CurveMode = None
		this.curveTo: PointString = None
		this.hasCurveFrom: bool = None
		this.hasCurveTo: bool = None
		this.point: PointString = None
class SJPath():
	def __init__(self):
		this._class: str = 'path'
		this.isClosed: bool = None
		this.points: List[SJCurvePoint] = None
class _SJLayerBase(SJIDBase):
	def __init__(self):
		this.name: str = None
		this.nameIsFixed: bool = None
		this.isVisible: bool = None
		this.isLocked: bool = None
		this.layerListExpandedType: LayerListExpandedType = None
		this.hasClickThrough: bool = None
		this.layers: List[SJLayer] = None
		this.style: SJStyle = None
		this.isFlippedHorizontal: bool = None
		this.isFlippedVertical: bool = None
		this.rotation: float = None
		this.shouldBreakMaskChain: bool = None
		this.resizingType: ResizingType = None
class _SJArtboardBase(_SJLayerBase):
	def __init__(self):
		this.frame: SJRect = None
		this.backgroundColor: SJColor = None
		this.hasBackgroundColor: bool = None
		this.horizontalRulerData: RulerData = None
		this.verticalRulerData: RulerData = None
		this.includeBackgroundColorInExport: bool = None
		this.includeInCloudUpload: bool = None

class SJSymbolMaster(_SJArtboardBase):
	def __init__(self):
		this._class: str = 'symbolMaster'
		this.includeBackgroundColorInInstance: bool = None
		this.symbolID: SJObjectId = None
class SJNestedSymbolOverride():
	def __init__(self):
		this.symbolID: SJObjectId = None
SJSymbolInstanceLayer_overrides = Dict[SJObjectId,Union[str,SJNestedSymbolOverride,SJImageDataReference]]

class SJSymbolInstanceLayer(_SJLayerBase):
	def __init__(self):
		this._class: str = 'symbolInstance'
		this.frame: SJRect = None
		this.horizontalSpacing: float = None
		this.verticalSpacing: float = None
		this.masterInfluenceEdgeMinXPadding: float = None
		this.masterInfluenceEdgeMaxXPadding: float = None
		this.masterInfluenceEdgeMinYPadding: float = None
		this.masterInfluenceEdgeMaxYPadding: float = None
		this.symbolID: SJObjectId = None
		this.overrides: SJSymbolInstanceLayer_overrides = {}
class SJArtboardLayer(_SJArtboardBase):
	def __init__(self):
		this._class: str = 'artboard'
class SJTextLayer(_SJLayerBase):
	def __init__(self):
		this._class: str = 'text'
		this.attributedString: MSAttributedString = None
		this.glyphBounds: SJStringRect = None
class SJGroupLayer(_SJLayerBase):
	def __init__(self):
		this._class: str = 'group'
class SJShapeGroupLayer(_SJLayerBase):
	def __init__(self):
		this._class: str = 'shapeGroup'
		this.style: SJStyle = None
		this.hasClippingMask: bool = None
SJShapeLayer__class = Enum('SJShapeLayer__class',{"rectangle": "rectangle", "oval": "oval", "shapePath": "shapePath"})
class SJShapeLayer(SJIDBase):
	def __init__(self):
		this.SJShapeLayer__class: str = 'rectangle'
EncodedBase64BinaryPlist = NewType('EncodedBase64BinaryPlist',str)
class KeyValueArchive():
	def __init__(self):
		this._archive: EncodedBase64BinaryPlist = None
NSColorArchive = NewType('NSColorArchive',KeyValueArchive)
class MSAttributedString():
	def __init__(self):
		this._class: str = 'MSAttributedString'
		this.archivedAttributedString: KeyValueArchive = None
SJLayer = Union[SJArtboardLayer,SJTextLayer,SJGroupLayer,SJShapeGroupLayer,SJShapeLayer,SJSymbolInstanceLayer]
