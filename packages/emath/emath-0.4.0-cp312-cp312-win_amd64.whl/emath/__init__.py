__all__ = [
    "BVector1",
    "BVector2",
    "BVector3",
    "BVector4",
    "DVector1",
    "DVector2",
    "DVector3",
    "DVector4",
    "FVector1",
    "FVector2",
    "FVector3",
    "FVector4",
    "I8Vector1",
    "I8Vector2",
    "I8Vector3",
    "I8Vector4",
    "I16Vector1",
    "I16Vector2",
    "I16Vector3",
    "I16Vector4",
    "I32Vector1",
    "I32Vector2",
    "I32Vector3",
    "I32Vector4",
    "IVector1",
    "IVector2",
    "IVector3",
    "IVector4",
    "I64Vector1",
    "I64Vector2",
    "I64Vector3",
    "I64Vector4",
    "U8Vector1",
    "U8Vector2",
    "U8Vector3",
    "U8Vector4",
    "U16Vector1",
    "U16Vector2",
    "U16Vector3",
    "U16Vector4",
    "U32Vector1",
    "U32Vector2",
    "U32Vector3",
    "U32Vector4",
    "UVector1",
    "UVector2",
    "UVector3",
    "UVector4",
    "U64Vector1",
    "U64Vector2",
    "U64Vector3",
    "U64Vector4",
    "FMatrix2x2",
    "FMatrix2x3",
    "FMatrix2x4",
    "FMatrix3x2",
    "FMatrix3x3",
    "FMatrix3x4",
    "FMatrix4x2",
    "FMatrix4x3",
    "FMatrix4x4",
    "DMatrix2x2",
    "DMatrix2x3",
    "DMatrix2x4",
    "DMatrix3x2",
    "DMatrix3x3",
    "DMatrix3x4",
    "DMatrix4x2",
    "DMatrix4x3",
    "DMatrix4x4",
    "FMatrix2",
    "FMatrix3",
    "FMatrix4",
    "DMatrix2",
    "DMatrix3",
    "DMatrix4",
    "DMatrix2x2Array",
    "DMatrix2x3Array",
    "DMatrix2x4Array",
    "DMatrix3x2Array",
    "DMatrix3x3Array",
    "DMatrix3x4Array",
    "DMatrix4x2Array",
    "DMatrix4x3Array",
    "DMatrix4x4Array",
    "DVector1Array",
    "DVector2Array",
    "DVector3Array",
    "DVector4Array",
    "FMatrix2x2Array",
    "FMatrix2x3Array",
    "FMatrix2x4Array",
    "FMatrix3x2Array",
    "FMatrix3x3Array",
    "FMatrix3x4Array",
    "FMatrix4x2Array",
    "FMatrix4x3Array",
    "FMatrix4x4Array",
    "BVector1Array",
    "BVector2Array",
    "BVector3Array",
    "BVector4Array",
    "FVector1Array",
    "FVector2Array",
    "FVector3Array",
    "FVector4Array",
    "I8Vector1Array",
    "I8Vector2Array",
    "I8Vector3Array",
    "I8Vector4Array",
    "I16Vector1Array",
    "I16Vector2Array",
    "I16Vector3Array",
    "I16Vector4Array",
    "I32Vector1Array",
    "I32Vector2Array",
    "I32Vector3Array",
    "I32Vector4Array",
    "I64Vector1Array",
    "I64Vector2Array",
    "I64Vector3Array",
    "I64Vector4Array",
    "IVector1Array",
    "IVector2Array",
    "IVector3Array",
    "IVector4Array",
    "U8Vector1Array",
    "U8Vector2Array",
    "U8Vector3Array",
    "U8Vector4Array",
    "U16Vector1Array",
    "U16Vector2Array",
    "U16Vector3Array",
    "U16Vector4Array",
    "U32Vector1Array",
    "U32Vector2Array",
    "U32Vector3Array",
    "U32Vector4Array",
    "U64Vector1Array",
    "U64Vector2Array",
    "U64Vector3Array",
    "U64Vector4Array",
    "UVector1Array",
    "UVector2Array",
    "UVector3Array",
    "UVector4Array",
    "BArray",
    "DArray",
    "FArray",
    "I8Array",
    "U8Array",
    "I16Array",
    "U16Array",
    "I32Array",
    "U32Array",
    "IArray",
    "UArray",
    "I64Array",
    "U64Array",
    "FQuaternion",
    "FQuaternionArray",
    "DQuaternion",
    "DQuaternionArray",
    "Number",
]

# emath
# python
from typing import SupportsFloat
from typing import SupportsInt
from typing import TypeAlias

