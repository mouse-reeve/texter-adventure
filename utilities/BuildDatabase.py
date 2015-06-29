''' Creates the graph database from a properly formatted json file '''
import json
import logging
from py2neo import Graph, Node, Relationship
import sys

def add_turn(turn):
    ''' loads the json turn info into neo4j '''
    if not ('id' in turn and 'text' in turn and 'options' in turn):
        logging.error('Turn json is missing a field')
        return

    turn_node = Node('turn', text=turn['text'], uid=turn['id'])
    data = [turn_node]

    for option in turn['options']:
        option_node = Node('option', text=option['text'], destination=option['destination'])
        edge = Relationship(turn_node, "TO", option_node)
        data.append(option_node)
        data.append(edge)

    for node in data:
        GRAPH.create(node)

if __name__ == '__main__':
    GRAPH = Graph()
    TURNS = json.load(open(sys.argv[1], 'r'))

    # add turn and option data
    for turn_json in TURNS:
        add_turn(turn_json)

    # connect options to their following turn
    GRAPH.cypher.execute('MATCH (o:option), (t:turn) '
                         'WHERE t.uid = o.destination '
                         'CREATE (o) - [:THEN] -> (t)')

