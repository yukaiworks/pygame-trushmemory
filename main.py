# 神経衰弱　分別版
# github 用に作り直した
# https://qiita.com/Prosamo/items/de12a90ba026b7517d2a

import pygame
from pygame.locals import *
import sys
import random
import asyncio

SCREEN_RECT = Rect(0, 0, 1000, 800)
BG_COLOR = (233, 146, 13)
FONT_COLOR = (18, 65, 112)
TICK = 20

# 画像
IMG_PATH_FOODWASTE = ["./img/apple_core.png","./img/fish_bone.png","./img/potato_peels.png"]
IMG_PATH_CANS = ["./img/can_of_tea.png","./img/can_of_tomatoes.png"]
IMG_PATH_PLASTICS = ["./img/plastic_hanger.png","./img/shopping_bag.png","./img/tooth_brush.png","./img/chip_bag.png"]
IMG_PATH_JOKER = "./img/litium.png"
IMG_PATH_LIFE = "./img/heart.png"
IMG_PATH_CHECK_ICON = "./img/check_icon.png"
IMG_PATH_PATTERN = "./img/pattern.png"
IMG_PATH_BG_FUKIDASI = "./img/fukidasi.png"
IMG_PATH_TITLE = "./img/title.png"
IMG_PATH_RESULT = "./img/result.png"

# 音
HIT_SOUND_PATH = "./sound/hit.ogg"
BEEP_SOUND_PATH = "./sound/beep4.ogg"
FLIP_SOUND_PATH = "./sound/flipcard.ogg"
CHAIME_SOUND_PATH = "./sound/chaime.ogg"
DECISION_SOUND_PATH = "./sound/decision44.ogg"

TYPE_JOKER = 0
TYPE_FOODWASTE = 1
TYPE_CANS = 2
TYPE_PLASTICS = 3
desc_trush = {TYPE_JOKER:["リチウムイオンでんち","","すてかた ちゅうい！","もえるごみに いれては いけません！","かじに なります"],
             TYPE_FOODWASTE:["なまごみ","","コンポストに いれると、つちに かえります"],
             TYPE_CANS:["カン","","かいしゅうして、カンに うまれかわります"],
             TYPE_PLASTICS:["プラスチック","","かいしゅうして、プラスチックに","うまれかわります"]}

pygame.init()

joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print('ジョイスティックの名前:', joystick.get_name())
    print('ボタン数 :', joystick.get_numbuttons())
        
screen = pygame.display.set_mode(SCREEN_RECT.size)
font_lg = pygame.font.Font("KosugiMaru-Regular.ttf", 50)
font_md = pygame.font.Font("KosugiMaru-Regular.ttf", 30)
font_sm = pygame.font.Font("KosugiMaru-Regular.ttf", 24)
clock = pygame.time.Clock()

class Trush(pygame.sprite.Sprite):
    def __init__(self, img_path, trushtype = None, x = 0, y = 0):
        self.image = pygame.transform.scale((pygame.image.load(img_path).convert_alpha()), (200,200))
        self.pos = (x, y)
        self.trushtype = trushtype
        self.is_open = False
        self.image_back = pygame.Surface((200,200), SRCALPHA)
        pygame.draw.circle(self.image_back,(230, 230, 230),(100,100),100)
        pattern_img = pygame.transform.scale(pygame.image.load(IMG_PATH_PATTERN).convert_alpha(),(180,180))
        self.image_back.blit(pattern_img, (10,10))

    def draw(self, screen):
        if self.is_open:
            screen.blit(self.image, self.pos)
        else:
            screen.blit(self.image_back, self.pos)
    def draw_pointing(self, screen):
        rect = self.image.get_rect(topleft= self.pos)
        pygame.draw.circle(screen, (200, 100, 100), rect.center,100, 5)
    def is_inside(self, point):
        rect = self.image.get_rect(topleft= self.pos)
        return rect.collidepoint(point)

