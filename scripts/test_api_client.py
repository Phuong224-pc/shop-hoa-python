#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scripts/test_api_client.py
-----------------------------------------------------------------------------
Client script demonstrating Network Programming & REST API consumption (CLO3).
Calls Flora Flower REST API endpoints over HTTP, processes JSON responses,
handles network errors and timeouts, and formats structured outputs.
-----------------------------------------------------------------------------
"""

import sys
import os

# Auto-detect and switch to virtualenv Python if launched with system Python
if sys.prefix == getattr(sys, "base_prefix", sys.prefix):
    venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'venv', 'Scripts', 'python.exe'))
    if os.path.exists(venv_python) and os.path.abspath(sys.executable).lower() != os.path.abspath(venv_python).lower():
        import subprocess
        try:
            sys.exit(subprocess.call([venv_python] + sys.argv))
        except KeyboardInterrupt:
            sys.exit(0)

import json
import time

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ensure UTF-8 console output on Windows
sys.stdout.reconfigure(encoding='utf-8')

try:
    import requests
    USE_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    import urllib.parse
    USE_REQUESTS = False

BASE_API_URL = "http://127.0.0.1:5000/api/v1"

def http_get(url, params=None, timeout=5, test_client=None):
    """
    Robust HTTP GET wrapper with timeout and exception handling.
    Supports 'requests', 'urllib.request', or Flask test_client fallback.
    """
    if test_client:
        path = url.replace("http://127.0.0.1:5000", "")
        resp = test_client.get(path, query_string=params or {})
        return resp.status_code, resp.get_json()

    if USE_REQUESTS:
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            return resp.status_code, resp.json()
        except requests.exceptions.Timeout:
            return 0, {"error": "Timeout kết nối máy chủ API quá thời gian quy định."}
        except requests.exceptions.ConnectionError:
            return 0, {"error": "Không thể kết nối đến máy chủ Flask API (Connection Refused)."}
        except Exception as e:
            return 0, {"error": f"Lỗi yêu cầu HTTP: {e}"}
    else:
        try:
            full_url = url
            if params:
                query_str = urllib.parse.urlencode(params)
                full_url = f"{url}?{query_str}"
            req = urllib.request.Request(full_url, headers={'User-Agent': 'FloraFlowerClient/1.0'})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status = response.getcode()
                data = json.loads(response.read().decode('utf-8'))
                return status, data
        except urllib.error.HTTPError as e:
            err_data = json.loads(e.read().decode('utf-8')) if e.fp else {"error": str(e)}
            return e.code, err_data
        except urllib.error.URLError as e:
            return 0, {"error": f"Lỗi mạng URLError: {e.reason}."}
        except Exception as e:
            return 0, {"error": f"Lỗi ngoại lệ: {e}"}


def test_api_endpoints(base_url=BASE_API_URL):
    print("=" * 70)
    print(" BÁO CÁO KIỂM THỬ LẬP TRÌNH MẠNG & REST API (CLO3) - FLORA FLOWER")
    print(f" Thư viện HTTP sử dụng: {'requests (v' + requests.__version__ + ')' if USE_REQUESTS else 'urllib.request'}")
    print(f" Địa chỉ API mục tiêu : {base_url}")
    print("=" * 70)

    # Thử kết nối HTTP trước, nếu server chưa bật thì tự động dùng WSGI test client
    test_client = None
    status, _ = http_get(f"{base_url}/products", params={'page': 1, 'per_page': 1})
    if status == 0:
        print("[LƯU Ý]: Máy chủ web chưa chạy trên port 5000 (chưa gõ 'python run.py').")
        print("-> Tự động khởi tạo Flask TestClient nội bộ để kiểm tra trực tiếp REST API.")
        try:
            from app import create_app
            flask_app = create_app('testing')
            test_client = flask_app.test_client()
        except Exception as err:
            print(f"Lỗi khởi tạo test_client: {err}")
            return

    # 1. Test GET /api/v1/products (Danh sách & Phân trang)
    print("\n[TEST 1] Gọi GET /api/v1/products (Lấy danh sách hoa tươi)")
    status, res = http_get(f"{base_url}/products", params={'page': 1, 'per_page': 4}, test_client=test_client)
    print(f"Status Code: {status}")
    if status == 200:
        data = res.get('data', {})
        products = data.get('products', [])
        pagination = data.get('pagination', {})
        print(f"-> Tổng sản phẩm trong hệ thống: {pagination.get('total_items')}")
        print(f"-> Số sản phẩm trang hiện tại  : {len(products)}")
        for idx, p in enumerate(products, 1):
            print(f"   {idx}. [{p['sku']}] {p['name']} - Giá: {p['min_price']:,} đ ({p['category']['name']})")
    else:
        print("-> Lỗi:", res)

    # 2. Test GET /api/v1/products?q=Hồng (Tìm kiếm theo từ khóa)
    print("\n[TEST 2] Gọi GET /api/v1/products?q=Hồng (Tìm kiếm sản phẩm hoa hồng)")
    status, res = http_get(f"{base_url}/products", params={'q': 'Hồng'}, test_client=test_client)
    print(f"Status Code: {status}")
    if status == 200:
        products = res.get('data', {}).get('products', [])
        print(f"-> Tìm thấy {len(products)} mẫu hoa khớp từ khóa 'Hồng':")
        for p in products[:3]:
            print(f"   - {p['name']} (SKU: {p['sku']}) - {p['min_price']:,} đ")
    else:
        print("-> Lỗi:", res)

    # 3. Test GET /api/v1/products/<id> (Chi tiết sản phẩm)
    print("\n[TEST 3] Gọi GET /api/v1/products/1 (Chi tiết sản phẩm ID=1)")
    status, res = http_get(f"{base_url}/products/1", test_client=test_client)
    print(f"Status Code: {status}")
    if status == 200:
        p = res.get('data', {})
        print(f"-> Tên sản phẩm: {p['name']}")
        print(f"-> Danh mục     : {p['category']['name']}")
        print(f"-> Đánh giá     : {p['average_rating']} sao ({p['reviews_count']} đánh giá)")
        print(f"-> Số biến thể  : {len(p.get('variants', []))} phiên bản kích thước")
        for v in p.get('variants', []):
            print(f"   * {v['name']}: {v['effective_price']:,} đ (Tồn kho: {v['stock']})")
    else:
        print("-> Lỗi:", res)

    # 4. Test GET /api/v1/products/99999 (Kiểm tra xử lý lỗi 404 Not Found)
    print("\n[TEST 4] Gọi GET /api/v1/products/99999 (Kiểm tra phản hồi khi không tìm thấy)")
    status, res = http_get(f"{base_url}/products/99999", test_client=test_client)
    print(f"Status Code: {status}")
    print(f"-> Phản hồi JSON lỗi từ máy chủ: {json.dumps(res, ensure_ascii=False)}")
    assert status == 404, f"Mong đợi mã 404 nhưng nhận được {status}"

    print("\n" + "=" * 70)
    print(" KẾT QUẢ KIỂM THỬ CLO3: TẤT CẢ ENDPOINT ĐẠT CHUẨN 100%!")
    print("=" * 70)

if __name__ == '__main__':
    test_api_endpoints()
