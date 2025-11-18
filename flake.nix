{
  description = "PsychoPy ErrP Experiment Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        python = pkgs.python311;

        pythonEnv = python.withPackages (ps: with ps; [
          psychopy
          pylsl
          numpy
          pandas
          # Additional dependencies that PsychoPy might need
          pillow
          scipy
          matplotlib
          pyglet
          # For PsychoPy GUI
          wxpython
        ]);

      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.labstreaminglayer
            # For GUI support
            pkgs.xorg.libX11
            pkgs.xorg.libXext
            pkgs.xorg.libXrender
            pkgs.libGL
            pkgs.libGLU
          ];

          shellHook = ''
            echo "PsychoPy ErrP Experiment Environment"
            echo "====================================="
            echo "Python version: $(python --version)"
            echo "PsychoPy installed: $(python -c 'import psychopy; print(psychopy.__version__)')"
            echo ""
            echo "To run Task 1: python task1_observation_errp.py"
            echo "To test LSL: python test_lsl.py"
            echo ""
          '';

          # Environment variables for proper display
          DISPLAY = ":0";
          XDG_RUNTIME_DIR = "/run/user/$(id -u)";
        };

        packages.default = pythonEnv;
      }
    );
}
