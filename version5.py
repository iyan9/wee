'''
1. 第二個按鈕功能寫完了
   - 點擊後，隨機一個顏色的所有色塊會全部消掉
2. 修改了一些小bug
   - 不會再有色塊吊出螢幕了
   - 還有一些我忘了
'''

import random
from collections import deque

import pygame
from pygame.locals import MOUSEBUTTONUP, QUIT

Color = {  # 消消樂色塊的顏色們
    1: (0, 206, 209),
    2: (179, 153, 255),
    3: (255, 128, 191),
    4: (255, 253, 208),
    5: (77, 128, 230)
}


class Box(pygame.sprite.Sprite):  # 色塊class
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
        # 生成棋盤，傳入參數為精靈group
        self.scores = 0
        self.deleteCnt = 0
        self.chess = []
        self.group = group

        for x in range(1, 11):
            x_line = []
            for y in range(10):
                pos = (40 * x, 40 * (10 - y))
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
        # 獲取x,y節點附近的相同節點座標，如果沒有相同的，就返回None
        point_value = self.chess[x][y][0]
        out = set()
        out.add((x, y))
        deq = deque()
        deq.append((x, y))

        while len(deq):
            # 廣度優先搜索
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
        # 點擊座標點，如果有消除動作，就返回True，如果没有消除動作就返回False
        x = pos[0] // 40 - 1  # x -1
        y = 9 - (pos[1] // 40) + 1  # y+1

        # 判斷點擊座標是否有在棋盤格內，如果沒有則回傳False
        if x < 0 or x > 9:
            return False
        elif y < 0 or y > 9:
            return False

        # 判斷x,y是否在chess中
        if len(self.chess) <= x:
            return False
        if len(self.chess[x]) <= y:
            return False

        # 搜索相鄰的節點，返回set
        to_del_set = self.search(x, y)
        if not to_del_set:
            return False

        # 更新分數
        self.scores += pow(len(to_del_set), 2) * 5
        
        self.deleteCnt = len(to_del_set)

        # 删除節點
        for point in to_del_set:
            self.group.remove(self.chess[point[0]][point[1]])
            # 處理在這個節點上部的移動標記
            for y_num in range(point[1], len(self.chess[point[0]])):
                self.chess[point[0]][y_num][1].change_y += 1

        to_del = sorted(to_del_set, key=lambda x: x[1], reverse=True)
        for point in to_del:
            del self.chess[point[0]][point[1]]

        # 删除空列
        for index, _ in enumerate(self.chess):
            if not self.chess[index]:
                # 將右側所有節點向左移動一格
                for x_line in range(index + 1, len(self.chess)):
                    for y_line in range(0, len(self.chess[x_line])):
                        self.chess[x_line][y_line][1].change_x += 1
        for index in range(len(self.chess) - 1, -1, -1):
            if not self.chess[index]:
                del self.chess[index]
        return True
        
    def rearrange(self):
        group.empty()
        i = len(self.chess)+1
        j = [0] * i
        for x in range(1, i):
            j[x] = len(self.chess[x-1])
        self.chess.clear()
        for x in range(1, i):
            x_line = []
            for y in range(j[x]):
                pos = (40 * x, 40 * (10 - y))
                color = random.randint(1, 5)
                newBox = Box(Color[color], pos)
                group.add(newBox)
                x_line.append((color, newBox))
            self.chess.append(x_line)
        return True


    def tool_3(self):
        changed_set = set()
        color = random.randint(1, 5)
        for x in range(len(self.chess)):
            for y in range (len(self.chess[x])):
                if self.chess[x][y][0] == color:
                    changed_set.add((x,y))

        if len(changed_set) >= 1:
            for changed_point in changed_set:
                self.group.remove(self.chess[changed_point[0]][changed_point[1]])
                for y_num in range(changed_point[1], len(self.chess[changed_point[0]])):
                    self.chess[changed_point[0]][y_num][1].change_y += 1

        to_change = sorted(changed_set, key=lambda x: x[1], reverse=True)
        for changed_point in to_change:
            del self.chess[changed_point[0]][changed_point[1]]

        for index, _ in enumerate(self.chess):
            if not self.chess[index]:
                # 將右側所有節點向左移動一格
                for x_line in range(index + 1, len(self.chess)):
                    for y_line in range(0, len(self.chess[x_line])):
                        self.chess[x_line][y_line][1].change_x += 1

        for index in range(len(self.chess) - 1, -1, -1):
            if not self.chess[index]:
                del self.chess[index]
        return True


pygame.init()
screen = pygame.display.set_mode([480, 520])  # 開新視窗
bg = pygame.Surface([480, 520])  # 建立畫布
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
    
    switchIcon = pygame.image.load("C:\\Users\\chial\\Desktop\\switchIcon.png")
    switchIconrect = switchIcon.get_rect()
    switchIconPosX = 350
    switchIconPosY = 440
    switchIconHeight = 50
    switchIconWidth = 50
    
    delcolorIcon = pygame.image.load("C:\\Users\\chial\\Desktop\\brush.png")
    delcolorIconrect = delcolorIcon.get_rect()
    delcolorIconPosX = 300
    delcolorIconPosY = 440
    delcolorIconWidth = 50
    delcolorIconHeight = 50

    if event.type == QUIT:
        exit()
    elif event.type == MOUSEBUTTONUP:
        if (switchIconPosX - 4 < pygame.mouse.get_pos()[0] < switchIconPosX - 4 + switchIconWidth and
            switchIconPosY - 4 < pygame.mouse.get_pos()[1] < switchIconPosY - 4 + switchIconHeight):
            xiaoxiaole.rearrange()
            switchIcon = pygame.Surface([50, 50])
            switchIcon.fill([0, 0, 0])
            screen.blit(switchIcon, (switchIconPosX, switchIconPosY))
            group.update()
            pygame.display.update()
            group.clear(screen, bg)
            group.draw(screen)
            pygame.display.update()

        elif (delcolorIconPosX - 4 < pygame.mouse.get_pos()[0] < delcolorIconPosX - 4 + delcolorIconWidth and
            delcolorIconPosY - 4 < pygame.mouse.get_pos()[1] < delcolorIconPosY - 4 + delcolorIconHeight):
            xiaoxiaole.tool_3()
            delcolorIcon = pygame.Surface([50, 50])
            delcolorIcon.fill([0, 0, 0])
            screen.blit(delcolorIcon, (delcolorIconPosX, delcolorIconPosY))
            group.update()
            group.clear(screen, bg)
            group.draw(screen)
            pygame.display.update()

        else:
            xiaoxiaole.client(event.pos)
            group.update()
            group.clear(screen, bg)
            group.draw(screen)
            pygame.display.update()

        if 3 <= xiaoxiaole.delete_cnt() < 6:
            screen.blit(switchIcon, (switchIconPosX, switchIconPosY))
            pygame.display.update()
        elif xiaoxiaole.delete_cnt() >= 6:
            screen.blit(delcolorIcon, (delcolorIconPosX, delcolorIconPosY))
            pygame.display.update()
            
        pygame.draw.rect(screen, (0, 0, 0), [0, 440, 200, 80], 0)
        my_font = pygame.font.SysFont("simsunnsimsun", 20)  # 字體名稱, 字體大小
        outline1 = 'score : {0}'.format(xiaoxiaole.get_score())
        out1 = my_font.render(outline1, True, (255, 255, 255))  # 一些字體設定
        screen.blit(out1, (60, 470))  # 顯示這行字   
        pygame.display.update()
    

        
        if not xiaoxiaole.can_continue():
            pygame.draw.rect(screen, (0, 0, 0), [0, 440, 480, 80], 0)
            group.empty()
            group.clear(screen, bg)
            group.draw(screen)  # 清空螢幕
            my_font = pygame.font.SysFont("simsunnsimsun", 24)  # 字體名稱, 字體大小
            outline = 'SCORE：{0}'.format(xiaoxiaole.get_score())
            out = my_font.render(outline, True, (255, 255, 255))  # 一些字體設定
            screen.blit(out, (20, 180))  # 顯示這行字
            pygame.display.update()  # 顯示最新更新