with import <nixpkgs> {};

mkShell {
    nativeBuildInputs = [ pkg-config ];
    buildInputs = [
        python313
        python313Packages.pip
        python313Packages.kivy
        python313Packages.kivy-garden
        
        # I think we need these
        SDL2 libGL xorg.libX11 freetype mesa libdrm

        # maybe need these?
        kdePackages.qtbase libglvnd dbus.dev
        pkgs.wayland.dev
        wayland-scanner
        wayland-protocols
        libxkbcommon
    ];
}