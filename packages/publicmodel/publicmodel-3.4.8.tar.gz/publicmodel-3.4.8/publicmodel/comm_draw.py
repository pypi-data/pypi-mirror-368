import tkinter as tk

from publicmodel.common import rgb_to_hex


def get_text_center_coords(canvas, text_item):
    bbox = canvas.bbox(text_item)
    if bbox:
        x_center = (bbox[0] + bbox[2]) / 2
        y_center = (bbox[1] + bbox[3]) / 2
        return x_center, y_center
    else:
        return -1, -1


def get_text_center_coords2(canvas, text_item):
    coords = canvas.coords(text_item)
    if not coords or coords == '':
        # print(f'coords = {coords}\nitem = {text_item}\n')
        x_center = (coords[0] + coords[2]) / 2
        y_center = (coords[1] + coords[3]) / 2
        # print(f'x_center = {x_center}\n'
        #       f'y_center = {y_center}')
        return x_center, y_center


def contains_digit(s):
    return any(char.isdigit() for char in s)


def ball_first(canvas, ball_color='green', ball_x1=485, ball_y1=675):
    hex1 = ball_color
    num = contains_digit(hex1)
    if hex1[0] != '#' and num:
        hex1 = hex1.upper()
        hex2 = rgb_to_hex(hex1)
    else:
        hex2 = hex1

    ball_x2 = ball_x1 + 30
    ball_y2 = ball_y1 + 30
    # 画第一个圆形
    return canvas.create_oval(ball_x1, ball_y1, ball_x2, ball_y2, fill=hex2)


def change_ball_color(canvas, ball, color):
    canvas.itemconfig(ball, fill=color)
    canvas.update()


def ball_to(canvas, target_x, target_y, ball_color='green', pixel=0.1,
            sleep_ms=1, ball_x1=485, ball_y1=700, text=False):
    hex1 = ball_color
    num = contains_digit(hex1)
    if hex1[0] != '#' and num:
        hex1 = hex1.upper()
        hex2 = rgb_to_hex(hex1)
    else:
        hex2 = hex1

    ball_x2 = ball_x1 + 30
    ball_y2 = ball_y1 + 30
    # 画撞击的紫球
    purple_ball2 = canvas.create_oval(ball_x1, ball_y1, ball_x2, ball_y2, fill=hex2)

    # 计算紫球的中心坐标
    purple_center_x, purple_center_y = (ball_x1 + ball_x2) / 2, (ball_y1 + ball_y2) / 2

    # 定义移动紫球的函数
    text2 = text

    def move_purple_ball(purple_center_x, purple_center_y, text3=text2):
        # 计算与目标位置的剩余距离
        remaining_distance_x, remaining_distance_y = target_x - purple_center_x, target_y - purple_center_y

        # 使用线性插值算法计算移动步长
        lerp_factor = min(pixel / ((remaining_distance_x ** 2 + remaining_distance_y ** 2) ** 0.5), 1)
        move_dx = lerp_factor * remaining_distance_x
        move_dy = lerp_factor * remaining_distance_y

        # 移动紫球
        canvas.move(purple_ball2, move_dx, move_dy)

        # 更新紫球的中心坐标
        purple_center_x += move_dx
        purple_center_y += move_dy

        # 判断是否到达目标位置
        if lerp_factor == 1:
            canvas.delete(purple_ball2)
            if not text3:
                return
            else:
                canvas.delete(text3)
                # 停止移动
                return

        # 延迟一段时间后再次调用move_purple_ball()函数
        canvas.after(sleep_ms, move_purple_ball, purple_center_x, purple_center_y)

    # 调用move_purple_ball()函数，开始移动紫球
    move_purple_ball(purple_center_x, purple_center_y)


if __name__ == '__main__':
    window = tk.Tk()
    width = 950
    height = 800
    window.geometry(f'{width}x{height}')
    window.resizable(False, False)
    canvas = tk.Canvas(window, width=width, height=height)
    canvas.pack()
    ball_to(canvas, 100, 100, sleep_ms=5, pixel=1, ball_x1=500, ball_y1=715)
    window.mainloop()
