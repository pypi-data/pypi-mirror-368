#!/usr/bin/env python
"""
This work is made available under the Apache License, Version 2.0.

You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.
"""

from typing import List, Optional, Any, Dict, Union
from dataclasses import dataclass, field
import xml.dom.minidom
import datetime

__author__ = 'Atualizado por Cristiano Ritta (tiano.ritta@gmail.com) - original:Petter Chr. Bjelland (petter.bjelland@gmail.com)'
__updated_by__ = 'Atualizado para Python 3.11'

class XMLSerializable:
    """Base class for objects that can be serialized to XML."""
    
    def toxml(self, namespacedef_=None):
        """Convert object to XML string."""
        doc = xml.dom.minidom.Document()
        root_node = self._to_element(doc)
        doc.appendChild(root_node)
        xml_str = doc.toprettyxml(indent="  ", encoding="utf-8")
        return xml_str.decode('utf-8')
    
    def _to_element(self, doc):
        """Convert object to XML element."""
        raise NotImplementedError("Subclasses must implement _to_element")


@dataclass
class FrameStyle(XMLSerializable):
    Colour: Optional[int] = None
    Visible: Optional[int] = None
    Margin: Optional[int] = None
    
    def _to_element(self, doc):
        element = doc.createElement('FrameStyle')
        if self.Colour is not None:
            element.setAttribute('Colour', str(self.Colour))
        if self.Visible is not None:
            element.setAttribute('Visible', str(self.Visible))
        if self.Margin is not None:
            element.setAttribute('Margin', str(self.Margin))
        return element


@dataclass
class IconStyle(XMLSerializable):
    Type: str
    FrameStyle: Optional[FrameStyle] = None
    
    def _to_element(self, doc):
        element = doc.createElement('IconStyle')
        element.setAttribute('Type', self.Type)
        if self.FrameStyle:
            element.appendChild(self.FrameStyle._to_element(doc))
        return element


@dataclass
class Icon(XMLSerializable):
    IconStyle: IconStyle
    
    def _to_element(self, doc):
        element = doc.createElement('Icon')
        element.appendChild(self.IconStyle._to_element(doc))
        return element


@dataclass
class Entity(XMLSerializable):
    Icon: Icon
    EntityId: str
    Identity: str
    
    def _to_element(self, doc):
        element = doc.createElement('Entity')
        element.setAttribute('EntityId', self.EntityId)
        element.setAttribute('Identity', self.Identity)
        element.appendChild(self.Icon._to_element(doc))
        return element


@dataclass
class End(XMLSerializable):
    X: int
    Y: int
    Entity: Entity
    
    def _to_element(self, doc):
        element = doc.createElement('End')
        element.setAttribute('X', str(self.X))
        element.setAttribute('Y', str(self.Y))
        element.appendChild(self.Entity._to_element(doc))
        return element


@dataclass
class TimeZone(XMLSerializable):
    Name: str
    UniqueID: int
    
    def _to_element(self, doc):
        element = doc.createElement('TimeZone')
        element.setAttribute('Name', self.Name)
        element.setAttribute('UniqueID', str(self.UniqueID))
        return element


@dataclass
class LinkStyle(XMLSerializable):
    StrengthReference: str
    Type: str
    ArrowStyle: str
    LineColour: int
    MlStyle: str
    
    def _to_element(self, doc):
        element = doc.createElement('LinkStyle')
        element.setAttribute('StrengthReference', self.StrengthReference)
        element.setAttribute('Type', self.Type)
        element.setAttribute('ArrowStyle', self.ArrowStyle)
        element.setAttribute('LineColour', str(self.LineColour))
        element.setAttribute('MlStyle', self.MlStyle)
        return element


@dataclass
class Link(XMLSerializable):
    End1Id: str
    End2Id: str
    LinkStyle: LinkStyle
    
    def _to_element(self, doc):
        element = doc.createElement('Link')
        element.setAttribute('End1Id', self.End1Id)
        element.setAttribute('End2Id', self.End2Id)
        element.appendChild(self.LinkStyle._to_element(doc))
        return element


