from __future__ import annotations
import usdex.core._usdex_core
import typing
import pxr.Gf
import pxr.Sdf
import pxr.Tf
import pxr.Usd
import pxr.UsdGeom
import pxr.UsdLux
import pxr.UsdPhysics
import pxr.UsdShade
import pxr.Vt

__all__ = [
    "ColorSpace",
    "DiagnosticsLevel",
    "DiagnosticsOutputStream",
    "FloatPrimvarData",
    "Int64PrimvarData",
    "IntPrimvarData",
    "JointFrame",
    "NameCache",
    "RotationOrder",
    "StringPrimvarData",
    "TokenPrimvarData",
    "ValidChildNameCache",
    "Vec2fPrimvarData",
    "Vec3fPrimvarData",
    "activateDiagnosticsDelegate",
    "addAssetInterface",
    "addDiffuseTextureToPreviewMaterial",
    "addMetallicTextureToPreviewMaterial",
    "addNormalTextureToPreviewMaterial",
    "addOpacityTextureToPreviewMaterial",
    "addOrmTextureToPreviewMaterial",
    "addPhysicsToMaterial",
    "addPreviewMaterialInterface",
    "addRoughnessTextureToPreviewMaterial",
    "alignPhysicsJoint",
    "bindMaterial",
    "bindPhysicsMaterial",
    "blockDisplayName",
    "buildVersion",
    "clearDisplayName",
    "computeEffectiveDisplayName",
    "computeEffectivePreviewSurfaceShader",
    "configureStage",
    "createMaterial",
    "deactivateDiagnosticsDelegate",
    "defineCamera",
    "defineCubicBasisCurves",
    "defineDomeLight",
    "defineLinearBasisCurves",
    "definePayload",
    "definePhysicsFixedJoint",
    "definePhysicsMaterial",
    "definePhysicsPrismaticJoint",
    "definePhysicsRevoluteJoint",
    "definePhysicsSphericalJoint",
    "definePointCloud",
    "definePolyMesh",
    "definePreviewMaterial",
    "defineRectLight",
    "defineReference",
    "defineScope",
    "defineXform",
    "enableTranscodingSetting",
    "exportLayer",
    "getAssetToken",
    "getColorSpaceToken",
    "getContentsToken",
    "getDiagnosticLevel",
    "getDiagnosticsLevel",
    "getDiagnosticsOutputStream",
    "getDisplayName",
    "getGeometryToken",
    "getLayerAuthoringMetadata",
    "getLibraryToken",
    "getLightAttr",
    "getLocalTransform",
    "getLocalTransformComponents",
    "getLocalTransformComponentsQuat",
    "getLocalTransformMatrix",
    "getMaterialsToken",
    "getPayloadToken",
    "getPhysicsToken",
    "getTexturesToken",
    "getValidChildName",
    "getValidChildNames",
    "getValidPrimName",
    "getValidPrimNames",
    "getValidPropertyName",
    "getValidPropertyNames",
    "hasLayerAuthoringMetadata",
    "isDiagnosticsDelegateActive",
    "isEditablePrimLocation",
    "isLight",
    "linearToSrgb",
    "removeMaterialInterface",
    "sRgbToLinear",
    "saveLayer",
    "saveStage",
    "setDiagnosticsLevel",
    "setDiagnosticsOutputStream",
    "setDisplayName",
    "setLayerAuthoringMetadata",
    "setLocalTransform",
    "version"
]


class ColorSpace():
    """
    Texture color space (encoding) types

    Members:

      eAuto : Check for gamma or metadata in the texture itself

      eRaw : Use linear sampling (typically used for Normal, Roughness, Metallic, Opacity textures, or when using high dynamic range file formats like EXR)

      eSrgb : Use sRGB sampling (typically used for Diffuse textures when using PNG files)
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    __members__: dict # value = {'eAuto': <ColorSpace.eAuto: 0>, 'eRaw': <ColorSpace.eRaw: 1>, 'eSrgb': <ColorSpace.eSrgb: 2>}
    eAuto: usdex.core._usdex_core.ColorSpace # value = <ColorSpace.eAuto: 0>
    eRaw: usdex.core._usdex_core.ColorSpace # value = <ColorSpace.eRaw: 1>
    eSrgb: usdex.core._usdex_core.ColorSpace # value = <ColorSpace.eSrgb: 2>
    pass
class DiagnosticsLevel():
    """
    Controls the diagnostics that will be emitted when the ``Delegate`` is active.

    Members:

      eFatal : Only ``Tf.Fatal`` are emitted.

      eError : Emit ``Tf.Error`` and ``Tf.Fatal``, but suppress ``Tf.Warn`` and ``Tf.Status`` diagnostics.

      eWarning : Emit ``Tf.Warn``, ``Tf.Error``, and ``Tf.Fatal``, but suppress ``Tf.Status`` diagnostics.

      eStatus : All diagnostics are emitted.
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    __members__: dict # value = {'eFatal': <DiagnosticsLevel.eFatal: 0>, 'eError': <DiagnosticsLevel.eError: 1>, 'eWarning': <DiagnosticsLevel.eWarning: 2>, 'eStatus': <DiagnosticsLevel.eStatus: 3>}
    eError: usdex.core._usdex_core.DiagnosticsLevel # value = <DiagnosticsLevel.eError: 1>
    eFatal: usdex.core._usdex_core.DiagnosticsLevel # value = <DiagnosticsLevel.eFatal: 0>
    eStatus: usdex.core._usdex_core.DiagnosticsLevel # value = <DiagnosticsLevel.eStatus: 3>
    eWarning: usdex.core._usdex_core.DiagnosticsLevel # value = <DiagnosticsLevel.eWarning: 2>
    pass
