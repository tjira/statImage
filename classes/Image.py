import json
import cv2
import numpy
import os


class Image:
	edge = 10
	filenames = list()

	def __init__(self, **kwargs):
		self.filename = kwargs.pop("filename", None)
		if self.filename:
			self.matrix = cv2.imread(self.filename, cv2.IMREAD_GRAYSCALE)
		else:
			self.matrix = kwargs.pop("matrix")
			self.filename = "simulated.png"

	def threshold(self, **kwargs):
		point = kwargs.pop("threshold", 100)
		ret, self.matrix = cv2.threshold(self.matrix, point, 255, cv2.THRESH_BINARY)

	def morphology(self, **kwargs):
		kernel = numpy.ones(kwargs.pop("kernel", (1, 1)), numpy.uint8)
		seq = kwargs.pop("seq", (-1, 1))
		for i in seq:
			if i < 0:
				self.matrix = cv2.dilate(self.matrix, kernel, iterations=abs(i))
			else:
				self.matrix = cv2.erode(self.matrix, kernel, iterations=abs(i))

	def removeSmallComps(self, **kwargs):
		minCompSize = kwargs.pop("minCompSize", 100)
		connectivity = kwargs.pop("connectivity", 8)
		minHoleSize = kwargs.pop("minHoleSize", 10)
		maxHoleSize = kwargs.pop("maxHoleSize", 10**6)
		invOutput = cv2.connectedComponentsWithStats(255-self.matrix, connectivity=connectivity)
		compSizes = invOutput[2][1:,4]
		noComps = invOutput[0] - 1
		compLabels = invOutput[1]
		output = cv2.connectedComponentsWithStats(self.matrix, connectivity=connectivity)
		holeSizes = output[2][1:,4]
		noHoles = output[0] - 1
		for i in range(noHoles):
			if holeSizes[i] < minHoleSize or holeSizes[i] > maxHoleSize:
				noHoles -= 1
		for i in range(noComps):
			if compSizes[i] < minCompSize:
				self.matrix[compLabels==i+1] = 255
				noComps -= 1				
		return noComps, noHoles

	def area(self):
		a = len(self.matrix[numpy.where(self.matrix==0)])
		return a*self.edge**2/self.matrix.shape[1]**2

	def length(self):
		cnts = cv2.findContours(255-self.matrix, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2]
		l = sum([cv2.arcLength(cnt, True) for cnt in cnts])
		return l*self.edge/self.matrix.shape[1]

	def chi(self, connectivity):
		invOutput = cv2.connectedComponentsWithStats(255-self.matrix, connectivity=8)
		output = cv2.connectedComponentsWithStats(self.matrix, connectivity=8)
		noComps = invOutput[0] - 1
		noHoles = output[0] - 2
		return noComps, noHoles

	def computeChars(self, **kwargs):
		self.threshold(**kwargs)
		self.save("_threshold")
		self.morphology(**kwargs)
		self.save("_binary")
		components, holes = self.removeSmallComps(**kwargs)
		self.save("_binaryEdited")
		a = self.area()
		l = self.length()
		chars = [a, l, [components, holes]]
		self.saveStats(chars, kwargs)
		return chars

	def save(self, appendix):
		path = os.path.abspath(self.filename).split(os.sep)
		path[-1] = path[-1].split(".")[0] + appendix + ".png"
		path = os.sep.join(path)
		self.filenames.append(path)
		cv2.imwrite(path, self.matrix)

	def saveStats(self, chars, kwargs):
		path = os.path.abspath(self.filename).split(os.sep)
		path[-1] = "stats.json"
		jsonDict = {
			"Characteristics": chars,
			"Size": self.matrix.shape,
			"Threshold": kwargs["threshold"],
			"MorphKernel": kwargs["kernel"],
			"MorphSeq": kwargs["seq"],
			"minCompSize": kwargs["minCompSize"],
			"minHoleSize": kwargs["minHoleSize"],
			"maxHoleSize": kwargs["maxHoleSize"]
			}
		with open(os.sep.join(path), "w") as stats:
			stats.write(json.dumps(jsonDict, sort_keys=True, indent=4))

	def display(self):
		cv2.namedWindow("Image", cv2.WINDOW_NORMAL | 16)
		cv2.resizeWindow("Image", 500, int(500/self.matrix.shape[1]*self.matrix.shape[0]))
		cv2.imshow("Image", self.matrix)
		cv2.waitKey(0)
		cv2.destroyAllWindows()