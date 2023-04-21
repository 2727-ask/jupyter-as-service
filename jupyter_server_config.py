# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
# mypy: ignore-errors
import os
import stat
import subprocess

from jupyter_core.paths import jupyter_data_dir

c = get_config()  # noqa: F821
c.ServerApp.ip = "0.0.0.0"
c.ServerApp.open_browser = False
c.NotebookApp.port = int(os.environ.get("PORT", 8888))
c.NotebookApp.password = u'argon2:$argon2id$v=19$m=10240,t=10,p=8$ly8U08xvnFaWmVGsrVDoDA$W8TDsO0aJ+SdT/gL+mkfH44ptVgy0/GWD13QJuaULOs'

# to output both image/svg+xml and application/pdf plot formats in the notebook file
c.InlineBackend.figure_formats = {"png", "jpeg", "svg", "pdf"}

# https://github.com/jupyter/notebook/issues/3130
c.FileContentsManager.delete_to_trash = False

# Generate a self-signed certificate
OPENSSL_CONFIG = """\
[req]
distinguished_name = req_distinguished_name
[req_distinguished_name]
"""
if "GEN_CERT" in os.environ:
    dir_name = jupyter_data_dir()
    pem_file = os.path.join(dir_name, "notebook.pem")
    os.makedirs(dir_name, exist_ok=True)

    # Generate an openssl.cnf file to set the distinguished name
    cnf_file = os.path.join(os.getenv("CONDA_DIR", "/usr/lib"), "ssl", "openssl.cnf")
    if not os.path.isfile(cnf_file):
        with open(cnf_file, "w") as fh:
            fh.write(OPENSSL_CONFIG)

    # Generate a certificate if one doesn't exist on disk
    subprocess.check_call(
        [
            "openssl",
            "req",
            "-new",
            "-newkey=rsa:2048",
            "-days=365",
            "-nodes",
            "-x509",
            "-subj=/C=XX/ST=XX/L=XX/O=generated/CN=generated",
            f"-keyout={pem_file}",
            f"-out={pem_file}",
        ]
    )
    # Restrict access to the file
    os.chmod(pem_file, stat.S_IRUSR | stat.S_IWUSR)
    c.ServerApp.certfile = pem_file

# Change default umask for all subprocesses of the notebook server if set in
# the environment
if "NB_UMASK" in os.environ:
    os.umask(int(os.environ["NB_UMASK"], 8))


# import os
# c = get_config()
# # Kernel config
# c.IPKernelApp.pylab = 'inline'  # if you want plotting support always in your notebook
# # Notebook config
# # c.NotebookApp.notebook_dir = 'nbs'
# # c.NotebookApp.allow_origin = u'cfe-jupyter.herokuapp.com' # put your public IP Address here
# c.NotebookApp.ip = '*'
# c.NotebookApp.allow_remote_access = True
# c.NotebookApp.open_browser = False
# # ipython -c "from notebook.auth import passwd; passwd()"
# c.NotebookApp.password = u'sha1:8da45965a489:86884d5b174e2f64e900edd129b5ef0d2f784a65'
# c.NotebookApp.port = int(os.environ.get("PORT", 8888))
# c.NotebookApp.allow_root = True
# c.NotebookApp.allow_password_change = True
# c.ConfigurableHTTPProxy.command = ['configurable-http-proxy', '--redirect-port', '80']