@dataclass
class ChartItem(XMLSerializable):
    Label: str
    Description: str = ""
    XPosition: Optional[int] = None
    End: Optional[End] = None
    Link: Optional[Link] = None
    _DateTime: Optional[datetime.datetime] = None
    _TimeZone: Optional[TimeZone] = None
    _DateTimeDescription: Optional[str] = None
    _DateSet: bool = False
    _TimeSet: bool = False
    
    def set_DateTime(self, dt):
        self._DateTime = dt
        
    def set_TimeZone(self, tz):
        self._TimeZone = tz
        
    def set_DateTimeDescription(self, desc):
        self._DateTimeDescription = desc
        
    def set_DateSet(self, val):
        self._DateSet = val
        
    def set_TimeSet(self, val):
        self._TimeSet = val
    
    def _to_element(self, doc):
        element = doc.createElement('ChartItem')
        element.setAttribute('Label', self.Label)
        
        if self.XPosition is not None:
            element.setAttribute('XPosition', str(self.XPosition))
            
        if self.Description:
            desc_elem = doc.createElement('Description')
            desc_elem.appendChild(doc.createTextNode(self.Description))
            element.appendChild(desc_elem)
            
        if self.End:
            element.appendChild(self.End._to_element(doc))
            
        if self.Link:
            element.appendChild(self.Link._to_element(doc))
            
        if self._DateTime:
            dt_elem = doc.createElement('DateTime')
            # Format date to ISO format
            dt_str = self._DateTime.strftime('%Y-%m-%dT%H:%M:%S')
            dt_elem.appendChild(doc.createTextNode(dt_str))
            element.appendChild(dt_elem)
            
            if self._DateSet:
                element.setAttribute('DateSet', 'True')
                
            if self._TimeSet:
                element.setAttribute('TimeSet', 'True')
                
            if self._DateTimeDescription:
                dt_desc = doc.createElement('DateTimeDescription')
                dt_desc.appendChild(doc.createTextNode(self._DateTimeDescription))
                element.appendChild(dt_desc)
                
            if self._TimeZone:
                element.appendChild(self._TimeZone._to_element(doc))
                
        return element


@dataclass
class ChartItemCollection(XMLSerializable):
    ChartItems: List[ChartItem] = field(default_factory=list)
    
    def add_ChartItem(self, item):
        self.ChartItems.append(item)
        
    def _to_element(self, doc):
        element = doc.createElement('ChartItemCollection')
        for item in self.ChartItems:
            element.appendChild(item._to_element(doc))
        return element


@dataclass
class EntityType(XMLSerializable):
    Name: str
    IconFile: str
    
    def _to_element(self, doc):
        element = doc.createElement('EntityType')
        element.setAttribute('Name', self.Name)
        element.setAttribute('IconFile', self.IconFile)
        return element


@dataclass
class EntityTypeCollection(XMLSerializable):
    EntityTypes: List[EntityType] = field(default_factory=list)
    
    def add_EntityType(self, entity_type):
        self.EntityTypes.append(entity_type)
        
    def _to_element(self, doc):
        element = doc.createElement('EntityTypeCollection')
        for entity_type in self.EntityTypes:
            element.appendChild(entity_type._to_element(doc))
        return element


@dataclass
class LinkType(XMLSerializable):
    Name: str
    
    def _to_element(self, doc):
        element = doc.createElement('LinkType')
        element.setAttribute('Name', self.Name)
        return element


@dataclass
class LinkTypeCollection(XMLSerializable):
    LinkTypes: List[LinkType] = field(default_factory=list)
    
    def add_LinkType(self, link_type):
        self.LinkTypes.append(link_type)
        
    def _to_element(self, doc):
        element = doc.createElement('LinkTypeCollection')
        for link_type in self.LinkTypes:
            element.appendChild(link_type._to_element(doc))
        return element


@dataclass
class Strength(XMLSerializable):
    DotStyle: str
    Name: str
    Id: str
    
    def _to_element(self, doc):
        element = doc.createElement('Strength')
        element.setAttribute('DotStyle', self.DotStyle)
        element.setAttribute('Name', self.Name)
        element.setAttribute('Id', self.Id)
        return element


@dataclass
class StrengthCollection(XMLSerializable):
    Strengths: List[Strength]
    
    def _to_element(self, doc):
        element = doc.createElement('StrengthCollection')
        for strength in self.Strengths:
            element.appendChild(strength._to_element(doc))
        return element


@dataclass
class Chart(XMLSerializable):
    IdReferenceLinking: bool
    EntityTypeCollection: Optional[EntityTypeCollection] = None
    LinkTypeCollection: Optional[LinkTypeCollection] = None
    ChartItemCollections: List[ChartItemCollection] = field(default_factory=list)
    StrengthCollection: Optional[StrengthCollection] = None
    
    def add_EntityTypeCollection(self, collection):
        self.EntityTypeCollection = collection
        
    def add_LinkTypeCollection(self, collection):
        self.LinkTypeCollection = collection
        
    def add_ChartItemCollection(self, collection):
        self.ChartItemCollections.append(collection)
        
    def add_StrengthCollection(self, collection):
        self.StrengthCollection = collection
        
    def _to_element(self, doc):
        element = doc.createElement('Chart')
        element.setAttribute('IdReferenceLinking', str(self.IdReferenceLinking).lower())
        
        if self.EntityTypeCollection:
            element.appendChild(self.EntityTypeCollection._to_element(doc))
            
        if self.LinkTypeCollection:
            element.appendChild(self.LinkTypeCollection._to_element(doc))
            
        if self.StrengthCollection:
            element.appendChild(self.StrengthCollection._to_element(doc))
            
        for collection in self.ChartItemCollections:
            element.appendChild(collection._to_element(doc))
            
        return element

