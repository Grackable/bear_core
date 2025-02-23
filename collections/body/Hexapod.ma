//Maya ASCII 2022 scene
//Name: Hexapod.ma
//Last modified: Fri, Mar 22, 2024 02:47:03 PM
//Codeset: 1252
requires maya "2022";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2022";
fileInfo "version" "2022";
fileInfo "cutIdentifier" "202108111415-612a77abf4";
fileInfo "osv" "Windows 10 Home v2009 (Build: 22631)";
fileInfo "UUID" "F0952264-4A26-799A-AF03-8C9C1E05B1BC";
createNode transform -s -n "persp";
	rename -uid "41936871-47CA-3649-B18D-5D9C3FF7ADF9";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 29.107614712089596 21.830711034067196 29.107614712089596 ;
	setAttr ".r" -type "double3" -27.938352729602379 44.999999999999972 -5.172681101354183e-14 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "A87C1D39-49FF-55C1-9530-8EA25FC41BBC";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 46.594918314209451;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "AC28E5E2-40D3-D967-6867-F3A1E2518E0C";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -90 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "8A2695B7-4638-87D8-0A04-AB873F515E91";
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
	rename -uid "C333AF39-46F5-565E-E273-4898711119E9";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "083176C3-4B76-E871-F735-5799F4D300EC";
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
	rename -uid "20795D6A-4F51-FA3E-F395-389C64A2889E";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 90 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "65059816-4EE8-1848-7034-32AE2778F3AF";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "guide";
	rename -uid "D9F6E1EF-4EAF-6306-8B4C-C093ACCE47A2";
	addAttr -ci true -sn "globalNamingConvention" -ln "globalNamingConvention" -dt "string";
	addAttr -ci true -sn "geometryGroup" -ln "geometryGroup" -dt "string";
	addAttr -ci true -sn "geometryToken" -ln "geometryToken" -dt "string";
	addAttr -ci true -sn "guidePivotToken" -ln "guidePivotToken" -dt "string";
	addAttr -ci true -sn "guideShapeToken" -ln "guideShapeToken" -dt "string";
	addAttr -ci true -sn "spaceToken" -ln "spaceToken" -dt "string";
	addAttr -ci true -sn "controlToken" -ln "controlToken" -dt "string";
	addAttr -ci true -sn "skinJointToken" -ln "skinJointToken" -dt "string";
	addAttr -ci true -sn "leftSideToken" -ln "leftSideToken" -dt "string";
	addAttr -ci true -sn "rightSideToken" -ln "rightSideToken" -dt "string";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "guideRoot" -ln "guideRoot" -dt "string";
	addAttr -ci true -sn "rigRoot" -ln "rigRoot" -dt "string";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr -l on ".globalNamingConvention" -type "string" "component, side, element, indices, specific, nodeType";
	setAttr -l on ".geometryGroup" -type "string" "geometry";
	setAttr -l on ".geometryToken" -type "string" "geo";
	setAttr -l on ".guidePivotToken" -type "string" "guidePivot";
	setAttr -l on ".guideShapeToken" -type "string" "guideShape";
	setAttr -l on ".spaceToken" -type "string" "offset";
	setAttr -l on ".controlToken" -type "string" "control";
	setAttr -l on ".skinJointToken" -type "string" "skin";
	setAttr -l on ".leftSideToken" -type "string" "L";
	setAttr -l on ".rightSideToken" -type "string" "R";
	setAttr -l on -k on ".namingConvention" -type "string" "nodeType";
	setAttr -l on -k on ".globalScale";
	setAttr -l on -k on ".guideRoot" -type "string" "guide";
	setAttr -l on -k on ".rigRoot" -type "string" "rig";
createNode transform -n "hexapod_guide" -p "guide";
	rename -uid "A08893DF-4A7E-0015-ED38-DD86E1976511";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".readyForRigBuild" yes;
	setAttr -l on -k on ".globalScale";
	setAttr -l on ".namingConvention" -type "string" "component, nodeType";
	setAttr -l on ".bearVersion" -type "string" "0.910";
	setAttr -l on ".componentType" -type "string" "Collection";
	setAttr ".name" -type "string" "hexapod";
createNode transform -n "root_guide" -p "hexapod_guide";
	rename -uid "29F72BE0-4B6E-AFA4-8D7E-D49EF8004CA1";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "side" -ln "side" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "hasGlobalScale" -ln "hasGlobalScale" -dt "string";
	addAttr -ci true -sn "hasPlacement" -ln "hasPlacement" -dt "string";
	addAttr -ci true -sn "hasMain" -ln "hasMain" -dt "string";
	addAttr -ci true -sn "hasJoint" -ln "hasJoint" -dt "string";
	addAttr -ci true -sn "displaySwitch" -ln "displaySwitch" -dt "string";
	addAttr -ci true -sn "output_root_main_pivot_skin" -ln "output_root_main_pivot_skin" 
		-dt "string";
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
	setAttr -l on ".componentType" -type "string" "Root";
	setAttr ".name" -type "string" "root";
	setAttr ".parentNode" -type "string" "None";
	setAttr ".hasGlobalScale" -type "string" "True";
	setAttr ".hasPlacement" -type "string" "True";
	setAttr ".hasMain" -type "string" "True";
	setAttr ".hasJoint" -type "string" "True";
	setAttr ".displaySwitch" -type "string" "displaySwitch";
	setAttr -l on ".output_root_main_pivot_skin" -type "string" "root_main_pivot_skin";
createNode transform -n "body_guide" -p "hexapod_guide";
	rename -uid "3A073D64-404A-DFB7-A5B3-73B6CFB1D2C4";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "side" -ln "side" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "element" -ln "element" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "parentType" -ln "parentType" -dt "string";
	addAttr -ci true -sn "parentOrientNode" -ln "parentOrientNode" -dt "string";
	addAttr -ci true -sn "count" -ln "count" -dt "string";
	addAttr -ci true -sn "chainParented" -ln "chainParented" -dt "string";
	addAttr -ci true -sn "hasJoints" -ln "hasJoints" -dt "string";
	addAttr -ci true -sn "inheritScale" -ln "inheritScale" -dt "string";
	addAttr -ci true -sn "hasSecondaryControl" -ln "hasSecondaryControl" -dt "string";
	addAttr -ci true -sn "displaySwitch" -ln "displaySwitch" -dt "string";
	addAttr -ci true -sn "output_body_skin" -ln "output_body_skin" -dt "string";
	setAttr ".t" -type "double3" 0 60 40 ;
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
	setAttr -l on ".componentType" -type "string" "Single";
	setAttr ".name" -type "string" "body";
	setAttr ".element" -type "string" "None";
	setAttr ".parentNode" -type "string" "root_main_control";
	setAttr ".parentType" -type "string" "None";
	setAttr ".parentOrientNode" -type "string" "None";
	setAttr ".count" -type "string" "1";
	setAttr ".chainParented" -type "string" "False";
	setAttr ".hasJoints" -type "string" "True";
	setAttr ".inheritScale" -type "string" "True";
	setAttr ".hasSecondaryControl" -type "string" "False";
	setAttr ".displaySwitch" -type "string" "bodyDisplaySwitch";
	setAttr -l on ".output_body_skin" -type "string" "body_skin";
