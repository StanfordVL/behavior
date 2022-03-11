FROM igibson/igibson:latest

RUN git clone --depth 1 https://github.com/StanfordVL/behavior /opt/behavior

WORKDIR /opt/behavior

RUN pip install --no-cache-dir -e .

WORKDIR /opt/behavior/behavior/benchmark/scripts
