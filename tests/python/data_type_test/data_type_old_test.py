import os
from tests.python.data_type_test.parsy_utils import alt_class, strings, strings_from_tuple

from parsy import ParseError, alt, forward_declaration, regex, seq, string

SCRIPT_FILE = os.path.abspath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_FILE)

INPUT_DATA_FILE = os.path.join(SCRIPT_DIR, "blender-4.0-data_types.txt")


SPACE = string(" ")
GRAVE_QUOTE = string("`")
SINGLE_QUOTE = string("'")
DOUBLE_QUOTE = string('"')
DOT = string(".")
COMMA = string(",")
COMMA_SPACE = COMMA + SPACE
BRACK_L = string("[")
BRACK_R = string("]")
BRACE_L = string("{")
BRACE_R = string("}")
PAREN_L = string("(")
PAREN_R = string(")")


NAME = regex(r"[a-zA-Z_]\w*")
NAME_GRAVE_QUOTE = GRAVE_QUOTE >> NAME << GRAVE_QUOTE

PRIMARY = NAME.sep_by(DOT).map(".".join)
# PRIMARY_GRAVE_QUOTE = GRAVE_QUOTE >> PRIMARY << GRAVE_QUOTE
# PRIMARY_SINGLE_QUOTE = SINGLE_QUOTE >> PRIMARY << SINGLE_QUOTE

GENERIC_TYPE = SINGLE_QUOTE >> string("GenericType") << SINGLE_QUOTE

BL_OPERATORS = GRAVE_QUOTE >> string("bl_operators.") + PRIMARY << GRAVE_QUOTE
BL_UI_PROPERTIES = GRAVE_QUOTE >> string("bl_ui.properties_") + PRIMARY << GRAVE_QUOTE | string("bl_ui.properties_") + PRIMARY
BL_UI_SPACE = GRAVE_QUOTE >> string("bl_ui.space_") + PRIMARY << GRAVE_QUOTE | string("bl_ui.space_") + PRIMARY
BL_UI_UI_UL_LIST = GRAVE_QUOTE >> string("bl_ui.UI_UL_list") << GRAVE_QUOTE


ACTION_OT = GRAVE_QUOTE >> alt_class(("duplicate",), "ACTION_OT_", False) << GRAVE_QUOTE
ARMATURE_OT = GRAVE_QUOTE >> alt_class(("duplicate", "extrude"), "ARMATURE_OT_", False) << GRAVE_QUOTE
CLIP_OT = GRAVE_QUOTE >> string("CLIP_OT_add_marker") << GRAVE_QUOTE
CURVE_OT = GRAVE_QUOTE >> alt_class(("duplicate", "extrude"), "CURVE_OT_", False) << GRAVE_QUOTE
GPENCIL_OT = GRAVE_QUOTE >> alt_class(("duplicate", "extrude"), "GPENCIL_OT_", False) << GRAVE_QUOTE
GRAPH_OT = GRAVE_QUOTE >> alt_class(("duplicate",), "GRAPH_OT_", False) << GRAVE_QUOTE
MAKS_OT = (
    GRAVE_QUOTE >> alt_class(("add_feather_vertex", "add_vertex", "duplicate", "slide_point"), "MASK_OT_", False) << GRAVE_QUOTE
)
MATHUTILS_BVHTREE_BVHTREE = GRAVE_QUOTE >> alt_class(("BVHTree",), "mathutils.bvhtree.") << GRAVE_QUOTE
MBALL_OT = GRAVE_QUOTE >> alt_class(("duplicate_metaelems",), "MBALL_OT_", False) << GRAVE_QUOTE
NLA_OT = GRAVE_QUOTE >> alt_class(("duplicate",), "NLA_OT_", False) << GRAVE_QUOTE
OBJECT_OT = GRAVE_QUOTE >> alt_class(("duplicate",), "OBJECT_OT_", False) << GRAVE_QUOTE
PAINTCURVE_OT = (
    GRAVE_QUOTE
    >> alt_class(
        (
            "add_point",
            "slide",
        ),
        "PAINTCURVE_OT_",
        False,
    )
    << GRAVE_QUOTE
)

NODE_OT = (
    GRAVE_QUOTE
    >> alt_class(
        (
            "attach",
            "detach",
            "duplicate",
            "link_viewer",
            "links_detach",
            "select",
            "translate_attach",
        ),
        "NODE_OT_",
        False,
    )
    << GRAVE_QUOTE
)

MESH_OT = (
    GRAVE_QUOTE
    >> alt_class(
        (
            "duplicate",
            "extrude_context",
            "extrude_edges_indiv",
            "extrude_faces_indiv",
            "extrude_region",
            "extrude_verts_indiv",
            "loopcut",
            "offset_edge_loops",
            "polybuild_face_at_cursor",
            "polybuild_split_at_cursor",
            "polybuild_transform_at_cursor",
            "rip_edge",
            "rip",
        ),
        "MESH_OT_",
        False,
    )
    << GRAVE_QUOTE
)

SEQUENCER_OT = GRAVE_QUOTE >> alt_class(("duplicate",), "SEQUENCER_OT_", False) << GRAVE_QUOTE

TRANSFORM_OT = (
    GRAVE_QUOTE
    >> alt_class(
        (
            "edge_slide",
            "seq_slide",
            "shrink_fatten",
            "transform",
            "translate",
        ),
        "TRANSFORM_OT_",
        False,
    )
    << GRAVE_QUOTE
)

UV_OT = GRAVE_QUOTE >> alt_class(("rip",), "UV_OT_", False) << GRAVE_QUOTE

NUMPY = GRAVE_QUOTE >> alt_class(("ndarray",), "numpy.") << GRAVE_QUOTE


GRAVE_QUOTE_TYPES = (
    GRAVE_QUOTE
    >> alt_class(
        (
            "CyclesCurveRenderSettings",
            "CyclesLightSettings",
            "CyclesMaterialSettings",
            "CyclesMeshSettings",
            "CyclesObjectSettings",
            "CyclesRenderLayerSettings",
            "CyclesRenderSettings",
            "CyclesView3DShadingSettings",
            "CyclesVisibilitySettings",
            "CyclesWorldSettings",
            "idprop.type.IDPropertyGroupViewItems",
            "idprop.type.IDPropertyGroupViewKeys",
            "idprop.type.IDPropertyGroupViewValues",
        )
    )
    << GRAVE_QUOTE
)

SINGLE_QUOTE_TYPES = (
    SINGLE_QUOTE
    >> alt_class(
        (
            "BMLayerCollection",
            "BoneCollection",
            "Collection",
        )
    )
    << SINGLE_QUOTE
)

FREESTYLE_TYPES = (
    GRAVE_QUOTE
    >> alt_class(
        (
            "AdjacencyIterator",
            "BBox",
            "BinaryPredicate1D",
            "Chain",
            "ChainingIterator",
            "CurvePointIterator",
            "FEdge",
            "FEdgeSharp",
            "FEdgeSmooth",
            "Id",
            "IntegrationType",
            "Interface0D",
            "Interface0DIterator",
            "Interface1D",
            "Material",
            "MediumType",
            "Nature",
            "orientedViewEdgeIterator",
            "SShape",
            "Stroke",
            "StrokeAttribute",
            "StrokeVertex",
            "SVertex",
            "SVertexIterator",
            "UnaryPredicate1D",
            "ViewEdge",
            "ViewShape",
            "StrokeVertexIterator",
            "ViewVertex",
            "UnaryFunction0D",
            "UnaryFunction0DDouble",
            "UnaryFunction1DVoid",
            "UnaryPredicate0D",
        ),
        "freestyle.types.",
    )
    << GRAVE_QUOTE
)

FREESTYLE_CHAININGITERATORS = (
    GRAVE_QUOTE
    >> alt_class(
        (
            "ChainPredicateIterator",
            "ChainSilhouetteIterator",
        ),
        "freestyle.chainingiterators.",
    )
    << GRAVE_QUOTE
)

GPU_TYPES = (
    GRAVE_QUOTE
    >> alt_class(
        (
            "Buffer",
            "GPUBatch",
            "GPUShader",
            "GPUStageInterfaceInfo",
            "GPUTexture",
            "GPUUniformBuf",
            "GPUVertBuf",
            "GPUVertFormat",
        ),
        "gpu.types.",
        False,
    )
    << GRAVE_QUOTE
)

BMESH_TYPES_ELEMENTS = alt(
    *(
        GRAVE_QUOTE >> string(f"bmesh.types.{t}") << GRAVE_QUOTE
        | GRAVE_QUOTE >> string(t) << GRAVE_QUOTE
        | SINGLE_QUOTE >> string(t) << SINGLE_QUOTE
        for t in (
            "BMEdge",
            "BMFace",
            "BMLoop",
            "BMVert",
        )
    )
)

AUD = GRAVE_QUOTE >> strings("SequenceEntry", "Handle", "HRTF", "ImpulseResponse", "Source") << GRAVE_QUOTE

BMESH_TYPES = (
    GRAVE_QUOTE
    >> alt_class(
        (
            "BMesh",
            "BMLayerAccessEdge",
            "BMLayerAccessFace",
            "BMLayerAccessLoop",
            "BMLayerAccessVert",
            "BMLayerItem",
        ),
        "bmesh.types.",
    )
    << GRAVE_QUOTE
)

COLLECTION_BPY_TYPES = (
    GRAVE_QUOTE
    >> alt_class(
        (
            "BMLayerCollection",
            "BoneCollection",
            "Collection",
        ),
        "bpy.types.",
    )
    << GRAVE_QUOTE
)