createNode transform -n "tail_guide" -p "hexapod_guide";
	rename -uid "D39FEA4B-49E5-1057-B27B-2F9F82F741E6";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "side" -ln "side" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "element" -ln "element" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "parentType" -ln "parentType" -dt "string";
	addAttr -ci true -sn "parentOrientNode" -ln "parentOrientNode" -dt "string";
	addAttr -ci true -sn "count" -ln "count" -dt "string";
	addAttr -ci true -sn "chainParented" -ln "chainParented" -dt "string";
	addAttr -ci true -sn "hasJoints" -ln "hasJoints" -dt "string";
	addAttr -ci true -sn "inheritScale" -ln "inheritScale" -dt "string";
	addAttr -ci true -sn "hasSecondaryControl" -ln "hasSecondaryControl" -dt "string";
	addAttr -ci true -sn "displaySwitch" -ln "displaySwitch" -dt "string";
	addAttr -ci true -sn "output_tail_01_skin" -ln "output_tail_01_skin" -dt "string";
	addAttr -ci true -sn "output_tail_02_skin" -ln "output_tail_02_skin" -dt "string";
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
	setAttr -l on ".componentType" -type "string" "Single";
	setAttr ".name" -type "string" "tail";
	setAttr ".element" -type "string" "None";
	setAttr ".parentNode" -type "string" "None";
	setAttr ".parentType" -type "string" "None";
	setAttr ".parentOrientNode" -type "string" "None";
	setAttr ".count" -type "string" "2";
	setAttr ".chainParented" -type "string" "True";
	setAttr ".hasJoints" -type "string" "True";
	setAttr ".inheritScale" -type "string" "True";
	setAttr ".hasSecondaryControl" -type "string" "False";
	setAttr ".displaySwitch" -type "string" "bodyDisplaySwitch";
	setAttr -l on ".output_tail_01_skin" -type "string" "tail_01_skin";
	setAttr -l on ".output_tail_02_skin" -type "string" "tail_02_skin";
createNode transform -n "head_guide" -p "hexapod_guide";
	rename -uid "99DA0B43-46DF-F137-E523-658B7A62CC7C";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "side" -ln "side" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "element" -ln "element" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "parentType" -ln "parentType" -dt "string";
	addAttr -ci true -sn "parentOrientNode" -ln "parentOrientNode" -dt "string";
	addAttr -ci true -sn "count" -ln "count" -dt "string";
	addAttr -ci true -sn "chainParented" -ln "chainParented" -dt "string";
	addAttr -ci true -sn "hasJoints" -ln "hasJoints" -dt "string";
	addAttr -ci true -sn "inheritScale" -ln "inheritScale" -dt "string";
	addAttr -ci true -sn "hasSecondaryControl" -ln "hasSecondaryControl" -dt "string";
	addAttr -ci true -sn "displaySwitch" -ln "displaySwitch" -dt "string";
	addAttr -ci true -sn "output_head_skin" -ln "output_head_skin" -dt "string";
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
	setAttr -l on ".componentType" -type "string" "Single";
	setAttr ".name" -type "string" "head";
	setAttr ".element" -type "string" "None";
	setAttr ".parentNode" -type "string" "None";
	setAttr ".parentType" -type "string" "None";
	setAttr ".parentOrientNode" -type "string" "None";
	setAttr ".count" -type "string" "1";
	setAttr ".chainParented" -type "string" "False";
	setAttr ".hasJoints" -type "string" "True";
	setAttr ".inheritScale" -type "string" "True";
	setAttr ".hasSecondaryControl" -type "string" "False";
	setAttr ".displaySwitch" -type "string" "bodyDisplaySwitch";
	setAttr -l on ".output_head_skin" -type "string" "head_skin";
createNode transform -n "legA_L_guide" -p "hexapod_guide";
	rename -uid "CE040266-497F-D838-61C3-0CB9BDA68F86";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "side" -ln "side" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "topName" -ln "topName" -dt "string";
	addAttr -ci true -sn "upperName" -ln "upperName" -dt "string";
	addAttr -ci true -sn "midName" -ln "midName" -dt "string";
	addAttr -ci true -sn "lowerName" -ln "lowerName" -dt "string";
	addAttr -ci true -sn "endName" -ln "endName" -dt "string";
	addAttr -ci true -sn "digitsName" -ln "digitsName" -dt "string";
	addAttr -ci true -sn "upperTwistCount" -ln "upperTwistCount" -dt "string";
	addAttr -ci true -sn "lowerTwistCount" -ln "lowerTwistCount" -dt "string";
	addAttr -ci true -sn "ankleTwistCount" -ln "ankleTwistCount" -dt "string";
	addAttr -ci true -sn "digits" -ln "digits" -dt "string";
	addAttr -ci true -sn "digitHasBase" -ln "digitHasBase" -dt "string";
	addAttr -ci true -sn "digitsNumberedNaming" -ln "digitsNumberedNaming" -dt "string";
	addAttr -ci true -sn "hasTopDeformJoint" -ln "hasTopDeformJoint" -dt "string";
	addAttr -ci true -sn "hasMidDeformJoint" -ln "hasMidDeformJoint" -dt "string";
	addAttr -ci true -sn "hasKnuckleDeformJoint" -ln "hasKnuckleDeformJoint" -dt "string";
	addAttr -ci true -sn "hasStretch" -ln "hasStretch" -dt "string";
	addAttr -ci true -sn "hasMidControl" -ln "hasMidControl" -dt "string";
	addAttr -ci true -sn "hasSmoothIk" -ln "hasSmoothIk" -dt "string";
	addAttr -ci true -sn "hasPlatform" -ln "hasPlatform" -dt "string";
	addAttr -ci true -sn "spaceNodes" -ln "spaceNodes" -dt "string";
	addAttr -ci true -sn "spaceNames" -ln "spaceNames" -dt "string";
	addAttr -ci true -sn "quadruped" -ln "quadruped" -dt "string";
	addAttr -ci true -sn "invertKnee" -ln "invertKnee" -dt "string";
	addAttr -ci true -sn "shoulderHasLegInfluence" -ln "shoulderHasLegInfluence" -dt "string";
	addAttr -ci true -sn "defaultAlignment" -ln "defaultAlignment" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "displaySwitch" -ln "displaySwitch" -dt "string";
	addAttr -ci true -sn "output_legA_L_ankle_guidePivot" -ln "output_legA_L_ankle_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legA_L_toes_guidePivot" -ln "output_legA_L_toes_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legA_L_shoulder_guidePivot" -ln "output_legA_L_shoulder_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legA_L_upper_01_skin" -ln "output_legA_L_upper_01_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_L_upper_02_skin" -ln "output_legA_L_upper_02_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_L_upper_03_skin" -ln "output_legA_L_upper_03_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_L_upper_04_skin" -ln "output_legA_L_upper_04_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_L_upper_05_skin" -ln "output_legA_L_upper_05_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_L_lower_01_skin" -ln "output_legA_L_lower_01_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_L_lower_02_skin" -ln "output_legA_L_lower_02_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_L_lower_03_skin" -ln "output_legA_L_lower_03_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_L_lower_04_skin" -ln "output_legA_L_lower_04_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_L_lower_05_skin" -ln "output_legA_L_lower_05_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_L_component" -ln "output_legA_L_component" -dt "string";
	addAttr -ci true -sn "output_legA_L_parent_loc" -ln "output_legA_L_parent_loc" -dt "string";
	addAttr -ci true -sn "output_legA_L_upper_guidePivot" -ln "output_legA_L_upper_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legA_L_lower_guidePivot" -ln "output_legA_L_lower_guidePivot" 
		-dt "string";
	setAttr ".t" -type "double3" 20 0 40 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".readyForRigBuild" yes;
	setAttr -l on ".namingConvention" -type "string" "component, side, nodeType";
	setAttr -l on ".side" -type "string" "L";
	setAttr -l on ".bearVersion" -type "string" "0.25.8";
	setAttr -l on ".componentType" -type "string" "Leg";
	setAttr ".name" -type "string" "legA";
	setAttr ".topName" -type "string" "shoulder";
	setAttr ".upperName" -type "string" "upper";
	setAttr ".midName" -type "string" "knee";
	setAttr ".lowerName" -type "string" "lower";
	setAttr ".endName" -type "string" "ankle";
	setAttr ".digitsName" -type "string" "toes";
	setAttr ".upperTwistCount" -type "string" "5";
	setAttr ".lowerTwistCount" -type "string" "5";
	setAttr ".ankleTwistCount" -type "string" "5";
	setAttr ".digits" -type "string" "None";
	setAttr ".digitHasBase" -type "string" "";
	setAttr ".digitsNumberedNaming" -type "string" "True";
	setAttr ".hasTopDeformJoint" -type "string" "True";
	setAttr ".hasMidDeformJoint" -type "string" "True";
	setAttr ".hasKnuckleDeformJoint" -type "string" "True";
	setAttr ".hasStretch" -type "string" "True";
	setAttr ".hasMidControl" -type "string" "True";
	setAttr ".hasSmoothIk" -type "string" "True";
	setAttr ".hasPlatform" -type "string" "False";
	setAttr ".spaceNodes" -type "string" "root_control, root_placement_control, root_main_pivot_control, body_control";
	setAttr ".spaceNames" -type "string" "root, placement, main, body";
	setAttr ".quadruped" -type "string" "False";
	setAttr ".invertKnee" -type "string" "False";
	setAttr ".shoulderHasLegInfluence" -type "string" "False";
	setAttr ".defaultAlignment" -type "string" "biped";
	setAttr ".parentNode" -type "string" "body_control";
	setAttr ".displaySwitch" -type "string" "bodyDisplaySwitch";
	setAttr -l on ".output_legA_L_ankle_guidePivot" -type "string" "legA_L_ankle_guidePivot";
	setAttr -l on ".output_legA_L_toes_guidePivot" -type "string" "legA_L_toes_guidePivot";
	setAttr -l on ".output_legA_L_shoulder_guidePivot" -type "string" "legA_L_shoulder_guidePivot";
	setAttr -l on ".output_legA_L_upper_01_skin" -type "string" "legA_L_upper_01_skin";
	setAttr -l on ".output_legA_L_upper_02_skin" -type "string" "legA_L_upper_02_skin";
	setAttr -l on ".output_legA_L_upper_03_skin" -type "string" "legA_L_upper_03_skin";
	setAttr -l on ".output_legA_L_upper_04_skin" -type "string" "legA_L_upper_04_skin";
	setAttr -l on ".output_legA_L_upper_05_skin" -type "string" "legA_L_upper_05_skin";
	setAttr -l on ".output_legA_L_lower_01_skin" -type "string" "legA_L_lower_01_skin";
	setAttr -l on ".output_legA_L_lower_02_skin" -type "string" "legA_L_lower_02_skin";
	setAttr -l on ".output_legA_L_lower_03_skin" -type "string" "legA_L_lower_03_skin";
	setAttr -l on ".output_legA_L_lower_04_skin" -type "string" "legA_L_lower_04_skin";
	setAttr -l on ".output_legA_L_lower_05_skin" -type "string" "legA_L_lower_05_skin";
	setAttr -l on ".output_legA_L_component" -type "string" "legA_L_guide";
	setAttr -l on ".output_legA_L_parent_loc" -type "string" "legA_L_parent_loc";
	setAttr -l on ".output_legA_L_upper_guidePivot" -type "string" "legA_L_upper_guidePivot";
	setAttr -l on ".output_legA_L_lower_guidePivot" -type "string" "legA_L_lower_guidePivot";
