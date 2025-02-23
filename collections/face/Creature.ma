//Maya ASCII 2022 scene
//Name: Creature.ma
//Last modified: Fri, Mar 22, 2024 02:47:50 PM
//Codeset: 1252
requires maya "2022";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2022";
fileInfo "version" "2022";
fileInfo "cutIdentifier" "202108111415-612a77abf4";
fileInfo "osv" "Windows 10 Home v2009 (Build: 22631)";
fileInfo "UUID" "B9144C2E-4C1D-A07D-49E3-849A9512C13E";
createNode transform -n "guide";
	rename -uid "8835E798-4B0B-7D1B-F94D-1D92AA4EBD9A";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "globalNamingConvention" -ln "globalNamingConvention" -dt "string";
	addAttr -ci true -sn "guideRoot" -ln "guideRoot" -dt "string";
	addAttr -ci true -sn "rigRoot" -ln "rigRoot" -dt "string";
	addAttr -ci true -sn "geometryGroup" -ln "geometryGroup" -dt "string";
	addAttr -ci true -sn "geometryToken" -ln "geometryToken" -dt "string";
	addAttr -ci true -sn "guidePivotToken" -ln "guidePivotToken" -dt "string";
	addAttr -ci true -sn "guideShapeToken" -ln "guideShapeToken" -dt "string";
	addAttr -ci true -sn "spaceToken" -ln "spaceToken" -dt "string";
	addAttr -ci true -sn "controlToken" -ln "controlToken" -dt "string";
	addAttr -ci true -sn "skinJointToken" -ln "skinJointToken" -dt "string";
	addAttr -ci true -sn "leftSideToken" -ln "leftSideToken" -dt "string";
	addAttr -ci true -sn "rightSideToken" -ln "rightSideToken" -dt "string";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr -l on ".namingConvention" -type "string" "nodeType";
	setAttr -l on ".globalNamingConvention" -type "string" "component, side, element, indices, specific, nodeType";
	setAttr -l on ".guideRoot" -type "string" "guide";
	setAttr -l on ".rigRoot" -type "string" "rig";
	setAttr -l on ".geometryGroup" -type "string" "geometry";
	setAttr -l on ".geometryToken" -type "string" "geo";
	setAttr -l on ".guidePivotToken" -type "string" "guidePivot";
	setAttr -l on ".guideShapeToken" -type "string" "guideShape";
	setAttr -l on ".spaceToken" -type "string" "offset";
	setAttr -l on ".controlToken" -type "string" "control";
	setAttr -l on ".skinJointToken" -type "string" "skin";
	setAttr -l on ".leftSideToken" -type "string" "L";
	setAttr -l on ".rightSideToken" -type "string" "R";
	setAttr -l on -k on ".globalScale";
createNode transform -n "creature_guide" -p "guide";
	rename -uid "26B740FB-46D9-4243-5E70-5294223D436D";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "side" -ln "side" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	setAttr ".t" -type "double3" 0 49.63057644468941 84.74565335405687 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".readyForRigBuild" yes;
	setAttr -l on ".namingConvention" -type "string" "component, nodeType";
	setAttr -l on ".side" -type "string" "None";
	setAttr -l on ".bearVersion" -type "string" "0.25.8";
	setAttr -l on ".componentType" -type "string" "Collection";
	setAttr ".name" -type "string" "creature";
createNode transform -n "eye_guide" -p "creature_guide";
	rename -uid "7CB90214-4117-4D26-4584-3FA0D5D0B316";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "hasEyelids" -ln "hasEyelids" -dt "string";
	addAttr -ci true -sn "hasOuterLine" -ln "hasOuterLine" -dt "string";
	addAttr -ci true -sn "hasSquashStretch" -ln "hasSquashStretch" -dt "string";
	addAttr -ci true -sn "hasCurveRig" -ln "hasCurveRig" -dt "string";
	addAttr -ci true -sn "hasIris" -ln "hasIris" -dt "string";
	addAttr -ci true -sn "hasIrisSquash" -ln "hasIrisSquash" -dt "string";
	addAttr -ci true -sn "hasHighlight" -ln "hasHighlight" -dt "string";
	addAttr -ci true -sn "upperLidJointCount" -ln "upperLidJointCount" -dt "string";
	addAttr -ci true -sn "lowerLidJointCount" -ln "lowerLidJointCount" -dt "string";
	addAttr -ci true -sn "hasUpperLashes" -ln "hasUpperLashes" -dt "string";
	addAttr -ci true -sn "hasLowerLashes" -ln "hasLowerLashes" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "eyeballLeftGeo" -ln "eyeballLeftGeo" -dt "string";
	addAttr -ci true -sn "eyeballRightGeo" -ln "eyeballRightGeo" -dt "string";
	addAttr -ci true -sn "eyeLeftNonUniformGeos" -ln "eyeLeftNonUniformGeos" -dt "string";
	addAttr -ci true -sn "eyeRightNonUniformGeos" -ln "eyeRightNonUniformGeos" -dt "string";
	addAttr -ci true -sn "squashStretchLeftGeos" -ln "squashStretchLeftGeos" -dt "string";
	addAttr -ci true -sn "squashStretchRightGeos" -ln "squashStretchRightGeos" -dt "string";
	addAttr -ci true -sn "eyeLeftScale" -ln "eyeLeftScale" -dt "string";
	addAttr -ci true -sn "eyeRightScale" -ln "eyeRightScale" -dt "string";
	addAttr -ci true -sn "initialPupilSize" -ln "initialPupilSize" -dt "string";
	addAttr -ci true -sn "hasJointGuides" -ln "hasJointGuides" -dt "string";
	addAttr -ci true -sn "spaceNodes" -ln "spaceNodes" -dt "string";
	addAttr -ci true -sn "spaceNames" -ln "spaceNames" -dt "string";
	addAttr -ci true -sn "displaySwitch" -ln "displaySwitch" -dt "string";
	addAttr -ci true -sn "output_eye_L_ball_skin" -ln "output_eye_L_ball_skin" -dt "string";
	addAttr -ci true -sn "output_eye_R_ball_skin" -ln "output_eye_R_ball_skin" -dt "string";
	addAttr -ci true -sn "output_eye_L_innerlid_skin" -ln "output_eye_L_innerlid_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eye_R_innerlid_skin" -ln "output_eye_R_innerlid_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eye_L_upperlidin_skin" -ln "output_eye_L_upperlidin_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eye_R_upperlidin_skin" -ln "output_eye_R_upperlidin_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eye_L_upperlid_skin" -ln "output_eye_L_upperlid_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eye_R_upperlid_skin" -ln "output_eye_R_upperlid_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eye_L_upperlidout_skin" -ln "output_eye_L_upperlidout_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eye_R_upperlidout_skin" -ln "output_eye_R_upperlidout_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eye_L_outerlid_skin" -ln "output_eye_L_outerlid_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eye_R_outerlid_skin" -ln "output_eye_R_outerlid_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eye_L_lowerlidout_skin" -ln "output_eye_L_lowerlidout_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eye_R_lowerlidout_skin" -ln "output_eye_R_lowerlidout_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eye_L_lowerlid_skin" -ln "output_eye_L_lowerlid_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eye_R_lowerlid_skin" -ln "output_eye_R_lowerlid_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eye_L_lowerlidin_skin" -ln "output_eye_L_lowerlidin_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eye_R_lowerlidin_skin" -ln "output_eye_R_lowerlidin_skin" 
		-dt "string";
	setAttr ".t" -type "double3" 4.5705365194577805 14.386938265506018 -7.7140238665716367 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".readyForRigBuild" yes;
	setAttr -l on ".namingConvention" -type "string" "component, nodeType";
	setAttr -l on ".bearVersion" -type "string" "0.25.8";
	setAttr -l on ".componentType" -type "string" "Eyes";
	setAttr ".name" -type "string" "eye";
	setAttr ".hasEyelids" -type "string" "True";
	setAttr ".hasOuterLine" -type "string" "False";
	setAttr ".hasSquashStretch" -type "string" "False";
	setAttr ".hasCurveRig" -type "string" "True";
	setAttr ".hasIris" -type "string" "True";
	setAttr ".hasIrisSquash" -type "string" "False";
	setAttr ".hasHighlight" -type "string" "False";
	setAttr ".upperLidJointCount" -type "string" "7";
	setAttr ".lowerLidJointCount" -type "string" "7";
	setAttr ".hasUpperLashes" -type "string" "False";
	setAttr ".hasLowerLashes" -type "string" "False";
	setAttr ".parentNode" -type "string" "head_control";
	setAttr ".eyeballLeftGeo" -type "string" "None";
	setAttr ".eyeballRightGeo" -type "string" "None";
	setAttr ".eyeLeftNonUniformGeos" -type "string" "None";
	setAttr ".eyeRightNonUniformGeos" -type "string" "None";
	setAttr ".squashStretchLeftGeos" -type "string" "None";
	setAttr ".squashStretchRightGeos" -type "string" "None";
	setAttr ".eyeLeftScale" -type "string" "1, 1, 1";
	setAttr ".eyeRightScale" -type "string" "1, 1, 1";
	setAttr ".initialPupilSize" -type "string" "0.5";
	setAttr ".hasJointGuides" -type "string" "False";
	setAttr ".spaceNodes" -type "string" "root_control, root_placement_control, root_main_pivot_control, body_control, chest_control, head_control";
	setAttr ".spaceNames" -type "string" "root, placement, main, body, chest, head";
	setAttr ".displaySwitch" -type "string" "faceDisplaySwitch";
	setAttr -l on ".output_eye_L_ball_skin" -type "string" "eye_L_ball_skin";
	setAttr -l on ".output_eye_R_ball_skin" -type "string" "eye_R_ball_skin";
	setAttr -l on ".output_eye_L_innerlid_skin" -type "string" "eye_L_innerlid_skin";
	setAttr -l on ".output_eye_R_innerlid_skin" -type "string" "eye_R_innerlid_skin";
	setAttr -l on ".output_eye_L_upperlidin_skin" -type "string" "eye_L_upperlidin_skin";
	setAttr -l on ".output_eye_R_upperlidin_skin" -type "string" "eye_R_upperlidin_skin";
	setAttr -l on ".output_eye_L_upperlid_skin" -type "string" "eye_L_upperlid_skin";
	setAttr -l on ".output_eye_R_upperlid_skin" -type "string" "eye_R_upperlid_skin";
	setAttr -l on ".output_eye_L_upperlidout_skin" -type "string" "eye_L_upperlidout_skin";
	setAttr -l on ".output_eye_R_upperlidout_skin" -type "string" "eye_R_upperlidout_skin";
	setAttr -l on ".output_eye_L_outerlid_skin" -type "string" "eye_L_outerlid_skin";
	setAttr -l on ".output_eye_R_outerlid_skin" -type "string" "eye_R_outerlid_skin";
	setAttr -l on ".output_eye_L_lowerlidout_skin" -type "string" "eye_L_lowerlidout_skin";
	setAttr -l on ".output_eye_R_lowerlidout_skin" -type "string" "eye_R_lowerlidout_skin";
	setAttr -l on ".output_eye_L_lowerlid_skin" -type "string" "eye_L_lowerlid_skin";
	setAttr -l on ".output_eye_R_lowerlid_skin" -type "string" "eye_R_lowerlid_skin";
	setAttr -l on ".output_eye_L_lowerlidin_skin" -type "string" "eye_L_lowerlidin_skin";
	setAttr -l on ".output_eye_R_lowerlidin_skin" -type "string" "eye_R_lowerlidin_skin";
