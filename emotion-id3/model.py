"""Gắn các phần lại: huấn luyện, dự đoán, đánh giá leave-one-out."""
from collections import Counter

import id3
import logic
from features import ATTRS, ATTR_TITLES, LABELS, extract, to_rows


def clean_data(data):
    if not isinstance(data, list):
        raise ValueError("data phải là danh sách")
    out = []
    for item in data:
        text = str(item.get("text", "")).strip()
        label = item.get("label")
        if not text:
            continue
        if label not in LABELS:
            raise ValueError(f"Nhãn không hợp lệ: {label!r}")
        out.append({"text": text[:300], "label": label})
    if len(out) < 2:
        raise ValueError("Cần ít nhất 2 câu huấn luyện")
    if len(out) > 500:
        raise ValueError("Tối đa 500 câu")
    return out


def train(data, strategy="bfs"):
    data = clean_data(data)
    rows = to_rows(data)
    root, steps = id3.build_tree(rows, ATTRS, strategy=strategy)
    return rows, root, steps


def evaluate_loo(rows, strategy="bfs"):
    """Leave-one-out: bỏ lần lượt từng mẫu, huấn luyện trên phần còn lại, dự đoán mẫu bị bỏ."""
    confusion = {a: {b: 0 for b in LABELS} for a in LABELS}
    correct = 0
    for i, held in enumerate(rows):
        rest = rows[:i] + rows[i + 1:]
        root, _ = id3.build_tree(rest, ATTRS, strategy=strategy)
        pred, _, _, _ = id3.predict(root, held)
        confusion[held["label"]][pred] += 1
        correct += pred == held["label"]
    return {"accuracy": correct / len(rows), "n": len(rows), "confusion": confusion}


def full_report(data, strategy="bfs"):
    rows, root, steps = train(data, strategy)
    train_correct = sum(id3.predict(root, r)[0] == r["label"] for r in rows)
    rules = []
    for leaf in id3.leaves(root):
        support = sum(1 for r in rows if _matches(r, id3.path_conditions(leaf)))
        rules.append(logic.build_rule(leaf, id3.path_conditions(leaf), support))
    return {
        "strategy": strategy,
        "attrs": [{"key": a, "title": ATTR_TITLES[a]} for a in ATTRS],
        "labels": LABELS,
        "rows": [{k: r[k] for k in ["text", "label", *ATTRS]} for r in rows],
        "distribution": dict(Counter(r["label"] for r in rows)),
        "root_entropy": steps[0]["entropy"],
        "steps": steps,
        "tree": id3.to_dict(root),
        "bfs_order": id3.bfs_order(root),
        "dfs_order": id3.dfs_order(root),
        "rules": rules,
        "train_accuracy": train_correct / len(rows),
        "loo": evaluate_loo(rows, strategy),
    }


def _matches(row, conds):
    return all(row[a] == v for a, v in conds)


def classify(data, text, strategy="bfs"):
    rows, root, _ = train(data, strategy)
    features = extract(text)
    label, path, node, fallback = id3.predict(root, features)
    leaf_conds = id3.path_conditions(node)
    support = sum(1 for r in rows if _matches(r, leaf_conds))
    rule = logic.build_rule(node, leaf_conds, support) if node.is_leaf else None
    return {
        "text": text,
        "label": label,
        "features": features,
        "path": path,
        "leaf": node.id,
        "fallback": fallback,
        "rule": rule,
        "dist": node.dist,
    }
