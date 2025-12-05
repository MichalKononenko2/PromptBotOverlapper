{
  lib,
  python3Packages
}:
with python3Packages;
buildPythonApplication {
  pname="promptbot_overlapper";
  version = "1.0";
  propagatedBuildInputs = [ flask requests ];
  src = ./.;
}

