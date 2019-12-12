import datetime

path = input().split('\\')  # 把題目輸入的路徑從\拆開
path = '\\\\'.join(path)  # 再把路徑用\\合成一個字串

f = open(path, 'r', newline='')  # 開啟檔案

lines = []
linecount = 1
for aline in f:
    if linecount == 1:
        linecount += 1
    else:
        linecount += 1
        lines.append(aline.strip().split(','))



n = int(input())  # 篩選的條件數

con = {}  # 篩選項目跟標準的dictionary
for i in range(n):
    condi = input().split(',')
    con[condi[0]] = condi[1:]




count = 0  # 租借量
unrea = 0  # 記是否有標準不合理的情況

if 'D' in con:  # 若要篩日期
    for i in range(len(con['D'])):  #　找出日期的標準中有沒有不是數字的
        if con['D'][i].isnumeric():
            con['D'][i] = int(con['D'][i])
            if con['D'][i] < 1 or con['D'][i] > 31:
                unrea += 1
                print('1 conDi ', con['D'],' i ', i, ' unrea ', unrea)
        else:
            unrea += 1
            print('2 conDi ', con['D'],' i ', i, ' unrea ', unrea)

if 'H' in con:  # 若要篩小時
    for i in range(len(con['H'])):
        if con['H'][i].isnumeric():
            con['H'][i] = int(con['H'][i])
        else:
            unrea += 1
            print('3 conHi ', con['H'],' i ', i, ' unrea ', unrea)
        if con['H'][i] < 0 or con['H'][i] > 23:
            unrea += 1
            print('4 conHi ', con['H'],' i ', i, ' unrea ', unrea)


if 'W' in con:  # 若要篩工作日
    for i in range(len(con['W'])):
        if con['W'][i].isnumeric():
            con['W'][i] = int(con['W'][i])
            if con['W'][i] != 0 and con['W'][i] != 1:
                unrea += 1
                print('5 conWi ', con['W'],' i ', i, ' unrea ', unrea)

if 'K' in con:  # 若要篩星期幾
    for i in range(len(con['K'])):
        if con['K'][i].isnumeric():
            con['K'][i] = int(con['K'][i])
            if con['K'][i] < 1 or con['K'][i] > 7:
                unrea += 1
                print('6 conKi ', con['K'],' i ', i, ' unrea ', unrea)

print('con ', con)
pre = []
for i in range(len(lines)): # range是len(lines)
    if 'D' in con:
        d = lines[i][0].split('/')[2]

        if int(d) in con['D']:  # 這行的日期在篩選標準中
            pre.append(lines[i])  # 就把這行放到pre中等待之後再篩選


    if 'H' in con:
        if int(lines[i][1]) in con['H']:
            pre.append(lines[i])


    if 'W' in con:
        if int(lines[i][3]) in con['W']:
            pre.append(lines[i])

    if 'K' in con:
        date = datetime.datetime.strptime(lines[i][0], '%Y/%m/%d')  # 把日期轉datetime格式
        day = int(date.date().weekday()) + 1  # 判斷星期幾
        if day in con['K']:
            pre.append(lines[i])




i = len(pre) - 1
while i > -1:
    if 'D' in con:
        if int(pre[i][0].split('/')[2]) not in con['D']:
            pre.pop(i)
            i -= 1
            continue

    if 'H' in con:
        if int(pre[i][1]) not in con['H']:
            pre.pop(i)
            i -= 1
            continue

    if 'W' in con:
        if int(pre[i][3]) not in con['W']:
            pre.pop(i)
            i -= 1
            continue


    if 'K' in con:
        date = datetime.datetime.strptime(pre[i][0], '%Y/%m/%d')
        day = int(date.date().weekday()) + 1  # 星期幾
        if day not in con['K']:
            pre.pop(i)
            i -= 1
            continue
    i -= 1





for i in range(len(pre)):
    count += int(pre[i][2])

if unrea != 0:
    print('-1')
else:
    print(count)


print('pre')
print(pre)