"""Trích thuộc tính rời rạc từ câu tiếng Việt (ID3 chỉ làm việc với thuộc tính rời rạc)."""
import re
import unicodedata

LABELS = ["Tích cực", "Tiêu cực", "Trung tính"]

POSITIVE = [
    "vui", "hạnh phúc", "tuyệt", "tuyệt vời", "yêu", "thích", "tốt", "hay", "đẹp", "tự hào",
    "hào hứng", "thú vị", "hài lòng", "may mắn", "ngon", "xuất sắc", "dễ thương", "ấm áp",
    "cảm ơn", "sung sướng", "thoải mái", "tự tin",
]
NEGATIVE = [
    "buồn", "tệ", "ghét", "chán", "giận", "tức", "thất vọng", "khóc", "sợ", "lo lắng", "mệt",
    "đau", "dở", "kinh khủng", "cô đơn", "khó chịu", "bực", "bực mình", "tồi", "hối hận", "xấu",
    "căng thẳng", "tuyệt vọng",
]
NEGATION = ["không", "chẳng", "chưa", "chả", "hổng", "đừng"]
INTENSIFIER = ["rất", "quá", "cực kỳ", "vô cùng", "siêu", "lắm"]

EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿]")

# Thuộc tính, thứ tự cố định để kết quả ổn định giữa các lần chạy.
ATTRS = ["tu_tich_cuc", "tu_tieu_cuc", "phu_dinh", "nhan_manh", "cam_than", "do_dai"]

ATTR_TITLES = {
    "tu_tich_cuc": "Có từ tích cực",
    "tu_tieu_cuc": "Có từ tiêu cực",
    "phu_dinh": "Có từ phủ định",
    "nhan_manh": "Có từ nhấn mạnh",
    "cam_than": "Có dấu ! hoặc emoji",
    "do_dai": "Độ dài câu",
}


def _normalize(text):
    text = unicodedata.normalize("NFC", text.lower())
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _contains(padded, words):
    return any(f" {w} " in padded for w in words)


def _yn(flag):
    return "co" if flag else "khong"


def extract(text):
    raw = unicodedata.normalize("NFC", text)
    norm = _normalize(raw)
    padded = f" {norm} "
    n_words = len(norm.split())
    if n_words <= 4:
        length = "ngan"
    elif n_words <= 8:
        length = "vua"
    else:
        length = "dai"
    return {
        "tu_tich_cuc": _yn(_contains(padded, POSITIVE)),
        "tu_tieu_cuc": _yn(_contains(padded, NEGATIVE)),
        "phu_dinh": _yn(_contains(padded, NEGATION)),
        "nhan_manh": _yn(_contains(padded, INTENSIFIER)),
        "cam_than": _yn("!" in raw or bool(EMOJI_RE.search(raw))),
        "do_dai": length,
    }


def to_rows(data):
    rows = []
    for item in data:
        row = extract(item["text"])
        row["label"] = item["label"]
        row["text"] = item["text"]
        rows.append(row)
    return rows
