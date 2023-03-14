FROM python:3.10-alpine3.16@sha256:ad9637f3477f328ec675dd9834c61707b3c75e57b91a70c5422325a72087abdf

# App base dir
WORKDIR /app

# Copy app
COPY /app .

# Install dependencies
RUN pip3 install -r requirements.txt

# Main command
CMD [ "python", "-u", "main.py" ]