createNode transform -n "eyebrow_guide" -p "creature_guide";
	rename -uid "F82FB854-42F4-16FE-3AB0-319CBB794F30";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "geoNode" -ln "geoNode" -dt "string";
	addAttr -ci true -sn "jointCount" -ln "jointCount" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "hasCurveRig" -ln "hasCurveRig" -dt "string";
	addAttr -ci true -sn "hasSurfaceRig" -ln "hasSurfaceRig" -dt "string";
	addAttr -ci true -sn "hasFollicleRig" -ln "hasFollicleRig" -dt "string";
	addAttr -ci true -sn "hasAnchorRig" -ln "hasAnchorRig" -dt "string";
	addAttr -ci true -sn "hasEyebrowMid" -ln "hasEyebrowMid" -dt "string";
	addAttr -ci true -sn "hasJointGuides" -ln "hasJointGuides" -dt "string";
	addAttr -ci true -sn "displaySwitch" -ln "displaySwitch" -dt "string";
	addAttr -ci true -sn "output_eyebrow_L_follicle_01_skin" -ln "output_eyebrow_L_follicle_01_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eyebrow_L_follicle_02_skin" -ln "output_eyebrow_L_follicle_02_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eyebrow_L_follicle_03_skin" -ln "output_eyebrow_L_follicle_03_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eyebrow_L_follicle_04_skin" -ln "output_eyebrow_L_follicle_04_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eyebrow_L_follicle_05_skin" -ln "output_eyebrow_L_follicle_05_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eyebrow_L_follicle_06_skin" -ln "output_eyebrow_L_follicle_06_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eyebrow_R_follicle_01_skin" -ln "output_eyebrow_R_follicle_01_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eyebrow_R_follicle_02_skin" -ln "output_eyebrow_R_follicle_02_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eyebrow_R_follicle_03_skin" -ln "output_eyebrow_R_follicle_03_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eyebrow_R_follicle_04_skin" -ln "output_eyebrow_R_follicle_04_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eyebrow_R_follicle_05_skin" -ln "output_eyebrow_R_follicle_05_skin" 
		-dt "string";
	addAttr -ci true -sn "output_eyebrow_R_follicle_06_skin" -ln "output_eyebrow_R_follicle_06_skin" 
		-dt "string";
	setAttr ".t" -type "double3" 4.4849347815567535 16.207199356271488 -6.5250194926815226 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".readyForRigBuild" yes;
	setAttr -l on ".namingConvention" -type "string" "component, nodeType";
	setAttr -l on ".bearVersion" -type "string" "0.25.8";
	setAttr -l on ".componentType" -type "string" "Eyebrows";
	setAttr ".name" -type "string" "eyebrow";
	setAttr ".geoNode" -type "string" "head_geo";
	setAttr ".jointCount" -type "string" "6";
	setAttr ".parentNode" -type "string" "head_control";
	setAttr ".hasCurveRig" -type "string" "True";
	setAttr ".hasSurfaceRig" -type "string" "False";
	setAttr ".hasFollicleRig" -type "string" "False";
	setAttr ".hasAnchorRig" -type "string" "False";
	setAttr ".hasEyebrowMid" -type "string" "True";
	setAttr ".hasJointGuides" -type "string" "False";
	setAttr ".displaySwitch" -type "string" "faceDisplaySwitch";
	setAttr -l on ".output_eyebrow_L_follicle_01_skin" -type "string" "eyebrow_L_follicle_01_skin";
	setAttr -l on ".output_eyebrow_L_follicle_02_skin" -type "string" "eyebrow_L_follicle_02_skin";
	setAttr -l on ".output_eyebrow_L_follicle_03_skin" -type "string" "eyebrow_L_follicle_03_skin";
	setAttr -l on ".output_eyebrow_L_follicle_04_skin" -type "string" "eyebrow_L_follicle_04_skin";
	setAttr -l on ".output_eyebrow_L_follicle_05_skin" -type "string" "eyebrow_L_follicle_05_skin";
	setAttr -l on ".output_eyebrow_L_follicle_06_skin" -type "string" "eyebrow_L_follicle_06_skin";
	setAttr -l on ".output_eyebrow_R_follicle_01_skin" -type "string" "eyebrow_R_follicle_01_skin";
	setAttr -l on ".output_eyebrow_R_follicle_02_skin" -type "string" "eyebrow_R_follicle_02_skin";
	setAttr -l on ".output_eyebrow_R_follicle_03_skin" -type "string" "eyebrow_R_follicle_03_skin";
	setAttr -l on ".output_eyebrow_R_follicle_04_skin" -type "string" "eyebrow_R_follicle_04_skin";
	setAttr -l on ".output_eyebrow_R_follicle_05_skin" -type "string" "eyebrow_R_follicle_05_skin";
	setAttr -l on ".output_eyebrow_R_follicle_06_skin" -type "string" "eyebrow_R_follicle_06_skin";