BPY_TYPES = (
    GRAVE_QUOTE
    >> alt_class(
        {
            "Action",
            "ActionConstraint",
            "ActionFCurves",
            "ActionGroup",
            "ActionGroups",
            "ActionPoseMarkers",
            "Addon",
            "AddonPreferences",
            "Addons",
            "AddSequence",
            "AdjustmentSequence",
            "AlphaOverSequence",
            "AlphaUnderSequence",
            "AnimData",
            "AnimDataDrivers",
            "AnimViz",
            "AnimVizMotionPaths",
            "AnyType",
            "AOV",
            "AOVs",
            "Area",
            "AreaLight",
            "AreaSpaces",
            "Armature",
            "ArmatureBones",
            "ArmatureConstraint",
            "ArmatureConstraintTargets",
            "ArmatureEditBones",
            "ArmatureGpencilModifier",
            "ArmatureModifier",
            "ArrayGpencilModifier",
            "ArrayModifier",
            "ASSETBROWSER_UL_metadata_tags",
            "AssetCatalogPath",
            "AssetHandle",
            "AssetLibraryReference",
            "AssetMetaData",
            "AssetRepresentation",
            "AssetShelf",
            "AssetTag",
            "AssetTags",
            "Attribute",
            "AttributeGroup",
            "BakeSettings",
            "BevelModifier",
            "BezierSplinePoint",
            "BlendData",
            "BlendDataActions",
            "BlendDataArmatures",
            "BlendDataBrushes",
            "BlendDataCacheFiles",
            "BlendDataCameras",
            "BlendDataCollections",
            "BlendDataCurves",
            "BlendDataFonts",
            "BlendDataGreasePencils",
            "BlendDataHairCurves",
            "BlendDataImages",
            "BlendDataLattices",
            "BlendDataLibraries",
            "BlendDataLights",
            "BlendDataLineStyles",
            "BlendDataMasks",
            "BlendDataMaterials",
            "BlendDataMeshes",
            "BlendDataMetaBalls",
            "BlendDataMovieClips",
            "BlendDataNodeTrees",
            "BlendDataObjects",
            "BlendDataPaintCurves",
            "BlendDataPalettes",
            "BlendDataParticles",
            "BlendDataPointClouds",
            "BlendDataProbes",
            "BlendDataScenes",
            "BlendDataScreens",
            "BlendDataSounds",
            "BlendDataSpeakers",
            "BlendDataTexts",
            "BlendDataTextures",
            "BlendDataVolumes",
            "BlendDataWindowManagers",
            "BlendDataWorkSpaces",
            "BlendDataWorlds",
            "BlenderRNA",
            "BlendTexture",
            "BoidRule",
            "BoidRuleAverageSpeed",
            "BoidRuleAvoid",
            "BoidRuleAvoidCollision",
            "BoidRuleFight",
            "BoidRuleFollowLeader",
            "BoidRuleGoal",
            "BoidSettings",
            "BoidState",
            "Bone",
            "BoneCollection",
            "BoneCollectionMemberships",
            "BoneCollections",
            "BoneColor",
            "BoolAttribute",
            "BoolAttributeValue",
            "BooleanModifier",
            "BoolProperty",
            "bpy_prop_collection",
            "bpy_struct",
            "bpy.types",
            "BrightContrastModifier",
            "Brush",
            "BrushCapabilities",
            "BrushCapabilitiesImagePaint",
            "BrushCapabilitiesSculpt",
            "BrushCapabilitiesVertexPaint",
            "BrushCapabilitiesWeightPaint",
            "BrushCurvesSculptSettings",
            "BrushGpencilSettings",
            "BrushTextureSlot",
            "BuildGpencilModifier",
            "BuildModifier",
            "ByteColorAttribute",
            "ByteColorAttributeValue",
            "ByteIntAttribute",
            "ByteIntAttributeValue",
            "CacheFile",
            "CacheFileLayer",
            "CacheFileLayers",
            "CacheObjectPath",
            "CacheObjectPaths",
            "Camera",
            "CameraBackgroundImage",
            "CameraBackgroundImages",
            "CameraDOFSettings",
            "CameraSolverConstraint",
            "CameraStereoData",
            "CastModifier",
            "ChannelDriverVariables",
            "ChildOfConstraint",
            "ChildParticle",
            "ClampToConstraint",
            "CLIP_UL_tracking_objects",
            "ClothCollisionSettings",
            "ClothModifier",
            "ClothSettings",
            "ClothSolverResult",
            "CloudsTexture",
            "Collection",
            "CollectionChild",
            "CollectionChildren",
            "CollectionLightLinking",
            "CollectionObject",
            "CollectionObjects",
            "CollectionProperty",
            "CollisionModifier",
            "CollisionSettings",
            "ColorBalanceModifier",
            "ColorGpencilModifier",
            "ColorManagedDisplaySettings",
            "ColorManagedInputColorspaceSettings",
            "ColorManagedSequencerColorspaceSettings",
            "ColorManagedViewSettings",
            "ColorMapping",
            "ColorMixSequence",
            "ColorRamp",
            "ColorRampElement",
            "ColorRampElements",
            "ColorSequence",
            "CompositorNode",
            "CompositorNodeAlphaOver",
            "CompositorNodeAntiAliasing",
            "CompositorNodeBilateralblur",
            "CompositorNodeBlur",
            "CompositorNodeBokehBlur",
            "CompositorNodeBokehImage",
            "CompositorNodeBoxMask",
            "CompositorNodeBrightContrast",
            "CompositorNodeChannelMatte",
            "CompositorNodeChromaMatte",
            "CompositorNodeColorBalance",
            "CompositorNodeColorCorrection",
            "CompositorNodeColorMatte",
            "CompositorNodeColorSpill",
            "CompositorNodeCombHSVA",
            "CompositorNodeCombineColor",
            "CompositorNodeCombineXYZ",
            "CompositorNodeCombRGBA",
            "CompositorNodeCombYCCA",
            "CompositorNodeCombYUVA",
            "CompositorNodeComposite",
            "CompositorNodeConvertColorSpace",
            "CompositorNodeCornerPin",
            "CompositorNodeCrop",
            "CompositorNodeCryptomatte",
            "CompositorNodeCryptomatteV2",
            "CompositorNodeCurveRGB",
            "CompositorNodeCurveVec",
            "CompositorNodeCustomGroup",
            "CompositorNodeDBlur",
            "CompositorNodeDefocus",
            "CompositorNodeDenoise",
            "CompositorNodeDespeckle",
            "CompositorNodeDiffMatte",
            "CompositorNodeDilateErode",
            "CompositorNodeDisplace",
            "CompositorNodeDistanceMatte",
            "CompositorNodeDoubleEdgeMask",
            "CompositorNodeEllipseMask",
            "CompositorNodeExposure",
            "CompositorNodeFilter",
            "CompositorNodeFlip",
            "CompositorNodeGamma",
            "CompositorNodeGlare",
            "CompositorNodeGroup",
            "CompositorNodeHueCorrect",
            "CompositorNodeHueSat",
            "CompositorNodeIDMask",
            "CompositorNodeImage",
            "CompositorNodeInpaint",
            "CompositorNodeInvert",
            "CompositorNodeKeying",
            "CompositorNodeKeyingScreen",
            "CompositorNodeKuwahara",
            "CompositorNodeLensdist",
            "CompositorNodeLevels",
            "CompositorNodeLumaMatte",
            "CompositorNodeMapRange",
            "CompositorNodeMapUV",
            "CompositorNodeMapValue",
            "CompositorNodeMask",
            "CompositorNodeMath",
            "CompositorNodeMixRGB",
            "CompositorNodeMovieClip",
            "CompositorNodeMovieDistortion",
            "CompositorNodeNormal",
            "CompositorNodeNormalize",
            "CompositorNodeOutputFile",
            "CompositorNodeOutputFileFileSlots",
            "CompositorNodeOutputFileLayerSlots",
            "CompositorNodePixelate",
            "CompositorNodePlaneTrackDeform",
            "CompositorNodePosterize",
            "CompositorNodePremulKey",
            "CompositorNodeRGB",
            "CompositorNodeRGBToBW",
            "CompositorNodeRLayers",
            "CompositorNodeRotate",
            "CompositorNodeScale",
            "CompositorNodeSceneTime",
            "CompositorNodeSeparateColor",
            "CompositorNodeSeparateXYZ",
            "CompositorNodeSepHSVA",
            "CompositorNodeSepRGBA",
            "CompositorNodeSepYCCA",
            "CompositorNodeSepYUVA",
            "CompositorNodeSetAlpha",
            "CompositorNodeSplitViewer",
            "CompositorNodeStabilize",
            "CompositorNodeSunBeams",
            "CompositorNodeSwitch",
            "CompositorNodeSwitchView",
            "CompositorNodeTexture",
            "CompositorNodeTime",
            "CompositorNodeTonemap",
            "CompositorNodeTrackPos",
            "CompositorNodeTransform",
            "CompositorNodeTranslate",
            "CompositorNodeTree",
            "CompositorNodeValToRGB",
            "CompositorNodeValue",
            "CompositorNodeVecBlur",
            "CompositorNodeViewer",
            "CompositorNodeZcombine",
            "ConsoleLine",
            "Constraint",
            "ConstraintTarget",
            "ConstraintTargetBone",
            "Context",
            "CopyLocationConstraint",
            "CopyRotationConstraint",
            "CopyScaleConstraint",
            "CopyTransformsConstraint",
            "CorrectiveSmoothModifier",
            "CrossSequence",
            "CryptomatteEntry",
            "Curve",
            "CurveMap",
            "CurveMapping",
            "CurveMapPoint",
            "CurveMapPoints",
            "CurveModifier",
            "CurvePaintSettings",
            "CurvePoint",
            "CurveProfile",
            "CurveProfilePoint",
            "CurveProfilePoints",
            "CURVES_UL_attributes",
            "Curves",
            "CurveSlice",
            "CurvesModifier",
            "CurveSplines",
            "CurvesSculpt",
            "DampedTrackConstraint",
            "DashGpencilModifierData",
            "DashGpencilModifierSegment",
            "DATA_UL_bone_collections",
            "DataTransferModifier",
            "DecimateModifier",
            "Depsgraph",
            "DepsgraphObjectInstance",
            "DepsgraphUpdate",
            "DisplaceModifier",
            "DisplaySafeAreas",
            "DistortedNoiseTexture",
            "DopeSheet",
            "Driver",
            "DriverTarget",
            "DriverVariable",
            "DynamicPaintBrushSettings",
            "DynamicPaintCanvasSettings",
            "DynamicPaintModifier",
            "DynamicPaintSurface",
            "DynamicPaintSurfaces",
            "EdgeSplitModifier",
            "EditBone",
            "EffectorWeights",
            "EffectSequence",
            "EnumProperty",
            "EnumPropertyItem",
            "EnvelopeGpencilModifier",
            "EQCurveMappingData",
            "Event",
            "ExplodeModifier",
            "FCurve",
            "FCurveKeyframePoints",
            "FCurveModifiers",
            "FCurveSample",
            "FFmpegSettings",
            "FieldSettings",
            "FileAssetSelectIDFilter",
            "FileAssetSelectParams",
            "FILEBROWSER_UL_dir",
            "FileBrowserFSMenuEntry",
            "FileSelectEntry",
            "FileSelectIDFilter",
            "FileSelectParams",
            "Float2Attribute",
            "Float2AttributeValue",
            "FloatAttribute",
            "FloatAttributeValue",
            "FloatColorAttribute",
            "FloatColorAttributeValue",
            "FloatProperty",
            "FloatVectorAttribute",
            "FloatVectorAttributeValue",
            "FloatVectorValueReadOnly",
            "FloorConstraint",
            "FluidDomainSettings",
            "FluidEffectorSettings",
            "FluidFlowSettings",
            "FluidModifier",
            "FModifier",
            "FModifierCycles",
            "FModifierEnvelope",
            "FModifierEnvelopeControlPoint",
            "FModifierEnvelopeControlPoints",
            "FModifierFunctionGenerator",
            "FModifierGenerator",
            "FModifierLimits",
            "FModifierNoise",
            "FModifierPython",
            "FModifierStepped",
            "FollowPathConstraint",
            "FollowTrackConstraint",
            "FreestyleLineSet",
            "FreestyleLineStyle",
            "FreestyleModules",
            "FreestyleModuleSettings",
            "FreestyleSettings",
            "Function",
            "FunctionNode",
            "FunctionNodeAlignEulerToVector",
            "FunctionNodeAxisAngleToRotation",
            "FunctionNodeBooleanMath",
            "FunctionNodeCombineColor",
            "FunctionNodeCompare",
            "FunctionNodeEulerToRotation",
            "FunctionNodeFloatToInt",
            "FunctionNodeInputBool",
            "FunctionNodeInputColor",
            "FunctionNodeInputInt",
            "FunctionNodeInputSpecialCharacters",
            "FunctionNodeInputString",
            "FunctionNodeInputVector",
            "FunctionNodeInvertRotation",
            "FunctionNodeQuaternionToRotation",
            "FunctionNodeRandomValue",
            "FunctionNodeReplaceString",
            "FunctionNodeRotateEuler",
            "FunctionNodeRotateVector",
            "FunctionNodeRotationToAxisAngle",
            "FunctionNodeRotationToEuler",
            "FunctionNodeRotationToQuaternion",
            "FunctionNodeSeparateColor",
            "FunctionNodeSliceString",
            "FunctionNodeStringLength",
            "FunctionNodeValueToString",
            "GammaCrossSequence",
            "GaussianBlurSequence",
            "GeometryNode",
            "GeometryNodeAccumulateField",
            "GeometryNodeAttributeDomainSize",
            "GeometryNodeAttributeStatistic",
            "GeometryNodeBlurAttribute",
            "GeometryNodeBoundBox",
            "GeometryNodeCaptureAttribute",
            "GeometryNodeCollectionInfo",
            "GeometryNodeConvexHull",
            "GeometryNodeCornersOfEdge",
            "GeometryNodeCornersOfFace",
            "GeometryNodeCornersOfVertex",
            "GeometryNodeCurveArc",
            "GeometryNodeCurveEndpointSelection",
            "GeometryNodeCurveHandleTypeSelection",
            "GeometryNodeCurveLength",
            "GeometryNodeCurveOfPoint",
            "GeometryNodeCurvePrimitiveBezierSegment",
            "GeometryNodeCurvePrimitiveCircle",
            "GeometryNodeCurvePrimitiveLine",
            "GeometryNodeCurvePrimitiveQuadrilateral",
            "GeometryNodeCurveQuadraticBezier",
            "GeometryNodeCurveSetHandles",
            "GeometryNodeCurveSpiral",
            "GeometryNodeCurveSplineType",
            "GeometryNodeCurveStar",
            "GeometryNodeCurveToMesh",
            "GeometryNodeCurveToPoints",
            "GeometryNodeCustomGroup",
            "GeometryNodeDeformCurvesOnSurface",
            "GeometryNodeDeleteGeometry",
            "GeometryNodeDistributePointsInVolume",
            "GeometryNodeDistributePointsOnFaces",
            "GeometryNodeDualMesh",
            "GeometryNodeDuplicateElements",
            "GeometryNodeEdgePathsToCurves",
            "GeometryNodeEdgePathsToSelection",
            "GeometryNodeEdgesOfCorner",
            "GeometryNodeEdgesOfVertex",
            "GeometryNodeEdgesToFaceGroups",
            "GeometryNodeExtrudeMesh",
            "GeometryNodeFaceOfCorner",
            "GeometryNodeFieldAtIndex",
            "GeometryNodeFieldOnDomain",
            "GeometryNodeFillCurve",
            "GeometryNodeFilletCurve",
            "GeometryNodeFlipFaces",
            "GeometryNodeGeometryToInstance",
            "GeometryNodeGroup",
            "GeometryNodeImageInfo",
            "GeometryNodeImageTexture",
            "GeometryNodeIndexOfNearest",
            "GeometryNodeInputCurveHandlePositions",
            "GeometryNodeInputCurveTilt",
            "GeometryNodeInputEdgeSmooth",
            "GeometryNodeInputID",
            "GeometryNodeInputImage",
            "GeometryNodeInputIndex",
            "GeometryNodeInputInstanceRotation",
            "GeometryNodeInputInstanceScale",
            "GeometryNodeInputMaterial",
            "GeometryNodeInputMaterialIndex",
            "GeometryNodeInputMeshEdgeAngle",
            "GeometryNodeInputMeshEdgeNeighbors",
            "GeometryNodeInputMeshEdgeVertices",
            "GeometryNodeInputMeshFaceArea",
            "GeometryNodeInputMeshFaceIsPlanar",
            "GeometryNodeInputMeshFaceNeighbors",
            "GeometryNodeInputMeshIsland",
            "GeometryNodeInputMeshVertexNeighbors",
            "GeometryNodeInputNamedAttribute",
            "GeometryNodeInputNormal",
            "GeometryNodeInputPosition",
            "GeometryNodeInputRadius",
            "GeometryNodeInputSceneTime",
            "GeometryNodeInputShadeSmooth",
            "GeometryNodeInputShortestEdgePaths",
            "GeometryNodeInputSignedDistance",
            "GeometryNodeInputSplineCyclic",
            "GeometryNodeInputSplineResolution",
            "GeometryNodeInputTangent",
            "GeometryNodeInstanceOnPoints",
            "GeometryNodeInstancesToPoints",
            "GeometryNodeInterpolateCurves",
            "GeometryNodeIsViewport",
            "GeometryNodeJoinGeometry",
            "GeometryNodeMaterialSelection",
            "GeometryNodeMeanFilterSDFVolume",
            "GeometryNodeMergeByDistance",
            "GeometryNodeMeshBoolean",
            "GeometryNodeMeshCircle",
            "GeometryNodeMeshCone",
            "GeometryNodeMeshCube",
            "GeometryNodeMeshCylinder",
            "GeometryNodeMeshFaceSetBoundaries",
            "GeometryNodeMeshGrid",
            "GeometryNodeMeshIcoSphere",
            "GeometryNodeMeshLine",
            "GeometryNodeMeshToCurve",
            "GeometryNodeMeshToPoints",
            "GeometryNodeMeshToSDFVolume",
            "GeometryNodeMeshToVolume",
            "GeometryNodeMeshUVSphere",
            "GeometryNodeObjectInfo",
            "GeometryNodeOffsetCornerInFace",
            "GeometryNodeOffsetPointInCurve",
            "GeometryNodeOffsetSDFVolume",
            "GeometryNodePoints",
            "GeometryNodePointsOfCurve",
            "GeometryNodePointsToCurves",
            "GeometryNodePointsToSDFVolume",
            "GeometryNodePointsToVertices",
            "GeometryNodePointsToVolume",
            "GeometryNodeProximity",
            "GeometryNodeRaycast",
            "GeometryNodeRealizeInstances",
            "GeometryNodeRemoveAttribute",
            "GeometryNodeRepeatInput",
            "GeometryNodeRepeatOutput",
            "GeometryNodeReplaceMaterial",
            "GeometryNodeResampleCurve",
            "GeometryNodeReverseCurve",
            "GeometryNodeRotateInstances",
            "GeometryNodeSampleCurve",
            "GeometryNodeSampleIndex",
            "GeometryNodeSampleNearest",
            "GeometryNodeSampleNearestSurface",
            "GeometryNodeSampleUVSurface",
            "GeometryNodeSampleVolume",
            "GeometryNodeScaleElements",
            "GeometryNodeScaleInstances",
            "GeometryNodeSDFVolumeSphere",
            "GeometryNodeSelfObject",
            "GeometryNodeSeparateComponents",
            "GeometryNodeSeparateGeometry",
            "GeometryNodeSetCurveHandlePositions",
            "GeometryNodeSetCurveNormal",
            "GeometryNodeSetCurveRadius",
            "GeometryNodeSetCurveTilt",
            "GeometryNodeSetID",
            "GeometryNodeSetMaterial",
            "GeometryNodeSetMaterialIndex",
            "GeometryNodeSetPointRadius",
            "GeometryNodeSetPosition",
            "GeometryNodeSetShadeSmooth",
            "GeometryNodeSetSplineCyclic",
            "GeometryNodeSetSplineResolution",
            "GeometryNodeSimulationInput",
            "GeometryNodeSimulationOutput",
            "GeometryNodeSplineLength",
            "GeometryNodeSplineParameter",
            "GeometryNodeSplitEdges",
            "GeometryNodeStoreNamedAttribute",
            "GeometryNodeStringJoin",
            "GeometryNodeStringToCurves",
            "GeometryNodeSubdivideCurve",
            "GeometryNodeSubdivideMesh",
            "GeometryNodeSubdivisionSurface",
            "GeometryNodeSwitch",
            "GeometryNodeTool3DCursor",
            "GeometryNodeToolFaceSet",
            "GeometryNodeToolSelection",
            "GeometryNodeToolSetFaceSet",
            "GeometryNodeToolSetSelection",
            "GeometryNodeTransform",
            "GeometryNodeTranslateInstances",
            "GeometryNodeTree",
            "GeometryNodeTriangulate",
            "GeometryNodeTrimCurve",
            "GeometryNodeUVPackIslands",
            "GeometryNodeUVUnwrap",
            "GeometryNodeVertexOfCorner",
            "GeometryNodeViewer",
            "GeometryNodeVolumeCube",
            "GeometryNodeVolumeToMesh",
            "Gizmo",
            "GizmoGroup",
            "GizmoGroupProperties",
            "GizmoProperties",
            "Gizmos",
            "GlowSequence",
            "GPENCIL_UL_annotation_layer",
            "GPENCIL_UL_layer",
            "GPENCIL_UL_masks",
            "GPENCIL_UL_matslots",
            "GPENCIL_UL_vgroups",
            "GPencilEditCurve",
            "GPencilEditCurvePoint",
            "GPencilFrame",
            "GPencilFrames",
            "GPencilInterpolateSettings",
            "GPencilLayer",
            "GPencilLayerMask",
            "GpencilModifier",
            "GPencilSculptGuide",
            "GPencilSculptSettings",
            "GPencilStroke",
            "GPencilStrokePoint",
            "GPencilStrokePoints",
            "GPencilStrokes",
            "GPencilTriangle",
            "GpencilVertexGroupElement",
            "GpPaint",
            "GpSculptPaint",
            "GpVertexPaint",
            "GpWeightPaint",
            "GreasePencil",
            "GreasePencilGrid",
            "GreasePencilLayers",
            "GreasePencilMaskLayers",
            "GroupNodeViewerPathElem",
            "Header",
            "Histogram",
            "HookGpencilModifier",
            "HookModifier",
            "HueCorrectModifier",
            "HydraRenderEngine",
            "ID",
            "IDMaterials",
            "IDOverrideLibrary",
            "IDOverrideLibraryProperties",
            "IDOverrideLibraryProperty",
            "IDOverrideLibraryPropertyOperation",
            "IDOverrideLibraryPropertyOperations",
            "IDPropertyWrapPtr",
            "IDViewerPathElem",
            "IKParam",
            "IMAGE_UL_render_slots",
            "IMAGE_UL_udim_tiles",
            "Image",
            "ImageFormatSettings",
            "ImagePackedFile",
            "ImagePaint",
            "ImagePreview",
            "ImageSequence",
            "ImageTexture",
            "ImageUser",
            "Int2Attribute",
            "Int2AttributeValue",
            "IntAttribute",
            "IntAttributeValue",
            "IntProperty",
            "Itasc",
            "Key",
            "KeyConfig",
            "KeyConfigPreferences",
            "KeyConfigurations",
            "Keyframe",
            "KeyingSet",
            "KeyingSetInfo",
            "KeyingSetPath",
            "KeyingSetPaths",
            "KeyingSets",
            "KeyingSetsAll",
            "KeyMap",
            "KeyMapItem",
            "KeyMapItems",
            "KeyMaps",
            "KinematicConstraint",
            "LaplacianDeformModifier",
            "LaplacianSmoothModifier",
            "Lattice",
            "LatticeGpencilModifier",
            "LatticeModifier",
            "LatticePoint",
            "LayerCollection",
            "LayerObjects",
            "LengthGpencilModifier",
            "Library",
            "LibraryWeakReference",
            "Light",
            "Lightgroup",
            "Lightgroups",
            "LightProbe",
            "LimitDistanceConstraint",
            "LimitLocationConstraint",
            "LimitRotationConstraint",
            "LimitScaleConstraint",
            "LineartGpencilModifier",
            "Linesets",
            "LineStyleAlphaModifier_AlongStroke",
            "LineStyleAlphaModifier_CreaseAngle",
            "LineStyleAlphaModifier_Curvature_3D",
            "LineStyleAlphaModifier_DistanceFromCamera",
            "LineStyleAlphaModifier_DistanceFromObject",
            "LineStyleAlphaModifier_Material",
            "LineStyleAlphaModifier_Noise",
            "LineStyleAlphaModifier_Tangent",
            "LineStyleAlphaModifier",
            "LineStyleAlphaModifiers",
            "LineStyleColorModifier_AlongStroke",
            "LineStyleColorModifier_CreaseAngle",
            "LineStyleColorModifier_Curvature_3D",
            "LineStyleColorModifier_DistanceFromCamera",
            "LineStyleColorModifier_DistanceFromObject",
            "LineStyleColorModifier_Material",
            "LineStyleColorModifier_Noise",
            "LineStyleColorModifier_Tangent",
            "LineStyleColorModifier",
            "LineStyleColorModifiers",
            "LineStyleGeometryModifier_2DOffset",
            "LineStyleGeometryModifier_2DTransform",
            "LineStyleGeometryModifier_BackboneStretcher",
            "LineStyleGeometryModifier_BezierCurve",
            "LineStyleGeometryModifier_Blueprint",
            "LineStyleGeometryModifier_GuidingLines",
            "LineStyleGeometryModifier_PerlinNoise1D",
            "LineStyleGeometryModifier_PerlinNoise2D",
            "LineStyleGeometryModifier_Polygonalization",
            "LineStyleGeometryModifier_Sampling",
            "LineStyleGeometryModifier_Simplification",
            "LineStyleGeometryModifier_SinusDisplacement",
            "LineStyleGeometryModifier_SpatialNoise",
            "LineStyleGeometryModifier_TipRemover",
            "LineStyleGeometryModifier",
            "LineStyleGeometryModifiers",
            "LineStyleModifier",
            "LineStyleTextureSlot",
            "LineStyleTextureSlots",
            "LineStyleThicknessModifier_AlongStroke",
            "LineStyleThicknessModifier_Calligraphy",
            "LineStyleThicknessModifier_CreaseAngle",
            "LineStyleThicknessModifier_Curvature_3D",
            "LineStyleThicknessModifier_DistanceFromCamera",
            "LineStyleThicknessModifier_DistanceFromObject",
            "LineStyleThicknessModifier_Material",
            "LineStyleThicknessModifier_Noise",
            "LineStyleThicknessModifier_Tangent",
            "LineStyleThicknessModifier",
            "LineStyleThicknessModifiers",
            "LockedTrackConstraint",
            "LoopColors",
            "Macro",
            "MagicTexture",
            "MaintainVolumeConstraint",
            "MarbleTexture",
            "MASK_UL_layers",
            "Mask",
            "MaskLayer",
            "MaskLayers",
            "MaskModifier",
            "MaskParent",
            "MaskSequence",
            "MaskSpline",
            "MaskSplinePoint",
            "MaskSplinePoints",
            "MaskSplinePointUW",
            "MaskSplines",
            "MATERIAL_UL_matslots",
            "Material",
            "MaterialGPencilStyle",
            "MaterialLineArt",
            "MaterialSlot",
            "Menu",
            "MESH_UL_attributes",
            "MESH_UL_color_attributes_selector",
            "MESH_UL_color_attributes",
            "MESH_UL_shape_keys",
            "MESH_UL_uvmaps",
            "MESH_UL_vgroups",
            "Mesh",
            "MeshCacheModifier",
            "MeshDeformModifier",
            "MeshEdge",
            "MeshEdges",
            "MeshLoop",
            "MeshLoopColor",
            "MeshLoopColorLayer",
            "MeshLoops",
            "MeshLoopTriangle",
            "MeshLoopTriangles",
            "MeshNormalValue",
            "MeshPaintMaskLayer",
            "MeshPaintMaskProperty",
            "MeshPolygon",
            "MeshPolygons",
            "MeshSequenceCacheModifier",
            "MeshSkinVertex",
            "MeshSkinVertexLayer",
            "MeshStatVis",
            "MeshToVolumeModifier",
            "MeshUVLoop",
            "MeshUVLoopLayer",
            "MeshVertex",
            "MeshVertices",
            "MetaBall",
            "MetaBallElements",
            "MetaElement",
            "MetaSequence",
            "MirrorGpencilModifier",
            "MirrorModifier",
            "Modifier",
            "ModifierViewerPathElem",
            "MotionPath",
            "MotionPathVert",
            "MovieClip",
            "MovieClipProxy",
            "MovieClipScopes",
            "MovieClipSequence",
            "MovieClipUser",
            "MovieReconstructedCamera",
            "MovieSequence",
            "MovieTracking",
            "MovieTrackingCamera",
            "MovieTrackingDopesheet",
            "MovieTrackingMarker",
            "MovieTrackingMarkers",
            "MovieTrackingObject",
            "MovieTrackingObjectPlaneTracks",
            "MovieTrackingObjects",
            "MovieTrackingObjectTracks",
            "MovieTrackingPlaneMarker",
            "MovieTrackingPlaneMarkers",
            "MovieTrackingPlaneTrack",
            "MovieTrackingPlaneTracks",
            "MovieTrackingReconstructedCameras",
            "MovieTrackingReconstruction",
            "MovieTrackingSettings",
            "MovieTrackingStabilization",
            "MovieTrackingTrack",
            "MovieTrackingTracks",
            "MulticamSequence",
            "MultiplyGpencilModifier",
            "MultiplySequence",
            "MultiresModifier",
            "MusgraveTexture",
            "NlaStrip",
            "NlaStripFCurves",
            "NlaStrips",
            "NlaTrack",
            "NlaTracks",
            "NODE_UL_repeat_zone_items",
            "NODE_UL_simulation_zone_items",
            "Node",
            "NodeCustomGroup",
            "NodeFrame",
            "NodeGeometryRepeatOutputItems",
            "NodeGeometrySimulationOutputItems",
            "NodeGroup",
            "NodeGroupInput",
            "NodeGroupOutput",
            "NodeInputs",
            "NodeInstanceHash",
            "NodeInternal",
            "NodeInternalSocketTemplate",
            "NodeLink",
            "NodeLinks",
            "NodeOutputFileSlotFile",
            "NodeOutputFileSlotLayer",
            "NodeOutputs",
            "NodeReroute",
            "Nodes",
            "NodesModifier",
            "NodesModifierBake",
            "NodesModifierBakes",
            "NodeSocket",
            "NodeSocketBool",
            "NodeSocketCollection",
            "NodeSocketColor",
            "NodeSocketFloat",
            "NodeSocketFloatAngle",
            "NodeSocketFloatDistance",
            "NodeSocketFloatFactor",
            "NodeSocketFloatPercentage",
            "NodeSocketFloatTime",
            "NodeSocketFloatTimeAbsolute",
            "NodeSocketFloatUnsigned",
            "NodeSocketGeometry",
            "NodeSocketImage",
            "NodeSocketInt",
            "NodeSocketIntFactor",
            "NodeSocketIntPercentage",
            "NodeSocketIntUnsigned",
            "NodeSocketMaterial",
            "NodeSocketObject",
            "NodeSocketRotation",
            "NodeSocketShader",
            "NodeSocketStandard",
            "NodeSocketString",
            "NodeSocketTexture",
            "NodeSocketVector",
            "NodeSocketVectorAcceleration",
            "NodeSocketVectorDirection",
            "NodeSocketVectorEuler",
            "NodeSocketVectorTranslation",
            "NodeSocketVectorVelocity",
            "NodeSocketVectorXYZ",
            "NodeSocketVirtual",
            "NodeTree",
            "NodeTreeInterface",
            "NodeTreeInterfaceItem",
            "NodeTreeInterfacePanel",
            "NodeTreeInterfaceSocket",
            "NodeTreeInterfaceSocketBool",
            "NodeTreeInterfaceSocketCollection",
            "NodeTreeInterfaceSocketColor",
            "NodeTreeInterfaceSocketFloat",
            "NodeTreeInterfaceSocketFloatAngle",
            "NodeTreeInterfaceSocketFloatDistance",
            "NodeTreeInterfaceSocketFloatFactor",
            "NodeTreeInterfaceSocketFloatPercentage",
            "NodeTreeInterfaceSocketFloatTime",
            "NodeTreeInterfaceSocketFloatTimeAbsolute",
            "NodeTreeInterfaceSocketFloatUnsigned",
            "NodeTreeInterfaceSocketGeometry",
            "NodeTreeInterfaceSocketImage",
            "NodeTreeInterfaceSocketInt",
            "NodeTreeInterfaceSocketIntFactor",
            "NodeTreeInterfaceSocketIntPercentage",
            "NodeTreeInterfaceSocketIntUnsigned",
            "NodeTreeInterfaceSocketMaterial",
            "NodeTreeInterfaceSocketObject",
            "NodeTreeInterfaceSocketRotation",
            "NodeTreeInterfaceSocketShader",
            "NodeTreeInterfaceSocketString",
            "NodeTreeInterfaceSocketTexture",
            "NodeTreeInterfaceSocketVector",
            "NodeTreeInterfaceSocketVectorAcceleration",
            "NodeTreeInterfaceSocketVectorDirection",
            "NodeTreeInterfaceSocketVectorEuler",
            "NodeTreeInterfaceSocketVectorTranslation",
            "NodeTreeInterfaceSocketVectorVelocity",
            "NodeTreeInterfaceSocketVectorXYZ",
            "NodeTreePath",
            "NoiseGpencilModifier",
            "NoiseTexture",
            "NormalEditModifier",
            "Object",
            "ObjectBase",
            "ObjectConstraints",
            "ObjectDisplay",
            "ObjectGpencilModifiers",
            "ObjectLightLinking",
            "ObjectLineArt",
            "ObjectModifiers",
            "ObjectShaderFx",
            "ObjectSolverConstraint",
            "OceanModifier",
            "OffsetGpencilModifier",
            "OpacityGpencilModifier",
            "Operator",
            "OperatorFileListElement",
            "OperatorMacro",
            "OperatorMousePath",
            "OperatorOptions",
            "OperatorProperties",
            "OperatorStrokeElement",
            "OutlineGpencilModifier",
            "OverDropSequence",
            "PackedFile",
            "Paint",
            "PaintCurve",
            "PaintModeSettings",
            "PaintToolSlot",
            "Palette",
            "PaletteColor",
            "PaletteColors",
            "Panel",
            "PARTICLE_UL_particle_systems",
            "Particle",
            "ParticleBrush",
            "ParticleDupliWeight",
            "ParticleEdit",
            "ParticleHairKey",
            "ParticleInstanceModifier",
            "ParticleKey",
            "ParticleSettings",
            "ParticleSettingsTextureSlot",
            "ParticleSettingsTextureSlots",
            "ParticleSystem",
            "ParticleSystemModifier",
            "ParticleSystems",
            "ParticleTarget",
            "PathCompare",
            "PathCompareCollection",
            "PHYSICS_UL_dynapaint_surfaces",
            "PivotConstraint",
            "Point",
            "PointCache",
            "PointCacheItem",
            "PointCaches",
            "POINTCLOUD_UL_attributes",
            "PointCloud",
            "PointerProperty",
            "PointLight",
            "Pose",
            "PoseBone",
            "PoseBoneConstraints",
            "Preferences",
            "PreferencesApps",
            "PreferencesEdit",
            "PreferencesExperimental",
            "PreferencesFilePaths",
            "PreferencesInput",
            "PreferencesKeymap",
            "PreferencesSystem",
            "PreferencesView",
            "PrimitiveBoolean",
            "PrimitiveFloat",
            "PrimitiveInt",
            "PrimitiveString",
            "Property",
            "PropertyGroup",
            "PropertyGroupItem",
            "PythonConstraint",
            "QuaternionAttribute",
            "QuaternionAttributeValue",
            "RaytraceEEVEE",
            "ReadOnlyInteger",
            "Region",
            "RegionView3D",
            "RemeshModifier",
            "RENDER_UL_renderviews",
            "RenderEngine",
            "RenderLayer",
            "RenderPass",
            "RenderPasses",
            "RenderResult",
            "RenderSettings",
            "RenderSlot",
            "RenderSlots",
            "RenderView",
            "RenderViews",
            "RepeatItem",
            "RepeatZoneViewerPathElem",
            "RetimingKey",
            "RetimingKeys",
            "RigidBodyConstraint",
            "RigidBodyObject",
            "RigidBodyWorld",
            "SCENE_UL_keying_set_paths",
            "Scene",
            "SceneDisplay",
            "SceneEEVEE",
            "SceneGpencil",
            "SceneHydra",
            "SceneObjects",
            "SceneRenderView",
            "SceneSequence",
            "Scopes",
            "Screen",
            "ScrewModifier",
            "ScriptDirectory",
            "ScriptDirectoryCollection",
            "Sculpt",
            "SelectedUvElement",
            "Sequence",
            "SequenceColorBalance",
            "SequenceColorBalanceData",
            "SequenceCrop",
            "SequenceEditor",
            "SequenceElement",
            "SequenceElements",
            "SequenceModifier",
            "SequenceModifiers",
            "SequenceProxy",
            "SequencerPreviewOverlay",
            "SequencerTimelineOverlay",
            "SequencerTonemapModifierData",
            "SequencerToolSettings",
            "SequencesMeta",
            "SequencesTopLevel",
            "SequenceTimelineChannel",
            "SequenceTransform",
            "ShaderFx",
            "ShaderFxBlur",
            "ShaderFxColorize",
            "ShaderFxFlip",
            "ShaderFxGlow",
            "ShaderFxPixel",
            "ShaderFxRim",
            "ShaderFxShadow",
            "ShaderFxSwirl",
            "ShaderFxWave",
            "ShaderNode",
            "ShaderNodeAddShader",
            "ShaderNodeAmbientOcclusion",
            "ShaderNodeAttribute",
            "ShaderNodeBackground",
            "ShaderNodeBevel",
            "ShaderNodeBlackbody",
            "ShaderNodeBrightContrast",
            "ShaderNodeBsdfAnisotropic",
            "ShaderNodeBsdfDiffuse",
            "ShaderNodeBsdfGlass",
            "ShaderNodeBsdfHair",
            "ShaderNodeBsdfHairPrincipled",
            "ShaderNodeBsdfPrincipled",
            "ShaderNodeBsdfRefraction",
            "ShaderNodeBsdfSheen",
            "ShaderNodeBsdfToon",
            "ShaderNodeBsdfTranslucent",
            "ShaderNodeBsdfTransparent",
            "ShaderNodeBump",
            "ShaderNodeCameraData",
            "ShaderNodeClamp",
            "ShaderNodeCombineColor",
            "ShaderNodeCombineHSV",
            "ShaderNodeCombineRGB",
            "ShaderNodeCombineXYZ",
            "ShaderNodeCustomGroup",
            "ShaderNodeDisplacement",
            "ShaderNodeEeveeSpecular",
            "ShaderNodeEmission",
            "ShaderNodeFloatCurve",
            "ShaderNodeFresnel",
            "ShaderNodeGamma",
            "ShaderNodeGroup",
            "ShaderNodeHairInfo",
            "ShaderNodeHoldout",
            "ShaderNodeHueSaturation",
            "ShaderNodeInvert",
            "ShaderNodeLayerWeight",
            "ShaderNodeLightFalloff",
            "ShaderNodeLightPath",
            "ShaderNodeMapping",
            "ShaderNodeMapRange",
            "ShaderNodeMath",
            "ShaderNodeMix",
            "ShaderNodeMixRGB",
            "ShaderNodeMixShader",
            "ShaderNodeNewGeometry",
            "ShaderNodeNormal",
            "ShaderNodeNormalMap",
            "ShaderNodeObjectInfo",
            "ShaderNodeOutputAOV",
            "ShaderNodeOutputLight",
            "ShaderNodeOutputLineStyle",
            "ShaderNodeOutputMaterial",
            "ShaderNodeOutputWorld",
            "ShaderNodeParticleInfo",
            "ShaderNodePointInfo",
            "ShaderNodeRGB",
            "ShaderNodeRGBCurve",
            "ShaderNodeRGBToBW",
            "ShaderNodeScript",
            "ShaderNodeSeparateColor",
            "ShaderNodeSeparateHSV",
            "ShaderNodeSeparateRGB",
            "ShaderNodeSeparateXYZ",
            "ShaderNodeShaderToRGB",
            "ShaderNodeSqueeze",
            "ShaderNodeSubsurfaceScattering",
            "ShaderNodeTangent",
            "ShaderNodeTexBrick",
            "ShaderNodeTexChecker",
            "ShaderNodeTexCoord",
            "ShaderNodeTexEnvironment",
            "ShaderNodeTexGradient",
            "ShaderNodeTexIES",
            "ShaderNodeTexImage",
            "ShaderNodeTexMagic",
            "ShaderNodeTexMusgrave",
            "ShaderNodeTexNoise",
            "ShaderNodeTexPointDensity",
            "ShaderNodeTexSky",
            "ShaderNodeTexVoronoi",
            "ShaderNodeTexWave",
            "ShaderNodeTexWhiteNoise",
            "ShaderNodeTree",
            "ShaderNodeUVAlongStroke",
            "ShaderNodeUVMap",
            "ShaderNodeValToRGB",
            "ShaderNodeValue",
            "ShaderNodeVectorCurve",
            "ShaderNodeVectorDisplacement",
            "ShaderNodeVectorMath",
            "ShaderNodeVectorRotate",
            "ShaderNodeVectorTransform",
            "ShaderNodeVertexColor",
            "ShaderNodeVolumeAbsorption",
            "ShaderNodeVolumeInfo",
            "ShaderNodeVolumePrincipled",
            "ShaderNodeVolumeScatter",
            "ShaderNodeWavelength",
            "ShaderNodeWireframe",
            "ShapeKey",
            "ShapeKeyBezierPoint",
            "ShapeKeyCurvePoint",
            "ShapeKeyPoint",
            "ShrinkwrapConstraint",
            "ShrinkwrapGpencilModifier",
            "ShrinkwrapModifier",
            "SimpleDeformModifier",
            "SimplifyGpencilModifier",
            "SimulationStateItem",
            "SimulationZoneViewerPathElem",
            "SkinModifier",
            "SmoothGpencilModifier",
            "SmoothModifier",
            "SoftBodyModifier",
            "SoftBodySettings",
            "SolidifyModifier",
            "Sound",
            "SoundEqualizerModifier",
            "SoundSequence",
            "Space",
            "SpaceClipEditor",
            "SpaceConsole",
            "SpaceDopeSheetEditor",
            "SpaceFileBrowser",
            "SpaceGraphEditor",
            "SpaceImageEditor",
            "SpaceImageOverlay",
            "SpaceInfo",
            "SpaceNLA",
            "SpaceNodeEditor",
            "SpaceNodeEditorPath",
            "SpaceNodeOverlay",
            "SpaceOutliner",
            "SpacePreferences",
            "SpaceProperties",
            "SpaceSequenceEditor",
            "SpaceSpreadsheet",
            "SpaceTextEditor",
            "SpaceUVEditor",
            "SpaceView3D",
            "Speaker",
            "SpeedControlSequence",
            "SPHFluidSettings",
            "Spline",
            "SplineBezierPoints",
            "SplineIKConstraint",
            "SplinePoint",
            "SplinePoints",
            "SpotLight",
            "SpreadsheetColumn",
            "SpreadsheetColumnID",
            "SpreadsheetRowFilter",
            "Stereo3dDisplay",
            "Stereo3dFormat",
            "StretchToConstraint",
            "StringAttribute",
            "StringAttributeValue",
            "StringProperty",
            "Struct",
            "StucciTexture",
            "StudioLight",
            "StudioLights",
            "SubdivGpencilModifier",
            "SubsurfModifier",
            "SubtractSequence",
            "SunLight",
            "SurfaceCurve",
            "SurfaceDeformModifier",
            "SurfaceModifier",
            "TexMapping",
            "TexPaintSlot",
            "Text",
            "TextBox",
            "TextCharacterFormat",
            "TextCurve",
            "TextLine",
            "TextSequence",
            "TEXTURE_UL_texpaintslots",
            "TEXTURE_UL_texslots",
            "Texture",
            "TextureGpencilModifier",
            "TextureNode",
            "TextureNodeAt",
            "TextureNodeBricks",
            "TextureNodeChecker",
            "TextureNodeCombineColor",
            "TextureNodeCompose",
            "TextureNodeCoordinates",
            "TextureNodeCurveRGB",
            "TextureNodeCurveTime",
            "TextureNodeDecompose",
            "TextureNodeDistance",
            "TextureNodeGroup",
            "TextureNodeHueSaturation",
            "TextureNodeImage",
            "TextureNodeInvert",
            "TextureNodeMath",
            "TextureNodeMixRGB",
            "TextureNodeOutput",
            "TextureNodeRGBToBW",
            "TextureNodeRotate",
            "TextureNodeScale",
            "TextureNodeSeparateColor",
            "TextureNodeTexBlend",
            "TextureNodeTexClouds",
            "TextureNodeTexDistNoise",
            "TextureNodeTexMagic",
            "TextureNodeTexMarble",
            "TextureNodeTexMusgrave",
            "TextureNodeTexNoise",
            "TextureNodeTexStucci",
            "TextureNodeTexture",
            "TextureNodeTexVoronoi",
            "TextureNodeTexWood",
            "TextureNodeTranslate",
            "TextureNodeTree",
            "TextureNodeValToNor",
            "TextureNodeValToRGB",
            "TextureNodeViewer",
            "TextureSlot",
            "Theme",
            "ThemeAssetShelf",
            "ThemeBoneColorSet",
            "ThemeClipEditor",
            "ThemeCollectionColor",
            "ThemeConsole",
            "ThemeDopeSheet",
            "ThemeFileBrowser",
            "ThemeFontStyle",
            "ThemeGradientColors",
            "ThemeGraphEditor",
            "ThemeImageEditor",
            "ThemeInfo",
            "ThemeNLAEditor",
            "ThemeNodeEditor",
            "ThemeOutliner",
            "ThemePanelColors",
            "ThemePreferences",
            "ThemeProperties",
            "ThemeSequenceEditor",
            "ThemeSpaceGeneric",
            "ThemeSpaceGradient",
            "ThemeSpaceListGeneric",
            "ThemeSpreadsheet",
            "ThemeStatusBar",
            "ThemeStripColor",
            "ThemeStyle",
            "ThemeTextEditor",
            "ThemeTopBar",
            "ThemeUserInterface",
            "ThemeView3D",
            "ThemeWidgetColors",
            "ThemeWidgetStateColors",
            "ThickGpencilModifier",
            "TimeGpencilModifier",
            "TimeGpencilModifierSegment",
            "TimelineMarker",
            "TimelineMarkers",
            "Timer",
            "TintGpencilModifier",
            "ToolSettings",
            "TrackToConstraint",
            "TransformCacheConstraint",
            "TransformConstraint",
            "TransformOrientation",
            "TransformOrientationSlot",
            "TransformSequence",
            "TriangulateModifier",
            "UDIMTile",
            "UDIMTiles",
            "UI_UL_list",
            "UILayout",
            "UIList",
            "UIPieMenu",
            "UIPopover",
            "UIPopupMenu",
            "UnifiedPaintSettings",
            "UnitSettings",
            "UnknownType",
            "USDHook",
            "UserAssetLibrary",
            "UserExtensionRepo",
            "UserExtensionRepoCollection",
            "USERPREF_UL_asset_libraries",
            "USERPREF_UL_extension_repos",
            "UserSolidLight",
            "UVLoopLayers",
            "UVProjectModifier",
            "UVProjector",
            "UvSculpt",
            "UVWarpModifier",
            "VectorFont",
            "VertexGroup",
            "VertexGroupElement",
            "VertexGroups",
            "VertexPaint",
            "VertexWeightEditModifier",
            "VertexWeightMixModifier",
            "VertexWeightProximityModifier",
            "View2D",
            "VIEW3D_AST_pose_library",
            "VIEW3D_AST_sculpt_brushes",
            "View3DCursor",
            "View3DOverlay",
            "View3DShading",
            "ViewerNodeViewerPathElem",
            "ViewerPath",
            "ViewerPathElem",
            "VIEWLAYER_UL_aov",
            "VIEWLAYER_UL_linesets",
            "ViewLayer",
            "ViewLayerEEVEE",
            "ViewLayers",
            "VOLUME_UL_grids",
            "Volume",
            "VolumeDisplaceModifier",
            "VolumeDisplay",
            "VolumeGrid",
            "VolumeGrids",
            "VolumeRender",
            "VolumeToMeshModifier",
            "VoronoiTexture",
            "WalkNavigation",
            "WarpModifier",
            "WaveModifier",
            "WeightAngleGpencilModifier",
            "WeightedNormalModifier",
            "WeightProxGpencilModifier",
            "WeldModifier",
            "WhiteBalanceModifier",
            "Window",
            "WindowManager",
            "WipeSequence",
            "WireframeModifier",
            "wmOwnerID",
            "wmOwnerIDs",
            "wmTools",
            "WoodTexture",
            "WorkSpace",
            "WorkSpaceTool",
            "World",
            "WorldLighting",
            "WorldMistSettings",
            "XrActionMap",
            "XrActionMapBinding",
            "XrActionMapBindings",
            "XrActionMapItem",
            "XrActionMapItems",
            "XrActionMaps",
            "XrComponentPath",
            "XrComponentPaths",
            "XrEventData",
            "XrSessionSettings",
            "XrSessionState",
            "XrUserPath",
            "XrUserPaths",
            "FluidSimulationModifier",  # for Blender 2.7
            "IDPropertyUIManager",  # for Blender 3.1
        },
        "bpy.types.",
    )
    << GRAVE_QUOTE
)

