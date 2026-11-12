# Phân loại cảm xúc bằng ID3

Ứng dụng web (Flask + gunicorn) đóng gói bằng Docker. ID3, entropy, information gain, BFS/DFS, Open/Closed và phần suy ra luật logic đều tự cài đặt, không dùng thư viện học máy.

## Chạy bằng Docker

```bash
docker compose up --build
# mở http://localhost:8000
```

Hoặc không dùng compose:

```bash
docker build -t emotion-id3 .
docker run --rm -p 8000:8000 emotion-id3
```

Khi build, Dockerfile chạy bộ kiểm thử; nếu test lỗi thì image không được tạo.

## Chạy không cần Docker

```bash
pip install -r requirements.txt
python app.py            # http://localhost:8000
python -m unittest discover -s tests -v
```

## Cấu trúc

| File | Nội dung |
|---|---|
| `id3.py` | entropy, information gain, xây cây bằng Open/Closed (BFS hoặc DFS), duyệt cây, dự đoán |
| `features.py` | trích 6 thuộc tính rời rạc từ câu tiếng Việt bằng từ điển từ khóa |
| `logic.py` | cây thành luật IF-THEN, logic mệnh đề, logic vị từ (∀, ∃), bảng chân trị |
| `model.py` | huấn luyện, dự đoán, đánh giá leave-one-out |
| `app.py` | API: `GET /api/dataset`, `POST /api/train`, `POST /api/predict`, `GET /health` |
| `static/index.html` | giao diện |
| `tests/test_id3.py` | kiểm thử, gồm bộ PlayTennis kinh điển (Gain(Outlook) ≈ 0.247) |

## Hạn chế

Dữ liệu mẫu do soạn tay và gán nhãn đúng theo quy tắc mà từ điển bắt được, nên độ chính xác 100% không phản ánh văn bản thực tế. Câu có từ ngoài từ điển, mỉa mai hoặc phủ định phức tạp sẽ bị phân loại sai. ID3 chỉ nhận thuộc tính rời rạc và dễ overfit khi dữ liệu ít.
