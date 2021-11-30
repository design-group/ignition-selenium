# Installation

How to install:
```
pip install git+ssh://git@git.ejgallo.com/operational_technology/ignition/infrastructure/test-automation.git#egg=perspective_automation
```

To install a version from a specific branch, add `@branch_name` after `test-automation.git`. For example, when cloning from a branch called `my_branch`:
```
pip install git+ssh://git@git.ejgallo.com/operational_technology/ignition/infrastructure/test-automation.git@my_branch#egg=perspective_automation
```

You can also install your local copy of this repository as a package (great for if you need to quickly test new features):
```
pip install -e /path/to/repo/
```

## Common Issues

If you are switching between versions, use the `-U` flag in your `pip install` command:

If you are having problems installing due to SSL/TLS certificate verification issues, include the following options between `install` and the Git URL:
```
--trusted-host pypi.org
```
