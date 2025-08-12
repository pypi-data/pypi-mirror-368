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

import random
import datetime
from typing import Dict, List, Tuple, Optional, Any, Union

# Import relativo dentro do pacote
from . import anx

__author__ = 'Petter Chr. Bjelland (petter.bjelland@gmail.com)'
__updated_by__ = 'Updated for Python 3.11'


class Pyanx:
    def __init__(self, ring_margin: int = 5):
        """
        Initialize a new Pyanx instance.
        
        Args:
            ring_margin: Margin for entity rings in pixels
        """
        self.entity_types: Dict[str, bool] = {}
        self.edges: List[Tuple[str, str, Dict[str, Any]]] = []
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.timezones: Dict[str, int] = {}
        self.ring_margin: int = ring_margin

    def add_node(
        self,
        entity_type: str = 'Anon',
        label: Optional[str] = None,
        ring_color: Optional[int] = None,
        description: str = '',
        datestr: Optional[str] = None,
        datestr_description: Optional[str] = None,
        dateformat: str = '%Y-%m-%dT%H:%M:%S',
        timezone: Optional[str] = None
    ) -> str:
        """
        Add a node to the chart.
        
        Args:
            entity_type: Type of entity
            label: Label for the node
            ring_color: Color of the ring around node
            description: Description of the node
            datestr: Date string in dateformat
            datestr_description: Description of the date
            dateformat: Format of the datestr
            timezone: Timezone of the date
            
        Returns:
            The node ID (label)
        """
        current_id = label

        if timezone and timezone not in self.timezones:
            self.timezones[timezone] = len(self.timezones)

        if entity_type not in self.entity_types:
            self.entity_types[entity_type] = True

        if datestr:
            _datetime = datetime.datetime.strptime(datestr, dateformat)
        else:
            _datetime = None

        self.nodes[current_id] = {
            'entity_type': entity_type,
            'label': label,
            'ring_color': ring_color,
            'description': description,
            'datetime': _datetime,
            'datetime_description': datestr_description,
            'timezone': timezone
        }

        return current_id

    def add_edge(
        self,
        source: str,
        sink: str,
        label: str = '',
        color: int = 0,
        style: str = 'Solid',
        description: str = '',
        datestr: Optional[str] = None,
        datestr_description: Optional[str] = None,
        dateformat: str = '%Y-%m-%dT%H:%M:%S',
        timezone: Optional[str] = None
    ) -> None:
        """
        Add an edge to the chart.
        
        Args:
            source: Source node ID
            sink: Sink node ID
            label: Label for the edge
            color: Color of the edge
            style: Style of the edge
            description: Description of the edge
            datestr: Date string in dateformat
            datestr_description: Description of the date
            dateformat: Format of the datestr
            timezone: Timezone of the date
        """
        if datestr:
            _datetime = datetime.datetime.strptime(datestr, dateformat)
        else:
            _datetime = None

        if timezone and timezone not in self.timezones:
            self.timezones[timezone] = len(self.timezones)

        self.edges.append((source, sink, {
            'label': label,
            'color': color,
            'style': style,
            'description': description,
            'datetime': _datetime,
            'datetime_description': datestr_description,
            'timezone': timezone
        }))

    def __add_entity_types(self, chart: anx.Chart) -> None:
        """Add entity types to the chart."""
        entity_type_collection = anx.EntityTypeCollection()

        for entity_type in self.entity_types:
            entity_type_collection.add_EntityType(anx.EntityType(Name=entity_type, IconFile=entity_type))

        chart.add_EntityTypeCollection(entity_type_collection)

    def __add_link_types(self, chart: anx.Chart) -> None:
        """Add link types to the chart."""
        link_type_collection = anx.LinkTypeCollection()
        link_type_collection.add_LinkType(anx.LinkType(Name="Link"))
        chart.add_LinkTypeCollection(link_type_collection)

    def __set_date(self, chart_item: anx.ChartItem, data: Dict[str, Any]) -> None:
        """Set date information on a chart item."""
        if not data['datetime']:
            return

        chart_item.set_DateTime(data['datetime'])

        if data['timezone']:
            chart_item.set_TimeZone(anx.TimeZone(data['timezone'], UniqueID=self.timezones[data['timezone']]))

        chart_item.set_DateTimeDescription(data['datetime_description'])
        chart_item.set_DateSet(True)
        chart_item.set_TimeSet(True)

    def __add_entities(self, chart: anx.Chart) -> None:
        """Add entities to the chart."""
        chart_item_collection = anx.ChartItemCollection()

        for data in self.nodes.values():
            circle = None

            if data['ring_color']:
                circle = anx.FrameStyle(Colour=data['ring_color'], Visible=1, Margin=self.ring_margin)

            x, y = (random.randint(0, 1000), random.randint(0, 1000))

            icon = anx.Icon(IconStyle=anx.IconStyle(Type=data['entity_type'], FrameStyle=circle))
            entity = anx.Entity(Icon=icon, EntityId=data['label'], Identity=data['label'])
            chart_item = anx.ChartItem(
                XPosition=x, 
                Label=data['label'], 
                End=anx.End(X=x, Y=y, Entity=entity), 
                Description=data['description']
            )

            self.__set_date(chart_item, data)

            chart_item_collection.add_ChartItem(chart_item)

        chart.add_ChartItemCollection(chart_item_collection)

    def __add_links(self, chart: anx.Chart) -> None:
        """Add links to the chart."""
        chart_item_collection = anx.ChartItemCollection()

        for source, sink, data in self.edges:
            link_style = anx.LinkStyle(
                StrengthReference=data['style'], 
                Type='Link', 
                ArrowStyle='ArrowOnHead', 
                LineColour=data['color'], 
                MlStyle="MultiplicityMultiple"
            )
            link = anx.Link(End1Id=source, End2Id=sink, LinkStyle=link_style)

            chart_item = anx.ChartItem(Label=data['label'], Link=link, Description=data['description'])

            self.__set_date(chart_item, data)

            chart_item_collection.add_ChartItem(chart_item)

        chart.add_ChartItemCollection(chart_item_collection)

    def create(self, path: str, pretty: bool = True, encoding: str = 'utf8') -> None:
        """
        Create the chart file.
        
        Args:
            path: Path to save the chart file
            pretty: Whether to use pretty printing
            encoding: File encoding
        """
        chart = anx.Chart(IdReferenceLinking=False)
        chart.add_StrengthCollection(anx.StrengthCollection([
            anx.Strength(DotStyle="DotStyleDashed", Name="Dashed", Id="Dashed"),
            anx.Strength(DotStyle="DotStyleSolid", Name="Solid", Id="Solid")
        ]))

        self.__add_entity_types(chart)
        self.__add_link_types(chart)
        self.__add_entities(chart)
        self.__add_links(chart)

        with open(path, 'w', encoding=encoding) as output_file:
            # Usando a função toxml do Chart para obter o XML
            xml_str = chart.toxml()
            # Removendo formatações indesejadas
            xml_str = xml_str.replace('<?xml version="1.0" encoding="utf-8"?>', '')
            output_file.write(xml_str.strip())

