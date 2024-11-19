# Dockerfile
FROM ubuntu:20.04

# Install necessary packages
RUN apt-get update && apt-get install -y python3 python3-pip sudo

# Create a directory for the application in /opt/app and set permissions
RUN mkdir -p /opt/app && chown root:root /opt/app && chmod 700 /opt/app

# Copy only the necessary application files to /opt/app
COPY app.py /opt/app/
COPY requirements.txt /opt/app/
COPY static /opt/app/static
COPY validator.py /opt/app/

# Install Python dependencies
RUN pip3 install -r /opt/app/requirements.txt

# Set the default working directory for the developer user
WORKDIR /home

# Ensure the developer's default shell starts in their home directory
RUN echo "cd /home" >> /home/.bashrc

# Expose port 5000 for Flask
EXPOSE 5000

# Run the Flask application from /opt/app
CMD ["python3", "/opt/app/app.py"]




# FROM ubuntu:20.04

# # Install necessary packages
# RUN apt-get update && apt-get install -y python3 python3-pip sudo libpq-dev

# # Create a directory for the application in /opt/app and set permissions
# RUN mkdir -p /opt/app && chown root:root /opt/app && chmod 700 /opt/app

# # Set the working directory to /opt/app
# WORKDIR /opt/app

# # Copy only the necessary application files to /opt/app
# COPY app.py /opt/app/
# COPY requirements.txt /opt/app/
# COPY static /opt/app/static
# COPY validator.py /opt/app/

# # Install Python dependencies
# RUN pip3 install -r /opt/app/requirements.txt

# # Set the default working directory for the developer user
# WORKDIR /home

# # Ensure the developer's default shell starts in their home directory
# RUN echo "cd /home" >> /home/.bashrc

# # Expose port 5000 for Flask
# EXPOSE 5000

# # Run the Flask application from /opt/app
# CMD ["python3", "/opt/app/app.py"]

