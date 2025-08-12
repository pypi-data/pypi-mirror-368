import sys
from pathlib import Path
from setuptools import setup


def abs_script_dir():
    """ Return the absolute path to the directory this script is located in. """
    return Path(__file__).resolve().parent


def get_version_number():
    """
    Extract version number from VERSION.md if it exists, otherwise extract it
    from the CI configuration in the SDK root folder. The VERSION.md file is
    created by CI and contains ENSENSO_SDK_VERSION.
    """
    version_file = abs_script_dir() / "VERSION.md"
    if version_file.is_file():
        with version_file.open("rt") as f:
            return f.read().strip()

    ci_config_file = abs_script_dir().parent / ".gitlab-ci.yml"
    major, minor = "", ""
    major_str, minor_str = "ENSENSO_SDK_VERSION_MAJOR", "ENSENSO_SDK_VERSION_MINOR"
    if not ci_config_file.is_file():
        p = ci_config_file.resolve()
        raise FileNotFoundError(f"CI configuration not found in {p}")
    with ci_config_file.open("rt") as f:
        for line in f:
            if major_str in line:
                major = line.split(":")[1].strip()
            if minor_str in line:
                minor = line.split(":")[1].strip()
            if minor and major:
                return major + "." + minor + ".0"
    raise NameError(f"{major_str} or {minor_str} not found in CI configuration")


readme_file = abs_script_dir() / "README.md"
with readme_file.open(encoding='utf-8') as f:
    long_description = f.read()


package_name = "nxlib"
if "--package-name" in sys.argv:
    package_name = sys.argv[2]
    del sys.argv[1:3]


setup(name=package_name,
      packages=["nxlib", "ensenso_nxlib"],
      python_requires=">3.5.0",
      version=get_version_number(),
      description="Python interface to interact with the Ensenso NxLib",
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3",
      ],
      url="https://www.ensenso.com/python-api",
      author="Optonic GmbH",
      author_email="support@optonic.com",
      license="MIT",
      install_requires=[
          "numpy",
      ],
      zip_safe=False,
      extras_require={
      })
