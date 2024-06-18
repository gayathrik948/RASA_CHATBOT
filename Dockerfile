FROM    python:3.8-slim
WORKDIR /src
COPY    requirements.txt .
RUN     /usr/local/bin/python -m pip install --upgrade pip
RUN     pip3 install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
RUN     python - m textblob.download_corpora
COPY    . .
COPY    other/rest.py /usr/local/lib/python3.6/site-packages/rasa/core/channels/rest.py
RUN     sed -i "s~\r~~g" bin/run
ENTRYPOINT      ["sh", "bin/run"]


