"""Chuyển cây quyết định thành luật IF-THEN, công thức logic mệnh đề và logic vị từ."""
from itertools import product

# Mỗi thuộc tính: nguyên tử mệnh đề, vị từ, và cách đọc tiếng Việt cho từng giá trị.
META = {
    "tu_tich_cuc": {"atom": "TuTichCuc", "pred": "CoTuTichCuc", "co": "chứa từ tích cực", "khong": "không chứa từ tích cực"},
    "tu_tieu_cuc": {"atom": "TuTieuCuc", "pred": "CoTuTieuCuc", "co": "chứa từ tiêu cực", "khong": "không chứa từ tiêu cực"},
    "phu_dinh": {"atom": "PhuDinh", "pred": "CoPhuDinh", "co": "có từ phủ định", "khong": "không có từ phủ định"},
    "nhan_manh": {"atom": "NhanManh", "pred": "CoNhanManh", "co": "có từ nhấn mạnh", "khong": "không có từ nhấn mạnh"},
    "cam_than": {"atom": "CamThan", "pred": "CoCamThan", "co": "có dấu ! hoặc emoji", "khong": "không có dấu ! hoặc emoji"},
}
LENGTH_VI = {"ngan": "ngắn (tối đa 4 từ)", "vua": "vừa (5 đến 8 từ)", "dai": "dài (từ 9 từ trở lên)"}
LABEL_CONST = {"Tích cực": "TichCuc", "Tiêu cực": "TieuCuc", "Trung tính": "TrungTinh"}


def _literal(attr, value):
    """Trả về (nguyên tử, dương/âm) cho một điều kiện attr = value."""
    if attr == "do_dai":
        return f"DoDai_{value}", True
    return META[attr]["atom"], value == "co"


def _prop_lit(attr, value):
    atom, positive = _literal(attr, value)
    return atom if positive else f"¬{atom}"


def _pred_lit(attr, value):
    if attr == "do_dai":
        return f"DoDai(x, {value})"
    pred = META[attr]["pred"]
    return f"{pred}(x)" if value == "co" else f"¬{pred}(x)"


def _vi_lit(attr, value):
    if attr == "do_dai":
        return f"có độ dài {LENGTH_VI[value]}"
    return META[attr][value]


def _neg(lit):
    return lit[1:] if lit.startswith("¬") else f"¬{lit}"


def _join_vi(items):
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " và " + items[-1]


def truth_table(conds, limit=5):
    atoms = []
    for attr, value in conds:
        atom, _ = _literal(attr, value)
        if atom not in atoms:
            atoms.append(atom)
    if not atoms or len(atoms) > limit:
        return None
    wanted = {}
    for attr, value in conds:
        atom, positive = _literal(attr, value)
        wanted[atom] = positive
    rows = []
    for vals in product([True, False], repeat=len(atoms)):
        env = dict(zip(atoms, vals))
        premise = all(env[a] == wanted[a] for a in atoms)
        rows.append({"vals": [int(v) for v in vals], "premise": int(premise), "implies_false": int(not premise)})
    return {"atoms": atoms, "rows": rows}


def build_rule(leaf, path, support):
    label = leaf.label
    const = LABEL_CONST.get(label, label.replace(" ", ""))
    prop = [_prop_lit(a, v) for a, v in path]
    pred = [_pred_lit(a, v) for a, v in path]
    vi = [_vi_lit(a, v) for a, v in path]
    concl_atom = f"CX_{const}"

    if path:
        if_then = "NẾU " + " VÀ ".join(vi) + f" THÌ cảm xúc là {label}"
        premise_prop = " ∧ ".join(prop)
        premise_pred = " ∧ ".join(pred)
        premise_vi = _join_vi(vi)
        forall = f"∀x ({premise_pred} → CamXuc(x, {const}))"
        forall_vi = f"Với mọi câu x: nếu x {premise_vi} thì cảm xúc của x là {label}."
        exists = f"∃x ({premise_pred} ∧ CamXuc(x, {const}))"
        exists_vi = f"Tồn tại ít nhất một câu x trong dữ liệu huấn luyện: x {premise_vi} và cảm xúc của x là {label} (có {support} câu như vậy)."
        propositional = f"({premise_prop}) → {concl_atom}"
        elim = f"¬({premise_prop}) ∨ {concl_atom}"
        demorgan = " ∨ ".join(_neg(p) for p in prop) + f" ∨ {concl_atom}"
    else:
        if_then = f"LUÔN LUÔN cảm xúc là {label}"
        forall = f"∀x CamXuc(x, {const})"
        forall_vi = f"Với mọi câu x: cảm xúc của x là {label}."
        exists = f"∃x CamXuc(x, {const})"
        exists_vi = f"Tồn tại ít nhất một câu x có cảm xúc {label} (có {support} câu)."
        propositional = concl_atom
        elim = demorgan = concl_atom

    return {
        "leaf": leaf.id,
        "label": label,
        "support": support,
        "conditions": [{"attr": a, "value": v} for a, v in path],
        "if_then": if_then,
        "propositional": propositional,
        "implication_elimination": elim,
        "de_morgan": demorgan,
        "forall": forall,
        "forall_vi": forall_vi,
        "exists": exists,
        "exists_vi": exists_vi,
        "truth_table": truth_table(path),
    }
