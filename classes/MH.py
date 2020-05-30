import numpy
import random
import cv2
from Image import Image


class MH:
	def __init__(self, **kwargs):
		self.connectivity = kwargs.pop("connectivity", 8)
		self.size = kwargs.pop("size", 100)
		self.iters = kwargs.pop("iters", 1000)
		self.r = kwargs.pop("r", (5, 10))
		self.intensity = kwargs.pop("intensity", 1)
		self.params = numpy.array(list(kwargs.pop("params", (0, 0, 0))))
		self.image = Image(matrix=numpy.ones((self.size, self.size), dtype=numpy.uint8)*255)
		self.circles = list()

	def iteration(self):
		action = "add" if random.random() < 0.5 or len(self.circles) == 0 else "remove"
		if action == "add":
			circle = self.drawCircle()
			if random.random() < self.HR(action):
				self.circles.append(circle)
				self.commit()
		else:
			index = self.removeCircle()
			if random.random() > self.HR(action):
				del self.circles[index]
				self.commit()
		return self.image.matrix, [self.image.area(), self.image.length(), self.image.chi(self.connectivity)]

	def makeImage(self, circles):
		image = Image(matrix=numpy.ones((self.size, self.size), dtype=numpy.uint8)*255)
		for circle in circles:
			cv2.circle(image.matrix, *circle, 0, -1)
		return image

	def drawCircle(self):
		self.temp = Image(matrix=numpy.copy(self.image.matrix))
		circle = self.randomCircle()
		cv2.circle(self.temp.matrix, *circle, 0, -1)
		return circle

	def removeCircle(self):
		index = random.randrange(len(self.circles))
		self.temp = self.makeImage(self.circles[:index] + self.circles[index+1:])
		return index

	def randomCircle(self):
		r = random.randrange(*self.r)
		circle = ((random.randrange(r + 1, self.size - r), random.randrange(r + 1, self.size - r)), r)
		return circle

	def chars(self):
		chi = self.image.chi(self.connectivity)
		chars = [self.image.area(), self.image.length(), chi[0] - chi[1]]
		return numpy.array(chars)

	def tempChars(self):
		chi = self.temp.chi(self.connectivity)
		chars = [self.temp.area(), self.temp.length(), chi[0] - chi[1]]
		return numpy.array(chars)

	def H(self, G, n):
		ratio = self.intensity*numpy.exp(numpy.sum(self.params*G))/(n + 1)
		return ratio

	def HR(self, action):
		if action == "add":
			G = self.tempChars() - self.chars()
			ratio = self.H(G, len(self.circles))
		else:
			G = self.chars() - self.tempChars()
			ratio = 1/self.H(G, len(self.circles) - 1)
		return min(ratio, 1)

	def commit(self):
		self.image.matrix = numpy.copy(self.temp.matrix)