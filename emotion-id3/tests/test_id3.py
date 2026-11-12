import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import id3  # noqa: E402
import model  # noqa: E402
from data import DEFAULT_DATA  # noqa: E402
from features import extract  # noqa: E402

# Bộ dữ liệu PlayTennis kinh điển (Quinlan): đáp án nổi tiếng là Gain(Outlook) = 0.246
TENNIS = [
    ("sunny", "hot", "high", "weak", "no"), ("sunny", "hot", "high", "strong", "no"),
    ("overcast", "hot", "high", "weak", "yes"), ("rain", "mild", "high", "weak", "yes"),
    ("rain", "cool", "normal", "weak", "yes"), ("rain", "cool", "normal", "strong", "no"),
    ("overcast", "cool", "normal", "strong", "yes"), ("sunny", "mild", "high", "weak", "no"),
    ("sunny", "cool", "normal", "weak", "yes"), ("rain", "mild", "normal", "weak", "yes"),
    ("sunny", "mild", "normal", "strong", "yes"), ("overcast", "mild", "high", "strong", "yes"),
    ("overcast", "hot", "normal", "weak", "yes"), ("rain", "mild", "high", "strong", "no"),
]
TENNIS_ROWS = [dict(zip(["outlook", "temp", "humidity", "wind", "label"], t)) for t in TENNIS]
TENNIS_ATTRS = ["outlook", "temp", "humidity", "wind"]


def shape(node):
    if node["attr"] is None:
        return node["label"]
    return (node["attr"], tuple((c["edge"], shape(c)) for c in node["children"]))


class EntropyGain(unittest.TestCase):
    def test_entropy_basic(self):
        self.assertEqual(id3.entropy(["a", "a", "a"]), 0.0)
        self.assertAlmostEqual(id3.entropy(["a", "b"]), 1.0)
        self.assertAlmostEqual(id3.entropy(["a", "a", "b", "b", "c", "c"]), 1.58496, places=4)

    def test_play_tennis_values(self):
        self.assertAlmostEqual(id3.entropy([r["label"] for r in TENNIS_ROWS]), 0.940, places=3)
        gains = {a: id3.gain_detail(TENNIS_ROWS, a)["gain"] for a in TENNIS_ATTRS}
        self.assertAlmostEqual(gains["outlook"], 0.247, places=3)
        self.assertAlmostEqual(gains["humidity"], 0.152, places=3)
        self.assertAlmostEqual(gains["wind"], 0.048, places=3)
        self.assertAlmostEqual(gains["temp"], 0.029, places=3)

    def test_play_tennis_root_is_outlook(self):
        root, steps = id3.build_tree(TENNIS_ROWS, TENNIS_ATTRS)
        self.assertEqual(root.attr, "outlook")
        self.assertEqual(steps[0]["chosen"], "outlook")
        self.assertEqual(root.children["overcast"].label, "yes")


class Strategies(unittest.TestCase):
    def test_bfs_dfs_same_tree_different_order(self):
        rows = model.train(DEFAULT_DATA, "bfs")[0]
        r_bfs, s_bfs = id3.build_tree(rows, model.ATTRS, strategy="bfs")
        r_dfs, s_dfs = id3.build_tree(rows, model.ATTRS, strategy="dfs")
        self.assertEqual(shape(id3.to_dict(r_bfs)), shape(id3.to_dict(r_dfs)))
        self.assertEqual(len(s_bfs), len(s_dfs))
        depths_bfs = [s["depth"] for s in s_bfs]
        self.assertEqual(depths_bfs, sorted(depths_bfs))  # BFS mở rộng theo từng tầng

    def test_open_closed_consistent(self):
        _, root, steps = model.train(DEFAULT_DATA, "dfs")
        last = steps[-1]
        self.assertEqual(last["open_after"], [])
        self.assertEqual(len(last["closed_after"]), len(steps))
        self.assertEqual(len(set(last["closed_after"])), len(steps))


class Sentiment(unittest.TestCase):
    def test_features(self):
        f = extract("Tôi không vui!")
        self.assertEqual((f["tu_tich_cuc"], f["phu_dinh"], f["cam_than"]), ("co", "co", "co"))
        self.assertEqual(extract("Hôm nay trời nhiều mây")["tu_tich_cuc"], "khong")

    def test_training_accuracy_and_samples(self):
        rep = model.full_report(DEFAULT_DATA, "bfs")
        self.assertEqual(rep["train_accuracy"], 1.0)
        self.assertGreater(rep["loo"]["accuracy"], 0.85)
        cases = {
            "Hôm nay tôi rất vui": "Tích cực",
            "Tôi không vui": "Tiêu cực",
            "Tôi ghét môn này": "Tiêu cực",
            "Tôi không buồn": "Trung tính",
            "Ngày mai trời mưa": "Trung tính",
        }
        for text, expected in cases.items():
            for strategy in ("bfs", "dfs"):
                out = model.classify(DEFAULT_DATA, text, strategy)
                self.assertEqual(out["label"], expected, f"{text} ({strategy})")

    def test_rules_cover_all_leaves(self):
        rep = model.full_report(DEFAULT_DATA, "bfs")
        self.assertEqual(sum(r["support"] for r in rep["rules"]), len(DEFAULT_DATA))
        for r in rep["rules"]:
            self.assertIn("→", r["propositional"])


if __name__ == "__main__":
    unittest.main()
