
import random
from collections import deque

import pygame
from pygame.locals import MOUSEBUTTONUP, QUIT

Color = {
    1: (0, 206, 209),    # 湖水綠
    2: (179, 153, 255),  # 紫丁香
    3: (255, 128, 191),  # 淺珊瑚粉
    4: (255, 253, 208),  # 奶油
    5: (77, 128, 230)    # 鼠尾草藍
}


class Box(pygame.sprite.Sprite):
    def __init__(self, color, position):
        super().__init__()
        self.image = pygame.Surface([40, 40])
        self.rect = self.image.fill(color=color)
        self.rect.topleft = position
        self.change_x = 0
        self.change_y = 0

    def update(self):
        if self.change_x:
            self.rect.x -= self.change_x * 40
            self.change_x = 0
        if self.change_y:
            self.rect.y += self.change_y * 40
            self.change_y = 0


class Xiaoxiaole:
    def __init__(self, group):
        # 生成棋盘，传入参数为精灵group
        self.scores = 0
        self.deleteCnt = 0
        self.chess = []
        self.group = group

        for x in range(10):
            x_line = []
            for y in range(10):
                pos = (40 * x, 40 * (9 - y))
                color = random.randint(1, 5)
                box = Box(Color[color], pos)
                group.add(box)
                x_line.append((color, box))
            self.chess.append(x_line)

    def can_continue(self):
        for x, line in enumerate(self.chess):
            for y, _ in enumerate(line):
                if self.search(x, y):
                    return True
        return False

    def get_score(self):
        return self.scores

    def search(self, x, y):
        # 获取x y 节点附近的相同节点坐标，如果没有相同的返回None
        point_value = self.chess[x][y][0]
        out = set()
        out.add((x, y))
        deq = deque()
        deq.append((x, y))

        while len(deq):
            # 广度优先搜索
            now = deq.popleft()
            neighbors = [(now[0] - 1, now[1]), (now[0] + 1, now[1]),
                         (now[0], now[1] - 1), (now[0], now[1] + 1)]
            chess_len = len(self.chess)
            for neighbor in neighbors:
                if neighbor in out:
                    continue
                if neighbor[0] < 0 or neighbor[0] >= chess_len:
                    continue
                if neighbor[1] < 0 or neighbor[1] >= len(self.chess[neighbor[0]]):
                    continue
                if self.chess[neighbor[0]][neighbor[1]][0] == point_value:
                    deq.append(neighbor)
                    out.add(neighbor)
        if len(out) > 1:
            return out
        else:
            return None
    
    def delete_cnt(self):
        return self.deleteCnt
    
    def client(self, pos):
        # 点击坐标点，如果有消除动作，则返回True，如果没有消除动作返回False
        x = pos[0] // 40
        y = 9 - (pos[1] // 40)
        # self.group.remove(self.chess[x][y][1])

        # 判断x y是否在chess中
        if len(self.chess) <= x:
            return False
        if len(self.chess[x]) <= y:
            return False

        # 搜索相邻的节点，返回set
        to_del_set = self.search(x, y)
        if not to_del_set:
            return False

        # 更新分数
        self.scores += pow(len(to_del_set), 2) * 5
        
        self.deleteCnt = len(to_del_set)

        # 删除节点
        for point in to_del_set:
            self.group.remove(self.chess[point[0]][point[1]])
            #  处理在这个节点上部的移动标记
            for y_num in range(point[1], len(self.chess[point[0]])):
                self.chess[point[0]][y_num][1].change_y += 1

        to_del = sorted(to_del_set, key=lambda x: x[1], reverse=True)
        for point in to_del:
            del self.chess[point[0]][point[1]]

        # 删除空列
        for index, _ in enumerate(self.chess):
            if not self.chess[index]:
                # 将右侧所有节点向左移动一格
                for x_line in range(index + 1, len(self.chess)):
                    for y_line in range(0, len(self.chess[x_line])):
                        self.chess[x_line][y_line][1].change_x += 1
        for index in range(len(self.chess) - 1, -1, -1):
            if not self.chess[index]:
                del self.chess[index]
        return True
    
    def rearrange(self):
        for x in range(len(self.chess)):
            x_line = []
            for y in range(len(self.chess[x])):
                pos = (40 * x, 40 * (9 - y))
                color = random.randint(1, 5)
                box = Box(Color[color], pos)
                group.add(box)
                x_line.append((color, box))
            self.chess.append(x_line)
        return True

pygame.init()
screen = pygame.display.set_mode([400, 480])  # 開新視窗
bg = pygame.Surface([400, 480])  # 建立畫布
bg.fill([0, 0, 0])  # 填滿黑色
group = pygame.sprite.Group()  # 建立一組動畫
xiaoxiaole = Xiaoxiaole(group)  # 消消樂遊戲放入動畫組
group.draw(screen)
pygame.display.update()  # 顯示最新更新
clock = pygame.time.Clock()  # 設定遊戲時間
pygame.event.set_allowed([QUIT, MOUSEBUTTONUP])  # 設定哪些按鍵可以操作遊戲(結束, 滑鼠按鍵鬆開)

while True:
    clock.tick(30)
    event = pygame.event.poll()  # 獲取一個事件
    
    switchIcon = pygame.image.load("C:\\2019AutumnPBC\\project\\switchIcon.png")
    switchIconrect = switchIcon.get_rect()
    
    if event.type == QUIT:
        exit()
    elif event.type == MOUSEBUTTONUP:
        pygame.draw.rect(screen, (0, 0, 0), [0, 400, 330, 80], 0)
        xiaoxiaole.client(event.pos)
        group.update()
        group.clear(screen, bg)
        group.draw(screen)
        pygame.display.update()
        
        
        my_font = pygame.font.SysFont("simsunnsimsun", 14)  # 字體名稱, 字體大小
        outline1 = 'score : {0}'.format(xiaoxiaole.get_score())
        outline2 = '消幾塊：{0}'.format(xiaoxiaole.delete_cnt())
        out1 = my_font.render(outline1, True, (255, 255, 255))  # 一些字體設定
        out2 = my_font.render(outline2, True, (255, 255, 255))  # 一些字體設定
        screen.blit(out1, (20, 410))  # 顯示這行字
        screen.blit(out2, (20, 440))
        
        switchIconPosX = 350
        switchIconPosY = 410
        switchIconHeight = 50
        switchIconWidth = 50
        
        if xiaoxiaole.delete_cnt() >= 9:
            screen.blit(switchIcon, (switchIconPosX, switchIconPosY))
            pygame.display.update()
            
        
        if (switchIconPosX - 4 < pygame.mouse.get_pos()[0] < switchIconPosX - 4 + switchIconWidth and
            switchIconPosY - 4 < pygame.mouse.get_pos()[1] < switchIconPosY - 4 + switchIconHeight):
            #pygame.draw.rect(screen, (0, 0, 0), [0, 0, 400, 400], 0)
            #group.clear(screen, bg)
            xiaoxiaole.rearrange()
            #group.update()
            #xiaoxiaole = Xiaoxiaole(group)
            pygame.display.update()
            xiaoxiaole.client(event.pos)
            pygame.draw.rect(screen, (0, 0, 0), [330, 400, 70, 80], 0)
            pygame.display.update()
            
            group.update()
        
        pygame.display.update()
        
        
        
        if not xiaoxiaole.can_continue():
            pygame.draw.rect(screen, (0, 0, 0), [0, 400, 400, 80], 0)
            group.empty()
            group.clear(screen, bg)
            group.draw(screen)  # 清空螢幕
            my_font = pygame.font.SysFont("simsunnsimsun", 24)  # 字體名稱, 字體大小
            outline = 'SCORE：{0}'.format(xiaoxiaole.get_score())
            out = my_font.render(outline, True, (255, 255, 255))  # 一些字體設定
            screen.blit(out, (20, 180))  # 顯示這行字
            pygame.display.update()  # 顯示最新更新