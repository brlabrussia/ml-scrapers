FROM python:3.8-buster
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

ARG username=user
ARG user_uid
ARG user_gid
RUN groupadd --gid $user_gid $username
RUN useradd -s /bin/bash --uid $user_uid --gid $user_gid -m $username
COPY ./app/ /home/$username/app/
RUN chown -R $user_uid:$user_gid /home/$username/app/
WORKDIR /home/$username/app/
USER user
