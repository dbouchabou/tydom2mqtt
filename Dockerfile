FROM python:3.10-alpine3.16@sha256:884085609a2da0054ebaf0392313cd7ceb8bee7d05ed28d5498f521d341a67be

# App base dir
WORKDIR /app

# Copy app
COPY /app .

# Install dependencies
RUN pip3 install -r requirements.txt

# Main command
CMD [ "python", "-u", "main.py" ]