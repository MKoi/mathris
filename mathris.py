import block
import grid
import evaluate
import random
import pygame
from recordtype import recordtype
from pygame.locals import *
from block import Block

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
targetfps = 60
screen_width = 240 #480
screen_height = 400 #800

# A and B = tuple(width, height)
# return p scaled by (B/A)
def posTransform(p, A, B):
	rx = B[0] / A[0]
	ry = B[1] / A[1]
	return p[0]*rx,B[1]-p[1]*ry
	

def gridToScreen(p, g):
	p2 = (p[0],p[1]+1)
	return posTransform(p2, (g.w,g.h), (screen_width,screen_height))

def screenToGrid(p, g):
	pg = posTransform(p, (screen_width,screen_height), (g.w,g.h))
	return (pg[0],pg[1]-1)
	

def createCharGfx(g):
	bw,bh = gridToScreen((1,g.h-2), g)
	br = pygame.Rect(0, 0, bw, bh)
	charfont = pygame.font.Font(None, bh)
	chars = '+-=0123456789'
	r = {}
	for c in chars:
		chargfx = charfont.render(c, 0, WHITE)
		r[c] = chargfx
	return r
	

# g = grid
def createBlockGfx(g):
	bw,bh = gridToScreen((1,g.h-2), g)
	br = pygame.Rect(0, 0, bw, bh)
	s = pygame.Surface(br.size)
	pygame.draw.rect(s, WHITE, br, 3)
	return s

# p = screen position
# c_gfx = char gfx
# r_gfx = rectangle gfx
def drawBlockGfx(p, c_gfx, r_gfx, s):
	dx = 0.5 * (r_gfx.get_rect().w - c_gfx.get_rect().w)
	dy = 0.5 * (r_gfx.get_rect().h - c_gfx.get_rect().h)
	pc = (p[0]+dx,p[1]+dy)
	s.blit(r_gfx, p)
	s.blit(c_gfx, pc)

# g = grid
# b = block
# gfx = block gfx
# c_gfx = char gfx
# s = surface to blit to
def drawGfx(b, g, gfx, c_gfxm, s):
	if b:
		for i in range(len(b.chars)):
			pg = b.positions()[i]
			ps = gridToScreen(pg, g)
			#print 'blit block: ', ps
			c_gfx = c_gfxm[b.chars[i]]
			drawBlockGfx(ps, c_gfx, gfx, s) 
	for x in range(g.w):
		for y in range(g.h):
			p = (x,y)
			if grid.occupied(p,g):
				ps = gridToScreen(p, g)
				c_gfx = c_gfxm[g.grid[x][y]]
				drawBlockGfx(ps, c_gfx, gfx, s)
			

# chars = chars of block
# pos = block position
def generateBlock(chars,pos=(5,20)):
	sl = Block.possibleshapes(len(chars))
	s = random.choice(sl)
	return Block(pos,s,chars)

def generateChars(g):
	im = random.randint(1,block.Block.maxchars)
	l = []
	while im:
		c = random.choice('0123456789') if im%2 else random.choice('+-=')
		l.append(c)
		im -= 1
	return l

# b = list of positions
# g = grid
# f = function to use in iteration
# m = max iterations
def spacesFree(b, g, f, m):
	for i in range(1,m):
		b2 = [f(p, i) for p in b]
		if any((grid.occupied(p,g) or not grid.inbounds(p,g)) for p in b2):
			break
	return i

def spacesBottom(b,g):
	return spacesFree(b.bottom(),g, lambda p, i : (p[0],p[1]-i), g.h)

def spacesTop(b,g):
	return spacesFree(b.top(),g, lambda p, i : (p[0],p[1]+i), g.h)

def spacesLeft(b,g):
	return spacesFree(b.left(),g, lambda p, i : (p[0]-i,p[1]), g.w)

def spacesRight(b,g):
	return spacesFree(b.right(),g, lambda p, i : (p[0]+i,p[1]), g.w)

