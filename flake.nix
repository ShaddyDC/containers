{
  description = "Description for the project";

  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = inputs @ {flake-parts, ...}:
    flake-parts.lib.mkFlake {inherit inputs;} {
      systems = ["x86_64-linux" "aarch64-linux" "aarch64-darwin" "x86_64-darwin"];
      perSystem = {pkgs, ...}: {
        devShells.default = let
          myPy = pkgs.python313.withPackages (ps: with ps; [google-generativeai requests]);
        in
          pkgs.mkShell {
            packages = with pkgs; [
              uv
              myPy 
            ];
            UV_PYTHON_PREFERENCE = "only-system";
            UV_PYTHON = "${myPy }";
          };
      };
    };
}
