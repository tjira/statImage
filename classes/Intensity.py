import cv2
import numpy
import json
import os
from Image import Image


class Intensity:
	def __init__(self, filename, grid):
		self.filename = filename
		self.gridSize = grid
		self.image = Image(filename=self.filename)
		self.size = self.image.matrix.shape[0]

	def estimate(self):
		n0 = int((self.size/self.gridSize + 1)**2)
		n1 = (self.size/self.gridSize)*(self.size / self.gridSize + 1)*2
		n2 = int((self.size/self.gridSize)**2)
		N0 = 0
		for i in range(self.size//self.gridSize + 1):
			for j in range(self.size//self.gridSize + 1):
				point = (min(j*self.gridSize, self.size-1), min(i*self.gridSize, self.size - 1))
				if self.image.matrix[point[0], point[1]] == 255:
					N0 += 1
					self.image.matrix[point[0], point[1]] = 50
		N1 = 0
		for i in range(self.size//self.gridSize + 1):
			for j in range(self.size//self.gridSize + 1):
				point = (min(j*self.gridSize, self.size - 1), min(i*self.gridSize, self.size - 1))
				if not 0 in self.image.matrix[point[0], point[1] + 1:min(point[1] + self.gridSize, self.size - 1)]:
					N1 += 1
					self.image.matrix[point[0], point[1] + 1:min(point[1] + self.gridSize, self.size - 1)] = 100
				if not 0 in self.image.matrix[point[0] + 1:min(point[0] + self.gridSize, self.size - 1), point[1]]:
					N1 += 1
					self.image.matrix[point[0] + 1:min(point[0] + self.gridSize, self.size - 1), point[1]] = 100
		N2 = 0
		for i in range(n2):
			point = (int(i//(self.size/self.gridSize)*self.gridSize), int(i%(self.size/self.gridSize)*self.gridSize))
			if not 0 in self.image.matrix[point[0] + 1:min(point[0] + self.gridSize, self.size - 1), point[1] + 1:min(point[1] + self.gridSize, self.size - 1)]:
				N2 += 1
				self.image.matrix[point[0] + 1:min(point[0] + self.gridSize, self.size - 1), point[1] + 1:min(point[1] + self.gridSize, self.size - 1)] = 150
		A0 = numpy.log(n0/N0)
		A1 = numpy.log(n1/N1)
		A2 = numpy.log(n2/N2)
		c = self.gridSize
		rho = 1/c**2*(A0 - 2*A1 + A2)*self.size
		outDataFile = os.path.join(os.sep.join(self.filename.split(os.sep)[:-1]), "intensity.json")
		with open(outDataFile, "w") as output:
			jsonDict = json.dumps({
				"n0": n0,
				"n1": n1,
				"n2": n2,
				"N0": N0,
				"N1": N1,
				"N2": N2,
				"A0": A0,
				"A1": A1,
				"A2": A2,
				"gridSize": self.gridSize,
				"intensity": rho
				}, sort_keys=True, indent=4)
			output.write(jsonDict)
		self.image.save("_intensityGrid")
		return round(rho, 2)