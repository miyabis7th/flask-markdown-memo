from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# メモとタグの多対多関連付けテーブル
memo_tags = db.Table('memo_tags',
    db.Column('memo_id', db.Integer, db.ForeignKey('memo.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Memo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    tags = db.relationship('Tag', secondary=memo_tags, lazy='subquery',
                          backref=db.backref('memos', lazy=True))

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    def __repr__(self):
        return self.name
