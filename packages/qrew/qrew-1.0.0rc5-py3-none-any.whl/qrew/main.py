#!/usr/bin/env python3
"""
Main entry point for Qrew application
"""
import os
import sys
import time
import platform
import signal
from threading import Thread
import socket
import requests

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Add the frozen application path for imports
if getattr(sys, "frozen", False):
    # Running as PyInstaller bundle
    application_path = sys._MEIPASS
    sys.path.insert(0, application_path)
    sys.path.insert(0, os.path.join(application_path, "qrew"))

# Force Windows to use IPv4 for all requests
if platform.system() == "Windows":
    # import requests.packages.urllib3.util.connection as urllib3_cn  # this is for older versions
    import urllib3.util.connection as urllib3_cn

    def allowed_gai_family():
        """Force IPv4 only for Windows"""
        return socket.AF_INET  # Force IPv4 only

    urllib3_cn.allowed_gai_family = allowed_gai_family


try:
    # Try with qrew prefix first for PyInstaller bundles
    from qrew.Qrew import (
        MainWindow,
        wait_for_rew_qt,
        check_rew_pro_license_or_exit,
        shutdown_handler,
        set_app_icon_cross_platform,
    )
    from qrew.Qrew_api_helper import initialize_rew_subscriptions
    from qrew.Qrew_message_handlers import run_flask_server, stop_flask_server
    from qrew.Qrew_styles import GLOBAL_STYLE, get_dark_palette, get_light_palette
    import qrew.Qrew_settings as qs
    from qrew.Qrew_messagebox import QrewMessageBox
    from qrew.Qrew_find_vlc import get_vlc_status
    from qrew.Qrew_dialogs import MultipleInstancesDialog
except ImportError:
    try:
        # Try with direct imports for development mode
        from Qrew import (
            MainWindow,
            wait_for_rew_qt,
            check_rew_pro_license_or_exit,
            shutdown_handler,
            set_app_icon_cross_platform,
        )
        from Qrew_api_helper import initialize_rew_subscriptions
        from Qrew_message_handlers import run_flask_server, stop_flask_server
        from Qrew_styles import GLOBAL_STYLE, get_dark_palette, get_light_palette
        import Qrew_settings as qs
        from Qrew_messagebox import QrewMessageBox
        from Qrew_find_vlc import get_vlc_status
        from Qrew_dialogs import MultipleInstancesDialog
    except ImportError:
        try:
            # Try with relative imports as last resort
            from .Qrew import (
                MainWindow,
                wait_for_rew_qt,
                check_rew_pro_license_or_exit,
                shutdown_handler,
                set_app_icon_cross_platform,
            )
            from .Qrew_api_helper import initialize_rew_subscriptions
            from .Qrew_message_handlers import run_flask_server, stop_flask_server
            from .Qrew_styles import GLOBAL_STYLE, get_dark_palette, get_light_palette
            from . import Qrew_settings as qs
            from .Qrew_messagebox import QrewMessageBox
            from .Qrew_find_vlc import get_vlc_status
            from .Qrew_dialogs import MultipleInstancesDialog
        except ImportError as e:
            print(f"Failed to import Qrew modules: {e}")
            print("Current sys.path:", sys.path)
            sys.exit(1)


