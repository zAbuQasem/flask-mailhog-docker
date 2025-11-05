from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Mail config
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER", "mailhog-lol")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", 1025))
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# DB connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "mysql-db"),
        user=os.getenv("DB_USER", "flaskuser"),
        password=os.getenv("DB_PASSWORD", "flaskpass"),
        database=os.getenv("DB_NAME", "emailsdb")
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        recipient = request.form['to']
        subject = request.form['subject']
        body = request.form['body']

        # Send email
        msg = Message(subject=subject,
                      sender='noreply@example.com',
                      recipients=[recipient])
        msg.body = body
        mail.send(msg)

        # Save to MySQL
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INT AUTO_INCREMENT PRIMARY KEY,
                recipient VARCHAR(255),
                subject VARCHAR(255),
                body TEXT
            )
        """)
        cursor.execute(
            "INSERT INTO emails (recipient, subject, body) VALUES (%s, %s, %s)",
            (recipient, subject, body)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Email sent to {recipient} and saved in DB!", "success")
        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)

