FROM python:3.8-buster
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

ARG username=user
ARG user_uid=1000
ARG user_gid=1000
RUN groupadd --gid $user_gid $username
RUN useradd -s /bin/bash --uid $user_uid --gid $user_gid -m $username
COPY . /home/$username/app/
RUN chown -R $user_uid:$user_gid /home/$username/app/
WORKDIR /home/$username/app/
USER user