from ._emath import BArray
from ._emath import BVector1
from ._emath import BVector1Array
from ._emath import BVector2
from ._emath import BVector2Array
from ._emath import BVector3
from ._emath import BVector3Array
from ._emath import BVector4
from ._emath import BVector4Array
from ._emath import DArray
from ._emath import DMatrix2x2
from ._emath import DMatrix2x2Array
from ._emath import DMatrix2x3
from ._emath import DMatrix2x3Array
from ._emath import DMatrix2x4
from ._emath import DMatrix2x4Array
from ._emath import DMatrix3x2
from ._emath import DMatrix3x2Array
from ._emath import DMatrix3x3
from ._emath import DMatrix3x3Array
from ._emath import DMatrix3x4
from ._emath import DMatrix3x4Array
from ._emath import DMatrix4x2
from ._emath import DMatrix4x2Array
from ._emath import DMatrix4x3
from ._emath import DMatrix4x3Array
from ._emath import DMatrix4x4
from ._emath import DMatrix4x4Array
from ._emath import DQuaternion
from ._emath import DQuaternionArray
from ._emath import DVector1
from ._emath import DVector1Array
from ._emath import DVector2
from ._emath import DVector2Array
from ._emath import DVector3
from ._emath import DVector3Array
from ._emath import DVector4
from ._emath import DVector4Array
from ._emath import FArray
from ._emath import FMatrix2x2
from ._emath import FMatrix2x2Array
from ._emath import FMatrix2x3
from ._emath import FMatrix2x3Array
from ._emath import FMatrix2x4
from ._emath import FMatrix2x4Array
from ._emath import FMatrix3x2
from ._emath import FMatrix3x2Array
from ._emath import FMatrix3x3
from ._emath import FMatrix3x3Array
from ._emath import FMatrix3x4
from ._emath import FMatrix3x4Array
from ._emath import FMatrix4x2
from ._emath import FMatrix4x2Array
from ._emath import FMatrix4x3
from ._emath import FMatrix4x3Array
from ._emath import FMatrix4x4
from ._emath import FMatrix4x4Array
from ._emath import FQuaternion
from ._emath import FQuaternionArray
from ._emath import FVector1
from ._emath import FVector1Array
from ._emath import FVector2
from ._emath import FVector2Array
from ._emath import FVector3
from ._emath import FVector3Array
from ._emath import FVector4
from ._emath import FVector4Array
from ._emath import I8Array
from ._emath import I8Vector1
from ._emath import I8Vector1Array
from ._emath import I8Vector2
from ._emath import I8Vector2Array
from ._emath import I8Vector3
from ._emath import I8Vector3Array
from ._emath import I8Vector4
from ._emath import I8Vector4Array
from ._emath import I16Array
from ._emath import I16Vector1
from ._emath import I16Vector1Array
from ._emath import I16Vector2
from ._emath import I16Vector2Array
from ._emath import I16Vector3
from ._emath import I16Vector3Array
from ._emath import I16Vector4
from ._emath import I16Vector4Array
from ._emath import I32Array
from ._emath import I32Vector1
from ._emath import I32Vector1Array
from ._emath import I32Vector2
from ._emath import I32Vector2Array
from ._emath import I32Vector3
from ._emath import I32Vector3Array
from ._emath import I32Vector4
from ._emath import I32Vector4Array
from ._emath import I64Array
from ._emath import I64Vector1
from ._emath import I64Vector1Array
from ._emath import I64Vector2
from ._emath import I64Vector2Array
from ._emath import I64Vector3
from ._emath import I64Vector3Array
from ._emath import I64Vector4
from ._emath import I64Vector4Array
from ._emath import IArray
from ._emath import IVector1
from ._emath import IVector1Array
from ._emath import IVector2
from ._emath import IVector2Array
from ._emath import IVector3
from ._emath import IVector3Array
from ._emath import IVector4
from ._emath import IVector4Array
from ._emath import U8Array
from ._emath import U8Vector1
from ._emath import U8Vector1Array
from ._emath import U8Vector2
from ._emath import U8Vector2Array
from ._emath import U8Vector3
from ._emath import U8Vector3Array
from ._emath import U8Vector4
from ._emath import U8Vector4Array
from ._emath import U16Array
from ._emath import U16Vector1
from ._emath import U16Vector1Array
from ._emath import U16Vector2
from ._emath import U16Vector2Array
from ._emath import U16Vector3
from ._emath import U16Vector3Array
from ._emath import U16Vector4
from ._emath import U16Vector4Array
from ._emath import U32Array
from ._emath import U32Vector1
from ._emath import U32Vector1Array
from ._emath import U32Vector2
from ._emath import U32Vector2Array
from ._emath import U32Vector3
from ._emath import U32Vector3Array
from ._emath import U32Vector4
from ._emath import U32Vector4Array
from ._emath import U64Array
from ._emath import U64Vector1
from ._emath import U64Vector1Array
from ._emath import U64Vector2
from ._emath import U64Vector2Array
from ._emath import U64Vector3
from ._emath import U64Vector3Array
from ._emath import U64Vector4
from ._emath import U64Vector4Array
from ._emath import UArray
from ._emath import UVector1
from ._emath import UVector1Array
from ._emath import UVector2
from ._emath import UVector2Array
from ._emath import UVector3
from ._emath import UVector3Array
from ._emath import UVector4
from ._emath import UVector4Array

Number: TypeAlias = SupportsFloat | SupportsInt

FMatrix2: TypeAlias = FMatrix2x2
FMatrix3: TypeAlias = FMatrix3x3
FMatrix4: TypeAlias = FMatrix4x4

FMatrix2Array: TypeAlias = FMatrix2x2Array
FMatrix3Array: TypeAlias = FMatrix3x3Array
FMatrix4Array: TypeAlias = FMatrix4x4Array

DMatrix2: TypeAlias = DMatrix2x2
DMatrix3: TypeAlias = DMatrix3x3
DMatrix4: TypeAlias = DMatrix4x4

DMatrix2Array: TypeAlias = DMatrix2x2Array
DMatrix3Array: TypeAlias = DMatrix3x3Array
DMatrix4Array: TypeAlias = DMatrix4x4Array
