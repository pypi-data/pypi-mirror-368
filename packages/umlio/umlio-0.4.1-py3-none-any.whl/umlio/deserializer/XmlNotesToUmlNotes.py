
from typing import cast

from logging import Logger
from logging import getLogger

from untangle import Element

from pyutmodelv2.PyutNote import PyutNote
from umlshapes.shapes.UmlNote import UmlNote

from umlio.IOTypes import Elements
from umlio.IOTypes import GraphicInformation
from umlio.IOTypes import UmlNotes
from umlio.IOTypes import umlNotesFactory

from umlio.XMLConstants import XmlConstants

from umlio.deserializer.XmlToPyut import XmlToPyut


class XmlNotesToUmlNotes:
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        self._xmlToPyut: XmlToPyut = XmlToPyut()

    def deserialize(self, umlDiagramElement: Element) -> UmlNotes:
        """

        Args:
            umlDiagramElement:  The Element document

        Returns:  deserialized UmlNote objects if any exist, else an empty list
        """
        umlNotes:     UmlNotes = umlNotesFactory()
        noteElements: Elements = cast(Elements, umlDiagramElement.get_elements(XmlConstants.ELEMENT_UML_NOTE))

        for noteElement in noteElements:
            self.logger.debug(f'{noteElement}')

            graphicInformation: GraphicInformation = GraphicInformation.toGraphicInfo(graphicElement=noteElement)
            pyutNote:           PyutNote           = self._xmlToPyut.noteToPyutNote(umlNoteElement=noteElement)
            umlNote:            UmlNote            = UmlNote(pyutNote=pyutNote)

            umlNote.id       = graphicInformation.id
            umlNote.size     = graphicInformation.size
            umlNote.position = graphicInformation.position

            umlNotes.append(umlNote)

        return umlNotes