createNode transform -n "mouth_guide" -p "creature_guide";
	rename -uid "9886C0EB-4CB1-CF3A-1F15-9A89C3FDF362";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "upperLipJointCount" -ln "upperLipJointCount" -dt "string";
	addAttr -ci true -sn "lowerLipJointCount" -ln "lowerLipJointCount" -dt "string";
	addAttr -ci true -sn "wrinkleJointCount" -ln "wrinkleJointCount" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "headJointNode" -ln "headJointNode" -dt "string";
	addAttr -ci true -sn "hasAnchorRig" -ln "hasAnchorRig" -dt "string";
	addAttr -ci true -sn "hasSurfaceRig" -ln "hasSurfaceRig" -dt "string";
	addAttr -ci true -sn "hasLips" -ln "hasLips" -dt "string";
	addAttr -ci true -sn "hasNoRollJoints" -ln "hasNoRollJoints" -dt "string";
	addAttr -ci true -sn "hasJointGuides" -ln "hasJointGuides" -dt "string";
	addAttr -ci true -sn "hasStickyLips" -ln "hasStickyLips" -dt "string";
	addAttr -ci true -sn "input_noseName" -ln "input_noseName" -dt "string";
	addAttr -ci true -sn "input_cheeksName" -ln "input_cheeksName" -dt "string";
	addAttr -ci true -sn "displaySwitch" -ln "displaySwitch" -dt "string";
	addAttr -ci true -sn "output_mouth_R_upperlip_01_skin" -ln "output_mouth_R_upperlip_01_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_upperlip_02_skin" -ln "output_mouth_R_upperlip_02_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_upperlip_03_skin" -ln "output_mouth_R_upperlip_03_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_upperlip_04_skin" -ln "output_mouth_R_upperlip_04_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_upperlip_05_skin" -ln "output_mouth_R_upperlip_05_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_upperlip_06_skin" -ln "output_mouth_R_upperlip_06_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_upperlip_07_skin" -ln "output_mouth_R_upperlip_07_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_upperlip_08_skin" -ln "output_mouth_R_upperlip_08_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_upperlip_09_skin" -ln "output_mouth_R_upperlip_09_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_upperlip_10_skin" -ln "output_mouth_R_upperlip_10_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_upperlip_11_skin" -ln "output_mouth_R_upperlip_11_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_upperlip_12_skin" -ln "output_mouth_R_upperlip_12_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_upperlip_13_skin" -ln "output_mouth_R_upperlip_13_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_lowerlip_01_skin" -ln "output_mouth_R_lowerlip_01_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_lowerlip_02_skin" -ln "output_mouth_R_lowerlip_02_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_lowerlip_03_skin" -ln "output_mouth_R_lowerlip_03_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_lowerlip_04_skin" -ln "output_mouth_R_lowerlip_04_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_lowerlip_05_skin" -ln "output_mouth_R_lowerlip_05_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_lowerlip_06_skin" -ln "output_mouth_R_lowerlip_06_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_lowerlip_07_skin" -ln "output_mouth_R_lowerlip_07_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_lowerlip_08_skin" -ln "output_mouth_R_lowerlip_08_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_lowerlip_09_skin" -ln "output_mouth_R_lowerlip_09_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_lowerlip_10_skin" -ln "output_mouth_R_lowerlip_10_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_lowerlip_11_skin" -ln "output_mouth_R_lowerlip_11_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_lowerlip_12_skin" -ln "output_mouth_R_lowerlip_12_skin" 
		-dt "string";
	addAttr -ci true -sn "output_mouth_R_lowerlip_13_skin" -ln "output_mouth_R_lowerlip_13_skin" 
		-dt "string";
	setAttr ".t" -type "double3" 0 1.8595291405684904 -5.1885714360854536 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".readyForRigBuild" yes;
	setAttr -l on ".namingConvention" -type "string" "component, nodeType";
	setAttr -l on ".bearVersion" -type "string" "0.25.8";
	setAttr -l on ".componentType" -type "string" "Mouth";
	setAttr ".name" -type "string" "mouth";
	setAttr ".upperLipJointCount" -type "string" "13";
	setAttr ".lowerLipJointCount" -type "string" "13";
	setAttr ".wrinkleJointCount" -type "string" "0";
	setAttr ".parentNode" -type "string" "head_control";
	setAttr ".headJointNode" -type "string" "head_skin";
	setAttr ".hasAnchorRig" -type "string" "False";
	setAttr ".hasSurfaceRig" -type "string" "True";
	setAttr ".hasLips" -type "string" "True";
	setAttr ".hasNoRollJoints" -type "string" "False";
	setAttr ".hasJointGuides" -type "string" "False";
	setAttr ".hasStickyLips" -type "string" "True";
	setAttr ".input_noseName" -type "string" "nose";
	setAttr ".input_cheeksName" -type "string" "cheeks";
	setAttr ".displaySwitch" -type "string" "faceDisplaySwitch";
	setAttr -l on ".output_mouth_R_upperlip_01_skin" -type "string" "mouth_R_upperlip_01_skin";
	setAttr -l on ".output_mouth_R_upperlip_02_skin" -type "string" "mouth_R_upperlip_02_skin";
	setAttr -l on ".output_mouth_R_upperlip_03_skin" -type "string" "mouth_R_upperlip_03_skin";
	setAttr -l on ".output_mouth_R_upperlip_04_skin" -type "string" "mouth_R_upperlip_04_skin";
	setAttr -l on ".output_mouth_R_upperlip_05_skin" -type "string" "mouth_R_upperlip_05_skin";
	setAttr -l on ".output_mouth_R_upperlip_06_skin" -type "string" "mouth_R_upperlip_06_skin";
	setAttr -l on ".output_mouth_R_upperlip_07_skin" -type "string" "mouth_R_upperlip_07_skin";
	setAttr -l on ".output_mouth_R_upperlip_08_skin" -type "string" "mouth_R_upperlip_08_skin";
	setAttr -l on ".output_mouth_R_upperlip_09_skin" -type "string" "mouth_R_upperlip_09_skin";
	setAttr -l on ".output_mouth_R_upperlip_10_skin" -type "string" "mouth_R_upperlip_10_skin";
	setAttr -l on ".output_mouth_R_upperlip_11_skin" -type "string" "mouth_R_upperlip_11_skin";
	setAttr -l on ".output_mouth_R_upperlip_12_skin" -type "string" "mouth_R_upperlip_12_skin";
	setAttr -l on ".output_mouth_R_upperlip_13_skin" -type "string" "mouth_R_upperlip_13_skin";
	setAttr -l on ".output_mouth_R_lowerlip_01_skin" -type "string" "mouth_R_lowerlip_01_skin";
	setAttr -l on ".output_mouth_R_lowerlip_02_skin" -type "string" "mouth_R_lowerlip_02_skin";
	setAttr -l on ".output_mouth_R_lowerlip_03_skin" -type "string" "mouth_R_lowerlip_03_skin";
	setAttr -l on ".output_mouth_R_lowerlip_04_skin" -type "string" "mouth_R_lowerlip_04_skin";
	setAttr -l on ".output_mouth_R_lowerlip_05_skin" -type "string" "mouth_R_lowerlip_05_skin";
	setAttr -l on ".output_mouth_R_lowerlip_06_skin" -type "string" "mouth_R_lowerlip_06_skin";
	setAttr -l on ".output_mouth_R_lowerlip_07_skin" -type "string" "mouth_R_lowerlip_07_skin";
	setAttr -l on ".output_mouth_R_lowerlip_08_skin" -type "string" "mouth_R_lowerlip_08_skin";
	setAttr -l on ".output_mouth_R_lowerlip_09_skin" -type "string" "mouth_R_lowerlip_09_skin";
	setAttr -l on ".output_mouth_R_lowerlip_10_skin" -type "string" "mouth_R_lowerlip_10_skin";
	setAttr -l on ".output_mouth_R_lowerlip_11_skin" -type "string" "mouth_R_lowerlip_11_skin";
	setAttr -l on ".output_mouth_R_lowerlip_12_skin" -type "string" "mouth_R_lowerlip_12_skin";
	setAttr -l on ".output_mouth_R_lowerlip_13_skin" -type "string" "mouth_R_lowerlip_13_skin";
