'''
1. 開始介面完成了，之後可以再美化

2. 新增了restart鍵
   - 遊戲失敗跟通過都可以restart(或按SPACE鍵)

'''

import random
from collections import deque

import pygame
from pygame.locals import KEYDOWN, K_SPACE, MOUSEBUTTONUP, QUIT

Color = {
    1: (0, 206, 209),
    2: (179, 153, 255),
    3: (255, 128, 191),
    4: (255, 253, 208),
    5: (77, 128, 230)
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
    def __init__(self, group, score):
        # 生成棋盘，傳入參數為精靈group
        self.level = 1
        self.scores = score
        self.blocks_left = 0
        self.bonus = 0
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
        self.blocks_left = 0
        for x, line in enumerate(self.chess):
            for y, _ in enumerate(line):
                self.blocks_left += 1
                if self.search(x, y):
                    return True
        return False
    
    def get_blocks_left(self):
        return self.blocks_left
    
    def get_bonus(self):
        if self.blocks_left < 10:
            self.scores += (10 - self.blocks_left)*100
            self.bonus = (10 - self.blocks_left)*100
        return self.bonus

    def next_level(self, level):
        target = [900, 2100, 3700, 5800, 8500, 11900, 16100]
        if self.scores >= target[level-1]:
            if level == 7:
                return False
            return True
        return False

    def get_score(self):
        return self.scores
    
    def get_target(self, level):
        target = [900, 2100, 3700, 5800, 8500, 11900, 16100]
        return target[level-1]

    def get_level(self):
        if level == 2:
            self.level = 2
        elif level == 3:
            self.level = 3
        elif level == 4:
            self.level = 4
        elif level == 5:
            self.level = 5
        elif level == 6:
            self.level = 6
        elif level == 7:
            self.level = 7
        
        return self.level

    def search(self, x, y):
        # 獲取x y 節點附近的相同節點座標，如果没有相同的返回None
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
        # 點擊座標點，如果有消除動作，則返回True，如果没有消除動作返回False
        x = pos[0] // 40 - 1  # x -1
        y = 9 - (pos[1] // 40) + 1  # y+1

        # 判斷點擊座標是否有在棋盤格內，如果沒有則回傳False
        if x < 0 or x > 9:
            return False
        elif y < 0 or y > 9:
            return False

        # 判断x y是否在chess中
        if len(self.chess) <= x:
            return False
        if len(self.chess[x]) <= y:
            return False

        # 搜索相鄰的節点，返回set
        to_del_set = self.search(x, y)
        if not to_del_set:
            return False

        # 更新分数
        self.scores += pow(len(to_del_set), 2) * 5
        
        self.deleteCnt = len(to_del_set)

        # 删除節點
        for point in to_del_set:
            self.group.remove(self.chess[point[0]][point[1]])
            #  處理在這個節點上部的移動標記
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
                # 将右侧所有节点向左移动一格
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
level = 1
score = 0
group = pygame.sprite.Group()  # 建立一組動畫
xiaoxiaole = Xiaoxiaole(group, score)  # 消消樂遊戲放入動畫組
clock = pygame.time.Clock()  # 設定遊戲時間
pygame.event.set_allowed([QUIT, MOUSEBUTTONUP, KEYDOWN])  # 設定哪些按鍵可以操作遊戲(結束, 滑鼠按鍵鬆開)



while True:
    clock.tick(30)
    
    '''設定「開始」按鈕的位置跟image'''
    startIcon = pygame.image.load("C:\\Users\\Matty\\Desktop\\play.png")
    # startIcon = pygame.transform.scale(startIcon, (180, 60))
    startIconrect = startIcon.get_rect()
    startIconPosX = 145
    startIconPosY = 250
    startIconWidth = 200
    startIconHeight = 188

    my_font = pygame.font.SysFont("simsunnsimsun", 60)  # 字體名稱, 字體大小
    title = '消消樂'
    out = my_font.render(title, True, (255, 255, 255))  # 一些字體設定
    screen.blit(out, (155, 170))  # 顯示這行字   
    screen.blit(startIcon, (startIconPosX, startIconPosY))
    
    pygame.display.update()

    event = pygame.event.wait()  # 獲取一個事件
    if event.type == QUIT:
        exit() 
    elif event.type == MOUSEBUTTONUP:
        if (startIconPosX - 4 < pygame.mouse.get_pos()[0] < startIconPosX - 4 + startIconWidth and
            startIconPosY - 4 < pygame.mouse.get_pos()[1] < startIconPosY - 4 + startIconHeight):
            group.draw(screen)
            my_font = pygame.font.SysFont("simsunnsimsun", 20)  # 字體名稱, 字體大小
            outline1 = 'Score  : {0}'.format(xiaoxiaole.get_score())
            outline2 = 'Level : {0}'.format(xiaoxiaole.get_level())
            outline3 = 'Target : {0}'.format(xiaoxiaole.get_target(level))
            out1 = my_font.render(outline1, True, (255, 255, 255))  # 一些字體設定
            out2 = my_font.render(outline2, True, (255, 255, 255))  # 一些字體設定
            out3 = my_font.render(outline3, True, (255, 255, 255))  # 一些字體設定
            screen.blit(out1, (120, 470))  # 顯示這行字   
            screen.blit(out2, (10, 450))  # 顯示這行字   
            screen.blit(out3, (120, 450))  # 顯示這行字
            pygame.display.update()  # 顯示最新更新
            break

while True:
    while True:
        clock.tick(30)
        
        '''設定「重新開始」按鈕的位置跟image'''
        restartIcon = pygame.image.load("C:\\Users\\Matty\\Desktop\\restart.png")
        # startIcon = pygame.transform.scale(startIcon, (180, 60))
        restartIconrect = restartIcon.get_rect()
        restartIconPosX = 180
        restartIconPosY = 260
        restartIconWidth = 100
        restartIconHeight = 100

        '''設定「重新整理」道具按鈕的位置跟image'''
        switchIcon = pygame.image.load("C:\\Users\\Matty\\Desktop\\商管程式設計\\wee\\switchIcon.png")
        switchIcon = pygame.transform.scale(switchIcon, (50, 50))
        switchIconrect = switchIcon.get_rect()
        switchIconPosX = 400
        switchIconPosY = 450
        switchIconHeight = 50
        switchIconWidth = 50

        '''設定「消除隨機一色的所有方塊」道具按鈕的位置跟image'''
        delcolorIcon = pygame.image.load("C:\\Users\\Matty\\Desktop\\商管程式設計\\wee\\brush.png")
        delcolorIcon = pygame.transform.scale(delcolorIcon, (50, 50))
        delcolorIconrect = delcolorIcon.get_rect()
        delcolorIconPosX = 350
        delcolorIconPosY = 450
        delcolorIconWidth = 50
        delcolorIconHeight = 50

        event = pygame.event.wait()  # 獲取一個事件
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

        # elif event.type == KEYDOWN:
            # if event.key == K_SPACE:
                # pygame.draw.rect(screen, (0, 0, 0), [0, 0, 480, 440], 0)  # 填滿黑色
                # level = 1 
                # score = 0
                # group = pygame.sprite.Group()  # 建立一組動畫
                # xiaoxiaole = Xiaoxiaole(group, score)  # 消消樂遊戲放入動畫組
                # group.draw(screen)
                # my_font = pygame.font.SysFont("simsunnsimsun", 20)  # 字體名稱, 字體大小
                # outline1 = 'Score  : {0}'.format(xiaoxiaole.get_score())
                # outline2 = 'Level : {0}'.format(xiaoxiaole.get_level())
                # outline3 = 'Target : {0}'.format(xiaoxiaole.get_target(level))
                # out1 = my_font.render(outline1, True, (255, 255, 255))  # 一些字體設定
                # out2 = my_font.render(outline2, True, (255, 255, 255))  # 一些字體設定
                # out3 = my_font.render(outline3, True, (255, 255, 255))  # 一些字體設定
                # screen.blit(out1, (120, 470))  # 顯示這行字   
                # screen.blit(out2, (10, 450))  # 顯示這行字   
                # screen.blit(out3, (120, 450))  # 顯示這行字
                # pygame.display.update()  # 顯示最新更新

            if 9 <= xiaoxiaole.delete_cnt() < 12:
                screen.blit(switchIcon, (switchIconPosX, switchIconPosY))
                pygame.display.update()
            elif xiaoxiaole.delete_cnt() >= 15:
                screen.blit(delcolorIcon, (delcolorIconPosX, delcolorIconPosY))
                pygame.display.update()
                
            pygame.draw.rect(screen, (0, 0, 0), [0, 440, 260, 80], 0)
            outline1 = 'Score  : {0}'.format(xiaoxiaole.get_score())
            outline2 = 'Level : {0}'.format(xiaoxiaole.get_level())
            outline3 = 'Target : {0}'.format(xiaoxiaole.get_target(level))
            out1 = my_font.render(outline1, True, (255, 255, 255))  # 一些字體設定
            out2 = my_font.render(outline2, True, (255, 255, 255))  # 一些字體設定
            out3 = my_font.render(outline3, True, (255, 255, 255))  # 一些字體設定
            screen.blit(out1, (120, 470))  # 顯示這行字   
            screen.blit(out2, (10, 450))  # 顯示這行字   
            screen.blit(out3, (120, 450))  # 顯示這行字
            pygame.display.update()
        

            if not xiaoxiaole.can_continue():
                xiaoxiaole.get_blocks_left()
                # pygame.draw.rect(screen, (0, 0, 0), [0, 440, 260, 80], 0)
                my_font = pygame.font.SysFont("simsunnsimsun", 20)  # 字體名稱, 字體大小
                outline4 = 'Blocks left : {0}'.format(xiaoxiaole.get_blocks_left())
                outline5 = 'Bonus points : +{0}'.format(xiaoxiaole.get_bonus())
                out4 = my_font.render(outline4, True, (255, 255, 255))  # 一些字體設定
                out5 = my_font.render(outline5, True, (255, 255, 255))  # 一些字體設定
                screen.blit(out4, (160, 180))  # 顯示這行字
                screen.blit(out5, (155, 200))  # 顯示這行字
                pygame.display.update()
                pygame.time.wait(2500)
                pygame.draw.rect(screen, (0, 0, 0), [0, 0, 480,520], 0)
                if not xiaoxiaole.next_level(level):
                    if level == 7:    # 若7關全過，出現「獲勝」畫面
                        pygame.draw.rect(screen, (0, 0, 0), [0, 440, 480, 80], 0)
                        group.empty()
                        group.clear(screen, bg)
                        group.draw(screen)  # 清空螢幕
                        my_font = pygame.font.SysFont("simsunnsimsun", 24)  # 字體名稱, 字體大小
                        outline = 'SCORE：{0}'.format(xiaoxiaole.get_score())
                        out = my_font.render(outline, True, (255, 255, 255))  # 一些字體設定
                        screen.blit(out, (170, 180))  # 顯示這行字
                        screen.blit(restartIcon, (restartIconPosX, restartIconPosY))
                        pygame.display.update()
                        break

                    else:  # 若沒達關卡目標分數，出現「失敗」畫面
                        pygame.draw.rect(screen, (0, 0, 0), [0, 440, 480, 80], 0)
                        group.empty()
                        group.clear(screen, bg)
                        group.draw(screen)  # 清空螢幕
                        my_font = pygame.font.SysFont("simsunnsimsun", 24)  # 字體名稱, 字體大小
                        outline = 'SCORE：{0}'.format(xiaoxiaole.get_score())
                        out = my_font.render(outline, True, (255, 255, 255))  # 一些字體設定
                        screen.blit(out, (170, 180))  # 顯示這行字
                        screen.blit(restartIcon, (restartIconPosX, restartIconPosY))
                        pygame.display.update()
                        break

                else:  # 若達成關卡目標，前進下一關
                    level += 1
                    score = xiaoxiaole.get_score()
                    group = pygame.sprite.Group()  # 建立一組動畫
                    xiaoxiaole = Xiaoxiaole(group, score)  # 消消樂遊戲放入動畫組
                    group.draw(screen)
                    pygame.draw.rect(screen, (0, 0, 0), [0, 440, 480, 80], 0)
                    my_font = pygame.font.SysFont("simsunnsimsun", 20)  # 字體名稱, 字體大小
                    outline1 = 'Score  : {0}'.format(xiaoxiaole.get_score())
                    outline2 = 'Level : {0}'.format(xiaoxiaole.get_level())
                    outline3 = 'Target : {0}'.format(xiaoxiaole.get_target(level))
                    out1 = my_font.render(outline1, True, (255, 255, 255))  # 一些字體設定
                    out2 = my_font.render(outline2, True, (255, 255, 255))  # 一些字體設定
                    out3 = my_font.render(outline3, True, (255, 255, 255))  # 一些字體設定
                    screen.blit(out1, (120, 470))  # 顯示這行字   
                    screen.blit(out2, (10, 450))  # 顯示這行字   
                    screen.blit(out3, (120, 450))  # 顯示這行字
                    pygame.display.update()

    while True:
        clock.tick(30)
        
        '''設定「重新開始」按鈕的位置跟image'''
        restartIcon = pygame.image.load("C:\\Users\\Matty\\Desktop\\restart.png")
        # startIcon = pygame.transform.scale(startIcon, (180, 60))
        restartIconrect = restartIcon.get_rect()
        restartIconPosX = 180
        restartIconPosY = 260
        restartIconWidth = 100
        restartIconHeight = 100               
        
        event = pygame.event.wait()  # 獲取一個事件
        if event.type == QUIT:
            exit() 
        elif event.type == MOUSEBUTTONUP:     
            if (restartIconPosX - 4 < pygame.mouse.get_pos()[0] < restartIconPosX - 4 + restartIconWidth and
                  restartIconPosY - 4 < pygame.mouse.get_pos()[1] < restartIconPosY - 4 + restartIconHeight):
                pygame.draw.rect(screen, (0, 0, 0), [0, 0, 480, 440], 0)  # 填滿黑色
                level = 1
                score = 0
                group = pygame.sprite.Group()  # 建立一組動畫
                xiaoxiaole = Xiaoxiaole(group, score)  # 消消樂遊戲放入動畫組
                group.draw(screen)
                my_font = pygame.font.SysFont("simsunnsimsun", 20)  # 字體名稱, 字體大小
                outline1 = 'Score  : {0}'.format(xiaoxiaole.get_score())
                outline2 = 'Level : {0}'.format(xiaoxiaole.get_level())
                outline3 = 'Target : {0}'.format(xiaoxiaole.get_target(level))
                out1 = my_font.render(outline1, True, (255, 255, 255))  # 一些字體設定
                out2 = my_font.render(outline2, True, (255, 255, 255))  # 一些字體設定
                out3 = my_font.render(outline3, True, (255, 255, 255))  # 一些字體設定
                screen.blit(out1, (120, 470))  # 顯示這行字   
                screen.blit(out2, (10, 450))  # 顯示這行字   
                screen.blit(out3, (120, 450))  # 顯示這行字
                pygame.display.update()  # 顯示最新更新
                break
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                pygame.draw.rect(screen, (0, 0, 0), [0, 0, 480, 440], 0)  # 填滿黑色
                level = 1 
                score = 0
                group = pygame.sprite.Group()  # 建立一組動畫
                xiaoxiaole = Xiaoxiaole(group, score)  # 消消樂遊戲放入動畫組
                group.draw(screen)
                my_font = pygame.font.SysFont("simsunnsimsun", 20)  # 字體名稱, 字體大小
                outline1 = 'Score  : {0}'.format(xiaoxiaole.get_score())
                outline2 = 'Level : {0}'.format(xiaoxiaole.get_level())
                outline3 = 'Target : {0}'.format(xiaoxiaole.get_target(level))
                out1 = my_font.render(outline1, True, (255, 255, 255))  # 一些字體設定
                out2 = my_font.render(outline2, True, (255, 255, 255))  # 一些字體設定
                out3 = my_font.render(outline3, True, (255, 255, 255))  # 一些字體設定
                screen.blit(out1, (120, 470))  # 顯示這行字   
                screen.blit(out2, (10, 450))  # 顯示這行字   
                screen.blit(out3, (120, 450))  # 顯示這行字
                pygame.display.update()  # 顯示最新更新
                break