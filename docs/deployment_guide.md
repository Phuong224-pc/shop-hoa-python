# HƯỚNG DẪN TRIỂN KHAI PRODUCTION & CHUYỂN ĐỔI POSTGRESQL (FLASK)

Tài liệu này cung cấp quy trình từng bước để đưa hệ thống **FLORA FLOWER** từ môi trường phát triển cục bộ (Local Development với SQLite & Flask Development Server) lên môi trường máy chủ thực tế (Production Server với Ubuntu Linux, Nginx, Gunicorn WSGI và PostgreSQL).

---

## 1. Mô Hình Kiến Trúc Triển Khai (Production Architecture)

```
       [ Client / Web Browser ]
                  │
             HTTPS (Port 443)
                  ▼
        ┌───────────────────┐
        │   Nginx Server    │ ───► Phục vụ trực tiếp Static Files (/static/)
        │  (Reverse Proxy)  │ ───► Phục vụ trực tiếp Media Files (/media/)
        └─────────┬─────────┘
                  │ Unix Socket (/run/floraflower.sock) hoặc HTTP (127.0.0.1:5000)
                  ▼
        ┌───────────────────┐
        │  Gunicorn Server  │ (Chạy Flask WSGI App: "app:create_app('production')")
        └─────────┬─────────┘
                  │ TCP (Port 5432) hoặc File I/O
                  ▼
        ┌───────────────────┐
        │ PostgreSQL Server │ (Cơ sở dữ liệu quan hệ mạnh mẽ, giao dịch ACID)
        │ (hoặc SQLite DB)  │
        └───────────────────┘
```

---

## 2. Chuẩn Bị Môi Trường Máy Chủ (Ubuntu Linux)

### Bước 2.1: Cập nhật hệ điều hành và cài đặt gói phụ thuộc
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-venv python3-pip nginx git -y
```

### Bước 2.2: Sao chép mã nguồn và thiết lập môi trường ảo
```bash
# Đặt mã nguồn tại thư mục chuẩn /var/www/
sudo mkdir -p /var/www/shophoa-python
sudo chown -R $USER:$USER /var/www/shophoa-python

# Clone hoặc giải nén mã nguồn vào thư mục trên
cd /var/www/shophoa-python

# Khởi tạo môi trường ảo Python
python3 -m venv venv
source venv/bin/activate

# Cài đặt danh mục thư viện phụ thuộc
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

---

## 3. Cấu Hình Cơ Sở Dữ Liệu (PostgreSQL hoặc SQLite)

### Lựa chọn A: Sử dụng SQLite (Đơn giản, sẵn có)
Hệ thống mặc định sử dụng SQLite tại file `instance/floraflower.db` hoặc `db.sqlite3`. Đảm bảo quyền ghi:
```bash
chmod 664 db.sqlite3
```

### Lựa chọn B: Chuyển đổi sang PostgreSQL (Khuyến nghị cho Production)
1. **Cài đặt PostgreSQL:**
   ```bash
   sudo apt install postgresql postgresql-contrib libpq-dev -y
   sudo -u postgres psql
   ```
2. **Khởi tạo Database & User:**
   ```sql
   CREATE DATABASE flora_flower_db;
   CREATE USER florashop WITH PASSWORD 'MatKhauBaoMat123@!';
   ALTER ROLE florashop SET client_encoding TO 'utf8';
   ALTER ROLE florashop SET default_transaction_isolation TO 'read committed';
   ALTER ROLE florashop SET timezone TO 'Asia/Ho_Chi_Minh';
   GRANT ALL PRIVILEGES ON DATABASE flora_flower_db TO florashop;
   \q
   ```
3. **Cập nhật chuỗi kết nối trong file `.env`:**
   ```env
   FLASK_ENV=production
   FLASK_APP=run.py
   SECRET_KEY=khoa-bi-mat-rat-dai-va-phuc-tap-cho-production-ngau-nhien-256bit
   DATABASE_URL=postgresql://florashop:MatKhauBaoMat123@!@localhost:5432/flora_flower_db

   # Cấu hình Email Flask-Mail
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   MAIL_DEFAULT_SENDER=Flora Flower <your_email@gmail.com>
   SHOP_NOTIFICATION_EMAIL=phuongtruong121204@gmail.com
   PUBLIC_BASE_URL=https://floraflower.com
   ```
