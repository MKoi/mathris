import os, sys
import random
from random import shuffle
import pygame
from pygame.locals import *


targetfps = 60
screen_width = 480
screen_height = 800
fontsize = 24
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Robo creator')
pygame.mouse.set_visible(1)


background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(BLACK)


def longest_common_substring(s1, s2):
	m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
	longest, x_longest = 0, 0
	for x in range(1, 1 + len(s1)):
		for y in range(1, 1 + len(s2)):
			if s1[x - 1] == s2[y - 1]:
				m[x][y] = m[x - 1][y - 1] + 1
				if m[x][y] > longest:
					longest = m[x][y]
					x_longest = x
			else:
				m[x][y] = 0
	return s1[x_longest - longest: x_longest]


class TextBuffer():
	
	bufferfont = pygame.font.Font(None, fontsize)
	
	def __init__(self, rect):
		self.pos = (0,0) # word, row
		self.text = [[]]
		self.textgfx = None
		self.rect = rect
		self.cursorgfx = pygame.Surface((self.bufferfont.size('_')[0], self.bufferfont.get_linesize()))
		pygame.draw.rect(self.cursorgfx, WHITE, self.cursorgfx.get_rect(), 0)
		self.cursorpos = self.rect.topleft
		self.cursorVisible = False
	
	def addtext(self, t):
		if not t:
			return

		if t[-1] == '\n':
			if len(t) > 1:
				self.text[-1].append(t[:-1]) # new word
			self.text.append([]) # new line
			self.pos = (0, self.pos[1] + 1)
		else:
			self.text[-1].append(t)
			self.pos = (self.pos[0] + 1, self.pos[1])
		self.generategfx()
		
	def delete(self):
		if self.pos[0]:
			del self.text[self.pos[1]][self.pos[0] - 1] #delete word
			self.pos = (self.pos[0] - 1, self.pos[1]) #decrement word
		elif self.pos[1]:
			if not self.text[self.pos[1]]:
				del self.text[self.pos[1]]
			newrow = self.pos[1] - 1
			self.pos = (len(self.text[newrow]), newrow)
		self.generategfx()
	
	
	def generatelines(self):
		res = []
		for l in self.text:
			line = ''
			for w in l:
				if line:
					line += ' '
				line += w
			res.append(line)
		return res
	
	def generategfx(self):
		lines = self.generatelines()
 		# first pass to find out image dimensions
 		w = h = 0
 		i = 0
 		for l in lines:
 			w = max(w, self.bufferfont.size(l)[0])
 			if i == self.pos[1]:
 				self.cursorpos = (self.rect.x + self.bufferfont.size(l)[0], self.rect.y + h)
 			h += self.bufferfont.get_linesize()
 			i += 1

 		self.textgfx = pygame.Surface((w, h))
 		# second pass to render to surface
 		h = 0
 		for l in lines:
 			t = self.bufferfont.render(l, 0, WHITE)
 			self.textgfx.blit(t, (0, h))
 			h += self.bufferfont.get_linesize()

	
	def draw(self, surface):
		if self.textgfx:
			surface.blit(self.textgfx, self.rect)
		surface.blit(self.cursorgfx, self.cursorpos)
	

class TextButton():
	
	buttonfont = pygame.font.Font(None, fontsize)
	
	def __init__(self, x, y, w, h, text):
		self.text = text
		textgfx = self.buttonfont.render(text, 0, WHITE)
		textgfx_pressed = self.buttonfont.render(text, 0, BLACK)
		self.rect = pygame.Rect(0, 0, w, h)
		self.surface = pygame.Surface(self.rect.size)
		self.surface_pressed = pygame.Surface(self.rect.size)
		pygame.draw.rect(self.surface, WHITE, self.rect, 3)
		pygame.draw.rect(self.surface_pressed, WHITE, self.rect, 0)
		textrect = textgfx.get_rect()
		textrect.center = int(w / 2), int(h / 2)
		self.surface.blit(textgfx, textrect)
		self.surface_pressed.blit(textgfx_pressed, textrect)
		self.rect.topleft = (x, y)
		self.touchrect = self.rect.inflate(int(-w/4), int(-h/4))
		self.pressed = False
		
	def draw(self, surface):
		if self.pressed:
			surface.blit(self.surface_pressed, self.rect)
		else:
			surface.blit(self.surface, self.rect)

	def handleEvent(self, eventObj):
		if eventObj.type == MOUSEBUTTONDOWN and self.touchrect.collidepoint(eventObj.pos):
			self.pressed = True
			return self.text
		elif not self.pressed and pygame.mouse.get_pressed()[0] and eventObj.type == MOUSEMOTION and self.touchrect.collidepoint(eventObj.pos):
			self.pressed = True
			return self.text
		elif eventObj.type == MOUSEBUTTONUP:
			self.pressed = False

