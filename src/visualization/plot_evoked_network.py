import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import random
import json
import os
import pickle
import networkx as nx
from itertools import count

# load what we need from the config file
with open(os.path.abspath(os.path.dirname(__file__)) +'/../../config.json','r') as f:
    config = json.load(f)

BASE_PATH = config['RecordingFolder'] # folder with all of the files generated by Suite2P for this recording (F.npy, iscell.npy, etc)
cell_dictionary_file = config['AnalysisFile']

def get_node_BF(cell_dict, cell_ID,freqs):
    median_across_itsies = np.median(cell_dict[cell_ID]['tuning_curve_peak'], axis=1)
    max_response_idx = np.argmax(median_across_itsies)
    return freqs[max_response_idx]

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

    frequencies = [4.4,5.4,6.6,8.1,10,12,15,19,23,28,28,35,43]

    cell_IDs_list = list(cell_dict.keys())

    BFs = []
    correlations = []
    for cell_idx_i in range(len(c)):
        for cell_idx_j in range(len(c)):
            if c[cell_idx_i,cell_idx_j] > 0.2:
                correlations.append(c[cell_idx_i,cell_idx_j])

            if c[cell_idx_i,cell_idx_j] > 0.3:

                cell1_ID = cell_IDs_list[cell_idx_i]
                cell1_x = cell_dict[cell1_ID]['x']
                cell1_y = cell_dict[cell1_ID]['y']
                BF = get_node_BF(cell_dict,cell1_ID,frequencies)
                g.add_node(cell1_ID,pos = (cell1_x,cell1_y),freq=BF)
                BFs.append(BF)
                
                cell2_ID = cell_IDs_list[cell_idx_j]
                cell2_x = cell_dict[cell2_ID]['x']
                cell2_y = cell_dict[cell2_ID]['y']
                BF = get_node_BF(cell_dict,cell2_ID,frequencies)
                g.add_node(cell2_ID,pos = (cell2_x,cell2_y),freq=BF)
                BFs.append(BF)

                g.add_edge(cell1_ID,cell2_ID)
                
            # else:
            #     cell_ID = cell_IDs_list[cell_idx_i]
            #     cell_x = cell_dict[cell_ID]['x']
            #     cell_y = cell_dict[cell_ID]['y']
            #     g.add_node(cell_ID,pos=(cell_x,cell_y),freq=get_node_BF(cell_dict,cell_ID,frequencies))

    # node_color = []
    # node_counter = 0
    # for n,outer_d in g.nodes(data=True):

    #     if g.degree(n) == 0 :
    #         n['freq'] = 0

    #     # else:
    #     #     node_color.append('red')

    #     # node_counter += 1

    print("Number of dictionary keys: ")
    print(len(cell_dict.keys()))

    print("Number of graph nodes: ")
    print(g.number_of_nodes())

    groups = set(nx.get_node_attributes(g,'freq').values())
    mapping = dict(zip(sorted(groups),count()))
    nodes = g.nodes()
    colors = [mapping[g.nodes[n]['freq']] for n in nodes]

    plt.figure()
    plt.title("Post-Psilocybin Correlated Spontaneous Activity (c>0.3)")
    #pos = nx.circular_layout(g)
    pos = nx.get_node_attributes(g,'pos')
    ec = nx.draw_networkx_edges(g,pos,alpha=0.2)
    nc = nx.draw_networkx_nodes(g, pos, nodelist=nodes,node_color=colors,node_size=100, cmap=plt.cm.jet_r)
    cbar = plt.colorbar(nc,ticks=range(len(mapping)))
    cbar.ax.set_yticklabels(mapping.keys())
    cbar.ax.set_title("Best Frequency")
    plt.axis('off')
    plt.show()

    p = plt.hist(correlations,density=True)
    plt.xlabel("Correlation")
    plt.ylabel("Normalized number of correlations")
    plt.title("Post-psilocybin Correlations")
    plt.show()

    p = plt.hist(BFs,density=True)
    plt.show()

if __name__=="__main__":
    main()