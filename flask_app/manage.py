from flask_api import create_app

app = create_app()

if __name__ == '__main__':
    # run app
    app.run(port=8000, host='0.0.0.0')