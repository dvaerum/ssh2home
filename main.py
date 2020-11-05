#!/usr/bin/env python
# ex: set tabstop=8 softtabstop=0 expandtab shiftwidth=4 smarttab:

from flask import Flask, Response
from tarfile import TarFile
import io
from pathlib import Path


class Config:
    port = 7654


CONFIG = Config()


app = Flask(__name__)


@app.route('/')
def hello_world():
    return ('This is my ssh dotfiles pull tool, '
            'for making sure that everytime I ssh '
            'to a server I have my environment with me :D')


@app.route('/pull/<hostname>')
def pull(hostname: str = None):
    home_dir = Path.home().__str__()
    io_stream = io.BytesIO()

    tar = TarFile(fileobj=io_stream, mode="w")
    for file_path in [".vimrc", ".vim"]:
        tar.add(name=f"{home_dir}/{file_path}",
                arcname=file_path)
    tar.close()
    io_stream.seek(0)
    return Response(io_stream.read1(), mimetype='application/x-tar')


@app.route('/startup_script/<hostname>')
def startup_script(hostname: str = None):
    


def main():
    app.run(host="localhost",
            port=CONFIG.port,
            debug=False)


if __name__ == "__main__":
    main()

