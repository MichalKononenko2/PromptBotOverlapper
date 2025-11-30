# Installation

Install ``nix'' to get started. You can get it [here](https://zero-to-nix.com/concepts/nix-installer/).
To quote from ``zero-to-nix.com``, you can install nix by running

```
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
```

After installing, run ``nix develop`` to get a development shell.

# Running the Program

The python script ```prompt_generator.py``` generates the prompt to be sent into the model of your
choice. The Angular JS code is to be window dressing around this. Run that script in a Python
interpreter to start.
