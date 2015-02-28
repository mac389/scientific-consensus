import matplotlib.pyplot as plt
import networkx as nx 
import numpy as np 

from matplotlib import rcParams
from scipy.stats import percentileofscore
from awesome_print import ap 

rcParams['text.usetex'] = True

format = lambda text: r'\Large \textbf{\textsc{%s}}'%text

def save_graph(g,filename='topology'):
    labels = {i:'%.02f'%g.node[i].estimate_of_pi for i in xrange(len(g))}
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
    adjust_spines(ax)
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

def compare_degree_sequences(one,two): #TODO: Expand to take arbitrary list
    fig = plt.figure()
    ax = fig.add_subplot(111)

    rank_one = np.array([percentileofscore(one,num) for num in one[::-1]])
    rank_two = np.array([percentileofscore(two,num) for num in two[::-1]])

    ax.loglog(rank_one,one,'k--',label=format('Before Interactions'))
    plt.hold(True)
    ax.loglog(rank_two,two,'r.-',label=format('After Interactions'))

    adjust_spines(ax)

    ax.set_ylabel(format('Degree'))
    ax.set_xlabel(format('Rank'))
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig('degree-rank.tiff')

def adjust_spines(ax,spines=['left','bottom']):
    for loc, spine in ax.spines.items():
        if loc in spines:
            spine.set_position(('outward',10)) # outward by 10 points
            spine.set_smart_bounds(True)
        else:
            spine.set_color('none') # don't draw spine

    # turn off ticks where there is no spine
    if 'left' in spines:
        ax.yaxis.set_ticks_position('left')
    else:
        # no yaxis ticks
        ax.yaxis.set_ticks([])

    if 'bottom' in spines:
        ax.xaxis.set_ticks_position('bottom')
    else:
        # no xaxis ticks
        ax.xaxis.set_ticks([])
