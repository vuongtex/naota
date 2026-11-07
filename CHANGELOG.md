# Nhật ký cập nhật

***Tiếng Việt** · [English](CHANGELOG.en.md)*

Lịch sử phiên bản NAOTA. Bản mới nhất ở trên cùng. Xem ngay trong app tại mục **Cập nhật** (bấm ô tài khoản dưới đáy thanh bên).

Định dạng: mỗi phiên bản là một khối `## [x.y.z] - ngày`, bên dưới nhóm thay đổi theo `### Thêm mới / Sửa lỗi / Cải thiện / Bảo mật`.

## [1.9.0] - 2026-11-07
### Cải thiện
- Đang viết.

## [1.8.1] - 2026-11-07
### Sửa lỗi
- **Nick Zalo rớt đăng nhập thì chuông báo ngay:** trước đây bot im mà chủ không hay biết, vì lỗi chỉ nằm trong nhật ký máy chủ. Nay chuông và Telegram báo rõ nick nào cần đăng nhập lại, và thẻ bot nói đúng lý do.

## [1.8.0] - 2026-11-05
### Bảo mật
- **Đóng nhiều đường rò từ đợt rà soát:** chatbot và việc nền dưới mức Toàn quyền không còn ghi được vào chỗ chứa mã chạy, việc hẹn giờ không vượt mức quyền của người tạo, file HTML mở từ bộ não chạy trong hộp cách ly, trang lạ trên máy không gửi lệnh vào NAOTA được.
### Thêm mới
- **Trang Models mới:** nút Ngắt kết nối trên mọi thẻ, OpenAI Compatible và Claude Compatible thêm được nhiều key và tự chuyển key khi hết lượt, Antigravity trên VPS thêm được tài khoản (phần này chưa thử với `agy` thật).
- **Naota Core sửa như một trợ lý**, đổi được tên riêng theo từng bộ não. **Một bot phục vụ tới 100 Trang Facebook.** Avatar có menu tự sắp xếp, gọi thoại từ chat trợ lý thì nói đúng vai trợ lý đó.
### Cải thiện
- **Việc nền bằng API key chạy tới cùng**, tới 500 vòng công cụ, mức Toàn quyền có terminal thật. **Chat sửa được mọi việc và lịch hẹn** trong Việc cần làm.
- **Nhanh và gọn hơn:** chuyển chat, Việc cần làm, Nhóm và Trợ lý tức thì, mic chép lời có ở hộp trả lời khách, Enter là gửi, trên Android không còn lặp từ.

## [1.7.0] - 2026-11-05
### Thêm mới
- **Việc của tôi có Nhịp hôm nay**: chuỗi Ngày sạch, gắn sao tối đa 3 việc ưu tiên, Bỏ qua lần này cho việc lặp, icon Dời và Xoá ngay trên dòng (xoá nhầm thì bấm Hoàn tác), và lời khen khi xong việc.
- **Lượt trả lời dài xong thì báo điện thoại**: từ 3 phút trở lên chuông sẽ rung, máy đang mở thì thôi. Lệnh chạy ngầm xong tự báo về đúng khung chat rồi làm tiếp phần đã hẹn.
### Cải thiện
- **Việc hẹn giờ tạo trong chat Cộng sự** báo về đúng chat đó và chạy đúng vai trợ lý đó, sự cố cũng báo về nơi giao việc. Việc đã tạo trước đây vẫn chạy như cũ. Lịch chạy bằng Codex giờ giao được việc cho Nhóm.
- **Hộp thư mở hội thoại tức thì**, chỉ tải phần tin mới. **Tên gói Claude hiển thị đúng** theo nhà cung cấp (ví dụ Ultra).

## [1.6.1] - 2026-11-04
### Thêm mới
- **Nút Sửa Agent ngay trong form Chatbot**: sửa Agent của bot tại chỗ, phần đang nhập trong form vẫn còn nguyên.
### Sửa lỗi
- **Luật dạy Trợ lý trong chat giờ tới được bot**: bot ở mọi mức quyền đều làm theo, không cần chép lại vào file Agent.
- **Bot đọc được danh thiếp Zalo**: khách gửi danh thiếp thì bot và Hộp thư thấy tên và số điện thoại.
- **Bot mức Chỉ đọc, Đọc tài liệu, Được ghi biết giờ hiện tại**: khách hỏi hôm nay hay giờ làm việc, bot không còn phải đoán.

