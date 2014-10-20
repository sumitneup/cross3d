import maya.OpenMaya as om
import maya.cmds as cmds
from blur3d.constants import ObjectType
from blur3d.api import application, UserProps
from blur3d.api.abstract.abstractsceneobject import AbstractSceneObject
						
class MayaSceneObject( AbstractSceneObject ):
	#--------------------------------------------------------------------------------
	#							Init class variables
	#--------------------------------------------------------------------------------
	
	# This enum provides a map between blur3d's objectTypes and OpenMaya.MFn object types.
	# If the values are in a tuple more than one MFn object type needs to map to blur3d's objectType
	# None values are ignored. They eather don't exist, or we haven't found the maya equivelent of it.
	# NOTE: Many of these are untested.
	_abstractToNativeObjectType = {ObjectType.Generic: om.MFn.kDagNode,
		ObjectType.Geometry: om.MFn.kMesh,
		ObjectType.Light: om.MFn.kLight,
		ObjectType.Camera: om.MFn.kCamera,
		ObjectType.Model: om.MFn.kModel,
		ObjectType.Group: None,
		ObjectType.Bone: om.MFn.kJoint,
		ObjectType.Particle: (om.MFn.kParticle, om.MFn.kNParticle), # I am not sure this is required, but it is supported
		ObjectType.FumeFX: None,
		ObjectType.Curve: om.MFn.kCurve,
		ObjectType.PolyMesh: om.MFn.kPolyMesh,
		ObjectType.NurbsSurface: om.MFn.kNurbsSurface,
		ObjectType.Thinking: None,
		ObjectType.XMeshLoader: None,
		ObjectType.CameraInterest: None
	}
	# Create the inverse of _abstractToNativeObjectType.
	_nativeToAbstractObjectType = {}
	for abstract, native in _abstractToNativeObjectType.iteritems():
		if isinstance(native, (tuple, list)):
			for item in native:
				_nativeToAbstractObjectType[item] = abstract
		else:
			_nativeToAbstractObjectType[native] = abstract
	
	def __init__(self, scene, nativeObject):
		""" MayaSceneObject's should always have the shape node stored in _nativePointer
		MayaSceneObject's should have the transform node stored in _nativeTransform
		A transform can have multiple shape nodes, as children, but a shape node can only
		have a single transform as its parent. If you init this class with a transform node
		it will automaticly convert the native pointer to the first shape node. If you init
		this class with a shape node it will use that shape node as the native pointer.
		
		TODO: When we want to add support for swaping shape nodes they should be implemented
		as self.setTransform(SceneObject). This will update the _nativeTransform for self and
		prevent needing to create a new SceneObject.
		"""
		# Make sure the nativeObject is a OpenMaya.MObject, and that its a shape node.
		mObj = self._asMOBject(nativeObject)
		nativeObject = self._getShapeNode(mObj)
		super(MayaSceneObject, self).__init__(scene, nativeObject)
		# _nativeTypePointer stores the specific MFn* object representation of MObject this is
		# used mostly by subclasses of SceneObject
		self._nativeTypePointer = mObj
		# store the transform node so we can access it later
		self._nativeTransform = self._getTransformNode(mObj)
	
	#--------------------------------------------------------------------------------
	#							blur3d private methods
	#--------------------------------------------------------------------------------
	@classmethod
	def _typeOfNativeObject(cls, nativeObject):
		"""
			\remarks	reimplements the AbstractSceneObject._typeOfNativeObject method to returns the ObjectType of the nativeObject applied
			\param		<Py3dsMax.mxs.Object> nativeObject || None
			\return		<bool> success
		"""
		# Make sure the nativeObject is a OpenMaya.MObject
		# TODO: Move this into a blur3d private function the __new__ factory can call.
		nativeObject = cls._asMOBject(nativeObject)
		apiType = nativeObject.apiType()
		if apiType == om.MFn.kTransform:
			apiType = cls._getShapeNode(nativeObject).apiType()
		
		# Checking for model.
		if apiType == om.MFn.kLocator:
			userProps = UserProps(nativeObject)
			if 'model' in userProps:
				return ObjectType.Model
		
		if apiType in cls._nativeToAbstractObjectType:
			return cls._nativeToAbstractObjectType[apiType]
		return AbstractSceneObject._typeOfNativeObject(nativeObject)
	
	#--------------------------------------------------------------------------------
	#							blur3d public methods
	#--------------------------------------------------------------------------------
	def displayName(self):
		""" Returns the display name for object. This does not include parent structure """
		return self._mObjName(self._nativeTransform, False)

	def name(self):
		""" Return the full name of this object, including parent structure """
		return self._mObjName(self._nativeTransform, True)
	
	def matchTransforms(self, obj, position=True, rotation=True, scale=True):
		""" Currently the auto-key support is a bit lite, but it should cover most of the cases. """
		srcName = obj.name()
		destName = self._mObjName(self._nativeTransform)
		def copyAttr(attrName):
			value = cmds.getAttr('{name}.{attrName}'.format(name=srcName, attrName=attrName))
			cmds.setAttr('{name}.{attrName}'.format(name=destName, attrName=attrName), value)
		
		if position:
			copyAttr('translateX')
			copyAttr('translateY')
			copyAttr('translateZ')
		if rotation:
			copyAttr('rotateX')
			copyAttr('rotateY')
			copyAttr('rotateZ')
		if scale:
			copyAttr('scaleX')
			copyAttr('scaleY')
			copyAttr('scaleZ')

		if application.autokey():
			self.key()
		return True
	
	def parameters(self):
		name = self._mObjName(self._nativePointer)
		parameters = {}
		for attrName in self.propertyNames():
			if attrName not in set([u'translateX', u'translateY', u'translateZ', u'rotateX', u'rotateY', u'rotateZ', u'scaleX', u'scaleY', u'scaleZ']):
				try:
					parameters[attrName] = self.property(attrName)
				except ValueError:
					pass
		return parameters
	
	def setParameters(self, parameters):
		name = self._mObjName(self._nativePointer)
		for key, value in parameters.iteritems():
			try:
				self.setProperty(key, value)
			except:
				print 'TRACEBACK: skipping param: {} {}...'.format(key, value)
				import traceback
				print traceback.format_exc()

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneObject', MayaSceneObject )