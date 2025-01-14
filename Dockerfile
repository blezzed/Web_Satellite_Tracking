FROM ubuntu:latest
LABEL authors="Administrator"

ENTRYPOINT ["top", "-b"]
# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy project files to the container
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install setuptools wheel
RUN apt-get update && apt-get install -y gcc \
    python3-distutils \
    libpq-dev \
    && apt-get clean

# Set GDAL environment variables
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Set GDAL library path for Django settings
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/libgeos_c.so

RUN pip install -r requirements.txt

# Copy project files
COPY . /app/

# Expose port for daphne
EXPOSE 8002

CMD ["daphne", "-b", "0.0.0.0", "-p", "8002", "web_satellite_tracking.asgi:application"]
