
from logging import Logger
from logging import getLogger
from typing import cast

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement

from umlshapes.shapes.UmlActor import UmlActor
from umlshapes.shapes.UmlUseCase import UmlUseCase

from umlio.IOTypes import UmlActors
from umlio.IOTypes import UmlUseCases

from umlio.serializer.BaseUmlToXml import BaseUmlToXml
from umlio.serializer.PyutToXml import PyutToXml
from umlio.XMLConstants import XmlConstants


class UmlUseCasesToXml(BaseUmlToXml):
    """
    """
    def __init__(self):
        super().__init__()
        self.logger: Logger = getLogger(__name__)

        self._pyutToXml: PyutToXml = PyutToXml()

    def serialize(self, documentTop: Element, umlUseCases: UmlUseCases, umlActors: UmlActors) -> Element:

        for actor in umlActors:
            umlActor:        UmlActor = cast(UmlActor, actor)
            umlActorElement: Element  = self._umlActorToXml(documentTop=documentTop, umlActor=umlActor)
            self._pyutToXml.pyutActorToXml(pyutActor=umlActor.pyutActor, umlActorElement=umlActorElement)

        for useCase in umlUseCases:
            umlUseCase:        UmlUseCase = cast(UmlUseCase, useCase)
            umlUseCaseElement: Element    = self._umlUseCaseToXml(documentTop=documentTop, umlUseCase=umlUseCase)
            self._pyutToXml.pyutUseCaseToXml(pyutUseCase=umlUseCase.pyutUseCase, umlUseCaseElement=umlUseCaseElement)

        return documentTop

    def _umlUseCaseToXml(self, documentTop: Element, umlUseCase: UmlUseCase) -> Element:

        attributes = self._umlBaseAttributes(umlShape=umlUseCase)
        umlTextSubElement: Element = SubElement(documentTop, XmlConstants.ELEMENT_UML_USE_CASE, attrib=attributes)

        return umlTextSubElement

    def _umlActorToXml(self, documentTop: Element, umlActor: UmlActor) -> Element:

        attributes = self._umlBaseAttributes(umlShape=umlActor)
        umlActorSubElement: Element = SubElement(documentTop, XmlConstants.ELEMENT_UML_ACTOR, attrib=attributes)

        return umlActorSubElement