#
# ゲームメイン画面
#
async def gamemain():
    # ライフ
    life = 3
    life_img = pygame.transform.scale(pygame.image.load(IMG_PATH_LIFE).convert_alpha(), (40,40)) 

    # サウンド
    hit_sound = pygame.mixer.Sound(HIT_SOUND_PATH)
    beep_sound = pygame.mixer.Sound(BEEP_SOUND_PATH)
    flip_sound = pygame.mixer.Sound(FLIP_SOUND_PATH)

    # カード準備　それぞれ2枚ずつと、ジョーカー。
    gap = 20
    trush_list = []
    trush_list.append(Trush(IMG_PATH_JOKER, TYPE_JOKER))
    for path in random.sample(IMG_PATH_FOODWASTE, 2):
        trush_list.append(Trush(path, TYPE_FOODWASTE))
    for path in random.sample(IMG_PATH_CANS, 2):
        trush_list.append(Trush(path, TYPE_CANS))
    for path in random.sample(IMG_PATH_PLASTICS, 2):
        trush_list.append(Trush(path, TYPE_PLASTICS))
    random.shuffle(trush_list)
    for idx, trush in enumerate(trush_list):
        if idx in [0, 2, 5]:
            x = SCREEN_RECT.width/2 - trush.image.get_width() - gap
        elif idx in [1, 3, 6]:
            x = SCREEN_RECT.width/2
        elif idx in [4]:
            x = SCREEN_RECT.width/2 + trush.image.get_width() + gap
        if idx < 2:
            y = 50
        elif idx < 5:
            x -= trush.image.get_width()/2
            y = 250 + gap*2
        else:
            y = 450 + gap*4
        trush.pos = (x, y)

    pointing_idx = 0
    checking_list = []
    while True:
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                # 十字キー　ポインターの移動
                if event.key == K_DOWN and pointing_idx < len(trush_list) -2:
                    if pointing_idx == 2:
                        pointing_idx += 1
                    pointing_idx += 2
                elif event.key == K_UP and pointing_idx > 1:
                    if pointing_idx == 4:
                        pointing_idx -= 1
                    pointing_idx -= 2
                elif event.key == K_RIGHT and pointing_idx in [0,2,3,5]:
                    pointing_idx += 1
                elif event.key == K_LEFT and pointing_idx in [1,3,4,6]:
                    pointing_idx -= 1

                # エンター
                if len(checking_list) < 2 and event.key == K_RETURN:
                    if not trush_list[pointing_idx].is_open:
                        flip_sound.play()
                        trush_list[pointing_idx].is_open = True
                        checking_list.append(trush_list[pointing_idx])
            elif event.type == MOUSEBUTTONDOWN: # タッチに対応
                for i, trush in enumerate(trush_list):
                    if not trush_list[i].is_open and trush.is_inside(event.pos):
                        pointing_idx = i
                        flip_sound.play()
                        trush_list[pointing_idx].is_open = True
                        checking_list.append(trush_list[pointing_idx])
                        break
            elif event.type == JOYBUTTONDOWN and joystick.get_button(0) and len(checking_list) < 2 :
                if not trush_list[pointing_idx].is_open:
                    flip_sound.play()
                    trush_list[pointing_idx].is_open = True
                    checking_list.append(trush_list[pointing_idx])
            elif event.type == JOYAXISMOTION:
                if joystick.get_axis(1) > 0.0 and pointing_idx < len(trush_list) -2:#DOWN
                    if pointing_idx == 2:
                        pointing_idx += 1
                    pointing_idx += 2
                elif joystick.get_axis(1) < 0.0 and pointing_idx > 1:#UP
                    if pointing_idx == 4:
                        pointing_idx -= 1
                    pointing_idx -= 2
                elif joystick.get_axis(0) > 0.0 and pointing_idx in [0,2,3,5]:#RIGHT
                    pointing_idx += 1
                elif joystick.get_axis(0) < 0.0 and pointing_idx in [1,3,4,6]:#LEFT
                    pointing_idx -= 1
        
        screen.fill(BG_COLOR)
        screen.blit(font_sm.render("↑↓→←:いどう", True, FONT_COLOR), (SCREEN_RECT.width - 200, 10))
        screen.blit(font_sm.render(("A" if joystick else "RETURN" )+":めくる", True, FONT_COLOR), (SCREEN_RECT.width - 200, 30))
        
        for i in range(life):
            screen.blit(life_img, (10 + 45*i, 10))
        for trush in trush_list:
            trush.draw(screen)
        # ポインターの位置
        if pointing_idx is not None:
            trush_list[pointing_idx].draw_pointing(screen)
        
        pygame.display.update()
        # 判定
        if len(checking_list) == 2:
            if checking_list[0].trushtype == checking_list[1].trushtype:
                print("kjhkjh")
                hit_sound.play()
                # そろった画面
                await sleep(TICK/2) #画面一時停止
                await sleep_with_info(TICK*2, checking_list)
            else:
                beep_sound.play()
                life -= 1
                if checking_list[1].trushtype == TYPE_JOKER:
                    print("kjhkjh")
                    # 注意がめん
                    await sleep(TICK/2) #画面一時停止
                    await sleep_with_info(TICK*2.5, checking_list[1:])
                else:
                    print("kjhkjh")
                    await sleep(TICK) #画面一時停止
                checking_list[0].is_open = False
                checking_list[1].is_open = False
            checking_list = []
        
        elif len(checking_list) == 1 and checking_list[0].trushtype == TYPE_JOKER:
            beep_sound.play()
            life -= 1
            # 注意がめん
            await sleep(TICK/2.5) #画面一時停止
            await sleep_with_info(TICK*2, checking_list)
            
            checking_list[0].is_open = False
            checking_list = []
        
            
        # 終了判定
        if life < 1:
            return trush_list
        elif len(checking_list) == 0 and complete(trush_list):
            await sleep(TICK) #画面一時停止
            return trush_list
        # フレームレート
        clock.tick(TICK)
        await asyncio.sleep(0) 
