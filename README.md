# Project03A
Project03 now on the web!


## Project03A - Stock Chart App

This is a Flask application that generates stock charts from data using the API from the previous project and using Docker. The app reads stock symbols from `stocks.csv` and displays the data graphically in a web interface.

## Features

- Select stock symbols from a predefined list in `stocks.csv`.
- Generate line or bar charts for open, close, high, and low prices.
- Supports multiple time intervals (intradaily, daily, weekly, monthly).
- Runs in a Docker container, making it easy to set up and run on any system with Docker installed.

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (recommended for Windows/Mac users)
- Git (to clone this repository)

## Getting Started

Follow these steps to set up and run the application.

### 1. Clone the Repository

Open a terminal and clone this repository to your local machine:

### 2. Build the Docker Image

docker build -t stock-chart-app .

### 3. Run the Docker Container

docker run -p 5000:5000 -v "$(pwd)/stocks.csv:/mnt/data/stocks.csv" stock-chart-app

### 4. Access the Application

Once the Docker container is running, open your browser and navigate to: http://localhost:5000
