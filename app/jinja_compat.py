import json
from decimal import Decimal
from datetime import datetime
from jinja2 import nodes
from jinja2.ext import Extension
from flask import url_for, current_app
from markupsafe import Markup

# Route mapping from legacy names to Flask blueprint endpoints
URL_MAP = {
    'accounts:login': 'auth.login',
    'accounts:register': 'auth.register',
    'accounts:logout': 'auth.logout',
    'accounts:profile': 'auth.profile',
    'accounts:addresses': 'auth.addresses',
    'accounts:address_add': 'auth.addresses',
    'accounts:address_delete': 'auth.delete_address',
    'accounts:address_set_default': 'auth.addresses',
    'accounts:wishlist': 'auth.wishlist',
    'accounts:orders': 'orders.my_orders',
    'accounts:password_change': 'auth.request_reset',
    'catalog:home': 'main.index',
    'catalog:product_list': 'catalog.product_list',
    'catalog:product_detail': 'catalog.product_detail',
    'catalog:category_detail': 'catalog.category_detail',
    'catalog:occasion_detail': 'catalog.occasion_detail',
    'catalog:flower_type_detail': 'catalog.product_list',
    'content:about': 'main.about',
    'content:contact': 'main.contact',
    'content:policy': 'main.policy',
    'cart:cart_detail': 'cart.view_cart',
    'cart:add_to_cart': 'cart.add_cart_item',
    'cart:update_cart_item': 'cart.update_cart_item',
    'cart:remove_cart_item': 'cart.remove_cart_item',
    'cart:apply_coupon': 'cart.apply_coupon',
    'cart:remove_coupon': 'cart.remove_coupon',
    'orders:checkout': 'orders.checkout',
    'orders:tracking': 'orders.tracking',
    'orders:order_detail': 'orders.detail',
    'orders:cancel_order': 'orders.cancel_order',
    'orders:reorder': 'orders.reorder',
    'payments:upload_proof': 'orders.upload_proof',
    'payments:view_proof': 'dashboard.view_proof',
    'reviews:add_review': 'reviews.submit_review',
    'dashboard:overview': 'dashboard.overview',
    'dashboard:product_list': 'dashboard.product_list',
    'dashboard:product_create': 'dashboard.product_create',
    'dashboard:product_edit': 'dashboard.product_edit',
    'dashboard:product_delete': 'dashboard.product_delete',
    'dashboard:product_toggle_status': 'dashboard.product_toggle_status',
    'dashboard:product_variant_save': 'dashboard.product_variant_save',
    'dashboard:product_variant_delete': 'dashboard.product_variant_delete',
    'dashboard:product_image_delete': 'dashboard.product_list',
    'dashboard:category_list': 'dashboard.categories',
    'dashboard:category_save': 'dashboard.categories',
    'dashboard:accessory_list': 'dashboard.accessories',
    'dashboard:accessory_save': 'dashboard.accessories',
    'dashboard:order_list': 'dashboard.order_list',
    'dashboard:order_detail': 'dashboard.order_detail',
    'dashboard:order_print_bill': 'dashboard.print_bill',
    'dashboard:order_print_florist': 'dashboard.print_florist',
    'dashboard:delivery_calendar': 'dashboard.delivery_calendar',
    'dashboard:inventory_list': 'dashboard.inventory_list',
    'dashboard:inventory_adjust': 'dashboard.inventory_adjust',
    'dashboard:inventory_import': 'dashboard.inventory_import',
    'dashboard:payment_list': 'dashboard.payment_list',
    'dashboard:payment_verify': 'dashboard.payment_verify',
    'dashboard:payment_refund': 'dashboard.payment_refund',
    'dashboard:review_list': 'dashboard.review_list',
    'dashboard:review_moderate': 'dashboard.review_moderate',
    'dashboard:customer_list': 'dashboard.customer_list',
    'dashboard:customer_detail': 'dashboard.customer_detail',
    'dashboard:customer_toggle_lock': 'dashboard.customer_toggle_lock',
    'dashboard:staff_list': 'dashboard.staff_list',
    'dashboard:staff_save': 'dashboard.staff_list',
    'dashboard:settings': 'dashboard.settings',
    'dashboard:contact_message_list': 'dashboard.contact_message_list',
    'dashboard:contact_message_update': 'dashboard.contact_message_update',
    'dashboard:promotion_list': 'dashboard.promotion_list',
    'dashboard:promotion_save': 'dashboard.promotion_save',
    'dashboard:audit_logs': 'dashboard.logs',
    'dashboard:export_orders_csv': 'dashboard.export_csv',
}