TYPE_ERROR_CORRECTION = strings_from_tuple(
    ("bpy.types.GPUShader", "gpu.types.GPUShader"),
    ("bpy.types.GPUShaderCreateInfo", "gpu.types.GPUShaderCreateInfo"),
    ("bpy.types.IDPropertyGroup", "idprop.types.IDPropertyGroup"),
    ("bpy.types.GreasePencilv3", "bpy.types.GreasePencil"),
    ("bpy_types.Header", "bpy.types.Header"),
    ("bpy_types.KeyingSetInfo", "bpy.types.KeyingSetInfo"),
    ("bpy_types.Menu", "bpy.types.Menu"),
    ("bpy_types.Node", "bpy.types.Node"),
    ("bpy_types.NodeInternal", "bpy.types.NodeInternal"),
    ("bpy_types.Operator", "bpy.types.Operator"),
    ("bpy_types.Panel", "bpy.types.Panel"),
    ("bpy_types.PropertyGroup", "bpy.types.PropertyGroup"),
    ("bpy_types.RNAMeta", "bpy.types.RNAMeta"),  # for Blender 2.7
    ("bpy_types.UIList", "bpy.types.UIList"),
)

TYPE_ERROR_CORRECTION_GRAVE_QUOTE = GRAVE_QUOTE >> TYPE_ERROR_CORRECTION << GRAVE_QUOTE