createNode transform -n "legA_R_guide" -p "hexapod_guide";
	rename -uid "2654326A-4F72-C9D9-23F9-CC80D6B703B8";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "side" -ln "side" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "topName" -ln "topName" -dt "string";
	addAttr -ci true -sn "upperName" -ln "upperName" -dt "string";
	addAttr -ci true -sn "midName" -ln "midName" -dt "string";
	addAttr -ci true -sn "lowerName" -ln "lowerName" -dt "string";
	addAttr -ci true -sn "endName" -ln "endName" -dt "string";
	addAttr -ci true -sn "digitsName" -ln "digitsName" -dt "string";
	addAttr -ci true -sn "upperTwistCount" -ln "upperTwistCount" -dt "string";
	addAttr -ci true -sn "lowerTwistCount" -ln "lowerTwistCount" -dt "string";
	addAttr -ci true -sn "ankleTwistCount" -ln "ankleTwistCount" -dt "string";
	addAttr -ci true -sn "digits" -ln "digits" -dt "string";
	addAttr -ci true -sn "digitHasBase" -ln "digitHasBase" -dt "string";
	addAttr -ci true -sn "digitsNumberedNaming" -ln "digitsNumberedNaming" -dt "string";
	addAttr -ci true -sn "hasTopDeformJoint" -ln "hasTopDeformJoint" -dt "string";
	addAttr -ci true -sn "hasMidDeformJoint" -ln "hasMidDeformJoint" -dt "string";
	addAttr -ci true -sn "hasKnuckleDeformJoint" -ln "hasKnuckleDeformJoint" -dt "string";
	addAttr -ci true -sn "hasStretch" -ln "hasStretch" -dt "string";
	addAttr -ci true -sn "hasMidControl" -ln "hasMidControl" -dt "string";
	addAttr -ci true -sn "hasSmoothIk" -ln "hasSmoothIk" -dt "string";
	addAttr -ci true -sn "hasPlatform" -ln "hasPlatform" -dt "string";
	addAttr -ci true -sn "spaceNodes" -ln "spaceNodes" -dt "string";
	addAttr -ci true -sn "spaceNames" -ln "spaceNames" -dt "string";
	addAttr -ci true -sn "quadruped" -ln "quadruped" -dt "string";
	addAttr -ci true -sn "invertKnee" -ln "invertKnee" -dt "string";
	addAttr -ci true -sn "shoulderHasLegInfluence" -ln "shoulderHasLegInfluence" -dt "string";
	addAttr -ci true -sn "defaultAlignment" -ln "defaultAlignment" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "displaySwitch" -ln "displaySwitch" -dt "string";
	addAttr -ci true -sn "output_legA_R_ankle_guidePivot" -ln "output_legA_R_ankle_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legA_R_toes_guidePivot" -ln "output_legA_R_toes_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legA_R_shoulder_guidePivot" -ln "output_legA_R_shoulder_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legA_R_upper_01_skin" -ln "output_legA_R_upper_01_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_R_upper_02_skin" -ln "output_legA_R_upper_02_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_R_upper_03_skin" -ln "output_legA_R_upper_03_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_R_upper_04_skin" -ln "output_legA_R_upper_04_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_R_upper_05_skin" -ln "output_legA_R_upper_05_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_R_lower_01_skin" -ln "output_legA_R_lower_01_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_R_lower_02_skin" -ln "output_legA_R_lower_02_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_R_lower_03_skin" -ln "output_legA_R_lower_03_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_R_lower_04_skin" -ln "output_legA_R_lower_04_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_R_lower_05_skin" -ln "output_legA_R_lower_05_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legA_R_component" -ln "output_legA_R_component" -dt "string";
	addAttr -ci true -sn "output_legA_R_parent_loc" -ln "output_legA_R_parent_loc" -dt "string";
	addAttr -ci true -sn "output_legA_R_upper_guidePivot" -ln "output_legA_R_upper_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legA_R_lower_guidePivot" -ln "output_legA_R_lower_guidePivot" 
		-dt "string";
	setAttr ".t" -type "double3" -20 0 40 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".readyForRigBuild" yes;
	setAttr -l on ".namingConvention" -type "string" "component, side, nodeType";
	setAttr -l on ".side" -type "string" "R";
	setAttr -l on ".bearVersion" -type "string" "0.25.8";
	setAttr -l on ".componentType" -type "string" "Leg";
	setAttr ".name" -type "string" "legA";
	setAttr ".topName" -type "string" "shoulder";
	setAttr ".upperName" -type "string" "upper";
	setAttr ".midName" -type "string" "knee";
	setAttr ".lowerName" -type "string" "lower";
	setAttr ".endName" -type "string" "ankle";
	setAttr ".digitsName" -type "string" "toes";
	setAttr ".upperTwistCount" -type "string" "5";
	setAttr ".lowerTwistCount" -type "string" "5";
	setAttr ".ankleTwistCount" -type "string" "5";
	setAttr ".digits" -type "string" "None";
	setAttr ".digitHasBase" -type "string" "";
	setAttr ".digitsNumberedNaming" -type "string" "True";
	setAttr ".hasTopDeformJoint" -type "string" "True";
	setAttr ".hasMidDeformJoint" -type "string" "True";
	setAttr ".hasKnuckleDeformJoint" -type "string" "True";
	setAttr ".hasStretch" -type "string" "True";
	setAttr ".hasMidControl" -type "string" "True";
	setAttr ".hasSmoothIk" -type "string" "True";
	setAttr ".hasPlatform" -type "string" "False";
	setAttr ".spaceNodes" -type "string" "root_control, root_placement_control, root_main_pivot_control, body_control";
	setAttr ".spaceNames" -type "string" "root, placement, main, body";
	setAttr ".quadruped" -type "string" "False";
	setAttr ".invertKnee" -type "string" "False";
	setAttr ".shoulderHasLegInfluence" -type "string" "False";
	setAttr ".defaultAlignment" -type "string" "biped";
	setAttr ".parentNode" -type "string" "body_control";
	setAttr ".displaySwitch" -type "string" "bodyDisplaySwitch";
	setAttr -l on ".output_legA_R_ankle_guidePivot" -type "string" "legA_R_ankle_guidePivot";
	setAttr -l on ".output_legA_R_toes_guidePivot" -type "string" "legA_R_toes_guidePivot";
	setAttr -l on ".output_legA_R_shoulder_guidePivot" -type "string" "legA_R_shoulder_guidePivot";
	setAttr -l on ".output_legA_R_upper_01_skin" -type "string" "legA_R_upper_01_skin";
	setAttr -l on ".output_legA_R_upper_02_skin" -type "string" "legA_R_upper_02_skin";
	setAttr -l on ".output_legA_R_upper_03_skin" -type "string" "legA_R_upper_03_skin";
	setAttr -l on ".output_legA_R_upper_04_skin" -type "string" "legA_R_upper_04_skin";
	setAttr -l on ".output_legA_R_upper_05_skin" -type "string" "legA_R_upper_05_skin";
	setAttr -l on ".output_legA_R_lower_01_skin" -type "string" "legA_R_lower_01_skin";
	setAttr -l on ".output_legA_R_lower_02_skin" -type "string" "legA_R_lower_02_skin";
	setAttr -l on ".output_legA_R_lower_03_skin" -type "string" "legA_R_lower_03_skin";
	setAttr -l on ".output_legA_R_lower_04_skin" -type "string" "legA_R_lower_04_skin";
	setAttr -l on ".output_legA_R_lower_05_skin" -type "string" "legA_R_lower_05_skin";
	setAttr -l on ".output_legA_R_component" -type "string" "legA_R_guide";
	setAttr -l on ".output_legA_R_parent_loc" -type "string" "legA_R_parent_loc";
	setAttr -l on ".output_legA_R_upper_guidePivot" -type "string" "legA_R_upper_guidePivot";
	setAttr -l on ".output_legA_R_lower_guidePivot" -type "string" "legA_R_lower_guidePivot";
