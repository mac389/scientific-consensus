import random, math

import networkx as nx
import matplotlib.pyplot as plt 
import numpy as np 
import Graphics as artist

from awesome_print import ap 
from Scientist import Scientist
from matplotlib import rcParams

nodes = 80
degree = 3
duration = 50
curiosity = 0.01 #(can make this different for different scientists)
PRUNING = 0.1
'''
    Homophily vs. curiosity; Influencers
    Connections diappear randomly
'''

rcParams['text.usetex'] = True
degree_sequence = lambda g: sorted(nx.degree(g).values(),reverse=True)

def degrees(g):
	degs = nx.degree(g)
	return [degs[node] for node in xrange(nodes)]

def get_attr(idx,field):
	return eval('g.node[%d].%s'%(idx,field))

def get_weighted_estimate(idx):
	return eval('g.node')

#Connect scientists; initially barabasi-albert then evolves by similarity
#g = nx.barabasi_albert_graph(nodes,degree)
g = nx.erdos_renyi_graph(nodes,degree/float(nodes))
for node_idx in xrange(nodes):
	g.node[node_idx] = Scientist(label=str(node_idx))

initial_degree_sequence = degree_sequence(g)
artist.save_graph(g,filename='initial-topology') #Default PNG, add TIFF later

field_estimate = np.zeros((nodes,duration))
centralities = np.zeros((nodes,duration))
target = random.choice(xrange(nodes))
communicabilities = np.zeros((nodes,duration))
degree_rec = np.zeros((nodes,duration))
for t in xrange(duration):
	for idx in xrange(nodes):
		neighbor_opinion = 0 if len(g.neighbors(idx))>0 else np.nan_to_num(np.nanmean([g.node[x].estimate_of_pi for x in g.neighbors(idx)]))
		actual_error = np.pi-get_attr(idx,'estimate_of_pi')
		
		g.node[idx].consensus = abs(get_attr(idx,'estimate_of_pi') - neighbor_opinion)/np.pi

		adjustment = get_attr(idx,'adjustment')
		anchor = get_attr(idx,'anchor')
		homophily = get_attr(idx,'homophily')

		#Adjust scientists bias based on a combination of neighbor opinion and actual results
		g.node[idx].anchor = (1-adjustment) * anchor + adjustment*(homophily*neighbor_opinion + (1-homophily)*actual_error)/np.pi
	
		#Homophily
		partner = random.choice(xrange(nodes))
		if all([random.random() < homophily,
				idx != partner,
				random.random() > abs(get_attr(idx,'estimate_of_pi')-get_attr(partner,'estimate_of_pi'))]):
			g.add_edge(idx,partner) 
		
		#Curiosity
		partner = random.choice(xrange(nodes))		
		if random.random() < curiosity:
			random.choice(xrange(nodes))
			if partner != idx:
				g.add_edge(idx,partner)
				
		#Randomly remove edges 
		if len(g.neighbors(idx)) > 0 and random.random()<PRUNING:
			target = random.choice(g.neighbors(idx))
			g.remove_edge(idx,target)
			
		#Write articles
		g.node[idx].write_paper(t)

		#Do experiments
		g.node[idx].experiment()

		field_estimate[idx,t] = get_attr(idx,'estimate_of_pi')
		degree_rec[:,t] = degrees(g)
	#NetworkX degree centrality returns a dictionary of node:centrality

artist.save_graph(g,filename='after-topology')
artist.compare_degree_sequences(initial_degree_sequence,degree_sequence(g))

artist.my_boxplot([field_estimate[:,0],field_estimate[:,-1]],'distributions-of-estimates',
	ylabel=r'\Large \textbf{\textsc{Estimate of}} $\pi$',xticklabels=map(artist.format,['Before','After']))

artist.my_boxplot([degree_rec[:,0],degree_rec[:,-1]],'degrees',
	ylabel=artist.format('Degrees'),xticklabels=map(artist.format,['Before','After']))