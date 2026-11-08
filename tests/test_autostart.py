import unittest
import winreg
from unittest.mock import patch

from autostart import RUN_KEY, RUN_VALUE_NAME, build_startup_command, set_run_at_startup


class AutostartTests(unittest.TestCase):
    def test_script_startup_command_quotes_paths(self) -> None:
        command = build_startup_command(
            executable=r"C:\Python 3\python.exe",
            script_path=r"C:\Users\max\Desktop\Mouse CMenu\main.py",
            frozen=False,
        )

        self.assertEqual(
            command,
            '"C:\\Python 3\\python.exe" '
            '"C:\\Users\\max\\Desktop\\Mouse CMenu\\main.py"',
        )

    def test_frozen_startup_command_uses_executable_only(self) -> None:
        command = build_startup_command(
            executable=r"C:\Program Files\Context Menu.exe",
            script_path=r"C:\ignored\main.py",
            frozen=True,
        )

        self.assertEqual(command, '"C:\\Program Files\\Context Menu.exe"')

    @patch("autostart.winreg.CloseKey")
    @patch("autostart.winreg.SetValueEx")
    @patch("autostart.winreg.CreateKeyEx", return_value=123)
    def test_enable_writes_run_registry_value(self, create_key, set_value, close_key) -> None:
        set_run_at_startup(True, '"C:\\Context Menu.exe"')

        create_key.assert_called_once_with(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY,
            0,
            winreg.KEY_SET_VALUE,
        )
        set_value.assert_called_once_with(
            123,
            RUN_VALUE_NAME,
            0,
            winreg.REG_SZ,
            '"C:\\Context Menu.exe"',
        )
        close_key.assert_called_once_with(123)

    @patch("autostart.winreg.CloseKey")
    @patch("autostart.winreg.DeleteValue")
    @patch("autostart.winreg.OpenKey", return_value=456)
    def test_disable_removes_run_registry_value(self, open_key, delete_value, close_key) -> None:
        set_run_at_startup(False)

        open_key.assert_called_once_with(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY,
            0,
            winreg.KEY_SET_VALUE,
        )
        delete_value.assert_called_once_with(456, RUN_VALUE_NAME)
        close_key.assert_called_once_with(456)


if __name__ == "__main__":
    unittest.main()