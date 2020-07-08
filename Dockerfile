FROM python:3.8-buster
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

ARG USERNAME=user
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME
RUN useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME
COPY ./app/ /home/user/app/
RUN chown -R $USER_UID:$USER_GID /home/user/app/
WORKDIR /home/user/app/
USER user
