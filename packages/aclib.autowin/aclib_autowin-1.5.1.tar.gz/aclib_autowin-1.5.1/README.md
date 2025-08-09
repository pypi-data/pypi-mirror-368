# Installation

### General
    pip install aclib.autowin
### Work with dm
    pip install aclib.autowin[dm]
### Work with cv
    pip install aclib.autowin[cv]
### Full installation
    pip install aclib.autowin[full]


# Usage

```python
# base typing
from aclib.autowin import _Pos, _Size, _Area, _Areas
# base api
from aclib.autowin import BaseWindow, screen, Window

# create win32 application
from aclib.autowin.appwindow import AppWindow
# css typing
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from aclib.autowin.appwindow._typing import _AppCSS

# use opencv
from aclib.autowin.cvwindow import CvWindow     # [cv] requires

# use dm plugin
from aclib.autowin.dmwindow import DmWindow     # [dm] requires

```
