import grid
import itertools

maxdepth = 13
bignum = 9999
evalNodeToRoot = 1
evalRootToNode = 2
evalBoth = 3

# evaluate arithmetic operation from position tree
# l=tree implemented as list of lists
# g=Grid
def evaluateList(g, l, backToFront=False):
	if not l or not grid.isnumber(l[0],g):
		return
	ibeg = 0 if not backToFront else len(l) - 1
	iend = len(l) if not backToFront else -1
	istep = 1 if not backToFront else -1
	numval = None
	op = ''
	i = ibeg
	x,y = l[i]
	numstr = g.grid[x][y]
	i += istep
	while i != iend:
		x,y = l[i]
		c = g.grid[x][y]
		if c in '0123456789':
		#if c.isdigit():
			numstr += c
		elif c in '+-':
			if numstr:
				if op and numval is not None:
					if op == '+':
						numval += int(numstr)
					elif op == '-':
						numval -= int(numstr)
				else:
					numval = int(numstr)
				op = c
				numstr = ''			
		else:
			return
		i += istep
	if numstr:
		if op and numval is not None:
			if op == '+':
				numval += int(numstr)
			elif op == '-':
				numval -= int(numstr)
		else:
			numval = int(numstr)
	return numval

# tuple[0] == pos, tuple[1] == prev_node
def nodesToRoot(n, fromRoot=False):
	l = [n[0]]
	nn = n[1]
	while nn:
		l.append(nn[0])
		nn = nn[1]
	if fromRoot:
		l.reverse()
	return l #l[::-1] if fromRoot else l

# t = tuple (pos,prevnode,val,valbackwards,depth)
def populateDict(node, d, evalBackwards=False):
	#print node
	if not node:
		return
	t = node[0]
	val = t[3] if evalBackwards else t[2]
	if val == bignum:
		for i in range(1,len(node)):
			populateDict(node[i], d, evalBackwards)
	else:
		if val in d:
			d[val].append(t)
		else:
			d.update({val:[t]})
		for i in range(1,len(node)):
			populateDict(node[i], d, evalBackwards)

def treeToList(node,prev=None):
	if node:
		n = node[0]
		prev2 = prev + [n[0]] if prev else [n[0]]
		if n[2] != bignum:
			yield prev2
		for i in range(1,len(node)):
			for l in treeToList(node[i],prev2):
				yield l

# evaluate valid char lists from grid of characters starting from p
# p = (3,2)
# g = Grid
# r = list of lists l[0] = node tuple, l[1+] are lists of child nodes
# d,db =  dictionary of value: [tuple1, tuple2], where each tuple points to node from which that value is evaluated
def charlist(g, p, evaldir=evalBoth):
		exc = [p]
		val = int(g.grid[p[0]][p[1]]) # evaluated value
		t = (p,None,val,val,len(exc))
		r = [t]
		d = {}
		db = {}
		if evaldir==evalBoth or evaldir==evalRootToNode:
			addKey(d, val, t)
		if evaldir==evalBoth or evaldir==evalNodeToRoot:
			addKey(db, val, t)
		adj = g.adjacent(p,exc,grid.isoperator,g)
		for a in adj:
			r.append([])
			charlistOp(g, a, exc, r[-1],t, d, db, evaldir)
			if len(r[-1]) == 1: # dead end, no more than sinle operator
				r.pop()
		return r, d, db

# append to result list and create child list
# evaluate tree values
def charlistNum(g, p, exc, r, prev, d, db, evaldir=evalBoth):
#	print 'charListNum r:',r
	if len(exc) < maxdepth:
		exc2 = exc + [p]
		x,y = exc[-1]
		val = int(g.grid[p[0]][p[1]]) # evaluated value
		prevpos = prev[1][0] # val of prev->prev->p
		prevval = int(g.grid[prevpos[0]][prevpos[1]])
		prevsum = prev[1][2] # val of prev->prev->val
		prevsumb = prev[1][3] # val of prev->prev->valb
		valb = bignum
		if g.grid[x][y] == '+': 
			if evaldir==evalBoth or evaldir==evalNodeToRoot:
				valb = val + prevsumb
			val += prevsum
		elif g.grid[x][y] == '-':
			if evaldir==evalBoth or evaldir==evalNodeToRoot:
				valb = val + prevsumb - 2*prevval
			val = prevsum - val
#		if evaldir==evalBoth or evaldir==evalNodeToRoot:
#			valb = evaluateList(g,exc2,True) # backwards evaluated value
		t = (p,prev,val,valb,len(exc2))
		if evaldir==evalBoth or evaldir==evalRootToNode:
			addKey(d, val, t)
		if evaldir==evalBoth or evaldir==evalNodeToRoot:
			addKey(db, valb, t)
		r.append(t)
		adj = g.adjacent(p,exc2,grid.isoperator,g)
		for a in adj:
			r.append([])
			charlistOp(g, a, exc2,r[-1],t,d,db,evaldir)
			if len(r[-1]) == 1: # dead end, no more than sinle operator
				r.pop()

