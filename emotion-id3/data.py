"""Dữ liệu huấn luyện mẫu (tự soạn, nhỏ). Có thể thêm/xóa câu ngay trong giao diện."""

P, N, T = "Tích cực", "Tiêu cực", "Trung tính"

DEFAULT_DATA = [
    # Chỉ có từ tích cực
    ("Hôm nay tôi rất vui", P),
    ("Bộ phim này tuyệt vời!", P),
    ("Tôi yêu món ăn này", P),
    ("Cảm ơn bạn rất nhiều", P),
    ("Chuyến đi hôm qua thật thú vị và đáng nhớ", P),
    ("Tôi cảm thấy hạnh phúc bên gia đình", P),
    ("Quá tuyệt!", P),
    ("Cô giáo dạy rất hay và nhiệt tình", P),
    ("Tôi tự hào về kết quả của mình", P),
    ("Món phở này ngon quá 😍", P),
    ("Thời tiết hôm nay đẹp", P),
    ("Tôi rất hài lòng với dịch vụ ở đây", P),
    ("Tôi may mắn khi gặp được người bạn tốt", P),
    ("Hào hứng quá!", P),
    ("Cảnh biển buổi sáng thật đẹp và ấm áp", P),
    # Chỉ có từ tiêu cực
    ("Tôi buồn quá", N),
    ("Hôm nay tôi rất mệt và chán", N),
    ("Tôi ghét sự dối trá!", N),
    ("Dịch vụ ở đây tệ quá", N),
    ("Tôi thất vọng về kết quả này", N),
    ("Cô ấy khóc suốt đêm qua vì đau lòng", N),
    ("Tôi giận anh ta vô cùng!", N),
    ("Bộ phim dở kinh khủng", N),
    ("Tôi sợ ngày mai thi trượt", N),
    ("Tôi cảm thấy cô đơn trong thành phố này", N),
    ("Thật khó chịu!", N),
    ("Tôi bực mình vì bị trễ giờ", N),
    ("Món ăn này dở và đắt", N),
    ("Tôi hối hận vì đã nói như vậy", N),
    ("Lo lắng quá", N),
    # Từ tích cực bị phủ định thì thành tiêu cực
    ("Tôi không vui", N),
    ("Món này không ngon", N),
    ("Phim này chẳng hay chút nào", N),
    ("Tôi không hài lòng với dịch vụ", N),
    ("Hôm nay thời tiết không đẹp", N),
    ("Tôi chưa hạnh phúc", N),
    ("Cô ấy không tốt với tôi", N),
    # Từ tiêu cực bị phủ định thì thành trung tính
    ("Tôi không buồn", T),
    ("Món này chẳng tệ", T),
    ("Tôi không ghét anh ấy", T),
    ("Tôi không còn lo lắng nữa", T),
    # Không có từ cảm xúc
    ("Hôm nay trời nhiều mây", T),
    ("Tôi đang đi học", T),
    ("Cuộc họp bắt đầu lúc chín giờ", T),
    ("Tôi không biết", T),
    ("Ngày mai tôi đi Hà Nội", T),
    ("Cửa hàng mở cửa từ sáng đến tối", T),
    ("Tôi chưa ăn sáng", T),
    ("Xe buýt đến trạm lúc tám giờ!", T),
    # Vừa tích cực vừa tiêu cực
    ("Phim hay nhưng kết thúc tệ", T),
    ("Món ăn ngon nhưng phục vụ chậm và dở", T),
    ("Tôi vui nhưng cũng hơi lo lắng", T),
    ("Cảnh đẹp nhưng đường đi mệt quá!", T),
]

DEFAULT_DATA = [{"text": t, "label": l} for t, l in DEFAULT_DATA]