4. **Khởi tạo bảng cơ sở dữ liệu trên PostgreSQL:**
   ```bash
   flask db upgrade
   ```

---

## 4. Chạy Kiểm Thử Trước Khi Khởi Động Service
Trước khi kích hoạt trên môi trường Production, thực hiện chạy toàn bộ test suite để đảm bảo 100% tính năng đạt chuẩn:
```bash
source venv/bin/activate
python -m unittest discover -s tests -p "test_*.py"
# -> Kết quả: Ran 14 tests ... OK (100% Passed)

# Kiểm tra client REST API (CLO3)
python scripts/test_api_client.py
```

---

## 5. Cấu Hình Gunicorn Service (Systemd)

Tạo file dịch vụ hệ thống:
```bash
sudo nano /etc/systemd/system/floraflower.service
```

Nội dung cấu hình:
```ini
[Unit]
Description=Gunicorn instance to serve Flora Flower Flask Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/shophoa-python
Environment="PATH=/var/www/shophoa-python/venv/bin"
EnvironmentFile=/var/www/shophoa-python/.env
ExecStart=/var/www/shophoa-python/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/run/floraflower.sock \
          --access-logfile /var/log/floraflower_access.log \
          --error-logfile /var/log/floraflower_error.log \
          "app:create_app('production')"

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Khởi chạy và kích hoạt service:
```bash
sudo systemctl daemon-reload
sudo systemctl start floraflower
sudo systemctl enable floraflower
sudo systemctl status floraflower
```

---

## 6. Cấu Hình Nginx Reverse Proxy & SSL Let's Encrypt

Tạo file virtual host Nginx:
```bash
sudo nano /etc/nginx/sites-available/floraflower
```

Nội dung cấu hình:
```nginx
server {
    listen 80;
    server_name floraflower.com www.floraflower.com;

    # Giới hạn kích thước upload ảnh hoa và chứng từ ủy nhiệm chi (15MB)
    client_max_body_size 15M;

    # Phục vụ Static Files trực tiếp qua Nginx
    location /static/ {
        alias /var/www/shophoa-python/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Phục vụ Media Files (hình ảnh hoa upload)
    location /media/ {
        alias /var/www/shophoa-python/media/;
        expires 7d;
        add_header Cache-Control "public, no-transform";
    }

    # Chuyển tiếp toàn bộ request động tới Flask qua Unix Socket
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/floraflower.sock;
    }
}
```

Kích hoạt site và khởi động lại Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/floraflower /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Cài đặt chứng chỉ SSL Let's Encrypt miễn phí và bật tự động gia hạn:
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d floraflower.com -d www.floraflower.com
```

---

## 7. Quy Trình Sao Lưu Dữ Liệu Tự Động (Backup & Recovery)

### Kịch bản sao lưu định kỳ (`scripts/backup_db.sh`):
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/floraflower"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p $BACKUP_DIR

# Sao lưu cơ sở dữ liệu SQLite
if [ -f "/var/www/shophoa-python/db.sqlite3" ]; then
    sqlite3 /var/www/shophoa-python/db.sqlite3 ".backup '$BACKUP_DIR/flora_sqlite_$TIMESTAMP.db'"
fi

# Sao lưu PostgreSQL (nếu sử dụng)
if command -v pg_dump &> /dev/null; then
    PGPASSWORD="MatKhauBaoMat123@!" pg_dump -U florashop -h localhost flora_flower_db | gzip > "$BACKUP_DIR/flora_pg_$TIMESTAMP.sql.gz"
fi

# Xóa các bản sao lưu cũ hơn 30 ngày
find $BACKUP_DIR -type f -mtime +30 -exec rm {} \;
```

Thiết lập Cronjob tự động chạy hàng ngày lúc 02:00 sáng:
```bash
crontab -e
# Thêm dòng sau:
0 2 * * * /bin/bash /var/www/shophoa-python/scripts/backup_db.sh
```
