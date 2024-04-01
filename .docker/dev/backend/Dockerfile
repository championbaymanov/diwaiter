FROM python:3.12.2

# Set up Python behaviour
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HOME=/home/app
ENV APP_HOME=/home/app/backend
ENV VIRTUAL_ENV=/opt/venv

# Install system dependencies
RUN apt-get update -y \
  && apt-get install -y netcat-openbsd gcc postgresql vim

# Create folders
RUN mkdir $HOME
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/assets
RUN mkdir $APP_HOME/media
RUN mkdir $APP_HOME/logs

# Set the working directory
WORKDIR $APP_HOME

# Copy all files
COPY ./ ./

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY $LOCAL_APP $APP_HOME

# create the app user
# RUN groupadd -r www-data && useradd -r -g www-data www-data
# RUN addgroup -S www-data && adduser  -S app -G app alpine

# chown all the files to the www-data user
#RUN chown -R www-data:www-data $APP_HOME/media
RUN chown -R www-data:www-data $APP_HOME

#ARG USER=www-data
#USER $USER

# run entrypoint.prod.sh
RUN ["chmod", "+x", "/home/app/backend/.docker/dev/backend/entrypoint.sh"]
ENTRYPOINT ["/home/app/backend/.docker/dev/backend/entrypoint.sh"]

