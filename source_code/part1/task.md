# crawl_data.py
1. Chạy xong đ thấy database đâu =))
2. Trong hàm rename_cols, không sử dụng chỉ số vì dễ gặp tính huống vị trí các cột bị đổi chỉ số. Bảng ban đầu ở dạng multi index, bảo AI nối level 0 với level 1. Tìm hiểu cái này đi
3. Cái code "df['Age'] = df['Age'].str[:2]" để làm j vây?
4. Code này không cần thiết "df['Nation'] = df['Nation'].str.split().str[-1].fillna("N/a")"
5. Code "df[nulls] = df[nulls].replace({0: np.nan, 0.0: np.nan})" không cần fill thành nan nữa (lỗi t lỗi t)

# Response
xong xuôi đổi tên file thành response.md rồi ghi rõ phần nào hoàn thiện r phần nào cấn cấn r báo lại t