createNode transform -n "legB_L_guide" -p "hexapod_guide";
	rename -uid "B156F0F7-4FEE-0812-FA09-1CA361A14917";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "side" -ln "side" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "topName" -ln "topName" -dt "string";
	addAttr -ci true -sn "upperName" -ln "upperName" -dt "string";
	addAttr -ci true -sn "midName" -ln "midName" -dt "string";
	addAttr -ci true -sn "lowerName" -ln "lowerName" -dt "string";
	addAttr -ci true -sn "endName" -ln "endName" -dt "string";
	addAttr -ci true -sn "digitsName" -ln "digitsName" -dt "string";
	addAttr -ci true -sn "upperTwistCount" -ln "upperTwistCount" -dt "string";
	addAttr -ci true -sn "lowerTwistCount" -ln "lowerTwistCount" -dt "string";
	addAttr -ci true -sn "ankleTwistCount" -ln "ankleTwistCount" -dt "string";
	addAttr -ci true -sn "digits" -ln "digits" -dt "string";
	addAttr -ci true -sn "digitHasBase" -ln "digitHasBase" -dt "string";
	addAttr -ci true -sn "digitsNumberedNaming" -ln "digitsNumberedNaming" -dt "string";
	addAttr -ci true -sn "hasTopDeformJoint" -ln "hasTopDeformJoint" -dt "string";
	addAttr -ci true -sn "hasMidDeformJoint" -ln "hasMidDeformJoint" -dt "string";
	addAttr -ci true -sn "hasKnuckleDeformJoint" -ln "hasKnuckleDeformJoint" -dt "string";
	addAttr -ci true -sn "hasStretch" -ln "hasStretch" -dt "string";
	addAttr -ci true -sn "hasMidControl" -ln "hasMidControl" -dt "string";
	addAttr -ci true -sn "hasSmoothIk" -ln "hasSmoothIk" -dt "string";
	addAttr -ci true -sn "hasPlatform" -ln "hasPlatform" -dt "string";
	addAttr -ci true -sn "spaceNodes" -ln "spaceNodes" -dt "string";
	addAttr -ci true -sn "spaceNames" -ln "spaceNames" -dt "string";
	addAttr -ci true -sn "quadruped" -ln "quadruped" -dt "string";
	addAttr -ci true -sn "invertKnee" -ln "invertKnee" -dt "string";
	addAttr -ci true -sn "shoulderHasLegInfluence" -ln "shoulderHasLegInfluence" -dt "string";
	addAttr -ci true -sn "defaultAlignment" -ln "defaultAlignment" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "displaySwitch" -ln "displaySwitch" -dt "string";
	addAttr -ci true -sn "output_legB_L_ankle_guidePivot" -ln "output_legB_L_ankle_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legB_L_toes_guidePivot" -ln "output_legB_L_toes_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legB_L_shoulder_guidePivot" -ln "output_legB_L_shoulder_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legB_L_upper_01_skin" -ln "output_legB_L_upper_01_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_L_upper_02_skin" -ln "output_legB_L_upper_02_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_L_upper_03_skin" -ln "output_legB_L_upper_03_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_L_upper_04_skin" -ln "output_legB_L_upper_04_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_L_upper_05_skin" -ln "output_legB_L_upper_05_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_L_lower_01_skin" -ln "output_legB_L_lower_01_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_L_lower_02_skin" -ln "output_legB_L_lower_02_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_L_lower_03_skin" -ln "output_legB_L_lower_03_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_L_lower_04_skin" -ln "output_legB_L_lower_04_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_L_lower_05_skin" -ln "output_legB_L_lower_05_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_L_component" -ln "output_legB_L_component" -dt "string";
	addAttr -ci true -sn "output_legB_L_parent_loc" -ln "output_legB_L_parent_loc" -dt "string";
	addAttr -ci true -sn "output_legB_L_upper_guidePivot" -ln "output_legB_L_upper_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legB_L_lower_guidePivot" -ln "output_legB_L_lower_guidePivot" 
		-dt "string";
	setAttr ".t" -type "double3" 20 0 0 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".readyForRigBuild" yes;
	setAttr -l on ".namingConvention" -type "string" "component, side, nodeType";
	setAttr -l on ".side" -type "string" "L";
	setAttr -l on ".bearVersion" -type "string" "0.25.8";
	setAttr -l on ".componentType" -type "string" "Leg";
	setAttr ".name" -type "string" "legB";
	setAttr ".topName" -type "string" "shoulder";
	setAttr ".upperName" -type "string" "upper";
	setAttr ".midName" -type "string" "knee";
	setAttr ".lowerName" -type "string" "lower";
	setAttr ".endName" -type "string" "ankle";
	setAttr ".digitsName" -type "string" "toes";
	setAttr ".upperTwistCount" -type "string" "5";
	setAttr ".lowerTwistCount" -type "string" "5";
	setAttr ".ankleTwistCount" -type "string" "5";
	setAttr ".digits" -type "string" "None";
	setAttr ".digitHasBase" -type "string" "False, False, False, False, False";
	setAttr ".digitsNumberedNaming" -type "string" "True";
	setAttr ".hasTopDeformJoint" -type "string" "True";
	setAttr ".hasMidDeformJoint" -type "string" "True";
	setAttr ".hasKnuckleDeformJoint" -type "string" "True";
	setAttr ".hasStretch" -type "string" "True";
	setAttr ".hasMidControl" -type "string" "True";
	setAttr ".hasSmoothIk" -type "string" "True";
	setAttr ".hasPlatform" -type "string" "False";
	setAttr ".spaceNodes" -type "string" "root_control, root_placement_control, root_main_pivot_control, body_control";
	setAttr ".spaceNames" -type "string" "root, placement, main, body";
	setAttr ".quadruped" -type "string" "False";
	setAttr ".invertKnee" -type "string" "True";
	setAttr ".shoulderHasLegInfluence" -type "string" "False";
	setAttr ".defaultAlignment" -type "string" "biped";
	setAttr ".parentNode" -type "string" "tail_01_control";
	setAttr ".displaySwitch" -type "string" "bodyDisplaySwitch";
	setAttr -l on ".output_legB_L_ankle_guidePivot" -type "string" "legB_L_ankle_guidePivot";
	setAttr -l on ".output_legB_L_toes_guidePivot" -type "string" "legB_L_toes_guidePivot";
	setAttr -l on ".output_legB_L_shoulder_guidePivot" -type "string" "legB_L_shoulder_guidePivot";
	setAttr -l on ".output_legB_L_upper_01_skin" -type "string" "legB_L_upper_01_skin";
	setAttr -l on ".output_legB_L_upper_02_skin" -type "string" "legB_L_upper_02_skin";
	setAttr -l on ".output_legB_L_upper_03_skin" -type "string" "legB_L_upper_03_skin";
	setAttr -l on ".output_legB_L_upper_04_skin" -type "string" "legB_L_upper_04_skin";
	setAttr -l on ".output_legB_L_upper_05_skin" -type "string" "legB_L_upper_05_skin";
	setAttr -l on ".output_legB_L_lower_01_skin" -type "string" "legB_L_lower_01_skin";
	setAttr -l on ".output_legB_L_lower_02_skin" -type "string" "legB_L_lower_02_skin";
	setAttr -l on ".output_legB_L_lower_03_skin" -type "string" "legB_L_lower_03_skin";
	setAttr -l on ".output_legB_L_lower_04_skin" -type "string" "legB_L_lower_04_skin";
	setAttr -l on ".output_legB_L_lower_05_skin" -type "string" "legB_L_lower_05_skin";
	setAttr -l on ".output_legB_L_component" -type "string" "legB_L_guide";
	setAttr -l on ".output_legB_L_parent_loc" -type "string" "legB_L_parent_loc";
	setAttr -l on ".output_legB_L_upper_guidePivot" -type "string" "legB_L_upper_guidePivot";
	setAttr -l on ".output_legB_L_lower_guidePivot" -type "string" "legB_L_lower_guidePivot";
