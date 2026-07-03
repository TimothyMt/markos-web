# Brain Vault Convention

## 4 Loại Note
- **frameworks**: Framework marketing ứng dụng cho nhiều ngành
- **industries**: Kiến trúc ngành cụ thể (d2c-skincare, b2b-saas)
- **craft**: Kỹ năng thực tactical (copywriting, cro-campaign)
- **stages**: Định giai đoạn khách hàng (awareness, consideration, conversion)

## Quy Tác Đặt Tên
- **Slug**: kebab-case (ví dụ: `d2c-skincare`, `copywriting-framework`)
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