BPY_UTILS_PREVIEWS = (
    GRAVE_QUOTE
    >> alt_class(
        ("ImagePreviewCollection",),
        "bpy.utils.previews.",
    )
    << GRAVE_QUOTE
)

IMBUF_TYPES = GRAVE_QUOTE >> alt_class(("ImBuf",), "imbuf.types.") << GRAVE_QUOTE

NONE = string("None")
ANY = SINGLE_QUOTE >> string("typing.Any") << SINGLE_QUOTE | regex(r"[Aa]ny")

LITERAL_INT = regex(r"[-+]?\d+").map(int).desc("LITERAL_INT")
INT = GRAVE_QUOTE >> string("int") << GRAVE_QUOTE | string("integer") | string("int")

LITERAL_BOOL = string("False") | string("True")
BOOL = string(":boolean:") | string("boolean") | string("bool")
BOOL_WITH_CONSTRAINT = seq(BOOL, (string(", default ") >> LITERAL_BOOL).optional())

LITERAL_TUPLE_BOOL = PAREN_L >> LITERAL_BOOL.sep_by(COMMA_SPACE) << PAREN_R
ARRAY_BOOL = string("boolean array")
ARRAY_BOOL_WITH_CONSTRAINT = seq(
    ARRAY_BOOL,
    string(" of ") >> LITERAL_INT << string(" items"),
    (string(", default ") >> LITERAL_TUPLE_BOOL).optional(),
)

