# Brain Vault Convention

## 4 Loại Note
- **frameworks**: Framework marketing ứng dụng cho nhiều ngành
- **industries**: Hồ sơ ngành (family: health-beauty, fnb, ...) — xem taxonomy 2 tầng ở KNOWLEDGE.md
- **craft**: Craft card output×kênh×ngành (vd tiktok-hook__health-beauty)
- **stages**: Giai đoạn trưởng thành business (launch, growth, scale)

## Quy Tác Đặt Tên
- **Slug**: kebab-case (ví dụ: `health-beauty`, `dunford-positioning`)
- Khớp giữa `applies_to` (frontmatter), `industry` (folder), và `slug` (filename)

## Frontmatter Keys
- **Bắt buộc**: `type`, `title`, `status`, `maturity`, `updated`, `source`
- **Routing** (chỉ cho framework): `applies_to`, `stage`, `goal_type`

## Ý Nghĩa [[Link]]
- `[[link]]` trong framework → note industry mà framework áp dụng được
- `[[link]]` trong industry → note framework phù hợp với ngành đó
- `[[link]]` trong craft → note framework mà craft triển khai
- Backlink = duyệt ngược: từ industry thấy mọi framework/craft trỏ vào nó

## Cách Hoạt Động
- **Obsidian**: Cockpit viết nội dung, duyệt link, sửa frontmatter
- **Max runtime**: Đọc file thuần (markdown + yaml), lọc qua logic Python (không cần Obsidian)