class TextButtonGroup():
	
	xspacing = 3
	yspacing = 3
	buttonw = 64
	buttonh = 64
	rows = 6
	cols = 6
	
	def __init__(self, sx, sy, tlist):
		screenx = lambda gridx: sx + (self.buttonw + self.xspacing) * gridx
		screeny = lambda gridy: sy + (self.buttonh + self.yspacing) * gridy
		
		self.buttons = [[TextButton(screenx(x),screeny(y),self.buttonw,self.buttonh, tlist[min(len(tlist)-1, y * self.cols + x)]) for y in range(self.rows)] for x in range(self.cols)] 
		
	
	def draw(self, surface):
		for i in self.buttons:
			for b in i:
				b.draw(surface)
	
	def handleEvent(self, eventObj):
		for i in self.buttons:
			for b in i:
				retval = b.handleEvent(event)
				if retval:
					return retval
		return retval


class InputState():
	
	beginstate = 0
	endstate = 0
	endstr = '[ENTER]'
	
	# state : [(next state, token)]
	tokens = {
		-1: [(0,'while')],
		'start': [('assignment','[VARIABLE]'),(2,'return'),(3,'while'),(-1,'end')],
		'assignment': [('expression','=')],
		'expr': [('rp_expr','('),]
		'rp_expr': [('rp_expr_ops','[VARIABLE]'),('rp_expr_ops','[NUMBER]')],
		'rp_expr_ops': [('rp_expr','[VARIABLE]'),('rp_expr','[NUMBER]')],
		2: [(0,'[VARIABLE]'),(0,'[LITERAL]')],
		3: [(5,'[VARIABLE]'),(5,'[LITERAL]'),(4,'(')],
		4: [(4,'[VARIABLE]'),(0,'[LITERAL]')],
		5: [(5,'<'),(5,'>'),(5,'='),(5,'='),(5,'='),(5,'=')],
		5: [(5,'<'),(5,'>'),(5,'='),(5,'='),(5,'='),(5,'=')],
		5: [(4,'[VARIABLE]'),(0,'[LITERAL]')],
			
	# 0 is start state, negative values require additional condition to be checked
	states = {
		-1: [(0,'if'),(0,'while'),(0,'loop')],
		0: [(1,'move'),(1,'shoot'),(2,'if'),(2,'while'),(0,'loop'),(-1,'end')],
		1: [(0,'north'),(0,'west'),(0,'south'),(0,'east')], 
		2: [(3,'my robot'),(5,'enemy'),(5,'block')],
		3: [(16,'is')],
		4: [(2,'and'),(2,'or'),(0,'[ENTER]')],
		5: [(13,'is'),(8,'in')],
		6: [(7,'somewhere'),(7,'directly'),(4,'north'),(4,'west'),(4,'south'),(4,'east')],
		7: [(4,'north'),(4,'west'),(4,'south'),(4,'east')],
		8: [(9,'somewhere'),(9,'directly'),(10,'north'),(10,'west'),(10,'south'),(10,'east')],
		9: [(10,'north'),(10,'west'),(10,'south'),(10,'east')],
		10: [(14, 'is')],
		11: [(4,'range'),(12,'1'),(12,'2'),(12,'3'),(12,'4'),(12,'5'),(12,'6'),(12,'7'),(12,'8'),(12,'9')],
		12: [(4,'block')],
		13: [(6,'not'),(7,'somewhere'),(7,'directly'),(4,'north'),(4,'west'),(4,'south'),(4,'east')],
		14: [(15,'not'),(11,'within')],
		15: [(11,'within')],
		16: [(18,'within'),(17,'not')],
		17: [(18,'within')],
		18: [(19,'enemy')],
		19: [(4,'range')],
		}


	def __init__(self):
		self.beginstate = 0
		self.endstate = 0
		self.endstr = '[ENTER]'
		self.rejectreason = ''
		self.hint = ''
		self.acceptedinput = []
		self.conditions = { -1: self.hasMatchingStart }
	
	def getRandomInput(self, hint):
		rndkeys = self.states.keys()
		shuffle(rndkeys)
		for k in rndkeys:
			t = self.matchtext(hint,k)
			if t:
				break
		firstpart = self.getRandomStatesFromBeginning(k)
		lastpart = self.getRandomStatesToEnd(t)
		statelist = firstpart + lastpart
		textlist = []
		for t in statelist:
			if t[1] != self.endstr:
				textlist.append(t[1])
		return textlist, len(firstpart)

	def getRandomStatesToEnd(self, t, endifpossible = True):
		statelist = []
		statelist.append(t)
		while t[0] != self.endstate:
			if endifpossible:
				nextstates = []
				for x in self.states[t[0]]:
					if x[0] == self.endstate:
						nextstates.append(x)
				if nextstates:
					t = random.choice(nextstates)
				else:
					t = random.choice(self.states[t[0]])
			else:
				t = random.choice(self.states[t[0]])
			statelist.append(t)
		return statelist
	
	def getRandomStatesFromBeginning(self, key):
		statelist = []
		while key != self.beginstate:
			t,key = self.getRandomPrevState(key)
			statelist.insert(0,t)
		return statelist
		
	def getRandomPrevState(self, key):
		prevstates = []
		for k, v in self.states.items():
			for t in v:
				if t[0] == key:
					prevstates.append((t,k))
		for t in prevstates:
			if t[1] == self.beginstate:
				#print "return ", t
				return t
		return random.choice(prevstates)

	def acceptInput(self, slist):
		if not slist:
			return False #empty input rejected
		conditionCheck = True
		i = self.beginstate
		# go through words in input list
		# print slist
		for s in slist:
			t = self.matchtext(s, i) # get next state if any
			if t:
				#print 'found', s, i
				if i < 0 and i in self.conditions:
					conditionCheck = self.conditions[i](s)
				i = t[0]
			else:
				#print 'not found', s, i
				break # no next state
		if i != self.endstate:
			# not yet in end state but check if current state has special transition to end
			t = self.matchtext(self.endstr, i)
			if t:
				i = t[0]
		if s == slist[-1] and i == self.endstate and conditionCheck:
			self.acceptedinput.append(slist)
			return True
		elif s != slist[-1]:
			self.rejectreason = 'unexpected input:{}'.format(s)
		elif i != self.endstate:
			self.rejectreason = 'unexpected end of command:{}'.format(s)
		elif not conditionCheck:
			self.rejectreason = 'missing matching {} statemens'.format(s)
		return False
	
	
	def matchtext(self,text,i):
		for t in self.states[i]:
			if t[1] == text:
				return t
	
	def hasMatchingStart(self, text):
		matchedtext = [text]
		for i in reversed(self.acceptedinput):
			if i and i[0] == matchedtext[-1]:
				matchedtext.pop()
				if not matchedtext:
					return True
			elif len(i) > 2 and i[0] == 'end':
				matchedtext.append(i[1])
		return False


	
class WordGrid():
	def __init__(self, w, h):
		self.width = w
		self.height = h
		self.grid = [['' for y in range(h)] for x in range(w)]
		self.wcount = 0
	
		
	def findAdjacent(self, x, y, w = '', excludeList=None, acceptEmpty=True):
		foundword = []
		foundempty = []
		x_indices = set((max(0,x-1),x,min(self.width-1,x+1)))
		y_indices = set((max(0,y-1),y,min(self.height-1,y+1)))
		for x1 in x_indices:
			for y1 in y_indices:
				if x1 != x or y1 != y:
					if not excludeList or (excludeList and (x1,y1) not in excludeList):
						if self.grid[x1][y1] == w: 
							foundword.append((x1,y1))
						elif acceptEmpty and self.grid[x1][y1] == '':
							foundempty.append((x1,y1))
		return foundword, foundempty
	
	def findAdjacentList(self, x, y, wlist = None, excludeList=None):
		if not wlist:
			return
		#print "find list: ", wlist
		slots = []
		free1,free2 = self.findAdjacent(x, y, wlist[0], excludeList)
		freelist = [free1,free2]
		for free in freelist:
			if free:
				if len(wlist) == 1:
					candidate = random.choice(free)
					slots.append(candidate)
				else:
					random.shuffle(free)
					for candidate in free:
						slots.append(candidate)
						newExcludeList = excludeList + [candidate]
						newSlots = self.findAdjacentList(candidate[0], candidate[1], wlist[1:], newExcludeList)
						#print "newslots len(",len(newSlots),") wlist len(",len(wlist),")"
						if newSlots and (len(newSlots) == len(wlist) - 1):
							slots.extend(newSlots)
							#print "found: ", slots
							break
			if len(slots) == len(wlist):
				return slots
		return slots
	
	def addAdjacent(self, x, y, w):
		free = self.findAdjacent(x, y)
		if not free:
			return None
		x,y = random.choice(free)
		self.grid[x][y] = w
		self.wcount += 1
		return (x,y)
	
	def addWord(self, w, x, y):
		if x in range(self.width) and y in range(self.height):
			if not self.grid[x][y]:
				self.wcount += 1
			self.grid[x][y] = w
			
	
	def removeWord(self, x, y):
		if x in range(self.width) and y in range(self.height):
			if self.grid[x][y]:
				self.grid[x][y] = ''
				self.wcount -= 1
	
	def getFreeSlots(self, wlist, pos, exclude):
		if not wlist or self.freeSlots() < len(wlist):
			print "required slots ", len(wlist), " > free slots ", self.freeSlots()
			return
		#print "slots for words: ", wlist
		freeList = []
		range_x = range(pos[0],pos[0]+1) if pos else range(self.width)
		range_y = range(pos[1],pos[1]+1) if pos else range(self.height)
		for x in range_x:
			for y in range_y:
				if self.grid[x][y] == wlist[0] or self.grid[x][y] == '':
					if exclude and (x,y) in exclude:
						print "exclude ", (x,y)
						continue
					slotList = [(x,y)]
					excludeList = list(slotList)
					if exclude:
						excludeList += exclude
					if len(wlist) > 1:
						#print "trying to get slotlist x:" + str(x) + " y:" + str(y)
						slotList.extend(self.findAdjacentList(x,y,wlist[1:],excludeList))
						#print "found list: ", slotList
					if len(slotList) == len(wlist):
						freeList.append(slotList)					
		return random.choice(freeList) if freeList else None
		
	def asList(self):
		retval = []
		for y in range(self.height):
			for x in range(self.width):
				retval.append(self.grid[x][y])
		return retval
	
	def freeSlots(self):
		return self.width * self.height - self.wcount
			
	def addWordList(self, wlist, pos = None, exclude = None):
		slots = self.getFreeSlots(wlist, pos, exclude)
		if slots:
			self.addWordListToSlots(wlist, slots)
		return slots

	def addWordListToSlots(self, wlist, slots):
		for i in range(len(slots)):
			self.addWord(wlist[i],slots[i][0],slots[i][1])

	def removeWordList(self, slist):
		if not slist:
			return
		for s in slist:
			self.removeWord(s[0],s[1])
			

class InputManager():
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.inputstates = InputState()
		self.wordgrid = WordGrid(TextButtonGroup.cols, TextButtonGroup.rows)
		self.generateInput()
		self.inputwords = []
		self.buttons = TextButtonGroup(x,y,self.wordgrid.asList())
		
	
	def generateInput(self):
		seedwords = ['my robot','enemy','range']
		seedwlist = self.inputstates.getRandomInput(random.choice(seedwords))[0]
		slots = self.wordgrid.addWordList(seedwlist)
		if not slots:
			return
		for i in range(len(slots)):
			#print "seedword ", seedwlist[i]
			w,pos = self.inputstates.getRandomInput(seedwlist[i])
			print "new input ", w
			w_end = w[pos:]
			w_beginning = list(reversed(w[:pos + 1])) # include pos also
			print "trying to add ", w_end, " to ", slots[i]
			slots_end = self.wordgrid.addWordList(w_end,slots[i])
			print "trying to add", w_beginning
			if slots_end and w_beginning:
				print "added ", w_end
				exclude = slots_end[1:] if len(slots_end) > 1 else None
				slots_beg = self.wordgrid.getFreeSlots(w_beginning, slots[i], exclude)
				if slots_beg:
					self.wordgrid.addWordListToSlots(w_beginning, slots_beg)
			
			
		
		
	def draw(self, surface):
		self.buttons.draw(surface)
	
	def handleEvent(self, eventObj):
		t = self.buttons.handleEvent(eventObj)
		if t:
			self.inputwords.append(t)
		if eventObj.type == MOUSEBUTTONUP:
			retval = None
			if self.inputstates.acceptInput(self.inputwords):
				retval = list(self.inputwords)
			self.inputwords = []
			return retval



screen.blit(background, (0, 0))
pygame.display.flip()

inputmgr = InputManager(10, 400)
textbfr = TextBuffer(pygame.Rect(10, 10, 470, 380))

exitgame = False
clock = pygame.time.Clock()
while not exitgame:
	dt = clock.tick(targetfps)
	for event in pygame.event.get():
		if event.type == QUIT:
			exitgame = True
			break
		elif event.type == KEYDOWN and event.key == K_ESCAPE:
			exitgame = True
			break
		t = inputmgr.handleEvent(event)
		if t:
			print t
			pass #textbfr.addtext(t)
			
	screen.blit(background, (0, 0))
	inputmgr.draw(screen)
	textbfr.draw(screen)
	pygame.display.flip()
