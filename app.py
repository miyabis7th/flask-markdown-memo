from flask import Flask, render_template, request, redirect, url_for, abort
import markdown
import os
from flask_sqlalchemy import SQLAlchemy
from models import db, Memo, Tag

app = Flask(__name__)

# Render用のPostgreSQL接続設定
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# アプリケーションコンテキスト内でデータベースのテーブルを作成
with app.app_context():
    db.create_all()
    
# タグを処理するヘルパー関数
def process_tags(tag_input):
    if not tag_input:
        return []
    
    # カンマで区切られたタグを分割
    tag_names = [tag.strip() for tag in tag_input.split(',') if tag.strip()]
    tags = []
    
    for tag_name in tag_names:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        tags.append(tag)
    
    return tags

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        memo = request.form.get('memo')
        tag_input = request.form.get('tags', '')
        
        if memo:
            new_memo = Memo(content=memo)
            tags = process_tags(tag_input)
            new_memo.tags = tags
            db.session.add(new_memo)
            db.session.commit()
        return redirect(url_for('index'))
    
    tag_filter = request.args.get('tag')
    if tag_filter:
        tag = Tag.query.filter_by(name=tag_filter).first_or_404()
        memos = tag.memos
    else:
        memos = Memo.query.order_by(Memo.id.desc()).all()
        
    rendered_memos = [(m.id, markdown.markdown(m.content), m.tags) for m in memos]
    all_tags = Tag.query.all()
    return render_template('index.html', memos=rendered_memos, all_tags=all_tags, current_tag=tag_filter)

@app.route('/memo/<int:memo_id>')
def memo_detail(memo_id):
    memo = Memo.query.get_or_404(memo_id)
    rendered_content = markdown.markdown(memo.content)
    return render_template('memo_detail.html', memo=memo, rendered_content=rendered_content)

@app.route('/memo/<int:memo_id>/edit', methods=['GET', 'POST'])
def edit_memo(memo_id):
    memo = Memo.query.get_or_404(memo_id)
    
    if request.method == 'POST':
        content = request.form.get('memo')
        tag_input = request.form.get('tags', '')
        
        if content:
            memo.content = content
            tags = process_tags(tag_input)
            memo.tags = tags
            db.session.commit()
            return redirect(url_for('memo_detail', memo_id=memo.id))
    
    # カンマ区切りのタグ文字列を作成
    current_tags = ', '.join([tag.name for tag in memo.tags])
    return render_template('edit_memo.html', memo=memo, current_tags=current_tags)

@app.route('/memo/<int:memo_id>/delete', methods=['POST'])
def delete_memo(memo_id):
    memo = Memo.query.get_or_404(memo_id)
    db.session.delete(memo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tags')
def view_tags():
    tags = Tag.query.all()
    # タグごとのメモの数を取得
    tag_counts = {tag.name: len(tag.memos) for tag in tags}
    return render_template('tags.html', tags=tags, tag_counts=tag_counts)

if __name__ == '__main__':
    # Cloud Run用にPORTを8080に設定（環境変数で上書き可能）
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)

# Trigger GitHub Actions workflow
