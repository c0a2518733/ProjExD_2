import os
import random
import sys
import math
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))


DELTA = {
    pg.K_UP : (0,-5),
    pg.K_DOWN : (0,+5),
    pg.K_LEFT : (-5,0),
    pg.K_RIGHT : (+5,0)
}

def gameover(screen: pg.Surface) -> None:
    """
    演習1：ゲームオーバー画面を5秒間表示する
    半透明の黒い画面に，泣いているこうかとんと「Game Over」を表示する
    引数：screen（画面Surface）
    戻り値：なし
    """
    go_screen = pg.Surface((WIDTH,HEIGHT))
    pg.draw.rect(go_screen,(0,0,0),pg.Rect(0,0,WIDTH,HEIGHT))
    go_screen.set_alpha(200)
    font = pg.font.Font(None,80)
    txt = font.render("Game Over", True, (255,255,255))
    txt_rct = txt.get_rect()
    txt_rct.center = WIDTH // 2, HEIGHT // 2
    go_screen.blit(txt,txt_rct)
    cry_img = pg.transform.rotozoom(pg.image.load("fig/8.png"),0,0.9)
    cry_rct = cry_img.get_rect()
    cry_rct.midright = txt_rct.left - 20, txt_rct.centery
    go_screen.blit(cry_img,cry_rct)
    cry_rct.midleft = txt_rct.right + 20, txt_rct.centery
    go_screen.blit(cry_img,cry_rct)
    screen.blit(go_screen,[0,0])
    pg.display.update()
    time.sleep(5)

def check_bound(obj_rct:pg.Rect) -> tuple[bool,bool]:
    """
    Rectが画面内か画面外かを判定する
    引数：こうかとんRect または 爆弾Rect
    戻り値：タプル（横方向判定結果，縦方向判定結果）
    画面内ならTrue,画面外ならFalse
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20,20))
    pg.draw.circle(bb_img,(255,0,0),(10,10),10)
    bb_img.set_colorkey((0,0,0))
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(10,WIDTH - 10)
    bb_rct.centery = random.randint(10,HEIGHT - 10)
    vx, vy = +5 , +5
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return
        screen.blit(bg_img, [0, 0])

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True,True):
            kk_rct.move_ip(-sum_mv[0],-sum_mv[1])
        screen.blit(kk_img,kk_rct)
        bb_rct.move_ip(vx,vy)
        yoko,tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
        screen.blit(bb_img,bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
