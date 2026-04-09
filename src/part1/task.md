1. Sửa lại tên các cột trong database

2. Database sau khi lấy về vẫn lưu cùng folder code. Phải để file database trong folder data

3. Không dồn hết tất cả code vào một hàm, tách ra mỗi hàm một chức năng. Hàm nào thực hện chức năng của hàm đấy sau đó gọi hàm
Ví dụ: lấy dữ liệu từ web cho vào 1 hàm, ép kiểu số, làm sạch bảng cho vào một hàm, xuất ra sql 1 hàm,...

4. Không cần ghi những thông tin như "đang truy cập FBref", "Tối ưu hóa dữ liệu...",... Sau khi thực hiện xong 1 hàm thì chỉ cần trả về 1 dòng thông tin
Ví dụ: Hàm lấy dữ liệu từ web sau khi lấy xong thì in ra 1 thông báo ngắn gọn như "Colleted Data"

5. Hạn chế đặt tên rườm rà, sau khi đã code lại mỗi hàm một chức năng thì trong mỗi hàm đặt tên ngắn gọn, việc trùng tên không ảnh hưởng vì dữ liệu chỉ xuất hiện nội bộ trong hàm đó thành ra không liên quan gì đến các hàm còn lại