## [1.6.0] - 2026-11-04
### Thêm mới
- **Threads vào thẻ Kết nối Meta**: bình luận dưới bài Threads về Hộp thư, bot trả lời công khai được. Mỗi tài khoản chọn tắt, chỉ hiện Hộp thư, hoặc bot trả lời. Threads chỉ cho ẩn bình luận chứ không cho xoá, NAOTA nói rõ và hỏi lại trước khi làm.
- **Nhóm làm được nhiều hơn**: gắn repo GitHub (sửa trên nhánh riêng, mở PR, CI đỏ tự giao sửa tối đa 3 vòng), gọi `/skill` trong chat Nhóm, và thành viên tự mở việc khi được giao từ khung chat, mặc định tối đa 5 việc mỗi ngày.
- **Việc của tôi có Tags và việc con**: Dự án cũ tự thành tag, không mất gì. Ghi chú gắn được link, `[[note]]` và file.
- **Kênh API nội bộ (thử nghiệm)**: một máy chủ của bạn hỏi Chatbot qua HTTP. Khoá hiện một lần, bot chỉ đọc, mặc định chỉ chính máy chạy NAOTA gọi được.

### Cải thiện
- **Kéo thả sắp xếp** Project, chat đã ghim và tag, mọi máy thấy cùng thứ tự. Thẻ Naota Core nói rõ đang chạy model nào và chọn được ngay trên thẻ. Điện thoại có nút **Cài lên điện thoại** trong menu.
- **Claude Code chờ việc chạy nền xong** rồi trả lời tiếp, tối đa 30 phút. Câu trả lời cho tin nhắn thêm giữa chừng hiện ngay dưới tin đó. Antigravity hết báo nhầm là không đọc được file ngữ cảnh.

## [1.5.0] - 2026-11-04
### Thêm mới
- **Nhắn riêng cho người bình luận** ngay trong hội thoại bình luận: chọn Trả lời công khai hoặc Nhắn riêng phía trên ô soạn. Meta cho một lần mỗi bình luận, trong vòng 7 ngày.
- **Instagram vào chung Hộp thư**: tick "Nối cả Instagram của Trang" khi kết nối, tin nhắn và bình luận Instagram về cùng chỗ, cùng bot với Trang.
- **Menu "..." của mỗi hội thoại** có thêm Xem trang cá nhân, Chặn, Xoá hội thoại. NAOTA luôn hỏi lại trước khi Xoá, vì xoá bình luận hay hội thoại Zalo cá nhân là xoá thật trên đó.

### Cải thiện
- Thẻ Facebook Messenger đổi thành **Kết nối Meta**, có icon từng ứng dụng, thêm nút **Gỡ kết nối** từng Fanpage. Hội thoại cũ vẫn giữ. Bình luận và Instagram có icon riêng để dễ phân biệt trong Hộp thư.

## [1.4.0] - 2026-11-03
### Thêm mới
- **Chọn múi giờ** ở **Cài đặt** (khối Ngôn ngữ và múi giờ) và ở bước cuối bộ cài lần đầu. "Hôm nay, hôm qua", nhắc hẹn và số liệu báo cáo tính theo múi giờ đó, kể cả khi máy chủ chạy giờ UTC. Mặc định là giờ Việt Nam.

### Sửa lỗi
- **Hết đơ máy lúc NAOTA đang trả lời**, và hết cảnh "Đang kết nối lại" lặp đi lặp lại trên máy hay mạng chậm.
- **Máy chủ nhỏ (VPS 1-2 nhân) không còn đứng hình** vì vài việc chậm chạy chặn cả app. Bộ nghe tin thoại chừa lại một nhân cho máy chủ.
- **Báo hết hạn mức 5 giờ của gói Claude ghi giờ mở lại theo múi giờ của bạn**, không còn theo giờ UTC.
- Windows: kết nối chạy bằng `npx` không còn hỏng khi đường dẫn có dấu cách, và link dạng `/C:/...` trong câu trả lời bấm mở được.

### Cải thiện
- **Mở chat mới bằng Claude Code đỡ tốn hạn mức**: phần lời dặn hệ thống giữ y nguyên giữa các chat để đọc lại từ bộ nhớ đệm.
- Bảng từ 4 cột trở lên trong Trò chuyện được rộng hơn trên máy tính, chữ thường vẫn giữ khổ dễ đọc.

## [1.3.6] - 2026-11-03
### Sửa lỗi
- **Trên điện thoại, bấm nút Cập nhật ở đáy menu thì menu tự đóng**, trang Cập nhật hiện ra ngay. Trước đây trang đã chuyển nhưng menu vẫn che.
- **Bấm Nâng cao trên điện thoại không còn làm menu đóng mất**, nên chọn được các mục bên trong.

