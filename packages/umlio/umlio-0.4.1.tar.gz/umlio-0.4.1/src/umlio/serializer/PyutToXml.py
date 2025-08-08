
from logging import Logger
from logging import getLogger

from os import linesep as osLineSep

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement

from codeallybasic.Common import XML_END_OF_LINE_MARKER

from umlio.IOTypes import ElementAttributes

from pyutmodelv2.PyutLink import LinkDestination
from pyutmodelv2.PyutLink import LinkSource
from pyutmodelv2.PyutLink import PyutLink

from pyutmodelv2.PyutModelTypes import ClassName
from pyutmodelv2.PyutActor import PyutActor
from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutClassCommon import PyutClassCommon
from pyutmodelv2.PyutField import PyutField
from pyutmodelv2.PyutInterface import PyutInterface
from pyutmodelv2.PyutMethod import PyutMethod
from pyutmodelv2.PyutMethod import SourceCode
from pyutmodelv2.PyutNote import PyutNote
from pyutmodelv2.PyutParameter import PyutParameter
from pyutmodelv2.PyutSDInstance import PyutSDInstance
from pyutmodelv2.PyutSDMessage import PyutSDMessage
from pyutmodelv2.PyutText import PyutText
from pyutmodelv2.PyutUseCase import PyutUseCase

from umlio.XMLConstants import XmlConstants