def resolve_url(name, **kwargs):
    endpoint = URL_MAP.get(name, name)
    # Map pk or other id aliases to id if needed
    if 'pk' in kwargs and 'id' not in kwargs:
        kwargs['id'] = kwargs.pop('pk')
    if 'transaction_id' in kwargs and 'id' not in kwargs:
        kwargs['id'] = kwargs.pop('transaction_id')
    if 'variant_id' in kwargs and 'id' not in kwargs:
        kwargs['id'] = kwargs.pop('variant_id')
    try:
        return url_for(endpoint, **kwargs)
    except Exception:
        # Fallback to direct path or anchor
        return f"#{name}"


class DjangoCompatExtension(Extension):
    tags = {'load', 'csrf_token', 'url', 'static', 'query_transform'}

    def parse(self, parser):
        token = parser.stream.current
        tag_name = token.value
        lineno = token.lineno
        next(parser.stream)  # consume tag

        if tag_name == 'load':
            # Consume everything until block_end '%}'
            while parser.stream.current.type != 'block_end':
                next(parser.stream)
            return []

        elif tag_name == 'csrf_token':
            call = self.call_method('_render_csrf', [], lineno=lineno)
            return nodes.Output([call], lineno=lineno)

        elif tag_name == 'static':
            path_expr = parser.parse_expression()
            call = self.call_method('_render_static', [path_expr], lineno=lineno)
            return nodes.Output([call], lineno=lineno)

        elif tag_name == 'query_transform':
            args = []
            kwargs = []
            while parser.stream.current.type != 'block_end':
                if parser.stream.current.type == 'name' and parser.stream.look().type == 'assign':
                    key = parser.stream.current.value
                    next(parser.stream)  # name
                    next(parser.stream)  # assign
                    val = parser.parse_expression()
                    kwargs.append(nodes.Keyword(key, val))
                else:
                    args.append(parser.parse_expression())
            call = self.call_method('_render_query_transform', args, kwargs, lineno=lineno)
            return nodes.Output([call], lineno=lineno)

        elif tag_name == 'url':
            name_expr = parser.parse_expression()
            args = []
            kwargs = []
            while parser.stream.current.type != 'block_end':
                if parser.stream.current.type == 'name' and parser.stream.look().type == 'assign':
                    key = parser.stream.current.value
                    next(parser.stream)  # name
                    next(parser.stream)  # assign
                    val = parser.parse_expression()
                    kwargs.append(nodes.Keyword(key, val))
                elif parser.stream.current.type == 'comma':
                    next(parser.stream)
                else:
                    args.append(parser.parse_expression())

            call = self.call_method('_render_url', [name_expr], kwargs, lineno=lineno)
            return nodes.Output([call], lineno=lineno)

        return []

    def _render_csrf(self):
        from flask_wtf.csrf import generate_csrf
        token = generate_csrf()
        return Markup(f'<input type="hidden" name="csrf_token" value="{token}">')

    def _render_static(self, path):
        return url_for('static', filename=path)

    def _render_url(self, name, **kwargs):
        return resolve_url(name, **kwargs)

    def _render_query_transform(self, **kwargs):
        from flask import request
        from urllib.parse import urlencode
        query_dict = request.args.to_dict()
        for k, v in kwargs.items():
            query_dict[k] = v
        return '?' + urlencode(query_dict) if query_dict else '?'


def register_filters_and_extensions(app):
    app.jinja_env.add_extension(DjangoCompatExtension)

    def filter_add(val, arg):
        try:
            return int(val) + int(arg)
        except Exception:
            return f"{val}{arg}"

    def filter_floatformat(val, arg=2):
        try:
            return f"{float(val):.{int(arg)}f}"
        except Exception:
            return val

    def filter_json_script(val, el_id):
        raw = json.dumps(val, ensure_ascii=False)
        return Markup(f'<script id="{el_id}" type="application/json">{raw}</script>')

    def filter_make_list(val):
        return list(val) if val else []

    def filter_stringformat(val, fmt):
        try:
            return fmt % val
        except Exception:
            return str(val)

    def filter_truncatechars(val, length):
        val = str(val or '')
        return val[:length] + '...' if len(val) > length else val

    def filter_truncatewords(val, count):
        val = str(val or '')
        words = val.split()
        return ' '.join(words[:count]) + '...' if len(words) > count else val

    def filter_slice(val, arg):
        if not val:
            return []
        if isinstance(arg, str) and ':' in arg:
            parts = arg.split(':')
            start = int(parts[0]) if parts[0] else None
            end = int(parts[1]) if len(parts) > 1 and parts[1] else None
            return list(val)[start:end]
        try:
            return list(val)[:int(arg)]
        except Exception:
            return list(val)

    app.jinja_env.filters['slice'] = filter_slice
    app.jinja_env.filters['add'] = filter_add
    app.jinja_env.filters['floatformat'] = filter_floatformat
    app.jinja_env.filters['json_script'] = filter_json_script
    app.jinja_env.filters['make_list'] = filter_make_list
    app.jinja_env.filters['stringformat'] = filter_stringformat
    app.jinja_env.filters['truncatechars'] = filter_truncatechars
    app.jinja_env.filters['truncatewords'] = filter_truncatewords
