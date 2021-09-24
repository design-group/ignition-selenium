
# Installation

How to install:
```
pip install git+ssh://git@git.ejgallo.com/operational_technology/ignition/infrastructure/test-automation.git#egg=perspective_automation
```

How to install a version from a specific branch:
```
pip install git+ssh://git@git.ejgallo.com/operational_technology/ignition/infrastructure/test-automation.git@branch_name#egg=perspective_automation
```

## Common Issues

If you are switching between versions, or just need to reinstall, uninstall the existing version first:
```
pip uninstall perspective_automation
```

If you are having problems installing due to SSL/TLS certificate verification issues, include the following options between `install` and the Git URL:
```
--trusted-host pypi.org
```