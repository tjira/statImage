import json
import os
import numpy
from Image import Image


class MLE:
	def __init__(self, image, **kwargs):
		self.connectivity = kwargs.pop("connectivity", "8")
		self.filename = image
		self.image = Image(filename=self.filename)
		self.folder = kwargs.pop("folder", "chain")
		self.guz, self.theta0 = self.loadChain()
		self.gux = self.countChars()
		self.theta = numpy.copy(self.theta0)
		self.allThetas = {1: list(self.theta)}

	def iteration(self):
		num_u = numpy.array([0, 0, 0])
		den_u = 0
		for i in range(len(self.guz)):
			num_u = num_u + self.guz[i]  *  numpy.exp(  sum(self.guz[i]*self.theta - self.guz[i]*self.theta0 )  )
			den_u = den_u + numpy.exp(  sum(self.guz[i]*self.theta - self.guz[i]*self.theta0)  )
		u = self.gux - num_u/den_u

		num_j = 0
		den_j = 0
		for i in range(len(self.guz)):
			num_j = num_j + sum(  (self.guz[i] - num_u/den_u)**2  )  *  numpy.exp(  sum(self.guz[i]*self.theta - self.guz[i]*self.theta0)  )
			den_j = den_j + numpy.exp(  sum(self.guz[i]*self.theta - self.guz[i]*self.theta0)  )
		j = num_j/den_j
		self.theta = self.theta + u/j
		self.allThetas[list(self.allThetas.keys())[-1]+1] = list(self.theta)

	def loadChain(self):
		with open(os.path.join(*self.folder.split(os.sep), "characteristics.json"), "r") as chars:
			chain = json.loads(chars.read())
		guz = list()
		for i in range(len(chain.keys())-5):
			chars = chain[str(i+1)]
			guz.append(numpy.array([chars[0], chars[1], chars[2][0]-chars[2][1]]))
		return guz, numpy.array(chain["params"])

	def saveThetas(self):
		path = self.filename.split(os.sep)[:-1] + ["estimation.json"]
		with open(os.sep.join(path), "w") as thetaFile:
			thetaFile.write(json.dumps(self.allThetas, sort_keys=True, indent=4))

	def countChars(self):
		a = self.image.area()
		l = self.image.length()
		chi = self.image.chi(self.connectivity)
		return numpy.array([a, l, chi[0]-chi[1]])