createNode transform -n "cheek_guide" -p "creature_guide";
	rename -uid "C8A12C08-4EEB-B272-5E34-A590E3BF737A";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "hasSecondaryControls" -ln "hasSecondaryControls" -dt "string";
	addAttr -ci true -sn "hasExtraCheekControl" -ln "hasExtraCheekControl" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "displaySwitch" -ln "displaySwitch" -dt "string";
	addAttr -ci true -sn "output_cheek_L_main_skin" -ln "output_cheek_L_main_skin" -dt "string";
	addAttr -ci true -sn "output_cheek_R_main_skin" -ln "output_cheek_R_main_skin" -dt "string";
	addAttr -ci true -sn "output_cheek_L_01_skin" -ln "output_cheek_L_01_skin" -dt "string";
	addAttr -ci true -sn "output_cheek_R_01_skin" -ln "output_cheek_R_01_skin" -dt "string";
	addAttr -ci true -sn "output_cheek_L_02_skin" -ln "output_cheek_L_02_skin" -dt "string";
	addAttr -ci true -sn "output_cheek_R_02_skin" -ln "output_cheek_R_02_skin" -dt "string";
	setAttr ".t" -type "double3" 7.177256682881608 11.151182431689406 -8.3410870053079122 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".readyForRigBuild" yes;
	setAttr -l on ".namingConvention" -type "string" "component, nodeType";
	setAttr -l on ".bearVersion" -type "string" "0.25.8";
	setAttr -l on ".componentType" -type "string" "Cheeks";
	setAttr ".name" -type "string" "cheek";
	setAttr ".hasSecondaryControls" -type "string" "True";
	setAttr ".hasExtraCheekControl" -type "string" "False";
	setAttr ".parentNode" -type "string" "head_control";
	setAttr ".displaySwitch" -type "string" "faceDisplaySwitch";
	setAttr -l on ".output_cheek_L_main_skin" -type "string" "cheek_L_main_skin";
	setAttr -l on ".output_cheek_R_main_skin" -type "string" "cheek_R_main_skin";
	setAttr -l on ".output_cheek_L_01_skin" -type "string" "cheek_L_01_skin";
	setAttr -l on ".output_cheek_R_01_skin" -type "string" "cheek_R_01_skin";
	setAttr -l on ".output_cheek_L_02_skin" -type "string" "cheek_L_02_skin";
	setAttr -l on ".output_cheek_R_02_skin" -type "string" "cheek_R_02_skin";
createNode transform -n "nose_guide" -p "creature_guide";
	rename -uid "563E7D5D-44DF-76D1-5F71-DC8955B07A14";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "controlCount" -ln "controlCount" -dt "string";
	addAttr -ci true -sn "hasNostril" -ln "hasNostril" -dt "string";
	addAttr -ci true -sn "hasTurnup" -ln "hasTurnup" -dt "string";
	addAttr -ci true -sn "turnupParentIndex" -ln "turnupParentIndex" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "displaySwitch" -ln "displaySwitch" -dt "string";
	addAttr -ci true -sn "output_nose_L_01_skin" -ln "output_nose_L_01_skin" -dt "string";
	addAttr -ci true -sn "output_nose_L_02_skin" -ln "output_nose_L_02_skin" -dt "string";
	addAttr -ci true -sn "output_nose_L_03_skin" -ln "output_nose_L_03_skin" -dt "string";
	addAttr -ci true -sn "output_nose_L_04_skin" -ln "output_nose_L_04_skin" -dt "string";
	addAttr -ci true -sn "output_nose_L_nostril_skin" -ln "output_nose_L_nostril_skin" 
		-dt "string";
	setAttr ".t" -type "double3" 0 11.218686732505994 -1.4750204067103994 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".readyForRigBuild" yes;
	setAttr -l on ".namingConvention" -type "string" "component, nodeType";
	setAttr -l on ".bearVersion" -type "string" "0.25.8";
	setAttr -l on ".componentType" -type "string" "Nose";
	setAttr ".name" -type "string" "nose";
	setAttr ".controlCount" -type "string" "4";
	setAttr ".hasNostril" -type "string" "True";
	setAttr ".hasTurnup" -type "string" "False";
	setAttr ".turnupParentIndex" -type "string" "0";
	setAttr ".parentNode" -type "string" "head_control";
	setAttr ".displaySwitch" -type "string" "faceDisplaySwitch";
	setAttr -l on ".output_nose_L_01_skin" -type "string" "nose_L_01_skin";
	setAttr -l on ".output_nose_L_02_skin" -type "string" "nose_L_02_skin";
	setAttr -l on ".output_nose_L_03_skin" -type "string" "nose_L_03_skin";
	setAttr -l on ".output_nose_L_04_skin" -type "string" "nose_L_04_skin";
	setAttr -l on ".output_nose_L_nostril_skin" -type "string" "nose_L_nostril_skin";
