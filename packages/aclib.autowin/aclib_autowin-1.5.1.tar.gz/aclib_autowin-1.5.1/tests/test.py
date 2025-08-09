
from aclib.autowin import AppWindow

app = AppWindow.newoverlapped()
print(app.create().loop())