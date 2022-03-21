# Installation

How to install:
```
pip3 install git+https://github.com/design-group/ignition-selenium.git#egg=perspective_automation
```

To install a version from a specific branch, add `@branch_name` after `test-automation.git`. For example, when cloning from a branch called `my_branch`:
```
pip3 install git+https://github.com/design-group/ignition-selenium.git@my_branch##egg=perspective_automation
```

For local testing of new features, you can also install your local copy of this repository as a package. 
Prior to installation, one should create a (virtual environment)[https://docs.python.org/3/library/venv.html], to make sure the version in this folder does not conflict with an existing installation.
```
pip install -e /path/to/repo/
```

## Common Issues

If you are switching between versions, use the `-U` flag in your `pip install` command:

If you are having problems installing due to SSL/TLS certificate verification issues, include the following options between `install` and the Git URL:
```
--trusted-host pypi.org
```
