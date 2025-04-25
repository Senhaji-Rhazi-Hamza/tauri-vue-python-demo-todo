from main import app  # ← this works if main.py is included

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()  # 👈 enables safe multiprocessing in PyInstaller

    app.run(host="127.0.0.1", port=8000)