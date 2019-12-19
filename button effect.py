
switchIcon = pygame.image.load("C:\\2019AutumnPBC\\project\\switchIcon.png")
switchIconrect = switchIcon.get_rect()

# 按鈕放置位置
x = 300
y = 410

# 按鈕大小
IMAGEWIDTH = 50
IMAGEHEIGHT = 50

if xiaoxiaole.delete_cnt() >= 9:
    screen.blit(switchIcon, (x, y))
    pygame.display.update()


while True:
    event = pygame.event.poll()
    if event.type == MOUSEBUTTONDOWN:
        if x - 4 < pygame.mouse.get_pos()[0] < x - 4 + IMAGEWIDTH and x - 4 < pygame.mouse.get_pos()[1] < x - 4 + IMAGEHEIGHT:
            效果