def charlistOp(g, p, exc, r, prev, d, db, evaldir=evalBoth):
#	print 'charListOp r:',r
	if len(exc) < maxdepth:
		exc2 = exc + [p]
		t = (p,prev,bignum,bignum,len(exc2))
		r.append(t)
		adj = g.adjacent(p,exc2,grid.isnumber,g)
		for a in adj:
			r.append([])
			charlistNum(g, a, exc2,r[-1], t, d,db, evaldir)


def addKey(d,k,v):
	if k in d:
		d[k].append(v)
	else:
		d.update({k:[v]})

# g = Grid
# lp = list of positions
# vals = list ot tuples (tree, val dict left to right, val dict right to left)
def findLvalRval(g, lp):
	# sort x ascending, y descending
	lp.sort(key = lambda p: (p[0],-p[1]))
	lplen = len(lp)
	vals = []
	if lplen < 2:
		return vals
	vals.append(charlist(g, lp[0],evalNodeToRoot))
	for i in range(1,lplen-1):
		vals.append(charlist(g, lp[i],evalBoth))
	vals.append(charlist(g, lp[lplen-1],evalRootToNode))
	return vals

def findIfNoCommon(lvals,mid,rvals,reject):
#	print 'findIfNoCommon:',len(lvals),' ',len(rvals)
	for l in lvals:
		for r in rvals:
			if l[4] + r[4] + 1 < reject:
				return
			ll = nodesToRoot(l)
			rl = nodesToRoot(r,True)
			ls = set(ll)
			if not ls.intersection(set(rl)):
				return ll + mid + rl

			
def findMatch(lvals,mid,rvals,reject):
	m = []
	ld = lvals[2]
	rd = rvals[1]
	common_keys = ld.viewkeys() & rd.viewkeys()
	for k in common_keys:
		ld[k].sort(key = lambda p: -p[4])
		rd[k].sort(key = lambda p: -p[4])
		e = findIfNoCommon(ld[k],mid,rd[k],reject)
		if e:
			if len(e) > reject:
				reject = len(e)
			m.append((e,k))
	if m:
		m.sort(key = lambda p: -len(p[0]))
		#print 'val:',m[0][1]
		return m[0][0]
	


def findEquals(g):
	pl = g.findchar('=')
	bestmatch = []
	if pl:
		for p in pl:

			lp = list(g.adjacent(p,None,grid.isnumber,g))
			vals = findLvalRval(g, lp)
#			sort_by_val_len = lambda p: (-len(p[1]),p[0])
#			for i in range(len(lvals)):
#				lvals[i].sort(key = sort_by_val_len)
#				rvals[i].sort(key = sort_by_val_len)

			match = []
			reject = 0
			for i in range(len(vals)-1):
				for j in range(i+1,len(vals)):
					m = findMatch(vals[i],[p],vals[j],reject)
					if m:
						#print g.printBlocks(m)
						if len(m) > reject:
							reject = len(m)
						match.append(m)
			#print 'total matches:',len(match)
			match.sort(key = lambda p: len(p))
			if match:
				g.removeBlocks(match[-1])
				bestmatch.append(match[-1])
	return bestmatch

def evaluateAll(g, p,backToFront=False):
	l = []
	t,ld,rd = charlist(g, p)	
	for s in treeToList(t):
		l.append(s)
		print g.printBlocks(s)
	return l
		
def unitTest():
#	ll = [['3','+','2','+','1'],['3','2'],['+'],['3','-','2'],['3','-','2','-','1'],['0','-','0','+','0','-','1'],['0']]
#	for l in ll:
#		print l,'=',evaluateList(l)
	clist = ['7','-','1','2','+','8','3','+','4','5','6','-']
	plist = [(2,3),(3,3),(0,2),(1,2),(2,2),(3,2),(0,1),(1,1),(2,1),(0,0),(1,0),(2,0)]
	g = grid.Grid(4,4)
	g.addBlocks(plist,clist)
	g.printGrid()
	p = (0,1)
	print 'evaluate from:',p
	evaluateAll(g,p)
	#p = (2,0)
	#print 'evaluate from:',p
	#print evaluateAll(g,p)
	p = (0,0)
	print 'evaluate from:',p
	evaluateAll(g,p)

	g = grid.Grid(10,10)
	g.populate()
	g.printGrid()
	p = (0,9)
	print 'evaluate from:',p
	#print evaluateAll(g,p)
	el = findEquals(g)


#unitTest()