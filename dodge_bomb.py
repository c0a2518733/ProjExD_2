import math
import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
BB_MAX = 5
SB_NUM = 8
SB_SPEED = 5
SB_LIFE = 150
KK_SPEED = 10
v = KK_SPEED
os.chdir(os.path.dirname(os.path.abspath(__file__)))


DELTA = {  # 押下キーと移動量
    pg.K_UP: (0, -v),
    pg.K_DOWN: (0, +v),
    pg.K_LEFT: (-v, 0),
    pg.K_RIGHT: (+v, 0)
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


def init_bb_imgs() -> tuple[list[pg.Surface], list[float]]:
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
    bb_accs = [1 + a / 5 for a in range(1, 11)]
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
        (+v, 0): pg.transform.rotozoom(kk_img, 0, 0.9),
        (+v, -v): pg.transform.rotozoom(kk_img, 45, 0.9),
        (0, -v): pg.transform.rotozoom(kk_img, 90, 0.9),
        (-v, -v): pg.transform.rotozoom(kk_imgs, -45, 0.9),
        (-v, 0): pg.transform.rotozoom(kk_imgs, 0, 0.9),
        (-v, +v): pg.transform.rotozoom(kk_imgs, 45, 0.9),
        (0, +v): pg.transform.rotozoom(kk_img, -90, 0.9),
        (+v, +v): pg.transform.rotozoom(kk_img, -45, 0.9),
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


def check_collider(kk_rct: pg.Rect, bb_rct: pg.Rect) -> bool:
    """
    こうかとんと爆弾の当たり判定を円形にする
    引数1 kk_rct：こうかとんRect
    引数2 bb_rct：爆弾Rect（大きい爆弾・小型爆弾のどちらでもよい）
    戻り値：当たっていればTrue，当たっていなければFalse
    """
    kk_r = min(kk_rct.width, kk_rct.height) / 2
    bb_r = bb_rct.width / 2
    dist = math.hypot(kk_rct.centerx - bb_rct.centerx,
                      kk_rct.centery - bb_rct.centery)
    return dist < kk_r + bb_r


def create_bomb(kk_rct: pg.Rect, size: int) -> dict:
    """
    追加機能5：こうかとんから300px以上離れた場所に，新しい爆弾を作る
    引数1 kk_rct：こうかとんRect
    引数2 size：爆弾の直径（今の段階の大きさ）
    戻り値：爆弾の辞書（rct：Rect，vx・vy：速度，touching：壁に触れているか）
    """
    while True:
        rct = pg.Rect(random.randint(0, WIDTH - size),
                      random.randint(0, HEIGHT - size), size, size)
        dist = math.hypot(rct.centerx - kk_rct.centerx,
                          rct.centery - kk_rct.centery)
        if dist >= 300:
            return {"rct": rct, "vx": +5, "vy": +5, "touching": False}


def fire_small_bombs(center: tuple[int, int]) -> list[dict]:
    """
    追加機能6：centerからSB_NUM方向へ放射状に小型爆弾を発射する
    引数：発射する中心座標（大きい爆弾の中心）
    戻り値：小型爆弾の辞書のリスト
    （rct：Rect，vx・vy：速度，bounced：跳ね返ったか，timer：跳ね返ってからのフレーム数）
    """
    small = []
    for i in range(SB_NUM):
        angle = math.radians(360 / SB_NUM * i)
        rct = pg.Rect(0, 0, 10, 10)
        rct.center = center
        rct.clamp_ip(pg.Rect(0, 0, WIDTH, HEIGHT))
        small.append({"rct": rct,
                  "vx": SB_SPEED * math.cos(angle),
                  "vy": SB_SPEED * math.sin(angle),
                  "bounced": False, "timer": 0})
    return small


def update_small_bombs(small: list[dict]) -> list[dict]:
    """
    追加機能7：小型爆弾を動かし，1回だけ跳ね返らせ，跳ね返ってから3秒で消す
    引数：小型爆弾のリスト
    戻り値：まだ残っている小型爆弾のリスト
    """
    for s in small:
        s["rct"].move_ip(s["vx"], s["vy"])
        if not s["bounced"]:
            yoko, tate = check_bound(s["rct"])
            if not yoko:
                s["vx"] *= -1
            if not tate:
                s["vy"] *= -1
            if not (yoko and tate):
                s["bounced"] = True
        else:
            s["timer"] += 1
    scr_rct = pg.Rect(0, 0, WIDTH, HEIGHT)
    return [s for s in small
            if s["timer"] < SB_LIFE and scr_rct.colliderect(s["rct"])]


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")

    kk_imgs = get_kk_imgs()  # 向きごとの画像辞書
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_imgs, bb_accs = init_bb_imgs()  # 爆弾と加速度のリスト
    bombs = [create_bomb(kk_rct, bb_imgs[0].get_width())]
    bounce_cnt = 0
    sb_img = pg.Surface((10, 10))
    pg.draw.circle(sb_img, (255, 128, 0), (5, 5), 5)
    sb_img.set_colorkey((0, 0, 0))

    small = []
    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        for b in bombs + small:
            if check_collider(kk_rct, b["rct"]):  # 当たり判定円形
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
        stage = min(tmr//500, 9)  # 10秒ごとに一段階アップ
        bb_img = bb_imgs[stage]

        for b in bombs:  # 大きい爆弾を1個ずつ動かす
            b["vx"], b["vy"] = calc_orientation(b["rct"], kk_rct,
                                                (b["vx"], b["vy"]))
            avx, avy = b["vx"] * bb_accs[stage], b["vy"] * bb_accs[stage]
            b["rct"].width = bb_img.get_rect().width
            b["rct"].height = bb_img.get_rect().height
            b["rct"].clamp_ip(screen.get_rect())  # 拡大ではみ出た部分を画面内に戻す
            b["rct"].move_ip(avx, avy)
            yoko, tate = check_bound(b["rct"])

            if not yoko:
                b["vx"] *= -1
            if not tate:
                b["vy"] *= -1

            out = not (yoko and tate)
            if out and not b["touching"]:  # 壁に当たった瞬間だけ1回と数える
                bounce_cnt += 1
            b["touching"] = out
            screen.blit(bb_img, b["rct"])

        if bounce_cnt >= 2:  # 2回反射するごとに爆弾を1個増やす
            bounce_cnt -= 2
            if len(bombs) < BB_MAX:
                bombs.append(create_bomb(kk_rct, bb_img.get_width()))

        if tmr > 0 and tmr % 250 == 0:  # 5秒ごとに小型爆弾を発射
            for b in bombs:
                small += fire_small_bombs(b["rct"].center)
        small = update_small_bombs(small)
        for s in small:
            screen.blit(sb_img, s["rct"])
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