createNode transform -n "tongue_guide" -p "creature_guide";
	rename -uid "B4D86888-4F64-889A-E0E9-859AB4371068";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "side" -ln "side" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "controlCount" -ln "controlCount" -dt "string";
	addAttr -ci true -sn "jointCount" -ln "jointCount" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "hasJointGuides" -ln "hasJointGuides" -dt "string";
	addAttr -ci true -sn "displaySwitch" -ln "displaySwitch" -dt "string";
	addAttr -ci true -sn "output_tongue_01_skin" -ln "output_tongue_01_skin" -dt "string";
	addAttr -ci true -sn "output_tongue_02_skin" -ln "output_tongue_02_skin" -dt "string";
	addAttr -ci true -sn "output_tongue_03_skin" -ln "output_tongue_03_skin" -dt "string";
	addAttr -ci true -sn "output_tongue_04_skin" -ln "output_tongue_04_skin" -dt "string";
	addAttr -ci true -sn "output_tongue_05_skin" -ln "output_tongue_05_skin" -dt "string";
	addAttr -ci true -sn "output_tongue_06_skin" -ln "output_tongue_06_skin" -dt "string";
	addAttr -ci true -sn "output_tongue_07_skin" -ln "output_tongue_07_skin" -dt "string";
	addAttr -ci true -sn "output_tongue_08_skin" -ln "output_tongue_08_skin" -dt "string";
	addAttr -ci true -sn "output_tongue_09_skin" -ln "output_tongue_09_skin" -dt "string";
	addAttr -ci true -sn "output_tongue_10_skin" -ln "output_tongue_10_skin" -dt "string";
	addAttr -ci true -sn "output_tongue_11_skin" -ln "output_tongue_11_skin" -dt "string";
	addAttr -ci true -sn "output_tongue_12_skin" -ln "output_tongue_12_skin" -dt "string";
	setAttr ".t" -type "double3" 0 7.4498577225153682 -15.177119455701899 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".readyForRigBuild" yes;
	setAttr -l on ".namingConvention" -type "string" "component, nodeType";
	setAttr -l on ".side" -type "string" "None";
	setAttr -l on ".bearVersion" -type "string" "0.25.8";
	setAttr -l on ".componentType" -type "string" "Tongue";
	setAttr ".name" -type "string" "tongue";
	setAttr ".controlCount" -type "string" "6";
	setAttr ".jointCount" -type "string" "12";
	setAttr ".parentNode" -type "string" "mouth_jaw_control";
	setAttr ".hasJointGuides" -type "string" "False";
	setAttr ".displaySwitch" -type "string" "faceDisplaySwitch";
	setAttr -l on ".output_tongue_01_skin" -type "string" "tongue_01_skin";
	setAttr -l on ".output_tongue_02_skin" -type "string" "tongue_02_skin";
	setAttr -l on ".output_tongue_03_skin" -type "string" "tongue_03_skin";
	setAttr -l on ".output_tongue_04_skin" -type "string" "tongue_04_skin";
	setAttr -l on ".output_tongue_05_skin" -type "string" "tongue_05_skin";
	setAttr -l on ".output_tongue_06_skin" -type "string" "tongue_06_skin";
	setAttr -l on ".output_tongue_07_skin" -type "string" "tongue_07_skin";
	setAttr -l on ".output_tongue_08_skin" -type "string" "tongue_08_skin";
	setAttr -l on ".output_tongue_09_skin" -type "string" "tongue_09_skin";
	setAttr -l on ".output_tongue_10_skin" -type "string" "tongue_10_skin";
	setAttr -l on ".output_tongue_11_skin" -type "string" "tongue_11_skin";
	setAttr -l on ".output_tongue_12_skin" -type "string" "tongue_12_skin";
createNode transform -n "ear_guide" -p "creature_guide";
	rename -uid "C79FEF1F-4AD5-C7E5-791B-CE92FD91BF25";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "controlCount" -ln "controlCount" -dt "string";
	addAttr -ci true -sn "extraControlCount" -ln "extraControlCount" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "displaySwitch" -ln "displaySwitch" -dt "string";
	setAttr ".t" -type "double3" 7.5479963938755645 24.108963972591667 -20.097512492496435 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".readyForRigBuild" yes;
	setAttr -l on ".namingConvention" -type "string" "component, nodeType";
	setAttr -l on ".bearVersion" -type "string" "0.25.8";
	setAttr -l on ".componentType" -type "string" "Ears";
	setAttr ".name" -type "string" "ear";
	setAttr ".controlCount" -type "string" "4";
	setAttr ".extraControlCount" -type "string" "0";
	setAttr ".parentNode" -type "string" "head_control";
	setAttr ".displaySwitch" -type "string" "faceDisplaySwitch";
createNode transform -s -n "persp";
	rename -uid "72C26B0F-42FB-9D20-71A5-FBB98B99A9C1";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 29.768781773218787 22.326586329914093 29.768781773218791 ;
	setAttr ".r" -type "double3" -27.938352729602379 44.999999999999972 -5.172681101354183e-14 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "7C692F34-42A5-47E6-DE0A-0F89FA820959";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 47.653302022736611;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "67821C5C-40E1-03FD-F25A-B8A3146B9518";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -90 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "E0123779-458F-8C00-CAA0-D99FCA6C8B59";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
createNode transform -s -n "front";
	rename -uid "CD500CDB-47B7-F637-0CE0-948A83EDC1BF";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "A83C6802-478F-119F-BF57-99944E2B4D16";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	rename -uid "C4E7C92B-48B5-B010-78A0-DDB2806B9FC1";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 90 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "27645B4F-4C6B-194E-020E-86A2B2D75709";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "1A3F88E1-4969-E677-0A43-A189A97A19F7";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "BBDCB849-467D-A2D7-7B6D-EF94599D1664";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "326404A6-4AB1-9643-74D5-D9A3001D876C";
createNode displayLayerManager -n "layerManager";
	rename -uid "678683FE-4522-3091-72A8-E2A97FB0BBF7";
createNode displayLayer -n "defaultLayer";
	rename -uid "202A4ADA-4A1F-54AE-B62A-49AF6DDFF2A6";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "1366810A-48CF-94EA-806A-A885EF34DA56";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "AB7BBFF1-4021-DA2E-DAE3-E9B50008557E";
	setAttr ".g" yes;
