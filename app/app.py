from flask import Flask, jsonify, request
from flaskext.mysql import MySQL

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'keshav_sr'
app.config['MYSQL_DATABASE_PASSWORD'] = 'ProKj!@12'
app.config['MYSQL_DATABASE_DB'] = 'nudity'
app.config['MYSQL_DATABASE_HOST'] = '114.69.243.150'
app.config['MYSQL_DATABASE_PORT'] = 47849
mysql.init_app(app)

@app.route('/', methods=['GET'])
def home():
    conn = mysql.connect()
    cursor =conn.cursor()

    cursor.execute("SELECT * from users")
    data = cursor.fetchall()
    return jsonify({
        'users':data
    })

if __name__ == '__main__':
    app.run(debug=True)
