from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.catalog import Product, ProductVariant, Category, Occasion

bp = Blueprint('api', __name__, url_prefix='/api/v1')

@bp.errorhandler(404)
def api_not_found(error):
    return jsonify({
        'status': 'error',
        'code': 404,
        'message': 'Tài nguyên yêu cầu không tồn tại.'
    }), 404

@bp.errorhandler(500)
def api_server_error(error):
    return jsonify({
        'status': 'error',
        'code': 500,
        'message': 'Đã xảy ra lỗi nội bộ máy chủ khi xử lý yêu cầu API.'
    }), 500


@bp.route('/products', methods=['GET'])
def get_products():
    """
    REST API endpoint to search, filter, and paginate published flower products.
    CLO3 demonstration: JSON data interchange over HTTP.
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 50)
        if page < 1 or per_page < 1:
            raise ValueError()
    except ValueError:
        return jsonify({
            'status': 'error',
            'code': 400,
            'message': 'Tham số phân trang page hoặc per_page không hợp lệ.'
        }), 400

    query = Product.query.filter_by(status='PUBLISHED')

    # Keyword search
    q = request.args.get('q', '').strip()
    if q:
        query = query.filter(
            (Product.name.ilike(f"%{q}%")) |
            (Product.sku.ilike(f"%{q}%")) |
            (Product.short_description.ilike(f"%{q}%"))
        )

    # Category filter
    category_slug = request.args.get('category', '').strip()
    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            query = query.filter_by(primary_category_id=cat.id)
        else:
            return jsonify({
                'status': 'success',
                'data': {
                    'products': [],
                    'pagination': {
                        'total_items': 0,
                        'total_pages': 0,
                        'current_page': page,
                        'per_page': per_page,
                        'has_next': False,
                        'has_prev': False
                    }
                }
            }), 200

    # Occasion filter
    occasion_slug = request.args.get('occasion', '').strip()
    if occasion_slug:
        occ = Occasion.query.filter_by(slug=occasion_slug).first()
        if occ:
            query = query.filter(Product.occasions.any(id=occ.id))

    # Price range
    try:
        min_p = request.args.get('min_price')
        max_p = request.args.get('max_price')
        if min_p is not None:
            query = query.join(ProductVariant).filter(ProductVariant.price >= float(min_p))
        if max_p is not None:
            query = query.join(ProductVariant).filter(ProductVariant.price <= float(max_p))
    except ValueError:
        return jsonify({
            'status': 'error',
            'code': 400,
            'message': 'Tham số min_price hoặc max_price phải là giá trị số.'
        }), 400

    # Sorting
    sort = request.args.get('sort', 'newest')
    if sort == 'price_asc':
        query = query.join(ProductVariant).filter_by(is_default=True).order_by(ProductVariant.price.asc())
    elif sort == 'price_desc':
        query = query.join(ProductVariant).filter_by(is_default=True).order_by(ProductVariant.price.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    query = query.distinct()
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    base_url = current_app.config.get('PUBLIC_BASE_URL', 'http://127.0.0.1:5000')

    product_list = []
    for p in pagination.items:
        product_list.append({
            'id': p.id,
            'name': p.name,
            'sku': p.sku,
            'slug': p.slug,
            'category': {
                'id': p.primary_category.id if p.primary_category else None,
                'name': p.primary_category.name if p.primary_category else None,
                'slug': p.primary_category.slug if p.primary_category else None
            },
            'presentation_style': p.presentation_style,
            'color_tone': p.color_tone,
            'short_description': p.short_description,
            'min_price': float(p.min_price),
            'max_price': float(p.max_price),
            'in_stock': p.in_stock,
            'total_stock': p.total_stock,
            'average_rating': float(p.average_rating),
            'reviews_count': p.approved_reviews_count,
            'image_url': f"{base_url}{p.main_image_url}" if p.main_image_url.startswith('/') else p.main_image_url
        })

    return jsonify({
        'status': 'success',
        'data': {
            'products': product_list,
            'pagination': {
                'total_items': pagination.total,
                'total_pages': pagination.pages,
                'current_page': pagination.page,
                'per_page': pagination.per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
    }), 200


@bp.route('/products/<int:id>', methods=['GET'])
def get_product_detail(id):
    """
    REST API endpoint returning detailed public specification of a flower product.
    """
    p = db.session.get(Product, id)
    if not p or p.status == 'ARCHIVED':
        return jsonify({
            'status': 'error',
            'code': 404,
            'message': f'Không tìm thấy sản phẩm hoa với ID = {id}.'
        }), 404

    base_url = current_app.config.get('PUBLIC_BASE_URL', 'http://127.0.0.1:5000')

    variants_data = []
    for v in p.variants.all():
        variants_data.append({
            'id': v.id,
            'name': v.name,
            'size_code': v.size_code,
            'sku': v.sku,
            'price': float(v.price),
            'sale_price': float(v.sale_price) if v.sale_price else None,
            'effective_price': float(v.effective_price),
            'stock': v.stock,
            'is_default': v.is_default
        })

    images_data = []
    for img in p.gallery_images.all():
        images_data.append({
            'id': img.id,
            'alt_text': img.alt_text,
            'image_url': f"{base_url}{img.image_url}" if img.image_url.startswith('/') else img.image_url
        })

    return jsonify({
        'status': 'success',
        'data': {
            'id': p.id,
            'name': p.name,
            'sku': p.sku,
            'slug': p.slug,
            'category': {
                'id': p.primary_category.id if p.primary_category else None,
                'name': p.primary_category.name if p.primary_category else None,
                'slug': p.primary_category.slug if p.primary_category else None
            },
            'presentation_style': p.presentation_style,
            'color_tone': p.color_tone,
            'short_description': p.short_description,
            'description': p.description,
            'flower_composition': p.flower_composition,
            'care_instructions': p.care_instructions,
            'seasonal_policy_notes': p.seasonal_policy_notes,
            'in_stock': p.in_stock,
            'total_stock': p.total_stock,
            'average_rating': float(p.average_rating),
            'reviews_count': p.approved_reviews_count,
            'main_image_url': f"{base_url}{p.main_image_url}" if p.main_image_url.startswith('/') else p.main_image_url,
            'variants': variants_data,
            'gallery_images': images_data
        }
    }), 200
