FROM continuumio/miniconda3

WORKDIR /app

ENV CONDA_ENV_PATH /opt/conda/envs/tg-generator-bot
ENV PATH $CONDA_ENV_PATH/bin:$PATH

RUN conda update -n base -c defaults conda -y && \
    conda config --add channels conda-forge && \
    conda config --set channel_priority flexible && \
    apt-get update && apt-get install -y curl gcc g++ && \
    rm -rf /var/lib/apt/lists/* && \
    conda install libarchive mamba gcc_linux-64 gxx_linux-64 -c conda-forge

RUN pip install --upgrade pip

COPY ./environment.yml /app/environment.yml
RUN mamba create -n tg-generator-bot python=3.10 && \
    mamba env update -n tg-generator-bot -f environment.yml

COPY . /app

CMD ["python", "tg_generator_bot.py"]
