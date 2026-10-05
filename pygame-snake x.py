import pygame
import random
import os

pygame.init()

WIDTH, HEIGHT = 800, 500
BLOCK = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game X")
clock = pygame.time.Clock()

# Colors
BLACK=(0,0,0); WHITE=(255,255,255); GREEN=(0,200,0)
RED=(255,60,60); BLUE=(0,120,255)
PURPLE=(200,0,200); YELLOW=(255,220,0)
CYAN=(0,255,255); ORANGE=(255,165,0)
DARK=(25,25,35)

font = pygame.font.SysFont("arial", 26, bold=True)
big_font = pygame.font.SysFont("arial", 52, bold=True)

FILES={"normal":"highscore_normal.txt","hardcore":"highscore_hardcore.txt"}
for f in FILES.values():
    if not os.path.exists(f): open(f,"w").write("0")

def get_highscore(mode): return int(open(FILES[mode]).read()) if mode in FILES else 0

def save_highscore(mode,score):
    if mode in FILES and score>get_highscore(mode):
        open(FILES[mode],"w").write(str(score))

def draw_text(t,f,c,x,y,center=False):
    r=f.render(t,True,c); rect=r.get_rect()
    rect.center=(x,y) if center else (x,y)
    screen.blit(r,rect)

def rand_pos(exclude):
    while True:
        p=[random.randrange(0,WIDTH,BLOCK),random.randrange(0,HEIGHT,BLOCK)]
        if p not in exclude: return p