def main():
    """Main application entry point"""
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # Check if another instance is already running
    def check_existing_instance():
        """Check if another Qrew instance is running on port 5555"""

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(("127.0.0.1", 5555))
                if result == 0:
                    print("⚠️  Another instance of Qrew appears to be running")
                    print("   Qrew can only run one instance at a time")
                    print("   Application will exit after showing warning dialog")
                    return True
        except (socket.error, OSError):
            pass
        return False

    # Check for existing instance and prepare to exit if found
    instance_conflict = check_existing_instance()

    # Start Flask server (skip if instance conflict detected)
    if not instance_conflict:
        try:
            flask_thread = Thread(target=run_flask_server, daemon=True)
            flask_thread.start()
            print("🔄 Flask server thread started...")

            # Give Flask server more time to start under PyInstaller
            time.sleep(2)

            # Check Flask server in a non-blocking way
            def check_flask_async():
                """Check Flask server asynchronously"""

                def check():
                    try:
                        response = requests.get(
                            "http://127.0.0.1:5555/health", timeout=2
                        )
                        if response.status_code == 200:
                            print("✅ Flask server verified running")
                        else:
                            print(f"⚠️  Flask server code {response.status_code}")
                    except (
                        requests.ConnectionError,
                        requests.Timeout,
                        requests.RequestException,
                    ) as e:
                        print(f"⚠️  Flask server verification failed: {e}")
                        print("   Continuing anyway, REW subscriptions may not work")

                Thread(target=check, daemon=True).start()

            check_flask_async()

        except (RuntimeError, ValueError, ConnectionError, OSError) as e:
            print(f"❌ Failed to start Flask server: {e}")
            print("   Application will continue but REW integration may not work")
    else:
        print("   Skipping Flask server startup due to instance conflict")
    # Create Qt application
    app = QApplication(sys.argv)
    # Set application icon (for taskbar/dock)
    app.setOrganizationName("Docdude")
    app.setApplicationName("Qrew")
    app.setApplicationDisplayName("Qrew")

    # Set cross-platform icon
    set_app_icon_cross_platform(app)
    app.setStyle("Fusion")
    app.setStyleSheet(GLOBAL_STYLE)
    use_light = qs.get("use_light_theme", False)
    palette = get_light_palette() if use_light else get_dark_palette()

    app.instance().setPalette(palette)

    # Check for VLC errors using centralized management
    def check_and_show_vlc_errors():
        """Check for VLC errors and show dialog if needed using centralized VLC management"""

        vlc_status = get_vlc_status()
        if vlc_status.get("error_message"):
            error_msg = vlc_status["error_message"]
            # Show warning but don't exit
            QrewMessageBox.warning(
                None,
                error_msg.get("title", "VLC Warning"),
                error_msg.get("text", "VLC not found")
                + "<br>You can still use the application, but audio playback will not work.",
            )

    # Check for instance conflict and show critical dialog
    def check_and_handle_instance_conflict():
        """Show critical dialog and exit if another instance is running"""
        if instance_conflict:
            #   QrewMessageBox.critical(
            #      None,
            #     "Multiple Instances Not Supported",
            #    "Another instance of Qrew is already running.<br>"
            #       "Each instance needs exclusive access to REW API<br>"
            #      "Click OK to exit this instance.",
            #  )
            # Gracefully exit after user acknowledges
            # Show dialog for retry/exit
            dialog = MultipleInstancesDialog()
            dialog_result = dialog.exec_()

            if dialog_result == 0:  # Exit button clicked
                sys.exit(1)
        #  QTimer.singleShot(100, lambda: sys.exit(0))

    # Schedule error checks after Qt initialization
    if instance_conflict:
        QTimer.singleShot(100, check_and_handle_instance_conflict)
    else:
        QTimer.singleShot(100, check_and_show_vlc_errors)

    # Check REW connection (skip if instance conflict)
    if not instance_conflict:
        wait_for_rew_qt()
        check_rew_pro_license_or_exit()

        # Initialize all subscriptions in background thread
        def init_subscriptions():
            try:
                initialize_rew_subscriptions()
                print("✅ REW subscriptions initialized")
            except (
                requests.ConnectionError,
                requests.Timeout,
                ValueError,
                ConnectionRefusedError,
            ) as e:
                print(f"⚠️  Failed to initialize REW subscriptions: {e}")
                print("   You may need to restart the application")

        init_thread = Thread(target=init_subscriptions)
        init_thread.daemon = True
        init_thread.start()
    else:
        print("   Skipping REW initialization due to instance conflict")

    # Create and show main window
    window = MainWindow()
    window.show()

    try:
        exit_code = app.exec_()
    finally:
        # Ensure Flask server is stopped on exit (if it was started)
        if not instance_conflict:
            print("🛑 Shutting down Flask server...")
            stop_flask_server()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
