import os
import maya.cmds as cmds
import maya.OpenMayaUI as omui


from PySide2 import QtWidgets
from PySide2 import QtGui, QtCore
from shiboken2 import wrapInstance

import maya.OpenMaya as om

import irisToolUi
reload (irisToolUi)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class ControlMainWindow(QtWidgets.QWidget):
 
    def __init__(self, parent=None):

        super(ControlMainWindow, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui = irisToolUi.Ui_irisToolUi()
        self.ui.setupUi(self)
        self.ui.setup.clicked.connect(self.setup)
        self.ui.irisFolder.clicked.connect(self.pickFolder)
        self.irisFolderPath = []



#------------------------------------------------------

    def setup(self):

        self.mesh = ["none"]
        self.id_01File= ["none"]
        self.id_02File= ["none"]
        self.id_03File= ["none"]
        self.id_04File= ["none"]
        self.id_05File= ["none"]
        self.id_06File= ["none"]
        self.fresnelFile= ["none"]
        self.aoFile= ["none"]
        side = []
        currentEngine = cmds.getAttr("defaultRenderGlobals.currentRenderer")
        #renderEngineValue = str(self.ui.renderEngine.currentIndex())
        presetValue = str(self.ui.colorPreset.currentIndex())

        if not self.irisFolderPath:
            om.MGlobal.displayError("Please select an Iris pack folder")
            return             
        irisFolderPath = self.irisFolderPath
    

        if self.ui.loadLeft.isChecked() == True:
            side = 'left'
        if self.ui.loadRight.isChecked() == True:
            side = 'right'

        if not side:
            om.MGlobal.displayError("Please choose the side(s) to load")
            return
            
        prompt = cmds.confirmDialog( title='iris Tool', message='This operation will take a few minutes', button=['ok','cancel'], defaultButton='Yes', cancelButton='No', dismissString='No' )
        if prompt == 'cancel':
            return

        if currentEngine =="arnold" :
            self.importMesh(irisFolderPath,side,presetValue)
            self.arnoldMeshSetup(presetValue,side)
            self.mapGather(irisFolderPath,side)
            self.shadersSetup(side,presetValue)
            



    def arnoldMeshSetup(self,presetValue,side):

        if presetValue == "0": 
            presetValue = "blue"

        if presetValue == "1":
            presetValue = "brown"

        if presetValue == "2":
            presetValue = "green"

        shape = [side+'_'+presetValue+':hi_top_geoShape',side+'_'+presetValue+':hi_bottom_geoShape']

        for shapes in shape:
            cmds.setAttr(shapes+".aiStepSize" , 0.010)
            cmds.setAttr(shapes+".aiVolumePadding" , 0.100)

    def pickFolder(self):
        

        self.irisFolderPath = cmds.fileDialog2(dialogStyle=2, fm = 3, cap ="Select an iris pack folder",okc ="select")
        if self.irisFolderPath == None :
            return
        
        self.ui.irisFolder.setText(self.irisFolderPath[0])


    def importMesh(self,irisFolderPath,side,presetValue):

        if presetValue == "0": 
            presetValue = "blue"

        if presetValue == "1":
            presetValue = "brown"

        if presetValue == "2":
            presetValue = "green"

        topMeshFile = os.path.isfile(irisFolderPath[0]+'/'+side+'/geo/hi_top_geo.obj')
        bottomMeshFile = os.path.isfile(irisFolderPath[0]+'/'+side+'/geo/hi_bottom_geo.obj') 

        if topMeshFile == True:
            topMeshFile = irisFolderPath[0]+'/'+side+'/geo/hi_top_geo.obj'

        if bottomMeshFile == True:
            bottomMeshFile = irisFolderPath[0]+'/'+side+'/geo/hi_bottom_geo.obj'

        cmds.file(topMeshFile,namespace = side+'_'+presetValue,mergeNamespacesOnClash=True, i=True,groupReference=True, groupName=side+"_hi_top_geo1")
        cmds.file(bottomMeshFile,namespace = side+'_'+presetValue,mergeNamespacesOnClash=True, i=True,groupReference=True, groupName=side+"_hi_bottom_geo1")



        cmds.select(side+"_hi_top_geo1")
        cmds.pickWalk(direction='down')
        cmds.rename(side+'_'+presetValue+':hi_top_geo' )
        cmds.parent(side+'_'+presetValue+':hi_top_geo',world=True)


        cmds.select(side+"_hi_bottom_geo1")
        cmds.pickWalk(direction='down')
        cmds.rename(side+'_'+presetValue+':hi_bottom_geo')
        cmds.parent(side+'_'+presetValue+':hi_bottom_geo', world=True)


        cmds.delete(side+'_hi_top_geo1')
        cmds.delete(side+'_hi_bottom_geo1')

        cmds.group(side+'_'+presetValue+':hi_top_geo',side+'_'+presetValue+':hi_bottom_geo',n=side+'_'+presetValue+':iris')

    def mapGather(self,irisFolderPath,side):

        topMeshFile = os.path.isfile(irisFolderPath[0]+'/'+side+'/geo/hi_top_geo.obj')
        bottomMeshFile = os.path.isfile(irisFolderPath[0]+'/'+side+'/geo/hi_bottom_geo.obj') 

        self.id_01File = os.path.isfile(irisFolderPath[0]+'/'+side+'/utility/id_01.tif')
        self.id_02File = os.path.isfile(irisFolderPath[0]+'/'+side+'/utility/id_02.tif')
        self.id_03File = os.path.isfile(irisFolderPath[0]+'/'+side+'/utility/id_03.tif')
        self.id_04File = os.path.isfile(irisFolderPath[0]+'/'+side+'/utility/id_04.tif')
        self.id_05File = os.path.isfile(irisFolderPath[0]+'/'+side+'/utility/id_05.tif')
        self.id_06File = os.path.isfile(irisFolderPath[0]+'/'+side+'/utility/id_06.tif')

        self.fresnelFile = os.path.isfile(irisFolderPath[0]+'/'+side+'/utility/fresnel.tif')
        self.aoFile = os.path.isfile(irisFolderPath[0]+'/'+side+'/utility/ao.tif')


        if self.id_01File == True:
            self.id_01File= irisFolderPath[0]+'/'+side+'/utility/id_01.tif'            

        if self.id_02File == True:
            self.id_02File= irisFolderPath[0]+'/'+side+'/utility/id_02.tif'  

        if self.id_03File == True:
            self.id_03File= irisFolderPath[0]+'/'+side+'/utility/id_03.tif'                     
        
        if self.id_04File == True:
            self.id_04File= irisFolderPath[0]+'/'+side+'/utility/id_04.tif'         

        if self.id_05File == True:
            self.id_05File= irisFolderPath[0]+'/'+side+'/utility/id_05.tif'         

        if self.id_06File == True:
            self.id_06File= irisFolderPath[0]+'/'+side+'/utility/id_06.tif'      

        if self.fresnelFile == True:
            self.fresnelFile= irisFolderPath[0]+'/'+side+'/fresnel/.tif'   

        if self.aoFile == True:
            self.aoFile = irisFolderPath[0]+'/'+side+'/utility/ao.tif'   


    def shadersSetup(self,side,presetValue):

        if presetValue == "0": 
            presetValue = "blue"

        if presetValue == "1":
            presetValue = "brown"

        if presetValue == "2":
            presetValue = "green"

        modPath = cmds.moduleInfo(path=True, moduleName='irisTool')
        arnoldPresetPath = modPath+'/scripts/shaders/arnold/'+presetValue+'.ma'
        cmds.file(arnoldPresetPath, i=True ,namespace = side+'_'+presetValue, mergeNamespacesOnClash=True)
        cmds.parent(side+'_'+presetValue+':projection', side+'_'+presetValue+':iris')       

        fileNodes = cmds.ls(type='file')

        topVolume = side+'_'+presetValue+':top_volume'
        bottomVolume = side+'_'+presetValue+':bottom_volume'

        for node in fileNodes :
            if cmds.getAttr(node+'.fileTextureName') == 'ID01':
                cmds.setAttr(node+'.fileTextureName',self.id_01File, type = "string" )
            if cmds.getAttr(node+'.fileTextureName') == 'ID02':
                cmds.setAttr(node+'.fileTextureName',self.id_02File, type = "string" )        
            if cmds.getAttr(node+'.fileTextureName') == 'ID03':
                cmds.setAttr(node+'.fileTextureName',self.id_03File, type = "string" )
            if cmds.getAttr(node+'.fileTextureName') == 'ID04':
                cmds.setAttr(node+'.fileTextureName',self.id_04File, type = "string" )
            if cmds.getAttr(node+'.fileTextureName') == 'ID05':
                cmds.setAttr(node+'.fileTextureName',self.id_05File, type = "string" )



        top_shading_group= cmds.sets(name = side+'_'+presetValue+':iris_top_' + "SG", renderable=True,noSurfaceShader=True,empty=True)
        bottom_shading_group= cmds.sets(name = side+'_'+presetValue+':iris_bottom_' + "SG", renderable=True,noSurfaceShader=True,empty=True)
        cmds.connectAttr('%s.outColor' %topVolume ,'%s.surfaceShader' %top_shading_group)
        cmds.connectAttr('%s.outColor' %bottomVolume ,'%s.surfaceShader' %bottom_shading_group)

        cmds.select(side+'_'+presetValue+':hi_bottom_geo')
        cmds.hyperShade(assign=bottom_shading_group)
        cmds.select(side+'_'+presetValue+':hi_top_geo')
        cmds.hyperShade(assign=top_shading_group)                      





def run():

    global win
    try:
        win.close()
        win.deleteLater()

    except: 
        pass

    win = ControlMainWindow(parent=maya_main_window())
    win.show()


