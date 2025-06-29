from flask_mysqldb import MySQL

def init_db(app):
    # MySQL Configuration for Railway DB
    app.config['MYSQL_HOST'] = 'turntable.proxy.rlwy.net'
    app.config['MYSQL_PORT'] = 45859
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'GeVuCRNxGxYqoCDuRSnZhlFSYJPhPtio'
    app.config['MYSQL_DB'] = 'battery_swap'
    return MySQL(app)