createNode script -n "uiConfigurationScriptNode";
	rename -uid "F46D4AE5-4755-4018-B2AC-96860DF19452";
	setAttr ".b" -type "string" (
		"// Maya Mel UI Configuration File.\n//\n//  This script is machine generated.  Edit at your own risk.\n//\n//\n\nglobal string $gMainPane;\nif (`paneLayout -exists $gMainPane`) {\n\n\tglobal int $gUseScenePanelConfig;\n\tint    $useSceneConfig = $gUseScenePanelConfig;\n\tint    $nodeEditorPanelVisible = stringArrayContains(\"nodeEditorPanel1\", `getPanel -vis`);\n\tint    $nodeEditorWorkspaceControlOpen = (`workspaceControl -exists nodeEditorPanel1Window` && `workspaceControl -q -visible nodeEditorPanel1Window`);\n\tint    $menusOkayInPanels = `optionVar -q allowMenusInPanels`;\n\tint    $nVisPanes = `paneLayout -q -nvp $gMainPane`;\n\tint    $nPanes = 0;\n\tstring $editorName;\n\tstring $panelName;\n\tstring $itemFilterName;\n\tstring $panelConfig;\n\n\t//\n\t//  get current state of the UI\n\t//\n\tsceneUIReplacement -update $gMainPane;\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Top View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        modelEditor -e \n            -docTag \"RADRENDER\" \n            -editorChanged \"updateModelPanelBar\" \n            -camera \"|top|topShape\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n"
		+ "            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n"
		+ "            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            -activeShadingGraph \"ballora_animatronic_shadow_rig:rsMaterial1SG,ballora_animatronic_shadow_rig:MAT_ballora,ballora_animatronic_shadow_rig:MAT_ballora\" \n"
		+ "            -activeCustomGeometry \"meshShaderball\" \n            -activeCustomLighSet \"defaultAreaLightSet\" \n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Side View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -docTag \"RADRENDER\" \n            -editorChanged \"updateModelPanelBar\" \n            -camera \"|side|sideShape\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n"
		+ "            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n"
		+ "            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n"
		+ "            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            -activeShadingGraph \"ballora_animatronic_shadow_rig:rsMaterial1SG,ballora_animatronic_shadow_rig:MAT_ballora,ballora_animatronic_shadow_rig:MAT_ballora\" \n            -activeCustomGeometry \"meshShaderball\" \n            -activeCustomLighSet \"defaultAreaLightSet\" \n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Front View\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Front View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -docTag \"RADRENDER\" \n            -editorChanged \"updateModelPanelBar\" \n            -camera \"|front|frontShape\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n"
		+ "            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n"
		+ "            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n"
		+ "            -sceneRenderFilter 0\n            -activeShadingGraph \"ballora_animatronic_shadow_rig:rsMaterial1SG,ballora_animatronic_shadow_rig:MAT_ballora,ballora_animatronic_shadow_rig:MAT_ballora\" \n            -activeCustomGeometry \"meshShaderball\" \n            -activeCustomLighSet \"defaultAreaLightSet\" \n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -docTag \"RADRENDER\" \n            -editorChanged \"updateModelPanelBar\" \n            -camera \"|persp|perspShape\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n"
		+ "            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 1\n            -activeComponentsXray 0\n            -displayTextures 1\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n"
		+ "            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 0\n            -nurbsCurves 0\n            -nurbsSurfaces 0\n            -polymeshes 1\n            -subdivSurfaces 0\n            -planes 0\n            -lights 0\n            -cameras 0\n            -controlVertices 0\n            -hulls 0\n            -grid 0\n            -imagePlane 0\n            -joints 0\n            -ikHandles 0\n            -deformers 0\n            -dynamics 0\n"
		+ "            -particleInstancers 0\n            -fluids 0\n            -hairSystems 0\n            -follicles 0\n            -nCloths 0\n            -nParticles 0\n            -nRigids 0\n            -dynamicConstraints 0\n            -locators 0\n            -manipulators 0\n            -pluginShapes 0\n            -dimensions 0\n            -handles 0\n            -pivots 0\n            -textures 0\n            -strokes 0\n            -motionTrails 0\n            -clipGhosts 0\n            -greasePencils 0\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1959\n            -height 1239\n            -sceneRenderFilter 0\n            -activeShadingGraph \"ballora_animatronic_shadow_rig:rsMaterial1SG,ballora_animatronic_shadow_rig:MAT_ballora,ballora_animatronic_shadow_rig:MAT_ballora\" \n            -activeCustomGeometry \"meshShaderball\" \n            -activeCustomLighSet \"defaultAreaLightSet\" \n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n"
		+ "            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"Outliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -docTag \"isolOutln_fromSeln\" \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 0\n            -showReferenceMembers 0\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n"
		+ "            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -isSet 0\n            -isSetMember 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n"
		+ "            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            -renderFilterIndex 0\n            -selectionOrder \"chronological\" \n            -expandAttribute 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"Outliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -docTag \"isolOutln_fromSeln\" \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 0\n            -showReferenceMembers 0\n            -showAttributes 0\n"
		+ "            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -displayMode \"DAG\" \n"
		+ "            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"graphEditor\" (localizedPanelLabel(\"Graph Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n"
		+ "            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showParentContainers 1\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n"
		+ "                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n"
		+ "                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayValues 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -showPlayRangeShades \"on\" \n                -lockPlayRangeShades \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -keyMinScale 1\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -valueLinesToggle 1\n                -outliner \"graphEditor1OutlineEd\" \n                -highlightAffectedCurves 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dopeSheetPanel\" (localizedPanelLabel(\"Dope Sheet\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dope Sheet\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showParentContainers 1\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n"
		+ "                -showUpstreamCurves 1\n                -showUnitlessCurves 0\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 1\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n"
		+ "                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"DopeSheetEd\");\n            dopeSheetEditor -e \n                -displayValues 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -outliner \"dopeSheetPanel1OutlineEd\" \n                -showSummary 1\n                -showScene 0\n                -hierarchyBelow 0\n                -showTicks 1\n                -selectionWindow 0 0 0 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"timeEditorPanel\" (localizedPanelLabel(\"Time Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Time Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"clipEditorPanel\" (localizedPanelLabel(\"Trax Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Trax Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = clipEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayValues 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"sequenceEditorPanel\" (localizedPanelLabel(\"Camera Sequencer\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Camera Sequencer\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = sequenceEditorNameFromPanel($panelName);\n"
		+ "            clipEditor -e \n                -displayValues 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 1 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperGraphPanel\" (localizedPanelLabel(\"Hypergraph Hierarchy\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypergraph Hierarchy\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"HyperGraphEd\");\n            hyperGraph -e \n                -graphLayoutStyle \"hierarchicalLayout\" \n                -orientation \"horiz\" \n                -mergeConnections 0\n                -zoom 1\n                -animateTransition 0\n                -showRelationships 1\n                -showShapes 0\n                -showDeformers 0\n                -showExpressions 0\n                -showConstraints 0\n"
		+ "                -showConnectionFromSelected 0\n                -showConnectionToSelected 0\n                -showConstraintLabels 0\n                -showUnderworld 0\n                -showInvisible 0\n                -transitionFrames 1\n                -opaqueContainers 0\n                -freeform 0\n                -imagePosition 0 0 \n                -imageScale 1\n                -imageEnabled 0\n                -graphType \"DAG\" \n                -heatMapDisplay 0\n                -updateSelection 1\n                -updateNodeAdded 1\n                -useDrawOverrideColor 0\n                -limitGraphTraversal -1\n                -range 0 0 \n                -iconSize \"smallIcons\" \n                -showCachedConnections 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperShadePanel\" (localizedPanelLabel(\"Hypershade\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypershade\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"visorPanel\" (localizedPanelLabel(\"Visor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Visor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"nodeEditorPanel\" (localizedPanelLabel(\"Node Editor\")) `;\n\tif ($nodeEditorPanelVisible || $nodeEditorWorkspaceControlOpen) {\n\t\tif (\"\" == $panelName) {\n\t\t\tif ($useSceneConfig) {\n\t\t\t\t$panelName = `scriptedPanel -unParent  -type \"nodeEditorPanel\" -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n"
		+ "                -connectNodeOnCreation 0\n                -connectOnDrop 0\n                -copyConnectionsOnPaste 0\n                -connectionStyle \"bezier\" \n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -crosshairOnEdgeDragging 0\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -editorMode \"default\" \n                -hasWatchpoint 0\n                $editorName;\n\t\t\t}\n\t\t} else {\n\t\t\t$label = `panel -q -label $panelName`;\n\t\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -connectNodeOnCreation 0\n                -connectOnDrop 0\n                -copyConnectionsOnPaste 0\n                -connectionStyle \"bezier\" \n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -crosshairOnEdgeDragging 0\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n"
		+ "                -syncedSelection 1\n                -extendToShapes 1\n                -editorMode \"default\" \n                -hasWatchpoint 0\n                $editorName;\n\t\t\tif (!$useSceneConfig) {\n\t\t\t\tpanel -e -l $label $panelName;\n\t\t\t}\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"createNodePanel\" (localizedPanelLabel(\"Create Node\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Create Node\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"polyTexturePlacementPanel\" (localizedPanelLabel(\"UV Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"UV Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"renderWindowPanel\" (localizedPanelLabel(\"Render View\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Render View\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"shapePanel\" (localizedPanelLabel(\"Shape Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tshapePanel -edit -l (localizedPanelLabel(\"Shape Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"posePanel\" (localizedPanelLabel(\"Pose Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tposePanel -edit -l (localizedPanelLabel(\"Pose Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynRelEdPanel\" (localizedPanelLabel(\"Dynamic Relationships\")) `;\n\tif (\"\" != $panelName) {\n"
		+ "\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dynamic Relationships\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"relationshipPanel\" (localizedPanelLabel(\"Relationship Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Relationship Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"referenceEditorPanel\" (localizedPanelLabel(\"Reference Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Reference Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"componentEditorPanel\" (localizedPanelLabel(\"Component Editor\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Component Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynPaintScriptedPanelType\" (localizedPanelLabel(\"Paint Effects\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Paint Effects\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"scriptEditorPanel\" (localizedPanelLabel(\"Script Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"profilerPanel\" (localizedPanelLabel(\"Profiler Tool\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Profiler Tool\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"contentBrowserPanel\" (localizedPanelLabel(\"Content Browser\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Content Browser\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"Stereo\" (localizedPanelLabel(\"Stereo\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Stereo\")) -mbv $menusOkayInPanels  $panelName;\n{ string $editorName = ($panelName+\"Editor\");\n            stereoCameraView -e \n                -editorChanged \"updateModelPanelBar\" \n                -camera \"|persp|perspShape\" \n"
		+ "                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"smoothShaded\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -holdOuts 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 0\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 32768\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n"
		+ "                -fogColor 0.5 0.5 0.5 1 \n                -depthOfFieldPreview 1\n                -maxConstantTransparency 1\n                -rendererOverrideName \"stereoOverrideVP2\" \n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 4 4 \n                -bumpResolution 4 4 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 0\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -controllers 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n"
		+ "                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -clipGhosts 1\n                -greasePencils 1\n                -shadows 0\n                -captureSequenceNumber -1\n                -width 0\n                -height 0\n"
		+ "                -sceneRenderFilter 0\n                -displayMode \"centerEye\" \n                -viewColor 0 0 0 1 \n                -useCustomBackground 1\n                $editorName;\n            stereoCameraView -e -viewSelected 0 $editorName;\n            stereoCameraView -e \n                -pluginObjects \"gpuCacheDisplayFilter\" 1 \n                $editorName; };\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Persp View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -docTag \"RADRENDER\" \n            -editorChanged \"updateModelPanelBar\" \n            -camera \"|persp|perspShape\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n"
		+ "            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n"
		+ "            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n"
		+ "            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1959\n            -height 1239\n            -sceneRenderFilter 0\n            -activeShadingGraph \"ballora_animatronic_shadow_rig:rsMaterial1SG,ballora_animatronic_shadow_rig:MAT_ballora,ballora_animatronic_shadow_rig:MAT_ballora\" \n            -activeCustomGeometry \"meshShaderball\" \n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"ToggledOutliner\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"ToggledOutliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -docTag \"isolOutln_fromSeln\" \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 1\n            -showReferenceMembers 1\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n"
		+ "            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -isSet 0\n            -isSetMember 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -selectCommand \"print(\\\"\\\")\" \n            -showNamespace 1\n            -showPinIcons 0\n"
		+ "            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            -renderFilterIndex 0\n            -selectionOrder \"chronological\" \n            -expandAttribute 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\tif ($useSceneConfig) {\n        string $configName = `getPanel -cwl (localizedPanelLabel(\"Current Layout\"))`;\n        if (\"\" != $configName) {\n\t\t\tpanelConfiguration -edit -label (localizedPanelLabel(\"Current Layout\")) \n\t\t\t\t-userCreated false\n\t\t\t\t-defaultImage \"vacantCell.xP:/\"\n\t\t\t\t-image \"\"\n\t\t\t\t-sc false\n\t\t\t\t-configString \"global string $gMainPane; paneLayout -e -cn \\\"single\\\" -ps 1 100 100 $gMainPane;\"\n\t\t\t\t-removeAllPanels\n\t\t\t\t-ap false\n\t\t\t\t\t(localizedPanelLabel(\"Persp View\")) \n\t\t\t\t\t\"modelPanel\"\n"
		+ "\t\t\t\t\t\"$panelName = `modelPanel -unParent -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -docTag \\\"RADRENDER\\\" \\n    -editorChanged \\\"updateModelPanelBar\\\" \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 32768\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1959\\n    -height 1239\\n    -sceneRenderFilter 0\\n    -activeShadingGraph \\\"ballora_animatronic_shadow_rig:rsMaterial1SG,ballora_animatronic_shadow_rig:MAT_ballora,ballora_animatronic_shadow_rig:MAT_ballora\\\" \\n    -activeCustomGeometry \\\"meshShaderball\\\" \\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t\t\"modelPanel -edit -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -docTag \\\"RADRENDER\\\" \\n    -editorChanged \\\"updateModelPanelBar\\\" \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 32768\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1959\\n    -height 1239\\n    -sceneRenderFilter 0\\n    -activeShadingGraph \\\"ballora_animatronic_shadow_rig:rsMaterial1SG,ballora_animatronic_shadow_rig:MAT_ballora,ballora_animatronic_shadow_rig:MAT_ballora\\\" \\n    -activeCustomGeometry \\\"meshShaderball\\\" \\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t$configName;\n\n            setNamedPanelLayout (localizedPanelLabel(\"Current Layout\"));\n        }\n\n        panelHistory -e -clear mainPanelHistory;\n        sceneUIReplacement -clear;\n\t}\n\n\ngrid -spacing 5 -size 12 -divisions 5 -displayAxes yes -displayGridLines yes -displayDivisionLines yes -displayPerspectiveLabels no -displayOrthographicLabels no -displayAxesBold yes -perspectiveLabelPosition axis -orthographicLabelPosition edge;\nviewManip -drawCompass 0 -compassAngle 0 -frontParameters \"\" -homeParameters \"\" -selectionLockParameters \"\";\n}\n");
	setAttr ".st" 3;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "A63F34DF-4E6D-3635-BDB0-46AC4A7B6BFD";
	setAttr ".b" -type "string" "playbackOptions -min 0 -max 100 -ast 0 -aet 200 ";
	setAttr ".st" 6;
