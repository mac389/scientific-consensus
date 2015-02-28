import random, os  
import numpy as np 
from awesome_print import ap 

'''
    Science as a Monte Carlo sampling of the truth; so could start with examining pi 
'''

'''
    We model science as follows:
       (All scientists are connected by a Barabasi-Albert network)
       1. A scientist writes a paper
       2. Scientists who are first neighbors of that scientists, as well as some random ones, read that paper. 
       3. Those scientists react to the paper by 
          - adjusting their anchor (not including modulation of adjustment by credibility at this point) by an 
            adjustment-weighted discrepancy. 
          - conducting an experiment that yields new results (how on earth to model this, I can see it in pi)
          - writing a paper (not including the effect of collborative writing)
       4. Can also include the effect of random paper writing (ignoring meta-analyses)


       Distinguishing between consensus and accuracy
'''

class Scientist(object):

	def __init__(self,anchor=None,adjustment=None,label=None,iterations=10, homophily=None):
		self.anchor = anchor if anchor is not None else random.uniform(-1.0,1.0)
		self.adjustment = adjustment if adjustment is not None else random.random()
		self.label = label if label is not None else 'Unknown'
		self.iterations = iterations
		self.homophily = homophily if homophily is not None else random.random()
		self.estimate_of_pi = self.estimate_pi()

		self.consensus = None
		self.fraction_of_each_paper_containing_science = 0.5
		self.article_length = 100
		self.threshold_for_writing_paper = 0.9

		self.outpath = os.path.join(os.getcwd(),'papers',self.label)

		if not os.path.isdir(self.outpath):
			os.makedirs(self.outpath)

	def __str__(self):
		return '%.02f'%self.estimate_of_pi

	def experiment(self):
		self.estimate_of_pi = self.estimate_pi()

	def write_paper(self,time):
		if random.random() > self.threshold_for_writing_paper:
			#assume all papers are the same length, 100 words
			consensus_count = max(1,int((1-self.fraction_of_each_paper_containing_science)*self.consensus*self.article_length))
			disagreement_count = int((1-self.fraction_of_each_paper_containing_science)*(1-self.consensus)*self.article_length)
			scientific_count = int(self.fraction_of_each_paper_containing_science*self.article_length)

			with open('vocabulary-consensus','rb') as consensus_words, open('vocabulary-disagreement','rb') as disagreement_words, open('vocabulary-science','rb') as science_words:
				paper = random.sample(consensus_words.read().splitlines(),consensus_count)
				paper += random.sample(disagreement_words.read().splitlines(),disagreement_count)
				paper += random.sample(science_words.read().splitlines(),scientific_count)

			with open(os.path.join(self.outpath,'%s'%time),'wb') as outfile:
				for word in paper:
					print>>outfile,word
			'''
					paper = (1-b) *( a*consensus + (1-a)*disagreement) + (b)*science
					b = fraction of science to opinion
					a = fraction of consensus to disagreement
			'''

	def estimate_pi(self,repeats=1000):
		run_estimate = np.zeros((repeats,))
		nhits = 0
		for repeat in xrange(repeats):
			for game in xrange(self.iterations):
				if (random.uniform(-1.0,1.0)+self.anchor)**2 + (random.uniform(-1.0,1.0)+self.anchor)**2 < 1.0:
					nhits +=1
			run_estimate[repeat] = nhits
			nhits=0
		return 4*run_estimate.mean()/float(self.iterations)

	def __repr__(self):
		return "ID: %s \t Estimate of Pi: %.04f \t Anchor: %.04f \t Adjustment: %.04f \t"%(self.label,self.estimate_of_pi, self.anchor,self.adjustment,)