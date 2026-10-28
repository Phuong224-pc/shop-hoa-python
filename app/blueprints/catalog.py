from flask import Blueprint, render_template, request, abort
from app.extensions import db
from app.models.catalog import Product, ProductVariant, Category, Occasion, Accessory, ProductImage
from app.forms.catalog import SearchForm

bp = Blueprint('catalog', __name__)

@bp.route('/products')
def product_list():
    form = SearchForm(request.args)
    page = request.args.get('page', 1, type=int)
    per_page = 12

    # Query only PUBLISHED products for client
    query = Product.query.filter_by(status='PUBLISHED')

    # Keyword search (Product name, SKU, or Description)
    q = request.args.get('q', '').strip()
    if q:
        query = query.filter(
            (Product.name.ilike(f"%{q}%")) |
            (Product.sku.ilike(f"%{q}%")) |
            (Product.short_description.ilike(f"%{q}%")) |
            (Product.flower_composition.ilike(f"%{q}%"))
        )

    # Category filter
    category_slug = request.args.get('category', '').strip()
    current_category = None
    if category_slug:
        current_category = Category.query.filter_by(slug=category_slug).first()
        if current_category:
            query = query.filter_by(primary_category_id=current_category.id)

    # Occasion filter
    occasion_slug = request.args.get('occasion', '').strip()
    current_occasion = None
    if occasion_slug:
        current_occasion = Occasion.query.filter_by(slug=occasion_slug).first()
        if current_occasion:
            query = query.filter(Product.occasions.any(id=current_occasion.id))

    # Price range
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    if min_price is not None:
        query = query.join(ProductVariant).filter(ProductVariant.price >= min_price)
    if max_price is not None:
        query = query.join(ProductVariant).filter(ProductVariant.price <= max_price)

    # Sorting
    sort = request.args.get('sort', 'newest')
    if sort == 'price_asc':
        query = query.join(ProductVariant).filter_by(is_default=True).order_by(ProductVariant.price.asc())
    elif sort == 'price_desc':
        query = query.join(ProductVariant).filter_by(is_default=True).order_by(ProductVariant.price.desc())
    elif sort == 'bestseller':
        query = query.order_by(Product.is_bestseller_manual.desc(), Product.created_at.desc())
    else:  # newest
        query = query.order_by(Product.created_at.desc())

    # Eliminate duplicate joins
    query = query.distinct()

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    categories = Category.query.filter_by(is_active=True).order_by(Category.display_order.asc()).all()
    occasions = Occasion.query.filter_by(is_active=True).order_by(Occasion.display_order.asc()).all()
    from app.models.catalog import FlowerType
    flower_types = FlowerType.query.filter_by(is_active=True).all()

    # Provide Django-compatible pagination properties
    class PageObjCompat:
        def __init__(self, p):
            self.p = p
            self.has_other_pages = p.pages > 1
            self.has_previous = p.has_prev
            self.previous_page_number = p.prev_num or 1
            self.has_next = p.has_next
            self.next_page_number = p.next_num or p.pages
            self.number = p.page
            self.paginator = type('Paginator', (), {
                'page_range': list(range(1, p.pages + 1))
            })()

        def __iter__(self):
            return iter(self.p.items)

        def __len__(self):
            return len(self.p.items)

    page_obj = PageObjCompat(pagination)

    return render_template(
        'shop/product_list.html',
        products=products,
        pagination=pagination,
        page_obj=page_obj,
        categories=categories,
        occasions=occasions,
        flower_types=flower_types,
        current_category=current_category,
        selected_category=current_category,
        current_occasion=current_occasion,
        selected_occasion=current_occasion,
        selected_flower_type=None,
        q=q,
        sort=sort,
        form=form
    )


@bp.route('/products/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    if product.status == 'ARCHIVED':
        abort(404)

    variants = product.variants.order_by(ProductVariant.price.asc()).all()
    default_variant = product.default_variant
    images = product.gallery_images.order_by(ProductImage.display_order.asc()).all()
    accessories = Accessory.query.filter_by(is_active=True).order_by(Accessory.display_order.asc()).all()
    related_products = Product.query.filter(
        Product.primary_category_id == product.primary_category_id,
        Product.id != product.id,
        Product.status == 'PUBLISHED'
    ).limit(4).all()

    from flask_login import current_user
    from app.forms.review import ReviewForm

    reviews = product.reviews.filter_by(status='APPROVED').all()
    is_favorited = False
    if current_user.is_authenticated:
        is_favorited = current_user.wishlist_items.filter_by(product_id=product.id).first() is not None

    review_form = ReviewForm()
    can_review = current_user.is_authenticated

    return render_template(
        'shop/product_detail.html',
        product=product,
        variants=variants,
        default_variant=default_variant,
        images=images,
        accessories=accessories,
        related_products=related_products,
        reviews=reviews,
        is_favorited=is_favorited,
        review_form=review_form,
        can_review=can_review
    )


@bp.route('/category/<slug>')
def category_detail(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    return product_list()


@bp.route('/occasion/<slug>')
def occasion_detail(slug):
    occasion = Occasion.query.filter_by(slug=slug).first_or_404()
    return product_list()
