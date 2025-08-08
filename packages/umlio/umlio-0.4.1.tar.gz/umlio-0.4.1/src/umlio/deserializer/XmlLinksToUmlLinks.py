
from typing import Dict
from typing import List
from typing import NewType
from typing import Union
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx import Point

from untangle import Element

from codeallybasic.SecureConversions import SecureConversions

from pyutmodelv2.PyutLink import LinkDestination
from pyutmodelv2.PyutLink import LinkSource
from pyutmodelv2.PyutLink import PyutLink
from pyutmodelv2.PyutInterface import PyutInterface
from pyutmodelv2.enumerations.PyutLinkType import PyutLinkType

from umlshapes.types.Common import EndPoints

from umlshapes.links.UmlLink import UmlLink
from umlshapes.links.UmlNoteLink import UmlNoteLink
from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlInheritance import UmlInheritance
from umlshapes.links.UmlComposition import UmlComposition
from umlshapes.links.UmlAggregation import UmlAggregation
from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface

from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlText import UmlText
from umlshapes.shapes.UmlUseCase import UmlUseCase
from umlshapes.shapes.UmlActor import UmlActor

from umlshapes.types.Common import AttachmentSide

from umlshapes.ShapeTypes import LinkableUmlShape
from umlshapes.ShapeTypes import LinkableUmlShapes

from umlio.IOTypes import Elements
from umlio.IOTypes import UmlLinkAttributes
from umlio.IOTypes import UmlLinks
from umlio.IOTypes import umlLinksFactory

from umlio.XMLConstants import XmlConstants

from umlio.deserializer.XmlToPyut import XmlToPyut


@dataclass
class ConnectedShapes:
    sourceShape:        LinkableUmlShape
    destinationShape:   LinkableUmlShape


UmlAssociationClasses = Union[UmlAssociation, UmlComposition, UmlAggregation]

# AssociationClassDescriptor = type[UmlAssociationClasses] = cast(type[LinkEventHandler], None)

LinkTypeToClass = NewType('LinkTypeToClass', Dict[PyutLinkType, type[UmlAssociationClasses]])

CLASSMAP: LinkTypeToClass = LinkTypeToClass(
    {
        PyutLinkType.ASSOCIATION: UmlAssociation,
        PyutLinkType.AGGREGATION: UmlAggregation,
        PyutLinkType.COMPOSITION: UmlComposition
    }
)
ASSOCIATION_LINK_TYPES: List[PyutLinkType] = [
    PyutLinkType.COMPOSITION, PyutLinkType.AGGREGATION, PyutLinkType.ASSOCIATION
]