createNode transform -n "legB_R_guide" -p "hexapod_guide";
	rename -uid "8361FA80-4347-7F4F-14C5-6CAAE6ECF8B4";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "side" -ln "side" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "topName" -ln "topName" -dt "string";
	addAttr -ci true -sn "upperName" -ln "upperName" -dt "string";
	addAttr -ci true -sn "midName" -ln "midName" -dt "string";
	addAttr -ci true -sn "lowerName" -ln "lowerName" -dt "string";
	addAttr -ci true -sn "endName" -ln "endName" -dt "string";
	addAttr -ci true -sn "digitsName" -ln "digitsName" -dt "string";
	addAttr -ci true -sn "upperTwistCount" -ln "upperTwistCount" -dt "string";
	addAttr -ci true -sn "lowerTwistCount" -ln "lowerTwistCount" -dt "string";
	addAttr -ci true -sn "ankleTwistCount" -ln "ankleTwistCount" -dt "string";
	addAttr -ci true -sn "digits" -ln "digits" -dt "string";
	addAttr -ci true -sn "digitHasBase" -ln "digitHasBase" -dt "string";
	addAttr -ci true -sn "digitsNumberedNaming" -ln "digitsNumberedNaming" -dt "string";
	addAttr -ci true -sn "hasTopDeformJoint" -ln "hasTopDeformJoint" -dt "string";
	addAttr -ci true -sn "hasMidDeformJoint" -ln "hasMidDeformJoint" -dt "string";
	addAttr -ci true -sn "hasKnuckleDeformJoint" -ln "hasKnuckleDeformJoint" -dt "string";
	addAttr -ci true -sn "hasStretch" -ln "hasStretch" -dt "string";
	addAttr -ci true -sn "hasMidControl" -ln "hasMidControl" -dt "string";
	addAttr -ci true -sn "hasSmoothIk" -ln "hasSmoothIk" -dt "string";
	addAttr -ci true -sn "hasPlatform" -ln "hasPlatform" -dt "string";
	addAttr -ci true -sn "spaceNodes" -ln "spaceNodes" -dt "string";
	addAttr -ci true -sn "spaceNames" -ln "spaceNames" -dt "string";
	addAttr -ci true -sn "quadruped" -ln "quadruped" -dt "string";
	addAttr -ci true -sn "invertKnee" -ln "invertKnee" -dt "string";
	addAttr -ci true -sn "shoulderHasLegInfluence" -ln "shoulderHasLegInfluence" -dt "string";
	addAttr -ci true -sn "defaultAlignment" -ln "defaultAlignment" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "displaySwitch" -ln "displaySwitch" -dt "string";
	addAttr -ci true -sn "output_legB_R_ankle_guidePivot" -ln "output_legB_R_ankle_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legB_R_toes_guidePivot" -ln "output_legB_R_toes_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legB_R_shoulder_guidePivot" -ln "output_legB_R_shoulder_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legB_R_upper_01_skin" -ln "output_legB_R_upper_01_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_R_upper_02_skin" -ln "output_legB_R_upper_02_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_R_upper_03_skin" -ln "output_legB_R_upper_03_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_R_upper_04_skin" -ln "output_legB_R_upper_04_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_R_upper_05_skin" -ln "output_legB_R_upper_05_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_R_lower_01_skin" -ln "output_legB_R_lower_01_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_R_lower_02_skin" -ln "output_legB_R_lower_02_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_R_lower_03_skin" -ln "output_legB_R_lower_03_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_R_lower_04_skin" -ln "output_legB_R_lower_04_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_R_lower_05_skin" -ln "output_legB_R_lower_05_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legB_R_component" -ln "output_legB_R_component" -dt "string";
	addAttr -ci true -sn "output_legB_R_parent_loc" -ln "output_legB_R_parent_loc" -dt "string";
	addAttr -ci true -sn "output_legB_R_upper_guidePivot" -ln "output_legB_R_upper_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legB_R_lower_guidePivot" -ln "output_legB_R_lower_guidePivot" 
		-dt "string";
	setAttr ".t" -type "double3" -20 0 0 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".readyForRigBuild" yes;
	setAttr -l on ".namingConvention" -type "string" "component, side, nodeType";
	setAttr -l on ".side" -type "string" "R";
	setAttr -l on ".bearVersion" -type "string" "0.25.8";
	setAttr -l on ".componentType" -type "string" "Leg";
	setAttr ".name" -type "string" "legB";
	setAttr ".topName" -type "string" "shoulder";
	setAttr ".upperName" -type "string" "upper";
	setAttr ".midName" -type "string" "knee";
	setAttr ".lowerName" -type "string" "lower";
	setAttr ".endName" -type "string" "ankle";
	setAttr ".digitsName" -type "string" "toes";
	setAttr ".upperTwistCount" -type "string" "5";
	setAttr ".lowerTwistCount" -type "string" "5";
	setAttr ".ankleTwistCount" -type "string" "5";
	setAttr ".digits" -type "string" "None";
	setAttr ".digitHasBase" -type "string" "False, False, False, False, False";
	setAttr ".digitsNumberedNaming" -type "string" "True";
	setAttr ".hasTopDeformJoint" -type "string" "True";
	setAttr ".hasMidDeformJoint" -type "string" "True";
	setAttr ".hasKnuckleDeformJoint" -type "string" "True";
	setAttr ".hasStretch" -type "string" "True";
	setAttr ".hasMidControl" -type "string" "True";
	setAttr ".hasSmoothIk" -type "string" "True";
	setAttr ".hasPlatform" -type "string" "False";
	setAttr ".spaceNodes" -type "string" "root_control, root_placement_control, root_main_pivot_control, body_control";
	setAttr ".spaceNames" -type "string" "root, placement, main, body";
	setAttr ".quadruped" -type "string" "False";
	setAttr ".invertKnee" -type "string" "True";
	setAttr ".shoulderHasLegInfluence" -type "string" "False";
	setAttr ".defaultAlignment" -type "string" "biped";
	setAttr ".parentNode" -type "string" "tail_01_control";
	setAttr ".displaySwitch" -type "string" "bodyDisplaySwitch";
	setAttr -l on ".output_legB_R_ankle_guidePivot" -type "string" "legB_R_ankle_guidePivot";
	setAttr -l on ".output_legB_R_toes_guidePivot" -type "string" "legB_R_toes_guidePivot";
	setAttr -l on ".output_legB_R_shoulder_guidePivot" -type "string" "legB_R_shoulder_guidePivot";
	setAttr -l on ".output_legB_R_upper_01_skin" -type "string" "legB_R_upper_01_skin";
	setAttr -l on ".output_legB_R_upper_02_skin" -type "string" "legB_R_upper_02_skin";
	setAttr -l on ".output_legB_R_upper_03_skin" -type "string" "legB_R_upper_03_skin";
	setAttr -l on ".output_legB_R_upper_04_skin" -type "string" "legB_R_upper_04_skin";
	setAttr -l on ".output_legB_R_upper_05_skin" -type "string" "legB_R_upper_05_skin";
	setAttr -l on ".output_legB_R_lower_01_skin" -type "string" "legB_R_lower_01_skin";
	setAttr -l on ".output_legB_R_lower_02_skin" -type "string" "legB_R_lower_02_skin";
	setAttr -l on ".output_legB_R_lower_03_skin" -type "string" "legB_R_lower_03_skin";
	setAttr -l on ".output_legB_R_lower_04_skin" -type "string" "legB_R_lower_04_skin";
	setAttr -l on ".output_legB_R_lower_05_skin" -type "string" "legB_R_lower_05_skin";
	setAttr -l on ".output_legB_R_component" -type "string" "legB_R_guide";
	setAttr -l on ".output_legB_R_parent_loc" -type "string" "legB_R_parent_loc";
	setAttr -l on ".output_legB_R_upper_guidePivot" -type "string" "legB_R_upper_guidePivot";
	setAttr -l on ".output_legB_R_lower_guidePivot" -type "string" "legB_R_lower_guidePivot";
