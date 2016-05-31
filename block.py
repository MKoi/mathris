import collections
import random

class Block:
	#available shapes I-shape, L-shape, J-shape, O-shape...
	shapes = "ILJONST"
	maxchars = 4
	def __init__(self,pos,layout,chars):
		clen = len(chars)
		if clen == 1:
			if layout == 'I':
				self.slots = [(0,0)]
			else: return
		elif clen == 2:
			if layout == 'I':
				self.slots = [(0,0),(0,1)]
			else: return
		elif clen == 3:
			if layout == 'I':
				self.slots = [(0,-1),(0,0),(0,1)]
			elif layout == 'L':
				self.slots = [(0,1),(0,0),(1,0)]
			elif layout == 'J':
				self.slots = [(0,1),(0,0),(-1,0)]
			else: return
		elif clen == 4:
			if layout == 'I':
				self.slots = [(0,-1),(0,0),(0,1),(0,2)]
			elif layout == 'L':
				self.slots = [(0,2),(0,1),(0,0),(1,0)]
			elif layout == 'J':
				self.slots = [(0,2),(0,1),(0,0),(-1,0)]
			elif layout == 'N':
				self.slots = [(0,1),(0,0),(-1,0),(-1,-1)]
			elif layout == 'S':
				self.slots = [(0,1),(0,0),(1,0),(1,-1)]
			elif layout == 'T':
				self.slots = [(-1,0),(0,0),(0,-1),(1,0)]
			elif layout == 'O':
				self.slots = [(-1,1),(0,1),(0,0),(-1,0)]
			else: return
		else:
			return
		self.layout = layout
		self.pos = pos
		self.chars = chars
	
	def positions(self, local=False):
		if local:
			return self.slots
		myadd = lambda p1,p2: (p1[0] + p2[0], p1[1] + p2[1])
		return [myadd(self.pos, p) for p in self.slots]
	
	def extents(self, local=False):
		s = self.slots if local else self.positions()
		xs = sorted(s, key = lambda p: p[0])
		ys = sorted(s, key = lambda p: p[1])
		xmax,ymax = xs[-1][0], ys[-1][1]
		xmin,ymin = xs[0][0], ys[0][1]
		return (xmax,ymax),(xmin,ymin)
	
	# k = sort lambda
	# i = tuple member index
	def filterPosition(self, k, i):
		ls = self.positions()
		ls.sort(key = k)
		return self.removeDuplicateTuple(ls, i)
	
	# l = list of tuples
	# i = tuple member index
	def removeDuplicateTuple(self, l, i):
		r = [l[0]]
		for lm in l:
			if lm[i] != r[-1][i]:
				r.append(lm)
		return r
	
	def bottom(self):
		return self.filterPosition(lambda p: (p[0],p[1]), 0)
	
	def top(self):
		return self.filterPosition(lambda p: (p[0],-p[1]), 0)
			
	def left(self):
		return self.filterPosition(lambda p: (p[1],p[0]), 1)
			
	def right(self):
		return self.filterPosition(lambda p: (p[1],-p[0]), 1)
	
	
	def movedown(self):
		self.pos = (self.pos[0],self.pos[1]-1)
		
	def moveleft(self):
		self.pos = (self.pos[0]-1,self.pos[1])
		
	def moveright(self):
		self.pos = (self.pos[0]+1,self.pos[1])
		
	# rotate clockwise or counter-clockwise (CW=False)
	def rotate(self, CW=True):
		# special case: rotate O-shape in place and not around (0,0)
		if self.layout == 'O':
			a = collections.deque(self.slots)
			i = -1 if CW else 1
			a.rotate(i)
			self.slots = a
		else:
			for i in range(len(self.slots)):
				x,y = self.slots[i]
				x1 = y if CW else -y
				y1 = -x if CW else x
				self.slots[i] = (x1,y1)
		return self.positions()
		
	@staticmethod
	def possibleshapes(bcount):
		shapes = ""
		if bcount > 0:
			shapes += "I"
		if bcount > 2:
			shapes += "LJ"
		if bcount > 3:
			shapes += "NSTO"
		return shapes
		
		
	@staticmethod
	def unitTest():	
		poslist = [(0,0),(4,4),(4,-4),(-4,4),(-4,4)]
		texts = ["1","1+","1+1","1+1="]
		
		blocklist = []
		for p in poslist:
			for t in texts:
				shapes = Block.possibleshapes(len(t))
				for s in shapes:
					blocklist.append(Block(p,s,t))
		
		for b in blocklist:
			print b.positions(), b.layout
			print b.rotate()
			print b.extents()
			print b.rotate()
			print b.extents()
			print b.rotate()
			print b.rotate()
			print b.rotate(False)
			print b.rotate(False)
			print b.rotate(False)
			print b.rotate(False)
	
#Block.unitTest()