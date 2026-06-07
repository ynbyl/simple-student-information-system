# this is the main file to run the app
# just do: python run.py

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
