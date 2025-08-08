
from typing import cast

from dataclasses import dataclass

from logging import Logger
from logging import getLogger

from os import linesep as osLineSep

from pyutmodelv2.PyutLink import LinkDestination
from pyutmodelv2.PyutLink import LinkSource
from untangle import Element

from codeallybasic.Common import XML_END_OF_LINE_MARKER
from codeallybasic.SecureConversions import SecureConversions

from pyutmodelv2.PyutField import PyutField
from pyutmodelv2.PyutField import PyutFields

from pyutmodelv2.PyutObject import PyutObject
from pyutmodelv2.PyutUseCase import PyutUseCase
from pyutmodelv2.PyutActor import PyutActor
from pyutmodelv2.PyutInterface import PyutInterface
from pyutmodelv2.PyutLink import PyutLink
from pyutmodelv2.PyutMethod import PyutMethods
from pyutmodelv2.PyutMethod import PyutParameters
from pyutmodelv2.PyutMethod import SourceCode
from pyutmodelv2.PyutParameter import PyutParameter
from pyutmodelv2.PyutMethod import PyutMethod
from pyutmodelv2.PyutMethod import PyutModifiers
from pyutmodelv2.PyutModifier import PyutModifier
from pyutmodelv2.PyutType import PyutType
from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutNote import PyutNote
from pyutmodelv2.PyutText import PyutText

from pyutmodelv2.PyutSDInstance import PyutSDInstance
from pyutmodelv2.PyutSDMessage import PyutSDMessage

from pyutmodelv2.enumerations.PyutStereotype import PyutStereotype
from pyutmodelv2.enumerations.PyutVisibility import PyutVisibility
from pyutmodelv2.enumerations.PyutDisplayParameters import PyutDisplayParameters
from pyutmodelv2.enumerations.PyutLinkType import PyutLinkType
from pyutmodelv2.enumerations.PyutDisplayMethods import PyutDisplayMethods

from umlio.IOTypes import Elements

from umlio.XMLConstants import XmlConstants


@dataclass
class ConvolutedPyutSDMessageInformation:
    """
    This class is necessary because I do not want to mix Ogl and pyutmodel code;  Unfortunately,
    the IDs of the PyutSDInstance are buried and require a lookup

    """
    pyutSDMessage: PyutSDMessage = cast(PyutSDMessage, None)
    sourceId:      int           = -1
    destinationId: int           = -1


