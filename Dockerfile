FROM python:3.10.10

# # Install ODBC driver dependencies
# RUN apt-get update && apt-get install -y \
#     curl \
#     gnupg \
#     unixodbc \
#     unixodbc-dev

# Install the Microsoft ODBC driver for SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
  #Ubuntu 16.04 package source
  curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
  apt-get update && \
  ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev && \
  echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile && \
  echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc


# # # install the Microsoft ODBC driver for SQL Server
# RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
#   #Ubuntu 16.04 package source
#   curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
#   apt-get update && \
#   ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev && \
#   echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile && \
#   echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

# Set working directory
# WORKDIR /code

# Copy requirements file
COPY ./requirements.txt  ./requirements.txt

# Install other dependencies
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# Copy the rest of the application code
COPY . .

# Set the entrypoint command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]