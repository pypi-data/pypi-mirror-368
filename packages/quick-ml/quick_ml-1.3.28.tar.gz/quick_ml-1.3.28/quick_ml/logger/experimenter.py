
import os

class Experimenter:

	def __init__(self, root_folder = None):

		self.root = root_folder

	def begin_experiment(self, exp_name= None):
		
		if exp_name:
			if self.root:
				os.mkdir(self.root + '/' + exp_name)

		else:

			os.mkdir()