def draw_bg():
    for y in range(HEIGHT):
        col=(10,10,30+y//6)
        pygame.draw.line(screen,col,(0,y),(WIDTH,y))

# systems

def spawn_walls(snake,food):
    walls=[]
    while len(walls)<6:
        p=rand_pos(snake)
        if p!=food and p not in walls:
            walls.append(p)
    return walls

def spawn_enemy():
    return {"pos":rand_pos([]),"dx":BLOCK,"dy":0}

POWER_TYPES=["speed","slow","shield","double"]

def spawn_powerup(exclude):
    return {"pos":rand_pos(exclude),"type":random.choice(POWER_TYPES)}

MENU="menu"; MODE="mode"; PLAYING="playing"; GAMEOVER="gameover"; WINNER="winner"; PAUSE="pause"
state=MENU; mode="normal"; multiplayer=False; winner=""


def reset():
    s1=[[100,100]]; s2=[[300,300]]
    return {
        "s1":s1,"s2":s2,
        "dx1":BLOCK,"dy1":0,
        "dx2":-BLOCK,"dy2":0,
        "food":rand_pos(s1+s2),
        "score1":0,"score2":0,
        "walls":[],"enemies":[],
        "powerup":None,"power_timer":0,"power_type":None,"power_spawn_timer":0
    }

game=reset()

running=True
while running:
    draw_bg()

    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            running=False

        if e.type==pygame.KEYDOWN:
            if state==MENU and e.key==pygame.K_SPACE:
                state=MODE

            elif state==MODE:
                if e.key==pygame.K_1:
                    mode="normal"; multiplayer=False; game=reset(); state=PLAYING
                if e.key==pygame.K_2:
                    mode="hardcore"; multiplayer=False; game=reset(); state=PLAYING
                if e.key==pygame.K_3:
                    multiplayer=True; game=reset(); state=PLAYING

            elif state==PLAYING:
                if e.key==pygame.K_p:
                    state=PAUSE

                if e.key==pygame.K_w and game["dy1"]==0:
                    game["dx1"],game["dy1"]=(0,-BLOCK)
                if e.key==pygame.K_s and game["dy1"]==0:
                    game["dx1"],game["dy1"]=(0,BLOCK)
                if e.key==pygame.K_a and game["dx1"]==0:
                    game["dx1"],game["dy1"]=(-BLOCK,0)
                if e.key==pygame.K_d and game["dx1"]==0:
                    game["dx1"],game["dy1"]=(BLOCK,0)

                if multiplayer:
                    if e.key==pygame.K_UP and game["dy2"]==0:
                        game["dx2"],game["dy2"]=(0,-BLOCK)
                    if e.key==pygame.K_DOWN and game["dy2"]==0:
                        game["dx2"],game["dy2"]=(0,BLOCK)
                    if e.key==pygame.K_LEFT and game["dx2"]==0:
                        game["dx2"],game["dy2"]=(-BLOCK,0)
                    if e.key==pygame.K_RIGHT and game["dx2"]==0:
                        game["dx2"],game["dy2"]=(BLOCK,0)

            elif state==PAUSE and e.key==pygame.K_p:
                state=PLAYING

            elif state in [GAMEOVER,WINNER] and e.key==pygame.K_r:
                state=MENU

    if state==MENU:
        draw_text("SNAKE X",big_font,GREEN,WIDTH//2,HEIGHT//3,True)
        draw_text("Press SPACE",font,WHITE,WIDTH//2,HEIGHT//2,True)

    elif state==MODE:
        draw_text("Select Mode",big_font,YELLOW,WIDTH//2,HEIGHT//3,True)
        draw_text("1 Normal",font,WHITE,WIDTH//2,HEIGHT//2,True)
        draw_text("2 Hardcore",font,WHITE,WIDTH//2,HEIGHT//2+40,True)
        draw_text("3 Multiplayer",font,WHITE,WIDTH//2,HEIGHT//2+80,True)

    elif state==PAUSE:
        draw_text("PAUSED",big_font,YELLOW,WIDTH//2,HEIGHT//2,True)
        draw_text("Press P to Resume",font,WHITE,WIDTH//2,HEIGHT//2+50,True)

    elif state==PLAYING:
        # removed top strip for cleaner UI

        s1,s2=game["s1"],game["s2"]

        new1=[s1[0][0]+game["dx1"],s1[0][1]+game["dy1"]]
        s1.insert(0,new1)

        if multiplayer:
            new2=[s2[0][0]+game["dx2"],s2[0][1]+game["dy2"]]
            s2.insert(0,new2)

        gain = 2 if game["power_type"]=="double" else 1

        if new1==game["food"]:
            game["score1"]+=gain
            game["food"]=rand_pos(s1+s2)
        else:
            s1.pop()

        if multiplayer:
            if new2==game["food"]:
                game["score2"]+=gain
                game["food"]=rand_pos(s1+s2)
            else:
                s2.pop()

        # spawn systems (NO walls/enemies in multiplayer)
        if mode=="hardcore" and not multiplayer:
            if not game["walls"]:
                game["walls"]=spawn_walls(s1+s2,game["food"])
            if len(game["enemies"])<3 and random.random()<0.05:
                game["enemies"].append(spawn_enemy())

        if game["powerup"] is None and random.random()<0.01:
            game["powerup"] = spawn_powerup(s1+s2)
            game["power_spawn_timer"] = 100  # 10 sec

        # powerup timer (disappears if not collected)
        if game.get("powerup"):
            game["power_spawn_timer"] -= 1
            if game["power_spawn_timer"] <= 0:
                game["powerup"] = None

        # collect powerup
        if game["powerup"] and new1==game["powerup"]["pos"]:
            # ensure shield appears more reliably
            if random.random() < 0.3:
                game["power_type"] = "shield"
            else:
                game["power_type"] = game["powerup"]["type"]
            game["power_timer"] = 100
            game["powerup"] = None

        # apply effects
        speed=10
        if game["power_timer"]>0:
            if game["power_type"]=="speed": speed=15
            if game["power_type"]=="slow": speed=6
            game["power_timer"]-=1
        else:
            game["power_type"]=None

        # move enemies
        for en in game["enemies"]:
            if random.random()<0.2:
                en["dx"],en["dy"]=random.choice([(BLOCK,0),(-BLOCK,0),(0,BLOCK),(0,-BLOCK)])
            en["pos"][0]=(en["pos"][0]+en["dx"])%WIDTH
            en["pos"][1]=(en["pos"][1]+en["dy"])%HEIGHT

        # collisions with shield
        shield = game["power_type"]=="shield"

        # P1 border + self
        if new1[0]<0 or new1[0]>=WIDTH or new1[1]<0 or new1[1]>=HEIGHT or new1 in s1[1:]:
            if shield:
                game["power_type"]=None
            else:
                state=GAMEOVER

        # P2 border + self (multiplayer FIX)
        if multiplayer:
            if new2[0]<0 or new2[0]>=WIDTH or new2[1]<0 or new2[1]>=HEIGHT or new2 in s2[1:]:
                winner="Player 1 Wins!"
                state=WINNER

        # P1 collision fix (multiplayer winner)
        if new1[0]<0 or new1[0]>=WIDTH or new1[1]<0 or new1[1]>=HEIGHT or new1 in s1[1:]:
            if shield:
                game["power_type"] = None
            else:
                if multiplayer:
                    winner = "Player 2 Wins!"
                    state = WINNER
                else:
                    state = GAMEOVER

        if new1 in game["walls"]:
            if shield: game["power_type"]=None
            else: state=GAMEOVER

        for en in game["enemies"]:
            if new1==en["pos"]:
                if shield: game["power_type"]=None
                else: state=GAMEOVER

        # draw snake
        for i,p in enumerate(s1):
            col=(0,255,0) if i==0 else (0,150,0)
            pygame.draw.rect(screen,col,(*p,BLOCK,BLOCK),border_radius=6)
            # shield glow effect
            if game.get("power_type")=="shield":
                glow_rect = pygame.Rect(p[0]-2, p[1]-2, BLOCK+4, BLOCK+4)
                pygame.draw.rect(screen, BLUE, glow_rect, 2, border_radius=8)

        if multiplayer:
            for i,p in enumerate(s2):
                col=(0,200,255) if i==0 else (0,100,200)
                pygame.draw.rect(screen,col,(*p,BLOCK,BLOCK),border_radius=6)
                # shield glow effect for P2
                if game.get("power_type")=="shield":
                    glow_rect = pygame.Rect(p[0]-2, p[1]-2, BLOCK+4, BLOCK+4)
                    pygame.draw.rect(screen, BLUE, glow_rect, 2, border_radius=8)

        pygame.draw.circle(screen,RED,(game["food"][0]+10,game["food"][1]+10),10)

        for w in game["walls"]:
            pygame.draw.rect(screen,(180,180,180),(*w,BLOCK,BLOCK),border_radius=4)

        for en in game["enemies"]:
            pygame.draw.rect(screen,PURPLE,(*en["pos"],BLOCK,BLOCK),border_radius=8)

        # draw powerup
        if game["powerup"]:
            color={"speed":YELLOW,"slow":CYAN,"shield":BLUE,"double":ORANGE}[game["powerup"]["type"]]
            pygame.draw.circle(screen,color,(game["powerup"]["pos"][0]+10,game["powerup"]["pos"][1]+10),10)

        draw_text(f"P1:{game['score1']}",font,GREEN,80,20)
        if multiplayer: draw_text(f"P2:{game['score2']}",font,BLUE,WIDTH-120,20)
        if not multiplayer: draw_text(f"High:{get_highscore(mode)}",font,WHITE,WIDTH-150,20)

        if not multiplayer: save_highscore(mode,game["score1"])

        clock.tick(speed)

    elif state in [GAMEOVER,WINNER]:
        overlay=pygame.Surface((WIDTH,HEIGHT)); overlay.set_alpha(160); overlay.fill((0,0,0))
        screen.blit(overlay,(0,0))

        if state==GAMEOVER:
            draw_text("GAME OVER",big_font,RED,WIDTH//2,HEIGHT//2,True)
        else:
            draw_text(winner,big_font,YELLOW,WIDTH//2,HEIGHT//2,True)

        draw_text("Press R",font,WHITE,WIDTH//2,HEIGHT//2+60,True)

    pygame.display.flip()

pygame.quit()