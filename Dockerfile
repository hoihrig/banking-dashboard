FROM python:3-alpine

COPY requirements.txt ./
RUN apk add --no-cache python3-dev libstdc++ && \
    apk add --no-cache --virtual .build-deps g++ && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    pip3 install -r requirements.txt && \
    apk del .build-deps

COPY  app_settings.py app.py sbanken_data.py ./
EXPOSE 8050

CMD ["python", "app.py"]