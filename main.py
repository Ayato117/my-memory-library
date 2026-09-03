from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
import mysql.connector # MySQLのライブラリ
from datetime import datetime
from flask_bcrypt import Bcrypt
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS
 

app = Flask(__name__)
CORS(app)
app.secret_key = 'secret_key'

bcrypt = Bcrypt(app) # パスワードのハッシュ化

UPLOAD_FOLDER = 'uploads/' # 画像のアップロード先
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # アップロード先のディレクトリを設定

def database_connection():
    return mysql.connector.connect(
        user='root',
        password='',
        host='localhost',
        port='3306',
        database='job_hunting',
    )

def get_current_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# index page
@app.route('/')
def index():
    if 'loggedin' in session:
        return render_template("index.html", login=True, username=session['username'])
    return render_template("index.html", login=False)

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        action = request.form.get('action') # 'login' or 'signup' を取得

        email = request.form['email']
        password = request.form['password']

        if action == 'signup':
            username = request.form['username']

            conn = database_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            existing_user = cursor.fetchone() # ユーザーが存在するかどうか

            if existing_user:
                cursor.close()
                conn.close()
                return render_template('auth.html', error='このメールアドレスは既に登録されています')

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8') 
            cursor.execute("INSERT INTO users (username, email, password, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)", (username, email, hashed_password, get_current_timestamp(), get_current_timestamp()))
            conn.commit() # コミットする
            cursor.close() # カーソルを閉じる
            conn.close() # 接続を閉じる

            return redirect(url_for('auth'))
        
        elif action == 'login':
            conn = database_connection()
            cursor = conn.cursor(dictionary=True) # 辞書型で取得
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user and bcrypt.check_password_hash(user['password'], password): # パスワードが一致した場合
                session['loggedin'] = True
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                return redirect(url_for('index'))
            else:
                return render_template('auth.html', error='ログインに失敗しました')
            
    return render_template("auth.html")

# logout page
@app.route('/logout')
def logout():
    session.clear() # セッションをクリア
    return redirect(url_for('index'))

# diary_home page
@app.route('/diary/home')
def diary_home():
    if 'loggedin' not in session:  # ログイン状態を確認
        return redirect(url_for('auth'))  # 未ログインの場合はログインページへリダイレクト

    conn = database_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 現在のユーザーの日記データを取得
    cursor.execute("SELECT diary_id, diary_title, diary_date, diary_content, diary_imageurl FROM diary WHERE user_id = %s", (session['user_id'],))
    diary_entries = cursor.fetchall()  # 全ての日記データを取得

    # イベントデータを構築
    events = [
        {
            "diary_id": entry.get("diary_id"),  # `diary_id` を追加
            "title": entry.get("diary_title") or "",
            "start": entry.get("diary_date") or "",
            "description": entry.get("diary_content") or "",
            "image_url": entry.get("diary_imageurl") or ""
        }
        for entry in diary_entries
    ]

    cursor.close()
    conn.close()

    # テンプレートに `events` を渡す
    return render_template("diary_home.html", username=session.get('username'), events=events)

@app.route('/delete_diary/<int:diary_id>', methods=['POST'])
def delete_diary(diary_id):
    if 'loggedin' not in session:
        return redirect(url_for('auth'))  # 未ログインの場合はログインページへリダイレクト

    conn = database_connection()
    cursor = conn.cursor()

    # 現在のユーザーのIDと一致する日記を削除
    cursor.execute("DELETE FROM diary WHERE diary_id = %s AND user_id = %s", (diary_id, session['user_id']))
    conn.commit()

    cursor.close()
    conn.close()

    # 成功メッセージをテンプレートに渡す
    # return redirect(url_for('diary_home', delete_success=True))

    # 削除成功のメッセージをフラッシュしてからリダイレクト
    flash("日記が削除されました。", "success")
    return redirect(url_for('diary_home'))  # クエリパラメータなしでリダイレクト

@app.route('/diary/detail/<int:diary_id>')
def diary_detail(diary_id):
    if 'loggedin' not in session:
        return redirect(url_for('auth'))

    conn = database_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM diary WHERE diary_id = %s AND user_id = %s", (diary_id, session['user_id']))
    diary_entry = cursor.fetchone()
    cursor.close()
    conn.close()

    if not diary_entry:
        return redirect(url_for('diary_home'))

    return render_template("diary_detail.html", username=session.get('username'), diary=diary_entry)

