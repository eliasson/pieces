FROM python:3.5

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

# path to torrent file must lie within root
CMD ["python", "pieces.py", "-v", "*path to torrent here*"]s
