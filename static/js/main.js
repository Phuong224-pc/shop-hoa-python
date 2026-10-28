/**
 * Flora Flower Boutique - Main Frontend JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Tự động đóng thông báo flash sau 5 giây
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // 2. Xử lý yêu thích sản phẩm qua AJAX
    const wishlistBtns = document.querySelectorAll('.btn-wishlist-toggle');
    wishlistBtns.forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            const icon = this.querySelector('i');

            fetch(`/accounts/wishlist/toggle/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => {
                if (res.redirected) {
                    window.location.href = res.url;
                    return null;
                }
                return res.json();
            })
            .then(data => {
                if (!data) return;
                if (data.success) {
                    if (data.is_favorite) {
                        btn.classList.add('active');
                        if (icon) {
                            icon.classList.remove('bi-heart');
                            icon.classList.add('bi-heart-fill');
                        }
                    } else {
                        btn.classList.remove('active');
                        if (icon) {
                            icon.classList.remove('bi-heart-fill');
                            icon.classList.add('bi-heart');
                        }
                    }
                    showToast(data.message, 'success');
                }
            })
            .catch(err => console.error(err));
        });
    });

    // 3. Xử lý chọn biến thể sản phẩm trên trang chi tiết
    const variantInputs = document.querySelectorAll('input[name="variant_id"]');
    const displayPriceEl = document.getElementById('product-display-price');
    const displayOriginalPriceEl = document.getElementById('product-original-price');
    const displayStockEl = document.getElementById('product-display-stock');
    const displaySkuEl = document.getElementById('product-display-sku');

    variantInputs.forEach(function (input) {
        input.addEventListener('change', function () {
            if (this.checked) {
                const price = this.getAttribute('data-price');
                const salePrice = this.getAttribute('data-sale-price');
                const stock = this.getAttribute('data-stock');
                const sku = this.getAttribute('data-sku');

                if (displaySkuEl) displaySkuEl.textContent = sku;
                if (displayStockEl) displayStockEl.textContent = stock;

                if (salePrice && parseInt(salePrice) > 0 && parseInt(salePrice) < parseInt(price)) {
                    if (displayPriceEl) displayPriceEl.textContent = formatVND(salePrice);
                    if (displayOriginalPriceEl) {
                        displayOriginalPriceEl.textContent = formatVND(price);
                        displayOriginalPriceEl.style.display = 'inline';
                    }
                } else {
                    if (displayPriceEl) displayPriceEl.textContent = formatVND(price);
                    if (displayOriginalPriceEl) displayOriginalPriceEl.style.display = 'none';
                }
            }
        });
    });

    // 4. Thư viện ảnh sản phẩm (Click thumbnail đổi ảnh chính)
    const thumbs = document.querySelectorAll('.detail-gallery-thumb');
    const mainImg = document.getElementById('main-gallery-img');
    thumbs.forEach(function (thumb) {
        thumb.addEventListener('click', function () {
            thumbs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            const targetSrc = this.getAttribute('data-full-src');
            if (mainImg && targetSrc) {
                mainImg.src = targetSrc;
            }
        });
    });
});

// Helper lấy CSRF token từ Cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Định dạng tiền tệ VND
function formatVND(val) {
    try {
        return parseInt(val).toLocaleString('vi-VN') + ' ₫';
    } catch (e) {
        return val + ' ₫';
    }
}

// Hiển thị toast thông báo nhanh
function showToast(msg, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-bg-${type === 'success' ? 'success' : 'dark'} border-0 mb-2`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi bi-info-circle me-1"></i> ${msg}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    container.appendChild(toastEl);
    const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
    toast.show();
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}