FLOAT = string("float") | string("double")

BYTES = string("bytes")

REF_RNA_ENUM = regex(r":ref:`rna_enum_\w+`").desc("REF_RNA_ENUM")

ENUM_STRING = (SINGLE_QUOTE >> regex(r"[\w-]+") << SINGLE_QUOTE).desc("ENUM_STRING")
ENUM_STRING_LIST = BRACK_L >> ENUM_STRING.sep_by(COMMA_SPACE) << BRACK_R
ENUM_LIST = ENUM_STRING_LIST | REF_RNA_ENUM
ENUM_WITH_CONSTRAINT = seq(string("enum in ") >> ENUM_LIST, (string(", default ") >> ENUM_STRING).optional())

ENUM_STRING_SET = BRACE_L >> ENUM_STRING.sep_by(COMMA_SPACE) << BRACE_R
ENUM_SET = ENUM_STRING_SET | REF_RNA_ENUM

ENUM_SET_WITH_CONSTRAINT = seq(
    string("enum set in ") >> ENUM_SET,
    (string(", default ") >> ENUM_STRING_SET).optional(),
)

STRING = GRAVE_QUOTE >> (string("string") | string("str")) << GRAVE_QUOTE | string("string") | string("str")
STRING_WITH_CONSTRAINT = seq(
    STRING >> string(" in "),
    ENUM_LIST,
)

