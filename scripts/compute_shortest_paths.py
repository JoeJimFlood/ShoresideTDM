import numpy as np
import pandas as pd
import os
import time
from datetime import datetime, timedelta
import openmatrix as omx

class node:
    def __init__(self, id, x, y, cycle_length):
        '''
        Defines node based on x-y coordinates
        
        Arguments:
            x (float): x-coordinate of node
            y (float): y-coordinate of node
            id: Identification
        '''
        self.x = x
        self.y = y
        self.id = id
        self.cycle_length = cycle_length
        self.olinks = []
        self.dlinks = []

    def __repr__(self):
        return 'Node {0} at ({1}, {2})'.format(self.id, self.x, self.y)

class link:
    def __init__(self, origin, destination, id, ffs):
        '''
        Creates a link between two nodes, with a specified volume-delay function

        Arguments:
            origin (Node): Link's origin node
            destination (node): Link's destination node
            id (int): Link ID
        '''
        self.origin = origin
        self.destination = destination
        self.id = id

        o = np.array([origin.x, origin.y])
        d = np.array([destination.x, destination.y])
        u = d - o
        self.length = np.linalg.norm(u)
        self.direction = u/self.length
        self.angle = np.angle(u[0] + 1j*u[1])
        
        self.ffs = ffs
        self.travel_time = (60 * self.length / self.ffs) + (destination.cycle_length / 120)

        self.origin.olinks.append(self)
        self.destination.dlinks.append(self)

    def __repr__(self):
        return 'Link {0} from Node {1} to Node {2}'.format(self.id, self.origin.id, self.destination.id)

class network:
    def __init__(self, links):
        '''
        Creates a network of links

        Arguments:
            links (list): List of links
        '''
        self.links = links
        nodes = []
        for l in links:
            if l.origin not in nodes:
                nodes.append(l.origin)
            if l.destination not in nodes:
                nodes.append(l.destination)
        #nodes.sort()
        self.nodes = nodes
        self.prohibited_movements = {}

    def prohibit_movements(self, movement_file):
        '''

        '''
        movements = pd.read_csv(movement_file)
        prohibited_movements = {}
        for m in movements[movements['prohibited_flag'] == 1].index:
            first = movements.loc[m, 'up_node_id']
            second = movements.loc[m, 'node_id']
            third = movements.loc[m, 'dest_node_id']
            link1 = self.find_connector(self.find_node(first), self.find_node(second))
            link2 = self.find_connector(self.find_node(second), self.find_node(third))
            if link1 not in prohibited_movements:
                prohibited_movements[link1] = []
            prohibited_movements[link1].append(link2)
        self.prohibited_movements = prohibited_movements

    def find_connector(self, origin, destination):
        '''
        Finds the link between an origin and destination. Assumes only one such link exists.

        Arguments:
            origin (node): Origin node
            destination (node): Destination node

        Returns:
            connecting_link (node): Link connecting nodes.
        '''
        possible_links = origin.olinks
        for l in possible_links:
            if l.destination == destination:
                connecting_link = l
                break
        try:
            return connecting_link
        except UnboundLocalError:
            print('WARNING: No link found connecting nodes {0} and {1}'.format(origin.id, destination.id))
            return None

    def get_adjacent_nodes(self, origin):
        '''
        Finds the nodes adjacent to an origin node

        Arguments:
            origin (int): The index of a node to find adjacent nodes

        Returns:
            adjacent_nodes (list): List of adjacent nodes
        '''
        adjacent_nodes = []
        for olink in origin.olinks:
            adjacent_nodes.append(olink.destination)
        return adjacent_nodes

    def get_shortest_route(self, origin, destination):
        '''
        Finds the shortest route between two nodes on the network using Dijkstra's algorithm
        '''
        visited = []

        paths = {}
        node_costs = {}
        for n in self.nodes:
            if n == origin:
                node_costs[n] = 0
            else:
                node_costs[n] = np.inf
            paths[n] = []

        #Origin node
        for l in origin.olinks:
            node_costs[l.destination] = l.travel_time
            paths[l.destination] += [origin]

        visited.append(origin)
        can_visit = self.get_adjacent_nodes(origin)

        for n in can_visit:
            visited.append(n)
            for l in n.olinks:
                c = node_costs[n] + l.travel_time
                if c < node_costs[l.destination]:
                    node_costs[l.destination] = c
                    paths[l.destination] = paths[l.origin] + [l.origin]
                        
            new_nodes = self.get_adjacent_nodes(n)
            for nn in new_nodes:
                if nn not in can_visit and nn not in visited:
                    can_visit.append(nn)

        paths[destination] += [destination]
        path_length = len(paths[destination]) - 1

        shortest_route = []
        for i in range(path_length):
            shortest_route.append(self.find_connector(paths[destination][i], paths[destination][i+1]))

        return shortest_route

    def find_node(self, id):
        '''
        Finds a node in the network with the specified id
        '''
        for n in self.nodes:
            if n.id == id:
                break

        return n

    @classmethod
    def from_files(cls, node_file, link_file):
        '''

        '''
        nodes = []
        node_df = pd.read_csv(node_file)
        for n in node_df.index:
            id = node_df.loc[n, 'node_id']
            x = node_df.loc[n, 'x']
            y = node_df.loc[n, 'y']
            cycle_length = node_df.loc[n, 'cycle_length_in_second']
            nodes.append(node(id, x, y, cycle_length))

        links = []
        link_df = pd.read_csv(link_file, encoding = 'ISO-8859-1')
        for l in link_df.index:
            origin_node_id = link_df.loc[l, 'from_node_id']
            destination_node_id = link_df.loc[l, 'to_node_id']

            found_origin = False
            found_destination = False
            for n in nodes:
                if n.id == origin_node_id:
                    origin = n
                    found_origin = True
                elif n.id == destination_node_id:
                    destination = n
                    found_destination = True
                if found_origin and found_destination:
                    break

            id = link_df.loc[l, 'link_id']
            ffs = link_df.loc[l, 'speed_limit']

            try:
                links.append(link(origin, destination, id, ffs))
            except UnboundLocalError:
                import pdb
                pdb.set_trace()

        

        return cls(links)