@app.route('/diary/edit/<int:diary_id>', methods=['GET', 'POST'])
def diary_edit(diary_id):
    if 'loggedin' not in session:
        return redirect(url_for('auth'))

    conn = database_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # フォームデータを取得
        diary_title = request.form['diary_title']
        diary_content = request.form['diary_content']
        diary_date = request.form['diary_date']
        diary_image = request.files.get('diary_image')

        # 画像処理
        if diary_image:  # 新しい画像がアップロードされた場合
            filename = secure_filename(diary_image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            diary_image.save(filepath)
            diary_imageurl = url_for('uploaded_file', filename=filename)
        else:  # 既存の画像を利用
            diary_imageurl = request.form.get('existing_imageurl', '')

        # データベースを更新
        cursor.execute("""
            UPDATE diary
            SET diary_title = %s, diary_date = %s, diary_content = %s, diary_imageurl = %s, updated_at = %s
            WHERE diary_id = %s AND user_id = %s
        """, (diary_title, diary_date, diary_content, diary_imageurl, get_current_timestamp(), diary_id, session['user_id']))
        conn.commit()
        cursor.close()
        conn.close()

        # 日記の詳細ページへリダイレクト
        return redirect(url_for('diary_detail', diary_id=diary_id))

    # 現在のデータを取得
    cursor.execute("SELECT * FROM diary WHERE diary_id = %s AND user_id = %s", (diary_id, session['user_id']))
    diary_entry = cursor.fetchone()
    cursor.close()
    conn.close()

    if not diary_entry:
        return redirect(url_for('diary_home'))

    return render_template("diary_edit.html", diary=diary_entry, username=session.get('username'))

# write a diary
@app.route('/diary/write', methods=['GET', 'POST'])
def diary_write():
    if 'loggedin' not in session:
        return redirect(url_for('auth'))

    if request.method == 'POST':
        diary_title = request.form['diary_title']
        diary_content = request.form['diary_content']
        diary_date = request.form['diary_date']
        diary_image = request.files.get('diary_image')

        if diary_image:
            filename = secure_filename(diary_image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            diary_image.save(filepath)
            diary_imageurl = url_for('uploaded_file', filename=filename)
        else:
            diary_imageurl = ''

        conn = database_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO diary (user_id, diary_title, diary_date, diary_content, diary_imageurl, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (session['user_id'], diary_title, diary_date, diary_content, diary_imageurl, get_current_timestamp(), get_current_timestamp()))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('diary_home'))

    # 空の events を渡してテンプレートエラーを防ぐ
    return render_template("diary_write.html", username=session.get('username'), events=[])


# calendar page
@app.route('/diary/calendar')
def diary_calendar():
    if 'loggedin' not in session:
        return redirect(url_for('auth'))

    selected_date = request.args.get('date')
    conn = database_connection()
    cursor = conn.cursor(dictionary=True)

    # 選択された日付がある場合、その日付の日記を取得
    if selected_date:
        cursor.execute("SELECT diary_title, diary_date, diary_content FROM diary WHERE user_id = %s AND DATE(diary_date) = %s", (session['user_id'], selected_date))
    else:
        cursor.execute("SELECT diary_title, diary_date, diary_content FROM diary WHERE user_id = %s", (session['user_id'],))

    diary_entries = cursor.fetchall()
    cursor.close()
    conn.close()

    # イベントデータを構築
    events = [
        {
            "title": entry["diary_title"],
            "start": entry["diary_date"].strftime('%Y-%m-%d'),  # 日付形式を変換
            "description": entry["diary_content"],
            "image_url": entry.get("diary_imageurl", "")  # 画像URLがない場合は空文字
        }
        for entry in diary_entries
    ]

    # diary_entries と events をテンプレートに渡す
    return render_template("diary_calendar.html", username=session.get('username'), events=events, diary_entries=diary_entries)


# search diaries
@app.route('/diary/search', methods=['GET', 'POST'])
def diary_search():
    if 'loggedin' not in session:
        return redirect(url_for('auth'))

    if request.method == 'POST':
        keyword = request.form['keyword']
        conn = database_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT diary_id, diary_title, diary_date, diary_content, diary_imageurl FROM diary WHERE user_id = %s AND (diary_title LIKE %s OR diary_content LIKE %s)",
            (session['user_id'], f"%{keyword}%", f"%{keyword}%"))
        search_results = cursor.fetchall()
        cursor.close()
        conn.close()

        # ここで、`diary_id` を含む結果を渡すことを確認
        events = [
            {
                "diary_id": entry["diary_id"],
                "title": entry["diary_title"],
                "start": entry["diary_date"].strftime('%Y-%m-%d') if isinstance(entry["diary_date"], datetime) else entry["diary_date"],  # 日付形式の確認
                "description": entry["diary_content"],
                "image_url": entry.get("diary_imageurl", "")
            }
            for entry in search_results
        ]

        return render_template("diary_search.html", search_results=search_results, username=session.get('username'), events=events)

    # 初期状態では空の `events` を渡す
    return render_template("diary_search.html", username=session.get('username'), events=[])


# uploaded file path
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename) # ファイルを返す


if __name__ == "__main__":
    app.run(debug=True, port=8888, threaded=True)