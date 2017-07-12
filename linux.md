# Linux

Ubuntu LTS 16.04 64-bit is the recommended platform.

## Requirements

* OS with 64-bit or 32-bit architecture
* Git
* Virtualenv
* Python2.7

For more details, scroll down to find how to setup a specific Linux distro.

## Instructions

```sh
git clone https://github.com/lucioveloso/lambda-toolkit
cd lambda-toolkit
./build.sh make
source build_env/bin/activate
```

### `./build.sh` Options

* `make`: build virtualenv and setup lambda_tollskit
* `clean`: clean virtualenv and generated files by the setup command
* `install`: build package and send to PyPI

### Ubuntu / Debian

* If `./build.sh` exits with an error, you may need to install the virtualenv:

```sh
sudo apt-get update && sudo apt-get -y upgrade
sudo apt-get install python-pip
pip install --upgrade pip
pip install virtualenv
```