LITERAL_INT_OR_INFINITY = LITERAL_INT | regex(r"[-+]?inf").map(float).desc("INFINITY")
LITERAL_FLOAT = regex(r"[-+]?(?:(?:(?:\d*\.\d+)|(?:\d+\.?))(?:[Ee][+-]?\d+)?|inf)").map(float).desc("LITERAL_FLOAT")
LITERAL_FLOAT2 = PAREN_L >> LITERAL_FLOAT.sep_by(COMMA_SPACE, min=2, max=2) << PAREN_R
LITERAL_FLOAT3 = PAREN_L >> LITERAL_FLOAT.sep_by(COMMA_SPACE, min=3, max=3) << PAREN_R
LITERAL_FLOAT4 = PAREN_L >> LITERAL_FLOAT.sep_by(COMMA_SPACE, min=4, max=4) << PAREN_R
LITERAL_MATRIX33 = PAREN_L >> LITERAL_FLOAT3.sep_by(COMMA_SPACE, min=3, max=3) << PAREN_R
LITERAL_MATRIX44 = PAREN_L >> LITERAL_FLOAT4.sep_by(COMMA_SPACE, min=4, max=4) << PAREN_R

RANGE_INT = seq(
    BRACK_L >> LITERAL_INT_OR_INFINITY,
    COMMA_SPACE >> LITERAL_INT_OR_INFINITY << BRACK_R,
)
INT_WITH_CONSTRAINT = seq(
    string("int in ") >> RANGE_INT,
    (string(", default ") >> LITERAL_INT_OR_INFINITY).optional(),
)

