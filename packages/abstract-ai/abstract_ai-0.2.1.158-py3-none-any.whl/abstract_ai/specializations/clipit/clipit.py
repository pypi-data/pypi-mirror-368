# clipit/__init__.py

import sys
import os
import threading
import webbrowser

def initialize_clipit(choice="display", port=None):
    """
    Start the GUI, client, script, or Flask server, depending on `choice`.
    If `choice == "flask"`, also open the browser to the drop-n-copy page.
    """

    if choice == "display":
        from abstract_ai.specializations.clipit.src.gui_frontend import gui_main
        gui_main()

    elif choice == "client":
        from abstract_ai.specializations.clipit.src.client import client_main
        client_main()

    elif choice == "script":
        # … your script logic here …
        print("Running in script mode (not implemented).")

    elif choice == "flask":
        # Default port if none given
        if port is None:
            port = 7823

        # Import and create the Flask app
        from abstract_ai.specializations.clipit.src.flask import abstract_clip_app
        app = abstract_clip_app()

        # Build the URL we want the browser to open
        url = f"http://127.0.0.1:{port}/drop-n-copy.html"
        print(f"→ Opening browser to: {url}")

        # Start a timer that waits 1 second, then opens the URL in the default browser.
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

        # Finally, run the Flask dev server (this blocks).
        app.run(debug=True, port=port)

    else:
        raise ValueError(f"Unknown mode: {choice!r}")

if __name__ == "__main__":
    choice = sys.argv[1] if len(sys.argv) > 1 else "display"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else None
    initialize_clipit(choice, port=port)
