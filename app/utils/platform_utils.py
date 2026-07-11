"""Platform detection + Android runtime-permission helpers.

On desktop every function is a safe no-op, so the same code runs on Windows for
development and on Android in the packaged APK. Android-only imports
(``android.permissions``, ``plyer``) are done lazily inside ``try`` blocks —
they don't exist on desktop and must never break import.
"""

from kivy.utils import platform


def is_android():
    return platform == "android"


def request_camera_permissions(callback=None):
    """Ask for CAMERA + storage at point-of-use (Android 6+ requires runtime grants).

    ``callback(granted: bool)`` is invoked when done. On desktop we report True.
    """
    if not is_android():
        if callback:
            callback(True)
        return
    try:
        from android.permissions import request_permissions, Permission

        def _on_result(perms, grants):
            if callback:
                callback(all(grants))

        request_permissions(
            [Permission.CAMERA,
             Permission.READ_EXTERNAL_STORAGE,
             Permission.WRITE_EXTERNAL_STORAGE],
            _on_result,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[permissions] request failed: {exc}")
        if callback:
            callback(False)


def request_notification_permission():
    """Android 13+ (API 33) needs a runtime grant to post notifications."""
    if not is_android():
        return
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.POST_NOTIFICATIONS])
    except Exception:  # noqa: BLE001 - older Android / desktop
        pass
