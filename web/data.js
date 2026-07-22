/* Marketing OS — mock data + navigation config (data thật nối sau) */
window.MOCK = {
  nav: [
    // LAUNCH-READINESS Pha 0: nav = GOLDEN PATH v1 (①→⑦ + Báo cáo kênh). Trang mock/chờ-FB
    // gom xuống "Sắp có" (soon:true → disable, giữ code + route vẫn chạy qua hash trực tiếp).
    // admin = operator-only → bỏ khỏi nav (vẫn vào được qua #admin). Xem docs/cmo/LAUNCH-READINESS.md.
    { group: '① Chẩn đoán', items: [
      { id: 'dossier',    label: 'Hồ sơ doanh nghiệp', icon: '🗂️' },
      { id: 'market',     label: 'Thị trường',         icon: '🌐' },
      { id: 'competitor', label: 'Đối thủ',            icon: '🥊' },
      { id: 'customer',   label: 'Khách hàng',         icon: '👥' },
      { id: 'pricing',    label: 'Định giá',           icon: '💰' },
      { id: 'swot',       label: 'SWOT',               icon: '🧭' },
    ]},
    { group: '② Nền thương hiệu', items: [
      { id: 'strategy',   label: 'Định vị & Chiến lược', icon: '🎯' },
      { id: 'message',    label: 'Thông điệp',           icon: '🏛️' },
      // voice → "Sắp có": trang này đọc user_brand_voice (chỉ bot ghi) → user self-serve luôn ra số
      // giả "Đạt 92%". Pha 2: repoint sang messaging.giọng (web sinh thật) rồi đưa lại lên đây.
    ]},
    { group: '③ Marketing', items: [
      { subhead: 'Chiến lược kênh' },
      { id: 'tactical', label: 'Cách đánh',           icon: '🔨' },
      { subhead: 'Sản xuất' },
      { id: 'direction', label: 'Định hướng',          icon: '🎯' },
      { id: 'matrix',   label: 'Ma trận & Chiến dịch', icon: '🧱' },
      { id: 'calendar', label: 'Lịch nội dung',       icon: '🗓️' },
      { id: 'adscopy',  label: 'Quảng cáo (copy)',    icon: '🧲' },
      { id: 'inbox',    label: 'Kịch bản chốt sale',  icon: '💬' },
      { id: 'sequence', label: 'Email / Zalo chuỗi',  icon: '✉️' },
    ]},
    { group: '④ Báo cáo kênh', items: [
      { id: 'channelreport', label: 'Báo cáo kênh',   icon: '📱' },
    ]},
    { group: '⑤ Hệ thống', items: [
      { id: 'settings', label: 'Cài đặt', icon: '⚙️' },
    ]},
    { group: 'Sắp có', items: [
      { id: 'voice',        label: 'Giọng & Tính cách',    icon: '🗣️', soon: true },
      { id: 'brandhealth',  label: 'Sức khỏe thương hiệu', icon: '🏛️', soon: true },
      { id: 'overview',     label: 'Hiệu quả Marketing',   icon: '📊', soon: true },
      { id: 'adsanalytics', label: 'Phân tích quảng cáo',  icon: '📈', soon: true },
      { id: 'optimizer',    label: 'Tối ưu tự động',       icon: '⚡', soon: true },
      { id: 'spy',          label: 'Theo dõi đối thủ',     icon: '🕵️', soon: true },
      { id: 'schedule',     label: 'Lịch trình & cảnh báo', icon: '⏰', soon: true },
      { id: 'accounts',     label: 'Kết nối tài khoản',    icon: '🔗', soon: true },
      { id: 'reports',      label: 'Báo cáo',              icon: '📑', soon: true },
    ]},
  ],

  // Hành trình khách hàng — context cho Max + thanh tiến trình
  journey: [
    { id: 'discovery', label: 'Khám phá',  icon: '🔍', page: 'dossier',  desc: 'Hiểu doanh nghiệp' },
    { id: 'diagnosis', label: 'Chẩn đoán', icon: '🩺', page: 'competitor', desc: 'Thị trường · đối thủ · khách hàng' },
    { id: 'strategy',  label: 'Chiến lược', icon: '🎯', page: 'strategy',  desc: 'Định vị · roadmap · KPI' },
    { id: 'execution', label: 'Sản xuất',  icon: '✍️', page: 'content',   desc: 'Nội dung · chiến dịch' },
    { id: 'run',       label: 'Vận hành',  icon: '📡', page: 'adsanalytics', desc: 'Chạy ads · tối ưu' },
  ],

  industries: ['F&B','Tech SaaS','E-commerce','Giáo dục','Health & Beauty','Bán lẻ','B2B Services','Bất động sản'],

  pipeline: [
    { name: 'Nghiên cứu thị trường', desc: 'TAM/SAM/SOM + động lực thị trường', status: 'done' },
    { name: 'Phân tích đối thủ',     desc: '8 đối thủ × 8 chiều', status: 'done' },
    { name: 'Customer Insight',      desc: 'ICP + JTBD + tâm lý', status: 'done' },
    { name: 'Định giá & Tâm lý',     desc: 'Mô hình giá + chiến thuật tâm lý', status: 'running' },
    { name: 'Social Listening',      desc: 'Tiếng nói khách hàng online', status: 'pending' },
    { name: 'Chiến lược tổng hợp',   desc: 'SAVE + SMART + roadmap 90 ngày', status: 'pending' },
  ],

  competitors: [
    { name: 'Đối thủ A', pos: 'Cao cấp', price: '$$$', usp: 'Thương hiệu mạnh', share: 28, threat: 'Cao' },
    { name: 'Đối thủ B', pos: 'Tầm trung', price: '$$', usp: 'Giá tốt', share: 19, threat: 'Trung bình' },
    { name: 'Đối thủ C', pos: 'Ngách', price: '$$$', usp: 'Cá nhân hóa', share: 12, threat: 'Trung bình' },
    { name: 'Đối thủ D', pos: 'Giá rẻ', price: '$', usp: 'Khuyến mãi liên tục', share: 9, threat: 'Thấp' },
  ],

  tracked: [
    { name: 'Highlands Coffee', ads: 24, status: 'online', last: '12 phút trước' },
    { name: 'Phúc Long',        ads: 17, status: 'online', last: '1 giờ trước' },
    { name: 'Katinat',          ads: 31, status: 'warn',   last: '3 giờ trước · 5 ad mới' },
  ],

  personas: [
    { name: 'Linh — Văn phòng', age: '25–34', job: 'Tiết kiệm thời gian buổi sáng', pain: 'Bận, ít thời gian', motiv: 'Tiện lợi & ổn định' },
    { name: 'Huy — Freelancer',  age: '22–30', job: 'Không gian làm việc',          pain: 'Hay đổi chỗ ngồi', motiv: 'Wifi & yên tĩnh' },
    { name: 'Mai — Sinh viên',   age: '18–24', job: 'Gặp gỡ bạn bè',                pain: 'Ngân sách hạn chế', motiv: 'Giá tốt, check-in đẹp' },
  ],

  pricingTiers: [
    { name: 'Economy', price: '29.000₫', tag: 'Dẫn dắt', items: ['Sản phẩm cơ bản','Không topping','Giờ thấp điểm'] },
    { name: 'Standard', price: '49.000₫', tag: 'Phổ biến', items: ['Size lớn','1 topping','Tích điểm'], hot: true },
    { name: 'Premium', price: '79.000₫', tag: 'Biên cao', items: ['Combo đôi','Topping cao cấp','Ưu tiên phục vụ'] },
  ],

  funnel: [
    { tier: 'Hiển thị', value: 1240000, cost: 'CPM 38.000₫', rate: '100%' },
    { tier: 'Click',    value: 42350,   cost: 'CPC 1.250₫',  rate: '3,4%' },
    { tier: 'Landing',  value: 36100,   cost: '—',           rate: '85%' },
    { tier: 'Lead',     value: 5240,    cost: 'CPL 9.600₫',  rate: '14,5%' },
    { tier: 'Booking',  value: 2380,    cost: 'CPA 21.100₫', rate: '45%' },
    { tier: 'Mua hàng', value: 1610,    cost: 'CPA 31.200₫', rate: '67%' },
  ],

  winners: [
    { name: 'CD Mùa hè — Video 9:16', roas: 4.1, spend: '2.1M', cpa: '24.000₫' },
    { name: 'Re-targeting 7 ngày',    roas: 5.3, spend: '1.4M', cpa: '18.500₫' },
  ],
  losers: [
    { name: 'Carousel SP cũ',  roas: 0.9, spend: '1.8M', cpa: '95.000₫' },
    { name: 'Lookalike 5%',    roas: 1.4, spend: '1.1M', cpa: '61.000₫' },
  ],

  optimizations: [
    { action: 'scale', text: 'Tăng ngân sách 20% — “Re-targeting 7 ngày”', why: 'ROAS 5,3x > mục tiêu', },
    { action: 'pause', text: 'Tạm dừng — “Carousel SP cũ”', why: 'CPA 95.000₫ vượt ngưỡng', },
    { action: 'dup',   text: 'Nhân bản — “Video 9:16” sang Lookalike 2%', why: 'Mẫu thắng, mở rộng', },
    { action: 'activate', text: 'Bật lại — “CD Tết” (theo lịch)', why: 'Đến khung giờ vàng', },
  ],

  jobs: [
    { name: 'Daily Digest',    when: '08:00 hằng ngày', status: 'on' },
    { name: 'Weekly Report',   when: 'Thứ 2, 08:00',    status: 'on' },
    { name: 'Alert Monitor',   when: 'Mỗi 4 giờ',        status: 'on' },
    { name: 'Token Refresh',   when: '02:00 hằng ngày', status: 'on' },
    { name: 'Snapshot Cleanup',when: 'CN, 03:00',        status: 'on' },
    { name: 'Competitor Monitor', when: 'Mỗi 1 giờ',     status: 'on' },
  ],

  thresholds: [
    { name: 'Frequency tối đa', value: '5,0' },
    { name: 'ROAS giảm cảnh báo', value: '20%' },
    { name: 'CPM tăng cảnh báo', value: '30%' },
  ],

  accounts: [
    { name: 'TK Quảng cáo 01', id: 'act_8842', status: 'online', spend: '8.2M/ngày' },
    { name: 'TK Quảng cáo 02', id: 'act_5510', status: 'off',    spend: 'Tạm dừng' },
  ],

  saveFramework: [
    { k: 'S', name: 'Solution — Giải pháp', text: 'Định khung theo vấn đề được giải quyết, không phải tính năng.' },
    { k: 'A', name: 'Access — Tiếp cận',    text: 'Kênh & cách mua khách hàng ưa thích (Maps, FB, Zalo OA).' },
    { k: 'V', name: 'Value — Giá trị',      text: 'Tổng giá trị cảm nhận vs lựa chọn thay thế + ROI.' },
    { k: 'E', name: 'Education — Giáo dục', text: 'Giáo dục nhu cầu TRƯỚC khi chào bán.' },
  ],

  // Định hướng theo giai đoạn (KHÔNG chốt số — số chốt khi lập chiến dịch, D-029/D-030)
  directionalGoals: [
    '0–30 ngày — ưu tiên NHẬN DIỆN: phủ thông điệp định vị, validate kênh & mẫu nội dung',
    '31–60 ngày — ưu tiên TƯƠNG TÁC / LEAD: nuôi tệp quan tâm, thu lead chất lượng',
    '61–90 ngày — ưu tiên CHUYỂN ĐỔI: tối ưu & scale cái đã có tín hiệu tốt',
  ],

  roadmap: [
    { phase: '0–30 ngày', title: 'Nền tảng', items: ['Chuẩn brand voice','Setup tracking','3 chiến dịch TOFU'] },
    { phase: '31–60 ngày', title: 'Tăng tốc', items: ['Scale mẫu thắng','Re-targeting funnel','Loyalty cơ bản'] },
    { phase: '61–90 ngày', title: 'Tối ưu', items: ['Lookalike mở rộng','Winback chuỗi','Tối ưu ngân sách'] },
  ],

  pillars: [
    { name: 'Educate', pct: 30, color: '#5b8cff' },
    { name: 'Trust',   pct: 25, color: '#7c4dff' },
    { name: 'Engage',  pct: 25, color: '#38d9f0' },
    { name: 'Convert', pct: 20, color: '#2dd4a7' },
  ],

  calendar: {
    days: ['T2','T3','T4','T5','T6','T7','CN'],
    posts: [
      [{p:'Educate',t:'Mẹo pha cà phê'}],
      [{p:'Engage',t:'Mini-game'}],
      [{p:'Trust',t:'Review KH'},{p:'Convert',t:'Flash sale combo đôi'}],
      [{p:'Educate',t:'Hậu trường'}],
      [{p:'Convert',t:'Mua 1 tặng 1 cuối tuần'}],
      [{p:'Engage',t:'UGC repost'}],
      [{p:'Trust',t:'Câu chuyện thương hiệu'}],
    ],
  },
  // Kế hoạch nội dung — mô hình ĐÚNG marketing:
  //  • alwaysOn = nền brand LẶP MỖI TUẦN, luôn chạy (không tắt khi có campaign)
  //  • campaigns = lớp CỘNG THÊM theo dịp, có window theo TUẦN, posts đẩy lên trên
  calendarPlan: {
    days: ['T2','T3','T4','T5','T6','T7','CN'],
    weeks: 4,
    alwaysOn: [
      { pillar:'Educate', title:'Mẹo pha cà phê tại nhà' },
      { pillar:'Engage',  title:'Mini-game đoán vị' },
      { pillar:'Trust',   title:'Review khách quen' },
      { pillar:'Educate', title:'Hậu trường pha chế' },
      { pillar:'Engage',  title:'UGC khách check-in' },
      { pillar:'Trust',   title:'Câu chuyện thương hiệu' },
      { pillar:'Educate', title:'Kiến thức hạt specialty' },
    ],
    campaigns: [
      { name:'Sale Hè', occasion:'Mùa hè', offer:'Mua 1 tặng 1', color:'#f59e0b',
        fromWeek:2, toWeek:3, posts:[
          { week:2, day:2, title:'Khởi động Sale Hè — Mua 1 tặng 1' },
          { week:2, day:5, title:'Flash sale cuối tuần' },
          { week:3, day:1, title:'Nhắc: Sale Hè sắp kết thúc' },
          { week:3, day:4, title:'Ngày cuối Mua 1 tặng 1' },
        ]},
    ],
  },

  // User mới = sạch: chưa có output nào (điền hồ sơ → bấm Chạy mới sinh)
  bizSkillRuns: [],
  sampleDocs: {},

  // M3.2: adsCopy / sequence mock đã bỏ — Ads copy & Email/Zalo chuỗi nay sinh THẬT (api/biz/content/asset)

  voice: {
    do: ['Gần gũi, thân thiện','Dùng “bạn” thay “quý khách”','Câu ngắn, dễ đọc','Có cảm xúc tích cực'],
    dont: ['Sáo rỗng, hô khẩu hiệu','Thuật ngữ khó','Cường điệu quá mức','Spam emoji'],
    tone: [ {k:'Trang trọng ↔ Thân mật', v:75}, {k:'Nghiêm túc ↔ Hài hước', v:60}, {k:'Chuyên gia ↔ Bạn bè', v:68} ],
  },

  users: [
    { id: '527…412', plan: 'Pro',  quota: 200000, used: 142300 },
    { id: '811…097', plan: 'Free', quota: 50000,  used: 49100 },
    { id: '344…820', plan: 'Pro',  quota: 200000, used: 88600 },
    { id: '905…173', plan: 'Team', quota: 500000, used: 215400 },
  ],

  reports: [
    { name: 'Báo cáo tuần — CD Mùa hè', date: '14/06/2026', type: 'Tuần' },
    { name: 'Chiến lược 90 ngày — Quán cà phê', date: '10/06/2026', type: 'Chiến lược' },
    { name: 'Phân tích đối thủ — Q2', date: '02/06/2026', type: 'Đối thủ' },
  ],

  alerts: [],

  // ── Báo cáo kênh (social audit 1 page) — dữ liệu THẬT kéo từ ScrapeCreators (SpeeGo) làm mẫu.
  // KPI/posts/ads = số thật; analysis[] = mục tiêu layout (sẽ thay bằng output thật của Max ở bước sau).
  channelReports: [{
    id: 'speego', platform: 'facebook', sample: true,
    name: 'SpeeGo Logistics Trung - Mỹ',
    url: 'https://www.facebook.com/profile.php?id=61573631665167',
    pageId: '61573631665167', model: 'Chuyên sâu',
    dataScope: 'Báo cáo Phân tích Fanpage dựa trên Dữ liệu 6 bài đăng gần nhất',
    kpi: { like: 1456, follower: 1400, lf: '104.00%', rating: 'Not yet rated (0 Reviews)' },
    posts: [
      { n: 1, date: '16/07', react: 0, comment: 0, format: 'Ảnh', text: '📢 U.S. Import Market Update — Ocean carriers have significantly increased shipping capacity, while blank sailings remain at a very low level…' },
      { n: 2, date: '14/07', react: 0, comment: 0, format: 'Ảnh', text: 'A day at the factory with the SpeeGo team. For us, Quality Control is more than just inspecting products before shipment…' },
      { n: 3, date: '11/07', react: 0, comment: 0, format: 'Ảnh', text: 'Behind every successful shipment is a dedicated team committed to continuous learning and professional development…' },
      { n: 4, date: '08/07', react: 0, comment: 0, format: 'Ảnh', text: '📦 Muốn ra mắt sản phẩm mới nhưng MOQ quá cao? Đặt hàng số lượng lớn khiến vốn bị chôn, áp lực dòng tiền…' },
      { n: 5, date: '07/07', react: 0, comment: 0, format: 'Ảnh', text: 'Kiểm soát chất lượng phải bắt đầu từ trước khi hàng rời khỏi Trung Quốc. Một lỗi nhỏ có thể dẫn đến chi phí phát sinh…' },
      { n: 6, date: '04/07', react: 0, comment: 0, format: 'Ảnh', text: 'Kiểm tra chất lượng không phải là một công đoạn phát sinh. Đó là bước bắt buộc để xử lý một lô hàng lỗi…' },
    ],
    ads: [
      { n: 1, format: 'Video', cta: 'Send message', active: true, body: '🚫 ĐỪNG NHẬP HÀNG QUA TAOBAO HAY 1688 NỮA! Chi phí cao - Không kiểm soát chất lượng hàng hóa. SpeeGo giúp bạn nhập hàng trực tiếp từ nhà máy Trung Quốc với giá tận xưởng 🔥' },
      { n: 2, format: 'Video', cta: 'Send message', active: true, body: '🚫 ĐỪNG NHẬP HÀNG QUA TAOBAO HAY 1688 NỮA! Chi phí cao - Không kiểm soát chất lượng hàng hóa. SpeeGo giúp bạn nhập hàng trực tiếp từ nhà máy Trung Quốc với giá tận xưởng 🔥' },
      { n: 3, format: 'Video', cta: 'Send message', active: true, body: '🚫 ĐỪNG NHẬP HÀNG QUA TAOBAO HAY 1688 NỮA! Chi phí cao - Không kiểm soát chất lượng hàng hóa. SpeeGo giúp bạn nhập hàng trực tiếp từ nhà máy Trung Quốc với giá tận xưởng 🔥' },
    ],
    derived: {
      freqPerDay: 0.42, freqLabel: 'Thấp',
      totalReact: 0, totalComment: 0, avgReact: 0, avgComment: 0,
      formatDist: [['Ảnh', 6]],
      adFormatDist: [['Video', 3]],
      ctaDist: [['Send message', 3]],
      weekday: { react: [0, 0, 0, 0, 0, 0, 0], comment: [0, 0, 0, 0, 0, 0, 0], share: [0, 0, 0, 0, 0, 0, 0], view: [0, 0, 0, 0, 0, 0, 0] },
      dates: ['04/07', '07/07', '08/07', '11/07', '14/07', '16/07'],
      dateSeries: [0, 0, 0, 0, 0, 0],
    },
    analysis: [
      { n: 1, title: 'Định vị Thương hiệu', blocks: [{ t: 'SpeeGo tự định vị là đơn vị vận chuyển quốc tế uy tín, chuyên nghiệp, tập trung tuyến Trung - Mỹ. Muốn khách nhớ đến như đối tác tối ưu chi phí và tối đa hiệu quả chuỗi cung ứng, đặc biệt trong kiểm soát chất lượng tại nguồn và xử lý thủ tục hải quan.' }] },
      { n: 2, title: 'Giọng nói Thương hiệu', blocks: [{ t: "Ngữ điệu chuyên nghiệp, cung cấp thông tin, định hướng giải pháp. Từ khóa lặp lại: 'Quality Control', 'OEM/ODM', 'tối ưu chi phí', 'giảm thiểu rủi ro', 'kết nối trực tiếp với nhà máy', 'minh bạch', 'đáng tin cậy', 'đội ngũ onsite'." }] },
      { n: 3, title: 'Khách hàng Mục tiêu', blocks: [{ t: 'Chủ doanh nghiệp, nhà nhập khẩu, quản lý chuỗi cung ứng tại VN, Mỹ, Canada. Nỗi đau: chi phí nhập cao qua trung gian (Taobao/1688), khó kiểm soát chất lượng từ nhà máy, rủi ro tồn kho do MOQ cao, thủ tục hải quan phức tạp, biến động giá cước.' }] },
      { n: 4, title: 'Hoạt động & Xu hướng', blocks: [
        { h: 'THÓI QUEN HOẠT ĐỘNG', t: 'Tần suất 0.42 bài/ngày (thấp). 6 bài phân bổ T3(2), T4(1), T5(1), T7(2). Khung giờ đa dạng, không tập trung. Tất cả đều 0 reaction, 0 comment.' },
        { h: 'XU HƯỚNG HIỆU QUẢ', t: 'Toàn bộ bài tháng 07/2026 đều 0 tương tác — kênh đi ngang/suy giảm về tương tác hữu cơ, chưa có dấu hiệu tăng trưởng.' },
      ] },
      { n: 5, title: 'Tuyến Nội dung', blocks: [
        { h: 'CẬP NHẬT THỊ TRƯỜNG & QUY ĐỊNH', t: 'Định vị chuyên gia, cung cấp thông tin biến động thị trường + quy định nhập khẩu Mỹ (song ngữ Anh-Việt). 1 bài · 0/0.' },
        { h: 'CHỨNG MINH NĂNG LỰC & QUY TRÌNH VẬN HÀNH', t: 'Tuyến chủ lực — mô tả quy trình QC tại nhà máy + đào tạo đội ngũ. 4 bài · 0/0.' },
        { h: 'GIẢI PHÁP NỖI ĐAU KHÁCH HÀNG (OEM/ODM)', t: 'Nêu vấn đề MOQ cao → giới thiệu giải pháp OEM/ODM linh hoạt. 1 bài · 0/0.' },
      ] },
      { n: 6, title: 'Công thức Nội dung', blocks: [
        { h: 'PAS (PROBLEM-AGITATE-SOLUTION)', t: 'Dùng xuyên suốt 3 bài hữu cơ + 3 quảng cáo: nêu vấn đề → khuấy động hậu quả → giải pháp SpeeGo + CTA.' },
        { h: 'THÔNG TIN & CHUYÊN GIA', t: 'Cung cấp cập nhật thị trường khách quan rồi lồng vai trò hỗ trợ. Bài 1.' },
        { h: 'HẬU TRƯỜNG & CAM KẾT', t: 'Chia sẻ quy trình nội bộ / đào tạo đội ngũ, khai thác sự tin tưởng. Bài 2, 3.' },
      ] },
      { n: 7, title: 'Phân tích Reel', blocks: [{ t: 'Không có bài Reel trong phạm vi phân tích. (Một số bài dạng Video không được tính là Reel.)' }] },
      { n: 8, title: 'Hoạt động Quảng cáo', blocks: [
        { h: 'MỤC TIÊU CHIẾN DỊCH', t: "CTA 'Send message' cả 3 quảng cáo → lead generation, thúc đẩy liên hệ nhận báo giá. Nhắm giai đoạn cân nhắc (MoFu) và chuyển đổi (BoFu)." },
        { h: 'NỖI ĐAU NHẬP HÀNG TRUYỀN THỐNG & GIẢI PHÁP', t: "Đánh trực diện Taobao/1688 (chi phí cao, không kiểm soát chất lượng) → định vị SpeeGo là giải pháp trực tiếp từ nhà máy." },
      ] },
      { n: 9, title: 'Phễu Marketing', blocks: [
        { h: 'TOFU', t: 'Chưa có chiến lược rõ để thu hút người lạ — thiếu nội dung tò mò/giải trí/lan truyền. 0 bài.' },
        { h: 'MOFU', t: 'Tập trung xây niềm tin qua chứng minh năng lực + kiểm soát chất lượng. 6 bài.' },
        { h: 'BOFU', t: 'Soft Sell ở bài hữu cơ + Hard Sell ở quảng cáo (Send message). 3 bài.' },
      ] },
      { n: 10, title: 'Tương tác & Bình luận', blocks: [
        { h: 'CHIẾN THUẬT SEEDING (CỦA TRANG)', t: 'Không phát hiện bình luận seeding từ thương hiệu.' },
        { h: 'CHỦ ĐỀ THẢO LUẬN (CỦA NGƯỜI DÙNG)', t: 'Không có bình luận người dùng → không thể phân tích tâm lý/chủ đề thảo luận.' },
      ] },
      { n: 11, title: 'Tóm tắt Chiến lược', blocks: [{ t: 'Trang đang chững lại về tương tác tự nhiên (≈0 toàn bộ). Tuy nhiên có chiến lược nội dung rõ: chứng minh năng lực + giải quyết nỗi đau, dùng PAS. Quảng cáo CTA Send message hướng lead-gen. Trọng tâm xây niềm tin giữa phễu + thúc đẩy cuối phễu.' }] },
      { n: 12, title: 'Điểm mạnh & Điểm yếu', blocks: [
        { h: 'ĐIỂM LÀM TỐT', t: "Tuyến 'Chứng minh năng lực' đầu tư nhất (4/6 bài), khớp định vị 'chuyên nghiệp, đáng tin cậy'. Định vị 'VẬN CHUYỂN QUỐC TẾ GIÁ TỐT' rõ ràng, nhắm đúng nỗi đau chi phí. Nội dung song ngữ Anh-Việt là điểm cộng." },
        { h: 'ĐIỂM LÀM CHƯA TỐT', t: 'Tất cả tuyến đều 0 tương tác. Thiếu hoàn toàn nội dung giải trí/viral/case-study khách hàng → yếu TOFU. Thiếu minh chứng trực quan (ảnh/video lô hàng thành công). Tần suất thấp (0.42 bài/ngày).' },
        { h: 'ĐỀ XUẤT TỐI ƯU', t: "Bổ sung bằng chứng trực quan quy trình QC; thêm 'Câu chuyện thành công của khách hàng'; tăng tần suất ≥1 bài/ngày; mở tuyến 'Cập nhật giá cước & xu hướng vận chuyển'." },
      ] },
    ],
  }],

  settings: { daily_digest: 1, alert_threshold: 1, weekly_report: 1, competitor_new: 0 },

  campaigns: [
    { name: 'Mùa hè rực rỡ', status: 'running', budget: '6.5tr/ngày', objective: 'Chuyển đổi' },
    { name: 'Re-targeting Q2', status: 'running', budget: '3tr/ngày', objective: 'Doanh số' },
  ],
  calendarPosts: null,
};
