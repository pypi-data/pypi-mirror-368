from argparse import Namespace

from hike.data.config import update_configuration
from hike.hike import Hike

# Ensure that Hike's configuration starts out the same way each time.
with update_configuration() as config:
    config.navigation_on_right = False
    config.command_line_on_top = False
    config.focus_viewer_on_load = False

app = Hike(Namespace(theme="textual-mono", navigation=False, command=["README.md"]))
if __name__ == "__main__":
    app.run()
