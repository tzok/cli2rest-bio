{ pkgs, ... }:
{
  languages.python = {
    enable = true;
    venv = {
      enable = true;
      requirements = ./requirements.txt;
    };
  };
  packages = with pkgs; [
    pyright
    zlib
  ];
}