LITERAL_INT_TUPLE = PAREN_L >> LITERAL_INT.sep_by(COMMA_SPACE) << PAREN_R
ARRAY_INT = string("int array")
ARRAY_INT_WITH_CONSTRAINT = seq(
    ARRAY_INT,
    string(" of ") >> LITERAL_INT,
    string(" items in ") >> RANGE_INT,
    (string(", default ") >> LITERAL_INT_TUPLE).optional(),
)

RANGE_FLOAT = seq(BRACK_L >> LITERAL_FLOAT, COMMA_SPACE >> LITERAL_FLOAT << BRACK_R)
FLOAT_WITH_CONSTRAINT = seq(
    string("float in ") >> RANGE_FLOAT,
    (string(", default ") >> LITERAL_FLOAT).optional(),
)

LITERAL_FLOAT_TUPLE = PAREN_L >> LITERAL_FLOAT.sep_by(COMMA_SPACE) << PAREN_R
ARRAY_FLOAT = string("float array")
ARRAY_FLOAT_WITH_CONSTRAINT = seq(
    ARRAY_FLOAT,
    string(" of ") >> LITERAL_INT,
    string(" items in ") >> RANGE_FLOAT,
    (string(", default ") >> LITERAL_FLOAT_TUPLE).optional(),
)

LITERAL_MATRIX_FLOAT = PAREN_L >> LITERAL_FLOAT_TUPLE.sep_by(COMMA_SPACE) << PAREN_R
MATRIX_FLOAT = string("float multi-dimensional array")
MATRIX_FLOAT_WITH_CONSTRAINT = seq(
    MATRIX_FLOAT,
    string(" of ") >> LITERAL_INT,
    string(" * ") >> LITERAL_INT,
    string(" items in ") >> RANGE_FLOAT,
    (string(", default ") >> LITERAL_MATRIX_FLOAT).optional(),
)

LITERAL_STRING = DOUBLE_QUOTE >> regex(r'[^"]*') << DOUBLE_QUOTE
STRING_WITH_CONSTRAINT = seq(
    STRING >> string(" in ") >> ENUM_LIST,
)
STRING_WITH_DEFAULT = seq(
    STRING >> string(", default ") >> LITERAL_STRING,
)

VECTOR = string("`mathutils.Vector`") | string("`Vector`")
VECTOR2 = regex(r"2[Dd] [Vv]ector")
VECTOR2_WITH_CONSTRAINT = seq(
    VECTOR >> string(" of 2 items in ") >> RANGE_FLOAT,
    (string(", default ") >> LITERAL_FLOAT2).optional(),
)
VECTOR3 = regex(r"3[Dd] [Vv]ector") | VECTOR << string(" of size 3")
VECTOR3_WITH_CONSTRAINT = seq(
    VECTOR >> string(" of 3 items in ") >> RANGE_FLOAT,
    (string(", default ") >> LITERAL_FLOAT3).optional(),
)
VECTOR4_WITH_CONSTRAINT = seq(
    VECTOR >> string(" of 4 items in ") >> RANGE_FLOAT,
    (string(", default ") >> LITERAL_FLOAT4).optional(),
)
COLOR = string("`mathutils.Color`") | string("`Color`")
COLOR3_WITH_CONSTRAINT = seq(
    COLOR >> string(" of 3 items in ") >> RANGE_FLOAT,
    (string(", default ") >> LITERAL_FLOAT3).optional(),
)
EULER = string("`mathutils.Euler`") | string("`Euler`")
EULER3_WITH_CONSTRAINT = seq(
    EULER >> string(" rotation of 3 items in ") >> RANGE_FLOAT,
    (string(", default ") >> LITERAL_FLOAT3).optional(),
)
QUATERNION = string("`mathutils.Quaternion`") | string("`Quaternion`")
QUATERNION4_WITH_CONSTRAINT = seq(
    QUATERNION >> string(" rotation of 4 items in ") >> RANGE_FLOAT,
    (string(", default ") >> LITERAL_FLOAT4).optional(),
)

