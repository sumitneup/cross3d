##
#	\namespace	blur3d.api.softimage.softimagescenerenderpass
#
#	\remarks	The SoftimageSceneRenderPass class will define all the operations for Softimage render passes interaction.  
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/08/11
#

from PySoftimage import xsi
from blur3d.api.abstract.abstractscenerenderpass import AbstractSceneRenderPass

#------------------------------------------------------------------------------------------------------------------------

class SoftimageSceneRenderPass( AbstractSceneRenderPass ): 

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def _nativeCamera( self ):
		cameraName = self.nativePointer().Camera.Value
		from blur3d.api import Scene
		scene = Scene()
		return scene.findObject( cameraName )
		
	def _setNativeCamera( self, nativeCamera ):
		self.nativePointer().Camera.Value = nativeCamera.FullName
		return True
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def name( self ):
		return self.nativePointer().FullName
		
	def displayName( self ):
		return self.nativePointer().Name

	def setDisplayName( self, name ):
		self.nativePointer().Name = name
		return True

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneRenderPass', SoftimageSceneRenderPass )