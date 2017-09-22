# VGM Player for RPi to RE Module Interface

## Installation

Choose one.

### Python bundled with Raspbian (Stretch 2017-09-07)

1. Install prerequisites.
   ```
   $ sudo apt-get install git python-dev libbz2-dev libreadline-dev libsqllite3-dev libssl-dev
   ```

1. Install pip.
   ```
   $ curl -O https://bootstrap.pypa.io/get-pip.py
   $ sudo python get-pip.py
   ```

1. Install Wiringpi-Python.
   ```
   $ sudo pip install wiringpi
   ```

1. Clone `vgmplayer-rpi-re` repository.
   ```
   $ git clone https://github.com/tettoon/vgmplayer-rpi-re.git
   $ cd vgmplayer-rpi-re
   ```

### pyenv

1. Install prerequisites.
   ```
   $ sudo apt-get install git libbz2-dev libreadline-dev libsqllite3-dev libssl-dev
   ```

1. Install pyenv.
   ```
   $ curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash
   ```
   Append below lines to `~/.bash_profile`.
   ```
   export PATH="~/.pyenv/bin:$PATH"
   eval "$(pyenv init -)"
   eval "$(pyenv virtualenv-init -)"
   ```
1. Load ~/.bash\_profile.
   ```
   source ~/.bash_profile
   ```
1. Install Python 2.7.13.
   ```
   $ pyenv install 2.7.13
   ```
   Wait a few minutes.

1. Clone `vgmplayer-rpi-re` repository.
   ```
   $ git clone https://github.com/tettoon/vgmplayer-rpi-re.git
   $ cd vgmplayer-rpi-re
   ```

1. Set local python version.
   ```
   $ pyenv local 2.7.13
   ```

1. Rehash pyenv.
   ```
   $ pyenv rehash
   ```

1. Install Wiringpi-Python.
   ```
   $ pip install wiringpi
   ```

## Usage
* Show help message.
  ```
  $ python vgmplayer.py --help
  ```
* Play VGM file.
  ```
  $ python vgmplayer.py -g -m YM2151 ~/vgm/mysong.vgz
  ```
* Play as M3U playlist.
  ```
  $ python vgmplayer.py -g -m YM2151 -l ~/vgm/mylist.m3u
  ```
