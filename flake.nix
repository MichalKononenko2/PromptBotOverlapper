{
  description = "The Content Assessment and LLM Tokenization App";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
    gitignore = {
      url = "github:hercules-ci/gitignore.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, gitignore }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        packages = with pkgs; [
          nodejs_20
          typescript
          nodePackages.npm
        ];
        app = pkgs.stdenv.mkDerivation {
          name = "content-evaluator-dev";
          version = "0.0.1";
          src = gitignore.lib.gitignoreSource ./.;
          buildInputs = packages;
          buildPhase = ''
            runHook preBuild
            npm run build
            runHook postBuild
          '';
          installPhase = ''
            runHook preInstall
            mkdir -p $out/bin
            cp package.json $out/package.json
            cp -r dist $out/dist
            cp dist/index.js $out/bin/example-ts-nix
            chmod a+x $out/bin/example-ts-nix

            runHook postInstall
          '';
        };
      in
      {
        defaultPackage = app;
        devShell = pkgs.mkShell {
          name = "content-evaluator-dev";

          # Packages necessary for developing a TypeScript/Angular app
          packages = packages; 
          # Environment variables and setup commands
          shellHook = ''
            echo "--- Welcome to the Content Evaluator Dev Shell ---"
            echo "Node.js (v20) and TypeScript are available."
            echo "You can start development by installing dependencies (e.g., 'npm install')."
          '';
        };
      }
    );
}

