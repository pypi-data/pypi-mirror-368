from tkinter import Tk

import pygame


def play_music(music_file, is_need_init=False):
    if is_need_init:
        pygame.mixer.init()
        pygame.mixer.music.load(music_file)
    pygame.mixer.music.stop()
    pygame.mixer.music.play()


def stop_music():
    pygame.mixer.music.stop()


def quit_music():
    pygame.mixer.music.stop()
    pygame.mixer.quit()


def play_music_gen_window(music_file, cycle_time_ms=28000,
                          is_need_init=False, is_hide_window=True):
    win = Tk()
    play_music(music_file, is_need_init)
    if is_hide_window and is_need_init:
        win.withdraw()
    win.withdraw()
    win.after(cycle_time_ms, play_music_gen_window, music_file, cycle_time_ms,
              False, is_hide_window)
    return win


def play_music_by_window(win, music_file, cycle_time_ms=290000,
                         is_need_init=False, is_hide_window=True):
    play_music(music_file, is_need_init)
    if is_hide_window and is_need_init:
        win.withdraw()
    ret_id = win.after(cycle_time_ms, play_music_by_window, win, music_file, cycle_time_ms,
                       False, is_hide_window)
    return ret_id


def change_music(win, music_file, cycle_time_ms=290000,
                 is_need_init=False, is_hide_window=True, ret_id=None):
    stop_music()
    if ret_id is not None:
        win.after_cancel(ret_id)

    ret_id = play_music_by_window(win, music_file, cycle_time_ms,
                                  is_need_init, is_hide_window)
    return ret_id

# window = Tk()
# music_file = "/Users/lele/lele/Python_module/tkinter/game_music_start1.mp3"
# play_music_by_window(window, music_file, 118000, True, True)
# window.withdraw()
# window.mainloop()
#
# window = Tk()
# music_file = "/Users/lele/lele/Python_module/tkinter/game_music_mid_forever.mp3"
# play_music_by_window(window, music_file, 62000, True, True)
# window.withdraw()
# window.mainloop()
#
# window = Tk()
# music_file = "/Users/lele/lele/Python_module/tkinter/game_music_last.mp3"
# play_music_by_window(window, music_file, 79000, True, True)
# window.withdraw()
# window.mainloop()
