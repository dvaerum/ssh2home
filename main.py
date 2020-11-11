#!/usr/bin/env python3
# ex: set tabstop=8 softtabstop=0 expandtab shiftwidth=4 smarttab:

import os
from os import path
import io
from pathlib import Path

from flask import Flask, Response
from tarfile import TarFile

from lib.misc import *
from lib.config import Config


LOCAL_PWD = path.dirname(path.realpath(__file__))
CONFIG = Config(path=f'{LOCAL_PWD}/config.yml')
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
    for file_path in CONFIG.files + CONFIG.host_files.get(hostname, []):
        if isinstance(file_path, str):
            tar.add(name=f"{home_dir}/{file_path}",
                    arcname=file_path)
        elif isinstance(file_path, dict):
            tar.add(name=f"{home_dir}/{file_path['src']}",
                    arcname=file_path['dst'])

    tar.close()
    io_stream.seek(0)
    return Response(io_stream.read1(), mimetype='application/x-tar')


@app.route('/startup-script/<hostname>')
@app.route('/startup-script/<hostname>/')
@app.route('/startup-script/<hostname>/<id>')
def startup_script(hostname: str = None, id: str = None):
    _packages = [package for package,distro in CONFIG.packages.items()
        if not isinstance(distro, list) or id in distro]

    script = template(f"{LOCAL_PWD}/templates/startup-script.sh.j2",
                      config=CONFIG,
                      distro_id=id,
                      packages=_packages,
                      password=CONFIG.password)
    return Response(script ,mimetype='application/x-sh')


def main():
    # Include reverse proxy in all ssh connections
    insert_text_block(f"{Path.home().__str__()}/.ssh/config",
                      template(f"{LOCAL_PWD}/templates/ssh_config.j2"))

    # Create environment variable file
    tmp_path = f"/tmp/{os.getlogin()}"
    os.makedirs(tmp_path, mode=0o700, exist_ok=True)
    with open(f"{tmp_path}/env", 'w') as f:
        f.write(f"PORT={CONFIG.port}\nSSH_BIN_PATH={CONFIG.ssh_bin}\n")

    with open(f"{tmp_path}/check_shells.sh", 'w') as f:
        f.write(template(f"{LOCAL_PWD}/templates/check_shells.sh.j2",
                         shells        = CONFIG.shell.shells,
                         dot_file_path = CONFIG.shell.dot_file_path,
                         update_interval = CONFIG.shell.update_interval))

    # Start web server
    app.run(host="localhost",
            port=CONFIG.port,
            debug=False)


if __name__ == "__main__":
    main()

