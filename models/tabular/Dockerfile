FROM python:3.7
ENV PORT "8080"
RUN pip3 --no-cache-dir install \
        flask \
        requests \
        fastai2 \
        gunicorn \
        pandas \
    && pip3 --no-cache-dir install \
        torch==1.4.0+cpu \
        torchvision==0.5.0+cpu \
        -f https://download.pytorch.org/whl/torch_stable.html

COPY ./ /app
WORKDIR /app

ADD https://storage.googleapis.com/sv-fastai/models/apthunt/20200502_cltab.pkl /tmp/model_20200502_cltab.pkl

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app