select -ne :time1;
	setAttr -av -k on ".cch";
	setAttr -k on ".fzn";
	setAttr -av -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".o" 47;
	setAttr -av -k on ".unw" 47;
	setAttr -av -k on ".etw";
	setAttr -av -k on ".tps";
	setAttr -av -k on ".tms";
select -ne :hardwareRenderingGlobals;
	setAttr -av -k on ".cch";
	setAttr -k on ".fzn";
	setAttr -av -k on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".rm";
	setAttr -k on ".lm";
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr -k on ".hom";
	setAttr -k on ".hodm";
	setAttr -k on ".xry";
	setAttr -k on ".jxr";
	setAttr -k on ".sslt";
	setAttr -k on ".cbr";
	setAttr -k on ".bbr";
	setAttr -av -k on ".mhl";
	setAttr -k on ".cons";
	setAttr -k on ".vac";
	setAttr -av -k on ".hwi";
	setAttr -k on ".csvd";
	setAttr -av -k on ".ta";
	setAttr -av -k on ".tq";
	setAttr -k on ".ts";
	setAttr -av -k on ".etmr";
	setAttr -av -k on ".tmr";
	setAttr -av -k on ".aoon";
	setAttr -av -k on ".aoam";
	setAttr -av -k on ".aora";
	setAttr -k on ".aofr";
	setAttr -av -k on ".aosm";
	setAttr -av -k on ".hff";
	setAttr -av -k on ".hfd";
	setAttr -av -k on ".hfs";
	setAttr -av -k on ".hfe";
	setAttr -av ".hfc";
	setAttr -av -k on ".hfcr";
	setAttr -av -k on ".hfcg";
	setAttr -av -k on ".hfcb";
	setAttr -av -k on ".hfa";
	setAttr -av -k on ".mbe";
	setAttr -k on ".mbt";
	setAttr -av -k on ".mbsof";
	setAttr -k on ".mbsc";
	setAttr -k on ".mbc";
	setAttr -k on ".mbfa";
	setAttr -k on ".mbftb";
	setAttr -k on ".mbftg";
	setAttr -k on ".mbftr";
	setAttr -k on ".mbfta";
	setAttr -k on ".mbfe";
	setAttr -k on ".mbme";
	setAttr -k on ".mbcsx";
	setAttr -k on ".mbcsy";
	setAttr -k on ".mbasx";
	setAttr -k on ".mbasy";
	setAttr -av -k on ".blen";
	setAttr -k on ".blth";
	setAttr -k on ".blfr";
	setAttr -k on ".blfa";
	setAttr -av -k on ".blat";
	setAttr -av -k on ".msaa";
	setAttr -av -k on ".aasc";
	setAttr -k on ".aasq";
	setAttr -k on ".laa";
	setAttr -k on ".fprt" yes;
	setAttr -k on ".rtfm";
select -ne :renderPartition;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".st";
	setAttr -cb on ".an";
	setAttr -cb on ".pt";
