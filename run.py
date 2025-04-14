from app import create_app

app = create_app()

running_port = app.config["PORT"]
if __name__ == "__main__":
    app.run(debug=True, port=running_port)