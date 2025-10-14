import subprocess


class AndroidEmulator:
    """A class to interact with an Android emulator via ADB commands."""

    def __init__(self, emulator_name: str = "emulator-5554"):
        """
        Args:
            emulator_name: The name or serial of the emulator instance. Defaults to "emulator-5554".
        """
        self.emulator_name = emulator_name
        self._root_adb_device()

    def _root_adb_device(self):
        """
        Enables root mode on the adb device if not yet enabled. This causes a restart of adbd on the
        device and the connection to the devices is temporarily lost.
        """
        subprocess.check_output(
            ["adb", "-s", self.emulator_name, "root"], encoding="UTF-8"
        )
        subprocess.check_output(
            ["adb", "-s", self.emulator_name, "wait-for-device"], encoding="UTF-8"
        )

    def _send_adb_command(self, cmd):
        return subprocess.check_output(
            ["adb", "-s", self.emulator_name] + cmd, encoding="UTF-8"
        )

    def send_fix(self, lon: str, lat: str) -> str:
        """
        Send a geo fix command to the emulator to set its GPS location.

        Args:
            lon: Longitude value.
            lat: Latitude value.

        Returns:
            str: The output from the ADB command.
        """
        return self._send_adb_command(["emu", "geo", "fix", lon, lat])
