from app.extensions import db
from app.models.catalog import ProductVariant
from app.models.inventory import StockTransaction

def record_order_sale(order):
    """Decrements stock and writes audit log for each purchased item."""
    for item in order.items:
        if item.product_variant_id:
            variant = db.session.get(ProductVariant, item.product_variant_id)
            if variant:
                old_stock = variant.stock
                new_stock = max(0, old_stock - item.quantity)
                variant.stock = new_stock

                txn = StockTransaction(
                    variant_id=variant.id,
                    transaction_type='SALE',
                    quantity_change=-item.quantity,
                    balance_after=new_stock,
                    reason=f"Đơn hàng #{order.order_number}",
                    reference_order_id=order.id
                )
                db.session.add(txn)
    db.session.commit()


def record_order_cancellation(order, performed_by=None, reason=''):
    """Restores stock for each purchased item when order is cancelled."""
    for item in order.items:
        if item.product_variant_id:
            variant = db.session.get(ProductVariant, item.product_variant_id)
            if variant:
                old_stock = variant.stock
                new_stock = old_stock + item.quantity
                variant.stock = new_stock

                txn = StockTransaction(
                    variant_id=variant.id,
                    transaction_type='CANCEL_RESTORE',
                    quantity_change=item.quantity,
                    balance_after=new_stock,
                    reason=f"Hoàn tồn do hủy đơn #{order.order_number}: {reason}",
                    performed_by_id=performed_by.id if performed_by else None,
                    reference_order_id=order.id
                )
                db.session.add(txn)
    db.session.commit()
