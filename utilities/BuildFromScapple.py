''' Creates the graph database from a properly formatted json file '''
from py2neo import Graph, Node, Relationship
import sys
import xml.etree.ElementTree as etree

def add_nodes(xml_blob):
    ''' Add each Scapple "note" as a neo4j node '''
    label = 'option'
    node = Node(label, uid=int(xml_blob.get('ID')))
    for item in xml_blob.getchildren():
        if item.tag == 'Appearance' and len(item.findall('Border')):
            node.set_labels('turn')
        elif item.tag == 'String':
            node.properties['text'] = item.text
        elif item.tag == 'PointsToNoteIDs':
            # format is either '1, 2, 3' or '1-3'
            link_range = item.text.split(', ')
            links = []
            for value in link_range:
                if '-' in value:
                    value = value.split('-')
                    links += range(int(value[0]), int(value[1])+1)
                else:
                    links.append(int(value))
            if len(links) > 1:
                node.set_labels('prompt')
            node.properties['pointsTo'] = links

    GRAPH.create(node)

if __name__ == '__main__':
    GRAPH = Graph()
    XML = etree.parse(sys.argv[1])
    for note in XML.getroot().getchildren()[0].getchildren():
        add_nodes(note)

    # connect options to their following turn
    GRAPH.cypher.execute('MATCH n, m ' \
                         'WHERE m.uid IN n.pointsTo ' \
                         'CREATE (n) - [:to] -> (m)')