#
# 画面一時停止。強制終了以外のコマンドを受け付けない
#
async def sleep(ticks):
    while ticks > 0:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(TICK)
        await asyncio.sleep(0)
        ticks -= 1

#
# 情報を出して画面一時停止。強制終了以外のコマンドを受け付けない
#
async def sleep_with_info(ticks, trush_list = []):
    sheet = pygame.surface.Surface(SCREEN_RECT.size)
    sheet.fill((100,100,100))
    sheet.set_alpha(200)#0が透明
    
    info = pygame.surface.Surface(SCREEN_RECT.size, SRCALPHA)
    img_bg = pygame.transform.scale_by(pygame.image.load(IMG_PATH_BG_FUKIDASI), 1.6)
    info.blit(img_bg, img_bg.get_rect(center = (SCREEN_RECT.width/2,SCREEN_RECT.height/2)))
    if len(trush_list) == 1 and trush_list[0].trushtype == TYPE_JOKER:
        img = pygame.transform.scale_by(trush_list[0].image.copy(), 1.3)
        info.blit(img, img.get_rect(center = (SCREEN_RECT.width/2, 500)))
        
    elif len(trush_list) == 2:
        img = pygame.transform.scale_by(trush_list[0].image.copy(), 1.3)
        info.blit(img, img.get_rect(center = (SCREEN_RECT.width/2 - 140, 500)))
        img = pygame.transform.scale_by(trush_list[1].image.copy(), 1.3)
        info.blit(img, img.get_rect(center = (SCREEN_RECT.width/2 + 140, 500)))
    
    for i,msg in enumerate(desc_trush[trush_list[0].trushtype]):
        info.blit(font_md.render(msg,True,FONT_COLOR), (200,200 + i*30))
        
        
    screen.blit(sheet, (0,0))
    screen.blit(info, (0,0))
    pygame.display.update()
    
    while ticks > 0:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(TICK)
        await asyncio.sleep(0)
        ticks -= 1

def complete(trush_list):
    for trush in trush_list:
        if not trush.is_open and not trush.trushtype == TYPE_JOKER:
            return False
    return True
    
