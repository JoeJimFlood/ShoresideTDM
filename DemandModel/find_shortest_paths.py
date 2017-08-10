import numpy as np
import pandas as pd
import os

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
        return connecting_link

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
            #print n.id
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
        link_df = pd.read_csv(link_file, encoding = "ISO-8859-1")
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

NODE_FILE = r'D:\ShoresideTDM\TimePeriods\AM\input_node.csv'
LINK_FILE = NODE_FILE.replace('node', 'link')
Shoreside = network.from_files(NODE_FILE, LINK_FILE)

TIME_PERIOD_FILE = r'D:\ShoresideTDM\Network\TimePeriods.csv'
time_periods = pd.read_csv(TIME_PERIOD_FILE)

links = pd.read_csv(LINK_FILE, encoding = 'ISO-8859-1')

for period in time_periods.index:
    name = time_periods.loc[period, 'Period']
    dta = time_periods.loc[period, 'DTA']
    if not dta:
        
        TRIP_TABLE_FILE = r'D:\ShoresideTDM\TimePeriods\{}\trip_table.csv'.format(name)
        trip_table = pd.read_csv(TRIP_TABLE_FILE, index_col = 0)

        flows = pd.Series(np.zeros_like(links.index), links['link_id'], dtype = np.float64)

        for onode in trip_table.index:
            for dnode in trip_table.columns:
                if trip_table.loc[onode, dnode]:
                    origin = Shoreside.find_node(onode)
                    destination = Shoreside.find_node(int(dnode))
                    route = Shoreside.get_shortest_route(origin, destination)

                    for l in route:
                        flows[l.id] += trip_table.loc[onode, dnode]

        raise Exception