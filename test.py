import numpy as np 

from awesome_print import ap 
from Scientist import Scientist

sci_guy = Scientist(label='Sci guy')
print sci_guy
print sci_guy.estimate_pi(repeats=10)