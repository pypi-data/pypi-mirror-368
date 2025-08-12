import numpy as np
from collections import deque


def _curve_print(curve: list):
    if not curve:
        print("[]")
        return

    col_widths = [0] * 8
    for i, point in enumerate(curve):
        col_idx = i % 8
        s = str(point)
        if len(s) > col_widths[col_idx]:
            col_widths[col_idx] = len(s)

    total = len(curve)
    lines = total // 8
    remainder = total % 8

    print("[")
    for i in range(lines):
        start_idx = i * 8
        line_elements = []
        for j in range(8):
            element = curve[start_idx + j]
            s = str(element)
            line_elements.append(s.ljust(col_widths[j]))
        line_str = "    " + ", ".join(line_elements)
        if i < lines - 1 or remainder > 0:
            line_str += ","
        print(line_str)

    if remainder > 0:
        start_idx = lines * 8
        line_elements = []
        for j in range(remainder):
            element = curve[start_idx + j]
            s = str(element)
            line_elements.append(s.ljust(col_widths[j]))
        line_str = "    " + ", ".join(line_elements)
        print(line_str)
    print("]")


def is_perfect_maze(maze):
    """
    判断给定的迷宫是否为完美迷宫

    完美迷宫的定义：
    1. 所有通路(0)都是连通的
    2. 不存在回路（即没有循环路径）

    Args:
        maze: np.ndarray, 方形数组，1代表墙壁，0代表通路

    Returns:
        bool: 如果是完美迷宫返回True，否则返回False
    """
    if not isinstance(maze, np.ndarray) or maze.ndim != 2 or maze.shape[0] != maze.shape[1]:
        raise ValueError("输入必须是方形的numpy数组")

    rows, cols = maze.shape

    # 找到所有通路的位置
    path_cells = np.argwhere(maze == 0)
    if len(path_cells) == 0:
        return False
    num_paths = len(path_cells)

    if num_paths == 1:
        return True
    visited = set()
    edge_count = 0
    start = tuple(path_cells[0])
    queue = deque([start])
    visited.add(start)
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    while queue:
        current = queue.popleft()
        current_row, current_col = current

        for dr, dc in directions:
            neighbor_row = current_row + dr
            neighbor_col = current_col + dc

            if 0 <= neighbor_row < rows and 0 <= neighbor_col < cols:
                neighbor = (neighbor_row, neighbor_col)

                if maze[neighbor_row, neighbor_col] == 0:
                    if current < neighbor:
                        edge_count += 1

                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

    if len(visited) != num_paths:
        return False
    return edge_count == num_paths - 1
