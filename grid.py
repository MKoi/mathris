import collections
import random
import itertools 
import array

# p is tuple (x,y), w=width, h=height
def inbounds(p, grid):
	return not (p[0] >= grid.w or p[0] < 0 or p[1] >= grid.h or p[1] < 0)

def occupied(p, grid):
	return inbounds(p, grid) and grid.grid[p[0]][p[1]] != 'e'

def isnumber(p, grid):
	return inbounds(p, grid) and grid.grid[p[0]][p[1]] and grid.grid[p[0]][p[1]] in '0123456789'

def isoperator(p, grid):
	return inbounds(p, grid) and (grid.grid[p[0]][p[1]] == '+' or grid.grid[p[0]][p[1]] == '-')


class Grid:
	def __init__(self, w, h):
		self.w = w
		self.h = h
		self.grid = [array.array('c',['e' for y in range(h)]) for x in range(w)]

	'''
	def adjacent(self, pos, excludeSet=None, condition=None, *args):
		a = {(0,1),(1,0),(0,-1),(-1,0)}
		myadd = lambda p1,p2: (p1[0] + p2[0], p1[1] + p2[1])
		a = {myadd(pos, p) for p in a}
		r = {p for p in a if condition(p,*args)} if condition else a
		if not excludeSet:
			return r
		# remove all elements found in excludeSet
		r.difference_update(excludeSet)
		return r
	'''
	def adjacent(self, pos, excludeSet=None, condition=None, *args):
		x,y = pos
		if condition:
			r = set()
			if condition((x-1,y),*args): r.add((x-1,y))
			if condition((x,y+1),*args): r.add((x,y+1))
			if condition((x,y-1),*args): r.add((x,y-1))
			if condition((x+1,y),*args): r.add((x+1,y))
		else:
			r = {(x-1,y),(x,y+1),(x,y-1),(x+1,y)}
		if not excludeSet:
			return r
		# remove all elements found in excludeSet
		r.difference_update(excludeSet)
		return r
	
	def isEmpty(self, pos):
		x,y = pos
		return self.grid[x][y]  == 'e'
		
	# l = list of positions
	# s = list of characters (i.e. string)
	def addBlocks(self, l, s):
		if len(l) != len(s) or len(l) == 0:
			return False
		for i in range(len(l)):
			p = l[i]
			c = s[i]
			if inbounds(p,self):
				self.grid[p[0]][p[1]] = c
		return True
		
	# l = list of positions to be removed
	def removeBlocks(self, l):
		for p in l:
			if inbounds(p,self):
				self.grid[p[0]][p[1]] = 'e'
	
	# floodfill: p is position, c is 'color' and nodes is grid of colors
	def connectednodes(self, p, c, nodes):
		if nodes[p[0]][p[1]] != c and self.grid[p[0]][p[1]] != 'e':
			nodes[p[0]][p[1]] = c
			x,y = p
			if x > 0:
				self.connectednodes((x-1,y),c,nodes)
			if x < self.w - 1:
				self.connectednodes((x+1,y),c,nodes)
			if y > 0:
				self.connectednodes((x,y-1),c,nodes)
			if y < self.h - 1:
				self.connectednodes((x,y+1),c,nodes)
	
	# return a list of sets. each set contains connected blocks
	def islands(self):
		nodes = [[0 for y in range(self.h)] for x in range(self.w)]
		c = 1
		# first iteration finds islands
		for j in range(self.h):
			for i in range(self.w):
				if nodes[i][j] == 0 and self.grid[i][j] != 'e':
					self.connectednodes((i,j),c,nodes)
					c += 1
		# second iteration constructs list of sets
		l = [set()]
		for j in range(self.h):
			for i in range(self.w):
				if nodes[i][j] > 0:
					idx = nodes[i][j]
					while len(l) < idx:
						l.append(set())
					l[idx-1].add((i,j))
		return l
						
	def shiftDown(self, l):
		ls = list(l)
		# sort by x, then by y
		ls.sort(key = lambda p: (p[0],p[1]))
		# lx = save only lowest y for each x
		lx = [ls[0]]
		for pos in ls:
			if pos[0] != lx[-1][0]:
				lx.append(pos)
		# smallest y decrement
		mindy = -self.h
		for pos in lx:
			x,y = pos
			y2 = y
			while y2 > 0 and self.grid[x][y2-1] == 'e': y2 -= 1
			mindy = max(y2-y,mindy)
		# shift down blocks
		if mindy != 0:
			for p in ls:
				x,y = p
				self.grid[x][y+mindy] = self.grid[x][y]
				self.grid[x][y] = 'e'
	
	def printGrid(self):
		for j in reversed(range(self.h)):
			line = ''
			for i in range(self.w):
				c = self.grid[i][j]
				# replace empty chars by whitespace
				if c == 'e': c = ' '
				line += c + ' '
			print line
		print ''
	
	def printBlocks(self, l):
		r = ''
		for c in l:
			r += self.grid[c[0]][c[1]]
		return r
	
	def populate(self):
		p = []
		l = []
		for i in range(self.w):
			for j in range(self.h):
				p.append((i,j))
				if (i%2 and not j%2) or (j%2 and not i%2):
					l.append(random.choice('0123456789'))
				elif ((i*self.w+j)%7) == 0:
					l.append('=')
				else:
					l.append(random.choice('+-'))
		self.addBlocks(p,l)
	
	def findchar(self, c):
		r = []
		for i in range(self.w):
			for j in range(self.h):
				if self.grid[i][j] == c:
					r.append((i,j))
		return r
					
					
	@staticmethod
	def unitTest():
		clist = [['1','+','2'],['3','-','4','='],['5','+','6','=']]
		plist = [[(0,4),(1,4),(1,3)],[(3,4),(4,4),(4,3),(4,2)],[(2,0),(2,1),(3,1),(3,0)]]
		g = Grid(5,5)
		g.printGrid()
		for i in range(len(clist)):
			g.addBlocks(plist[i],clist[i])
		g.printGrid()
		g.removeBlocks(plist[0])
		g.printGrid()
		g.addBlocks(plist[0],clist[0])
		g.printGrid()
		p = (0,4)
		print 'adjacent of ', p, ':', g.adjacent(p)
		print 'in bounds:', g.adjacent(p,None,inbounds,g)
		print 'occupied:', g.adjacent(p,None,occupied,g)
		p = (1,4)
		print 'adjacent of ', p, ':', g.adjacent(p)
		print 'in bounds:', g.adjacent(p,None,inbounds,g)
		print 'occupied:', g.adjacent(p,None,occupied,g)
		p = (0,2)
		print 'adjacent of ', p, ':', g.adjacent(p)
		print 'in bounds:', g.adjacent(p,None,inbounds,g)
		print 'occupied:', g.adjacent(p,None,occupied,g)
		islands = g.islands()
		print islands
		for l in islands:
			g.shiftDown(l)
		g.printGrid()
		islands = g.islands()
		print islands
		g.removeBlocks([(0,1),(1,1),(2,1),(3,1),(4,1)])
		g.printGrid()
		islands = g.islands()
		print islands
		for l in islands:
			g.shiftDown(l)
		g.printGrid()
		
#Grid.unitTest()	