class DiagnosticsOutputStream():
    """
    Control the output stream to which diagnostics are logged.

    Members:

      eNone : All diagnostics are suppressed.

      eStdout : All diagnostics print to the ``stdout`` stream.

      eStderr : All diagnostics print to the ``stderr`` stream.
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    __members__: dict # value = {'eNone': <DiagnosticsOutputStream.eNone: 0>, 'eStdout': <DiagnosticsOutputStream.eStdout: 1>, 'eStderr': <DiagnosticsOutputStream.eStderr: 2>}
    eNone: usdex.core._usdex_core.DiagnosticsOutputStream # value = <DiagnosticsOutputStream.eNone: 0>
    eStderr: usdex.core._usdex_core.DiagnosticsOutputStream # value = <DiagnosticsOutputStream.eStderr: 2>
    eStdout: usdex.core._usdex_core.DiagnosticsOutputStream # value = <DiagnosticsOutputStream.eStdout: 1>
    pass
class FloatPrimvarData():
    """
    ``PrimvarData`` that holds ``Vt.FloatArray`` values (e.g widths or scale factors).

                This is a read-only class to manage all ``UsdGeom.Primvar`` data as a single object without risk of detaching (copying) arrays.

                ``UsdGeom.Primvars`` are often used when authoring ``UsdGeom.PointBased`` prims (e.g meshes, curves, and point clouds) to describe surface varying
                properties that can affect how a prim is rendered, or to drive a surface deformation.

                However, ``UsdGeom.Primvar`` data can be quite intricate to use, especially with respect to indexed vs non-indexed primvars, element size, the
                complexities of ``Vt.Array`` detach (copy-on-write) semantics, and the ambiguity of "native" attributes vs primvar attributes (e.g. mesh normals).

                This class aims to provide simpler entry points to avoid common mistakes with respect to ``UsdGeom.Primvar`` data handling.

                All of the USD authoring "define" functions in this library accept optional ``PrimvarData`` to define e.g normals, display colors, etc.
            
    """
    def __eq__(self, arg0: FloatPrimvarData) -> bool: 
        """
        Check that all data between two ``PrimvarData`` objects is identical.

        This differs from the equality operator in that it ensures the ``Vt.Array`` values and indices have not detached.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if all the member data is equal (but not necessarily identical arrays).
        """
    @typing.overload
    def __init__(self, interpolation: str, values: pxr.Vt.FloatArray, elementSize: int = -1) -> None: 
        """
        Construct non-indexed ``PrimvarData``.

        Note:
            To avoid immediate array iteration, validation does not occur during construction, and is deferred until ``isValid()`` is called.
            This may be counter-intuitive as ``PrimvarData`` provides read-only access, but full validation is often only possible within the context
            of specific surface topology, so premature validation would be redundant.

        Args:
            interpolation: The primvar interpolation. Must match ``UsdGeom.Primvar.IsValidInterpolation()`` to be considered valid.
            values: Read-only accessor to the values array.
            elementSize: Optional element size. This should be fairly uncommon.
                See [GetElementSize](https://openusd.org/release/api/class_usd_geom_primvar.html#a711c3088ebca00ca75308485151c8590) for details.

        Returns:
            The read-only ``PrimvarData``.



        Construct indexed ``PrimvarData``.

        Note:
            To avoid immediate array iteration, validation does not occur during construction, and is deferred until ``isValid()`` is called.
            This may be counter-intuitive as ``PrimvarData`` provides read-only access, but full validation is often only possible within the context
            of specific surface topology, so premature validation would be redundant.

        Args:
            interpolation: The primvar interpolation. Must match ``UsdGeom.Primvar.IsValidInterpolation()`` to be considered valid.
            values: Read-only accessor to the values array.
            indices: Read-only accessor to the indices array.
            elementSize: Optional element size. This should be fairly uncommon.
                See [GetElementSize](https://openusd.org/release/api/class_usd_geom_primvar.html#a711c3088ebca00ca75308485151c8590) for details.

        Returns:
            The read-only ``PrimvarData``.
        """
    @typing.overload
    def __init__(self, interpolation: str, values: pxr.Vt.FloatArray, indices: pxr.Vt.IntArray, elementSize: int = -1) -> None: ...
    def __ne__(self, arg0: FloatPrimvarData) -> bool: 
        """
        Check for in-equality between two ``PrimvarData`` objects.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if any member data is not equal (but does not guarantee identical arrays).
        """
    def __str__(self) -> str: ...
    def effectiveSize(self) -> int: 
        """
        The effective size of the data, having accounted for values, indices, and element size.

        This is the number of variable values that "really" exist, as far as a consumer is concerned. The indices & elementSize are used as a storage
        optimization, but the consumer should consider the effective size as the number of "deduplicated" individual values.

        Returns:
            The effective size of the data.
        """
    def elementSize(self) -> int: 
        """
        The element size.

        Any value less than 1 is considered "non authored" and indicates no element size. This should be the most common case, as element size is a
        fairly esoteric extension of ``UsdGeom.Primvar`` data to account for non-typed array strides such as spherical harmonics float[9] arrays.

        See ``UsdGeom.Primvar.GetElementSize()`` for more details.

        Returns:
            The primvar element size.
        """
    @staticmethod
    def getPrimvarData(primvar: pxr.UsdGeom.Primvar, time: pxr.Usd.TimeCode = nan) -> FloatPrimvarData: 
        """
        Construct a ``PrimvarData`` from a ``UsdGeom.Primvar`` that has already been authored.

        The primvar may be indexed, non-indexed, with or without elements, or it may not even be validly authored scene description.
        Use ``isValid()`` to confirm that valid data has been gathered.

        Args:
            primvar: The previously authored ``UsdGeom.Primvar``.
            time: The time at which the attribute values are read.

        Returns:
            The read-only ``PrimvarData``.
        """
    def hasIndices(self) -> bool: 
        """
        Whether this is indexed or non-indexed ``PrimvarData``

        Returns:
            Whether this is indexed or non-indexed ``PrimvarData``.
        """
    def index(self) -> bool: 
        """
        Update the values and indices of this ``PrimvarData`` object to avoid duplicate values.

        Updates will not be made in the following conditions:
            - If element size is greater than one.
            - If the existing indexing is efficient.
            - If there are no duplicate values.
            - If the existing indices are invalid

        Returns:
            True if the values and/or indices were modified.
        """
    def indices(self) -> pxr.Vt.IntArray: 
        """
        Access to the indices array.

        This method throws a runtime error if the ``PrimvarData`` is not indexed. For exception-free access, check ``hasIndices()`` before calling this.

        Note:
            It may contain an empty or invalid indices array. Use ``PrimvarData.isValid()`` to validate that the indices are not out-of-range.

        Returns:
            The primvar indices
        """
    def interpolation(self) -> str: 
        """
        The geometric interpolation.

        It may be an invalid interpolation. Use ``PrimvarData.isValid()`` or ``UsdGeom.Primvar.IsValidInterpolation()`` to confirm.

        Returns:
            The geometric interpolation.
        """
    def isIdentical(self, other: FloatPrimvarData) -> bool: 
        """
        Check that all data between two ``PrimvarData`` objects is identical.

        This differs from the equality operator in that it ensures the ``Vt.Array`` values and indices have not detached.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if all the member data is equal and arrays are identical.
        """
    def isValid(self) -> bool: 
        """
        Whether the data is valid or invalid.

        This is a validation check with respect to the ``PrimvarData`` itself & the requirements of ``UsdGeom.Prim``. It does not validate with respect to
        specific surface topology data, as no such data is available or consistant across ``UsdGeom.PointBased`` prim types.

        This validation checks the following, in this order, and returns false if any condition fails:

            - The interpolation matches ``UsdGeom.Primvar.IsValidInterpolation()``.
            - The values are not empty. Note that individual values may be invalid (e.g ``NaN`` values on a ``Vt.FloatArray``) but this will not be
              considered a failure, as some workflows allow for ``NaN`` to indicate non-authored elements or "holes" within the data.
            - If it is non-indexed, and has elements, that the values divide evenly by elementSize.
            - If it is indexed, and has elements, that the indices divide evenly by elementSize.
            - If it is indexed, that the indices are all within the expected range of the values array.

        Returns:
            Whether the data is valid or invalid.
        """
    def setPrimvar(self, primvar: pxr.UsdGeom.Primvar, time: pxr.Usd.TimeCode = nan) -> bool: 
        """
        Set data on an existing ``UsdGeom.Primvar`` from a ``PrimvarData`` that has already been authored.

        Any existing authored data on the primvar will be overwritten or blocked with the ``PrimvarData`` members.

        To copy data from one ``UsdGeom.Primvar`` to another, use ``data: PrimvarData = PrimvarData.get(primvar: UsdGeom.Primvar)`` to gather the data,
        then use ``setPrimvar(primvar: UsdGeom.Primvar)`` to author it.

        Args:
            primvar: The previously authored ``UsdGeom.Primvar``.
            time: The time at which the attribute values are written.

        Returns:
            Whether the ``UsdGeom.Primvar`` was completely authored from the member data.
            Any failure to author may leave the primvar in an unknown state (e.g. it may have been partially authored).
        """
    def values(self) -> pxr.Vt.FloatArray: 
        """
        Access to the values array.

        Bear in mind the values may need to be accessed via ``indices()`` or using an ``elementSize()`` stride.

        It may contain an empty or invalid values array.

        Returns:
            The primvar values.
        """
    __hash__ = None
    pass
class Int64PrimvarData():
    """
    ``PrimvarData`` that holds ``Vt.Int64Array`` values (e.g ids that might be very large).

                This is a read-only class to manage all ``UsdGeom.Primvar`` data as a single object without risk of detaching (copying) arrays.

                ``UsdGeom.Primvars`` are often used when authoring ``UsdGeom.PointBased`` prims (e.g meshes, curves, and point clouds) to describe surface varying
                properties that can affect how a prim is rendered, or to drive a surface deformation.

                However, ``UsdGeom.Primvar`` data can be quite intricate to use, especially with respect to indexed vs non-indexed primvars, element size, the
                complexities of ``Vt.Array`` detach (copy-on-write) semantics, and the ambiguity of "native" attributes vs primvar attributes (e.g. mesh normals).

                This class aims to provide simpler entry points to avoid common mistakes with respect to ``UsdGeom.Primvar`` data handling.

                All of the USD authoring "define" functions in this library accept optional ``PrimvarData`` to define e.g normals, display colors, etc.
            
    """
    def __eq__(self, arg0: Int64PrimvarData) -> bool: 
        """
        Check that all data between two ``PrimvarData`` objects is identical.

        This differs from the equality operator in that it ensures the ``Vt.Array`` values and indices have not detached.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if all the member data is equal (but not necessarily identical arrays).
        """
    @typing.overload
    def __init__(self, interpolation: str, values: pxr.Vt.Int64Array, elementSize: int = -1) -> None: 
        """
        Construct non-indexed ``PrimvarData``.

        Note:
            To avoid immediate array iteration, validation does not occur during construction, and is deferred until ``isValid()`` is called.
            This may be counter-intuitive as ``PrimvarData`` provides read-only access, but full validation is often only possible within the context
            of specific surface topology, so premature validation would be redundant.

        Args:
            interpolation: The primvar interpolation. Must match ``UsdGeom.Primvar.IsValidInterpolation()`` to be considered valid.
            values: Read-only accessor to the values array.
            elementSize: Optional element size. This should be fairly uncommon.
                See [GetElementSize](https://openusd.org/release/api/class_usd_geom_primvar.html#a711c3088ebca00ca75308485151c8590) for details.

        Returns:
            The read-only ``PrimvarData``.



        Construct indexed ``PrimvarData``.

        Note:
            To avoid immediate array iteration, validation does not occur during construction, and is deferred until ``isValid()`` is called.
            This may be counter-intuitive as ``PrimvarData`` provides read-only access, but full validation is often only possible within the context
            of specific surface topology, so premature validation would be redundant.

        Args:
            interpolation: The primvar interpolation. Must match ``UsdGeom.Primvar.IsValidInterpolation()`` to be considered valid.
            values: Read-only accessor to the values array.
            indices: Read-only accessor to the indices array.
            elementSize: Optional element size. This should be fairly uncommon.
                See [GetElementSize](https://openusd.org/release/api/class_usd_geom_primvar.html#a711c3088ebca00ca75308485151c8590) for details.

        Returns:
            The read-only ``PrimvarData``.
        """
    @typing.overload
    def __init__(self, interpolation: str, values: pxr.Vt.Int64Array, indices: pxr.Vt.IntArray, elementSize: int = -1) -> None: ...
    def __ne__(self, arg0: Int64PrimvarData) -> bool: 
        """
        Check for in-equality between two ``PrimvarData`` objects.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if any member data is not equal (but does not guarantee identical arrays).
        """
    def __str__(self) -> str: ...
    def effectiveSize(self) -> int: 
        """
        The effective size of the data, having accounted for values, indices, and element size.

        This is the number of variable values that "really" exist, as far as a consumer is concerned. The indices & elementSize are used as a storage
        optimization, but the consumer should consider the effective size as the number of "deduplicated" individual values.

        Returns:
            The effective size of the data.
        """
    def elementSize(self) -> int: 
        """
        The element size.

        Any value less than 1 is considered "non authored" and indicates no element size. This should be the most common case, as element size is a
        fairly esoteric extension of ``UsdGeom.Primvar`` data to account for non-typed array strides such as spherical harmonics float[9] arrays.

        See ``UsdGeom.Primvar.GetElementSize()`` for more details.

        Returns:
            The primvar element size.
        """
    @staticmethod
    def getPrimvarData(primvar: pxr.UsdGeom.Primvar, time: pxr.Usd.TimeCode = nan) -> Int64PrimvarData: 
        """
        Construct a ``PrimvarData`` from a ``UsdGeom.Primvar`` that has already been authored.

        The primvar may be indexed, non-indexed, with or without elements, or it may not even be validly authored scene description.
        Use ``isValid()`` to confirm that valid data has been gathered.

        Args:
            primvar: The previously authored ``UsdGeom.Primvar``.
            time: The time at which the attribute values are read.

        Returns:
            The read-only ``PrimvarData``.
        """
    def hasIndices(self) -> bool: 
        """
        Whether this is indexed or non-indexed ``PrimvarData``

        Returns:
            Whether this is indexed or non-indexed ``PrimvarData``.
        """
    def index(self) -> bool: 
        """
        Update the values and indices of this ``PrimvarData`` object to avoid duplicate values.

        Updates will not be made in the following conditions:
            - If element size is greater than one.
            - If the existing indexing is efficient.
            - If there are no duplicate values.
            - If the existing indices are invalid

        Returns:
            True if the values and/or indices were modified.
        """
    def indices(self) -> pxr.Vt.IntArray: 
        """
        Access to the indices array.

        This method throws a runtime error if the ``PrimvarData`` is not indexed. For exception-free access, check ``hasIndices()`` before calling this.

        Note:
            It may contain an empty or invalid indices array. Use ``PrimvarData.isValid()`` to validate that the indices are not out-of-range.

        Returns:
            The primvar indices
        """
    def interpolation(self) -> str: 
        """
        The geometric interpolation.

        It may be an invalid interpolation. Use ``PrimvarData.isValid()`` or ``UsdGeom.Primvar.IsValidInterpolation()`` to confirm.

        Returns:
            The geometric interpolation.
        """
    def isIdentical(self, other: Int64PrimvarData) -> bool: 
        """
        Check that all data between two ``PrimvarData`` objects is identical.

        This differs from the equality operator in that it ensures the ``Vt.Array`` values and indices have not detached.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if all the member data is equal and arrays are identical.
        """
    def isValid(self) -> bool: 
        """
        Whether the data is valid or invalid.

        This is a validation check with respect to the ``PrimvarData`` itself & the requirements of ``UsdGeom.Prim``. It does not validate with respect to
        specific surface topology data, as no such data is available or consistant across ``UsdGeom.PointBased`` prim types.

        This validation checks the following, in this order, and returns false if any condition fails:

            - The interpolation matches ``UsdGeom.Primvar.IsValidInterpolation()``.
            - The values are not empty. Note that individual values may be invalid (e.g ``NaN`` values on a ``Vt.FloatArray``) but this will not be
              considered a failure, as some workflows allow for ``NaN`` to indicate non-authored elements or "holes" within the data.
            - If it is non-indexed, and has elements, that the values divide evenly by elementSize.
            - If it is indexed, and has elements, that the indices divide evenly by elementSize.
            - If it is indexed, that the indices are all within the expected range of the values array.

        Returns:
            Whether the data is valid or invalid.
        """
    def setPrimvar(self, primvar: pxr.UsdGeom.Primvar, time: pxr.Usd.TimeCode = nan) -> bool: 
        """
        Set data on an existing ``UsdGeom.Primvar`` from a ``PrimvarData`` that has already been authored.

        Any existing authored data on the primvar will be overwritten or blocked with the ``PrimvarData`` members.

        To copy data from one ``UsdGeom.Primvar`` to another, use ``data: PrimvarData = PrimvarData.get(primvar: UsdGeom.Primvar)`` to gather the data,
        then use ``setPrimvar(primvar: UsdGeom.Primvar)`` to author it.

        Args:
            primvar: The previously authored ``UsdGeom.Primvar``.
            time: The time at which the attribute values are written.

        Returns:
            Whether the ``UsdGeom.Primvar`` was completely authored from the member data.
            Any failure to author may leave the primvar in an unknown state (e.g. it may have been partially authored).
        """
    def values(self) -> pxr.Vt.Int64Array: 
        """
        Access to the values array.

        Bear in mind the values may need to be accessed via ``indices()`` or using an ``elementSize()`` stride.

        It may contain an empty or invalid values array.

        Returns:
            The primvar values.
        """
    __hash__ = None
    pass
class IntPrimvarData():
    """
    ``PrimvarData`` that holds ``Vt.IntArray`` values (e.g simple switch values or booleans consumable by shaders).

                This is a read-only class to manage all ``UsdGeom.Primvar`` data as a single object without risk of detaching (copying) arrays.

                ``UsdGeom.Primvars`` are often used when authoring ``UsdGeom.PointBased`` prims (e.g meshes, curves, and point clouds) to describe surface varying
                properties that can affect how a prim is rendered, or to drive a surface deformation.

                However, ``UsdGeom.Primvar`` data can be quite intricate to use, especially with respect to indexed vs non-indexed primvars, element size, the
                complexities of ``Vt.Array`` detach (copy-on-write) semantics, and the ambiguity of "native" attributes vs primvar attributes (e.g. mesh normals).

                This class aims to provide simpler entry points to avoid common mistakes with respect to ``UsdGeom.Primvar`` data handling.

                All of the USD authoring "define" functions in this library accept optional ``PrimvarData`` to define e.g normals, display colors, etc.
            
    """
    def __eq__(self, arg0: IntPrimvarData) -> bool: 
        """
        Check that all data between two ``PrimvarData`` objects is identical.

        This differs from the equality operator in that it ensures the ``Vt.Array`` values and indices have not detached.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if all the member data is equal (but not necessarily identical arrays).
        """
    @typing.overload
    def __init__(self, interpolation: str, values: pxr.Vt.IntArray, elementSize: int = -1) -> None: 
        """
        Construct non-indexed ``PrimvarData``.

        Note:
            To avoid immediate array iteration, validation does not occur during construction, and is deferred until ``isValid()`` is called.
            This may be counter-intuitive as ``PrimvarData`` provides read-only access, but full validation is often only possible within the context
            of specific surface topology, so premature validation would be redundant.

        Args:
            interpolation: The primvar interpolation. Must match ``UsdGeom.Primvar.IsValidInterpolation()`` to be considered valid.
            values: Read-only accessor to the values array.
            elementSize: Optional element size. This should be fairly uncommon.
                See [GetElementSize](https://openusd.org/release/api/class_usd_geom_primvar.html#a711c3088ebca00ca75308485151c8590) for details.

        Returns:
            The read-only ``PrimvarData``.



        Construct indexed ``PrimvarData``.

        Note:
            To avoid immediate array iteration, validation does not occur during construction, and is deferred until ``isValid()`` is called.
            This may be counter-intuitive as ``PrimvarData`` provides read-only access, but full validation is often only possible within the context
            of specific surface topology, so premature validation would be redundant.

        Args:
            interpolation: The primvar interpolation. Must match ``UsdGeom.Primvar.IsValidInterpolation()`` to be considered valid.
            values: Read-only accessor to the values array.
            indices: Read-only accessor to the indices array.
            elementSize: Optional element size. This should be fairly uncommon.
                See [GetElementSize](https://openusd.org/release/api/class_usd_geom_primvar.html#a711c3088ebca00ca75308485151c8590) for details.

        Returns:
            The read-only ``PrimvarData``.
        """
    @typing.overload
    def __init__(self, interpolation: str, values: pxr.Vt.IntArray, indices: pxr.Vt.IntArray, elementSize: int = -1) -> None: ...
    def __ne__(self, arg0: IntPrimvarData) -> bool: 
        """
        Check for in-equality between two ``PrimvarData`` objects.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if any member data is not equal (but does not guarantee identical arrays).
        """
    def __str__(self) -> str: ...
    def effectiveSize(self) -> int: 
        """
        The effective size of the data, having accounted for values, indices, and element size.

        This is the number of variable values that "really" exist, as far as a consumer is concerned. The indices & elementSize are used as a storage
        optimization, but the consumer should consider the effective size as the number of "deduplicated" individual values.

        Returns:
            The effective size of the data.
        """
    def elementSize(self) -> int: 
        """
        The element size.

        Any value less than 1 is considered "non authored" and indicates no element size. This should be the most common case, as element size is a
        fairly esoteric extension of ``UsdGeom.Primvar`` data to account for non-typed array strides such as spherical harmonics float[9] arrays.

        See ``UsdGeom.Primvar.GetElementSize()`` for more details.

        Returns:
            The primvar element size.
        """
    @staticmethod
    def getPrimvarData(primvar: pxr.UsdGeom.Primvar, time: pxr.Usd.TimeCode = nan) -> IntPrimvarData: 
        """
        Construct a ``PrimvarData`` from a ``UsdGeom.Primvar`` that has already been authored.

        The primvar may be indexed, non-indexed, with or without elements, or it may not even be validly authored scene description.
        Use ``isValid()`` to confirm that valid data has been gathered.

        Args:
            primvar: The previously authored ``UsdGeom.Primvar``.
            time: The time at which the attribute values are read.

        Returns:
            The read-only ``PrimvarData``.
        """
    def hasIndices(self) -> bool: 
        """
        Whether this is indexed or non-indexed ``PrimvarData``

        Returns:
            Whether this is indexed or non-indexed ``PrimvarData``.
        """
    def index(self) -> bool: 
        """
        Update the values and indices of this ``PrimvarData`` object to avoid duplicate values.

        Updates will not be made in the following conditions:
            - If element size is greater than one.
            - If the existing indexing is efficient.
            - If there are no duplicate values.
            - If the existing indices are invalid

        Returns:
            True if the values and/or indices were modified.
        """
    def indices(self) -> pxr.Vt.IntArray: 
        """
        Access to the indices array.

        This method throws a runtime error if the ``PrimvarData`` is not indexed. For exception-free access, check ``hasIndices()`` before calling this.

        Note:
            It may contain an empty or invalid indices array. Use ``PrimvarData.isValid()`` to validate that the indices are not out-of-range.

        Returns:
            The primvar indices
        """
    def interpolation(self) -> str: 
        """
        The geometric interpolation.

        It may be an invalid interpolation. Use ``PrimvarData.isValid()`` or ``UsdGeom.Primvar.IsValidInterpolation()`` to confirm.

        Returns:
            The geometric interpolation.
        """
    def isIdentical(self, other: IntPrimvarData) -> bool: 
        """
        Check that all data between two ``PrimvarData`` objects is identical.

        This differs from the equality operator in that it ensures the ``Vt.Array`` values and indices have not detached.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if all the member data is equal and arrays are identical.
        """
    def isValid(self) -> bool: 
        """
        Whether the data is valid or invalid.

        This is a validation check with respect to the ``PrimvarData`` itself & the requirements of ``UsdGeom.Prim``. It does not validate with respect to
        specific surface topology data, as no such data is available or consistant across ``UsdGeom.PointBased`` prim types.

        This validation checks the following, in this order, and returns false if any condition fails:

            - The interpolation matches ``UsdGeom.Primvar.IsValidInterpolation()``.
            - The values are not empty. Note that individual values may be invalid (e.g ``NaN`` values on a ``Vt.FloatArray``) but this will not be
              considered a failure, as some workflows allow for ``NaN`` to indicate non-authored elements or "holes" within the data.
            - If it is non-indexed, and has elements, that the values divide evenly by elementSize.
            - If it is indexed, and has elements, that the indices divide evenly by elementSize.
            - If it is indexed, that the indices are all within the expected range of the values array.

        Returns:
            Whether the data is valid or invalid.
        """
    def setPrimvar(self, primvar: pxr.UsdGeom.Primvar, time: pxr.Usd.TimeCode = nan) -> bool: 
        """
        Set data on an existing ``UsdGeom.Primvar`` from a ``PrimvarData`` that has already been authored.

        Any existing authored data on the primvar will be overwritten or blocked with the ``PrimvarData`` members.

        To copy data from one ``UsdGeom.Primvar`` to another, use ``data: PrimvarData = PrimvarData.get(primvar: UsdGeom.Primvar)`` to gather the data,
        then use ``setPrimvar(primvar: UsdGeom.Primvar)`` to author it.

        Args:
            primvar: The previously authored ``UsdGeom.Primvar``.
            time: The time at which the attribute values are written.

        Returns:
            Whether the ``UsdGeom.Primvar`` was completely authored from the member data.
            Any failure to author may leave the primvar in an unknown state (e.g. it may have been partially authored).
        """
    def values(self) -> pxr.Vt.IntArray: 
        """
        Access to the values array.

        Bear in mind the values may need to be accessed via ``indices()`` or using an ``elementSize()`` stride.

        It may contain an empty or invalid values array.

        Returns:
            The primvar values.
        """
    __hash__ = None
    pass
class JointFrame():
    """
    Specifies a position and rotation in the coordinate system specified by ``space``

    Note:
        The ``position`` and ``orientation`` are stored as doubles to avoid precision loss when aligning the joint to each body.
        This differs from the ``UsdPhysics.Joint`` schema, which stores them as floats. The final authored values on the
        ``PhysicsJoint`` prim will be cast down to floats to align with the schema.
    """
    class Space():
        """
        Coordinate systems in which a joint can be defined

        Members:

          Body0 : The joint is defined in the local space of ``body0``

          Body1 : The joint is defined in the local space of ``body1``

          World : The joint is defined in world space
        """
        def __eq__(self, other: object) -> bool: ...
        def __getstate__(self) -> int: ...
        def __hash__(self) -> int: ...
        def __index__(self) -> int: ...
        def __init__(self, value: int) -> None: ...
        def __int__(self) -> int: ...
        def __ne__(self, other: object) -> bool: ...
        def __repr__(self) -> str: ...
        def __setstate__(self, state: int) -> None: ...
        @property
        def name(self) -> str:
            """
            :type: str
            """
        @property
        def value(self) -> int:
            """
            :type: int
            """
        Body0: usdex.core._usdex_core.JointFrame.Space # value = <Space.Body0: 0>
        Body1: usdex.core._usdex_core.JointFrame.Space # value = <Space.Body1: 1>
        World: usdex.core._usdex_core.JointFrame.Space # value = <Space.World: 2>
        __members__: dict # value = {'Body0': <Space.Body0: 0>, 'Body1': <Space.Body1: 1>, 'World': <Space.World: 2>}
        pass
    @typing.overload
    def __init__(self) -> None: ...
    @staticmethod
    @typing.overload
    def __init__(*args, **kwargs) -> typing.Any: ...
    @property
    def orientation(self) -> pxr.Gf.Quatd:
        """
        The orientation of the joint

        :type: pxr.Gf.Quatd
        """
    @orientation.setter
    def orientation(self, arg0: pxr.Gf.Quatd) -> None:
        """
        The orientation of the joint
        """
    @property
    def position(self) -> pxr.Gf.Vec3d:
        """
        The position of the joint

        :type: pxr.Gf.Vec3d
        """
    @position.setter
    def position(self, arg0: pxr.Gf.Vec3d) -> None:
        """
        The position of the joint
        """
    @property
    def space(self) -> usdex::core::JointFrame::Space:
        """
        The space in which the joint is defined

        :type: usdex::core::JointFrame::Space
        """
    @space.setter
    def space(self, arg0: usdex::core::JointFrame::Space) -> None:
        """
        The space in which the joint is defined
        """
    pass
class NameCache():
    """
    The `NameCache` class provides a mechanism for generating unique and valid names for `UsdPrims` and their `UsdProperties`.

    The class ensures that generated names are valid according to OpenUSD name requirements and are unique within the context of sibling Prim and Property names.

    The cache provides a performant alternative to repeated queries by caching generated names and managing reserved names for Prims and Properties.

    Because reserved names are held in the cache, collisions can be avoided in cases where the Prim or Property has not been authored in the Stage.
    Names can be requested individually or in bulk, supporting a range of authoring patterns.
    Cache entries are based on prim path and are not unique between stages or layers.

    The name cache can be used in several authoring contexts, by providing a particular `parent` type:
    - `SdfPath`: Useful when generating names before authoring anything in USD.
    - `UsdPrim`: Useful when authoring in a `UsdStage`.
    - `SdfPrimSpec`: Useful when authoring in an `SdfLayer`

    When a cache entry is first created it will be populated with existing names depending on the scope of the supplied parent.
    - Given an `SdfPath` no names will be reserved
    - Given a `UsdPrim` it's existing child Prim and Property names (after composition) will be reserved
    - Given an `SdfPrimSpec` it's existing child Prim and Property names (before composition) will be reserved

    The parent must be stable to be useable as a cache key.
    - An `SdfPath` must be an absolute prim path containing no variant selections.
    - A `UsdPrim` must be valid.
    - An `SdfPrimSpec` must not be NULL or dormant.

    The pseudo root cannot have properties, therefore it is not useable as a parent for property related functions.

    Warning:

        This class does not automatically invalidate cached values based on changes to the prims from which values were cached.
        Additionally, a separate instance of this class should be used per-thread, calling methods from multiple threads is not safe.
    """
    def __init__(self) -> None: ...
    @typing.overload
    def clear(self, parent: pxr.Sdf.Path) -> None: 
        """
        Clear the reserved prim and property names for a prim.

        Args:
            parent: The parent prim path



        Clear the reserved prim and property names for a prim.

        Args:
            parent: The parent prim



        Clear the reserved prim and property names for a prim.

        Args:
            parent: The parent prim spec
        """
    @typing.overload
    def clear(self, parent: pxr.Usd.Prim) -> None: ...
    @typing.overload
    def clear(self, parent: pxr.Sdf.PrimSpec) -> None: ...
    @typing.overload
    def clearPrimNames(self, parent: pxr.Sdf.Path) -> None: 
        """
        Clear the reserved child names for a prim.

        Args:
            parent: The parent prim path



        Clear the reserved child names for a prim.

        Args:
            parent: The parent prim path



        Clear the reserved child names for a prim.

        Args:
            parent: The parent prim path
        """
    @typing.overload
    def clearPrimNames(self, parent: pxr.Usd.Prim) -> None: ...
    @typing.overload
    def clearPrimNames(self, parent: pxr.Sdf.PrimSpec) -> None: ...
    @typing.overload
    def clearPropertyNames(self, parent: pxr.Sdf.Path) -> None: 
        """
        Clear the reserved property names for a prim.

        Args:
            parent: The parent prim path



        Clear the reserved property names for a prim.

        Args:
            parent: The parent prim



        Clear the reserved property names for a prim.

        Args:
            parent: The parent prim spec
        """
    @typing.overload
    def clearPropertyNames(self, parent: pxr.Usd.Prim) -> None: ...
    @typing.overload
    def clearPropertyNames(self, parent: pxr.Sdf.PrimSpec) -> None: ...
    @typing.overload
    def getPrimName(self, parent: pxr.Sdf.Path, name: str) -> str: 
        """
        Make a name valid and unique for use as the name of a child of the given prim.

        An invalid token is returned on failure.

        Args:
            parent: The parent prim path
            name: Preferred name

        Returns:
            Valid and unique name token



        Make a name valid and unique for use as the name of a child of the given prim.

        An invalid token is returned on failure.

        Args:
            parent: The parent prim
            name: Preferred name

        Returns:
            Valid and unique name token



        Make a name valid and unique for use as the name of a child of the given prim.

        An invalid token is returned on failure.

        Args:
            parent: The parent prim spec
            name: Preferred name

        Returns:
            Valid and unique name token
        """
    @typing.overload
    def getPrimName(self, parent: pxr.Usd.Prim, name: str) -> str: ...
    @typing.overload
    def getPrimName(self, parent: pxr.Sdf.PrimSpec, name: str) -> str: ...
    @typing.overload
    def getPrimNames(self, parent: pxr.Sdf.Path, names: typing.List[str]) -> list(str): 
        """
        Make a list of names valid and unique for use as the names of a children of the given prim.

        Args:
            parent: The parent prim path
            names: Preferred names

        Returns:
            A vector of Valid and unique name tokens ordered to match the preferred names



        Make a list of names valid and unique for use as the names of a children of the given prim.

        Args:
            parent: The parent prim
            names: Preferred names

        Returns:
            A vector of Valid and unique name tokens ordered to match the preferred names



        Make a list of names valid and unique for use as the names of a children of the given prim.

        Args:
            parent: The parent prim spec
            names: Preferred names

        Returns:
            A vector of Valid and unique name tokens ordered to match the preferred names
        """
    @typing.overload
    def getPrimNames(self, parent: pxr.Usd.Prim, names: typing.List[str]) -> list(str): ...
    @typing.overload
    def getPrimNames(self, parent: pxr.Sdf.PrimSpec, names: typing.List[str]) -> list(str): ...
    @typing.overload
    def getPropertyName(self, parent: pxr.Sdf.Path, name: str) -> str: 
        """
        Make a name valid and unique for use as the name of a property on the given prim.

        An invalid token is returned on failure.

        Args:
            parent: The parent prim path
            name: Preferred name

        Returns:
            Valid and unique name token



        Make a name valid and unique for use as the name of a property on the given prim.

        An invalid token is returned on failure.

        Args:
            parent: The parent prim
            name: Preferred name

        Returns:
            Valid and unique name token



        Make a name valid and unique for use as the name of a property on the given prim.

        An invalid token is returned on failure.

        Args:
            parent: The parent prim spec
            name: Preferred name

        Returns:
            Valid and unique name token
        """
    @typing.overload
    def getPropertyName(self, parent: pxr.Usd.Prim, name: str) -> str: ...
    @typing.overload
    def getPropertyName(self, parent: pxr.Sdf.PrimSpec, name: str) -> str: ...
    @typing.overload
    def getPropertyNames(self, parent: pxr.Sdf.Path, names: typing.List[str]) -> list(str): 
        """
        Make a list of names valid and unique for use as the names of properties on the given prim.

        Args:
            parent: The parent prim path
            names: Preferred names

        Returns:
            A vector of Valid and unique name tokens ordered to match the preferred names



        Make a list of names valid and unique for use as the names of properties on the given prim.

        Args:
            parent: The parent prim
            names: Preferred names

        Returns:
            A vector of Valid and unique name tokens ordered to match the preferred names



        Make a list of names valid and unique for use as the names of properties on the given prim.

        Args:
            parent: The parent prim spec
            names: Preferred names

        Returns:
            A vector of Valid and unique name tokens ordered to match the preferred names
        """
    @typing.overload
    def getPropertyNames(self, parent: pxr.Usd.Prim, names: typing.List[str]) -> list(str): ...
    @typing.overload
    def getPropertyNames(self, parent: pxr.Sdf.PrimSpec, names: typing.List[str]) -> list(str): ...
    @typing.overload
    def update(self, parent: pxr.Usd.Prim) -> None: 
        """
        Update the reserved child and property names for a prim to include existing children and properties.

        Args:
            parent: The parent prim



        Update the reserved child and property names for a prim to include existing children and properties.

        Args:
            parent: The parent prim spec
        """
    @typing.overload
    def update(self, parent: pxr.Sdf.PrimSpec) -> None: ...
    @typing.overload
    def updatePrimNames(self, parent: pxr.Usd.Prim) -> None: 
        """
        Update the reserved child names for a prim to include existing children.

        Args:
            parent: The parent prim



        Update the reserved child names for a prim to include existing children.

        Args:
            parent: The parent prim spec
        """
    @typing.overload
    def updatePrimNames(self, parent: pxr.Sdf.PrimSpec) -> None: ...
    @typing.overload
    def updatePropertyNames(self, parent: pxr.Usd.Prim) -> None: 
        """
        Update the reserved property names for a prim to include existing properties.

        Args:
            parent: The parent prim



        Update the reserved property names for a prim to include existing properties.

        Args:
            parent: The parent prim spec
        """
    @typing.overload
    def updatePropertyNames(self, parent: pxr.Sdf.PrimSpec) -> None: ...
    pass
class RotationOrder():
    """
    Enumerates the rotation order of the 3-angle Euler rotation.

    Members:

      eXyz

      eXzy

      eYxz

      eYzx

      eZxy

      eZyx
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    __members__: dict # value = {'eXyz': <RotationOrder.eXyz: 0>, 'eXzy': <RotationOrder.eXzy: 1>, 'eYxz': <RotationOrder.eYxz: 2>, 'eYzx': <RotationOrder.eYzx: 3>, 'eZxy': <RotationOrder.eZxy: 4>, 'eZyx': <RotationOrder.eZyx: 5>}
    eXyz: usdex.core._usdex_core.RotationOrder # value = <RotationOrder.eXyz: 0>
    eXzy: usdex.core._usdex_core.RotationOrder # value = <RotationOrder.eXzy: 1>
    eYxz: usdex.core._usdex_core.RotationOrder # value = <RotationOrder.eYxz: 2>
    eYzx: usdex.core._usdex_core.RotationOrder # value = <RotationOrder.eYzx: 3>
    eZxy: usdex.core._usdex_core.RotationOrder # value = <RotationOrder.eZxy: 4>
    eZyx: usdex.core._usdex_core.RotationOrder # value = <RotationOrder.eZyx: 5>
    pass
class StringPrimvarData():
    """
    ``PrimvarData`` that holds ``Vt.StringArray`` values (e.g human readable descriptors).

                This is a read-only class to manage all ``UsdGeom.Primvar`` data as a single object without risk of detaching (copying) arrays.

                ``UsdGeom.Primvars`` are often used when authoring ``UsdGeom.PointBased`` prims (e.g meshes, curves, and point clouds) to describe surface varying
                properties that can affect how a prim is rendered, or to drive a surface deformation.

                However, ``UsdGeom.Primvar`` data can be quite intricate to use, especially with respect to indexed vs non-indexed primvars, element size, the
                complexities of ``Vt.Array`` detach (copy-on-write) semantics, and the ambiguity of "native" attributes vs primvar attributes (e.g. mesh normals).

                This class aims to provide simpler entry points to avoid common mistakes with respect to ``UsdGeom.Primvar`` data handling.

                All of the USD authoring "define" functions in this library accept optional ``PrimvarData`` to define e.g normals, display colors, etc.
            
    """
    def __eq__(self, arg0: StringPrimvarData) -> bool: 
        """
        Check that all data between two ``PrimvarData`` objects is identical.

        This differs from the equality operator in that it ensures the ``Vt.Array`` values and indices have not detached.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if all the member data is equal (but not necessarily identical arrays).
        """
    @typing.overload
    def __init__(self, interpolation: str, values: pxr.Vt.StringArray, elementSize: int = -1) -> None: 
        """
        Construct non-indexed ``PrimvarData``.

        Note:
            To avoid immediate array iteration, validation does not occur during construction, and is deferred until ``isValid()`` is called.
            This may be counter-intuitive as ``PrimvarData`` provides read-only access, but full validation is often only possible within the context
            of specific surface topology, so premature validation would be redundant.

        Args:
            interpolation: The primvar interpolation. Must match ``UsdGeom.Primvar.IsValidInterpolation()`` to be considered valid.
            values: Read-only accessor to the values array.
            elementSize: Optional element size. This should be fairly uncommon.
                See [GetElementSize](https://openusd.org/release/api/class_usd_geom_primvar.html#a711c3088ebca00ca75308485151c8590) for details.

        Returns:
            The read-only ``PrimvarData``.



        Construct indexed ``PrimvarData``.

        Note:
            To avoid immediate array iteration, validation does not occur during construction, and is deferred until ``isValid()`` is called.
            This may be counter-intuitive as ``PrimvarData`` provides read-only access, but full validation is often only possible within the context
            of specific surface topology, so premature validation would be redundant.

        Args:
            interpolation: The primvar interpolation. Must match ``UsdGeom.Primvar.IsValidInterpolation()`` to be considered valid.
            values: Read-only accessor to the values array.
            indices: Read-only accessor to the indices array.
            elementSize: Optional element size. This should be fairly uncommon.
                See [GetElementSize](https://openusd.org/release/api/class_usd_geom_primvar.html#a711c3088ebca00ca75308485151c8590) for details.

        Returns:
            The read-only ``PrimvarData``.
        """
    @typing.overload
    def __init__(self, interpolation: str, values: pxr.Vt.StringArray, indices: pxr.Vt.IntArray, elementSize: int = -1) -> None: ...
    def __ne__(self, arg0: StringPrimvarData) -> bool: 
        """
        Check for in-equality between two ``PrimvarData`` objects.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if any member data is not equal (but does not guarantee identical arrays).
        """
    def __str__(self) -> str: ...
    def effectiveSize(self) -> int: 
        """
        The effective size of the data, having accounted for values, indices, and element size.

        This is the number of variable values that "really" exist, as far as a consumer is concerned. The indices & elementSize are used as a storage
        optimization, but the consumer should consider the effective size as the number of "deduplicated" individual values.

        Returns:
            The effective size of the data.
        """
    def elementSize(self) -> int: 
        """
        The element size.

        Any value less than 1 is considered "non authored" and indicates no element size. This should be the most common case, as element size is a
        fairly esoteric extension of ``UsdGeom.Primvar`` data to account for non-typed array strides such as spherical harmonics float[9] arrays.

        See ``UsdGeom.Primvar.GetElementSize()`` for more details.

        Returns:
            The primvar element size.
        """
    @staticmethod
    def getPrimvarData(primvar: pxr.UsdGeom.Primvar, time: pxr.Usd.TimeCode = nan) -> StringPrimvarData: 
        """
        Construct a ``PrimvarData`` from a ``UsdGeom.Primvar`` that has already been authored.

        The primvar may be indexed, non-indexed, with or without elements, or it may not even be validly authored scene description.
        Use ``isValid()`` to confirm that valid data has been gathered.

        Args:
            primvar: The previously authored ``UsdGeom.Primvar``.
            time: The time at which the attribute values are read.

        Returns:
            The read-only ``PrimvarData``.
        """
    def hasIndices(self) -> bool: 
        """
        Whether this is indexed or non-indexed ``PrimvarData``

        Returns:
            Whether this is indexed or non-indexed ``PrimvarData``.
        """
    def index(self) -> bool: 
        """
        Update the values and indices of this ``PrimvarData`` object to avoid duplicate values.

        Updates will not be made in the following conditions:
            - If element size is greater than one.
            - If the existing indexing is efficient.
            - If there are no duplicate values.
            - If the existing indices are invalid

        Returns:
            True if the values and/or indices were modified.
        """
    def indices(self) -> pxr.Vt.IntArray: 
        """
        Access to the indices array.

        This method throws a runtime error if the ``PrimvarData`` is not indexed. For exception-free access, check ``hasIndices()`` before calling this.

        Note:
            It may contain an empty or invalid indices array. Use ``PrimvarData.isValid()`` to validate that the indices are not out-of-range.

        Returns:
            The primvar indices
        """
    def interpolation(self) -> str: 
        """
        The geometric interpolation.

        It may be an invalid interpolation. Use ``PrimvarData.isValid()`` or ``UsdGeom.Primvar.IsValidInterpolation()`` to confirm.

        Returns:
            The geometric interpolation.
        """
    def isIdentical(self, other: StringPrimvarData) -> bool: 
        """
        Check that all data between two ``PrimvarData`` objects is identical.

        This differs from the equality operator in that it ensures the ``Vt.Array`` values and indices have not detached.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if all the member data is equal and arrays are identical.
        """
    def isValid(self) -> bool: 
        """
        Whether the data is valid or invalid.

        This is a validation check with respect to the ``PrimvarData`` itself & the requirements of ``UsdGeom.Prim``. It does not validate with respect to
        specific surface topology data, as no such data is available or consistant across ``UsdGeom.PointBased`` prim types.

        This validation checks the following, in this order, and returns false if any condition fails:

            - The interpolation matches ``UsdGeom.Primvar.IsValidInterpolation()``.
            - The values are not empty. Note that individual values may be invalid (e.g ``NaN`` values on a ``Vt.FloatArray``) but this will not be
              considered a failure, as some workflows allow for ``NaN`` to indicate non-authored elements or "holes" within the data.
            - If it is non-indexed, and has elements, that the values divide evenly by elementSize.
            - If it is indexed, and has elements, that the indices divide evenly by elementSize.
            - If it is indexed, that the indices are all within the expected range of the values array.

        Returns:
            Whether the data is valid or invalid.
        """
    def setPrimvar(self, primvar: pxr.UsdGeom.Primvar, time: pxr.Usd.TimeCode = nan) -> bool: 
        """
        Set data on an existing ``UsdGeom.Primvar`` from a ``PrimvarData`` that has already been authored.

        Any existing authored data on the primvar will be overwritten or blocked with the ``PrimvarData`` members.

        To copy data from one ``UsdGeom.Primvar`` to another, use ``data: PrimvarData = PrimvarData.get(primvar: UsdGeom.Primvar)`` to gather the data,
        then use ``setPrimvar(primvar: UsdGeom.Primvar)`` to author it.

        Args:
            primvar: The previously authored ``UsdGeom.Primvar``.
            time: The time at which the attribute values are written.

        Returns:
            Whether the ``UsdGeom.Primvar`` was completely authored from the member data.
            Any failure to author may leave the primvar in an unknown state (e.g. it may have been partially authored).
        """
    def values(self) -> pxr.Vt.StringArray: 
        """
        Access to the values array.

        Bear in mind the values may need to be accessed via ``indices()`` or using an ``elementSize()`` stride.

        It may contain an empty or invalid values array.

        Returns:
            The primvar values.
        """
    __hash__ = None
    pass
class TokenPrimvarData():
    """
    ``PrimvarData`` that holds ``Vt.TokenArray`` values (e.g more efficient human readable descriptors).

    This is a more efficient format than raw strings if you have many repeated values across different prims.

    Note:
        ``TfToken`` lifetime lasts the entire process. Too many tokens in memory may consume resources somewhat unexpectedly.


    This is a read-only class to manage all ``UsdGeom.Primvar`` data as a single object without risk of detaching (copying) arrays.

    ``UsdGeom.Primvars`` are often used when authoring ``UsdGeom.PointBased`` prims (e.g meshes, curves, and point clouds) to describe surface varying
    properties that can affect how a prim is rendered, or to drive a surface deformation.

    However, ``UsdGeom.Primvar`` data can be quite intricate to use, especially with respect to indexed vs non-indexed primvars, element size, the
    complexities of ``Vt.Array`` detach (copy-on-write) semantics, and the ambiguity of "native" attributes vs primvar attributes (e.g. mesh normals).

    This class aims to provide simpler entry points to avoid common mistakes with respect to ``UsdGeom.Primvar`` data handling.

    All of the USD authoring "define" functions in this library accept optional ``PrimvarData`` to define e.g normals, display colors, etc.
    """
    def __eq__(self, arg0: TokenPrimvarData) -> bool: 
        """
        Check that all data between two ``PrimvarData`` objects is identical.

        This differs from the equality operator in that it ensures the ``Vt.Array`` values and indices have not detached.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if all the member data is equal (but not necessarily identical arrays).
        """
    @typing.overload
    def __init__(self, interpolation: str, values: pxr.Vt.TokenArray, elementSize: int = -1) -> None: 
        """
        Construct non-indexed ``PrimvarData``.

        Note:
            To avoid immediate array iteration, validation does not occur during construction, and is deferred until ``isValid()`` is called.
            This may be counter-intuitive as ``PrimvarData`` provides read-only access, but full validation is often only possible within the context
            of specific surface topology, so premature validation would be redundant.

        Args:
            interpolation: The primvar interpolation. Must match ``UsdGeom.Primvar.IsValidInterpolation()`` to be considered valid.
            values: Read-only accessor to the values array.
            elementSize: Optional element size. This should be fairly uncommon.
                See [GetElementSize](https://openusd.org/release/api/class_usd_geom_primvar.html#a711c3088ebca00ca75308485151c8590) for details.

        Returns:
            The read-only ``PrimvarData``.



        Construct indexed ``PrimvarData``.

        Note:
            To avoid immediate array iteration, validation does not occur during construction, and is deferred until ``isValid()`` is called.
            This may be counter-intuitive as ``PrimvarData`` provides read-only access, but full validation is often only possible within the context
            of specific surface topology, so premature validation would be redundant.

        Args:
            interpolation: The primvar interpolation. Must match ``UsdGeom.Primvar.IsValidInterpolation()`` to be considered valid.
            values: Read-only accessor to the values array.
            indices: Read-only accessor to the indices array.
            elementSize: Optional element size. This should be fairly uncommon.
                See [GetElementSize](https://openusd.org/release/api/class_usd_geom_primvar.html#a711c3088ebca00ca75308485151c8590) for details.

        Returns:
            The read-only ``PrimvarData``.
        """
    @typing.overload
    def __init__(self, interpolation: str, values: pxr.Vt.TokenArray, indices: pxr.Vt.IntArray, elementSize: int = -1) -> None: ...
    def __ne__(self, arg0: TokenPrimvarData) -> bool: 
        """
        Check for in-equality between two ``PrimvarData`` objects.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if any member data is not equal (but does not guarantee identical arrays).
        """
    def __str__(self) -> str: ...
    def effectiveSize(self) -> int: 
        """
        The effective size of the data, having accounted for values, indices, and element size.

        This is the number of variable values that "really" exist, as far as a consumer is concerned. The indices & elementSize are used as a storage
        optimization, but the consumer should consider the effective size as the number of "deduplicated" individual values.

        Returns:
            The effective size of the data.
        """
    def elementSize(self) -> int: 
        """
        The element size.

        Any value less than 1 is considered "non authored" and indicates no element size. This should be the most common case, as element size is a
        fairly esoteric extension of ``UsdGeom.Primvar`` data to account for non-typed array strides such as spherical harmonics float[9] arrays.

        See ``UsdGeom.Primvar.GetElementSize()`` for more details.

        Returns:
            The primvar element size.
        """
    @staticmethod
    def getPrimvarData(primvar: pxr.UsdGeom.Primvar, time: pxr.Usd.TimeCode = nan) -> TokenPrimvarData: 
        """
        Construct a ``PrimvarData`` from a ``UsdGeom.Primvar`` that has already been authored.

        The primvar may be indexed, non-indexed, with or without elements, or it may not even be validly authored scene description.
        Use ``isValid()`` to confirm that valid data has been gathered.

        Args:
            primvar: The previously authored ``UsdGeom.Primvar``.
            time: The time at which the attribute values are read.

        Returns:
            The read-only ``PrimvarData``.
        """
    def hasIndices(self) -> bool: 
        """
        Whether this is indexed or non-indexed ``PrimvarData``

        Returns:
            Whether this is indexed or non-indexed ``PrimvarData``.
        """
    def index(self) -> bool: 
        """
        Update the values and indices of this ``PrimvarData`` object to avoid duplicate values.

        Updates will not be made in the following conditions:
            - If element size is greater than one.
            - If the existing indexing is efficient.
            - If there are no duplicate values.
            - If the existing indices are invalid

        Returns:
            True if the values and/or indices were modified.
        """
    def indices(self) -> pxr.Vt.IntArray: 
        """
        Access to the indices array.

        This method throws a runtime error if the ``PrimvarData`` is not indexed. For exception-free access, check ``hasIndices()`` before calling this.

        Note:
            It may contain an empty or invalid indices array. Use ``PrimvarData.isValid()`` to validate that the indices are not out-of-range.

        Returns:
            The primvar indices
        """
    def interpolation(self) -> str: 
        """
        The geometric interpolation.

        It may be an invalid interpolation. Use ``PrimvarData.isValid()`` or ``UsdGeom.Primvar.IsValidInterpolation()`` to confirm.

        Returns:
            The geometric interpolation.
        """
    def isIdentical(self, other: TokenPrimvarData) -> bool: 
        """
        Check that all data between two ``PrimvarData`` objects is identical.

        This differs from the equality operator in that it ensures the ``Vt.Array`` values and indices have not detached.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if all the member data is equal and arrays are identical.
        """
    def isValid(self) -> bool: 
        """
        Whether the data is valid or invalid.

        This is a validation check with respect to the ``PrimvarData`` itself & the requirements of ``UsdGeom.Prim``. It does not validate with respect to
        specific surface topology data, as no such data is available or consistant across ``UsdGeom.PointBased`` prim types.

        This validation checks the following, in this order, and returns false if any condition fails:

            - The interpolation matches ``UsdGeom.Primvar.IsValidInterpolation()``.
            - The values are not empty. Note that individual values may be invalid (e.g ``NaN`` values on a ``Vt.FloatArray``) but this will not be
              considered a failure, as some workflows allow for ``NaN`` to indicate non-authored elements or "holes" within the data.
            - If it is non-indexed, and has elements, that the values divide evenly by elementSize.
            - If it is indexed, and has elements, that the indices divide evenly by elementSize.
            - If it is indexed, that the indices are all within the expected range of the values array.

        Returns:
            Whether the data is valid or invalid.
        """
    def setPrimvar(self, primvar: pxr.UsdGeom.Primvar, time: pxr.Usd.TimeCode = nan) -> bool: 
        """
        Set data on an existing ``UsdGeom.Primvar`` from a ``PrimvarData`` that has already been authored.

        Any existing authored data on the primvar will be overwritten or blocked with the ``PrimvarData`` members.

        To copy data from one ``UsdGeom.Primvar`` to another, use ``data: PrimvarData = PrimvarData.get(primvar: UsdGeom.Primvar)`` to gather the data,
        then use ``setPrimvar(primvar: UsdGeom.Primvar)`` to author it.

        Args:
            primvar: The previously authored ``UsdGeom.Primvar``.
            time: The time at which the attribute values are written.

        Returns:
            Whether the ``UsdGeom.Primvar`` was completely authored from the member data.
            Any failure to author may leave the primvar in an unknown state (e.g. it may have been partially authored).
        """
    def values(self) -> pxr.Vt.TokenArray: 
        """
        Access to the values array.

        Bear in mind the values may need to be accessed via ``indices()`` or using an ``elementSize()`` stride.

        It may contain an empty or invalid values array.

        Returns:
            The primvar values.
        """
    __hash__ = None
    pass
class ValidChildNameCache():
    """
    A caching mechanism for valid and unique child prim names.

    For best performance, this object should be reused for multiple name requests.

    It is not valid to request child names from prims from multiple stages as only the prim path is used as the cache key.

    Warning:

        This class does not automatically invalidate cached values based on changes to the stage from which values were cached.
        Additionally, a separate instance of this class should be used per-thread, calling methods from multiple threads is not safe.
    """
    def __init__(self) -> None: ...
    def clear(self, clear: pxr.Usd.Prim) -> None: 
        """
        Clear the name cache for a Prim.

        Args:
            prim: The prim that child names should be cleared for.
        """
    def getValidChildName(self, prim: pxr.Usd.Prim, name: str) -> str: 
        """
        Take a prim and a preferred name. Return a valid and unique name for use as the child name of the given prim.

        Args:
            prim: The prim that the child name should be valid for.
            names: Preferred prim name.

        Returns:
            Valid and unique name.
        """
    def getValidChildNames(self, prim: pxr.Usd.Prim, names: typing.List[str]) -> list(str): 
        """
        Take a prim and a vector of the preferred names. Return a matching vector of valid and unique names as the child names of the given prim.

        Args:

            prim: The USD prim where the given prim names should live under.
            names: A vector of preferred prim names.

        Returns:
            A vector of valid and unique names.
        """
    def update(self, prim: pxr.Usd.Prim) -> None: 
        """
        Update the name cache for a Prim to include all existing children.

        This does not clear the cache, so any names that have been previously returned will still be reserved.

        Args:
            prim: The prim that child names should be updated for.
        """
    pass
class Vec2fPrimvarData():
    """
    ``PrimvarData`` that holds ``Vt.Vec2fArray`` values (e.g texture coordinates).

                This is a read-only class to manage all ``UsdGeom.Primvar`` data as a single object without risk of detaching (copying) arrays.

                ``UsdGeom.Primvars`` are often used when authoring ``UsdGeom.PointBased`` prims (e.g meshes, curves, and point clouds) to describe surface varying
                properties that can affect how a prim is rendered, or to drive a surface deformation.

                However, ``UsdGeom.Primvar`` data can be quite intricate to use, especially with respect to indexed vs non-indexed primvars, element size, the
                complexities of ``Vt.Array`` detach (copy-on-write) semantics, and the ambiguity of "native" attributes vs primvar attributes (e.g. mesh normals).

                This class aims to provide simpler entry points to avoid common mistakes with respect to ``UsdGeom.Primvar`` data handling.

                All of the USD authoring "define" functions in this library accept optional ``PrimvarData`` to define e.g normals, display colors, etc.
            
    """
    def __eq__(self, arg0: Vec2fPrimvarData) -> bool: 
        """
        Check that all data between two ``PrimvarData`` objects is identical.

        This differs from the equality operator in that it ensures the ``Vt.Array`` values and indices have not detached.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if all the member data is equal (but not necessarily identical arrays).
        """
    @typing.overload
    def __init__(self, interpolation: str, values: pxr.Vt.Vec2fArray, elementSize: int = -1) -> None: 
        """
        Construct non-indexed ``PrimvarData``.

        Note:
            To avoid immediate array iteration, validation does not occur during construction, and is deferred until ``isValid()`` is called.
            This may be counter-intuitive as ``PrimvarData`` provides read-only access, but full validation is often only possible within the context
            of specific surface topology, so premature validation would be redundant.

        Args:
            interpolation: The primvar interpolation. Must match ``UsdGeom.Primvar.IsValidInterpolation()`` to be considered valid.
            values: Read-only accessor to the values array.
            elementSize: Optional element size. This should be fairly uncommon.
                See [GetElementSize](https://openusd.org/release/api/class_usd_geom_primvar.html#a711c3088ebca00ca75308485151c8590) for details.

        Returns:
            The read-only ``PrimvarData``.



        Construct indexed ``PrimvarData``.

        Note:
            To avoid immediate array iteration, validation does not occur during construction, and is deferred until ``isValid()`` is called.
            This may be counter-intuitive as ``PrimvarData`` provides read-only access, but full validation is often only possible within the context
            of specific surface topology, so premature validation would be redundant.

        Args:
            interpolation: The primvar interpolation. Must match ``UsdGeom.Primvar.IsValidInterpolation()`` to be considered valid.
            values: Read-only accessor to the values array.
            indices: Read-only accessor to the indices array.
            elementSize: Optional element size. This should be fairly uncommon.
                See [GetElementSize](https://openusd.org/release/api/class_usd_geom_primvar.html#a711c3088ebca00ca75308485151c8590) for details.

        Returns:
            The read-only ``PrimvarData``.
        """
    @typing.overload
    def __init__(self, interpolation: str, values: pxr.Vt.Vec2fArray, indices: pxr.Vt.IntArray, elementSize: int = -1) -> None: ...
    def __ne__(self, arg0: Vec2fPrimvarData) -> bool: 
        """
        Check for in-equality between two ``PrimvarData`` objects.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if any member data is not equal (but does not guarantee identical arrays).
        """
    def __str__(self) -> str: ...
    def effectiveSize(self) -> int: 
        """
        The effective size of the data, having accounted for values, indices, and element size.

        This is the number of variable values that "really" exist, as far as a consumer is concerned. The indices & elementSize are used as a storage
        optimization, but the consumer should consider the effective size as the number of "deduplicated" individual values.

        Returns:
            The effective size of the data.
        """
    def elementSize(self) -> int: 
        """
        The element size.

        Any value less than 1 is considered "non authored" and indicates no element size. This should be the most common case, as element size is a
        fairly esoteric extension of ``UsdGeom.Primvar`` data to account for non-typed array strides such as spherical harmonics float[9] arrays.

        See ``UsdGeom.Primvar.GetElementSize()`` for more details.

        Returns:
            The primvar element size.
        """
    @staticmethod
    def getPrimvarData(primvar: pxr.UsdGeom.Primvar, time: pxr.Usd.TimeCode = nan) -> Vec2fPrimvarData: 
        """
        Construct a ``PrimvarData`` from a ``UsdGeom.Primvar`` that has already been authored.

        The primvar may be indexed, non-indexed, with or without elements, or it may not even be validly authored scene description.
        Use ``isValid()`` to confirm that valid data has been gathered.

        Args:
            primvar: The previously authored ``UsdGeom.Primvar``.
            time: The time at which the attribute values are read.

        Returns:
            The read-only ``PrimvarData``.
        """
    def hasIndices(self) -> bool: 
        """
        Whether this is indexed or non-indexed ``PrimvarData``

        Returns:
            Whether this is indexed or non-indexed ``PrimvarData``.
        """
    def index(self) -> bool: 
        """
        Update the values and indices of this ``PrimvarData`` object to avoid duplicate values.

        Updates will not be made in the following conditions:
            - If element size is greater than one.
            - If the existing indexing is efficient.
            - If there are no duplicate values.
            - If the existing indices are invalid

        Returns:
            True if the values and/or indices were modified.
        """
    def indices(self) -> pxr.Vt.IntArray: 
        """
        Access to the indices array.

        This method throws a runtime error if the ``PrimvarData`` is not indexed. For exception-free access, check ``hasIndices()`` before calling this.

        Note:
            It may contain an empty or invalid indices array. Use ``PrimvarData.isValid()`` to validate that the indices are not out-of-range.

        Returns:
            The primvar indices
        """
    def interpolation(self) -> str: 
        """
        The geometric interpolation.

        It may be an invalid interpolation. Use ``PrimvarData.isValid()`` or ``UsdGeom.Primvar.IsValidInterpolation()`` to confirm.

        Returns:
            The geometric interpolation.
        """
    def isIdentical(self, other: Vec2fPrimvarData) -> bool: 
        """
        Check that all data between two ``PrimvarData`` objects is identical.

        This differs from the equality operator in that it ensures the ``Vt.Array`` values and indices have not detached.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if all the member data is equal and arrays are identical.
        """
    def isValid(self) -> bool: 
        """
        Whether the data is valid or invalid.

        This is a validation check with respect to the ``PrimvarData`` itself & the requirements of ``UsdGeom.Prim``. It does not validate with respect to
        specific surface topology data, as no such data is available or consistant across ``UsdGeom.PointBased`` prim types.

        This validation checks the following, in this order, and returns false if any condition fails:

            - The interpolation matches ``UsdGeom.Primvar.IsValidInterpolation()``.
            - The values are not empty. Note that individual values may be invalid (e.g ``NaN`` values on a ``Vt.FloatArray``) but this will not be
              considered a failure, as some workflows allow for ``NaN`` to indicate non-authored elements or "holes" within the data.
            - If it is non-indexed, and has elements, that the values divide evenly by elementSize.
            - If it is indexed, and has elements, that the indices divide evenly by elementSize.
            - If it is indexed, that the indices are all within the expected range of the values array.

        Returns:
            Whether the data is valid or invalid.
        """
    def setPrimvar(self, primvar: pxr.UsdGeom.Primvar, time: pxr.Usd.TimeCode = nan) -> bool: 
        """
        Set data on an existing ``UsdGeom.Primvar`` from a ``PrimvarData`` that has already been authored.

        Any existing authored data on the primvar will be overwritten or blocked with the ``PrimvarData`` members.

        To copy data from one ``UsdGeom.Primvar`` to another, use ``data: PrimvarData = PrimvarData.get(primvar: UsdGeom.Primvar)`` to gather the data,
        then use ``setPrimvar(primvar: UsdGeom.Primvar)`` to author it.

        Args:
            primvar: The previously authored ``UsdGeom.Primvar``.
            time: The time at which the attribute values are written.

        Returns:
            Whether the ``UsdGeom.Primvar`` was completely authored from the member data.
            Any failure to author may leave the primvar in an unknown state (e.g. it may have been partially authored).
        """
    def values(self) -> pxr.Vt.Vec2fArray: 
        """
        Access to the values array.

        Bear in mind the values may need to be accessed via ``indices()`` or using an ``elementSize()`` stride.

        It may contain an empty or invalid values array.

        Returns:
            The primvar values.
        """
    __hash__ = None
    pass
class Vec3fPrimvarData():
    """
    ``PrimvarData`` that holds ``Vt.Vec3fArray`` values (e.g normals, colors, or other vectors).

                This is a read-only class to manage all ``UsdGeom.Primvar`` data as a single object without risk of detaching (copying) arrays.

                ``UsdGeom.Primvars`` are often used when authoring ``UsdGeom.PointBased`` prims (e.g meshes, curves, and point clouds) to describe surface varying
                properties that can affect how a prim is rendered, or to drive a surface deformation.

                However, ``UsdGeom.Primvar`` data can be quite intricate to use, especially with respect to indexed vs non-indexed primvars, element size, the
                complexities of ``Vt.Array`` detach (copy-on-write) semantics, and the ambiguity of "native" attributes vs primvar attributes (e.g. mesh normals).

                This class aims to provide simpler entry points to avoid common mistakes with respect to ``UsdGeom.Primvar`` data handling.

                All of the USD authoring "define" functions in this library accept optional ``PrimvarData`` to define e.g normals, display colors, etc.
            
    """
    def __eq__(self, arg0: Vec3fPrimvarData) -> bool: 
        """
        Check that all data between two ``PrimvarData`` objects is identical.

        This differs from the equality operator in that it ensures the ``Vt.Array`` values and indices have not detached.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if all the member data is equal (but not necessarily identical arrays).
        """
    @typing.overload
    def __init__(self, interpolation: str, values: pxr.Vt.Vec3fArray, elementSize: int = -1) -> None: 
        """
        Construct non-indexed ``PrimvarData``.

        Note:
            To avoid immediate array iteration, validation does not occur during construction, and is deferred until ``isValid()`` is called.
            This may be counter-intuitive as ``PrimvarData`` provides read-only access, but full validation is often only possible within the context
            of specific surface topology, so premature validation would be redundant.

        Args:
            interpolation: The primvar interpolation. Must match ``UsdGeom.Primvar.IsValidInterpolation()`` to be considered valid.
            values: Read-only accessor to the values array.
            elementSize: Optional element size. This should be fairly uncommon.
                See [GetElementSize](https://openusd.org/release/api/class_usd_geom_primvar.html#a711c3088ebca00ca75308485151c8590) for details.

        Returns:
            The read-only ``PrimvarData``.



        Construct indexed ``PrimvarData``.

        Note:
            To avoid immediate array iteration, validation does not occur during construction, and is deferred until ``isValid()`` is called.
            This may be counter-intuitive as ``PrimvarData`` provides read-only access, but full validation is often only possible within the context
            of specific surface topology, so premature validation would be redundant.

        Args:
            interpolation: The primvar interpolation. Must match ``UsdGeom.Primvar.IsValidInterpolation()`` to be considered valid.
            values: Read-only accessor to the values array.
            indices: Read-only accessor to the indices array.
            elementSize: Optional element size. This should be fairly uncommon.
                See [GetElementSize](https://openusd.org/release/api/class_usd_geom_primvar.html#a711c3088ebca00ca75308485151c8590) for details.

        Returns:
            The read-only ``PrimvarData``.
        """
    @typing.overload
    def __init__(self, interpolation: str, values: pxr.Vt.Vec3fArray, indices: pxr.Vt.IntArray, elementSize: int = -1) -> None: ...
    def __ne__(self, arg0: Vec3fPrimvarData) -> bool: 
        """
        Check for in-equality between two ``PrimvarData`` objects.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if any member data is not equal (but does not guarantee identical arrays).
        """
    def __str__(self) -> str: ...
    def effectiveSize(self) -> int: 
        """
        The effective size of the data, having accounted for values, indices, and element size.

        This is the number of variable values that "really" exist, as far as a consumer is concerned. The indices & elementSize are used as a storage
        optimization, but the consumer should consider the effective size as the number of "deduplicated" individual values.

        Returns:
            The effective size of the data.
        """
    def elementSize(self) -> int: 
        """
        The element size.

        Any value less than 1 is considered "non authored" and indicates no element size. This should be the most common case, as element size is a
        fairly esoteric extension of ``UsdGeom.Primvar`` data to account for non-typed array strides such as spherical harmonics float[9] arrays.

        See ``UsdGeom.Primvar.GetElementSize()`` for more details.

        Returns:
            The primvar element size.
        """
    @staticmethod
    def getPrimvarData(primvar: pxr.UsdGeom.Primvar, time: pxr.Usd.TimeCode = nan) -> Vec3fPrimvarData: 
        """
        Construct a ``PrimvarData`` from a ``UsdGeom.Primvar`` that has already been authored.

        The primvar may be indexed, non-indexed, with or without elements, or it may not even be validly authored scene description.
        Use ``isValid()`` to confirm that valid data has been gathered.

        Args:
            primvar: The previously authored ``UsdGeom.Primvar``.
            time: The time at which the attribute values are read.

        Returns:
            The read-only ``PrimvarData``.
        """
    def hasIndices(self) -> bool: 
        """
        Whether this is indexed or non-indexed ``PrimvarData``

        Returns:
            Whether this is indexed or non-indexed ``PrimvarData``.
        """
    def index(self) -> bool: 
        """
        Update the values and indices of this ``PrimvarData`` object to avoid duplicate values.

        Updates will not be made in the following conditions:
            - If element size is greater than one.
            - If the existing indexing is efficient.
            - If there are no duplicate values.
            - If the existing indices are invalid

        Returns:
            True if the values and/or indices were modified.
        """
    def indices(self) -> pxr.Vt.IntArray: 
        """
        Access to the indices array.

        This method throws a runtime error if the ``PrimvarData`` is not indexed. For exception-free access, check ``hasIndices()`` before calling this.

        Note:
            It may contain an empty or invalid indices array. Use ``PrimvarData.isValid()`` to validate that the indices are not out-of-range.

        Returns:
            The primvar indices
        """
    def interpolation(self) -> str: 
        """
        The geometric interpolation.

        It may be an invalid interpolation. Use ``PrimvarData.isValid()`` or ``UsdGeom.Primvar.IsValidInterpolation()`` to confirm.

        Returns:
            The geometric interpolation.
        """
    def isIdentical(self, other: Vec3fPrimvarData) -> bool: 
        """
        Check that all data between two ``PrimvarData`` objects is identical.

        This differs from the equality operator in that it ensures the ``Vt.Array`` values and indices have not detached.

        Args:
            other: The other ``PrimvarData``.

        Returns:
            True if all the member data is equal and arrays are identical.
        """
    def isValid(self) -> bool: 
        """
        Whether the data is valid or invalid.

        This is a validation check with respect to the ``PrimvarData`` itself & the requirements of ``UsdGeom.Prim``. It does not validate with respect to
        specific surface topology data, as no such data is available or consistant across ``UsdGeom.PointBased`` prim types.

        This validation checks the following, in this order, and returns false if any condition fails:

            - The interpolation matches ``UsdGeom.Primvar.IsValidInterpolation()``.
            - The values are not empty. Note that individual values may be invalid (e.g ``NaN`` values on a ``Vt.FloatArray``) but this will not be
              considered a failure, as some workflows allow for ``NaN`` to indicate non-authored elements or "holes" within the data.
            - If it is non-indexed, and has elements, that the values divide evenly by elementSize.
            - If it is indexed, and has elements, that the indices divide evenly by elementSize.
            - If it is indexed, that the indices are all within the expected range of the values array.

        Returns:
            Whether the data is valid or invalid.
        """
    def setPrimvar(self, primvar: pxr.UsdGeom.Primvar, time: pxr.Usd.TimeCode = nan) -> bool: 
        """
        Set data on an existing ``UsdGeom.Primvar`` from a ``PrimvarData`` that has already been authored.

        Any existing authored data on the primvar will be overwritten or blocked with the ``PrimvarData`` members.

        To copy data from one ``UsdGeom.Primvar`` to another, use ``data: PrimvarData = PrimvarData.get(primvar: UsdGeom.Primvar)`` to gather the data,
        then use ``setPrimvar(primvar: UsdGeom.Primvar)`` to author it.

        Args:
            primvar: The previously authored ``UsdGeom.Primvar``.
            time: The time at which the attribute values are written.

        Returns:
            Whether the ``UsdGeom.Primvar`` was completely authored from the member data.
            Any failure to author may leave the primvar in an unknown state (e.g. it may have been partially authored).
        """
    def values(self) -> pxr.Vt.Vec3fArray: 
        """
        Access to the values array.

        Bear in mind the values may need to be accessed via ``indices()`` or using an ``elementSize()`` stride.

        It may contain an empty or invalid values array.

        Returns:
            The primvar values.
        """
    __hash__ = None
    pass
def activateDiagnosticsDelegate() -> None:
    """
    Activates the ``Delegate`` to specialize ``TfDiagnostics`` handling.

    The ``Tf`` module from OpenUSD provides various diagnostic logging abilities, including the ability to override the default message
    handler (which prints to ``stderr``) with one or more custom handlers.

    This function can be used to activate a specialized ``TfDiagnosticMgr::Delegate`` provided by OpenUSD Exchange. The primary advantages
    of this ``Delegate`` are:

    - Diagnostics can be filtered by ``DiagnosticsLevel``.
    - Diagnostics can be redirected to ``stdout``, ``stderr``, or muted entirely using ``DiagnosticsOutputStream``.
    - The message formatting is friendlier to end-users.

    Note:
        Use of this ``Delegate`` is entirely optional and it is not activated by default when loading this module. To active it, client code
        must explicitly call ``activateDiagnosticsDelegate()``. This is to allow clients to opt-in and to prevent double printing for clients
        that already have their own ``TfDiagnosticMgr::Delegate`` implementation.
    """
def addAssetInterface(stage: pxr.Usd.Stage, source: pxr.Usd.Stage) -> bool:
    """
    Add an Asset Interface to a stage, which payloads a source stage's contents.

    This function creates a payload to the source stage's contents as the default prim on the stage.

    It (re)configures the stage with the source stage's metadata, payloads the defaultPrim from the source stage, and annotates the Asset
    Interface with USD model metadata including component kind, asset name, and extents hint.

    Args:
        stage: The stage's edit target will become the Asset Interface
        source: The stage that the Asset Interface will target as a Payload

    Returns:
        True if the Asset Interface was added successfully, false otherwise.
    """
def addDiffuseTextureToPreviewMaterial(material: pxr.UsdShade.Material, texturePath: pxr.Sdf.AssetPath) -> bool:
    """
    Adds a diffuse texture to a preview material

    It is expected that the material was created by ``definePreviewMaterial()``

    The texture will be sampled using texture coordinates from the default UV set (generally named ``primvars:st``).

    Args:
        material: The material prim
        texturePath: The ``Sdf.AssetPath`` for the texture

    Returns:
        Whether or not the texture was added to the material
    """
def addMetallicTextureToPreviewMaterial(material: pxr.UsdShade.Material, texturePath: pxr.Sdf.AssetPath) -> bool:
    """
    Adds a single channel metallic texture to a preview material

    It is expected that the material was created by ``definePreviewMaterial()``

    The texture will be sampled using texture coordinates from the default UV set (generally named ``primvars:st``).

    Args:
        material: The material prim
        texturePath: The ``Sdf.AssetPath`` for the texture

    Returns:
        Whether or not the texture was added to the material
    """
def addNormalTextureToPreviewMaterial(material: pxr.UsdShade.Material, texturePath: pxr.Sdf.AssetPath) -> bool:
    """
    Adds a normals texture to a preview material

    It is expected that the material was created by ``definePreviewMaterial()``

    The texture will be sampled using texture coordinates from the default UV set (generally named ``primvars:st``).

    The UsdPreviewSurface specification requires the texture reader to provide data that is properly scaled and ready to be consumed as a
    tangent space normal. Textures stored in 8-bit file formats require scale and bias adjustment to transform the normals into tangent space.

    This module cannot read the provided ``texturePath`` to inspect the channel data (the file may not resolve locally, or even exist yet).
    To account for this, it performs the scale and bias adjustment when the `texturePath` extension matches a list of known 8-bit formats:
    ``["bmp", "tga", "jpg", "jpeg", "png", "tif"]``. Similarly, it assumes that the raw normals data was written into the file, regardless of
    any file format specific color space metadata. If either of these assumptions is incorrect for your source data, you will need to adjust
    the ``scale``, ``bias``, and ``sourceColorSpace`` settings after calling this function.

    Args:
        material: The material prim
        texturePath: The ``Sdf.AssetPath`` for the texture

    Returns:
        Whether or not the texture was added to the material
    """
def addOpacityTextureToPreviewMaterial(material: pxr.UsdShade.Material, texturePath: pxr.Sdf.AssetPath) -> bool:
    """
    Adds a single channel opacity texture to a preview material

    It is expected that the material was created by ``definePreviewMaterial()``

    The texture will be sampled using texture coordinates from the default UV set (generally named ``primvars:st``).

    Args:
        material: The material prim
        texturePath: The ``Sdf.AssetPath`` for the texture

    Returns:
        Whether or not the texture was added to the material
    """
def addOrmTextureToPreviewMaterial(material: pxr.UsdShade.Material, texturePath: pxr.Sdf.AssetPath) -> bool:
    """
    Adds an ORM (occlusion, roughness, metallic) texture to a preview material

    An ORM texture is a normal 3-channel image asset, where the R channel represents occlusion, the G channel represents roughness,
    and the B channel represents metallic/metallness.

    It is expected that the material was created by ``definePreviewMaterial()``

    The texture will be sampled using texture coordinates from the default UV set (generally named ``primvars:st``).

    Args:
        material: The material prim
        texturePath: The ``Sdf.AssetPath`` for the texture

    Returns:
        Whether or not the texture was added to the material
    """
def addPhysicsToMaterial(material: pxr.UsdShade.Material, dynamicFriction: float, staticFriction: typing.Optional[float] = None, restitution: typing.Optional[float] = None, density: typing.Optional[float] = None) -> bool:
    """
    Adds physical material parameters to an existing Material.

    Used to apply ``UsdPhysics.MaterialAPI`` and related properties to an existing ``UsdShade.Material`` (e.g. a visual material).

    @note When mixing visual and physical materials, be sure use both ``usdex.core.bindMaterial`` and ``usdex.core.bindPhysicsMaterial`` on the target geometry, to ensure the
    material is used in both rendering and simulation contexts.

    Parameters:
        - **material** - The material to add the physics material parameters to
        - **dynamicFriction** - The dynamic friction of the material
        - **staticFriction** - The static friction of the material
        - **restitution** - The restitution of the material
        - **density** - The density of the material

    Returns:
        ``True`` if the physics material parameters were successfully added to the material, ``False`` otherwise.
    """
def addPreviewMaterialInterface(material: pxr.UsdShade.Material) -> bool:
    """
    Adds ``UsdShade.Inputs`` to the material prim to create an "interface" to the underlying Preview Shader network.

    All non-default-value ``UsdShade.Inputs`` on the effective surface shader for the universal render context will be "promoted" to the
    ``UsdShade.Material`` as new ``UsdShade.Inputs``. They will be connected to the original source inputs on the shaders, to drive those
    values, and they will be authored with a value matching what had been set on the shader inputs at the time this function was called.

    Additionally, ``UsdUVTexture.file`` inputs on connected shaders will be promoted to the material, following the same logic as direct
    surface inputs.

    Note:

        It is preferable to author all initial shader attributes (including textures) *before* calling ``addPreviewMaterialInterface()``.

    Warning:

        This function will fail if there is any other render context driving the material surface. It is only suitable for use on Preview
        Shader networks, such as the network generated by ``definePreviewMaterial()`` and its associated ``add*Texture`` functions. If you
        require multiple contexts, you should instead construct a Material Interface directly, or with targetted end-user interaction.

    Args:
        material: The material prim

    Returns:
        Whether or not the Material inputs were added successfully
    """
def addRoughnessTextureToPreviewMaterial(material: pxr.UsdShade.Material, texturePath: pxr.Sdf.AssetPath) -> bool:
    """
    Adds a single channel roughness texture to a preview material

    It is expected that the material was created by ``definePreviewMaterial()``

    The texture will be sampled using texture coordinates from the default UV set (generally named ``primvars:st``).

    Args:
        material: The material prim
        texturePath: The ``Sdf.AssetPath`` for the texture

    Returns:
        Whether or not the texture was added to the material
    """
def alignPhysicsJoint(joint: pxr.UsdPhysics.Joint, frame: JointFrame, axis: pxr.Gf.Vec3f) -> None:
    """
    Aligns an existing joint with the specified position, rotation, and axis.

    The Joint's local position & orientation relative to each Body will be authored
    to align to the specified position, orientation, and axis.

    The ``axis`` specifies the primary axis for rotation or translation, based on the local joint orientation relative to each body.

    - To rotate or translate about about the X-axis, specify (1, 0, 0). To operate in the opposite direction, specify (-1, 0, 0).
    - To rotate or translate about about the Y-axis, specify (0, 1, 0). To operate in the opposite direction, specify (0, -1, 0).
    - To rotate or translate about about the Z-axis, specify (0, 0, 1). To operate in the opposite direction, specify (0, 0, -1).
    - Any other direction will be aligned to X-axis via a local rotation or translation for both bodies.

    Parameters:
        - **joint** - The joint to align
        - **frame** - Specifies the position and rotation of the joint in the specified coordinate system.
        - **axis** - The axis of the joint.
    """
def bindMaterial(prim: pxr.Usd.Prim, material: pxr.UsdShade.Material) -> bool:
    """
    Authors a direct binding to the given material on this prim.

    Validates both the prim and the material, applies the ``UsdShade.MaterialBindingAPI`` to the target prim,
    and binds the material to the target prim.

    Note:
        The material is bound with the default "all purpose" used for both full and preview rendering, and with the default "fallback strength"
        meaning descendant prims can override with a different material. If alternate behavior is desired, use the
        ``UsdShade.MaterialBindingAPI`` directly.

    Args:
        prim: The prim that the material will affect
        material: The material to bind to the prim

    Returns:
        Whether the material was successfully bound to the target prim.
    """
def bindPhysicsMaterial(prim: pxr.Usd.Prim, material: pxr.UsdShade.Material) -> bool:
    """
    Binds a physics material to a given rigid body or collision geometry.

    Validates both the prim and the material, applies the ``UsdShade.MaterialBindingAPI`` to the target prim,
    and binds the material to the target prim with the "physics" purpose.

    Note:
        The material is bound with the "physics" purpose, and with the default "fallback strength",
        meaning descendant prims can override with a different material. If alternate behavior is desired,
        use the ``UsdShade.MaterialBindingAPI`` directly.

    Note:
        We cannot bind materials to prims across different instance boundaries.
        This function returns an error if ``prim`` and ``material`` are not placed in an editable location.

    Returns:
        ``True`` if the material was successfully bound to the target prim, ``False`` otherwise.
    """
def blockDisplayName(prim: pxr.Usd.Prim) -> bool:
    """
    Block this prim's display name (metadata)

    The fallback value will be explicitly authored to cause the value to resolve as if there were no authored value opinions in weaker layers

    Args:
        prim: The prim to block the display name for

    Returns:
        True on success, otherwise false
    """
def buildVersion() -> str:
    """
    Verify the expected usdex modules are being loaded at runtime.

    Returns:
        A human-readable build version string for the usdex modules.
    """
def clearDisplayName(prim: pxr.Usd.Prim) -> bool:
    """
    Clears this prim's display name (metadata) in the current EditTarget (only)

    Args:
        prim: The prim to clear the display name for

    Returns:
        True on success, otherwise false
    """
def computeEffectiveDisplayName(prim: pxr.Usd.Prim) -> str:
    """
    Calculate the effective display name of this prim

    If the display name is un-authored or empty then the prim's name is returned

    Args:
        prim: The prim to compute the display name for

    Returns:
        The effective display name
    """
def computeEffectivePreviewSurfaceShader(material: pxr.UsdShade.Material) -> pxr.UsdShade.Shader:
    """
    Get the effective surface Shader of a Material for the universal render context.

    Args:
        material: The Material to consider

    Returns:
        The connected Shader. Returns an invalid shader object on error.
    """
@typing.overload
def configureStage(stage: pxr.Usd.Stage, defaultPrimName: str, upAxis: str, linearUnits: float, massUnits: float, authoringMetadata: typing.Optional[str] = None) -> bool:
    """
    Configure a stage so that the defining metadata is explicitly authored.

    The default prim will be used as the target of a Reference or Payload to this layer when no explicit prim path is specified.
    A root prim with the given ``defaultPrimName`` will be defined on the stage.
    If a new prim is defined then the type name will be set to ``Scope``.

    The stage metrics of `Up Axis <https://openusd.org/release/api/group___usd_geom_up_axis__group.html#details>`_,
    `Linear Units <https://openusd.org/release/api/group___usd_geom_linear_units__group.html#details>`_ and
    `Mass Units <https://openusd.org/release/api/usd_physics_page_front.html#usdPhysics_units>`_ will be authored.

    The root layer will be annotated with authoring metadata, unless previously annotated. This is to preserve
    authoring metadata on referenced layers that came from other applications. See ``setLayerAuthoringMetadata`` for more details.

    Args:
        stage: The stage to be configured.
        defaultPrimName: Name of the default root prim.
        upAxis: The up axis for all the geometry contained in the stage.
        linearUnits: The meters per unit for all linear measurements in the stage.
        massUnits: The kilograms per unit for all mass measurements in the stage.
        authoringMetadata: The provenance information from the host application. See ``setLayerAuthoringMetadata`` for details.

    Returns:
        A bool indicating if the metadata was successfully authored.




    Configure a stage so that the defining metadata is explicitly authored.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Args:
        stage: The stage to be configured.
        defaultPrimName: Name of the default root prim.
        upAxis: The up axis for all the geometry contained in the stage.
        linearUnits: The meters per unit for all linear measurements in the stage.
        authoringMetadata: The provenance information from the host application. See ``setLayerAuthoringMetadata`` for details.

    Returns:
        A bool indicating if the metadata was successfully authored.
    """
@typing.overload
def configureStage(stage: pxr.Usd.Stage, defaultPrimName: str, upAxis: str, linearUnits: float, authoringMetadata: typing.Optional[str] = None) -> bool:
    pass
def createMaterial(parent: pxr.Usd.Prim, name: str) -> pxr.UsdShade.Material:
    """
    Create a ``UsdShade.Material`` as the child of the Prim parent

    Args:
        parent: Parent prim of the material
        name: Name of the material to be created
    Returns:
        The newly created ``UsdShade.Material``. Returns an invalid material object on error.
    """
def deactivateDiagnosticsDelegate() -> None:
    """
    Deactivates the ``Delegate`` to restore default ``TfDiagnostics`` handling.

    When deactivated, the default ``TfDiagnosticMgr`` printing is restored, unless some other ``Delegate`` is still active.
    """
@typing.overload
def defineCamera(stage: pxr.Usd.Stage, path: pxr.Sdf.Path, cameraData: pxr.Gf.Camera) -> pxr.UsdGeom.Camera:
    """
    Defines a basic 3d camera on the stage.

    Note that ``Gf.Camera`` is a simplified form of 3d camera data that does not account for time-sampled data, shutter window,
    stereo role, or exposure. If you need to author those properties, do so after defining the ``UsdGeom.Camera``.

    An invalid UsdGeomCamera will be returned if camera attributes could not be authored successfully.

    Parameters:
        - **stage** - The stage on which to define the camera
        - **path** - The absolute prim path at which to define the camera
        - **cameraData** - The camera data to set, including the world space transform matrix

    Returns:
        A ``UsdGeom.Camera`` schema wrapping the defined ``Usd.Prim``.




    Defines a basic 3d camera on the stage.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **parent** - Prim below which to define the camera
        - **name** - Name of the camera
        - **cameraData** - The camera data to set, including the world space transform matrix

    Returns:
        A ``UsdGeom.Camera`` schema wrapping the defined ``Usd.Prim``.




    Defines a basic 3d camera from an existing prim.

    This converts an existing prim to a Camera type, preserving any existing transform data.

    Parameters:
        - **prim** - The existing prim to convert to a camera
        - **cameraData** - The camera data to set, including the world space transform matrix

    Returns:
        A ``UsdGeom.Camera`` schema wrapping the converted ``Usd.Prim``.
    """
@typing.overload
def defineCamera(parent: pxr.Usd.Prim, name: str, cameraData: pxr.Gf.Camera) -> pxr.UsdGeom.Camera:
    pass
@typing.overload
def defineCamera(prim: pxr.Usd.Prim, cameraData: pxr.Gf.Camera) -> pxr.UsdGeom.Camera:
    pass
@typing.overload
def defineCubicBasisCurves(stage: pxr.Usd.Stage, path: pxr.Sdf.Path, curveVertexCounts: pxr.Vt.IntArray, points: pxr.Vt.Vec3fArray, basis: str = 'bezier', wrap: str = 'nonperiodic', widths: typing.Optional[FloatPrimvarData] = None, normals: typing.Optional[Vec3fPrimvarData] = None, displayColor: typing.Optional[Vec3fPrimvarData] = None, displayOpacity: typing.Optional[FloatPrimvarData] = None) -> pxr.UsdGeom.BasisCurves:
    """
    Defines a batched Cubic ``UsdGeom.BasisCurves`` prim on the stage.

    Attribute values will be validated and in the case of invalid data the Curves will not be defined. An invalid ``UsdGeom.BasisCurves``
    object will be returned in this case.

    Values will be authored for all attributes required to completely describe the Curves, even if weaker matching opinions already exist.

        - Curve Vertex Counts
        - Points
        - Type
        - Basis
        - Wrap
        - Extent

    The "extent" of the Curves will be computed and authored based on the ``points`` and ``widths`` provided.

    The following common primvars can optionally be authored at the same time using a ``PrimvarData`` to specify interpolation, data,
    and optionally indices or elementSize.

        - Widths
        - Normals
        - Display Color
        - Display Opacity

    For both widths and normals, if they are provided, they are authored as ``primvars:widths`` and ``primvars:normals``, so that indexing is
    possible and to ensure that the value takes precedence in cases where both the non-primvar and primvar attributes are authored.

    Parameters:
        - **stage** The stage on which to define the curves.
        - **path** The absolute prim path at which to define the curves.
        - **curveVertexCounts** The number of vertices in each independent curve. The length of this array determines the number of curves.
        - **points** Vertex/CV positions for the curves described in local space.
        - **basis** The basis specifies the vstep and matrix used for cubic interpolation. Accepted values for cubic curves are
            ``UsdGeom.Tokens.bezier``, ``UsdGeom.Tokens.bspline``, or ``UsdGeom.Tokens.catmullRom``.
        - **wrap** Determines how the start and end points of the curve behave. Accepted values are ``UsdGeom.Tokens.nonperiodic``,
            ``UsdGeom.Tokens.periodic``, and ``UsdGeom.Tokens.pinned`` (bspline and catmullRom only).
        - **widths** Values for the width specification for the curves.
        - **normals** Values for the normals primvar for the curves. If authored, the curves are considered oriented ribbons rather than tubes.
        - **displayColor** Values to be authored for the display color primvar.
        - **displayOpacity** Values to be authored for the display opacity primvar.

    Returns
        ``UsdGeom.BasisCurves`` schema wrapping the defined ``Usd.Prim``



    Defines a batched Cubic ``UsdGeom.BasisCurves`` prim on the stage.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **parent** Prim below which to define the curves
        - **name** Name of the curves
        - **curveVertexCounts** The number of vertices in each independent curve. The length of this array determines the number of curves.
        - **points** Vertex/CV positions for the curves described in local space.
        - **basis** The basis specifies the vstep and matrix used for cubic interpolation. Accepted values for cubic curves are
            ``UsdGeom.Tokens.bezier``, ``UsdGeom.Tokens.bspline``, ``UsdGeom.Tokens.catmullRom``.
        - **wrap** Determines how the start and end points of the curve behave. Accepted values are ``UsdGeom.Tokens.nonperiodic``,
            ``UsdGeom.Tokens.periodic``, and ``UsdGeom.Tokens.pinned`` (bspline and catmullRom only).
        - **widths** Values for the width specification for the curves.
        - **normals** Values for the normals primvar for the curves. If authored, the curves are considered oriented ribbons rather than tubes.
        - **displayColor** Values to be authored for the display color primvar.
        - **displayOpacity** Values to be authored for the display opacity primvar.

    Returns
        ``UsdGeom.BasisCurves`` schema wrapping the defined ``Usd.Prim``



    Defines a batched Cubic ``UsdGeom.BasisCurves`` prim on the stage.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **prim** The stage on which to define the curves.
        - **name** The absolute prim path at which to define the curves.
        - **curveVertexCounts** The number of vertices in each independent curve. The length of this array determines the number of curves.
        - **points** Vertex/CV positions for the curves described in local space.
        - **basis** The basis specifies the vstep and matrix used for cubic interpolation. Accepted values for cubic curves are
            ``UsdGeom.Tokens.bezier``, ``UsdGeom.Tokens.bspline``, or ``UsdGeom.Tokens.catmullRom``.
        - **wrap** Determines how the start and end points of the curve behave. Accepted values are ``UsdGeom.Tokens.nonperiodic``,
            ``UsdGeom.Tokens.periodic``, and ``UsdGeom.Tokens.pinned`` (bspline and catmullRom only).
        - **widths** Values for the width specification for the curves.
        - **normals** Values for the normals primvar for the curves. If authored, the curves are considered oriented ribbons rather than tubes.
        - **displayColor** Values to be authored for the display color primvar.
        - **displayOpacity** Values to be authored for the display opacity primvar.

    Returns
        ``UsdGeom.BasisCurves`` schema wrapping the defined ``Usd.Prim``
    """
@typing.overload
def defineCubicBasisCurves(parent: pxr.Usd.Prim, name: str, curveVertexCounts: pxr.Vt.IntArray, points: pxr.Vt.Vec3fArray, basis: str = 'bezier', wrap: str = 'nonperiodic', widths: typing.Optional[FloatPrimvarData] = None, normals: typing.Optional[Vec3fPrimvarData] = None, displayColor: typing.Optional[Vec3fPrimvarData] = None, displayOpacity: typing.Optional[FloatPrimvarData] = None) -> pxr.UsdGeom.BasisCurves:
    pass
@typing.overload
def defineCubicBasisCurves(prim: pxr.Usd.Prim, curveVertexCounts: pxr.Vt.IntArray, points: pxr.Vt.Vec3fArray, basis: str = 'bezier', wrap: str = 'nonperiodic', widths: typing.Optional[FloatPrimvarData] = None, normals: typing.Optional[Vec3fPrimvarData] = None, displayColor: typing.Optional[Vec3fPrimvarData] = None, displayOpacity: typing.Optional[FloatPrimvarData] = None) -> pxr.UsdGeom.BasisCurves:
    pass
@typing.overload
def defineDomeLight(stage: pxr.Usd.Stage, path: pxr.Sdf.Path, intensity: float = 1.0, texturePath: typing.Optional[str] = None, textureFormat: str = 'automatic') -> pxr.UsdLux.DomeLight:
    """
        Creates a dome light with an optional texture.

        A dome light represents light emitted inward from a distant external environment, such as a sky or IBL light probe.

        Texture Format values:

            - ``automatic`` - Tries to determine the layout from the file itself.
            - ``latlong`` - Latitude as X, longitude as Y.
            - ``mirroredBall`` - An image of the environment reflected in a sphere, using an implicitly orthogonal projection.
            - ``angular`` - Similar to mirroredBall but the radial dimension is mapped linearly to the angle, for better sampling at the edges.
            - ``cubeMapVerticalCross`` - Set to "automatic" by default.

        **Note:**

            The DomeLight schema requires the
            `dome's top pole to be aligned with the world's +Y axis <https://openusd.org/release/api/class_usd_lux_dome_light.html#details>`_.
            In USD 23.11 a new `UsdLuxDomeLight_1 <https://openusd.org/release/api/class_usd_lux_dome_light__1.html#details>`_ schema was
            added which gives control over the pole axis. However, it is not widely supported yet, so we still prefer to author the original
            DomeLight schema and expect consuming application and renderers to account for the +Y pole axis.

        Parameters:
            - **stage** - The stage in which the light should be authored
            - **path** - The path which the light prim should be written to
            - **intensity** - The intensity value of the dome light
            - **texturePath** - The path to the texture file to use on the dome light.
            - **textureFormat** - How the texture should be mapped on the dome light.

        Returns:
            The dome light if created successfully.



        Creates a dome light with an optional texture.

        This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

        Parameters:
            - **parent** - Prim below which to define the light
            - **name** - Name of the light
            - **intensity** - The intensity value of the dome light
            - **texturePath** - The path to the texture file to use on the dome light.
            - **textureFormat** - How the texture should be mapped on the dome light.

        Returns:
            The dome light if created successfully.



    Creates a dome light with an optional texture.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Args:
        prim: Prim to define the dome light on. The prim's type will be set to ``UsdLux.DomeLight``.
        intensity: The intensity value of the dome light
        texturePath: The path to the texture file to use on the dome light.
        textureFormat: How the texture should be mapped on the dome light.

    Returns:
        The light if created successfully.
    """
@typing.overload
def defineDomeLight(parent: pxr.Usd.Prim, name: str, intensity: float = 1.0, texturePath: typing.Optional[str] = None, textureFormat: str = 'automatic') -> pxr.UsdLux.DomeLight:
    pass
@typing.overload
def defineDomeLight(prim: pxr.Usd.Prim, intensity: float = 1.0, texturePath: typing.Optional[str] = None, textureFormat: str = 'automatic') -> pxr.UsdLux.DomeLight:
    pass
@typing.overload
def defineLinearBasisCurves(stage: pxr.Usd.Stage, path: pxr.Sdf.Path, curveVertexCounts: pxr.Vt.IntArray, points: pxr.Vt.Vec3fArray, wrap: str = 'nonperiodic', widths: typing.Optional[FloatPrimvarData] = None, normals: typing.Optional[Vec3fPrimvarData] = None, displayColor: typing.Optional[Vec3fPrimvarData] = None, displayOpacity: typing.Optional[FloatPrimvarData] = None) -> pxr.UsdGeom.BasisCurves:
    """
    Defines a batched Linear ``UsdGeom.BasisCurves`` prim on the stage.

    Attribute values will be validated and in the case of invalid data the Curves will not be defined. An invalid ``UsdGeom.BasisCurves``
    object will be returned in this case.

    Values will be authored for all attributes required to completely describe the Curves, even if weaker matching opinions already exist.

        - Curve Vertex Counts
        - Points
        - Type
        - Wrap
        - Extent

    The "extent" of the Curves will be computed and authored based on the ``points`` and ``widths`` provided.

    The following common primvars can optionally be authored at the same time using a ``PrimvarData`` to specify interpolation, data,
    and optionally indices or elementSize.

        - Widths
        - Normals
        - Display Color
        - Display Opacity

    For both widths and normals, if they are provided, they are authored as ``primvars:widths`` and ``primvars:normals``, so that indexing is
    possible and to ensure that the value takes precedence in cases where both the non-primvar and primvar attributes are authored.

    Parameters:
        - **stage** The stage on which to define the curves.
        - **path** The absolute prim path at which to define the curves.
        - **curveVertexCounts** The number of vertices in each independent curve. The length of this array determines the number of curves.
        - **points** Vertex/CV positions for the curves described in local space.
        - **wrap** Determines how the start and end points of the curve behave. Accepted values for linear curves are
            ``UsdGeom.Tokens.nonperiodic`` and ``UsdGeom.Tokens.periodic``.
        - **widths** Values for the width specification for the curves.
        - **normals** Values for the normals primvar for the curves. If authored, the curves are considered oriented ribbons rather than tubes.
        - **displayColor** Values to be authored for the display color primvar.
        - **displayOpacity** Values to be authored for the display opacity primvar.

    Returns
        ``UsdGeom.BasisCurves`` schema wrapping the defined ``Usd.Prim``



    Defines a batched Linear ``UsdGeom.BasisCurves`` prim on the stage.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **parent** Prim below which to define the curves
        - **name** Name of the curves
        - **curveVertexCounts** The number of vertices in each independent curve. The length of this array determines the number of curves.
        - **points** Vertex/CV positions for the curves described in local space.
        - **wrap** Determines how the start and end points of the curve behave. Accepted values for linear curves are
            ``UsdGeom.Tokens.nonperiodic`` and ``UsdGeom.Tokens.periodic``.
        - **widths** Values for the width specification for the curves.
        - **normals** Values for the normals primvar for the curves. If authored, the curves are considered oriented ribbons rather than tubes.
        - **displayColor** Values to be authored for the display color primvar.
        - **displayOpacity** Values to be authored for the display opacity primvar.

    Returns
        ``UsdGeom.BasisCurves`` schema wrapping the defined ``Usd.Prim``



    Defines a batched Linear ``UsdGeom.BasisCurves`` prim on the stage.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **prim** The stage on which to define the curves.
        - **name** The absolute prim path at which to define the curves.
        - **curveVertexCounts** The number of vertices in each independent curve. The length of this array determines the number of curves.
        - **points** Vertex/CV positions for the curves described in local space.
        - **wrap** Determines how the start and end points of the curve behave. Accepted values for linear curves are
            ``UsdGeom.Tokens.nonperiodic`` and ``UsdGeom.Tokens.periodic``.
        - **widths** Values for the width specification for the curves.
        - **normals** Values for the normals primvar for the curves. If authored, the curves are considered oriented ribbons rather than tubes.
        - **displayColor** Values to be authored for the display color primvar.
        - **displayOpacity** Values to be authored for the display opacity primvar.

    Returns
        ``UsdGeom.BasisCurves`` schema wrapping the defined ``Usd.Prim``
    """
@typing.overload
def defineLinearBasisCurves(parent: pxr.Usd.Prim, name: str, curveVertexCounts: pxr.Vt.IntArray, points: pxr.Vt.Vec3fArray, wrap: str = 'nonperiodic', widths: typing.Optional[FloatPrimvarData] = None, normals: typing.Optional[Vec3fPrimvarData] = None, displayColor: typing.Optional[Vec3fPrimvarData] = None, displayOpacity: typing.Optional[FloatPrimvarData] = None) -> pxr.UsdGeom.BasisCurves:
    pass
@typing.overload
def defineLinearBasisCurves(prim: pxr.Usd.Prim, curveVertexCounts: pxr.Vt.IntArray, points: pxr.Vt.Vec3fArray, wrap: str = 'nonperiodic', widths: typing.Optional[FloatPrimvarData] = None, normals: typing.Optional[Vec3fPrimvarData] = None, displayColor: typing.Optional[Vec3fPrimvarData] = None, displayOpacity: typing.Optional[FloatPrimvarData] = None) -> pxr.UsdGeom.BasisCurves:
    pass
@typing.overload
def definePayload(stage: pxr.Usd.Stage, path: pxr.Sdf.Path, source: pxr.Usd.Prim) -> pxr.Usd.Prim:
    """
    Define a payload to a prim.

    This creates a payload prim that targets a prim in another layer (external payload) or the same layer (internal payload).

    The payload's assetPath will be set to the relative identifier between the stage's edit target and the source's stage if it's
    an external payload with a valid relative path.

    For more information, see:
        - https://openusd.org/release/glossary.html#usdglossary-payload
        - https://openusd.org/release/api/class_usd_payloads.html#details

    Parameters:
        - **stage** - The stage on which to define the payload
        - **path** - The absolute prim path at which to define the payload
        - **source** - The payload to add

    Returns:
        The newly created payload prim. Returns an invalid prim on error.




    Define a payload to a prim as a child of the ``parent`` prim

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **parent** - The parent prim to add the payload to
        - **source** - The payload to add
        - **name** - The name of the payload. If not provided, uses the source prim's name

    Returns:
        The newly created payload prim. Returns an invalid prim on error.
    """
@typing.overload
def definePayload(parent: pxr.Usd.Prim, source: pxr.Usd.Prim, name: typing.Optional[str] = None) -> pxr.Usd.Prim:
    pass
@typing.overload
def definePhysicsFixedJoint(stage: pxr.Usd.Stage, path: pxr.Sdf.Path, body0: pxr.Usd.Prim, body1: pxr.Usd.Prim, frame: JointFrame) -> pxr.UsdPhysics.FixedJoint:
    """
    Creates a fixed joint connecting two rigid bodies.

    A fixed joint connects two prims making them effectively welded together.
    For maximal coordinate (free-body) solvers it is important to fully constrain the two bodies. For reduced coordinate solvers this is may seem
    redundant, but it is important for consistency & cross-solver portability.

    Using the coordinate system specified by the ``jointFrame``, the local position and rotation
    corresponding to ``body0`` and ``body1`` of the joint are automatically calculated.

    Parameters:
        - **stage** - The stage on which to define the joint
        - **path** - The absolute prim path at which to define the joint
        - **body0** - The first body of the joint
        - **body1** - The second body of the joint
        - **frame** - The position and rotation of the joint in the specified coordinate system.

    Returns:
        ``UsdPhysics.FixedJoint`` schema wrapping the defined ``Usd.Prim``.



    Creates a fixed joint connecting two rigid bodies.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **parent** - Prim below which to define the physics joint
        - **name** - Name of the physics joint
        - **body0** - The first body of the joint
        - **body1** - The second body of the joint
        - **frame** - The position and rotation of the joint in the specified coordinate system.

    Returns:
        ``UsdPhysics.FixedJoint`` schema wrapping the defined ``Usd.Prim``.



    Creates a fixed joint connecting two rigid bodies.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **prim** - Prim to define the joint. The prim's type will be set to ``UsdPhysics.FixedJoint``.
        - **body0** - The first body of the joint
        - **body1** - The second body of the joint
        - **frame** - The position and rotation of the joint in the specified coordinate system.

    Returns:
        ``UsdPhysics.FixedJoint`` schema wrapping the defined ``Usd.Prim``.
    """
@typing.overload
def definePhysicsFixedJoint(parent: pxr.Usd.Prim, name: str, body0: pxr.Usd.Prim, body1: pxr.Usd.Prim, frame: JointFrame) -> pxr.UsdPhysics.FixedJoint:
    pass
@typing.overload
def definePhysicsFixedJoint(prim: pxr.Usd.Prim, body0: pxr.Usd.Prim, body1: pxr.Usd.Prim, frame: JointFrame) -> pxr.UsdPhysics.FixedJoint:
    pass
@typing.overload
def definePhysicsMaterial(stage: pxr.Usd.Stage, path: pxr.Sdf.Path, dynamicFriction: float, staticFriction: typing.Optional[float] = None, restitution: typing.Optional[float] = None, density: typing.Optional[float] = None) -> pxr.UsdShade.Material:
    """
    Creates a Physics Material.

    When ``UsdPhysics.MaterialAPI`` is applied on a ``UsdShade.Material`` it specifies various physical properties which should be used during simulation of
    the bound geometry.

    See [UsdPhysicsMaterialAPI](https://openusd.org/release/api/class_usd_physics_material_a_p_i.html) for details.

    Parameters:
        - **stage** - The stage on which to define the material
        - **path** - The absolute prim path at which to define the material
        - **dynamicFriction** - The dynamic friction of the material
        - **staticFriction** - The static friction of the material
        - **restitution** - The restitution of the material
        - **density** - The density of the material

    Returns:
        ``UsdShade.Material`` schema wrapping the defined ``Usd.Prim``.



    Creates a Physics Material.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **parent** - Prim below which to define the physics material
        - **name** - Name of the physics material
        - **dynamicFriction** - The dynamic friction of the material
        - **staticFriction** - The static friction of the material
        - **restitution** - The restitution of the material
        - **density** - The density of the material

    Returns:
        ``UsdShade.Material`` schema wrapping the defined ``Usd.Prim``.



    Creates a Physics Material.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **prim** - Prim to define the material. The prim's type will be set to ``UsdShade.Material``.
        - **dynamicFriction** - The dynamic friction of the material
        - **staticFriction** - The static friction of the material
        - **restitution** - The restitution of the material
        - **density** - The density of the material

    Returns:
        ``UsdShade.Material`` schema wrapping the defined ``Usd.Prim``.
    """
@typing.overload
def definePhysicsMaterial(parent: pxr.Usd.Prim, name: str, dynamicFriction: float, staticFriction: typing.Optional[float] = None, restitution: typing.Optional[float] = None, density: typing.Optional[float] = None) -> pxr.UsdShade.Material:
    pass
@typing.overload
def definePhysicsMaterial(prim: pxr.Usd.Prim, dynamicFriction: float, staticFriction: typing.Optional[float] = None, restitution: typing.Optional[float] = None, density: typing.Optional[float] = None) -> pxr.UsdShade.Material:
    pass
@typing.overload
def definePhysicsPrismaticJoint(stage: pxr.Usd.Stage, path: pxr.Sdf.Path, body0: pxr.Usd.Prim, body1: pxr.Usd.Prim, frame: JointFrame, axis: pxr.Gf.Vec3f, lowerLimit: typing.Optional[float] = None, upperLimit: typing.Optional[float] = None) -> pxr.UsdPhysics.PrismaticJoint:
    """
    Creates a prismatic joint, which acts as a slider along a single axis, connecting two rigid bodies.

    Using the coordinate system specified by the ``jointFrame``, the local position and rotation
    corresponding to ``body0`` and ``body1`` of the joint are automatically calculated.

    The ``axis`` specifies the primary axis for rotation, based on the local joint orientation relative to each body.

    - To slide along the X-axis, specify (1, 0, 0). To slide in the opposite direction, specify (-1, 0, 0).
    - To slide along the Y-axis, specify (0, 1, 0). To slide in the opposite direction, specify (0, -1, 0).
    - To slide along the Z-axis, specify (0, 0, 1). To slide in the opposite direction, specify (0, 0, -1).
    - Any other direction will be aligned to X-axis via a local rotation for both bodies.

    The ``lowerLimit`` and ``upperLimit`` are specified as distance along the ``axis`` in
    [linear units of the stage](https://openusd.org/release/api/group___usd_geom_linear_units__group.html).

    Parameters:
        - **stage** - The stage on which to define the joint
        - **path** - The absolute prim path at which to define the joint
        - **body0** - The first body of the joint
        - **body1** - The second body of the joint
        - **frame** - The position and rotation of the joint in the specified coordinate system.
        - **axis** - The axis of the joint.
        - **lowerLimit** - The lower limit of the joint (distance).
        - **upperLimit** - The upper limit of the joint (distance).

    Returns:
        ``UsdPhysics.PrismaticJoint`` schema wrapping the defined ``Usd.Prim``.



    Creates a prismatic joint, which acts as a slider along a single axis, connecting two rigid bodies.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **parent** - Prim below which to define the physics joint
        - **name** - Name of the physics joint
        - **body0** - The first body of the joint
        - **body1** - The second body of the joint
        - **frame** - The position and rotation of the joint in the specified coordinate system.
        - **axis** - The axis of the joint.
        - **lowerLimit** - The lower limit of the joint (distance).
        - **upperLimit** - The upper limit of the joint (distance).

    Returns:
        ``UsdPhysics.PrismaticJoint`` schema wrapping the defined ``Usd.Prim``.



    Creates a prismatic joint, which acts as a slider along a single axis, connecting two rigid bodies.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **prim** - Prim to define the joint. The prim's type will be set to ``UsdPhysics.PrismaticJoint``.
        - **body0** - The first body of the joint
        - **body1** - The second body of the joint
        - **frame** - The position and rotation of the joint in the specified coordinate system.
        - **axis** - The axis of the joint.
        - **lowerLimit** - The lower limit of the joint (distance).
        - **upperLimit** - The upper limit of the joint (distance).

    Returns:
        ``UsdPhysics.PrismaticJoint`` schema wrapping the defined ``Usd.Prim``.
    """
@typing.overload
def definePhysicsPrismaticJoint(parent: pxr.Usd.Prim, name: str, body0: pxr.Usd.Prim, body1: pxr.Usd.Prim, frame: JointFrame, axis: pxr.Gf.Vec3f, lowerLimit: typing.Optional[float] = None, upperLimit: typing.Optional[float] = None) -> pxr.UsdPhysics.PrismaticJoint:
    pass
@typing.overload
def definePhysicsPrismaticJoint(prim: pxr.Usd.Prim, body0: pxr.Usd.Prim, body1: pxr.Usd.Prim, frame: JointFrame, axis: pxr.Gf.Vec3f, lowerLimit: typing.Optional[float] = None, upperLimit: typing.Optional[float] = None) -> pxr.UsdPhysics.PrismaticJoint:
    pass
@typing.overload
def definePhysicsRevoluteJoint(stage: pxr.Usd.Stage, path: pxr.Sdf.Path, body0: pxr.Usd.Prim, body1: pxr.Usd.Prim, frame: JointFrame, axis: pxr.Gf.Vec3f, lowerLimit: typing.Optional[float] = None, upperLimit: typing.Optional[float] = None) -> pxr.UsdPhysics.RevoluteJoint:
    """
    Creates a revolute joint, which acts as a hinge around a single axis, connecting two rigid bodies.

    Using the coordinate system specified by the ``jointFrame``, the local position and rotation
    corresponding to ``body0`` and ``body1`` of the joint are automatically calculated.

    The ``axis`` specifies the primary axis for rotation, based on the local joint orientation relative to each body.

    - To rotate around the X-axis, specify (1, 0, 0). To rotate in the opposite direction, specify (-1, 0, 0).
    - To rotate around the Y-axis, specify (0, 1, 0). To rotate in the opposite direction, specify (0, -1, 0).
    - To rotate around the Z-axis, specify (0, 0, 1). To rotate in the opposite direction, specify (0, 0, -1).
    - Any other direction will be aligned to X-axis via a local rotation for both bodies.

    Parameters:
        - **stage** - The stage on which to define the joint
        - **path** - The absolute prim path at which to define the joint
        - **body0** - The first body of the joint
        - **body1** - The second body of the joint
        - **frame** - The position and rotation of the joint in the specified coordinate system.
        - **axis** - The axis of rotation
        - **lowerLimit** - The lower limit of the joint (degrees).
        - **upperLimit** - The upper limit of the joint (degrees).

    Returns:
        ``UsdPhysics.RevoluteJoint`` schema wrapping the defined ``Usd.Prim``.



    Creates a revolute joint, which acts as a hinge around a single axis, connecting two rigid bodies.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **parent** - Prim below which to define the physics joint
        - **name** - Name of the physics joint
        - **body0** - The first body of the joint
        - **body1** - The second body of the joint
        - **frame** - The position and rotation of the joint in the specified coordinate system.
        - **axis** - The axis of rotation
        - **lowerLimit** - The lower limit of the joint (degrees).
        - **upperLimit** - The upper limit of the joint (degrees).

    Returns:
        ``UsdPhysics.RevoluteJoint`` schema wrapping the defined ``Usd.Prim``.



    Creates a revolute joint, which acts as a hinge around a single axis, connecting two rigid bodies.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **prim** - Prim to define the joint. The prim's type will be set to ``UsdPhysics.RevoluteJoint``.
        - **body0** - The first body of the joint
        - **body1** - The second body of the joint
        - **frame** - The position and rotation of the joint in the specified coordinate system.
        - **axis** - The axis of rotation
        - **lowerLimit** - The lower limit of the joint (degrees).
        - **upperLimit** - The upper limit of the joint (degrees).

    Returns:
        ``UsdPhysics.RevoluteJoint`` schema wrapping the defined ``Usd.Prim``.
    """
@typing.overload
def definePhysicsRevoluteJoint(parent: pxr.Usd.Prim, name: str, body0: pxr.Usd.Prim, body1: pxr.Usd.Prim, frame: JointFrame, axis: pxr.Gf.Vec3f, lowerLimit: typing.Optional[float] = None, upperLimit: typing.Optional[float] = None) -> pxr.UsdPhysics.RevoluteJoint:
    pass
@typing.overload
def definePhysicsRevoluteJoint(prim: pxr.Usd.Prim, body0: pxr.Usd.Prim, body1: pxr.Usd.Prim, frame: JointFrame, axis: pxr.Gf.Vec3f, lowerLimit: typing.Optional[float] = None, upperLimit: typing.Optional[float] = None) -> pxr.UsdPhysics.RevoluteJoint:
    pass
@typing.overload
def definePhysicsSphericalJoint(stage: pxr.Usd.Stage, path: pxr.Sdf.Path, body0: pxr.Usd.Prim, body1: pxr.Usd.Prim, frame: JointFrame, axis: pxr.Gf.Vec3f, coneAngle0Limit: typing.Optional[float] = None, coneAngle1Limit: typing.Optional[float] = None) -> pxr.UsdPhysics.SphericalJoint:
    """
    Creates a spherical joint, which acts as a ball and socket joint, connecting two rigid bodies.

    Using the coordinate system specified by the ``jointFrame``, the local position and rotation
    corresponding to ``body0`` and ``body1`` of the joint are automatically calculated.

    The ``axis`` specifies the primary axis for rotation, based on the local joint orientation relative to each body.

    - To rotate around the X-axis, specify (1, 0, 0). To rotate in the opposite direction, specify (-1, 0, 0).
    - To rotate around the Y-axis, specify (0, 1, 0). To rotate in the opposite direction, specify (0, -1, 0).
    - To rotate around the Z-axis, specify (0, 0, 1). To rotate in the opposite direction, specify (0, 0, -1).
    - Any other direction will be aligned to X-axis via a local rotation for both bodies.

    For SphericalJoint, the axis specified here is used as the center, and the horizontal and vertical cone angles are limited by ``coneAngle0Limit`` and
    ``coneAngle1Limit``.

    Parameters:
        - **stage** - The stage on which to define the joint
        - **path** - The absolute prim path at which to define the joint
        - **body0** - The first body of the joint
        - **body1** - The second body of the joint
        - **frame** - The position and rotation of the joint in the specified coordinate system.
        - **axis** - The axis of the joint.
        - **coneAngle0Limit** - The lower limit of the cone angle (degrees).
        - **coneAngle1Limit** - The upper limit of the cone angle (degrees).

    Returns:
        ``UsdPhysics.SphericalJoint`` schema wrapping the defined ``Usd.Prim``.



    Creates a spherical joint, which acts as a ball and socket joint, connecting two rigid bodies.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **parent** - Prim below which to define the physics joint
        - **name** - Name of the physics joint
        - **body0** - The first body of the joint
        - **body1** - The second body of the joint
        - **frame** - The position and rotation of the joint in the specified coordinate system.
        - **axis** - The axis of the joint.
        - **coneAngle0Limit** - The lower limit of the cone angle (degrees).
        - **coneAngle1Limit** - The upper limit of the cone angle (degrees).

    Returns:
        ``UsdPhysics.SphericalJoint`` schema wrapping the defined ``Usd.Prim``.



    Creates a spherical joint, which acts as a ball and socket joint, connecting two rigid bodies.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **prim** - Prim to define the joint. The prim's type will be set to ``UsdPhysics.SphericalJoint``.
        - **body0** - The first body of the joint
        - **body1** - The second body of the joint
        - **frame** - The position and rotation of the joint in the specified coordinate system.
        - **axis** - The axis of the joint.
        - **coneAngle0Limit** - The lower limit of the cone angle (degrees).
        - **coneAngle1Limit** - The upper limit of the cone angle (degrees).

    Returns:
        ``UsdPhysics.SphericalJoint`` schema wrapping the defined ``Usd.Prim``.
    """
@typing.overload
def definePhysicsSphericalJoint(parent: pxr.Usd.Prim, name: str, body0: pxr.Usd.Prim, body1: pxr.Usd.Prim, frame: JointFrame, axis: pxr.Gf.Vec3f, coneAngle0Limit: typing.Optional[float] = None, coneAngle1Limit: typing.Optional[float] = None) -> pxr.UsdPhysics.SphericalJoint:
    pass
@typing.overload
def definePhysicsSphericalJoint(prim: pxr.Usd.Prim, body0: pxr.Usd.Prim, body1: pxr.Usd.Prim, frame: JointFrame, axis: pxr.Gf.Vec3f, coneAngle0Limit: typing.Optional[float] = None, coneAngle1Limit: typing.Optional[float] = None) -> pxr.UsdPhysics.SphericalJoint:
    pass
@typing.overload
def definePointCloud(stage: pxr.Usd.Stage, path: pxr.Sdf.Path, points: pxr.Vt.Vec3fArray, ids: typing.Optional[pxr.Vt.Int64Array] = None, widths: typing.Optional[FloatPrimvarData] = None, normals: typing.Optional[Vec3fPrimvarData] = None, displayColor: typing.Optional[Vec3fPrimvarData] = None, displayOpacity: typing.Optional[FloatPrimvarData] = None) -> pxr.UsdGeom.Points:
    """
    Defines a ``UsdGeom.Points`` prim on the stage.

    Attribute values will be validated and in the case of invalid data the Points will not be defined. An invalid ``UsdGeom.Points``
    object will be returned in this case.

    Values will be authored for all attributes required to completely describe the Points, even if weaker matching opinions already exist.

        - Point Count
        - Points
        - Extent

    The "extent" of the Points will be computed and authored based on the ``points`` and ``widths`` provided.

    The following common primvars can optionally be authored at the same time using a ``PrimvarData`` to specify interpolation, data,
    and optionally indices or elementSize.

        - Ids
        - Widths
        - Normals
        - Display Color
        - Display Opacity

    For both widths and normals, if they are provided, they are authored as ``primvars:widths`` and ``primvars:normals``, so that indexing is
    possible and to ensure that the value takes precedence in cases where both the non-primvar and primvar attributes are authored.

    Parameters:
        - **stage** The stage on which to define the points.
        - **path** The absolute prim path at which to define the points.
        - **points** Vertex/CV positions for the points described in local space.
        - **ids** Values for the id specification for the points.
        - **widths** Values for the width specification for the points.
        - **normals** Values for the normals primvar for the points. Only Vertex normals are considered valid.
        - **displayColor** Values to be authored for the display color primvar.
        - **displayOpacity** Values to be authored for the display opacity primvar.

    Returns
        ``UsdGeom.Points`` schema wrapping the defined ``Usd.Prim``



    Defines a ``UsdGeom.Points`` prim on the stage.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **parent** Prim below which to define the points.
        - **name** Name of the points prim.
        - **points** Vertex/CV positions for the points described in local space.
        - **ids** Values for the id specification for the points.
        - **widths** Values for the width specification for the points.
        - **normals** Values for the normals primvar for the points. Only Vertex normals are considered valid.
        - **displayColor** Values to be authored for the display color primvar.
        - **displayOpacity** Values to be authored for the display opacity primvar.

    Returns
        ``UsdGeom.Points`` schema wrapping the defined ``Usd.Prim``



    Defines a point cloud using the ``UsdGeom.Points`` schema.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Args:
        prim: Prim to define the point cloud on. The prim's type will be set to ``UsdGeom.Points``.
        points: Positions of the points.
        widths: Values for the width specification for the points.
        normals: Values for the normals primvar for the points.
        displayColor: Values to be authored for the display color primvar.
        displayOpacity: Values to be authored for the display opacity primvar.

    Returns:
        ``UsdGeom.Points`` schema wrapping the defined ``Usd.Prim``
    """
@typing.overload
def definePointCloud(parent: pxr.Usd.Prim, name: str, points: pxr.Vt.Vec3fArray, ids: typing.Optional[pxr.Vt.Int64Array] = None, widths: typing.Optional[FloatPrimvarData] = None, normals: typing.Optional[Vec3fPrimvarData] = None, displayColor: typing.Optional[Vec3fPrimvarData] = None, displayOpacity: typing.Optional[FloatPrimvarData] = None) -> pxr.UsdGeom.Points:
    pass
@typing.overload
def definePointCloud(prim: pxr.Usd.Prim, points: pxr.Vt.Vec3fArray, widths: typing.Optional[FloatPrimvarData] = None, normals: typing.Optional[Vec3fPrimvarData] = None, displayColor: typing.Optional[Vec3fPrimvarData] = None, displayOpacity: typing.Optional[FloatPrimvarData] = None) -> pxr.UsdGeom.Points:
    pass
@typing.overload
def definePolyMesh(stage: pxr.Usd.Stage, path: pxr.Sdf.Path, faceVertexCounts: pxr.Vt.IntArray, faceVertexIndices: pxr.Vt.IntArray, points: pxr.Vt.Vec3fArray, normals: typing.Optional[Vec3fPrimvarData] = None, uvs: typing.Optional[Vec2fPrimvarData] = None, displayColor: typing.Optional[Vec3fPrimvarData] = None, displayOpacity: typing.Optional[FloatPrimvarData] = None) -> pxr.UsdGeom.Mesh:
    """
    Defines a basic polygon mesh on the stage.

    All interrelated attribute values will be authored, even if weaker matching opinions already exist.

    The following common primvars can optionally be authored at the same time.

        - Normals
        - Primary UV Set
        - Display Color
        - Display Opacity

    Parameters:
        - **stage** - The stage on which to define the mesh
        - **path** - The absolute prim path at which to define the mesh
        - **faceVertexCounts** - The number of vertices in each face of the mesh
        - **faceVertexIndices** - Indices of the positions from the ``points`` to use for each face vertex
        - **points** - Vertex positions for the mesh described points in local space
        - **normals** - Values to be authored for the normals primvar
        - **uvs** - Values to be authored for the uv primvar
        - **displayColor** - Value to be authored for the display color primvar
        - **displayOpacity** - Value to be authored for the display opacity primvar

    Returns:
        ``UsdGeom.Mesh`` schema wrapping the defined ``Usd.Prim``.




    Defines a basic polygon mesh on the stage.

    All interrelated attribute values will be authored, even if weaker matching opinions already exist.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **parent** - Prim below which to define the mesh
        - **name** - Name of the mesh
        - **faceVertexCounts** - The number of vertices in each face of the mesh
        - **faceVertexIndices** - Indices of the positions from the ``points`` to use for each face vertex
        - **points** - Vertex positions for the mesh described points in local space
        - **normals** - Values to be authored for the normals primvar
        - **uvs** - Values to be authored for the uv primvar
        - **displayColor** - Value to be authored for the display color primvar
        - **displayOpacity** - Value to be authored for the display opacity primvar

    Returns:
        ``UsdGeom.Mesh`` schema wrapping the defined ``Usd.Prim``.




    Defines a basic polygon mesh on the stage.

    All interrelated attribute values will be authored, even if weaker matching opinions already exist.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **prim** - Existing prim to convert to a mesh
        - **faceVertexCounts** - The number of vertices in each face of the mesh
        - **faceVertexIndices** - Indices of the positions from the ``points`` to use for each face vertex
        - **points** - Vertex positions for the mesh described points in local space
        - **normals** - Values to be authored for the normals primvar
        - **uvs** - Values to be authored for the uv primvar
        - **displayColor** - Value to be authored for the display color primvar
        - **displayOpacity** - Value to be authored for the display opacity primvar

    Returns:
        ``UsdGeom.Mesh`` schema wrapping the defined ``Usd.Prim``.
    """
@typing.overload
def definePolyMesh(parent: pxr.Usd.Prim, name: str, faceVertexCounts: pxr.Vt.IntArray, faceVertexIndices: pxr.Vt.IntArray, points: pxr.Vt.Vec3fArray, normals: typing.Optional[Vec3fPrimvarData] = None, uvs: typing.Optional[Vec2fPrimvarData] = None, displayColor: typing.Optional[Vec3fPrimvarData] = None, displayOpacity: typing.Optional[FloatPrimvarData] = None) -> pxr.UsdGeom.Mesh:
    pass
@typing.overload
def definePolyMesh(prim: pxr.Usd.Prim, faceVertexCounts: pxr.Vt.IntArray, faceVertexIndices: pxr.Vt.IntArray, points: pxr.Vt.Vec3fArray, normals: typing.Optional[Vec3fPrimvarData] = None, uvs: typing.Optional[Vec2fPrimvarData] = None, displayColor: typing.Optional[Vec3fPrimvarData] = None, displayOpacity: typing.Optional[FloatPrimvarData] = None) -> pxr.UsdGeom.Mesh:
    pass
@typing.overload
def definePreviewMaterial(stage: pxr.Usd.Stage, path: pxr.Sdf.Path, color: pxr.Gf.Vec3f, opacity: float = 1.0, roughness: float = 0.5, metallic: float = 0.0) -> pxr.UsdShade.Material:
    """
    Defines a PBR ``UsdShade.Material`` driven by a ``UsdPreviewSurface`` shader network for the universal render context.

    The input parameters reflect a subset of the `UsdPreviewSurface specification <https://openusd.org/release/spec_usdpreviewsurface.html>`_
    commonly used when authoring materials using the metallic/metalness workflow (as opposed to the specular workflow). Many other inputs are
    available and can be authored after calling this function (including switching to the specular workflow).

    Parameters:
        - **stage** - The stage on which to define the Material
        - **path** - The absolute prim path at which to define the Material
        - **color** - The diffuse color of the Material
        - **opacity** - The Opacity Amount to set, 0.0-1.0 range where 1.0 = opaque and 0.0 = invisible
        - **roughness** - The Roughness Amount to set, 0.0-1.0 range where 1.0 = flat and 0.0 = glossy
        - **metallic** - The Metallic Amount to set, 0.0-1.0 range where 1.0 = max metallic and 0.0 = no metallic

    Returns:
        The newly defined ``UsdShade.Material``. Returns an Invalid prim on error



    Defines a PBR ``UsdShade.Material`` driven by a ``UsdPreviewSurface`` shader network for the universal render context.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **parent** - Prim below which to define the Material
        - **name** - Name of the Material
        - **color** - The diffuse color of the Material
        - **opacity** - The Opacity Amount to set, 0.0-1.0 range where 1.0 = opaque and 0.0 = invisible
        - **roughness** - The Roughness Amount to set, 0.0-1.0 range where 1.0 = flat and 0.0 = glossy
        - **metallic** - The Metallic Amount to set, 0.0-1.0 range where 1.0 = max metallic and 0.0 = no metallic

    Returns:
        The newly defined ``UsdShade.Material``. Returns an Invalid prim on error



    Defines a PBR ``UsdShade.Material`` driven by a ``UsdPreviewSurface`` shader network for the universal render context.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Args:
        prim: Prim to define the material on. The prim's type will be set to ``UsdShade.Material``.
        color: The diffuse color of the Material
        opacity: The Opacity Amount to set, 0.0-1.0 range where 1.0 = opaque and 0.0 = invisible
        roughness: The Roughness Amount to set, 0.0-1.0 range where 1.0 = flat and 0.0 = glossy
        metallic: The Metallic Amount to set, 0.0-1.0 range where 1.0 = max metallic and 0.0 = no metallic

    Returns:
        The newly defined ``UsdShade.Material``. Returns an Invalid object on error.
    """
@typing.overload
def definePreviewMaterial(parent: pxr.Usd.Prim, name: str, color: pxr.Gf.Vec3f, opacity: float = 1.0, roughness: float = 0.5, metallic: float = 0.0) -> pxr.UsdShade.Material:
    pass
@typing.overload
def definePreviewMaterial(prim: pxr.Usd.Prim, color: pxr.Gf.Vec3f, opacity: float = 1.0, roughness: float = 0.5, metallic: float = 0.0) -> pxr.UsdShade.Material:
    pass
@typing.overload
def defineRectLight(stage: pxr.Usd.Stage, path: pxr.Sdf.Path, width: float, height: float, intensity: float = 1.0, texturePath: typing.Optional[str] = None) -> pxr.UsdLux.RectLight:
    """
        Creates a rectangular (rect) light with an optional texture.

        A rect light represents light emitted from one side of a rectangle.

        Parameters:
            - **stage** - The stage in which the light should be authored
            - **path** - The path which the light prim should be written to
            - **width** - The width of the rectangular light, in the local X axis.
            - **height** - The height of the rectangular light, in the local Y axis.
            - **intensity** - The intensity value of the rectangular light
            - **texturePath** - Optional - The path to the texture file to use on the rectangular light.

        Returns:
            The rect light if created successfully.



        Creates a rectangular (rect) light with an optional texture.

        This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

        Parameters:
            - **parent** - Prim below which to define the light
            - **name** - Name of the light
            - **width** - The width of the rectangular light, in the local X axis.
            - **height** - The height of the rectangular light, in the local Y axis.
            - **intensity** - The intensity value of the rectangular light
            - **texturePath** - Optional - The path to the texture file to use on the rectangular light.

        Returns:
            The rect light if created successfully.



    Creates a rectangular (rect) light with an optional texture.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Args:
        prim: Prim to define the rectangular light on. The prim's type will be set to ``UsdLux.RectLight``.
        width: The width of the rectangular light, in the local X axis.
        height: The height of the rectangular light, in the local Y axis.
        intensity: The intensity value of the rectangular light.
        texturePath: The path to the texture file to use on the rectangular light.

    Returns:
        The light if created successfully.
    """
@typing.overload
def defineRectLight(parent: pxr.Usd.Prim, name: str, width: float, height: float, intensity: float = 1.0, texturePath: typing.Optional[str] = None) -> pxr.UsdLux.RectLight:
    pass
@typing.overload
def defineRectLight(prim: pxr.Usd.Prim, width: float, height: float, intensity: float = 1.0, texturePath: typing.Optional[str] = None) -> pxr.UsdLux.RectLight:
    pass
@typing.overload
def defineReference(stage: pxr.Usd.Stage, path: pxr.Sdf.Path, source: pxr.Usd.Prim) -> pxr.Usd.Prim:
    """
    Define a reference to a prim.

    This creates a reference prim that targets a prim in another layer (external reference) or the same layer (internal reference).

    The reference's assetPath will be set to the relative identifier between the stage's edit target and the source's stage if it's
    an external reference with a valid relative path.

    For more information, see:
        - https://openusd.org/release/glossary.html#usdglossary-references
        - https://openusd.org/release/api/class_usd_references.html#details

    Parameters:
        - **stage** - The stage on which to define the reference
        - **path** - The absolute prim path at which to define the reference
        - **source** - The prim to reference

    Returns:
        The newly created reference prim. Returns an invalid prim on error.




    Define a reference to a prim as a child of the ``parent`` prim

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **parent** - The parent prim to add the reference to
        - **source** - The prim to reference
        - **name** - The name of the reference. If not provided, uses the source prim's name

    Returns:
        The newly created reference prim. Returns an invalid prim on error.
    """
@typing.overload
def defineReference(parent: pxr.Usd.Prim, source: pxr.Usd.Prim, name: typing.Optional[str] = None) -> pxr.Usd.Prim:
    pass
@typing.overload
def defineScope(stage: pxr.Usd.Stage, path: pxr.Sdf.Path) -> pxr.UsdGeom.Scope:
    """
    Defines a scope on the stage.

    A scope is a simple grouping primitive that is useful for organizing prims in a scene.

    Parameters:
        - **stage** - The stage on which to define the scope
        - **path** - The absolute prim path at which to define the scope

    Returns:
        A ``UsdGeom.Scope`` schema wrapping the defined ``Usd.Prim``. Returns an invalid schema on error.




    Defines a scope on the stage.

    This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

    Parameters:
        - **parent** - Prim below which to define the scope
        - **name** - Name of the scope

    Returns:
        A ``UsdGeom.Scope`` schema wrapping the defined ``Usd.Prim``. Returns an invalid schema on error.




    Defines a scope from an existing prim.

    This converts an existing prim to a Scope type.

    Parameters:
        - **prim** - The existing prim to convert to a scope

    Returns:
        A ``UsdGeom.Scope`` schema wrapping the defined ``Usd.Prim``. Returns an invalid schema on error.
    """
@typing.overload
def defineScope(parent: pxr.Usd.Prim, name: str) -> pxr.UsdGeom.Scope:
    pass
@typing.overload
def defineScope(prim: pxr.Usd.Prim) -> pxr.UsdGeom.Scope:
    pass
@typing.overload
def defineXform(stage: pxr.Usd.Stage, path: pxr.Sdf.Path, transform: typing.Optional[pxr.Gf.Transform] = None) -> pxr.UsdGeom.Xform:
    """
    Defines an xform on the stage.

    Parameters:
        - **stage** - The stage on which to define the xform
        - **path** - The absolute prim path at which to define the xform
        - **transform** - Optional local transform to set

    Returns:
        UsdGeom.Xform schema wrapping the defined Usd.Prim. Returns an invalid schema on error.



    Defines an xform on the stage.

    Parameters:
        - **parent** - Prim below which to define the xform
        - **name** - Name of the xform
        - **transform** - Optional local transform to set

    Returns:
        UsdGeom.Xform schema wrapping the defined Usd.Prim. Returns an invalid schema on error.



    Defines an xform from an existing prim.

    This converts an existing prim to an Xform type, preserving any existing transform data.

    Parameters:
        - **prim** - The existing prim to convert to an xform
        - **transform** - Optional local transform to set

    Returns:
        UsdGeom.Xform schema wrapping the converted Usd.Prim.
    """
@typing.overload
def defineXform(parent: pxr.Usd.Prim, name: str, transform: typing.Optional[pxr.Gf.Transform] = None) -> pxr.UsdGeom.Xform:
    pass
@typing.overload
def defineXform(prim: pxr.Usd.Prim, transform: typing.Optional[pxr.Gf.Transform] = None) -> pxr.UsdGeom.Xform:
    pass
def exportLayer(layer: pxr.Sdf.Layer, identifier: str, authoringMetadata: str, comment: typing.Optional[str] = None, fileFormatArgs: typing.Dict[str, str] = {}) -> bool:
    """
    Export the given ``Sdf.Layer`` to an identifier with an optional comment.

    Note:

        This does not impact sublayers or any stages that this layer may be contributing to. See ``setLayerAuthoringMetadata`` for details.
        This is to preserve authoring metadata on referenced layers that came from other applications.

    Args:
        layer: The layer to be exported.
        identifier: The identifier to be used for the new layer.
        authoringMetadata: The provenance information from the host application. See ``setLayerAuthoringMetadata`` for details.
            If the "creator" key already exists, it will not be overwritten & this data will be ignored.
        comment: The comment will be authored in the layer as the ``Sdf.Layer`` comment.
        fileFormatArgs: Additional file format-specific arguments to be supplied during layer export.

    Returns:
        A bool indicating if the export was successful.
    """
def getAssetToken() -> str:
    """
    Get the Asset token.

    Returns:
        The Asset token.
    """
def getColorSpaceToken(value: ColorSpace) -> str:
    """
    Get the `str` matching a given `ColorSpace`

    The string representation is typically used when setting shader inputs, such as ``inputs:sourceColorSpace`` on ``UsdUVTexture``.

    Args:
        value: The ``ColorSpace``

    Returns:
        The `str` for the given ``ColorSpace`` value
    """
def getContentsToken() -> str:
    """
    Get the token for the Contents layer.

    Returns:
        The token for the Contents layer.
    """
def getDiagnosticLevel(code: pxr.Tf.DiagnosticType) -> DiagnosticsLevel:
    """
    Get the ``DiagnosticsLevel`` for a given ``TfDiagnosticType``.

    Args:
        code: The ``TfDiagnosticType`` to get the ``DiagnosticsLevel`` for.

    Returns:
        The ``DiagnosticsLevel`` for the ``TfDiagnosticType``.
    """
def getDiagnosticsLevel() -> DiagnosticsLevel:
    """
    Get the current ``DiagnosticsLevel`` for the ``Delegate``.

    This can be called at any time, but the filtering will only take affect after calling ``activateDiagnosticsDelegate()``.

    Returns:
        The current ``DiagnosticsLevel`` for the ``Delegate``.
    """
def getDiagnosticsOutputStream() -> DiagnosticsOutputStream:
    """
    Get the current ``DiagnosticsOutputStream`` for the ``Delegate``.

    This can be called at any time, but will only take affect after calling ``activateDiagnosticsDelegate()``.

    Returns:
        The current ``DiagnosticsOutputStream`` for the ``Delegate``.
    """
def getDisplayName(prim: pxr.Usd.Prim) -> str:
    """
    Return this prim's display name (metadata).

    Args:
        prim: The prim to get the display name from

    Returns:
        Authored value, or an empty string if no display name has been set.
    """
def getGeometryToken() -> str:
    """
    Get the token for the Geometry layer and scope.

    Returns:
        The token for the Geometry layer and scope.
    """
def getLayerAuthoringMetadata(layer: pxr.Sdf.Layer) -> str:
    """
    Get metadata from the ``Sdf.Layer`` indicating the provenance of the data.

    Note:

        This metadata is strictly informational, it is not advisable to drive runtime behavior from this metadata.
        In the future, the "creator" key may change, or a more formal specification for data provenance may emerge.

    This function retrieves the provenance information from the "creator" key of the CustomLayerData.

    Args:
        layer: The layer to read from

    Returns:
        The provenance information for this layer, or an empty string if none exists
    """
def getLibraryToken() -> str:
    """
    Get the token for the Library layer.

    Returns:
        The token for the Library layer.
    """
def getLightAttr(defaultAttr: pxr.Usd.Attribute) -> pxr.Usd.Attribute:
    """
    Get the "correct" light attribute for a light that could have any combination of authored old and new UsdLux schema attributes

    The new attribute names have "inputs:" prepended to the names to make them connectable.

        - Light has only "intensity" authored: return "intensity" attribute

        - Light has only "inputs:intensity" authored: return "inputs:intensity" attribute

        - Light has both "inputs:intensity" and "intensity" authored: return "inputs:intensity"

    Args:
        defaultAttr: The attribute to read from the light schema: eg. ``UsdLux.RectLight.GetHeightAttr()``

    Returns:
        The attribute from which the light value should be read
    """
@typing.overload
def getLocalTransform(prim: pxr.Usd.Prim, time: pxr.Usd.TimeCode = nan) -> pxr.Gf.Transform:
    """
    Get the local transform of a prim at a given time.

    Args:
        prim: The prim to get local transform from.
        time: Time at which to query the value.

    Returns:
        Transform value as a transform.




    Get the local transform of an xformable at a given time.

    Args:
        xformable: The xformable to get local transform from.
        time: Time at which to query the value.

    Returns:
        Transform value as a transform.
    """
@typing.overload
def getLocalTransform(xformable: pxr.UsdGeom.Xformable, time: pxr.Usd.TimeCode = nan) -> pxr.Gf.Transform:
    pass
@typing.overload
def getLocalTransformComponents(prim: pxr.Usd.Prim, time: pxr.Usd.TimeCode = nan) -> tuple:
    """
    Get the local transform of a prim at a given time in the form of common transform components.

    Args:
        prim: The prim to get local transform from.
        time: Time at which to query the value.

    Returns:
        Transform value as a tuple of translation, pivot, rotation, rotation order, scale.




    Get the local transform of an xformable at a given time in the form of common transform components.

    Args:
        xformable: The xformable to get local transform from.
        time: Time at which to query the value.

    Returns:
        Transform value as a tuple of translation, pivot, rotation, rotation order, scale.
    """
@typing.overload
def getLocalTransformComponents(xformable: pxr.UsdGeom.Xformable, time: pxr.Usd.TimeCode = nan) -> tuple:
    pass
@typing.overload
def getLocalTransformComponentsQuat(prim: pxr.Usd.Prim, time: pxr.Usd.TimeCode = nan) -> tuple:
    """
    Get the local transform of a prim at a given time in the form of common transform components with quaternion orientation.

    Args:
        prim: The prim to get local transform from.
        time: Time at which to query the value.

    Returns:
        Transform value as a tuple of translation, pivot, orientation (quaternion), scale.




    Get the local transform of an xformable at a given time in the form of common transform components with quaternion orientation.

    Args:
        xformable: The xformable to get local transform from.
        time: Time at which to query the value.

    Returns:
        Transform value as a tuple of translation, pivot, orientation (quaternion), scale.
    """
@typing.overload
def getLocalTransformComponentsQuat(xformable: pxr.UsdGeom.Xformable, time: pxr.Usd.TimeCode = nan) -> tuple:
    pass
@typing.overload
def getLocalTransformMatrix(prim: pxr.Usd.Prim, time: pxr.Usd.TimeCode = nan) -> pxr.Gf.Matrix4d:
    """
    Get the local transform of a prim at a given time in the form of a 4x4 matrix.

    Args:
        prim: The prim to get local transform from.
        time: Time at which to query the value.

    Returns:
        Transform value as a 4x4 matrix.




    Get the local transform of an xformable at a given time in the form of a 4x4 matrix.

    Args:
        xformable: The xformable to get local transform from.
        time: Time at which to query the value.

    Returns:
        Transform value as a 4x4 matrix.
    """
@typing.overload
def getLocalTransformMatrix(xformable: pxr.UsdGeom.Xformable, time: pxr.Usd.TimeCode = nan) -> pxr.Gf.Matrix4d:
    pass
def getMaterialsToken() -> str:
    """
    Get the token for the Materials layer and scope.

    Returns:
        The token for the Materials layer and scope.
    """
def getPayloadToken() -> str:
    """
    Get the token for the Payload directory.

    Returns:
        The token for the Payload directory.
    """
def getPhysicsToken() -> str:
    """
    Get the token for the Physics layer and scope.

    Returns:
        The token for the Physics layer and scope.
    """
def getTexturesToken() -> str:
    """
    Get the token for the Textures directory.

    Returns:
        The token for the Textures directory.
    """
def getValidChildName(prim: pxr.Usd.Prim, name: str) -> str:
    """
    Take a prim and a preferred name. Return a valid and unique name as the child name of the given prim.

    Args:
        prim: The USD prim where the given prim name should live under.
        names: A preferred prim name.

    Returns:
        A valid and unique name.
    """
def getValidChildNames(prim: pxr.Usd.Prim, names: typing.List[str]) -> list(str):
    """
    Take a prim and a vector of the preferred names. Return a matching vector of valid and unique names as the child names of the given prim.

    Args:
        prim: The USD prim where the given prim names should live under.
        names: A vector of preferred prim names.

    Returns:
        A vector of valid and unique names.
    """
def getValidPrimName(name: str) -> str:
    """
    Produce a valid prim name from the input name

    Args:
        name: The input name

    Returns:
        A string that is considered valid for use as a prim name.
    """
def getValidPrimNames(names: typing.List[str], reservedNames: list(str) = []) -> list(str):
    """
    Take a vector of the preferred names and return a matching vector of valid and unique names.

    Args:
        names: A vector of preferred prim names.
        reservedNames: A vector of reserved prim names. Names in the vector will not be included in the returns.

    Returns:
        A vector of valid and unique names.
    """
def getValidPropertyName(name: str) -> str:
    """
    Produce a valid property name using the Bootstring algorithm.

    Args:
        name: The input name

    Returns:
        A string that is considered valid for use as a property name.
    """
def getValidPropertyNames(names: typing.List[str], reservedNames: list(str) = []) -> list(str):
    """
    Take a vector of the preferred names and return a matching vector of valid and unique names.

    Args:
        names: A vector of preferred property names.
        reservedNames: A vector of reserved prim names. Names in the vector will not be included in the return.

    Returns:
        A vector of valid and unique names.
    """
def hasLayerAuthoringMetadata(layer: pxr.Sdf.Layer) -> bool:
    """
    Check if the ``Sdf.Layer`` has metadata indicating the provenance of the data.

    Note:

        This metadata is strictly informational, it is not advisable to drive runtime behavior from this metadata.
        In the future, the "creator" key may change, or a more formal specification for data provenance may emerge.

    Checks the CustomLayerData for a "creator" key.

    Args:
        layer: The layer to check

    Returns:
        A bool indicating if the metadata exists
    """
def isDiagnosticsDelegateActive() -> bool:
    """
    Test whether the ``Delegate`` is currently active.

    When active, the ``Delegate`` replaces the default ``TfDiagnosticMgr`` printing with a more customized result.
    See ``activateDiagnosticsDelegate()`` for more details.

    Returns:
        Whether the `Delegate` is active
    """
@typing.overload
def isEditablePrimLocation(stage: pxr.Usd.Stage, path: pxr.Sdf.Path) -> tuple:
    """
    Validate that prim opinions could be authored at this path on the stage

    This validates that the ``stage`` and ``path`` are valid, and that the path is absolute.
    If a prim already exists at the given path it must not be an instance proxy.

    If the location is invalid and ``reason`` is non-null, an error message describing the validation error will be set.

    Parameters:
        - **stage** - The stage to consider.
        - **path** - The absolute to consider.

    Returns:
        Tuple[bool, str] with a bool indicating if the location is valid, and the string is a non-empty reason if the location is invalid.



    Validate that prim opinions could be authored for a child prim with the given name

    This validates that the ``prim`` is valid, and that the ``name`` is a valid identifier.
    If a prim already exists at the given path it must not be an instance proxy.

    If the location is invalid and ``reason`` is non-null, an error message describing the validation error will be set.

    Parameters:
        - **parent** - The UsdPrim which would be the parent of the proposed location.
        - **name** - The name which would be used for the UsdPrim at the proposed location.

    Returns:
        Tuple[bool, str] with a bool indicating if the location is valid, and the string is a non-empty reason if the location is invalid.




    Validate that prim opinions could be authored for the prim

    This validates that the ``prim`` is valid and not be an instance proxy.

    If the location is invalid and ``reason`` is non-null, an error message describing the validation error will be set.

    Parameters:
        - **prim** - The UsdPrim to consider.

    Returns:
        Tuple[bool, str] with a bool indicating if the location is valid, and the string is a non-empty reason if the location is invalid.
    """
@typing.overload
def isEditablePrimLocation(prim: pxr.Usd.Prim, name: str) -> tuple:
    pass
@typing.overload
def isEditablePrimLocation(prim: pxr.Usd.Prim) -> tuple:
    pass
def isLight(prim: pxr.Usd.Prim) -> bool:
    """
    Determines if a UsdPrim has a ``UsdLux.LightAPI`` schema applied

    Args:
        prim: The prim to check for an applied ``UsdLux.LightAPI`` schema

    Returns:
        True if the prim has a ``UsdLux.LightAPI`` schema applied
    """
def linearToSrgb(color: pxr.Gf.Vec3f) -> pxr.Gf.Vec3f:
    """
    Translate a linear color value to sRGB color space

    Many 3D modeling applications define colors in sRGB (0-1) color space. Many others use a linear color space that aligns with how light
    and color behave in the natural world. When authoring ``UsdShade.Shader`` color input data, including external texture assets, you may
    need to translate between color spaces.

    Note:

        Color is a complex topic in 3D rendering and providing utilities covering the full breadth of color science is beyond the scope of this
        module. See this [MathWorks article](https://www.mathworks.com/help/images/understanding-color-spaces-and-color-space-conversion.html)
        for a relatively brief introduction. If you need more specific color handling please use a dedicated color science library like
        [OpenColorIO](https://opencolorio.org).

    Args:
        color: linear representation of a color to be translated to sRGB color space

    Returns:
        The translated color in sRGB color space
    """
def removeMaterialInterface(material: pxr.UsdShade.Material, bakeValues: bool = True) -> bool:
    """
    Removes any ``UsdShade.Inputs`` found on the material prim.

    All ``UsdShade.Inputs`` on the ``UsdShade.Material`` will be disconnected from any underlying shader inputs, then removed from the
    material. The current values may be optionally "baked down" onto the shader inputs in order to retain the current material behavior,
    or may be discarded in order to revert to a default appearance based on the shader definitions.

    Note:

        While ``addPreviewMaterialInterface`` is specific to Preview Material shader networks, ``removeMaterialInterface`` *affects all
        render contexts* and will remove all ``UsdShade.Inputs`` returned via ``UsdShade.Material.GetInterfaceInputs()``, baking down the
        values onto all consumer shaders, regardless of render context.

    Args:
        material: The material prim
        bakeValues: Whether or not the current Material inputs values are set on the underlying Shader inputs

    Returns:
        Whether or not the Material inputs were removed successfully
    """
def sRgbToLinear(color: pxr.Gf.Vec3f) -> pxr.Gf.Vec3f:
    """
    Translate an sRGB color value to linear color space

    Many 3D modeling applications define colors in sRGB (0-1) color space. Many others use a linear color space that aligns with how light
    and color behave in the natural world. When authoring ``UsdShade.Shader`` color input data, including external texture assets, you may
    need to translate between color spaces.

    Note:

        Color is a complex topic in 3D rendering and providing utilities covering the full breadth of color science is beyond the scope of this
        module. See this [MathWorks article](https://www.mathworks.com/help/images/understanding-color-spaces-and-color-space-conversion.html)
        for a relatively brief introduction. If you need more specific color handling please use a dedicated color science library like
        [OpenColorIO](https://opencolorio.org).

    Args:
        color: sRGB representation of a color to be translated to linear color space

    Returns:
        The translated color in linear color space
    """
def saveLayer(layer: pxr.Sdf.Layer, authoringMetadata: typing.Optional[str] = None, comment: typing.Optional[str] = None) -> bool:
    """
    Save the given ``Sdf.Layer`` with an optional comment

    Note:

        This does not impact sublayers or any stages that this layer may be contributing to. See ``setLayerAuthoringMetadata`` for details.
        This is to preserve authoring metadata on referenced layers that came from other applications.

    Args:
        layer: The stage to be saved.
        authoringMetadata: The provenance information from the host application. See ``setLayerAuthoringMetadata`` for details.
        comment: The comment will be authored in the layer as the ``Sdf.Layer`` comment.

     Returns:
        A bool indicating if the save was successful.
    """
def saveStage(stage: pxr.Usd.Stage, authoringMetadata: typing.Optional[str] = None, comment: typing.Optional[str] = None) -> None:
    """
    Save the given ``Usd.Stage`` with metadata applied to all dirty layers.

    Save all dirty layers and sublayers contributing to this stage.

    All dirty layers will be annotated with authoring metadata, unless previously annotated. This is to preserve
    authoring metadata on referenced layers that came from other applications.

    The comment will be authored in all layers as the SdfLayer comment.

    Args:
        stage: The stage to be saved.
        authoringMetadata: The provenance information from the host application. See ``setLayerAuthoringMetadata`` for details.
            If the "creator" key already exists on a given layer, it will not be overwritten & this data will be ignored.
        comment: The comment will be authored in all dirty layers as the ``Sdf.Layer`` comment.
    """
def setDiagnosticsLevel(value: DiagnosticsLevel) -> None:
    """
    Set the ``DiagnosticsLevel`` for the ``Delegate`` to filter ``TfDiagnostics`` by severity.

    This can be called at any time, but the filtering will only take affect after calling ``activateDiagnosticsDelegate()``.

    Args:
        value: The highest severity ``DiagnosticsLevel`` that should be emitted.
    """
def setDiagnosticsOutputStream(value: DiagnosticsOutputStream) -> None:
    """
    Set the ``DiagnosticsOutputStream`` for the ``Delegate`` to redirect ``Tf.Diagnostics`` to different streams.

    This can be called at any time, but will only take affect after calling ``activateDiagnosticsDelegate()``.

    Args:
        value: The stream to which all diagnostics should be emitted.
    """
def setDisplayName(prim: pxr.Usd.Prim, name: str) -> bool:
    """
    Sets this prim's display name (metadata)

    DisplayName is meant to be a descriptive label, not necessarily an alternate identifier; therefore there is no restriction on which
    characters can appear in it

    Args:
        prim: The prim to set the display name for
        name: The value to set

    Returns:
        True on success, otherwise false
    """
def setLayerAuthoringMetadata(layer: pxr.Sdf.Layer, value: str) -> None:
    """
    Set metadata on the ``Sdf.Layer`` indicating the provenance of the data.

    It is desirable to capture data provenance information into the metadata of SdfLayers, in order to keep track of what tools & versions
    were used throughout content creation pipelines, and to capture notes from the content author. While OpenUSD does not currently have a
    formal specification for this authoring metadata, some conventions have emerged throughout the OpenUSD Ecosystem.

    The most common convention for tool tracking is to include a "creator" string in the ``Sdf.Layer.customLayerData``. Similarly, notes from
    the content author should be captured via ``Sdf.Layer.SetComment``. While these are trivial using ``Sdf.Layer`` public methods, they are
    also easy to forget, and difficult to discover.

    This function assists authoring applications in settings authoring metadata, so that each application can produce consistant provenance
    information. The metadata should only add information which can be used to track the data back to its origin. It should not be used to
    store sensitive information about the content, nor about the end user (i.e. do not use it to store Personal Identifier Information).

    Example:

        .. code-block:: python

            layer = Sdf.Layer.CreateAnonymous()
            authoring_metadata = "My Content Editor® 2024 SP 2, USD Exporter Plugin v1.1.23.11"
            usdex.core.exportLayer(layer, file_name, authoring_metadata, user_comment);

    Note:

        This metadata is strictly informational, it is not advisable to drive runtime behavior from this metadata.
        In the future, the "creator" key may change, or a more formal specification for data provenance may emerge.

    Args:
        layer: The layer to modify
        value: The provenance information for this layer
    """
@typing.overload
def setLocalTransform(prim: pxr.Usd.Prim, transform: pxr.Gf.Transform, time: pxr.Usd.TimeCode = nan) -> bool:
    """
    Set the local transform of a prim.

    Parameters:
        - **prim** - The prim to set local transform on.
        - **transform** - The transform value to set.
        - **time** - Time at which to write the value.

    Returns:
        A bool indicating if the local transform was set.




    Set the local transform of a prim from a 4x4 matrix.

    Parameters:
        - **prim** - The prim to set local transform on.
        - **matrix** - The matrix value to set.
        - **time** - Time at which to write the value.

    Returns:
        A bool indicating if the local transform was set.




    Set the local transform of a prim from common transform components.

    Parameters:
        - **prim** - The prim to set local transform on.
        - **translation** - The translation value to set.
        - **pivot** - The pivot position value to set.
        - **rotation** - The rotation value to set in degrees.
        - **rotationOrder** - The rotation order of the rotation value.
        - **scale** - The scale value to set.
        - **time** - Time at which to write the value.

    Returns:
        A bool indicating if the local transform was set.




    Set the local transform of a prim from common transform components using a quaternion for orientation.

    Parameters:
        - **prim** - The prim to set local transform on.
        - **translation** - The translation value to set.
        - **orientation** - The orientation value to set as a quaternion.
        - **scale** - The scale value to set - defaults to (1.0, 1.0, 1.0).
        - **time** - Time at which to write the value.

    Returns:
        A bool indicating if the local transform was set.




    Set the local transform of an xformable.

    Args:
        xformable: The xformable to set local transform on.
        transform: The transform value to set.
        time: Time at which to write the value.

    Returns:
        A bool indicating if the local transform was set.




    Set the local transform of an xformable from a 4x4 matrix.

    Args:
        xformable: The xformable to set local transform on.
        matrix: The matrix value to set.
        time: Time at which to write the value.

    Returns:
        A bool indicating if the local transform was set.




    Set the local transform of an xformable from common transform components.

    Args:
        xformable: The xformable to set local transform on.
        translation: The translation value to set.
        pivot: The pivot position value to set.
        rotation: The rotation value to set in degrees.
        rotationOrder: The rotation order of the rotation value.
        scale: The scale value to set.
        time: Time at which to write the value.

    Returns:
        A bool indicating if the local transform was set.




    Set the local transform of an xformable from common transform components using a quaternion for orientation.

    Args:
        xformable: The xformable to set local transform on.
        translation: The translation value to set.
        orientation: The orientation value to set as a quaternion.
        scale: The scale value to set - defaults to (1.0, 1.0, 1.0).
        time: Time at which to write the value.

    Returns:
        A bool indicating if the local transform was set.
    """
@typing.overload
def setLocalTransform(prim: pxr.Usd.Prim, matrix: pxr.Gf.Matrix4d, time: pxr.Usd.TimeCode = nan) -> bool:
    pass
@typing.overload
def setLocalTransform(prim: pxr.Usd.Prim, translation: pxr.Gf.Vec3d, pivot: pxr.Gf.Vec3d, rotation: pxr.Gf.Vec3f, rotationOrder: RotationOrder, scale: pxr.Gf.Vec3f, time: pxr.Usd.TimeCode = nan) -> bool:
    pass
@typing.overload
def setLocalTransform(prim: pxr.Usd.Prim, translation: pxr.Gf.Vec3d, orientation: pxr.Gf.Quatf, scale: pxr.Gf.Vec3f = Gf.Vec3f(1.0, 1.0, 1.0), time: pxr.Usd.TimeCode = nan) -> bool:
    pass
@typing.overload
def setLocalTransform(xformable: pxr.UsdGeom.Xformable, transform: pxr.Gf.Transform, time: pxr.Usd.TimeCode = nan) -> bool:
    pass
@typing.overload
def setLocalTransform(xformable: pxr.UsdGeom.Xformable, matrix: pxr.Gf.Matrix4d, time: pxr.Usd.TimeCode = nan) -> bool:
    pass
@typing.overload
def setLocalTransform(xformable: pxr.UsdGeom.Xformable, translation: pxr.Gf.Vec3d, pivot: pxr.Gf.Vec3d, rotation: pxr.Gf.Vec3f, rotationOrder: RotationOrder, scale: pxr.Gf.Vec3f, time: pxr.Usd.TimeCode = nan) -> bool:
    pass
@typing.overload
def setLocalTransform(xformable: pxr.UsdGeom.Xformable, translation: pxr.Gf.Vec3d, orientation: pxr.Gf.Quatf, scale: pxr.Gf.Vec3f = Gf.Vec3f(1.0, 1.0, 1.0), time: pxr.Usd.TimeCode = nan) -> bool:
    pass
def version() -> str:
    """
    Verify the expected usdex modules are being loaded at runtime.

    Returns:
        A human-readable version string for the usdex modules.
    """
enableTranscodingSetting = 'USDEX_ENABLE_TRANSCODING'
