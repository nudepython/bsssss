from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime


app = Flask(__name__, static_url_path='/static')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    genre = db.Column(db.String(50))
    rating = db.Column(db.Integer)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    def __repr__(self):
        return '<Book %r>' % self.title

@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('keyword')
        books = Book.query.filter(Book.title.contains(search_query)).all()
        return render_template('search.html', books=books, search_query=search_query)
    else:
        return redirect(url_for('index'))

@app.after_request
def apply_cufon(response):
    response.direct_passthrough = False

    if response.content_type == 'text/html; charset=utf-8':
        response.set_data(
            response.get_data(as_text=True).replace(
                '<script type="text/javascript">Cufon.replace',
                '<script type="text/javascript">window.onload = function() { Cufon.replace'
            )
        )

    return response


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        rating = request.form['rating']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        start_date_str = start_date
        end_date_str = end_date
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')

        book = Book(title=title, author=author, genre=genre, rating=rating, description=description, start_date=start_date, end_date=end_date)
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('add.html', books=Book.query.all())

@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