MATRIX = string("`mathutils.Matrix`") | string("`Matrix`")
MATRIX33 = string("3x3 `Matrix`")
MATRIX33_WITH_CONSTRAINT = seq(
    MATRIX >> string(" of 3 * 3 items in ") >> RANGE_FLOAT,
    (string(", default ") >> LITERAL_MATRIX33).optional(),
)

MATRIX44 = string("4x4 `mathutils.Matrix`") | string("4x4 `Matrix`")
MATRIX44_WITH_CONSTRAINT = seq(
    MATRIX >> string(" of 4 * 4 items in ") >> RANGE_FLOAT,
    (string(", default ") >> LITERAL_MATRIX44).optional(),
)

BGL_BUFFER = string("`bgl.Buffer` ") << regex(r"[a-zA-Z_ {}().']+")

PAIR_ELEMENT = QUATERNION | VECTOR | FLOAT | BOOL | INT | BMESH_TYPES_ELEMENTS
PAIR = (
    PAREN_L >> PAIR_ELEMENT.sep_by(COMMA_SPACE, min=2, max=2) << PAREN_R << string(" pair").optional()
    | string("tuple pair of ") >> PAIR_ELEMENT
)

MULTIPROCESSING_POOL = GRAVE_QUOTE >> alt_class(("ThreadPool",), "multiprocessing.pool.") << GRAVE_QUOTE

DEPENDS_ON_FUNCTION_PROTOTYPE = string("Depends on function prototype") | string("Depends of function prototype")

TUPLE = GRAVE_QUOTE >> string("tuple") << GRAVE_QUOTE | string("tuple")
TUPLE_OF_ELEMENTS = forward_declaration()
LIST_ELEMENT = VECTOR | PAIR | TUPLE_OF_ELEMENTS
LIST = GRAVE_QUOTE >> string("list") << GRAVE_QUOTE | string("list")
LIST_OF_ELEMENT = regex("[Ll]ist of ") >> (
    VECTOR << (string(" objects") | string("'s"))
    | INT << string("s")
    | FLOAT << string("s")
    | STRING << string("s")
    | TUPLE << string("s")
    | LIST_ELEMENT
)

LIST_LIST_ELEMENT = INT
LIST_LIST_OF_ELEMENT = string("list of list of ") >> LIST_LIST_ELEMENT

DICT = string("dict")

BPY_PROPERTY_COLLECTION_ELEMENT = NAME_GRAVE_QUOTE
BPY_PROPERTY_COLLECTION_OF_ELEMENT = string("`bpy_prop_collection` of ") >> BPY_PROPERTY_COLLECTION_ELEMENT
NAMED_BPY_PROPERTY_COLLECTION = seq(
    NAME_GRAVE_QUOTE << SPACE,
    BPY_PROPERTY_COLLECTION_OF_ELEMENT,
)

SEQUENCE_OF_BM_ELEM = string("`BMElemSeq` of ") >> BMESH_TYPES_ELEMENTS
SEQUENCE_OF_BM_EDGE = string("`BMEdgeSeq`")
SEQUENCE_OF_BM_EDIT_SEL = string("`BMEditSelSeq`")
SEQUENCE_OF_BM_FACE = string("`BMFaceSeq`")
SEQUENCE_OF_BM_LOOP = string("`BMLoopSeq`")
SEQUENCE_OF_BM_VERT = string("`BMVertSeq`")

SEQUENCE_ELEMENT = FLOAT
SEQUENCE_OF_ELEMENT = string("sequence of ") >> SEQUENCE_ELEMENT

SEQUENCE_OF_FLOAT = string("sequence of ") >> (
    string("1, 2, 3 or 4 values") | string("3 or 4 floats") | string("2 or 3 floats") | string("floats") | string("float")
)

SEQUENCE_OF_STRING = string("sequence of strings")

SEQUENCE_OF_BOOL = string("sequence of bools")

SUBCLASS = BPY_TYPES << string(" subclass")

CALLABLE = strings("callable", "Callable")
CALLABLE_WITH_CONSTRAINT = seq(
    CALLABLE,
    (string(" that takes a string and returns a ") >> (BOOL | STRING) | string("[[], Union[float, None]]")),
)

####################################################################################################

OPTIONAL_ELEMENT = FLOAT | BPY_TYPES | FREESTYLE_TYPES | VECTOR
OPTIONAL = OPTIONAL_ELEMENT << string(" or ") << NONE

UNION_ELEMENT = (
    SEQUENCE_OF_BOOL
    | MATRIX33
    | BOOL
    | DICT
    | NONE
    | EULER
    | QUATERNION
    | FREESTYLE_TYPES
    | MATRIX
    | BMESH_TYPES_ELEMENTS
    | BPY_TYPES
)
UNION = seq(
    UNION_ELEMENT.sep_by(COMMA_SPACE, min=1),
    string(" or ") >> UNION_ELEMENT,
)


TUPLE_ELEMENT = (
    LIST_LIST_OF_ELEMENT
    | LIST_OF_ELEMENT
    | QUATERNION
    | VECTOR
    | STRING
    | INT
    | BOOL
    | BPY_TYPES
    | FREESTYLE_TYPES
    | BMESH_TYPES_ELEMENTS
)
TUPLE_OF_ELEMENT = seq(TUPLE << string(" of "), TUPLE_ELEMENT)
TUPLE_OF_ELEMENTS.become(PAREN_L >> TUPLE_ELEMENT.sep_by(COMMA_SPACE) << PAREN_R)

TYPE_SPECIFIER = (
    ENUM_WITH_CONSTRAINT
    | ENUM_SET_WITH_CONSTRAINT
    | PAIR
    | TUPLE_OF_ELEMENTS
    | TUPLE
    | UNION
    | MATRIX44_WITH_CONSTRAINT
    | MATRIX44
    | MATRIX33_WITH_CONSTRAINT
    | QUATERNION4_WITH_CONSTRAINT
    | EULER3_WITH_CONSTRAINT
    | COLOR3_WITH_CONSTRAINT
    | VECTOR4_WITH_CONSTRAINT
    | VECTOR3_WITH_CONSTRAINT
    | VECTOR2_WITH_CONSTRAINT
    | VECTOR3
    | VECTOR2
    | EULER
    | COLOR
    | ARRAY_FLOAT_WITH_CONSTRAINT
    | ARRAY_INT_WITH_CONSTRAINT
    | ARRAY_BOOL_WITH_CONSTRAINT
    | MATRIX_FLOAT_WITH_CONSTRAINT
    | FLOAT_WITH_CONSTRAINT
    | INT_WITH_CONSTRAINT
    | BOOL_WITH_CONSTRAINT
    | STRING_WITH_CONSTRAINT
    | BOOL
    | NAMED_BPY_PROPERTY_COLLECTION
    | BPY_PROPERTY_COLLECTION_OF_ELEMENT
    | BGL_BUFFER
    | SEQUENCE_OF_BM_ELEM
    | OPTIONAL
    | DICT
    | ANY
    | FLOAT
    | INT
    | LIST_OF_ELEMENT
    | LIST
    | STRING
    | MATRIX
    | QUATERNION
    | VECTOR
    | BMESH_TYPES_ELEMENTS
    | BMESH_TYPES
    | FREESTYLE_TYPES
    | FREESTYLE_CHAININGITERATORS
    | GENERIC_TYPE
    | ACTION_OT
    | ARMATURE_OT
    | CLIP_OT
    | CURVE_OT
    | GPENCIL_OT
    | GRAPH_OT
    | MAKS_OT
    | MESH_OT
    | MBALL_OT
    | NLA_OT
    | NODE_OT
    | OBJECT_OT
    | PAINTCURVE_OT
    | SEQUENCER_OT
    | TRANSFORM_OT
    | UV_OT
    | NUMPY
    | BL_OPERATORS
    | BL_UI_PROPERTIES
    | BL_UI_SPACE
    | BL_UI_UI_UL_LIST
    | SEQUENCE_OF_BM_EDGE
    | SEQUENCE_OF_BM_EDIT_SEL
    | SEQUENCE_OF_BM_FACE
    | SEQUENCE_OF_BM_LOOP
    | SEQUENCE_OF_BM_VERT
    | GRAVE_QUOTE_TYPES
    | SUBCLASS
    | BPY_TYPES
    | BPY_UTILS_PREVIEWS
    | AUD
    | GPU_TYPES
    | IMBUF_TYPES
    | COLLECTION_BPY_TYPES
    | MATHUTILS_BVHTREE_BVHTREE
    | MULTIPROCESSING_POOL
    | TYPE_ERROR_CORRECTION_GRAVE_QUOTE
    | TYPE_ERROR_CORRECTION
    | CALLABLE_WITH_CONSTRAINT
    | CALLABLE
)


HINT = string("readonly") | string("optional") | string("optional argument") | string("never None")
HINTS = PAREN_L >> HINT.sep_by(COMMA_SPACE) << PAREN_R

TYPE_QUALIFIER = seq(
    TYPE_SPECIFIER,
    (COMMA_SPACE >> HINTS).optional(),
)

DATA_TYPE = TYPE_QUALIFIER << string(".").optional()

with open(INPUT_DATA_FILE, "rt", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        try:
            DATA_TYPE.parse(line)
        except ParseError as e:
            print(line)
