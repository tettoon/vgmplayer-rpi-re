# VGM Player for RPi to RE Module Interface

## Installation

1. Install pyenv.
   ```
   curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash
   ```
   Append below to `~/.bashrc` file.
   ```
   export PATH="~/.pyenv/bin:$PATH"
   eval "$(pyenv init -)"
   eval "$(pyenv virtualenv-init -)"
   ```

1. Install prerequisite libraries.
   ```
   sudo apt-get install libbz2-dev libreadline-dev libsqllite3-dev libssl-dev
   ```

1. Install Python 2.7.13.
   ```
   pyenv install 2.7.13
   ```

1. Clone `vgmplayer-rpi-re` repository.
   ```
   git clone https://github.com/tettoon/vgmplayer-rpi-re.git
   cd vgmplayer-rpi-re
   ```

1. Set local python version.
   ```
   pyenv local 2.7.13
   ```

1. Install Wiringpi-Python.
   ```
   sudo pip install wiringpi
   ```

1. Rehash pyenv.
   ```
   pyenv rehash
   ```

## Usage
```
sudo python vgmplayer.py --help
```
```
sudo python vgmplayer.py -m YM2151 -g ~/vgm/mysong.vgz
```
```
sudo python vgmplayer.py -m YM2151 -g -l ~/vgm/mylist.m3u
```