class XmlLinksToUmlLinks:
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        self._xmlToPyut: XmlToPyut = XmlToPyut()

    def deserialize(self, umlDiagramElement: Element, linkableUmlShapes: LinkableUmlShapes) -> UmlLinks:

        umlLinks:     UmlLinks = umlLinksFactory()
        linkElements: Elements = cast(Elements, umlDiagramElement.get_elements(XmlConstants.ELEMENT_UML_LINK))

        for linkElement in linkElements:
            self.logger.debug(f'{linkElement=}')
            umlLink: UmlLink = self._umlLinkElementToUmlLink(umlLinkElement=linkElement, linkableUmlShapes=linkableUmlShapes)

            umlLinks.append(umlLink)

        lollipopElements: Elements = cast(Elements, umlDiagramElement.get_elements(XmlConstants.ELEMENT_LOLLIPOP))

        for lollipopElement in lollipopElements:
            self.logger.info(f'{lollipopElement}')
            umlLollipopInterface: UmlLollipopInterface = self._getLollipop(lollipopElement=lollipopElement, linkableUmlShapes=linkableUmlShapes)

            umlLinks.append(umlLollipopInterface)

        return umlLinks

    def _umlLinkElementToUmlLink(self, umlLinkElement: Element, linkableUmlShapes: LinkableUmlShapes) -> UmlLink:

        pyutLinkElements: Elements = cast(Elements, umlLinkElement.get_elements(XmlConstants.ELEMENT_MODEL_LINK))
        assert len(pyutLinkElements) == 1, 'There can only be one'

        singlePyutLinkElement: Element = pyutLinkElements[0]        # I hate this short cut

        umlLink: UmlLink = self._getUmlLink(umlLinkElement=umlLinkElement,
                                            singlePyutLinkElement=singlePyutLinkElement,
                                            linkableUmlShapes=linkableUmlShapes
                                            )

        return umlLink

    def _getUmlLink(self, umlLinkElement: Element, singlePyutLinkElement: Element, linkableUmlShapes: LinkableUmlShapes) -> UmlLink:

        connectedShapes: ConnectedShapes = self._getConnectedShapes(singlePyutLinkElement, linkableUmlShapes)
        pyutLink:        PyutLink        = self._getPyutLink(singlePyutLinkElement, connectedShapes)

        umlLink: UmlLink = self._umlLinkFactory(srcShape=connectedShapes.sourceShape,
                                                pyutLink=pyutLink,
                                                destShape=connectedShapes.destinationShape,
                                                )

        umlLinkAttributes: UmlLinkAttributes = UmlLinkAttributes.fromGraphicLink(linkElement=umlLinkElement)
        self.logger.debug(f'{umlLinkAttributes}=')

        umlLink.id        = umlLinkAttributes.id
        umlLink.spline    = umlLinkAttributes.spline

        umlLink.MakeLineControlPoints(n=2)       # Make this configurable

        umlLink.endPoints = EndPoints(
            toPosition=umlLinkAttributes.toPosition,
            fromPosition=umlLinkAttributes.fromPosition
        )
        controlPoints: List[Point] = self._getLineControlPoints(umlLinkElement=umlLinkElement)
        for cp in controlPoints:
            umlLink.InsertLineControlPoint(point=cp)

        return umlLink

    def _getPyutLink(self, pyutLinkElement: Element, connectedShapes: ConnectedShapes) -> PyutLink:
        """

        Args:
            pyutLinkElement:    The Xml Elements
            connectedShapes:    The shapes at the ends of the link

        Returns:    A data model link
        """

        # noinspection PyUnresolvedReferences
        pyutLink: PyutLink = self._xmlToPyut.linkToPyutLink(
            singleLink=pyutLinkElement,
            source=self._getLinkSourceModelClass(connectedShapes.sourceShape),
            destination=self._getLinkDestinationModelClass(connectedShapes.destinationShape)
        )
        self.logger.debug(f'{pyutLink=}')

        return pyutLink

    def _getConnectedShapes(self, pyutLinkElement: Element, linkableUmlShapes: LinkableUmlShapes) -> ConnectedShapes:
        """

        Args:
            pyutLinkElement:
            linkableUmlShapes:   The dictionary of potential shapes

        Returns:  The connected shapes;  Will assert if it cannot find them
        """
        sourceId: int = int(pyutLinkElement[XmlConstants.ATTRIBUTE_SOURCE_ID])
        dstId:    int = int(pyutLinkElement[XmlConstants.ATTRIBUTE_DESTINATION_ID])

        try:
            sourceShape:      LinkableUmlShape = linkableUmlShapes[sourceId]
            destinationShape: LinkableUmlShape = linkableUmlShapes[dstId]
        except KeyError as ke:
            self.logger.error(f'{linkableUmlShapes=}')
            self.logger.error(f'Developer Error -- {pyutLinkElement=}')
            self.logger.error(f'Developer Error -- {sourceId=} {dstId=}  KeyError index: {ke}')
            assert False, 'Developer error'

        return ConnectedShapes(sourceShape=sourceShape, destinationShape=destinationShape)

    def _getLinkSourceModelClass(self, linkableUmlShape: LinkableUmlShape) -> LinkSource:
        """

        Args:
            linkableUmlShape:

        Returns:  The appropriate model class instance
        """

        if isinstance(linkableUmlShape, UmlClass):
            return linkableUmlShape.pyutClass
        elif isinstance(linkableUmlShape, UmlNote):
            return linkableUmlShape.pyutNote
        elif isinstance(linkableUmlShape, UmlText):
            return linkableUmlShape.pyutText
        elif isinstance(linkableUmlShape, UmlActor):
            return linkableUmlShape.pyutActor
        else:
            assert False, f'{linkableUmlShape=} is not a source linkable UML Shape'

    def _getLinkDestinationModelClass(self, linkableUmlShape: LinkableUmlShape) -> LinkDestination:
        """

        Args:
            linkableUmlShape:

        Returns: The appropriate model class instance
        """

        if isinstance(linkableUmlShape, UmlClass):
            return linkableUmlShape.pyutClass
        elif isinstance(linkableUmlShape, UmlUseCase):
            return linkableUmlShape.pyutUseCase
        else:
            assert False, f'{linkableUmlShape=} is not a destination linkable UML Shape'

    def _getLineControlPoints(self, umlLinkElement: Element) -> List[Point]:
        """
         <LineControlPoint x="100" y="100" />

        Args:
            umlLinkElement:

        Returns:
        """

        controlPoints: List[Point] = []

        controlPointElements: Elements = cast(Elements, umlLinkElement.get_elements(XmlConstants.ELEMENT_MODEL_LINE_CONTROL_POINT))
        for controlPointElement in controlPointElements:
            x: int = SecureConversions.secureInteger(controlPointElement[XmlConstants.ATTRIBUTE_X])
            y: int = SecureConversions.secureInteger(controlPointElement[XmlConstants.ATTRIBUTE_Y])

            point: Point = Point(x=x, y=y)
            controlPoints.append(point)

        return controlPoints

    def _umlLinkFactory(self, srcShape: LinkableUmlShape, pyutLink: PyutLink, destShape: LinkableUmlShape) -> UmlLink:
        """

        Args:
            srcShape:
            pyutLink:
            destShape:

        Returns:  The appropriate UML Link shape

        """
        if pyutLink.linkType == PyutLinkType.INHERITANCE:
            # Note dest and source are reversed here
            return UmlInheritance(baseClass=cast(UmlClass, destShape), pyutLink=pyutLink, subClass=cast(UmlClass, srcShape))
        elif pyutLink.linkType in ASSOCIATION_LINK_TYPES:
            umlAssociation = CLASSMAP[pyutLink.linkType](pyutLink)
            #
            # Need to do this because the shape is not yet on a canvas
            #
            umlAssociation.sourceShape      = srcShape
            umlAssociation.destinationShape = destShape
            return umlAssociation
        elif pyutLink.linkType == PyutLinkType.NOTELINK:
            umlNoteLink: UmlNoteLink = UmlNoteLink(pyutLink=pyutLink)
            umlNoteLink.sourceNote       = cast(UmlNote, srcShape)
            umlNoteLink.destinationClass = cast(UmlClass, destShape)
            return umlNoteLink
        else:
            assert False, f'Unknown link type, {pyutLink.linkType=}'

    def _getLollipop(self, lollipopElement: Element, linkableUmlShapes: LinkableUmlShapes) -> UmlLollipopInterface:
        """
        <UmlLollipopInterface lineCentum="0.1" attachmentSide="Right" attachedToId="valley.darkness.implementor">

        Args:
            lollipopElement:
            linkableUmlShapes:

        Returns:

        """
        pyutInterface: PyutInterface = self._xmlToPyut.interfaceToPyutInterface(lollipopElement)

        umlLollipopInterface: UmlLollipopInterface = UmlLollipopInterface(pyutInterface=pyutInterface)

        attachmentSideStr: str      = lollipopElement[XmlConstants.ATTRIBUTE_ATTACHMENT_SIDE]
        attachedToId:      str      = lollipopElement[XmlConstants.ATTRIBUTE_ATTACHED_TO_ID]
        attachedTo:        UmlClass = self._findAttachedToClass(attachedToId=attachedToId, linkableUmlShapes=linkableUmlShapes)

        umlLollipopInterface.lineCentum     = SecureConversions.secureFloat(lollipopElement[XmlConstants.ATTRIBUTE_LINE_CENTUM])
        umlLollipopInterface.attachmentSide = AttachmentSide.toEnum(attachmentSideStr)

        umlLollipopInterface.attachedTo = attachedTo

        return umlLollipopInterface

    def _findAttachedToClass(self, attachedToId: str, linkableUmlShapes: LinkableUmlShapes) -> UmlClass:
        """
        This method is necessary because the linkable shapes dictionary is index by the PyutClass ID
        However, the pointer to the attached class is a UmlClass id.  All this came about because
        lollipops reused the PyutInterface class

        Args:
            attachedToId:
            linkableUmlShapes:

        Returns:  The appropriate UmlClass

        """
        foundClass: UmlClass = cast(UmlClass, None)
        for uc in linkableUmlShapes.values():
            umlClass: UmlClass = cast(UmlClass, uc)
            if umlClass.id == attachedToId:
                foundClass = umlClass
                break

        assert foundClass is not None, 'Developer error, missing class in linkableUmlShapes'
        return foundClass