createNode transform -n "legC_L_guide" -p "hexapod_guide";
	rename -uid "DA97C583-4E7B-918E-3F30-8DA0B82D13E2";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "side" -ln "side" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "topName" -ln "topName" -dt "string";
	addAttr -ci true -sn "upperName" -ln "upperName" -dt "string";
	addAttr -ci true -sn "midName" -ln "midName" -dt "string";
	addAttr -ci true -sn "lowerName" -ln "lowerName" -dt "string";
	addAttr -ci true -sn "endName" -ln "endName" -dt "string";
	addAttr -ci true -sn "digitsName" -ln "digitsName" -dt "string";
	addAttr -ci true -sn "upperTwistCount" -ln "upperTwistCount" -dt "string";
	addAttr -ci true -sn "lowerTwistCount" -ln "lowerTwistCount" -dt "string";
	addAttr -ci true -sn "ankleTwistCount" -ln "ankleTwistCount" -dt "string";
	addAttr -ci true -sn "digits" -ln "digits" -dt "string";
	addAttr -ci true -sn "digitHasBase" -ln "digitHasBase" -dt "string";
	addAttr -ci true -sn "digitsNumberedNaming" -ln "digitsNumberedNaming" -dt "string";
	addAttr -ci true -sn "hasTopDeformJoint" -ln "hasTopDeformJoint" -dt "string";
	addAttr -ci true -sn "hasMidDeformJoint" -ln "hasMidDeformJoint" -dt "string";
	addAttr -ci true -sn "hasKnuckleDeformJoint" -ln "hasKnuckleDeformJoint" -dt "string";
	addAttr -ci true -sn "hasStretch" -ln "hasStretch" -dt "string";
	addAttr -ci true -sn "hasMidControl" -ln "hasMidControl" -dt "string";
	addAttr -ci true -sn "hasSmoothIk" -ln "hasSmoothIk" -dt "string";
	addAttr -ci true -sn "hasPlatform" -ln "hasPlatform" -dt "string";
	addAttr -ci true -sn "spaceNodes" -ln "spaceNodes" -dt "string";
	addAttr -ci true -sn "spaceNames" -ln "spaceNames" -dt "string";
	addAttr -ci true -sn "quadruped" -ln "quadruped" -dt "string";
	addAttr -ci true -sn "invertKnee" -ln "invertKnee" -dt "string";
	addAttr -ci true -sn "shoulderHasLegInfluence" -ln "shoulderHasLegInfluence" -dt "string";
	addAttr -ci true -sn "defaultAlignment" -ln "defaultAlignment" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "displaySwitch" -ln "displaySwitch" -dt "string";
	addAttr -ci true -sn "output_legC_L_ankle_guidePivot" -ln "output_legC_L_ankle_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legC_L_toes_guidePivot" -ln "output_legC_L_toes_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legC_L_shoulder_guidePivot" -ln "output_legC_L_shoulder_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legC_L_upper_01_skin" -ln "output_legC_L_upper_01_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_L_upper_02_skin" -ln "output_legC_L_upper_02_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_L_upper_03_skin" -ln "output_legC_L_upper_03_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_L_upper_04_skin" -ln "output_legC_L_upper_04_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_L_upper_05_skin" -ln "output_legC_L_upper_05_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_L_lower_01_skin" -ln "output_legC_L_lower_01_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_L_lower_02_skin" -ln "output_legC_L_lower_02_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_L_lower_03_skin" -ln "output_legC_L_lower_03_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_L_lower_04_skin" -ln "output_legC_L_lower_04_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_L_lower_05_skin" -ln "output_legC_L_lower_05_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_L_component" -ln "output_legC_L_component" -dt "string";
	addAttr -ci true -sn "output_legC_L_parent_loc" -ln "output_legC_L_parent_loc" -dt "string";
	addAttr -ci true -sn "output_legC_L_upper_guidePivot" -ln "output_legC_L_upper_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legC_L_lower_guidePivot" -ln "output_legC_L_lower_guidePivot" 
		-dt "string";
	setAttr ".t" -type "double3" 20 0 -40 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".readyForRigBuild" yes;
	setAttr -l on ".namingConvention" -type "string" "component, side, nodeType";
	setAttr -l on ".side" -type "string" "L";
	setAttr -l on ".bearVersion" -type "string" "0.25.8";
	setAttr -l on ".componentType" -type "string" "Leg";
	setAttr ".name" -type "string" "legC";
	setAttr ".topName" -type "string" "shoulder";
	setAttr ".upperName" -type "string" "upper";
	setAttr ".midName" -type "string" "knee";
	setAttr ".lowerName" -type "string" "lower";
	setAttr ".endName" -type "string" "ankle";
	setAttr ".digitsName" -type "string" "toes";
	setAttr ".upperTwistCount" -type "string" "5";
	setAttr ".lowerTwistCount" -type "string" "5";
	setAttr ".ankleTwistCount" -type "string" "5";
	setAttr ".digits" -type "string" "None";
	setAttr ".digitHasBase" -type "string" "False, False, False, False, False";
	setAttr ".digitsNumberedNaming" -type "string" "True";
	setAttr ".hasTopDeformJoint" -type "string" "True";
	setAttr ".hasMidDeformJoint" -type "string" "True";
	setAttr ".hasKnuckleDeformJoint" -type "string" "True";
	setAttr ".hasStretch" -type "string" "True";
	setAttr ".hasMidControl" -type "string" "True";
	setAttr ".hasSmoothIk" -type "string" "True";
	setAttr ".hasPlatform" -type "string" "False";
	setAttr ".spaceNodes" -type "string" "root_control, root_placement_control, root_main_pivot_control, body_control";
	setAttr ".spaceNames" -type "string" "root, placement, main, body";
	setAttr ".quadruped" -type "string" "False";
	setAttr ".invertKnee" -type "string" "False";
	setAttr ".shoulderHasLegInfluence" -type "string" "False";
	setAttr ".defaultAlignment" -type "string" "biped";
	setAttr ".parentNode" -type "string" "tail_02_control";
	setAttr ".displaySwitch" -type "string" "bodyDisplaySwitch";
	setAttr -l on ".output_legC_L_ankle_guidePivot" -type "string" "legC_L_ankle_guidePivot";
	setAttr -l on ".output_legC_L_toes_guidePivot" -type "string" "legC_L_toes_guidePivot";
	setAttr -l on ".output_legC_L_shoulder_guidePivot" -type "string" "legC_L_shoulder_guidePivot";
	setAttr -l on ".output_legC_L_upper_01_skin" -type "string" "legC_L_upper_01_skin";
	setAttr -l on ".output_legC_L_upper_02_skin" -type "string" "legC_L_upper_02_skin";
	setAttr -l on ".output_legC_L_upper_03_skin" -type "string" "legC_L_upper_03_skin";
	setAttr -l on ".output_legC_L_upper_04_skin" -type "string" "legC_L_upper_04_skin";
	setAttr -l on ".output_legC_L_upper_05_skin" -type "string" "legC_L_upper_05_skin";
	setAttr -l on ".output_legC_L_lower_01_skin" -type "string" "legC_L_lower_01_skin";
	setAttr -l on ".output_legC_L_lower_02_skin" -type "string" "legC_L_lower_02_skin";
	setAttr -l on ".output_legC_L_lower_03_skin" -type "string" "legC_L_lower_03_skin";
	setAttr -l on ".output_legC_L_lower_04_skin" -type "string" "legC_L_lower_04_skin";
	setAttr -l on ".output_legC_L_lower_05_skin" -type "string" "legC_L_lower_05_skin";
	setAttr -l on ".output_legC_L_component" -type "string" "legC_L_guide";
	setAttr -l on ".output_legC_L_parent_loc" -type "string" "legC_L_parent_loc";
	setAttr -l on ".output_legC_L_upper_guidePivot" -type "string" "legC_L_upper_guidePivot";
	setAttr -l on ".output_legC_L_lower_guidePivot" -type "string" "legC_L_lower_guidePivot";
