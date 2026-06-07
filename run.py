from app import app
from app.dao import init_db

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
    # app.run(host='', port=, debug=True) #Возможность подключение всех устройств на вайфае