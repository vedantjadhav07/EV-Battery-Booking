import os
from flask_mysqldb import MySQL

def init_db(app):
    
    app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
    app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
    app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
    app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
    app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3306))
      # Optional
    return MySQL(app)
