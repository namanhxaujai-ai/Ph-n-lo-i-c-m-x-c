"""ID3 cài đặt từ đầu: entropy, information gain, xây cây bằng BFS/DFS với danh sách Open/Closed."""
import math
from collections import Counter, deque

EPS = 1e-12


def entropy(labels):
    """H(S) = -sum p_i * log2(p_i)"""
    n = len(labels)
    if n == 0:
        return 0.0
    h = 0.0
    for c in Counter(labels).values():
        p = c / n
        h -= p * math.log2(p)
    return h if h > EPS else 0.0


def partition(rows, attr):
    groups = {}
    for r in rows:
        groups.setdefault(r[attr], []).append(r)
    return dict(sorted(groups.items()))


def gain_detail(rows, attr, target="label"):
    """Gain(S, A) = H(S) - sum |Sv|/|S| * H(Sv), kèm chi tiết từng nhánh để hiển thị phép tính."""
    n = len(rows)
    base = entropy([r[target] for r in rows])
    parts, remainder = [], 0.0
    for value, group in partition(rows, attr).items():
        labels = [r[target] for r in group]
        h = entropy(labels)
        remainder += len(group) / n * h
        parts.append({"value": value, "n": len(group), "entropy": h, "dist": dict(Counter(labels))})
    gain = base - remainder
    return {"attr": attr, "gain": gain if abs(gain) > EPS else 0.0, "remainder": remainder, "parts": parts}


class Node:
    def __init__(self, nid, depth, parent, edge, rows, attrs):
        self.id = nid
        self.depth = depth
        self.parent = parent
        self.edge = edge
        self.rows = rows
        self.attrs = attrs
        self.attr = None
        self.label = None
        self.children = {}
        self.majority = None
        self.entropy = 0.0
        self.dist = {}

    @property
    def is_leaf(self):
        return self.attr is None


def build_tree(rows, attrs, target="label", strategy="bfs"):
    """Xây cây ID3 bằng vòng lặp với danh sách Open (nút chờ chia) và Closed (nút đã chia).

    strategy="bfs": Open là hàng đợi (FIFO), duyệt theo từng tầng.
    strategy="dfs": Open là ngăn xếp (LIFO), đi sâu trước.
    Kết quả cây giống nhau, chỉ khác thứ tự mở rộng nút.
    """
    if strategy not in ("bfs", "dfs"):
        raise ValueError("strategy phải là 'bfs' hoặc 'dfs'")
    if not rows:
        raise ValueError("Cần ít nhất một mẫu dữ liệu")

    counter = 0

    def new_node(depth, parent, edge, node_rows, node_attrs):
        nonlocal counter
        node = Node(f"n{counter}", depth, parent, edge, node_rows, node_attrs)
        counter += 1
        return node

    root = new_node(0, None, None, rows, list(attrs))
    open_list, closed, steps = [root], [], []

    while open_list:
        open_before = [n.id for n in open_list]
        node = open_list.pop(0)

        labels = [r[target] for r in node.rows]
        dist = Counter(labels)
        node.dist = dict(dist)
        node.entropy = entropy(labels)
        node.majority = min(dist.items(), key=lambda kv: (-kv[1], kv[0]))[0]

        gains, best, reason = [], None, None
        if len(dist) == 1:
            reason = "pure"
        elif not node.attrs:
            reason = "no_attrs"
        else:
            gains = [gain_detail(node.rows, a, target) for a in node.attrs]
            best = max(gains, key=lambda g: round(g["gain"], 10))
            if best["gain"] <= EPS:
                reason = "no_gain"

        kids = []
        if reason:
            node.label = node.majority
        else:
            node.attr = best["attr"]
            remaining = [a for a in node.attrs if a != node.attr]
            for value, group in partition(node.rows, node.attr).items():
                child = new_node(node.depth + 1, node, value, group, remaining)
                node.children[value] = child
                kids.append(child)
            open_list = open_list + kids if strategy == "bfs" else kids + open_list

        closed.append(node.id)
        steps.append({
            "step": len(steps) + 1,
            "node": node.id,
            "depth": node.depth,
            "n": len(node.rows),
            "dist": node.dist,
            "entropy": node.entropy,
            "gains": sorted(gains, key=lambda g: -g["gain"]),
            "chosen": node.attr,
            "leaf_label": node.label,
            "reason": reason or "split",
            "path": path_conditions(node),
            "children": [k.id for k in kids],
            "open_before": open_before,
            "open_after": [n.id for n in open_list],
            "closed_after": list(closed),
        })
    return root, steps


def path_conditions(node):
    conds = []
    while node.parent is not None:
        conds.append((node.parent.attr, node.edge))
        node = node.parent
    return list(reversed(conds))


def to_dict(node):
    return {
        "id": node.id,
        "depth": node.depth,
        "edge": node.edge,
        "attr": node.attr,
        "label": node.label,
        "majority": node.majority,
        "n": len(node.rows),
        "dist": node.dist,
        "entropy": node.entropy,
        "children": [to_dict(c) for c in node.children.values()],
    }


def describe(node):
    return {"id": node.id, "depth": node.depth, "attr": node.attr, "label": node.label, "edge": node.edge}


def bfs_order(root):
    queue, out = deque([root]), []
    while queue:
        node = queue.popleft()
        out.append(describe(node))
        queue.extend(node.children.values())
    return out


def dfs_order(root):
    stack, out = [root], []
    while stack:
        node = stack.pop()
        out.append(describe(node))
        stack.extend(reversed(list(node.children.values())))
    return out


def leaves(root):
    out, stack = [], [root]
    while stack:
        node = stack.pop()
        if node.is_leaf:
            out.append(node)
        else:
            stack.extend(reversed(list(node.children.values())))
    return out


def predict(root, example):
    """Đi từ gốc xuống lá. Giá trị chưa gặp khi huấn luyện thì trả về nhãn đa số của nút hiện tại."""
    node, path, fallback = root, [], False
    while not node.is_leaf:
        value = example.get(node.attr)
        child = node.children.get(value)
        if child is None:
            fallback = True
            return node.majority, path, node, fallback
        path.append({"node": node.id, "attr": node.attr, "value": value})
        node = child
    return node.label, path, node, fallback
