from flask import Flask, jsonify, request
from flaskext.mysql import MySQL

myapp = Flask(__name__)

mysql = MySQL()
myapp.config['MYSQL_DATABASE_USER'] = 'keshav_sr'
myapp.config['MYSQL_DATABASE_PASSWORD'] = 'ProKj!@12'
myapp.config['MYSQL_DATABASE_DB'] = 'nudity'
myapp.config['MYSQL_DATABASE_HOST'] = '114.69.243.150'
myapp.config['MYSQL_DATABASE_PORT'] = 47849
mysql.init_app(myapp)

@myapp.route('/', methods=['GET'])
def home():
    conn = mysql.connect()
    cursor =conn.cursor()

    cursor.execute("SELECT * from users")
    data = cursor.fetchall()
    return jsonify({
        'users':data
    })

if __name__ == '__main__':
    myapp.run(debug=True)
