import random

import networkx as nx
import matplotlib.pyplot as plt 
import numpy as np 
import Graphics as artist

from awesome_print import ap 
from Scientist import Scientist
from matplotlib import rcParams

nodes = 80
degree = 3
duration = 40
curiosity = 0.01 #(can make this different for different scientists)
PRUNING = 0.1
'''
    Homophily vs. curiosity; Influencers
    Connections diappear randomly
'''

rcParams['text.usetex'] = True

def save_graph(filename='topology'):
	labels = {i:'%.02f'%g.node[i].estimate_of_pi for i in xrange(nodes)}
	pos = nx.spring_layout(g,k=.25)
	n = nx.draw_networkx(g,pos=pos,labels=labels, node_size=800,linewidth=None)

	plt.axis('off')
	plt.tight_layout()
	plt.savefig('%s.png'%filename)
	plt.close()

def my_boxplot(data,filename,ylabel=None,xlabel=None,xticklabels=None):
	fig = plt.figure()
	ax = fig.add_subplot(111)
	bp = ax.boxplot(data,patch_artist=True)
	artist.adjust_spines(ax)
	## change outline color, fill color and linewidth of the boxes
	for box in bp['boxes']:
	    # change outline color
	    box.set( color='#7570b3', linewidth=2)
	    # change fill color
	    box.set( facecolor = '#1b9e77' )

	## change color and linewidth of the whiskers
	for whisker in bp['whiskers']:
	    whisker.set(color='#7570b3', linewidth=2)

	## change color and linewidth of the caps
	for cap in bp['caps']:
	    cap.set(color='#7570b3', linewidth=2)

	## change color and linewidth of the medians
	for median in bp['medians']:
	    median.set(color='#b2df8a', linewidth=2)

	## change the style of fliers and their fill
	for flier in bp['fliers']:
	    flier.set(marker='o', color='#e7298a', alpha=0.5)
	
	if ylabel is not None:
		ax.set_ylabel(ylabel)

	if xlabel is not None:
		ax.set_xlabel(xlabel)

	if xticklabels is not None:
		ax.set_xticklabels(xticklabels)
	#plt.legend(frameon=False)
	plt.savefig('%s.tiff'%filename)
	plt.close()

def get_attr(idx,field):
	return eval('g.node[%d].%s'%(idx,field))

def get_weighted_estimate(idx):
	return eval('g.node')

#Connect scientists; initially barabasi-albert then evolves by similarity
g = nx.barabasi_albert_graph(nodes,degree)
for node_idx in xrange(nodes):
	g.node[node_idx] = Scientist(label=str(node_idx))

save_graph(filename='initial-topology') #Default PNG, add TIFF later

field_estimate = np.zeros((nodes,duration))
centralities = np.zeros((nodes,duration))

for t in xrange(duration):
	for idx in xrange(nodes):
		neighbor_opinion = np.array([g.node[x].estimate_of_pi for x in g.neighbors(idx)]).mean()
		actual_error = np.pi-get_attr(idx,'estimate_of_pi')
		if np.isnan(neighbor_opinion):
			g.node[idx].consensus = 1
		else:
			g.node[idx].consensus = abs(get_attr(idx,'estimate_of_pi') - neighbor_opinion)/np.pi
		
		#print (1-get_attr(idx,'adjustment'))*neighbor_opinion
		adjustment = get_attr(idx,'adjustment')
		anchor = get_attr(idx,'anchor')
		homophily = get_attr(idx,'homophily')

		g.node[idx].anchor = (1-adjustment) * anchor + adjustment*(homophily*neighbor_opinion + (1-homophily)*actual_error)/np.pi

		
		#Add edges propotional to how correct idx is 
		target = random.choice(xrange(nodes))
		if random.random() > abs(np.pi-get_attr(target,'estimate_of_pi')):
			g.add_edge(idx,target)

		
		#Remove edges from scientists with bad estimates proportional to how bad their estimate is 
		for neighbor in g.neighbors(idx):
			if random.random() < abs(get_attr(x,'estimate_of_pi') -np.pi) and random.random()<PRUNING:
				g.remove_edge(idx,neighbor)

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
	field_estimate[:,t] = [get_attr(idx,'estimate_of_pi') for idx in xrange(nodes)]

	#ap(nx.degree_centrality(g))
	centr = nx.degree_centrality(g)
	centralities[:,t] = [centr[node] for node in xrange(nodes)]
	#NetworkX degree centrality returns a dictionary of node:centrality
save_graph(filename='after-topology')

my_boxplot([field_estimate[:,0],field_estimate[:,-1]],'distributions-of-estimates',
	ylabel=r'\Large \textbf{\textsc{Estimate of}} $\pi$',xticklabels=map(artist.format,['Before','After']))

my_boxplot([centralities[:,0],centralities[:,-1]],'centralities',
	ylabel=artist.format('Degree Centrality'),xticklabels=map(artist.format,['Before','After']))
