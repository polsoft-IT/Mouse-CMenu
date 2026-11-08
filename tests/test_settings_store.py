import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from app_launcher import launch_application
from settings_store import AppSettings, MenuEntry, SettingsStore


class SettingsStoreTests(unittest.TestCase):
    def test_round_trips_nested_menu_entries(self) -> None:
        with TemporaryDirectory() as directory:
            store = SettingsStore(Path(directory) / "settings.json")
            settings = AppSettings(
                language="pl",
                shortcut="wheel_down",
                show_app_icons=True,
                run_at_startup=True,
                menu_entries=(
                    MenuEntry(
                        kind="submenu",
                        label="Grafika",
                        children=(
                            MenuEntry(
                                kind="app",
                                label="Paint",
                                command="C:/Windows/mspaint.exe",
                                icon="C:/Icons/paint.ico",
                            ),
                        ),
                    ),
                ),
            )

            store.save(settings)

            self.assertEqual(store.load(), settings)

    def test_invalid_field_types_fall_back_without_crashing(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text(
                '{"language": [], "shortcut": [], "show_app_icons": [], '
                '"run_at_startup": [], '
                '"menu_entries": [{"kind": [], "label": "Bad"}]}'
            )

            self.assertEqual(SettingsStore(path).load(), AppSettings())

    def test_failed_replace_preserves_previous_settings(self) -> None:
        with TemporaryDirectory() as directory:
            store = SettingsStore(Path(directory) / "settings.json")
            original = AppSettings(language="pl")
            store.save(original)

            with patch("settings_store.os.replace", side_effect=OSError("simulated replace failure")):
                with self.assertRaises(OSError):
                    store.save(AppSettings(language="en"))

            self.assertEqual(store.load(), original)


class AppLauncherTests(unittest.TestCase):
    @patch("app_launcher.os.startfile")
    @patch("app_launcher.subprocess.Popen")
    def test_executable_starts_directly_with_its_folder_as_working_directory(
        self,
        popen,
        startfile,
    ) -> None:
        application_path = r"C:\Program Files\My App\app.exe"

        launch_application(application_path)

        popen.assert_called_once_with(
            [application_path],
            cwd=str(Path(application_path).resolve().parent),
            shell=False,
        )
        startfile.assert_not_called()

    @patch("app_launcher.os.startfile")
    @patch("app_launcher.subprocess.Popen")
    def test_shortcut_is_opened_by_windows_shell(self, popen, startfile) -> None:
        application_path = r"C:\Users\Public\Desktop\My App.lnk"

        launch_application(application_path)

        startfile.assert_called_once_with(application_path)
        popen.assert_not_called()


if __name__ == "__main__":
    unittest.main()