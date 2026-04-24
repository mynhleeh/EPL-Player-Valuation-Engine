# Nguyên tắc viết báo cáo
## 1: Cấu trúc & Tổ chức thông tin (Structure)
* **Khung tài liệu chuẩn mực:** Bắt buộc phải có Tóm tắt (Summary) khái quát toàn bộ đồ án ở trang đầu. Phải có Mục lục (Table of Contents) và Danh mục Hình ảnh/Bảng biểu (List of Figures/Tables).
* **Phân rã vấn đề (Problem Breakdown):** Mỗi yêu cầu/bài toán không được trình bày lộn xộn mà phải tuân thủ cấu trúc phân tầng cố định:
    1.  *Mục tiêu bài toán (Objective)*
    2.  *Công cụ sử dụng (Tools/Libraries)*
    3.  *Phương pháp luận (Methodology)*
    4.  *Kết quả & Đánh giá (Results & Evaluation)*
* **Tính liền mạch:** Sử dụng tính năng ngắt trang (Page Break) để tách biệt các chương lớn, không để tiêu đề nằm ở cuối trang này nhưng nội dung lại trôi sang đầu trang kia.

## 2: Thẩm mỹ Học thuật & Trực quan hóa (Visuals & Formatting)
* **Tuyệt đối KHÔNG chụp ảnh màn hình Code:** Nếu bắt buộc phải đưa mã nguồn vào báo cáo để minh họa một thuật toán phức tạp, hãy sử dụng các hộp định dạng (Code Blocks) với phông chữ Monospace (ví dụ: Consolas, Courier New) nền sáng. Tốt nhất, hãy đưa code vào phần Phụ lục (Appendix).
* **Chuyển hóa Dữ liệu (Data Transformation):** Không bao giờ sao chép trực tiếp kết quả từ Terminal hoặc chụp ảnh Terminal. Dữ liệu đầu ra (ví dụ: top 3 cầu thủ, bảng dự đoán giá trị) phải được thiết kế lại thành các Bảng biểu (Tables) được căn lề và định dạng viền chuyên nghiệp.
* **Tiêu chuẩn Biểu đồ:** Mọi biểu đồ (Histogram, Scatter plot, PCA) khi xuất ra từ Python (matplotlib/seaborn) phải được lưu ở độ phân giải cao, dán vào báo cáo phải giữ nguyên tỷ lệ khung hình (không bị bóp méo). Phải luôn có nhãn trục X/Y, chú giải (Legend) và Tiêu đề Hình ảnh (Figure Caption) đặt ngay bên dưới biểu đồ.

## 3: Nghệ thuật Giải thích Kỹ thuật (Technical Explanation)
* **Văn phong Khách quan (Objective Tone):** Loại bỏ hoàn toàn các đại từ nhân xưng ngôi thứ nhất ("Tôi", "Chúng tôi", "I", "We"). Chuyển sang sử dụng thể bị động hoặc đặt "Dữ liệu/Mô hình/Hệ thống" làm chủ ngữ. (Ví dụ: Thay vì viết *"Tôi đã dùng hàm dropna để xóa dữ liệu trống"*, hãy viết *"Các dữ liệu trống được loại bỏ để đảm bảo tính nhất quán của mô hình"*).
* **Trừu tượng hóa vấn đề (Abstraction):** Giải thích "Tại sao" (Why) và "Như thế nào về mặt Toán học/Logic" (How), thay vì dịch Code sang tiếng Việt. Giảng viên biết thư viện `pandas` dùng để làm gì, bạn không cần viết "Thư viện pandas được dùng để xử lý dataframe". Hãy tập trung giải thích: *Tại sao bạn lại chọn các đặc trưng (features) đó cho mô hình phân cụm? Logic nội suy dữ liệu hỏng của bạn là gì?*


# Checklist

**Về Bố cục & Hình thức:**
- [ ] Báo cáo đã có trang Tóm tắt (Summary), Mục lục (TOC) và Danh mục hình ảnh chưa?
- [ ] Các chương, phần lớn đã được ngắt trang (Page Break) hợp lý chưa?
- [ ] Mình có lỡ dùng từ ngữ cảm xúc, đánh giá chủ quan (ví dụ: "giao diện đẹp", "kết quả tuyệt vời") không?

**Về Xử lý Code & Biểu đồ:**
- [ ] Mình CÓ ĐANG chụp ảnh màn hình giao diện IDE (VSCode, PyCharm...) để chèn vào bài không? (Nếu CÓ -> XÓA NGAY).
- [ ] Có đoạn raw code lộn xộn nào đang nằm tản mạn giữa các đoạn văn bản không?
- [ ] Các biểu đồ có bị méo/biến dạng không? Đã có tên trục (X, Y) và chú thích ảnh (Figure 1, Figure 2...) ở dưới mỗi ảnh chưa?
- [ ] Kết quả đầu ra (Output) đã được kẻ bảng cẩn thận chưa, hay vẫn đang là ảnh chụp màn hình nền đen chữ trắng từ Terminal?

**Về Văn phong Diễn đạt:**
- [ ] Dùng chức năng tìm kiếm (Ctrl+F) để quét các từ "Tôi", "Mình", "Nhóm", "I", "We". Mình đã xóa/viết lại toàn bộ những câu chứa các từ này thành thể bị động chưa?
- [ ] Mình đang giải thích ý tưởng của thuật toán (Tư duy), hay chỉ đang tường thuật lại chức năng của từng hàm trong Python (Cú pháp)? Chuyển trọng tâm sang giải thích Tư duy.