createNode transform -n "legC_R_guide" -p "hexapod_guide";
	rename -uid "968F240D-4AD5-7007-6D7E-0D8B5199D2E4";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "side" -ln "side" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "topName" -ln "topName" -dt "string";
	addAttr -ci true -sn "upperName" -ln "upperName" -dt "string";
	addAttr -ci true -sn "midName" -ln "midName" -dt "string";
	addAttr -ci true -sn "lowerName" -ln "lowerName" -dt "string";
	addAttr -ci true -sn "endName" -ln "endName" -dt "string";
	addAttr -ci true -sn "digitsName" -ln "digitsName" -dt "string";
	addAttr -ci true -sn "upperTwistCount" -ln "upperTwistCount" -dt "string";
	addAttr -ci true -sn "lowerTwistCount" -ln "lowerTwistCount" -dt "string";
	addAttr -ci true -sn "ankleTwistCount" -ln "ankleTwistCount" -dt "string";
	addAttr -ci true -sn "digits" -ln "digits" -dt "string";
	addAttr -ci true -sn "digitHasBase" -ln "digitHasBase" -dt "string";
	addAttr -ci true -sn "digitsNumberedNaming" -ln "digitsNumberedNaming" -dt "string";
	addAttr -ci true -sn "hasTopDeformJoint" -ln "hasTopDeformJoint" -dt "string";
	addAttr -ci true -sn "hasMidDeformJoint" -ln "hasMidDeformJoint" -dt "string";
	addAttr -ci true -sn "hasKnuckleDeformJoint" -ln "hasKnuckleDeformJoint" -dt "string";
	addAttr -ci true -sn "hasStretch" -ln "hasStretch" -dt "string";
	addAttr -ci true -sn "hasMidControl" -ln "hasMidControl" -dt "string";
	addAttr -ci true -sn "hasSmoothIk" -ln "hasSmoothIk" -dt "string";
	addAttr -ci true -sn "hasPlatform" -ln "hasPlatform" -dt "string";
	addAttr -ci true -sn "spaceNodes" -ln "spaceNodes" -dt "string";
	addAttr -ci true -sn "spaceNames" -ln "spaceNames" -dt "string";
	addAttr -ci true -sn "quadruped" -ln "quadruped" -dt "string";
	addAttr -ci true -sn "invertKnee" -ln "invertKnee" -dt "string";
	addAttr -ci true -sn "shoulderHasLegInfluence" -ln "shoulderHasLegInfluence" -dt "string";
	addAttr -ci true -sn "defaultAlignment" -ln "defaultAlignment" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "displaySwitch" -ln "displaySwitch" -dt "string";
	addAttr -ci true -sn "output_legC_R_ankle_guidePivot" -ln "output_legC_R_ankle_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legC_R_toes_guidePivot" -ln "output_legC_R_toes_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legC_R_shoulder_guidePivot" -ln "output_legC_R_shoulder_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legC_R_upper_01_skin" -ln "output_legC_R_upper_01_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_R_upper_02_skin" -ln "output_legC_R_upper_02_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_R_upper_03_skin" -ln "output_legC_R_upper_03_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_R_upper_04_skin" -ln "output_legC_R_upper_04_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_R_upper_05_skin" -ln "output_legC_R_upper_05_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_R_lower_01_skin" -ln "output_legC_R_lower_01_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_R_lower_02_skin" -ln "output_legC_R_lower_02_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_R_lower_03_skin" -ln "output_legC_R_lower_03_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_R_lower_04_skin" -ln "output_legC_R_lower_04_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_R_lower_05_skin" -ln "output_legC_R_lower_05_skin" 
		-dt "string";
	addAttr -ci true -sn "output_legC_R_component" -ln "output_legC_R_component" -dt "string";
	addAttr -ci true -sn "output_legC_R_parent_loc" -ln "output_legC_R_parent_loc" -dt "string";
	addAttr -ci true -sn "output_legC_R_upper_guidePivot" -ln "output_legC_R_upper_guidePivot" 
		-dt "string";
	addAttr -ci true -sn "output_legC_R_lower_guidePivot" -ln "output_legC_R_lower_guidePivot" 
		-dt "string";
	setAttr ".t" -type "double3" -20 0 -40 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".readyForRigBuild" yes;
	setAttr -l on ".namingConvention" -type "string" "component, side, nodeType";
	setAttr -l on ".side" -type "string" "R";
	setAttr -l on ".bearVersion" -type "string" "0.25.8";
	setAttr -l on ".componentType" -type "string" "Leg";
	setAttr ".name" -type "string" "legC";
	setAttr ".topName" -type "string" "shoulder";
	setAttr ".upperName" -type "string" "upper";
	setAttr ".midName" -type "string" "knee";
	setAttr ".lowerName" -type "string" "lower";
	setAttr ".endName" -type "string" "ankle";
	setAttr ".digitsName" -type "string" "toes";
	setAttr ".upperTwistCount" -type "string" "5";
	setAttr ".lowerTwistCount" -type "string" "5";
	setAttr ".ankleTwistCount" -type "string" "5";
	setAttr ".digits" -type "string" "None";
	setAttr ".digitHasBase" -type "string" "False, False, False, False, False";
	setAttr ".digitsNumberedNaming" -type "string" "True";
	setAttr ".hasTopDeformJoint" -type "string" "True";
	setAttr ".hasMidDeformJoint" -type "string" "True";
	setAttr ".hasKnuckleDeformJoint" -type "string" "True";
	setAttr ".hasStretch" -type "string" "True";
	setAttr ".hasMidControl" -type "string" "True";
	setAttr ".hasSmoothIk" -type "string" "True";
	setAttr ".hasPlatform" -type "string" "False";
	setAttr ".spaceNodes" -type "string" "root_control, root_placement_control, root_main_pivot_control, body_control";
	setAttr ".spaceNames" -type "string" "root, placement, main, body";
	setAttr ".quadruped" -type "string" "False";
	setAttr ".invertKnee" -type "string" "False";
	setAttr ".shoulderHasLegInfluence" -type "string" "False";
	setAttr ".defaultAlignment" -type "string" "biped";
	setAttr ".parentNode" -type "string" "tail_02_control";
	setAttr ".displaySwitch" -type "string" "bodyDisplaySwitch";
	setAttr -l on ".output_legC_R_ankle_guidePivot" -type "string" "legC_R_ankle_guidePivot";
	setAttr -l on ".output_legC_R_toes_guidePivot" -type "string" "legC_R_toes_guidePivot";
	setAttr -l on ".output_legC_R_shoulder_guidePivot" -type "string" "legC_R_shoulder_guidePivot";
	setAttr -l on ".output_legC_R_upper_01_skin" -type "string" "legC_R_upper_01_skin";
	setAttr -l on ".output_legC_R_upper_02_skin" -type "string" "legC_R_upper_02_skin";
	setAttr -l on ".output_legC_R_upper_03_skin" -type "string" "legC_R_upper_03_skin";
	setAttr -l on ".output_legC_R_upper_04_skin" -type "string" "legC_R_upper_04_skin";
	setAttr -l on ".output_legC_R_upper_05_skin" -type "string" "legC_R_upper_05_skin";
	setAttr -l on ".output_legC_R_lower_01_skin" -type "string" "legC_R_lower_01_skin";
	setAttr -l on ".output_legC_R_lower_02_skin" -type "string" "legC_R_lower_02_skin";
	setAttr -l on ".output_legC_R_lower_03_skin" -type "string" "legC_R_lower_03_skin";
	setAttr -l on ".output_legC_R_lower_04_skin" -type "string" "legC_R_lower_04_skin";
	setAttr -l on ".output_legC_R_lower_05_skin" -type "string" "legC_R_lower_05_skin";
	setAttr -l on ".output_legC_R_component" -type "string" "legC_R_guide";
	setAttr -l on ".output_legC_R_parent_loc" -type "string" "legC_R_parent_loc";
	setAttr -l on ".output_legC_R_upper_guidePivot" -type "string" "legC_R_upper_guidePivot";
	setAttr -l on ".output_legC_R_lower_guidePivot" -type "string" "legC_R_lower_guidePivot";
