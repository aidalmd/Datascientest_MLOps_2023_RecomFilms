import mysql.connector 



cnx = mysql.connector.connect(user='root', password='admin1234',
                              host='127.0.0.1',
                              use_pure=False)

mycursor= cnx.cursor()

mycursor.execute("CREATE DATABASE mydatabase")