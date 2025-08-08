
from typing import cast

from logging import Logger
from logging import getLogger

from untangle import Element

from pyutmodelv2.PyutClass import PyutClass

from umlshapes.shapes.UmlClass import UmlClass

from umlio.IOTypes import Elements
from umlio.IOTypes import GraphicInformation
from umlio.IOTypes import UmlClasses
from umlio.IOTypes import umlClassesFactory

from umlio.XMLConstants import XmlConstants

from umlio.deserializer.XmlToPyut import XmlToPyut


class XmlClassesToUmlClasses:
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        self._xmlToPyut: XmlToPyut = XmlToPyut()

    def deserialize(self, umlDiagramElement: Element) -> UmlClasses:
        """

        Args:
            umlDiagramElement:  The Element document

        Returns:  deserialized UmlNote objects if any exist, else an empty list
        """
        umlClasses:    UmlClasses = umlClassesFactory()
        classElements: Elements   = cast(Elements, umlDiagramElement.get_elements(XmlConstants.ELEMENT_UML_CLASS))

        for classElement in classElements:
            self.logger.debug(f'{classElement}')

            graphicInformation: GraphicInformation = GraphicInformation.toGraphicInfo(graphicElement=classElement)
            pyutClass:          PyutClass          = self._xmlToPyut.classToPyutClass(umlClassElement=classElement)
            umlClass:           UmlClass           = UmlClass(pyutClass=pyutClass)

            umlClass.id       = graphicInformation.id
            umlClass.size     = graphicInformation.size
            umlClass.position = graphicInformation.position

            umlClasses.append(umlClass)

        return umlClasses
