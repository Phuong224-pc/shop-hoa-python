import sys
import click

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from flask.cli import AppGroup
from app.ai.rag import (
    index_all_docs, index_all_products,
    ask_flower_assistant, stream_flower_assistant
)
from app.models.ai import AiChunk

ai_cli = AppGroup('ai', help='Lệnh quản lý hệ thống AI và RAG của Flora Flower')

@ai_cli.command('index-docs')
def cmd_index_docs():
    """Đánh chỉ mục toàn bộ tài liệu chính sách cửa hàng (Markdown)."""
    click.echo("Đang nạp và trích xuất vector cho tài liệu chính sách...")
    count = index_all_docs()
    click.echo(f"Hoàn tất! Đã tạo thành công {count} chunks tài liệu chính sách.")

@ai_cli.command('index-products')
@click.option('--rebuild', is_flag=True, help='Xóa chỉ mục sản phẩm cũ và lập lại từ đầu')
def cmd_index_products(rebuild):
    """Đánh chỉ mục toàn bộ sản phẩm hoa tươi đang bán."""
    click.echo(f"Đang sinh vector cho sản phẩm hoa (rebuild={rebuild})...")
    count = index_all_products(rebuild=rebuild)
    click.echo(f"Hoàn tất! Đã đánh chỉ mục cho {count} sản phẩm hoa tươi.")

@ai_cli.command('stats')
def cmd_stats():
    """Xem thống kê chỉ mục vectorstore hiện tại."""
    total = AiChunk.query.count()
    doc_count = AiChunk.query.filter_by(source='doc').count()
    prod_count = AiChunk.query.filter_by(source='product').count()
    click.echo("=== THỐNG KÊ VECTORSTORE FLORA FLOWER ===")
    click.echo(f"Tổng số chunks đã index : {total}")
    click.echo(f"- Chunks tài liệu shop  : {doc_count}")
    click.echo(f"- Chunks sản phẩm hoa   : {prod_count}")

@ai_cli.command('ask')
@click.argument('question')
@click.option('--stream', is_flag=True, help='Stream câu trả lời từng từ một')
def cmd_ask(question, stream):
    """Đặt câu hỏi trực tiếp cho Trợ lý AI từ terminal."""
    click.echo(f"\n[Khách hàng]: {question}\n[Trợ lý Flora]:")
    if stream:
        for chunk in stream_flower_assistant(question):
            if chunk.get('type') == 'text':
                click.echo(chunk.get('content', ''), nl=False)
            elif chunk.get('type') == 'meta':
                click.echo(f"\n\n[Trích dẫn]: {len(chunk.get('citations', []))} nguồn")
                for c in chunk.get('citations', []):
                    click.echo(f"  [{c['index']}] {c['title']}")
        click.echo("")
    else:
        res = ask_flower_assistant(question)
        click.echo(res['answer'])
        if res.get('citations'):
            click.echo(f"\n[Trích dẫn]: {len(res['citations'])} nguồn")
            for c in res['citations']:
                click.echo(f"  [{c['index']}] {c['title']}")
