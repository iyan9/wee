'''
bomb function 完成
'''

import random
from collections import deque

import pygame
from pygame.locals import KEYDOWN, KEYUP, K_SPACE, MOUSEBUTTONDOWN, MOUSEBUTTONUP, QUIT

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
        # 生成棋盤，傳入參數為精靈group
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
        # 獲取x y 節點附近的相同節點座標，如果沒有相同的返回None
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
        # 點擊座標點，如果有消除動作，則返回True，如果沒有消除動作返回False
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

        # 搜索相鄰的節點，返回set
        to_del_set = self.search(x, y)
        if not to_del_set:
            return False

        # 更新分數
        self.scores += pow(len(to_del_set), 2) * 5

        self.deleteCnt = len(to_del_set)

        # 刪除節點
        for point in to_del_set:
            self.group.remove(self.chess[point[0]][point[1]])
            #  處理在這個節點上部的移動標記
            for y_num in range(point[1], len(self.chess[point[0]])):
                self.chess[point[0]][y_num][1].change_y += 1

        to_del = sorted(to_del_set, key=lambda x: x[1], reverse=True)
        for point in to_del:
            del self.chess[point[0]][point[1]]

        # 刪除空列
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
        self.deleteCnt = 0
        group.empty()  # 先把整個group資料清空
        i = len(self.chess) + 1  # 有幾直列
        j = [0] * i
        for x in range(1, i):
            j[x] = len(self.chess[x-1])  # 對於每一直列，紀錄它們分別有幾個方塊
        self.chess.clear()
        for x in range(1, i):
            x_line = []
            for y in range(j[x]):
                # 窮舉每個方塊
                pos = (40 * x, 40 * (10 - y))
                color = random.randint(1, 5)  # 隨機一個顏色
                newBox = Box(Color[color], pos)  # 將隨機的顏色填入新方塊
                group.add(newBox)  # 將新方塊填入group
                x_line.append((color, newBox))
            self.chess.append(x_line)  # 將新方塊填入棋盤
        # self.scores += 500
        return True
        
    def bomb_function(self, bombx, bomby):
        bx = bombx // 40 - 1  # x -1
        by = 9 - (bomby // 40) + 1  # y+1


        # 判斷點擊座標是否有在棋盤格內，如果沒有則回傳False
        if bx < 0 or bx > 9:
            return False
        elif bx < 0 or by > 9:
            return False

        # 判断bx by是否在chess中
        if len(self.chess) <= bx:
            return False
        if len(self.chess[bx]) <= by:
            return False

        # 搜索相鄰的節點
        out = []
        deq = deque()
        deq.append((bx, by))
        now = deq.popleft()

        neighboring = []
        neighboring.append((bx, by))
        neighboring.append([now[0], now[1] + 1]) #上
        neighboring.append([now[0] + 1, now[1] + 1]) #右上
        neighboring.append([now[0] + 1, now[1]]) #右
        neighboring.append([now[0] - 1, now[1]]) #左
        neighboring.append([now[0] - 1, now[1] - 1]) #左下
        neighboring.append([now[0] + 1, now[1] - 1]) #右下
        neighboring.append([now[0], now[1] - 1]) #下
        neighboring.append([now[0] - 1, now[1] + 1]) #左上

        chess_len = len(self.chess)
        to_bomb = []

        for to_del in neighboring:
            if 0 <= to_del[0] <= len(self.chess) - 1:
                if 0 <= to_del[1] <= len(self.chess[to_del[0]]) - 1:
                    to_bomb.append(to_del)
        
        # 刪除節點
        for to_del in to_bomb:
            self.group.remove(self.chess[to_del[0]][to_del[1]])
            #  處理在這個節點上部的移動標記
            for y_num in range(to_del[1], len(self.chess[to_del[0]])):
                self.chess[to_del[0]][y_num][1].change_y += 1

        to_bomb = sorted(to_bomb, key=lambda x: x[1], reverse=True)
        for point in to_bomb:
            del self.chess[point[0]][point[1]]

        # 刪除空列
        for index, _ in enumerate(self.chess):
            if not self.chess[index]:
                # 將右側所有節點向左移動一格
                for x_line in range(index + 1, len(self.chess)):
                    for y_line in range(0, len(self.chess[x_line])):
                        self.chess[x_line][y_line][1].change_x += 1
        for index in range(len(self.chess) - 1, -1, -1):
            if not self.chess[index]:
                del self.chess[index]
        self.scores += 500
        return True

    def tool_3(self):
        self.deleteCnt = 0
        changed_set = set()
        color = random.randint(1, 5)
        for x in range(len(self.chess)):
            for y in range(len(self.chess[x])):
                if self.chess[x][y][0] == color:
                    changed_set.add((x, y))

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
        # self.scores += 500
        return True


class Button:
    def __init__(self, image, posX, posY, width, height):
        self.icon = pygame.image.load(image)
        # pygame.transform.scale(self.icon, (width, height))
        self.icon_rect = self.icon.get_rect()
        self.posX = posX
        self.posY = posY
        self.width = width
        self.height = height
        self.mouse_on_button = 'No'

    def display(self):
        screen.blit(self.icon, (self.posX, self.posY))
        pygame.display.update()
        return True

    def disappear(self):
        pygame.time.wait(100)
        self.icon = pygame.Surface([self.width, self.height])
        self.icon.fill([0, 0, 0])
        screen.blit(self.icon, (self.posX, self.posY))
        return True

    def mouse_down(self, color = (0, 0, 0)):
        if (self.posX < pygame.mouse.get_pos()[0] < self.posX + self.width and
            self.posY  < pygame.mouse.get_pos()[1] < self.posY + self.height):
            pygame.draw.rect(screen, color, [self.posX, self.posY, self.width, self.height], 0)
            pygame.display.update()
            self.posY += 5
            self.display()
            self.mouse_on_button = 'Yes'
            return True
        else:
            return False

    def mouse_up(self, color = (0, 0, 0)):
        if self.mouse_on_button == 'Yes':
            pygame.draw.rect(screen, color, [self.posX, self.posY, self.width, self.height], 0)
            pygame.display.update()

            self.posY -= 5
            self.display()
            self.mouse_on_button = 'No'
            return True
        else:
            return False

    def get_mouse_on_button(self):
        return self.mouse_on_button


pygame.init()
screen = pygame.display.set_mode([480, 520])  # 開新視窗
bg = pygame.Surface([480, 520])  # 建立畫布
bg.fill([0, 0, 0])  # 填滿黑色
level = 1
score = 0
group = pygame.sprite.Group()  # 建立一組動畫
xiaoxiaole = Xiaoxiaole(group, score)  # 消消樂遊戲放入動畫組
clock = pygame.time.Clock()  # 設定遊戲時間
pygame.event.set_allowed([QUIT, MOUSEBUTTONUP, MOUSEBUTTONDOWN, KEYDOWN])  # 設定哪些按鍵可以操作遊戲(結束, 滑鼠按鍵鬆開)

'''設定開始介面的標題'''
pygame.draw.rect(screen, (63, 63, 63), [0, 0, 480, 520], 0)
image = pygame.image.load('C:\\Users\\Matty\\Desktop\\消消樂.png')
image.convert()
screen.blit(image, (40,50))
# my_font = pygame.font.SysFont("simsunnsimsun", 60)  # 字體名稱, 字體大小
# title = '新年快樂消消樂'
# out = my_font.render(title, True, (255, 255, 255))  # 一些字體設定
# screen.blit(out, (25, 170))  # 顯示這行字

'''顯示最高紀錄'''
address = 'C:\\Users\\Matty\\Desktop\\record.txt'
record = open(address, 'r', encoding='utf-8')
bestScore = record.read()  # 從txt檔讀取最高紀錄
my_font2 = pygame.font.SysFont("sitkasmallsitkatextsitkasubheadingsitkaheadingsitkadisplaysitkabanner", 25)
outline2 = 'Best Score : {0}'.format(bestScore)
out2 = my_font2.render(outline2, True, (255, 255, 255))
screen.blit(out2, (110, 480))

play_button = Button('C:\\Users\\Matty\\Desktop\\startButton.png', 145, 290, 200, 188)  # 設定「開始」按鈕的位置跟image
play_button.display()

while True:  # 開始介面的PLAY按鈕
    clock.tick(30)

    event = pygame.event.wait()  # 獲取一個事件
    if event.type == QUIT:
        exit()

    elif event.type == MOUSEBUTTONDOWN:
        '''使用滑鼠時，PLAY按鈕的動畫'''
        play_button.mouse_down((63, 63, 63))
    elif event.type == MOUSEBUTTONUP:
        if play_button.mouse_up((63, 63, 63)):
            pygame.time.wait(150)
            break

pygame.draw.rect(screen, (0, 0, 0), [0, 0, 480, 520], 0)
group.draw(screen)
my_font = pygame.font.SysFont("sitkasmallsitkatextsitkasubheadingsitkaheadingsitkadisplaysitkabanner", 20)  # 字體名稱, 字體大小
# my_font = pygame.font.Font('C:\\Users\\Matty\\Desktop\\Mosk Medium 500.ttf',20)
outline1 = 'Score   : {0}'.format(xiaoxiaole.get_score())
outline2 = 'Level : {0}'.format(xiaoxiaole.get_level())
outline3 = 'Target : {0}'.format(xiaoxiaole.get_target(level))
out1 = my_font.render(outline1, True, (255, 255, 255))  # 一些字體設定
out2 = my_font.render(outline2, True, (255, 255, 255))  # 一些字體設定
out3 = my_font.render(outline3, True, (255, 255, 255))  # 一些字體設定
screen.blit(out1, (120, 470))  # 顯示這行字
screen.blit(out2, (20, 450))  # 顯示這行字
screen.blit(out3, (120, 450))  # 顯示這行字
help_button = Button("C:\\Users\\Matty\\Desktop\\helpIcon.png", 440, 5, 30, 30)
pygame.display.update()  # 顯示最新更新
function = 'none'

while True:
    while True:
        while True:  # 遊戲介面
            clock.tick(30)

            restart_button = Button("C:\\Users\\Matty\\Desktop\\restartButton.png", 190, 260, 100, 100)  # 設定「重新開始」按鈕的位置跟image
            help_button.display()

            event = pygame.event.wait()  # 獲取一個事件
            if event.type == QUIT:
                exit()

            elif event.type == MOUSEBUTTONDOWN:
                delcolor_button = Button("C:\\Users\\Matty\\Desktop\\delcolorIcon.png", 295, 450, 50, 50)  # 設定「消除隨機一色的所有方塊」道具按鈕的位置跟image
                bomb_button = Button("C:\\Users\\Matty\\Desktop\\bombIcon.png", 355, 450, 50, 50)
                switch_button = Button("C:\\Users\\Matty\\Desktop\\switchIcon.png", 400, 450, 50, 50)  # 設定「重新整理」道具按鈕的位置跟image
                if switch_button.mouse_down():
                    continue
                elif delcolor_button.mouse_down():
                    continue
                elif help_button.mouse_down():
                    continue
                elif bomb_button.mouse_down():
                    continue

            elif event.type == MOUSEBUTTONUP:
                if switch_button.get_mouse_on_button() == 'Yes':
                    if switch_button.mouse_up():
                        xiaoxiaole.rearrange()
                        group.update()
                        group.clear(screen, bg)
                        group.draw(screen)
                        switch_button.disappear()
                        pygame.display.update()

                elif delcolor_button.get_mouse_on_button() == 'Yes':
                    if delcolor_button.mouse_up():
                        xiaoxiaole.tool_3()
                        group.update()
                        group.clear(screen, bg)
                        group.draw(screen)
                        delcolor_button.disappear()
                        pygame.display.update()

                elif bomb_button.get_mouse_on_button() == 'Yes':
                    if bomb_button.mouse_up():
                        bomb_button.disappear()
                        pygame.display.update()
                        function = 'bomb'
                        break

                elif help_button.get_mouse_on_button() == 'Yes':
                    if help_button.mouse_up():
                        pygame.display.update()
                        function = 'help'
                        break

                else:
                    xiaoxiaole.client(event.pos)
                    group.update()
                    group.clear(screen, bg)
                    group.draw(screen)
                    pygame.display.update()

                if 9 <= xiaoxiaole.delete_cnt() < 12:
                    switch_button = Button("C:\\Users\\Matty\\Desktop\\switchIcon.png", 400, 450, 50, 50)  # 設定「重新整理」道具按鈕的位置跟image
                    switch_button.display()
                elif 12 <= xiaoxiaole.delete_cnt() < 15:
                    bomb_button = Button("C:\\Users\\Matty\\Desktop\\bombIcon.png", 355, 450, 50, 50)  # 設定「消除隨機一色的所有方塊」道具按鈕的位置跟image
                    bomb_button.display()
                elif 15 <= xiaoxiaole.delete_cnt():
                    delcolor_button = Button("C:\\Users\\Matty\\Desktop\\delcolorIcon.png", 295, 450, 50, 50)  # 設定「消除隨機一色的所有方塊」道具按鈕的位置跟image
                    delcolor_button.display()

                pygame.draw.rect(screen, (0, 0, 0), [0, 440, 280, 80], 0)
                outline1 = 'Score   : {0}'.format(xiaoxiaole.get_score())
                outline2 = 'Level : {0}'.format(xiaoxiaole.get_level())
                outline3 = 'Target : {0}'.format(xiaoxiaole.get_target(level))
                out1 = my_font.render(outline1, True, (255, 255, 255))  # 一些字體設定
                out2 = my_font.render(outline2, True, (255, 255, 255))  # 一些字體設定
                out3 = my_font.render(outline3, True, (255, 255, 255))  # 一些字體設定
                screen.blit(out1, (120, 470))  # 顯示這行字
                screen.blit(out2, (20, 450))  # 顯示這行字
                screen.blit(out3, (120, 450))  # 顯示這行字
                pygame.display.update()

                if not xiaoxiaole.can_continue():
                    xiaoxiaole.get_blocks_left()
                    # pygame.draw.rect(screen, (0, 0, 0), [0, 440, 260, 80], 0)
                    my_font = pygame.font.SysFont("sitkasmallsitkatextsitkasubheadingsitkaheadingsitkadisplaysitkabanner", 20)  # 字體名稱, 字體大小
                    outline4 = 'Blocks left : {0}'.format(xiaoxiaole.get_blocks_left())
                    outline5 = 'Bonus points : +{0}'.format(xiaoxiaole.get_bonus())
                    out4 = my_font.render(outline4, True, (255, 255, 255))  # 一些字體設定
                    out5 = my_font.render(outline5, True, (255, 255, 255))  # 一些字體設定
                    screen.blit(out4, (160, 180))  # 顯示這行字
                    screen.blit(out5, (155, 200))  # 顯示這行字
                    pygame.display.update()
                    pygame.time.wait(2250)
                    pygame.draw.rect(screen, (0, 0, 0), [0, 0, 480, 520], 0)
                    
                    if not xiaoxiaole.next_level(level):
                        '''無法進行下一關時(失敗或已經玩到最後一關)'''
                        thisScore = xiaoxiaole.get_score()  # 取出這次玩的分數
                        address = 'C:\\Users\\Matty\\Desktop\\record.txt'
                        record = open(address, 'r', encoding='utf-8')
                        bestScore = int(record.read())  # 讀取txt檔案中的數字，並記為最高紀錄
                        if thisScore >= bestScore:
                            '''若這次玩的分數大於最高紀錄，覆蓋它'''
                            bestScore = thisScore
                            record = open(address, 'w', encoding='utf-8')
                            record.write(str(bestScore))
                        
                        '''重新讀取txt中的最高紀錄並設定顯示的格式'''
                        address = 'C:\\Users\\Matty\\Desktop\\record.txt'
                        record = open(address, 'r', encoding='utf-8')
                        bestScore = record.read()
                        my_font2 = pygame.font.SysFont("sitkasmallsitkatextsitkasubheadingsitkaheadingsitkadisplaysitkabanner", 30)
                        
                        
                        if level == 7:    # 若7關全過，出現「獲勝」畫面
                            pygame.draw.rect(screen, (0, 0, 0), [0, 440, 480, 80], 0)
                            group.empty()
                            group.clear(screen, bg)
                            group.draw(screen)  # 清空螢幕
                            my_font = pygame.font.SysFont("sitkasmallsitkatextsitkasubheadingsitkaheadingsitkadisplaysitkabanner", 24)  # 字體名稱, 字體大小
                            outline = 'SCORE : {0}'.format(xiaoxiaole.get_score())
                            out = my_font2.render(outline, True, (255, 255, 255))  # 一些字體設定
                            screen.blit(out, (150, 180))  # 顯示這行字
                            outline2 = 'Best Score  : {0}'.format(bestScore)
                            out2 = my_font2.render(outline2, True, (255, 255, 255))
                            screen.blit(out2, (100, 130))
                            restart_button.display()
                            pygame.display.update()
                            function = 'restart'
                            break

                        else:  # 若沒達關卡目標分數，出現「失敗」畫面
                            pygame.draw.rect(screen, (0, 0, 0), [0, 440, 480, 80], 0)
                            group.empty()
                            group.clear(screen, bg)
                            group.draw(screen)  # 清空螢幕
                            my_font = pygame.font.SysFont("sitkasmallsitkatextsitkasubheadingsitkaheadingsitkadisplaysitkabanner", 24)  # 字體名稱, 字體大小
                            outline = 'SCORE : {0}'.format(xiaoxiaole.get_score())
                            out = my_font2.render(outline, True, (255, 255, 255))  # 一些字體設定
                            screen.blit(out, (150, 180))  # 顯示這行字
                            outline2 = 'Best Score  : {0}'.format(bestScore)
                            out2 = my_font2.render(outline2, True, (255, 255, 255))
                            screen.blit(out2, (100, 130))
                            restart_button.display()
                            pygame.display.update()
                            function = 'restart'
                            break

                    else:  # 若達成關卡目標，前進下一關
                        level += 1
                        score = xiaoxiaole.get_score()
                        group = pygame.sprite.Group()  # 建立一組動畫
                        xiaoxiaole = Xiaoxiaole(group, score)  # 消消樂遊戲放入動畫組
                        group.draw(screen)
                        pygame.draw.rect(screen, (0, 0, 0), [0, 440, 480, 80], 0)
                        my_font = pygame.font.SysFont("sitkasmallsitkatextsitkasubheadingsitkaheadingsitkadisplaysitkabanner", 20)  # 字體名稱, 字體大小
                        outline1 = 'Score   : {0}'.format(xiaoxiaole.get_score())
                        outline2 = 'Level : {0}'.format(xiaoxiaole.get_level())
                        outline3 = 'Target : {0}'.format(xiaoxiaole.get_target(level))
                        out1 = my_font.render(outline1, True, (255, 255, 255))  # 一些字體設定
                        out2 = my_font.render(outline2, True, (255, 255, 255))  # 一些字體設定
                        out3 = my_font.render(outline3, True, (255, 255, 255))  # 一些字體設定
                        screen.blit(out1, (120, 470))  # 顯示這行字
                        screen.blit(out2, (20, 450))  # 顯示這行字
                        screen.blit(out3, (120, 450))  # 顯示這行字
                        pygame.display.update()

            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    pygame.draw.rect(screen, (0, 0, 0), [0, 0, 480, 520], 0)  # 填滿黑色
                    level = 1
                    score = 0
                    group = pygame.sprite.Group()  # 建立一組動畫
                    xiaoxiaole = Xiaoxiaole(group, score)  # 消消樂遊戲放入動畫組
                    group.draw(screen)
                    my_font = pygame.font.SysFont("sitkasmallsitkatextsitkasubheadingsitkaheadingsitkadisplaysitkabanner", 20)  # 字體名稱, 字體大小
                    outline1 = 'Score   : {0}'.format(xiaoxiaole.get_score())
                    outline2 = 'Level : {0}'.format(xiaoxiaole.get_level())
                    outline3 = 'Target : {0}'.format(xiaoxiaole.get_target(level))
                    out1 = my_font.render(outline1, True, (255, 255, 255))  # 一些字體設定
                    out2 = my_font.render(outline2, True, (255, 255, 255))  # 一些字體設定
                    out3 = my_font.render(outline3, True, (255, 255, 255))  # 一些字體設定
                    screen.blit(out1, (120, 470))  # 顯示這行字
                    screen.blit(out2, (20, 450))  # 顯示這行字
                    screen.blit(out3, (120, 450))  # 顯示這行字
                    pygame.display.update()  # 顯示最新更新
        while function == 'bomb':  # 放置bomb
            bombevent = pygame.event.poll()
            if bombevent.type == QUIT:
                exit()

            elif bombevent.type == MOUSEBUTTONUP:
                bomblocat = list(bombevent.pos)
                bombx = bomblocat[0]
                bomby = bomblocat[1]
                xiaoxiaole.bomb_function(bombx, bomby)
                pygame.draw.rect(screen, (0, 0, 0), [0, 440, 280, 80], 0)
                outline1 = 'Score   : {0}'.format(xiaoxiaole.get_score())
                outline2 = 'Level : {0}'.format(xiaoxiaole.get_level())
                outline3 = 'Target : {0}'.format(xiaoxiaole.get_target(level))
                out1 = my_font.render(outline1, True, (255, 255, 255))  # 一些字體設定
                out2 = my_font.render(outline2, True, (255, 255, 255))  # 一些字體設定
                out3 = my_font.render(outline3, True, (255, 255, 255))  # 一些字體設定
                screen.blit(out1, (120, 470))  # 顯示這行字
                screen.blit(out2, (20, 450))  # 顯示這行字
                screen.blit(out3, (120, 450))  # 顯示這行字
                group.update()
                group.clear(screen, bg)
                group.draw(screen)
                pygame.display.update()
                function = 'none'
                break
        while function == 'help':  # 遊戲介紹頁面
            clock.tick(30)

            pygame.draw.rect(screen, (0, 0, 0), [0, 0, 480, 520], 0)  # 畫一塊黑色長方形覆蓋掉開始介面

            '''設定字體名稱, 字體大小'''
            # my_font_title = pygame.font.Font('C:\\Users\\Matty\\Desktop\\Mosk Medium 500.ttf',40)
            # my_font = pygame.font.Font('C:\\Users\\Matty\\Desktop\\Mosk Medium 500.ttf',20)
            my_font_title = pygame.font.SysFont("simsunnsimsun", 40)
            my_font = pygame.font.SysFont("simsunnsimsun", 20)
            my_font2 = pygame.font.SysFont("sitkasmallsitkatextsitkasubheadingsitkaheadingsitkadisplaysitkabanner", 20)

            outline1 = '遊戲方法'
            outline2 = '點擊相鄰的同色方塊來消除方塊'
            outline3 = '直到畫面上沒有任何相鄰的同色方塊，則回合結束'
            outline4 = '一次消除的方塊數量越多，獲得的分數會越高'
            outline5 = '在回合結束時，會計算畫面上剩下的方塊數量'
            outline6 = '剩下越少方塊，則可以加的分數越多，max 1000分'
            outline14 = '當分數達到target score，則可以進入下一關'
            

            outline7 = '遊戲道具'
            outline8 = '重新整理：一次消除9塊可以獲得'
            outline9 = '          讓畫面上的所有方塊顏色隨機變化'
            outline10 = '九宮炸彈：一次消除12塊可以獲得'
            outline11 = '          消除畫面上任一九宮格內的方塊'
            outline12 = '同色消除：一次消除15塊可以獲得'
            outline13 = '          隨機將畫面上任一色的所有方塊全消除'

            outline15 = '         Click or SPACE to continue'
            

            '''一些字體設定'''
            out1 = my_font_title.render(outline1, True, (255, 255, 255))
            out2 = my_font.render(outline2, True, (255, 255, 255))
            out3 = my_font.render(outline3, True, (255, 255, 255))
            out4 = my_font.render(outline4, True, (255, 255, 255))
            out5 = my_font.render(outline5, True, (255, 255, 255))
            out6 = my_font.render(outline6, True, (255, 255, 255))
            out14 = my_font.render(outline14, True, (255, 255, 255))

            out7 = my_font_title.render(outline7, True, (255, 255, 255))
            out8 = my_font.render(outline8, True, (255, 255, 255))
            out9 = my_font.render(outline9, True, (255, 255, 255))
            out10 = my_font.render(outline10, True, (255, 255, 255))
            out11 = my_font.render(outline11, True, (255, 255, 255))
            out12 = my_font.render(outline12, True, (255, 255, 255))
            out13 = my_font.render(outline13, True, (255, 255, 255))

            out15 = my_font2.render(outline15, True, (150, 150, 150))

            '''把文字顯示在面上'''
            screen.blit(out1, (20, 30))
            screen.blit(out2, (20, 75))
            screen.blit(out3, (20, 100))
            screen.blit(out4, (20, 125))
            screen.blit(out5, (20, 150))
            screen.blit(out6, (20, 175))
            screen.blit(out14, (20, 200))

            screen.blit(out7, (20, 255))
            screen.blit(out8, (20, 300))
            screen.blit(out9, (20, 325))
            screen.blit(out10, (20, 355))
            screen.blit(out11, (20, 380))
            screen.blit(out12, (20, 410))
            screen.blit(out13, (20, 435))

            screen.blit(out15, (20, 490))

            pygame.display.update()  # 顯示最新更新

            event = pygame.event.wait()  # 獲取一個事件
            if event.type == QUIT:
                exit()
            elif event.type == MOUSEBUTTONUP:
                pygame.draw.rect(screen, (0, 0, 0), [0, 0, 480, 520], 0)
                group.draw(screen)
                my_font = pygame.font.SysFont("sitkasmallsitkatextsitkasubheadingsitkaheadingsitkadisplaysitkabanner", 20)  # 字體名稱, 字體大小
                outline1 = 'Score   : {0}'.format(xiaoxiaole.get_score())
                outline2 = 'Level : {0}'.format(xiaoxiaole.get_level())
                outline3 = 'Target : {0}'.format(xiaoxiaole.get_target(level))
                out1 = my_font.render(outline1, True, (255, 255, 255))  # 一些字體設定
                out2 = my_font.render(outline2, True, (255, 255, 255))  # 一些字體設定
                out3 = my_font.render(outline3, True, (255, 255, 255))  # 一些字體設定
                screen.blit(out1, (120, 470))  # 顯示這行字
                screen.blit(out2, (20, 450))  # 顯示這行字
                screen.blit(out3, (120, 450))  # 顯示這行字
                pygame.display.update()  # 顯示最新更新
                function = 'none'
                break
            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    pygame.draw.rect(screen, (0, 0, 0), [0, 0, 480, 520], 0)
                    group.draw(screen)
                    my_font = pygame.font.SysFont("sitkasmallsitkatextsitkasubheadingsitkaheadingsitkadisplaysitkabanner", 20)  # 字體名稱, 字體大小
                    outline1 = 'Score   : {0}'.format(xiaoxiaole.get_score())
                    outline2 = 'Level : {0}'.format(xiaoxiaole.get_level())
                    outline3 = 'Target : {0}'.format(xiaoxiaole.get_target(level))
                    out1 = my_font.render(outline1, True, (255, 255, 255))  # 一些字體設定
                    out2 = my_font.render(outline2, True, (255, 255, 255))  # 一些字體設定
                    out3 = my_font.render(outline3, True, (255, 255, 255))  # 一些字體設定
                    screen.blit(out1, (120, 470))  # 顯示這行字
                    screen.blit(out2, (20, 450))  # 顯示這行字
                    screen.blit(out3, (120, 450))  # 顯示這行字
                    pygame.display.update()  # 顯示最新更新
                    function = 'none'
                    break
        if function == 'restart':
            function = 'none'
            break
    while True:  # restart介面
        clock.tick(30)

        event = pygame.event.wait()  # 獲取一個事件
        if event.type == QUIT:
            exit()

        elif event.type == MOUSEBUTTONDOWN:
            '''使用滑鼠時，restart按鈕的動畫'''
            restart_button.mouse_down()
        elif event.type == MOUSEBUTTONUP:
            if restart_button.mouse_up():
                pygame.time.wait(150)
                pygame.draw.rect(screen, (0, 0, 0), [0, 0, 480, 520], 0)
                level = 1
                score = 0
                group = pygame.sprite.Group()  # 建立一組動畫
                xiaoxiaole = Xiaoxiaole(group, score)  # 消消樂遊戲放入動畫組
                group.draw(screen)
                my_font = pygame.font.SysFont("sitkasmallsitkatextsitkasubheadingsitkaheadingsitkadisplaysitkabanner", 20)  # 字體名稱, 字體大小
                outline1 = 'Score   : {0}'.format(xiaoxiaole.get_score())
                outline2 = 'Level : {0}'.format(xiaoxiaole.get_level())
                outline3 = 'Target : {0}'.format(xiaoxiaole.get_target(level))
                out1 = my_font.render(outline1, True, (255, 255, 255))  # 一些字體設定
                out2 = my_font.render(outline2, True, (255, 255, 255))  # 一些字體設定
                out3 = my_font.render(outline3, True, (255, 255, 255))  # 一些字體設定
                screen.blit(out1, (120, 470))  # 顯示這行字
                screen.blit(out2, (20, 450))  # 顯示這行字
                screen.blit(out3, (120, 450))  # 顯示這行字
                pygame.display.update()  # 顯示最新更新
                break

        elif event.type == KEYUP:
            if event.key == K_SPACE:
                pygame.draw.rect(screen, (0, 0, 0), [0, 0, 480, 520], 0)  # 填滿黑色
                level = 1
                score = 0
                group = pygame.sprite.Group()  # 建立一組動畫
                xiaoxiaole = Xiaoxiaole(group, score)  # 消消樂遊戲放入動畫組
                group.draw(screen)
                my_font = pygame.font.SysFont("sitkasmallsitkatextsitkasubheadingsitkaheadingsitkadisplaysitkabanner", 20)  # 字體名稱, 字體大小
                outline1 = 'Score   : {0}'.format(xiaoxiaole.get_score())
                outline2 = 'Level : {0}'.format(xiaoxiaole.get_level())
                outline3 = 'Target : {0}'.format(xiaoxiaole.get_target(level))
                out1 = my_font.render(outline1, True, (255, 255, 255))  # 一些字體設定
                out2 = my_font.render(outline2, True, (255, 255, 255))  # 一些字體設定
                out3 = my_font.render(outline3, True, (255, 255, 255))  # 一些字體設定
                screen.blit(out1, (120, 470))  # 顯示這行字
                screen.blit(out2, (20, 450))  # 顯示這行字
                screen.blit(out3, (120, 450))  # 顯示這行字
                pygame.display.update()  # 顯示最新更新
                break
