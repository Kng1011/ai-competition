FROM python:3.12.2-alpine3.19

WORKDIR /app

# Install nodemon and nodejs
RUN apk update && \
    apk add --no-cache curl nodejs npm && \
    npm install -g npm@10.5.1 nodemon

# Upgrade pip
RUN python -m pip install --upgrade pip

# Install Python dependencies from requirements.txt
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entrypoint script into the container
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /usr/local/bin/entrypoint.sh

# Fix endlines for windows systems
RUN sed -i 's/\r$//' /usr/local/bin/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["entrypoint.sh"]

# Set default command (to be overridden by ENTRYPOINT script)
CMD ["main.py"]