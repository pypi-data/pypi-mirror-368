{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShell = pkgs.mkShell {
          # Provide the base tools for your environment.
          # Nix provides the Python *interpreter* and the *uv command*.
          # uv manages all the python *packages*.
          buildInputs = [
            pkgs.python313 # The interpreter you want.
            pkgs.uv # The standalone uv command.

            # Your other system-level tools.
            pkgs.gfortran
            pkgs.rustc
            pkgs.cargo
            pkgs.aider-chat
          ];

          # This script runs automatically when you enter the shell.
          shellHook = ''
            # Set the virtual environment directory.
            VENV_DIR=".venv"

            # Create the virtual environment with uv if it doesn't exist.
            if [ ! -d "$VENV_DIR" ]; then
              echo "Creating new uv virtual environment in $VENV_DIR..."
              # Use the Python 3.13 provided by Nix as the base.
              uv venv -p python3.13 $VENV_DIR
            fi

            # Activate the virtual environment.
            source "$VENV_DIR/bin/activate"

            # Install/update packages from your pyproject.toml.
            # This is the equivalent of 'pip install -r requirements.txt'.
            echo "Syncing dependencies with pyproject.toml..."
            uv pip sync pyproject.toml

            echo "Environment is ready."
          '';
        };
      }
    );
}
