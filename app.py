from flask import Flask, render_template, request, redirect, url_for
import markdown
import os

app = Flask(__name__)

memos = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        memo = request.form.get('memo')
        if memo:
            memos.append(memo)
        return redirect(url_for('index'))
    rendered_memos = [markdown.markdown(m) for m in memos]
    return render_template('index.html', memos=rendered_memos)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