## [1.3.4] - 2026-11-03
### Sửa lỗi
- **Bot Zalo trong nhóm nhận ra khi được tag bằng tên Zalo của nick**, kể cả ngay sau khi máy chủ khởi động lại. Trước đây NAOTA quên tên đó mỗi lần khởi động lại, nên tag nick bằng tên khác với tên kết nối thì bot im.

## [1.3.3] - 2026-11-03
### Sửa lỗi
- **Trang Chatbot ghi đúng tên bộ não đang chọn**, không còn hiện chữ "brain" hay đường dẫn thư mục. Phần giải thích mức **Được ghi** và **Toàn quyền** của bot cũng ghi "bộ não".

## [1.3.2] - 2026-11-03
### Cải thiện
- **Tiêu đề trang khớp tên trên thanh bên**: Bản đồ bộ não, Việc cần làm, Trợ lý, Kết nối dữ liệu, Kênh của tôi, Chọn Models.
- **Trên điện thoại, ô chọn bộ não nằm đầu menu**, mở menu ra là thấy ngay đang ở bộ não nào.

## [1.3.1] - 2026-11-03
### Cải thiện
- Chỉ đổi số phiên bản. Hai thay đổi định đưa vào bản này nằm ở bản 1.3.2.

## [1.3.0] - 2026-11-03
### Cải thiện
- **Thanh bên mới một cột**: các mục chia khúc có tên nhỏ (Đội ngũ, Kiến thức, Kết nối, Hệ thống).
- **Tên mục dễ hiểu hơn trên thanh bên**: Bản đồ bộ não, Trò chuyện, Việc cần làm, Trợ lý, Kết nối dữ liệu, Chọn Models.
- **Số phiên bản và nút Cập nhật luôn hiện dưới đáy thanh bên**, có bản mới thì nút chuyển vàng.
- **Nâng cao nằm dưới Tài khoản**, bấm là xổ Terminal, Plugin, Webhook, Phiên đăng nhập, Link chia sẻ và Cộng đồng NAOTA. Ngôn ngữ chọn trong Cài đặt. Các trang và thanh trên giữ nguyên như 1.2.1.

## [1.2.1] - 2026-11-03
### Cải thiện
- **Chợ ứng dụng có Naota Gate**: ChatGPT, Claude nối vào Naota qua một gói, đọc và nhắn vào hội thoại, ghi sổ tay. Máy đã cài gói **Naota trong ChatGPT** thấy Gate như một bản cập nhật, không phải nối lại.
- **14 gói của Chợ ứng dụng đổi sang mã tiếng Anh**, ví dụ Quản lý khách hàng là `naota.crm`. Gói đã cài hiện **Có bản mới** và cập nhật tại chỗ, giữ nguyên dữ liệu.

## [1.2.0] - 2026-11-03
### Thêm mới
- **ChatGPT, Claude ghi sổ tay vào Naota.** Khi bạn bàn việc với một AI bên ngoài đã nối vào Naota, AI đó ghi lại bạn đã nói gì, đã chốt gì và vì sao. Naota giữ được ngữ cảnh và nhớ quyết định của bạn, không tốn lượt chạy nào.
### Cải thiện
- Trang **Ghi nhớ** ghi rõ là **NAOTA**: đồng bộ NAOTA với GitHub, NAOTA tự học từ trò chuyện, NAOTA đã tự học gì.

## [1.1.1] - 2026-11-03
### Sửa lỗi
- **Menu trên điện thoại không còn đè chữ.** Các mục cuối (Nguồn dữ liệu, Chợ ứng dụng, Hệ thống...) từng tràn lên ô ngôn ngữ, ô chọn bộ não và số phiên bản. Giờ mọi thứ xếp liền nhau, vuốt xuống là thấy.