BASE_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
NODE_FILE = os.path.join(BASE_PATH, r'DTA_Base\input_node.csv')
LINK_FILE = NODE_FILE.replace('node', 'link')
NODE_INFO_FILE = os.path.join(BASE_PATH, 'Network', 'node_info.csv')
MOVEMENT_FILE = LINK_FILE.replace('link', 'movement')
OUTPUT_FILE = os.path.join(BASE_PATH, r'Network\shortest_paths.omx')

Shoreside = network.from_files(NODE_FILE, LINK_FILE)
node_info = pd.read_csv(NODE_INFO_FILE)
activity_nodes = list(node_info[node_info['Type'] > 0]['Node'])
external_nodes = list(node_info[node_info['Type'] == 4]['Node'])

node_ids = [n.id for n in Shoreside.nodes]
link_ids = [l.id for l in Shoreside.links]

shortest_paths = pd.Panel(np.zeros((len(link_ids), len(activity_nodes), len(activity_nodes)), np.uint8),
                          items = link_ids, major_axis = activity_nodes, minor_axis = activity_nodes)

N = len(activity_nodes)**2

i = 0
current_percent = 0

time_stamp = time.time()
start_time = datetime.now()

percent_times = np.array([])

for onode_id in activity_nodes:
    for dnode_id in activity_nodes:

        i += 1

        if 100*i//N > current_percent:
            
            current_percent += 1
            percent_stamp = time.time()
            average_time = (percent_stamp - time_stamp) / current_percent
            projected_runtime = 100*average_time
            projected_end = start_time + timedelta(seconds = projected_runtime)
            
            print('{0}%, {1}'.format(current_percent, projected_end.strftime('%d %B %Y %H:%M:%S')))

        if onode_id == dnode_id:
            continue

        if onode_id not in external_nodes and dnode_id not in external_nodes:
            continue

        onode = Shoreside.find_node(onode_id)
        dnode = Shoreside.find_node(dnode_id)

        path = Shoreside.get_shortest_route(onode, dnode)
        for link_path in path:
            shortest_paths.ix[link_path.id, onode.id, dnode.id] = 1

write_start = time.time()
f = omx.open_file(OUTPUT_FILE, 'w')
f.create_mapping('Nodes', activity_nodes)
for link_id in link_ids:
    f['Link{}'.format(link_id)] = shortest_paths[link_id].values
f.close()
write_end = time.time()
write_time = write_end - write_start
print('File written in {} seconds'.format(round(write_time, 1)))

print('Shortest paths computed')