
from typing import cast

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutActor import PyutActor
from umlshapes.shapes.UmlActor import UmlActor
from untangle import Element

from umlio.IOTypes import Elements
from umlio.IOTypes import GraphicInformation
from umlio.IOTypes import UmlActors
from umlio.IOTypes import umlActorsFactory

from umlio.XMLConstants import XmlConstants

from umlio.deserializer.XmlToPyut import XmlToPyut


class XmlActorsToUmlActors:
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        self._xmlToPyut: XmlToPyut = XmlToPyut()

    def deserialize(self, umlDiagramElement: Element) -> UmlActors:
        """

        Args:
            umlDiagramElement:  The Element document

        Returns:  deserialized UmlNote objects if any exist, else an empty list
        """
        umlActors:     UmlActors = umlActorsFactory()
        actorElements: Elements = cast(Elements, umlDiagramElement.get_elements(XmlConstants.ELEMENT_UML_ACTOR))

        for actorElement in actorElements:
            self.logger.debug(f'{actorElement}')

            graphicInformation: GraphicInformation = GraphicInformation.toGraphicInfo(graphicElement=actorElement)
            pyutActor:          PyutActor           = self._xmlToPyut.actorToPyutActor(umlActorElement=actorElement)
            umlActor:           UmlActor            = UmlActor(pyutActor=pyutActor)

            umlActor.id       = graphicInformation.id
            umlActor.size     = graphicInformation.size
            umlActor.position = graphicInformation.position

            umlActors.append(umlActor)

        return umlActors