select -ne :renderGlobalsList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
select -ne :defaultShaderList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 5 ".s";
select -ne :postProcessList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
	setAttr -k on ".ihi";
select -ne :standardSurface1;
	setAttr ".bc" -type "float3" 0.40000001 0.40000001 0.40000001 ;
	setAttr ".sr" 0.5;
select -ne :initialShadingGroup;
	setAttr -av -k on ".cch";
	setAttr -k on ".fzn";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".bbx";
	setAttr -k on ".vwm";
	setAttr -k on ".tpv";
	setAttr -k on ".uit";
	setAttr -k on ".mwc";
	setAttr -av -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr -k on ".ro" yes;
select -ne :initialParticleSE;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".mwc";
	setAttr -av -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr -k on ".ro" yes;
lockNode -l 0 -lu 1;
select -ne :defaultRenderGlobals;
	addAttr -ci true -h true -sn "dss" -ln "defaultSurfaceShader" -dt "string";
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -av -k on ".macc";
	setAttr -av -k on ".macd";
	setAttr -av -k on ".macq";
	setAttr -av -k on ".mcfr";
	setAttr -cb on ".ifg";
	setAttr -av -k on ".clip";
	setAttr -av -k on ".edm";
	setAttr -av -k on ".edl";
	setAttr -av -cb on ".ren";
	setAttr -av -k on ".esr";
	setAttr -av -k on ".ors";
	setAttr -cb on ".sdf";
	setAttr -av -k on ".outf";
	setAttr -av -cb on ".imfkey";
	setAttr -av -k on ".gama";
	setAttr -av -k on ".exrc";
	setAttr -av -k on ".expt";
	setAttr -av -cb on ".an";
	setAttr -k on ".ar";
	setAttr -av -k on ".fs";
	setAttr -av -k on ".ef";
	setAttr -av -k on ".bfs";
	setAttr -av -k on ".me";
	setAttr -k on ".se";
	setAttr -av -k on ".be";
	setAttr -av -cb on ".ep";
	setAttr -av -k on ".fec";
	setAttr -av -k on ".ofc";
	setAttr -cb on ".ofe";
	setAttr -cb on ".efe";
	setAttr -cb on ".oft";
	setAttr -k on ".umfn";
	setAttr -cb on ".ufe";
	setAttr -av -cb on ".pff";
	setAttr -av -k on ".peie";
	setAttr -av -cb on ".ifp";
	setAttr -k on ".rv";
	setAttr -av -k on ".comp";
	setAttr -av -k on ".cth";
	setAttr -av -k on ".soll";
	setAttr -av -cb on ".sosl";
	setAttr -av -k on ".rd";
	setAttr -av -k on ".lp";
	setAttr -av -k on ".sp";
	setAttr -av -k on ".shs";
	setAttr -av -k on ".lpr";
	setAttr -cb on ".gv";
	setAttr -cb on ".sv";
	setAttr -av -k on ".mm";
	setAttr -av -k on ".npu";
	setAttr -av -k on ".itf";
	setAttr -av -k on ".shp";
	setAttr -cb on ".isp";
	setAttr -av -k on ".uf";
	setAttr -av -k on ".oi";
	setAttr -av -k on ".rut";
	setAttr -av -k on ".mot";
	setAttr -av -k on ".mb";
	setAttr -av -k on ".mbf";
	setAttr -av -k on ".mbso";
	setAttr -av -k on ".mbsc";
	setAttr -av -k on ".afp";
	setAttr -av -k on ".pfb";
	setAttr -av -k on ".pram";
	setAttr -av -k on ".poam";
	setAttr -av -k on ".prlm";
	setAttr -av -k on ".polm";
	setAttr -av -cb on ".prm";
	setAttr -av -cb on ".pom";
	setAttr -cb on ".pfrm";
	setAttr -cb on ".pfom";
	setAttr -av -k on ".bll";
	setAttr -av -k on ".bls";
	setAttr -av -k on ".smv";
	setAttr -av -k on ".ubc";
	setAttr -av -k on ".mbc";
	setAttr -cb on ".mbt";
	setAttr -av -k on ".udbx";
	setAttr -av -k on ".smc";
	setAttr -av -k on ".kmv";
	setAttr -cb on ".isl";
	setAttr -cb on ".ism";
	setAttr -cb on ".imb";
	setAttr -av -k on ".rlen";
	setAttr -av -k on ".frts";
	setAttr -av -k on ".tlwd";
	setAttr -av -k on ".tlht";
	setAttr -av -k on ".jfc";
	setAttr -cb on ".rsb";
	setAttr -av -k on ".ope";
	setAttr -av -k on ".oppf";
	setAttr -av -k on ".rcp";
	setAttr -av -k on ".icp";
	setAttr -av -k on ".ocp";
	setAttr -cb on ".hbl";
	setAttr ".dss" -type "string" "lambert1";
select -ne :defaultResolution;
	setAttr -av -k on ".cch";
	setAttr -av -k on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -k on ".bnm";
	setAttr -av -k on ".w";
	setAttr -av -k on ".h";
	setAttr -av -k on ".pa" 1;
	setAttr -av -k on ".al";
	setAttr -av -k on ".dar";
	setAttr -av -k on ".ldar";
	setAttr -av -k on ".dpi";
	setAttr -av -k on ".off";
	setAttr -av -k on ".fld";
	setAttr -av -k on ".zsl";
	setAttr -av -k on ".isu";
	setAttr -av -k on ".pdu";
select -ne :defaultColorMgtGlobals;
	setAttr ".cfe" yes;
	setAttr ".cfp" -type "string" "<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio";
	setAttr ".vtn" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".vn" -type "string" "ACES 1.0 SDR-video";
	setAttr ".dn" -type "string" "sRGB";
	setAttr ".wsn" -type "string" "ACEScg";
	setAttr ".otn" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".potn" -type "string" "ACES 1.0 SDR-video (sRGB)";
select -ne :hardwareRenderGlobals;
	setAttr -av -k on ".cch";
	setAttr -av -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -av -k off -cb on ".ctrs" 256;
	setAttr -av -k off -cb on ".btrs" 512;
	setAttr -av -k off -cb on ".fbfm";
	setAttr -av -k off -cb on ".ehql";
	setAttr -av -k off -cb on ".eams";
	setAttr -av -k off -cb on ".eeaa";
	setAttr -av -k off -cb on ".engm";
	setAttr -av -k off -cb on ".mes";
	setAttr -av -k off -cb on ".emb";
	setAttr -av -k off -cb on ".mbbf";
	setAttr -av -k off -cb on ".mbs";
	setAttr -av -k off -cb on ".trm";
	setAttr -av -k off -cb on ".tshc";
	setAttr -av -k off -cb on ".enpt";
	setAttr -av -k off -cb on ".clmt";
	setAttr -av -k off -cb on ".tcov";
	setAttr -av -k off -cb on ".lith";
	setAttr -av -k off -cb on ".sobc";
	setAttr -av -k off -cb on ".cuth";
	setAttr -av -k off -cb on ".hgcd";
	setAttr -av -k off -cb on ".hgci";
	setAttr -av -k off -cb on ".mgcs";
	setAttr -av -k off -cb on ".twa";
	setAttr -av -k off -cb on ".twz";
	setAttr -av -k on ".hwcc";
	setAttr -av -k on ".hwdp";
	setAttr -av -k on ".hwql";
	setAttr -av -k on ".hwfr";
	setAttr -av -k on ".soll";
	setAttr -av -k on ".sosl";
	setAttr -av -k on ".bswa";
	setAttr -av -k on ".shml";
	setAttr -av -k on ".hwel";
connectAttr "guide.globalScale" "guide.sx" -l on;
connectAttr "guide.globalScale" "guide.sy" -l on;
connectAttr "guide.globalScale" "guide.sz" -l on;
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
// End of Creature.ma
