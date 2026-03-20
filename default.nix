{ lib
, buildPythonPackage
, python
, aiofiles
}:

buildPythonPackage rec {
  pname = "aiolaunchpad";
  version = "unstable-2017-07-20";
  format = "other";

  src = ./.;

  propagatedBuildInputs = [
    aiofiles
  ];

  dontBuild = true;

  installPhase = ''
    runHook preInstall
    install -Dm644 aiolaunchpad.py "$out/${python.sitePackages}/aiolaunchpad.py"
    runHook postInstall
  '';

  pythonImportsCheck = [
    "aiolaunchpad"
  ];

  meta = with lib; {
    description = "AsyncIO framework to control Novation Launch controllers from Python";
    homepage = "https://github.com/hoh/aiolaunchpad";
    license = licenses.asl20;
    platforms = platforms.unix;
  };
}
