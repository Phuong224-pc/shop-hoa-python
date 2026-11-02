import json
from pathlib import Path
from flask import (
    Blueprint, render_template, request, jsonify,
    Response, stream_with_context, session, abort, flash, redirect, url_for
)
from flask_login import current_user
from app.ai.rag import (
    ask_flower_assistant, stream_flower_assistant,
    DOCS_DIR
)
from app.ai.vectorstore import default_vector_store
from app.ai.writing import (
    summarize_description, suggest_hashtags,
    rewrite_boutique_style, translate_description
)
from app.ai.guard import rate_limiter, check_prompt_injection, sanitize_input
from app.ai.forms import AiAskForm, AiSearchForm
from app.models.catalog import Product

bp = Blueprint('ai', __name__, url_prefix='/ai')

def get_client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr or '127.0.0.1').split(',')[0].strip()

# -------------------------------------------------------------
# 1. CUSTOMER FLOWER CONSULTANT (RAG)
# -------------------------------------------------------------
@bp.route('/assistant', methods=['GET', 'POST'])
def assistant():
    form = AiAskForm()
    history = session.get('ai_chat_history', [])

    if request.method == 'POST':
        client_key = get_client_ip()
        allowed, retry_after = rate_limiter.is_allowed(client_key)
        if not allowed:
            return jsonify({
                'success': False,
                'error': f'Bạn đã gửi quá nhiều yêu cầu trong thời gian ngắn. Vui lòng thử lại sau {retry_after} giây.'
            }), 429

        raw_query = request.form.get('query') or (request.get_json(silent=True) or {}).get('query', '')
        query = sanitize_input(raw_query)

        if not query:
            return jsonify({'success': False, 'error': 'Vui lòng nhập nội dung câu hỏi.'}), 400

        is_safe, warning = check_prompt_injection(query)
        if not is_safe:
            return jsonify({'success': False, 'error': warning}), 400

        try:
            result = ask_flower_assistant(query, history=history)

            # Update history (keep last 6 turns)
            history.append({'role': 'user', 'content': query})
            history.append({'role': 'assistant', 'content': result['answer']})
            session['ai_chat_history'] = history[-6:]

            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'answer': result['answer'],
                    'citations': result['citations'],
                    'products': result['products']
                })

            return render_template('ai/assistant.html', form=form, history=history, latest_result=result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    return render_template('ai/assistant.html', form=form, history=history)


@bp.route('/assistant/stream')
def assistant_stream():
    """
    Server-Sent Events (SSE) streaming endpoint for Gemini AI responses.
    """
    client_key = get_client_ip()
    allowed, retry_after = rate_limiter.is_allowed(client_key)
    if not allowed:
        def err_gen():
            yield f"data: {json.dumps({'type': 'error', 'message': f'Quá nhiều yêu cầu. Vui lòng đợi {retry_after} giây.'})}\n\n"
        return Response(err_gen(), mimetype='text/event-stream')

    raw_query = request.args.get('query', '').strip()
    query = sanitize_input(raw_query)
    if not query:
        def empty_gen():
            yield f"data: {json.dumps({'type': 'error', 'message': 'Vui lòng nhập nội dung cần hỏi.'})}\n\n"
        return Response(empty_gen(), mimetype='text/event-stream')

    is_safe, warning = check_prompt_injection(query)
    if not is_safe:
        def unsafe_gen():
            yield f"data: {json.dumps({'type': 'error', 'message': warning})}\n\n"
        return Response(unsafe_gen(), mimetype='text/event-stream')

    history = session.get('ai_chat_history', [])

    def event_stream():
        full_text = []
        try:
            for item in stream_flower_assistant(query, history=history):
                if item.get('type') == 'text':
                    full_text.append(item.get('content', ''))
                yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"

            # Save completed turn to session history
            history.append({'role': 'user', 'content': query})
            history.append({'role': 'assistant', 'content': "".join(full_text)})
            session['ai_chat_history'] = history[-6:]
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return Response(stream_with_context(event_stream()), mimetype='text/event-stream')


@bp.route('/assistant/clear', methods=['POST'])
def clear_history():
    session.pop('ai_chat_history', None)
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Đã làm mới đoạn hội thoại.'})
    flash('Đã làm mới đoạn hội thoại tư vấn.', 'info')
    return redirect(url_for('ai.assistant'))


# -------------------------------------------------------------
# 2. SMART HYBRID PRODUCT SEARCH
# -------------------------------------------------------------
@bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    in_stock = request.args.get('in_stock') == '1'
    category_id = request.args.get('category_id', type=int)

    results = []
    if q:
        results = default_vector_store.hybrid_search(
            query=q,
            source_filter='product',
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            in_stock_only=in_stock,
            alpha=0.65,
            top_k=12
        )

    if request.args.get('format') == 'json' or request.is_json:
        return jsonify({
            'query': q,
            'total': len(results),
            'results': [
                {
                    'id': r['product_id'],
                    'title': r['title'],
                    'score': r['score'],
                    'metadata': r['metadata']
                } for r in results
            ]
        })

    return render_template(
        'ai/search.html',
        query=q,
        results=results,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock
    )


# -------------------------------------------------------------
# 3. ADMIN WRITING TOOLS
# -------------------------------------------------------------
@bp.route('/post-tool/summarize', methods=['POST'])
def tool_summarize():
    if not current_user.is_authenticated or not current_user.is_store_staff():
        abort(403)
    text = request.form.get('text') or (request.get_json(silent=True) or {}).get('text', '')
    if not text.strip():
        return jsonify({'success': False, 'error': 'Vui lòng cung cấp mô tả gốc.'}), 400
    try:
        summary = summarize_description(text)
        return jsonify({'success': True, 'result': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/post-tool/hashtags', methods=['POST'])
def tool_hashtags():
    if not current_user.is_authenticated or not current_user.is_store_staff():
        abort(403)
    data = request.get_json(silent=True) or request.form
    text = data.get('text', '')
    name = data.get('name', '')
    try:
        tags = suggest_hashtags(text, product_name=name)
        return jsonify({'success': True, 'result': " ".join(tags), 'tags': tags})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/post-tool/rewrite', methods=['POST'])
def tool_rewrite():
    if not current_user.is_authenticated or not current_user.is_store_staff():
        abort(403)
    data = request.get_json(silent=True) or request.form
    text = data.get('text', '')
    style = data.get('style', 'thơ mộng, sang trọng')
    try:
        rewritten = rewrite_boutique_style(text, style=style)
        return jsonify({'success': True, 'result': rewritten})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/post-tool/translate', methods=['POST'])
def tool_translate():
    if not current_user.is_authenticated or not current_user.is_store_staff():
        abort(403)
    data = request.get_json(silent=True) or request.form
    text = data.get('text', '')
    target_lang = data.get('target_lang', 'tiếng Anh')
    try:
        translated = translate_description(text, target_lang=target_lang)
        return jsonify({'success': True, 'result': translated})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# -------------------------------------------------------------
# 4. VIEW POLICY DOCS
# -------------------------------------------------------------
@bp.route('/docs/<filename>')
def view_doc(filename):
    safe_name = Path(filename).name
    file_path = DOCS_DIR / safe_name
    if not file_path.exists() or not safe_name.endswith('.md'):
        abort(404)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return render_template('ai/doc_view.html', filename=safe_name, content=content)