## [1.1.0] - 2026-11-02
### Thêm mới
- **Bộ cài cho máy tính.** Tải Naota-Setup.exe (Windows) hoặc Naota-macOS.dmg (Mac), mở như mọi ứng dụng, không phải gõ lệnh.
- **Fanpage nối một lần, dùng cho ba việc:** bấm Đăng nhập Facebook là bot trả lời tin nhắn Messenger, trả lời bình luận dưới bài, và Naota đăng bài lên Trang ngay hoặc theo lịch. Có hướng dẫn từng bước.
- **Nghe tin nhắn thoại không cần Groq:** dùng khoá OpenAI, Gemini, hoặc bộ nghe chạy ngay trên máy. Chatbot Zalo cá nhân nghe được tin thoại và xem được video khách gửi.
- **AI bên ngoài giao việc cho Naota:** tìm, đọc và gửi lời nhắn vào một cuộc trò chuyện của Naota như chính bạn gõ, bạn xem được trực tiếp và bấm Dừng khi cần.
### Cải thiện
- **Chữ hiện ra dần khi trả lời** với mọi bộ não: Claude Code, Grok Build, Antigravity và các bộ não dùng khoá API.
- **Trang Webhook làm lại:** tóm tắt gọn một dòng, mỗi webhook mở trong một cửa sổ riêng, tìm quy trình theo tên.
- **Chọn bộ não** bằng danh sách riêng của Naota, giống nhau trên mọi máy và tự sắp được thứ tự. File .html mở ra xem trang ngay, mã ở tab bên cạnh. Dán đoạn dài thì xem trước rồi chọn dán hay đính kèm.
- **Đội ngũ tự thử lại** bước gặp lỗi tạm thời, và mỗi phần của kế hoạch ghi rõ phải chờ phần nào xong trước.
### Sửa lỗi
- Đăng nhập Claude trên máy có trình duyệt tự hoàn tất, không còn chờ mã. Kéo thả file vào khung chat chính chạy lại, ghi nhớ bớt lấy nhầm nhật ký cũ, tên file có dấu giữ đúng khi tải về.
## [1.0.5] - 2026-11-02
### Sửa lỗi
- **Nút Cập nhật trên VPS không còn đứng chờ mãi.** Máy chủ chạy NAOTA bằng tài khoản thường mà chưa cho phép tự cập nhật thì trang báo lỗi ngay, kèm lệnh cập nhật tay và cách bật nút Cập nhật, thay vì chờ 10 phút rồi bảo tải lại trang.

## [1.0.4] - 2026-11-02
### Cải thiện
- **Bộ icon mới** cho cả thanh bên lẫn bên trong app, nét gọn và dễ nhận hơn.
- Mục **Linh vật** đổi tên thành **Avatar**.
- **Cập nhật** ra hẳn thanh bên, ngay dưới **Tài khoản**. Có bản mới thì mục này hiện chấm **Mới**.
- Chữ "brain" sót lại trong giao diện, trang Plugin và trang Tự học đã đổi sang tiếng Việt: **bộ não** là kho ghi chú, **model AI** là Claude, ChatGPT...

## [1.0.3] - 2026-11-02
### Cải thiện
- **Trang Tài khoản và Cài đặt** ghi khối **Tên NAOTA** thay cho chữ Workspace. Trang **Models AI** ghi nhãn **Chính** trên thẻ bộ não chính.

## [1.0.2] - 2026-11-02
### Cải thiện
- **Chợ ứng dụng gọi một tên.** Nút và lời nhắc ở trang Cộng sự, Nguồn dữ liệu, Plugin đều ghi **Chợ ứng dụng**, khớp thanh bên.
- **Bớt chữ tiếng Anh khó hiểu:** trang Học ghi Ghi nhớ, Cộng sự, Quy trình, Bảng việc, **Dọn dẹp định kỳ**; trang Models AI ghi **bộ não chính**; trang Tài khoản ghi **Tên NAOTA của bạn**.

## [1.0.1] - 2026-11-02
### Cải thiện
- **Thanh bên gọn hơn.** Mọi mục hiện một lượt, không phải mở từng nhóm. Mục ít dùng gom vào nhóm **Nâng cao**, nhóm **Hệ thống** ghim ở đáy.
- **Tên menu dễ hiểu hơn:** Sơ đồ, Tài liệu, Ghi nhớ, Đội ngũ, Bảng việc, Nguồn dữ liệu, Chợ ứng dụng, Kênh của tôi, Models AI. Ra lệnh bằng giọng nói nhận cả tên mới.
- **Màn chào mừng nói dễ hiểu hơn.** Chọn bộ não bằng gói bạn đang dùng, vào xong bấm **Đăng nhập Claude** ở **Models AI**, không phải gõ lệnh.
- **Trang chủ toàn tiếng Việt:** Bộ não, Cộng sự, Kỹ năng, Quy trình, số ghi chú.
## [1.0.0] - 2026-10-31
### Thêm mới
- **NAOTA ra đời.** Bộ não AI của riêng bạn, do Hoàng Ngọc Vương phát triển cho cộng đồng NAOTA.
