##  Installation

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

## Example Usage

```python
# Library requires import of the component you will be interacting with
from perspective_automation.components import Button
import time

def test_example():
    # Specify URL that selenium will try to locate the component on.
	PAGE_PATH = "/data/perspective/client/OnlineDemo/apps/preparedfoodsline"
	BASE__URL = "https://demo.ia.io"

    # Create your session and specify an alias that will be used in the block
    with Session(base_url=BASE__URL, page_path=PAGE_PATH, wait_timeout_in_seconds=3, headless=False) as session:

        # Create your component and specify the locator type and value
        my_button = BUtton(session, By.ID, "myButtonID")

        # Interaction and Unit Testing Below 
        my_button.click()

        # Wait for 10 seconds so user can see the result of the interaction.
        time.sleep(10)

```