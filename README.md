GUI Application for displaying temperature and humidity on a Raspberry PI.

**TODO:** Add images

# Dependencies
- Kivy
- kivy-garden.graph
- mesa libgl x11 dependencies?

**Windows**
```
python -m pip install kivy kivy-garden
# set environment path to python's scripts folder
garden install graph
```

# Testing on PC
You can test the app on PC. The python program will use
artificial readings if you do.

If you are running NixOS then do `nix-shell` which will get you necessary dependencies.