class XmlToPyut:
    """
    Converts pyutmodel Version 11 XML to Pyut Objects
    """
    NOTE_NAME:   str = 'Note'
    noteCounter: int = 0

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

    def classToPyutClass(self, umlClassElement: Element) -> PyutClass:
        classElement: Element = umlClassElement.PyutClass

        pyutClass: PyutClass = PyutClass()

        pyutClass = cast(PyutClass, self._addPyutObjectAttributes(pyutElement=classElement, pyutObject=pyutClass))

        displayStr:              str                   = classElement[XmlConstants.ATTRIBUTE_DISPLAY_PARAMETERS]
        displayParameters:       PyutDisplayParameters = PyutDisplayParameters(displayStr)
        displayConstructorStr:   str                   = classElement[XmlConstants.ATTRIBUTE_DISPLAY_CONSTRUCTOR]
        displayDunderMethodsStr: str                   = classElement[XmlConstants.ATTRIBUTE_DISPLAY_DUNDER_METHODS]

        displayConstructor:   PyutDisplayMethods = self._securePyutDisplayMethods(displayStr=displayConstructorStr)
        displayDunderMethods: PyutDisplayMethods = self._securePyutDisplayMethods(displayStr=displayDunderMethodsStr)

        showStereotype:     bool = bool(classElement[XmlConstants.ATTRIBUTE_DISPLAY_STEREOTYPE])
        showFields:         bool = bool(classElement[XmlConstants.ATTRIBUTE_DISPLAY_FIELDS])
        showMethods:        bool = bool(classElement[XmlConstants.ATTRIBUTE_DISPLAY_METHODS])
        stereotypeStr:      str  = classElement[XmlConstants.ATTRIBUTE_STEREOTYPE]
        fileName:           str  = classElement[XmlConstants.ATTRIBUTE_FILENAME]

        pyutClass.displayParameters    = displayParameters
        pyutClass.displayConstructor   = displayConstructor
        pyutClass.displayDunderMethods = displayDunderMethods

        pyutClass.displayStereoType = showStereotype
        pyutClass.showFields        = showFields
        pyutClass.showMethods       = showMethods

        pyutClass.description = classElement['description']
        pyutClass.stereotype  = PyutStereotype.toEnum(stereotypeStr)
        pyutClass.fileName    = fileName

        pyutClass.methods = self._methodToPyutMethods(classElement=classElement)
        pyutClass.fields  = self._fieldToPyutFields(classElement=classElement)

        return pyutClass

    def textToPyutText(self, umlTextElement: Element) -> PyutText:
        """
        Parses the Text elements
        Args:
            umlTextElement:   Of the form:   <UmlText id="xx.xx.xx"/>

        Returns: A PyutText Object
        """
        pyutTextElement: Element  = umlTextElement.PyutText
        pyutText:    PyutText = PyutText()

        pyutText.id  = int(pyutTextElement[XmlConstants.ATTRIBUTE_ID])

        rawContent:   str = pyutTextElement['content']
        cleanContent: str = rawContent.replace(XML_END_OF_LINE_MARKER, osLineSep)
        pyutText.content = cleanContent

        return pyutText

    def noteToPyutNote(self, umlNoteElement: Element) -> PyutNote:
        """
        Parse Note element

        Args:
            umlNoteElement: of the form:  <UmlNote id="xx.xx.xx"/>

        Returns: A PyutNote Object
        """
        pyutNoteElement = umlNoteElement.PyutNote

        pyutNote: PyutNote = PyutNote()

        # fix line feeds
        pyutNote = cast(PyutNote, self._addPyutObjectAttributes(pyutElement=pyutNoteElement, pyutObject=pyutNote))

        rawContent:   str = pyutNoteElement[XmlConstants.ATTRIBUTE_CONTENT]
        cleanContent: str = rawContent.replace(XML_END_OF_LINE_MARKER, osLineSep)
        pyutNote.content = cleanContent

        return pyutNote

    def interfaceToPyutInterface(self, umlInterfaceElement: Element) -> PyutInterface:

        pyutInterfaceElement: Element = umlInterfaceElement.PyutInterface

        interfaceId: int = int(pyutInterfaceElement['id'])
        name:        str = pyutInterfaceElement[XmlConstants.ATTRIBUTE_NAME]
        description: str = pyutInterfaceElement[XmlConstants.ATTRIBUTE_DESCRIPTION]

        pyutInterface: PyutInterface = PyutInterface(name=name)
        pyutInterface.id          = interfaceId
        pyutInterface.description = description

        implementors: Elements = cast(Elements, pyutInterfaceElement.get_elements(XmlConstants.ELEMENT_MODEL_IMPLEMENTOR))
        for implementor in implementors:
            pyutInterface.addImplementor(implementor[XmlConstants.ELEMENT_MODEL_IMPLEMENTING_CLASS_NAME])

        pyutInterface.methods = self._interfaceMethodsToPyutMethods(interface=pyutInterfaceElement)

        return pyutInterface

    def actorToPyutActor(self, umlActorElement: Element) -> PyutActor:
        """

        Args:
            umlActorElement:   untangle Element in the above format

        Returns:   PyutActor
        """
        pyutActorElement: Element   = umlActorElement.PyutActor

        pyutActor: PyutActor = PyutActor()

        pyutActor = cast(PyutActor, self._addPyutObjectAttributes(pyutElement=pyutActorElement, pyutObject=pyutActor))

        return pyutActor

    def useCaseToPyutUseCase(self, umlUseCaseElement: Element) -> PyutUseCase:
        """

        Args:
            umlUseCaseElement:  An `untangle` Element in the above format

        Returns:  PyutUseCase
        """
        useCaseElement: Element     = umlUseCaseElement.PyutUseCase

        pyutUseCase:    PyutUseCase = PyutUseCase()

        pyutUseCase = cast(PyutUseCase, self._addPyutObjectAttributes(pyutElement=useCaseElement, pyutObject=pyutUseCase))

        return pyutUseCase

    def linkToPyutLink(self, singleLink: Element, source: LinkSource, destination: LinkDestination) -> PyutLink:

        linkTypeStr:     str          = singleLink[XmlConstants.ATTRIBUTE_LINK_TYPE]

        linkType:        PyutLinkType = PyutLinkType.toEnum(linkTypeStr)
        cardSrc:         str          = singleLink[XmlConstants.ATTRIBUTE_SOURCE_CARDINALITY_VALUE]
        cardDest:        str          = singleLink[XmlConstants.ATTRIBUTE_DESTINATION_CARDINALITY_VALUE]
        bidir:           bool         = SecureConversions.secureBoolean(singleLink[XmlConstants.ATTRIBUTE_BIDIRECTIONAL])
        linkDescription: str          = singleLink['name']

        pyutLink: PyutLink = PyutLink(name=linkDescription,
                                      linkType=linkType,
                                      cardinalitySource=cardSrc, cardinalityDestination=cardDest,
                                      bidirectional=bidir,
                                      source=source,
                                      destination=destination)

        return pyutLink

    def sdInstanceToPyutSDInstance(self, oglSDInstanceElement: Element) -> PyutSDInstance:

        instanceElement: Element = oglSDInstanceElement.PyutSDInstance
        pyutSDInstance:  PyutSDInstance = PyutSDInstance()

        pyutSDInstance.id                     = int(instanceElement[XmlConstants.ATTRIBUTE_ID])
        pyutSDInstance.instanceName           = instanceElement[XmlConstants.ATTRIBUTE_INSTANCE_NAME]
        pyutSDInstance.instanceLifeLineLength = SecureConversions.secureInteger(instanceElement[XmlConstants.ATTRIBUTE_LIFE_LINE_LENGTH])

        return pyutSDInstance

    def sdMessageToPyutSDMessage(self, oglSDMessageElement: Element) -> ConvolutedPyutSDMessageInformation:
        """
        TODO:  Need to fix how SD Messages are created
        Args:
            oglSDMessageElement:

        Returns:  Bogus data class
        """
        messageElement: Element = oglSDMessageElement.PyutSDMessage

        pyutSDMessage:  PyutSDMessage = PyutSDMessage()

        pyutSDMessage.id = int(messageElement['id'])
        pyutSDMessage.message = messageElement['message']
        pyutSDMessage.linkType = PyutLinkType.SD_MESSAGE

        srcID: int = int(messageElement[XmlConstants.ATTRIBUTE_SD_MESSAGE_SOURCE_ID])
        dstID: int = int(messageElement[XmlConstants.ATTRIBUTE_SD_MESSAGE_DESTINATION_ID])

        srcTime: int = int(messageElement[XmlConstants.ATTRIBUTE_SOURCE_TIME])
        dstTime: int = int(messageElement[XmlConstants.ATTRIBUTE_DESTINATION_TIME])

        pyutSDMessage.sourceY      = srcTime
        pyutSDMessage.destinationY = dstTime

        bogus: ConvolutedPyutSDMessageInformation = ConvolutedPyutSDMessageInformation()

        bogus.pyutSDMessage = pyutSDMessage
        bogus.sourceId      = srcID
        bogus.destinationId = dstID

        return bogus

    def _methodToPyutMethods(self, classElement: Element) -> PyutMethods:
        """
        The pyutClass may not have methods;
        Args:
            classElement:  The pyutClassElement

        Returns:  May return an empty list
        """
        untangledPyutMethods: PyutMethods = PyutMethods([])

        methodElements: Elements = cast(Elements, classElement.get_elements(XmlConstants.ELEMENT_MODEL_METHOD))

        for methodElement in methodElements:
            methodName: str            = methodElement['name']
            visibility: PyutVisibility = PyutVisibility.toEnum(methodElement[XmlConstants.ATTRIBUTE_VISIBILITY])
            self.logger.debug(f"{methodName=} - {visibility=}")

            pyutMethod: PyutMethod = PyutMethod(name=methodName, visibility=visibility)

            pyutMethod.modifiers = self._modifierToPyutMethodModifiers(methodElement=methodElement)

            returnAttribute = methodElement[XmlConstants.ATTRIBUTE_METHOD_RETURN_TYPE]
            pyutMethod.returnType = PyutType(returnAttribute)

            parameters = self._paramToPyutParameters(methodElement)
            pyutMethod.parameters = parameters
            pyutMethod.sourceCode = self._sourceCodeToPyutSourceCode(methodElement=methodElement)

            untangledPyutMethods.append(pyutMethod)

        return untangledPyutMethods

    def _fieldToPyutFields(self, classElement: Element) -> PyutFields:
        untangledPyutFields: PyutFields = PyutFields([])

        fieldElements: Elements = cast(Elements, classElement.get_elements(XmlConstants.ELEMENT_MODEL_FIELD))

        for fieldElement in fieldElements:
            visibility: PyutVisibility = PyutVisibility.toEnum(fieldElement['visibility'])
            fieldName    = fieldElement[XmlConstants.ATTRIBUTE_NAME]
            pyutType     = PyutType(fieldElement[XmlConstants.ATTRIBUTE_FIELD_TYPE])
            defaultValue = fieldElement[XmlConstants.ATTRIBUTE_DEFAULT_VALUE]

            pyutField: PyutField = PyutField(name=fieldName, visibility=visibility, type=pyutType, defaultValue=defaultValue)

            untangledPyutFields.append(pyutField)

        return untangledPyutFields

    def _modifierToPyutMethodModifiers(self, methodElement: Element) -> PyutModifiers:
        """
        Should be in this form:

            <Modifier name="Modifier1"/>
            <Modifier name="Modifier2"/>
            <Modifier name="Modifier3"/>
            <Modifier name="Modifier4"/>

        Args:
            methodElement:

        Returns:   A PyutModifiers object that may be empty.
        """

        modifierElements = methodElement.get_elements('Modifier')

        pyutModifiers: PyutModifiers = PyutModifiers([])
        if len(modifierElements) > 0:
            for modifierElement in modifierElements:
                modifierName:           str       = modifierElement['name']
                pyutModifier: PyutModifier = PyutModifier(name=modifierName)
                pyutModifiers.append(pyutModifier)

        return pyutModifiers

    def _paramToPyutParameters(self, methodElement: Element) -> PyutParameters:

        parameterElements = methodElement.get_elements(XmlConstants.ELEMENT_MODEL_PARAMETER)

        untangledPyutMethodParameters: PyutParameters = PyutParameters([])
        for parameterElement in parameterElements:
            name:           str = parameterElement['name']
            defaultValue:   str = parameterElement['defaultValue']
            parameterType:  PyutType = PyutType(parameterElement['type'])

            pyutParameter: PyutParameter = PyutParameter(name=name, type=parameterType, defaultValue=defaultValue)

            untangledPyutMethodParameters.append(pyutParameter)

        return untangledPyutMethodParameters

    def _sourceCodeToPyutSourceCode(self, methodElement: Element) -> SourceCode:

        sourceCodeElements = methodElement.get_elements(XmlConstants.ELEMENT_MODEL_SOURCE_CODE)
        codeElements = sourceCodeElements[0].get_elements(XmlConstants.ELEMENT_MODEL_CODE)
        sourceCode: SourceCode = SourceCode([])
        for codeElement in codeElements:
            self.logger.debug(f'{codeElement.cdata=}')
            codeLine: str = codeElement.cdata
            sourceCode.append(codeLine)
        return sourceCode

    def _interfaceMethodsToPyutMethods(self, interface: Element) -> PyutMethods:

        pyutMethods: PyutMethods = self._methodToPyutMethods(interface)

        return pyutMethods

    def _addPyutObjectAttributes(self, pyutElement: Element, pyutObject: PyutObject) -> PyutObject:
        """

        Args:
            pyutElement:    pyutElement XML with common keys
            pyutObject:     The PyutObject to update

        Returns:  The updated pyutObject as
        """

        pyutObject.id       = int(pyutElement[XmlConstants.ATTRIBUTE_ID])    # TODO revisit this when we start using UUIDs
        pyutObject.name     = pyutElement[XmlConstants.ATTRIBUTE_NAME]
        pyutObject.fileName = pyutElement[XmlConstants.ATTRIBUTE_FILENAME]

        if pyutObject.name is None:
            XmlToPyut.noteCounter += 1
            pyutObject.name = f'{XmlToPyut.NOTE_NAME}-{XmlToPyut.noteCounter}'
        return pyutObject

    def _securePyutDisplayMethods(self, displayStr: str) -> PyutDisplayMethods:

        if displayStr is not None:
            pyutDisplayMethods: PyutDisplayMethods = PyutDisplayMethods(displayStr)
        else:
            pyutDisplayMethods = PyutDisplayMethods.UNSPECIFIED

        return pyutDisplayMethods
