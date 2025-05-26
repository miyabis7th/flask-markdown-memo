from flask import Flask, render_template, request, redirect, url_for, abort
import markdown
import os
from flask_sqlalchemy import SQLAlchemy
from models import db, Memo

app = Flask(__name__)

# Render用のPostgreSQL接続設定
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        memo = request.form.get('memo')
        if memo:
            new_memo = Memo(content=memo)
            db.session.add(new_memo)
            db.session.commit()
        return redirect(url_for('index'))
    memos = Memo.query.order_by(Memo.id.desc()).all()
    rendered_memos = [(m.id, markdown.markdown(m.content)) for m in memos]
    return render_template('index.html', memos=rendered_memos)

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
        if content:
            memo.content = content
            db.session.commit()
            return redirect(url_for('memo_detail', memo_id=memo.id))
    
    return render_template('edit_memo.html', memo=memo)

@app.route('/memo/<int:memo_id>/delete', methods=['POST'])
def delete_memo(memo_id):
    memo = Memo.query.get_or_404(memo_id)
    db.session.delete(memo)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
