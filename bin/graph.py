#!/usr/bin/env python

IMPORT_FLAG = False

try:
    import subprocess
    import argparse
    import sys
    import os
    import pydot
    import ast
    import networkx as nx
    import matplotlib.pyplot as plt
except ImportError:
    IMPORT_FLAG = True

def main():
    args = get_args()

    if args.filename != None:
        read_file   = open(args.filename, mode='r')
        node_string = read_file.readline()
        edge_string = read_file.readline()
        node_list   = ast.literal_eval(node_string)
        edge_list   = ast.literal_eval(edge_string)
    else:
        node_list, edge_list = create_list(args)
        print len(node_list)
        print len(edge_list)

    if IMPORT_FLAG == False and args.networkx is True:
        graph = nx.Graph()
        print 'Initializing'
        size_list = []
        clean_node_list = []
        for item in node_list:
            nodesize = 300
            for edge in edge_list:
                if item == edge[1]:
                    nodesize += 100
            size_list.append(nodesize)
            clean_node_list.append(os.path.basename(item))
        graph.add_nodes_from(clean_node_list)
        print 'Nodes set'
        for item in edge_list:
            from_node = os.path.basename(item[1])
            to_node = os.path.basename(item[0])
            graph.add_edge(from_node, to_node)
        print 'Edges set'
        print 'Creating Graph'
        position = nx.spring_layout(graph)
        for item in position:
            position[item] *= 10
        nx.draw_networkx(graph,
                         pos=position,
                         font_size=10,
                         node_size=size_list)
        print 'Drawing Graph'
        plt.show()
        print 'DONE'
    elif IMPORT_FLAG == False and args.graphviz is True:
        directorygraph = create_graph(node_list, edge_list, args)
        directorygraph.write('directory.dot')
    elif IMPORT_FLAG:
        print 'ERROR - The library pydot is not installed. Writing to file'
        write_file = open('graph.txt', mode='w')
        write_file.write(str(node_list))
        write_file.write('\n')
        write_file.write(str(edge_list))
        write_file.close()
    if args.write:
        write_file = open('graph.txt', mode='w')
        write_file.write(str(node_list))
        write_file.write('\n')
        write_file.write(str(edge_list))
        write_file.close()

def create_graph(node_list, edge_list, args):

    directorygraph = pydot.Dot(graph_type='digraph', overlap='false')

    for item in node_list:
        node_size = 0.0
        for edge in edge_list:
            if item == edge[1]:
                node_size += 0.1
        node_name = os.path.basename(item)
        if node_name == '':
            pass
        else:
            if os.path.islink(item):
                node = pydot.Node(node_name,
                                  style='filled',
                                  shape='circle',
                                  fontsize='%f' %(5 + 5 * node_size),
                                  fixedsize='true',
                                  fillcolor='red')
            else:
                node = pydot.Node(node_name,
                                  style='filled',
                                  shape='circle',
                                  fontsize='%f' %(5 + 5 * node_size),
                                  height='%f' %(.5 + node_size),
                                  width='%f' %(.75 + node_size),
                                  fixedsize='true',
                                  fillcolor='green')
            directorygraph.add_node(node)


    for item in edge_list:
        root = os.path.basename(item[1])
        if os.path.basename(item[1]) == '':
            root = args.directory
        edge = pydot.Edge(root,
                          os.path.basename(item[0]))
        directorygraph.add_edge(edge)

    return directorygraph


def create_list(args):

    print args

    node_list = []
    files = subprocess.Popen('find %s -maxdepth %i'
                             %(args.directory, args.level),
                             stdout=subprocess.PIPE,
                             shell=True)
    nodes = files.communicate()[0].splitlines()
    for item in nodes:
        if item == ' ':
            pass
        elif os.path.isdir(item) == False:
            pass
        else:
            node_list.append(item)
    node_list.append(args.directory)

    edge_list = []
    for item in node_list:
        if item in node_list:
            edge = [item, os.path.dirname(item)]
            edge_list.append(edge)
        if os.path.dirname(item) in node_list:
            edge = [item, os.path.dirname(item)]
            edge_list.append(edge)

    return node_list, edge_list


def get_args():
    parser = argparse.ArgumentParser(
        description='Create a graph from a directory tree')
    parser.add_argument('-d', '--directory', type=str,
                        default='./',
                        help='Directory to analyze')
    parser.add_argument('-f', '--filename', type=str,
                        default=None,
                        help='Sourcefile for node and edges')
    parser.add_argument('-w', '--write', action='store_true',
                        help='Write to a file?')
    parser.add_argument('-l', '--level', type=int,
                        default=5,
                        help='How many levels down?')
    parser.add_argument('-g', '--graphviz', action='store_true',
                        default=True,
                        help='''Generate graph using dot?
                              (Recommended for smaller graphs)''')
    parser.add_argument('-n', '--networkx', action='store_true',
                        default=None,
                        help='''Generate graph using NetworkX?
                              (Recommended for larger graphs)''')
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    sys.exit(main())
