FROM python:3.7
ENV PORT "8080"
RUN python -m pip install --upgrade pip \
    && pip3 --no-cache-dir install \
        flask \
        requests \
        fastai2 \
        gunicorn \
        pandas \
        ipykernel \
    && pip3 --no-cache-dir install \
        torch==1.4.0+cpu \
        torchvision==0.5.0+cpu \
        -f https://download.pytorch.org/whl/torch_stable.html

ADD https://storage.googleapis.com/sv-fastai/models/apthunt/20200503_cltab.pkl /tmp/model_20200503_cltab.pkl

COPY ./*.py /app/
WORKDIR /app

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app