import random

import networkx as nx
import matplotlib.pyplot as plt 
import numpy as np 
import Graphics as artist

from awesome_print import ap 
from Scientist import Scientist
from matplotlib import rcParams

nodes = 50
degree = 3
duration = 30 
curiosity = 0.01 #(can make this different for different scientists)
PRUNING = 0.01
'''
    Homophily vs. curiosity; Influencers

    Connections decay at a certain rate
'''

rcParams['text.usetex'] = True

def save_graph(filename='topology'):
	#--Simple visualization
	labels = {i:'%.02f'%g.node[i].estimate_of_pi for i in xrange(nodes)}
	pos = nx.spring_layout(g,k=.25)
	n = nx.draw_networkx(g,pos=pos,labels=labels, node_size=800,linewidth=None)
	#nx.draw_networkx(g,pos,with_label=False)
	#nx.draw_networkx_nodes(g,pos,node_size=1200)
	#nx.draw_networkx_labels(g,pos,labels)

	plt.axis('off')
	plt.tight_layout()
	plt.savefig('%s.png'%filename)
	plt.close()

def get_attr(idx,field):
	return eval('g.node[%d].%s'%(idx,field))

def get_weighted_estimate(idx):
	return eval('g.node')

#Create graph
#Connect scientists; initially barabasi-albert then evolves by similarity
g = nx.barabasi_albert_graph(nodes,degree)
for node_idx in xrange(nodes):
	g.node[node_idx] = Scientist(label=str(node_idx))


save_graph(filename='initial-topology') #Default PNG, add TIFF later

field_estimate = np.zeros((nodes,duration))

for t in xrange(duration):
	for idx in xrange(nodes):
		neighbor_opinion = np.array([g.node[x].estimate_of_pi for x in g.neighbors(idx)]).mean()
		g.node[idx].estimate_of_pi =  (1-get_attr(idx,'adjustment'))*neighbor_opinion + get_attr(idx,'adjustment')*get_attr(idx,'estimate_of_pi') 

		#Homophily
		for partner in g.neighbors(idx):
			if random.random() > abs(get_attr(idx,'estimate_of_pi')-get_attr(partner,'estimate_of_pi')):
				g.add_edge(idx,partner) 
				break

		#Curiosity
		if random.random() < curiosity:
			random.choice(xrange(nodes))
			if partner != idx:
				g.add_edge(idx,partner)

				
		#Randomly remove edges 
		if len(g.neighbors(idx)) > 0 and random.random()<PRUNING:
			target = random.choice(g.neighbors(idx))
			print 'Removing neighbor %d of node %d, with neighbors %s, at time %d'%(target,idx,g.neighbors(idx),t)
			g.remove_edge(idx,target)
		
			
		#Adjust anchor; uncertain how to do this	
		field_estimate[idx,t] = get_attr(idx,'estimate_of_pi')
	field_estimate[t] = np.average([get_attr(idx,'estimate_of_pi') for idx in xrange(nodes)])

save_graph(filename='after-topology')

fig = plt.figure()
ax = fig.add_subplot(111)
ax.hist(field_estimate[:,0],color='k',label=artist.format('Before'),histtype='step')
plt.hold(True)
ax.hist(field_estimate[:,-1],color='r',label=artist.format('After'),histtype='step')
artist.adjust_spines(ax)
ax.set_xlabel(r'\Large \textbf{\textsc{Estimate of}} $\pi$')
ax.set_ylabel(artist.format('Count'))
plt.legend(frameon=False)
plt.savefig('distributions-of-estimates.tiff')
