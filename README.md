## Installation for phantom-mask

0.
  - Since Mac OS Catalina, zsh will become the default terminal process, check you have set zsh as default shell
  - Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop)

1. Clone phantom-mask repository

   ```shell
   $ git clone https://github.com/mickeyleetw/phantom-mask.git
   ```

2. Python Version Management

  - Install manbaforge:

    - Install mambaforge
      ```sh
      $ brew install --cask mambaforge
      ```
    - Create environment by conda

      ```sh
      $ conda create -n ENVIRONMENT python=3.9.9
      ```

      Note that **DO NOT** use **UNDERSCORE** in the name of environment.
    - Activate the env:

      ```sh
      $ conda activate ENVIRONMENT
      ```

    - Initialize your shell by (shell name, e.g. zsh)

      ```sh
      $ conda init <SHELL_NAME>
      ```

    - _ QUIT terminal and restart _
      Displays the currently active Python version

      ```sh
      $ python --version
      ```

      The output is the following:

      ```sh
      Python 3.9.9
      ```

      If the python version is incorrect (for example, using another version you've set in pyenv),
      check your path by:

      ```sh
      echo -e ${PATH//:/\\n}
      ```

      and if you see the path of pyenv is prior to mambaforge, you can try adding a path directly to your shell setting file (e.g., .zshrc) before pyenv initialization. For example,

      ```sh
      export PATH="/usr/local/Caskroom/mambaforge/base/bin:$PATH"
      ```


3. Install project dependencies by requirement.txt

   ```shell
   $ pip install -r requirements.txt
   ```

## Setup for database

   ```shell
   $ cd ./phanton-mask
   $ docker-compose up -d
   ```

   ```shell
   container phantom-mask-postgresql-1  Running
   ```


## Reset database

```shell
# create database and load raw data
$ python cli.py reset-db


## Run phantom-mask server

```shell
# normal mode
$ python cli.py run

# auto-reload mode
$ python cli.py run --reload
```

Both the above commands will boot microservice template service on `http://localhosl:8003`
The default response in root path will return the following JSON response

```json
{ "status": 0 }
```

### OpenAPI

The openapi spec generated by FastAPI can be browsed on `http://localhost:8003/v1/docs`

