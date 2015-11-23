# We found this code on Dan Moore's website at http://www.mooreds.com/wordpress/archives/1797
# to act as an initial testing framework for our algorithm.

__author__ = "Dan Moore"
class Board:
        def __init__(self, size = 1, bomblocations = []):
		self._size = size
		self._bomblocations = bomblocations

	def size(self):
		return self._size

	def _bombLocation(self, location):
                for onebomblocation in self._bomblocations:
                	if onebomblocation == location:
				return 'x'

	def _isOnBoard(self, location):
		if location[0] == self._size:
		    	return False
		if location[1] >= self._size:
		    	return False
		return True

	def whatsAt(self, location):
		if self._bombLocation(location) == 'x':
			return 'x'
		if not self._isOnBoard(location):
			return None
		return self._numberOfBombsAdjacent(location)

	def _numberOfBombsAdjacent(self, location):
		bombcount = 0
		# change x, then y
		currx = location[0]
		curry = location[1]
		for xincrement in [-1,0,1]:
			xtotest = currx + xincrement
			for yincrement in [-1,0,1]:
				ytotest = curry + yincrement
				#print 'testing: '+ str(xtotest) + ', '+str(ytotest)+ ', '+str(bombcount)
				if not self._isOnBoard([xtotest,ytotest]):
					continue
				if self._bombLocation([xtotest,ytotest]) == 'x':
					bombcount += 1
		return bombcount

	def printBoard(self):
		x = 0
		while x < self._size:
			y = 0
			while y < self._size:
				print self.whatsAt([x,y]),
				y += 1
			x += 1
			print

# def main():
#     board = Board(15,[[0,1],[1,2],[2,4],[2,5],[3,5],[5,5]])

# if __name__ == "__main__":
# 	main()
