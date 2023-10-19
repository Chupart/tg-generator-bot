FROM continuumio/miniconda3

WORKDIR /app

ENV CONDA_ENV_PATH /opt/conda/envs/prompt-generator-api
ENV PATH $CONDA_ENV_PATH/bin:$PATH

RUN conda update -n base -c defaults conda -y && \
    conda config --add channels conda-forge && \
    conda config --set channel_priority flexible && \
    apt-get update && apt-get install -y curl gcc g++ && \
    rm -rf /var/lib/apt/lists/* && \
    conda install libarchive mamba gcc_linux-64 gxx_linux-64 -c conda-forge

RUN pip install --upgrade pip

RUN mamba create -n prompt-generator-api python=3.10 && \
    /opt/conda/envs/prompt-generator-api/bin/pip install torch transformers flask flask_restful flask_limiter

RUN git clone https://github.com/jordip/prompt-generator-api.git /app

ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Use flask run to start the application
CMD ["flask", "run"]