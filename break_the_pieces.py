data = ['\n+-------------------+--+\n|                   |  |\n|                   |  |\n|  +----------------+  |\n|  |                   |\n|  |                   |\n+--+-------------------+',
     ['+-----+\n|     |\n|     |\n+-----+',
      '+------+\n|      |\n|      |\n+------+',
      '+------------+\n|            |\n|            |\n|            |\n+------------+']
     ]


def find_inner_areas(matrix):
    def is_border(x, y):
        return x == 0 or y == 0 or x == len(matrix) - 1 or y == len(matrix[0]) - 1

    def bfs(x, y):
        queue = [(x, y)]
        area = [(x, y)]
        visited.add((x, y))
        touches_border = is_border(x, y)

        while queue:
            cx, cy = queue.pop(0)
            for nx, ny in [(cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)]:
                if 0 <= nx < len(matrix) and 0 <= ny < len(matrix[0]) and (nx, ny) not in visited and matrix[nx][
                    ny] == 0:
                    queue.append((nx, ny))
                    visited.add((nx, ny))
                    area.append((nx, ny))
                    if is_border(nx, ny):
                        touches_border = True

        return area, touches_border

    visited = set()
    inner_areas = []

    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j] == 0 and (i, j) not in visited:
                area, touches_border = bfs(i, j)
                if not touches_border:
                    inner_areas.append(area)

    return inner_areas


def draw_area(area):
    if not area:
        return ""

    min_x = min(x for x, y in area)
    max_x = max(x for x, y in area)
    min_y = min(y for x, y in area)
    max_y = max(y for x, y in area)

    height = max_x - min_x + 1
    width = max_y - min_y + 1

    # Создаем матрицу для отрисовки области
    drawing = [[' ' for _ in range(width + 2)] for _ in range(height + 2)]

    # Заполняем внутреннюю область нулями
    for x, y in area:
        drawing[x - min_x + 1][y - min_y + 1] = '0'

    # Определяем границы
    for x in range(height + 2):
        for y in range(width + 2):
            if drawing[x][y] == ' ':
                if (x > 0 and drawing[x - 1][y] == '0') or (x < height + 1 and drawing[x + 1][y] == '0'):
                    drawing[x][y] = '-'
                elif (y > 0 and drawing[x][y - 1] == '0') or (y < width + 1 and drawing[x][y + 1] == '0'):
                    drawing[x][y] = '|'
                elif ((x > 0 and y > 0 and drawing[x - 1][y - 1] == '0') or
                      (x > 0 and y < width + 1 and drawing[x - 1][y + 1] == '0') or
                      (x < height + 1 and y > 0 and drawing[x + 1][y - 1] == '0') or
                      (x < height + 1 and y < width + 1 and drawing[x + 1][y + 1] == '0')):
                    drawing[x][y] = '?'
    for x in range(height):
        for y in range(width):
            if drawing[x + 1][y + 1] == '-' or drawing[x + 1][y + 1] == '|':
                minuses = 0
                bars = 0
                pluses = 0
                around = [
                    drawing[x][y + 1],
                    drawing[x + 2][y + 1],
                    drawing[x + 1][y],
                    drawing[x + 1][y + 2]
                ]
                diag = [
                    drawing[x][y],
                    drawing[x + 2][y + 2],
                    drawing[x + 2][y],
                    drawing[x][y + 2]
                ]
                zeros = 0
                for d in diag:
                    if d == '0':
                        zeros += 1
                for a in around:
                    if a == '-':
                        minuses += 1
                    elif a == '|':
                        bars += 1
                    elif a == '?':
                        pluses += 1
                    elif a == '0':
                        zeros += 1
                if ((minuses == 1 and bars == 1) or (minuses == 1 and pluses == 1) or (bars == 1 and pluses == 1)) and (
                        zeros >= 4):
                    drawing[x + 1][y + 1] = '+'
                elif (pluses == 2) and (zeros >= 3):
                    drawing[x + 1][y + 1] = '+'

    # Приводим матрицу к строковому виду
    return '\n'.join(''.join(row).replace('0', ' ').replace('?', '+').rstrip(' ') for row in drawing)


def break_pieces(shape):
    shape = shape.strip('\n')
    shape = shape.splitlines()
    height = len(shape)
    width = max(map(len, shape))
    for i in range(len(shape)):
        s = shape[i]
        if len(s) < width:
            shape[i] = s + ' ' * (width - len(s))

    bounds = []
    for i in range(height):
        bounds.append([])
        for j in range(width):
            bounds[i].append(0 if shape[i][j] == ' ' else 1)
    areas = find_inner_areas(bounds)
    res = []
    for area in areas:
        res.append(draw_area(area))
    return res

print('given:')
print(data[0])
print('expected:')
for s in data[1]:
    print(s)
res = break_pieces(data[0])
print('result:')
for s in res:
    print(s)