createNode transform -n "bodyDisplaySwitch_guide" -p "hexapod_guide";
	rename -uid "22C054D0-4B5D-1699-B1A8-96AC4BD8760F";
	addAttr -ci true -sn "readyForRigBuild" -ln "readyForRigBuild" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "globalScale" -ln "globalScale" -dv 1 -min 0.01 -at "float";
	addAttr -ci true -sn "namingConvention" -ln "namingConvention" -dt "string";
	addAttr -ci true -sn "side" -ln "side" -dt "string";
	addAttr -ci true -sn "bearVersion" -ln "bearVersion" -dt "string";
	addAttr -ci true -sn "componentType" -ln "componentType" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "parentNode" -ln "parentNode" -dt "string";
	addAttr -ci true -sn "output_bodyDisplaySwitch" -ln "output_bodyDisplaySwitch" -dt "string";
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
	setAttr -l on ".componentType" -type "string" "DisplaySwitch";
	setAttr ".name" -type "string" "bodyDisplaySwitch";
	setAttr ".parentNode" -type "string" "None";
	setAttr -l on ".output_bodyDisplaySwitch" -type "string" "bodyDisplaySwitch";
createNode lightLinker -s -n "lightLinker1";
	rename -uid "F1BA216A-48C1-5587-5A75-7BBA834BF729";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "F1354039-4602-6C1E-5937-AAA634273CFB";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "2CC5F31C-462A-F7BD-3B7E-3F9BB7C809F9";
createNode displayLayerManager -n "layerManager";
	rename -uid "675AD5AB-4ACC-D0DD-B3E3-6BBE3342FF11";
createNode displayLayer -n "defaultLayer";
	rename -uid "20C6BD75-4741-5F6E-091B-C188349746D4";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "07ADAE63-4BEE-0E40-026A-63B24EFC298C";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "D170D21B-4340-C73C-A687-0F8D0B7F4AB6";
	setAttr ".g" yes;
createNode aiOptions -s -n "defaultArnoldRenderOptions";
	rename -uid "6462E4C4-434C-86E8-B470-9A8EDB7E460A";
	setAttr ".version" -type "string" "5.2.0";
createNode aiAOVFilter -s -n "defaultArnoldFilter";
	rename -uid "25102449-4460-34EA-07C6-EA9B19038330";
	setAttr ".ai_translator" -type "string" "gaussian";
createNode aiAOVDriver -s -n "defaultArnoldDriver";
	rename -uid "11E51F56-4CB8-2B82-A30B-AE97CD885ADD";
	setAttr ".ai_translator" -type "string" "exr";
createNode aiAOVDriver -s -n "defaultArnoldDisplayDriver";
	rename -uid "908B6723-4615-4E6A-8B1C-9989A968AFA0";
	setAttr ".output_mode" 0;
	setAttr ".ai_translator" -type "string" "maya";
createNode script -n "uiConfigurationScriptNode";
	rename -uid "AE9BC26A-4A10-0B41-CAA4-1E876041014E";
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
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"ToggledOutliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 1\n            -showReferenceMembers 1\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n"
		+ "            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -isSet 0\n            -isSetMember 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n"
		+ "            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            -renderFilterIndex 0\n            -selectionOrder \"chronological\" \n            -expandAttribute 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\tif ($useSceneConfig) {\n        string $configName = `getPanel -cwl (localizedPanelLabel(\"Current Layout\"))`;\n        if (\"\" != $configName) {\n\t\t\tpanelConfiguration -edit -label (localizedPanelLabel(\"Current Layout\")) \n\t\t\t\t-userCreated false\n\t\t\t\t-defaultImage \"vacantCell.xP:/\"\n\t\t\t\t-image \"\"\n\t\t\t\t-sc false\n\t\t\t\t-configString \"global string $gMainPane; paneLayout -e -cn \\\"single\\\" -ps 1 100 100 $gMainPane;\"\n\t\t\t\t-removeAllPanels\n\t\t\t\t-ap false\n\t\t\t\t\t(localizedPanelLabel(\"Persp View\")) \n\t\t\t\t\t\"modelPanel\"\n"
		+ "\t\t\t\t\t\"$panelName = `modelPanel -unParent -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -docTag \\\"RADRENDER\\\" \\n    -editorChanged \\\"updateModelPanelBar\\\" \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 32768\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1959\\n    -height 1239\\n    -sceneRenderFilter 0\\n    -activeShadingGraph \\\"ballora_animatronic_shadow_rig:rsMaterial1SG,ballora_animatronic_shadow_rig:MAT_ballora,ballora_animatronic_shadow_rig:MAT_ballora\\\" \\n    -activeCustomGeometry \\\"meshShaderball\\\" \\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t\t\"modelPanel -edit -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -docTag \\\"RADRENDER\\\" \\n    -editorChanged \\\"updateModelPanelBar\\\" \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 32768\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1959\\n    -height 1239\\n    -sceneRenderFilter 0\\n    -activeShadingGraph \\\"ballora_animatronic_shadow_rig:rsMaterial1SG,ballora_animatronic_shadow_rig:MAT_ballora,ballora_animatronic_shadow_rig:MAT_ballora\\\" \\n    -activeCustomGeometry \\\"meshShaderball\\\" \\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t$configName;\n\n            setNamedPanelLayout (localizedPanelLabel(\"Current Layout\"));\n        }\n\n        panelHistory -e -clear mainPanelHistory;\n        sceneUIReplacement -clear;\n\t}\n\n\ngrid -spacing 5 -size 12 -divisions 5 -displayAxes yes -displayGridLines yes -displayDivisionLines yes -displayPerspectiveLabels no -displayOrthographicLabels no -displayAxesBold yes -perspectiveLabelPosition axis -orthographicLabelPosition edge;\nviewManip -drawCompass 0 -compassAngle 0 -frontParameters \"\" -homeParameters \"\" -selectionLockParameters \"\";\n}\n");
	setAttr ".st" 3;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "8008216F-4A10-AE26-27CB-21976D6A3F64";
	setAttr ".b" -type "string" "playbackOptions -min 0 -max 250 -ast 0 -aet 250 ";
	setAttr ".st" 6;
select -ne :time1;
	setAttr -av -k on ".cch";
	setAttr -k on ".fzn";
	setAttr -av -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".o" 0;
	setAttr -av -k on ".unw";
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
connectAttr ":defaultArnoldDisplayDriver.msg" ":defaultArnoldRenderOptions.drivers"
		 -na;
connectAttr ":defaultArnoldFilter.msg" ":defaultArnoldRenderOptions.filt";
connectAttr ":defaultArnoldDriver.msg" ":defaultArnoldRenderOptions.drvr";
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
// End of Hexapod.ma