#
# スタート画面
#
async def start_page():
    # タッチスタートの場合、この画面がSKIPされてしまうため
    countup = 0
    
    title_img = pygame.transform.scale_by(pygame.image.load(IMG_PATH_TITLE).convert_alpha(), 0.6)
    # 説明文
    msg = []
    msg.append("[なまごみ] [カン] [プラスチック]")
    msg.append("しゅるいごと の ペア を つくってね。チャンス は ３かい。")
    msg.append("")
    msg.append("ただし、ジョーカー は １ アウト！")

    # 流れる画像
    trush_list = []
    path_list = IMG_PATH_FOODWASTE + IMG_PATH_CANS + IMG_PATH_PLASTICS
    for path in path_list:
        trush_list.append(Trush(path))
    random.shuffle(trush_list)
    for i in range(len(trush_list)):
        trush_list[i].pos = (10 + 230*i, 580)
        trush_list[i].is_open = True

    while True:
        countup += 1
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key in [K_a,K_RETURN]:
                return
            elif event.type == JOYBUTTONDOWN and joystick.get_button(0):
                return
            elif event.type == MOUSEBUTTONDOWN and countup > TICK:
                return
                
        screen.fill(BG_COLOR)
        screen.blit(title_img, title_img.get_rect(center =(SCREEN_RECT.width/2,250)))
        screen.blit(font_sm.render(("A" if joystick else "RETURN" )+":はじめる", True, FONT_COLOR), (SCREEN_RECT.width - 200, 10))
        for idx, m in enumerate(msg):
            screen.blit(font_sm.render(msg[idx], True, FONT_COLOR), (50, 400 + 30*idx))
        for i,trush in enumerate(trush_list):
            trush.pos = (trush.pos[0] -3, trush.pos[1])
            if trush.pos[0] < -300:
                bef = len(trush_list) -1 if i == 0 else i-1
                trush.pos = (trush_list[bef].pos[0] + 230, trush.pos[1])
                    
            trush.draw(screen)
        pygame.display.update()
        clock.tick(TICK)
        await asyncio.sleep(0)        
#
# エンディング画面
#
async def end_page(result_list):
    # ステータス
    foodwaste_disped = False
    cans_disped = False
    plastics_disped = False
    endmsg_disped = False
    
    # サウンド
    clicking_sound = pygame.mixer.Sound(DECISION_SOUND_PATH)
    chaime_sound = pygame.mixer.Sound(CHAIME_SOUND_PATH)

    # 画像
    check_img = pygame.transform.scale(pygame.image.load(IMG_PATH_CHECK_ICON).convert_alpha(), (50,50)) 
    result_img = pygame.transform.scale_by(pygame.image.load(IMG_PATH_RESULT).convert_alpha(), 0.5)

    # 結果の集計
    foodwaste = True
    cans = True
    plastics = True
    for trush in result_list:
        if trush.trushtype == TYPE_FOODWASTE and not trush.is_open:
            foodwaste = False
        elif trush.trushtype == TYPE_CANS and not trush.is_open:
            cans = False
        elif trush.trushtype == TYPE_PLASTICS and not trush.is_open:
            plastics = False

    countup = 0
    while True:
        # カウントアップ
        countup += 1
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key in [K_a,K_RETURN]:
                return
            elif event.type == JOYBUTTONDOWN and joystick.get_button(0):
                return
            elif event.type == MOUSEBUTTONDOWN:
                return

        screen.fill(BG_COLOR)
        screen.blit(font_sm.render(("A" if joystick else "RETURN" )+":おわる", True, FONT_COLOR), (SCREEN_RECT.width - 200, 10))
        if foodwaste:
            result_img.blit(check_img, (80, 120))
        if cans:
            result_img.blit(check_img, (80, 260))
        if plastics:
            result_img.blit(check_img, (80, 400))

        if countup < TICK*1:
            result = result_img.subsurface(Rect(0,0,result_img.get_width(), 100))
        elif countup < TICK*2:
            if not foodwaste_disped:
                clicking_sound.play()
                result = result_img.subsurface(Rect(0,0,result_img.get_width(), 250))
                foodwaste_disped = True
        elif countup < TICK*3:
            if not cans_disped:
                clicking_sound.play()
                result = result_img.subsurface(Rect(0,0,result_img.get_width(), 360))
                cans_disped = True
        elif countup < TICK*4:
            if not plastics_disped:
                clicking_sound.play()
                result = result_img.subsurface(Rect(0,0,result_img.get_width(), 470))
                plastics_disped = True
        else:
            if not endmsg_disped and (foodwaste or cans or plastics) :
                chaime_sound.play()
                result = result_img
                endmsg_disped = True
            
        screen.blit(result, (0, 100))
        pygame.display.update()

        # 10秒で強制終了
        if countup > TICK * 10:
            return
            
        clock.tick(TICK)
        await asyncio.sleep(0)  
        
async def main():
    while True:
        await start_page()
        result = await gamemain()
        await end_page(result)
    clock.tick(TICK)    
    await asyncio.sleep(0)

asyncio.run(main())    

