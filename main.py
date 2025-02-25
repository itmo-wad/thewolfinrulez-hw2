from flask import Flask, render_template, request, redirect, url_for, session, flash
import redis

app = Flask(__name__)
app.secret_key = 'your_secret_key'

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('profile'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    stored_password = redis_client.get(f'user:{username}')
    if stored_password and stored_password.decode('utf-8') == password:
        session['username'] = username
        return redirect(url_for('profile'))
    else:
        flash('Invalid credentials', 'error')
        return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if redis_client.exists(f'user:{username}'):
            flash('Username is occupied', 'error')
            return redirect(url_for('register'))

        redis_client.set(f'user:{username}', password)
        flash('Successful registration!', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('index'))
    return f"""
        <h1>Welcome, {session['username']}!</h1>
        <a href="/logout"><button>Logout</button></a>
    """


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Log out.', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)