class PyutToXml:
    """
    Serializes Pyut Model classes to DOM
    """

    def __init__(self):
        super().__init__()
        self.logger: Logger = getLogger(__name__)

    def pyutClassToXml(self, pyutClass: PyutClass, umlClassElement: Element) -> Element:
        """
        Exporting a PyutClass to a miniDom Element.

        Args:
            pyutClass:        The pyut class to serialize
            umlClassElement:  The xml element to update

        Returns:
            A new updated element
        """

        commonAttributes = self._pyutClassCommonAttributes(pyutClass)
        attributes = {
            XmlConstants.ATTRIBUTE_ID:                     str(pyutClass.id),
            XmlConstants.ATTRIBUTE_NAME:                   pyutClass.name,
            XmlConstants.ATTRIBUTE_DISPLAY_METHODS:        str(pyutClass.showMethods),
            XmlConstants.ATTRIBUTE_DISPLAY_PARAMETERS:     pyutClass.displayParameters.value,
            XmlConstants.ATTRIBUTE_DISPLAY_CONSTRUCTOR:    pyutClass.displayConstructor.value,
            XmlConstants.ATTRIBUTE_DISPLAY_DUNDER_METHODS: pyutClass.displayDunderMethods.value,
            XmlConstants.ATTRIBUTE_DISPLAY_FIELDS:         str(pyutClass.showFields),
            XmlConstants.ATTRIBUTE_DISPLAY_STEREOTYPE:     str(pyutClass.displayStereoType),
            XmlConstants.ATTRIBUTE_FILENAME:               pyutClass.fileName,
        }

        attributes = attributes | commonAttributes

        pyutClassElement: Element = SubElement(umlClassElement, XmlConstants.ELEMENT_MODEL_CLASS, attrib=attributes)

        for method in pyutClass.methods:
            self._pyutMethodToXml(pyutMethod=method, pyutClassElement=pyutClassElement)

        for pyutField in pyutClass.fields:
            self._pyutFieldToXml(pyutField=pyutField, pyutClassElement=pyutClassElement)
        return pyutClassElement

    def pyutLinkToXml(self, pyutLink: PyutLink, umlLinkElement: Element) -> Element:
        """
        Exporting a PyutLink to an Element.

        Args:
            pyutLink:   Link to save
            umlLinkElement:     xml document

        Returns:
            A new minidom element
        """
        src: LinkSource      = pyutLink.source
        dst: LinkDestination = pyutLink.destination

        srcLinkId:  int = src.id
        destLinkId: int = dst.id

        attributes: ElementAttributes = ElementAttributes({
            XmlConstants.ATTRIBUTE_NAME:           pyutLink.name,
            XmlConstants.ATTRIBUTE_LINK_TYPE:      pyutLink.linkType.name,
            XmlConstants.ATTRIBUTE_SOURCE_ID:      str(srcLinkId),
            XmlConstants.ATTRIBUTE_DESTINATION_ID: str(destLinkId),
            XmlConstants.ATTRIBUTE_BIDIRECTIONAL:  str(pyutLink.bidirectional),
            XmlConstants.ATTRIBUTE_SOURCE_CARDINALITY_VALUE:      pyutLink.sourceCardinality,
            XmlConstants.ATTRIBUTE_DESTINATION_CARDINALITY_VALUE: pyutLink.destinationCardinality,
        })
        pyutLinkElement: Element = SubElement(umlLinkElement, XmlConstants.ELEMENT_MODEL_LINK, attrib=attributes)

        return pyutLinkElement

    def pyutInterfaceToXml(self, pyutInterface: PyutInterface, interface2Element: Element) -> Element:

        classId: int = pyutInterface.id

        attributes: ElementAttributes = ElementAttributes({
            XmlConstants.ATTRIBUTE_ID:          str(classId),
            XmlConstants.ATTRIBUTE_NAME:        pyutInterface.name,
            XmlConstants.ATTRIBUTE_DESCRIPTION: pyutInterface.description
        })
        pyutInterfaceElement: Element = SubElement(interface2Element, XmlConstants.ELEMENT_MODEL_INTERFACE, attrib=attributes)

        for method in pyutInterface.methods:
            self._pyutMethodToXml(pyutMethod=method, pyutClassElement=pyutInterfaceElement)

        for className in pyutInterface.implementors:
            self.logger.debug(f'implementing className: {className}')
            self._pyutImplementorToXml(className, pyutInterfaceElement)

        return pyutInterfaceElement

    def pyutNoteToXml(self, pyutNote: PyutNote, umlNoteElement: Element) -> Element:

        noteId:       int = pyutNote.id
        content:      str = pyutNote.content
        fixedContent: str  = content.replace(osLineSep, XML_END_OF_LINE_MARKER)
        if pyutNote.fileName is None:
            pyutNote.fileName = ''

        attributes: ElementAttributes = ElementAttributes({
            XmlConstants.ATTRIBUTE_ID:       str(noteId),
            XmlConstants.ATTRIBUTE_CONTENT:  fixedContent,
            XmlConstants.ATTRIBUTE_FILENAME: pyutNote.fileName,
        })
        pyutNoteElement: Element = SubElement(umlNoteElement, XmlConstants.ELEMENT_MODEL_NOTE, attrib=attributes)

        return pyutNoteElement

    def pyutTextToXml(self, pyutText: PyutText, umlTextElement: Element) -> Element:

        textId:       int = pyutText.id
        content:      str = pyutText.content
        fixedContent: str  = content.replace(osLineSep, XML_END_OF_LINE_MARKER)

        attributes: ElementAttributes = ElementAttributes({
            XmlConstants.ATTRIBUTE_ID:       str(textId),
            XmlConstants.ATTRIBUTE_CONTENT:  fixedContent,
        })
        pyutTextElement: Element = SubElement(umlTextElement, XmlConstants.ELEMENT_MODEL_TEXT, attrib=attributes)

        return pyutTextElement

    def pyutActorToXml(self, pyutActor: PyutActor, umlActorElement: Element) -> Element:

        actorId:  int = pyutActor.id
        fileName: str = pyutActor.fileName
        if fileName is None:
            fileName = ''

        attributes: ElementAttributes = ElementAttributes({
            XmlConstants.ATTRIBUTE_ID:       str(actorId),
            XmlConstants.ATTRIBUTE_NAME:     pyutActor.name,
            XmlConstants.ATTRIBUTE_FILENAME: fileName,
        })
        pyutActorElement: Element = SubElement(umlActorElement, XmlConstants.ELEMENT_MODEL_ACTOR, attributes)

        return pyutActorElement

    def pyutUseCaseToXml(self, pyutUseCase: PyutUseCase, umlUseCaseElement: Element) -> Element:

        useCaseId: int = pyutUseCase.id
        fileName:  str = pyutUseCase.fileName
        if fileName is None:
            fileName = ''

        attributes: ElementAttributes = ElementAttributes({
            XmlConstants.ATTRIBUTE_ID:       str(useCaseId),
            XmlConstants.ATTRIBUTE_NAME:     pyutUseCase.name,
            XmlConstants.ATTRIBUTE_FILENAME: fileName
        })
        pyutUseCaseElement: Element = SubElement(umlUseCaseElement, XmlConstants.ELEMENT_MODEL_USE_CASE, attributes)

        return pyutUseCaseElement

    def pyutSDInstanceToXml(self, pyutSDInstance: PyutSDInstance, oglSDInstanceElement: Element) -> Element:

        sdInstanceId: int = pyutSDInstance.id

        attributes: ElementAttributes = ElementAttributes({
            XmlConstants.ATTRIBUTE_ID:               str(sdInstanceId),
            XmlConstants.ATTRIBUTE_INSTANCE_NAME:    pyutSDInstance.instanceName,
            XmlConstants.ATTRIBUTE_LIFE_LINE_LENGTH: str(pyutSDInstance.instanceLifeLineLength),
        })

        pyutSDInstanceElement: Element = SubElement(oglSDInstanceElement, XmlConstants.ELEMENT_MODEL_SD_INSTANCE, attrib=attributes)

        return pyutSDInstanceElement

    def pyutSDMessageToXml(self, pyutSDMessage: PyutSDMessage, oglSDMessageElement: Element) -> Element:

        sdMessageId: int = pyutSDMessage.id

        # srcInstance: PyutSDInstance = pyutSDMessage.getSource()
        # dstInstance: PyutSDInstance = pyutSDMessage.getDestination()
        srcInstance: LinkSource      = pyutSDMessage.source
        dstInstance: LinkDestination = pyutSDMessage.destination

        idSrc: int = srcInstance.id
        idDst: int = dstInstance.id

        attributes: ElementAttributes = ElementAttributes({
            XmlConstants.ATTRIBUTE_ID:                        str(sdMessageId),
            XmlConstants.ATTRIBUTE_MESSAGE:                   pyutSDMessage.message,
            XmlConstants.ATTRIBUTE_SOURCE_TIME:               str(pyutSDMessage.sourceY),
            XmlConstants.ATTRIBUTE_DESTINATION_TIME:          str(pyutSDMessage.destinationY),
            XmlConstants.ATTRIBUTE_SD_MESSAGE_SOURCE_ID:      str(idSrc),
            XmlConstants.ATTRIBUTE_SD_MESSAGE_DESTINATION_ID: str(idDst),
        })

        pyutSDMessageElement: Element = SubElement(oglSDMessageElement, XmlConstants.ELEMENT_MODEL_SD_MESSAGE, attrib=attributes)

        return pyutSDMessageElement

    def _pyutMethodToXml(self, pyutMethod: PyutMethod, pyutClassElement: Element) -> Element:
        """
        Exporting a PyutMethod to an Element

        Args:
            pyutMethod:        Method to serialize
            pyutClassElement:  xml document

        Returns:
            The new updated element
        """
        attributes = {
            XmlConstants.ATTRIBUTE_NAME:               pyutMethod.name,
            XmlConstants.ATTRIBUTE_VISIBILITY:         pyutMethod.visibility.name,
            XmlConstants.ATTRIBUTE_METHOD_RETURN_TYPE: pyutMethod.returnType.value,
        }
        pyutMethodElement: Element = SubElement(pyutClassElement, XmlConstants.ELEMENT_MODEL_METHOD, attrib=attributes)
        for modifier in pyutMethod.modifiers:
            attributes = {
                XmlConstants.ATTRIBUTE_NAME: modifier.name,
            }
            SubElement(pyutMethodElement, XmlConstants.ELEMENT_MODEL_MODIFIER, attrib=attributes)
        self._pyutSourceCodeToXml(pyutMethod.sourceCode, pyutMethodElement)

        for pyutParameter in pyutMethod.parameters:
            self._pyutParameterToXml(pyutParameter, pyutMethodElement)
        # pyutMethodElement: Element = xmlDoc.createElement(XmlConstants.ELEMENT_MODEL_METHOD)
        #
        # pyutMethodElement.setAttribute(XmlConstants.ATTR_NAME, pyutMethod.name)
        #
        # visibility: PyutVisibilityEnum = pyutMethod.getVisibility()
        # visName:    str                = self.__safeVisibilityToName(visibility)
        #
        # if visibility is not None:
        #     pyutMethodElement.setAttribute(XmlConstants.ATTR_VISIBILITY, visName)
        #
        # for modifier in pyutMethod.modifiers:
        #     xmlModifier: Element = xmlDoc.createElement(XmlConstants.ELEMENT_MODEL_MODIFIER)
        #     xmlModifier.setAttribute(XmlConstants.ATTR_NAME, modifier.name)
        #     pyutMethodElement.appendChild(xmlModifier)
        #
        # if pyutMethod.returnType is not None:
        #     xmlReturnType: Element = xmlDoc.createElement(XmlConstants.ELEMENT_MODEL_RETURN)
        #     xmlReturnType.setAttribute(XmlConstants.ATTR_TYPE, str(pyutMethod.returnType))
        #     pyutMethodElement.appendChild(xmlReturnType)
        #
        # for param in pyutMethod.parameters:
        #     pyutMethodElement.appendChild(self._pyutParamToDom(param, xmlDoc))
        #
        # codeRoot: Element = self._pyutSourceCodeToDom(pyutMethod.sourceCode, xmlDoc)
        # pyutMethodElement.appendChild(codeRoot)
        # return pyutMethodElement
        return pyutMethodElement

    def _pyutClassCommonAttributes(self, classCommon: PyutClassCommon):

        attributes = {
            XmlConstants.ATTRIBUTE_DESCRIPTION: classCommon.description
        }
        return attributes

    def _pyutSourceCodeToXml(self, sourceCode: SourceCode, pyutMethodElement: Element):

        codeRoot: Element = SubElement(pyutMethodElement, XmlConstants.ELEMENT_MODEL_SOURCE_CODE)

        for code in sourceCode:
            codeElement: Element = SubElement(codeRoot, XmlConstants.ELEMENT_MODEL_CODE)
            codeElement.text = code

        return codeRoot

    def _pyutParameterToXml(self, pyutParameter: PyutParameter, pyutMethodElement: Element) -> Element:

        attributes = {
            XmlConstants.ATTRIBUTE_NAME:           pyutParameter.name,
            XmlConstants.ATTRIBUTE_PARAMETER_TYPE: pyutParameter.type.value,
        }

        defaultValue = pyutParameter.defaultValue
        if defaultValue is not None:
            attributes[XmlConstants.ATTRIBUTE_DEFAULT_VALUE] = pyutParameter.defaultValue

        pyutParameterElement: Element = SubElement(pyutMethodElement, XmlConstants.ELEMENT_MODEL_PARAMETER, attrib=attributes)

        return pyutParameterElement

    def _pyutFieldToXml(self, pyutField: PyutField, pyutClassElement: Element) -> Element:
        """
        Serialize a PyutField to an Element

        Args:
            pyutField:         The PyutField to serialize
            pyutClassElement: The Pyut Class element to update

        Returns:
            The new updated element
        """
        attributes = {
            XmlConstants.ATTRIBUTE_NAME:          pyutField.name,
            XmlConstants.ATTRIBUTE_VISIBILITY:    pyutField.visibility.name,
            XmlConstants.ATTRIBUTE_FIELD_TYPE:    pyutField.type.value,
            XmlConstants.ATTRIBUTE_DEFAULT_VALUE: pyutField.defaultValue,
        }
        pyutFieldElement: Element = SubElement(pyutClassElement, XmlConstants.ELEMENT_MODEL_FIELD, attrib=attributes)

        return pyutFieldElement

    def _pyutImplementorToXml(self, className: ClassName, pyutInterfaceElement: Element) -> Element:

        attributes: ElementAttributes = ElementAttributes({
            XmlConstants.ATTRIBUTE_IMPLEMENTING_CLASS_NAME: className,
        })
        implementorElement: Element = SubElement(pyutInterfaceElement, XmlConstants.ELEMENT_MODEL_IMPLEMENTOR, attrib=attributes)
        return implementorElement
