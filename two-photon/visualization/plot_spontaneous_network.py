import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import random
import json
import os
import pickle
import networkx as nx

# load what we need from the config file
with open(os.path.abspath(os.path.dirname(__file__)) +'/../../config.json','r') as f:
    config = json.load(f)

BASE_PATH = config['RecordingFolder'] # folder with all of the files generated by Suite2P for this recording (F.npy, iscell.npy, etc)
cell_dictionary_file = config['AnalysisFile']

def plot_events(cell_trace,events):
    for i in range(len(events[0])):
        plt.axvline(x=events[0][i])
    
    plt.plot(cell_trace,linewidth=2,color='black')
    plt.show()

def main():

    with open(BASE_PATH+"corrcoefs.pkl",'rb') as f:
        coeffs = pickle.load(f)

    # load our dictionary
    with open(BASE_PATH + cell_dictionary_file, 'rb') as f:
        cell_dict = pickle.load(f)

    coeffs[coeffs>0.99] = 0

    g = nx.Graph()
    c = coeffs

    # for cell in cell_dict:
    #     plt.plot(cell_dict[cell]['x'],cell_dict[cell]['y'],marker='o')

    # plt.show()

    cell_IDs_list = list(cell_dict.keys())

    correlations = []
    for cell_idx_i in range(len(c)):
        for cell_idx_j in range(len(c)):
            if c[cell_idx_i,cell_idx_j] > 0.2:
                correlations.append(c[cell_idx_i,cell_idx_j])

            if c[cell_idx_i,cell_idx_j] > 0.3:

                cell1_ID = cell_IDs_list[cell_idx_i]
                cell1_x = cell_dict[cell1_ID]['x']
                cell1_y = cell_dict[cell1_ID]['y']
                g.add_node(cell1_ID,pos = (cell1_x,cell1_y))

                cell2_ID = cell_IDs_list[cell_idx_j]
                cell2_x = cell_dict[cell2_ID]['x']
                cell2_y = cell_dict[cell2_ID]['y']
                g.add_node(cell2_ID,pos = (cell2_x,cell2_y))

                g.add_edge(cell1_ID,cell2_ID)
                
            # else:
            #     cell_ID = cell_IDs_list[cell_idx_i]
            #     cell_x = cell_dict[cell_ID]['x']
            #     cell_y = cell_dict[cell_ID]['y']
            #     g.add_node(cell_ID,pos=(cell_x,cell_y),color="red")

    node_color = []
    node_counter = 0
    for node in g:

        if g.degree(node) == 0 :
            node_color.append('black')

        else:
            node_color.append('red')

        node_counter += 1

    print("Number of connected components: ")
    print(nx.number_connected_components(g))
    print("Number total edges: ")
    print(g.number_of_edges())
    print("Number of nodes: ")
    print(g.number_of_nodes())

    plt.figure()
    plt.title("Post-Psilocybin Correlated Spontaneous Activity (c>0.2)")
    #pos = nx.get_node_attributes(g,'pos')
    pos = nx.circular_layout(g)
    nx.draw(g,pos,node_color=node_color)
    plt.show()

    p = plt.hist(correlations,density=True)
    plt.xlabel("Correlation")
    plt.ylabel("Normalized number of correlations")
    plt.title("Post-saline Correlations")
    plt.show()

if __name__=="__main__":
    main()