def bottomTouch(b, g):
	return spacesBottom(b,g) <= 1
		
def topTouch(b, g):
	return spacesTop(b,g) <= 1
	
def leftTouch(b, g):
	return spacesLeft(b,g) <= 1
	
def rightTouch(b, g):
	return spacesRight(b,g) <= 1

def overLap(b, g):
	return any((grid.occupied(p,g) or p[0] < 0 or p[0] >= g.w or p[1] < 0) for p in b.positions())

def checkMatches(g):
	m = evaluate.findEquals(g)
	while m:
		print m
		islands = g.islands()
		for l in islands:
			g.shiftDown(l)
		m = evaluate.findEquals(g)


def main():
	
	pygame.init()
	screen = pygame.display.set_mode((screen_width, screen_height))
	pygame.display.set_caption('Mathris')
	pygame.mouse.set_visible(0)
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill(BLACK)
	
	
	g = grid.Grid(10,20)
	
	b = generateBlock(generateChars(g))
	gfx = createBlockGfx(g)
	charGfx = createCharGfx(g)
	screen.blit(background, (0, 0))
	pygame.display.flip()
	
	exitgame = False
	max_key_interval = 200
	max_rot_key_interval = 150
	min_key_interval = 50
	key_factor = 0.8
	Key = recordtype('Key', [('t_action',0), ('t_repeat',200)])
	def setDefaults(k):
		k.t_action = 0
		k.t_repeat = max_key_interval
	def reduceKeyInterval(k):
		k.t_repeat *= key_factor
		if k.t_repeat < min_key_interval:
			k.t_repeat = min_key_interval
		k.t_action = k.t_repeat
	rightkey = Key()
	leftkey = Key()
	upkey = Key(t_action = 0, t_repeat = max_rot_key_interval)
	fall_time_sec = 5.0
	ms_per_row = 1000.0 * fall_time_sec / g.h
	dropkey_handled = False
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
		pressed = pygame.key.get_pressed()
		if pressed[pygame.K_LEFT] and not pressed[pygame.K_RIGHT]:
			if not leftTouch(b, g):
				leftkey.t_action -= dt
				if leftkey.t_action < 0:
					b.moveleft()
					reduceKeyInterval(leftkey)
		if pressed[pygame.K_RIGHT] and not pressed[pygame.K_LEFT]:
			if not rightTouch(b, g):
				rightkey.t_action -= dt
				if rightkey.t_action < 0:
					b.moveright()
					reduceKeyInterval(rightkey)
		
		if not pressed[pygame.K_RIGHT]:
			setDefaults(rightkey)
		if not pressed[pygame.K_LEFT]:
			setDefaults(leftkey)
		if pressed[pygame.K_UP]:
			upkey.t_action -= dt
			if upkey.t_action < 0:
				b.rotate()
				upkey.t_action = upkey.t_repeat
				if overLap(b,g):
					b.rotate(False)
					upkey.t_action = 0
		if not pressed[pygame.K_UP]:
			upkey.t_action = 0
		if pressed[pygame.K_DOWN] and not dropkey_handled:
			while not bottomTouch(b,g):
				b.movedown()
			ms_per_row = 0
			dropkey_handled = True
		if not pressed[pygame.K_DOWN] and dropkey_handled:
			dropkey_handled = False
			
		ms_per_row -= dt
		if ms_per_row < 0.0:
			if bottomTouch(b, g):
				g.addBlocks(b.positions(),b.chars)
				checkMatches(g)
				
				b = generateBlock(generateChars(g))
				if overLap(b,g):
					b = None
					exitgame = True
			else:
				b.movedown()
			ms_per_row = 1000.0 * fall_time_sec / g.h
			
			
		screen.blit(background, (0, 0))
		drawGfx(b, g, gfx, charGfx, screen)
		pygame.display.flip()	
	
main()