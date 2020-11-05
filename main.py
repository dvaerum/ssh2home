#!/usr/bin/env python
# ex: set tabstop=8 softtabstop=0 expandtab shiftwidth=4 smarttab:

from os import path
import io
from pathlib import Path

from flask import Flask, Response
from tarfile import TarFile

from lib.misc import *


class Config:
    port = 7654


CONFIG = Config()

LOCAL_PWD = path.dirname(path.realpath(__file__))
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


@app.route('/startup-script/<hostname>')
def startup_script(hostname: str = None):
    with open(f"{LOCAL_PWD}/templates/startup-script.sh.j2") as f:
        return Response(f.read() ,mimetype='application/x-sh')


def main():
    with open(f"{LOCAL_PWD}/templates/ssh_config.j2") as f:
        insert_text_block(f"{Path.home().__str__()}/.ssh/config",
                          f.read())

    app.run(host="localhost",
            port=CONFIG.port,
            debug=False)


if __name__ == "__main__":
    main()

