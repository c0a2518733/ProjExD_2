import math
import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))


DELTA = {  # 押下キーと移動量
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0)
}


def gameover(screen: pg.Surface) -> None:
    """
    演習1：ゲームオーバー画面を5秒間表示する
    半透明の黒い画面に，泣いているこうかとんと「Game Over」を表示する
    引数：screen（画面Surface）
    戻り値：なし
    """
    go_screen = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(go_screen, (0, 0, 0), pg.Rect(0, 0, WIDTH, HEIGHT))
    go_screen.set_alpha(200)  # 透明度設定
    font = pg.font.Font(None, 80)  # 白文字Game Overを作成しSurfaceに貼る
    txt = font.render("Game Over", True, (255, 255, 255))
    txt_rct = txt.get_rect()
    txt_rct.center = WIDTH // 2, HEIGHT // 2
    go_screen.blit(txt, txt_rct)
    cry_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    cry_rct = cry_img.get_rect()
    cry_rct.midright = txt_rct.left - 20, txt_rct.centery
    go_screen.blit(cry_img, cry_rct)
    cry_rct.midleft = txt_rct.right + 20, txt_rct.centery
    go_screen.blit(cry_img, cry_rct)
    screen.blit(go_screen, [0, 0])
    pg.display.update()
    time.sleep(5)


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    演習2：大きさの違う爆弾Surfaceのリストと加速度のリストを作る
    戻り値：タプル（爆弾Surfaceのリスト（10段階），加速度のリスト）
    """
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))  # 黒い部分を透明化
        bb_imgs.append(bb_img)
    bb_accs = [a for a in range(1, 11)]
    return bb_imgs, bb_accs


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    演習3：移動量の合計値タプルと，その向きのこうかとん画像の辞書を作る
    戻り値：辞書（キー：移動量の合計値タプル，値：rotozoomしたSurface）
    """
    kk_imgs = pg.image.load("fig/3.png")
    kk_img = pg.transform.flip(kk_imgs, True, False)
    return {  # 方向角度とイラストの方向設定
        (0, 0): pg.transform.rotozoom(kk_imgs, 0, 0.9),
        (+5, 0): pg.transform.rotozoom(kk_img, 0, 0.9),
        (+5, -5): pg.transform.rotozoom(kk_img, 45, 0.9),
        (0, -5): pg.transform.rotozoom(kk_img, 90, 0.9),
        (-5, -5): pg.transform.rotozoom(kk_imgs, -45, 0.9),
        (-5, 0): pg.transform.rotozoom(kk_imgs, 0, 0.9),
        (-5, +5): pg.transform.rotozoom(kk_imgs, 45, 0.9),
        (0, +5): pg.transform.rotozoom(kk_img, -90, 0.9),
        (+5, +5): pg.transform.rotozoom(kk_img, -45, 0.9),
    }


def calc_orientation(org: pg.Rect, dst: pg.Rect,
                     current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    演習4：orgから見てdstがある方向（移動すべき方向）のベクトルを求める
    引数1 org：移動する側のRect（爆弾Rect）
    引数2 dst：目標のRect（こうかとんRect）
    引数3 current_xy：計算前の移動方向ベクトル（vx, vy）
    戻り値：ノルムが√50になるように正規化した方向ベクトル
    ただし，orgとdstの距離が300未満なら，慣性としてcurrent_xyを返す
    """
    x_diff = dst.centerx - org.centerx
    y_diff = dst.centery - org.centery
    norm = math.sqrt(x_diff**2 + y_diff**2)
    if norm < 300:  # 近いときは向きを変えない
        return current_xy
    vx = x_diff / norm * math.sqrt(50)
    vy = y_diff / norm * math.sqrt(50)
    return vx, vy


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    Rectが画面内か画面外かを判定する
    引数：こうかとんRect または 爆弾Rect
    戻り値：タプル（横方向判定結果，縦方向判定結果）
    画面内ならTrue,画面外ならFalse
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False  # 横方向の判定
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False  # 縦方向の判定
    return yoko, tate


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")

    kk_imgs = get_kk_imgs()  # 向きごとの画像辞書
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_imgs, bb_accs = init_bb_imgs()  # 爆弾と加速度のリスト
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(10, WIDTH - 10)
    bb_rct.centery = random.randint(10, HEIGHT - 10)
    vx, vy = +5, +5  # 爆弾のデフォルト速度
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
            if key_lst[key]:  # 縦と横の移動量設定
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        kk_img = kk_imgs[tuple(sum_mv)]  # 移動方向にあった画像の向きにする
        screen.blit(kk_img, kk_rct)
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        stage = min(tmr//500, 9)  # 10秒ごとに一段階アップ
        avx, avy = vx * bb_accs[stage], vy * bb_accs[stage]
        bb_img = bb_imgs[stage]
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height
        bb_rct.clamp_ip(screen.get_rect())  # 拡大ではみ出た部分を画面内に戻す
        bb_rct.move_ip(avx, avy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
