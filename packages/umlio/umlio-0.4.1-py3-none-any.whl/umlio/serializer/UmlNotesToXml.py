
from typing import cast

from logging import Logger
from logging import getLogger

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement

from umlshapes.shapes.UmlNote import UmlNote

from umlio.IOTypes import UmlNotes

from umlio.serializer.BaseUmlToXml import BaseUmlToXml
from umlio.serializer.PyutToXml import PyutToXml
from umlio.XMLConstants import XmlConstants


class UmlNotesToXml(BaseUmlToXml):
    def __init__(self):
        super().__init__()
        self.logger: Logger = getLogger(__name__)

        self._pyutToXml: PyutToXml = PyutToXml()

    def serialize(self, documentTop: Element, umlNotes: UmlNotes) -> Element:

        for note in umlNotes:
            umlNote: UmlNote = cast (UmlNote, note)
            umlNoteElement: Element = self._umlNoteToXml(documentTop=documentTop, umlNote=umlNote)
            self._pyutToXml.pyutNoteToXml(pyutNote=umlNote.pyutNote, umlNoteElement=umlNoteElement)

        return documentTop

    def _umlNoteToXml(self, documentTop: Element, umlNote: UmlNote) -> Element:

        attributes = self._umlBaseAttributes(umlShape=umlNote)
        umlNoteSubElement: Element = SubElement(documentTop, XmlConstants.ELEMENT_UML_NOTE, attrib=attributes)

        return umlNoteSubElement
