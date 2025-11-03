#!/usr/bin/python3

import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

import subprocess
from pathlib import Path

DBusGMainLoop(set_as_default=True)

SERVICE = "krunner.customcmd"
OBJPATH = "/runner" # Default value for X-Plasma-DBusRunner-Path metadata property
IFACE = "org.kde.krunner1"

CMD_TIMEOUT = 5  # seconds

class Runner(dbus.service.Object):
    def __init__(self):
        dbus.service.Object.__init__(self, dbus.service.BusName(SERVICE, dbus.SessionBus()), OBJPATH)

        self.cmds = {}

        for cmd_file in Path("./cmds").iterdir():
            if cmd_file.is_file() and cmd_file.stat().st_mode & 0o111:
                print("Found command file:", cmd_file)
                cmd_file_name = cmd_file.stem
                cmd_file_path = cmd_file.resolve()
                print(f"Command file name: {cmd_file_name}")
                print(f"Command file path: {cmd_file_path}")
                self.cmds[cmd_file_name] = str(cmd_file_path)

    @dbus.service.method(IFACE, in_signature='s', out_signature='a(sssida{sv})')
    def Match(self, query: str):
        """This method is used to get the matches and it returns a list of tuples"""
        print("Match: query=", query)
        fields = query.split(maxsplit=1)
        if len(fields) < 2:
            return []
        cmd = fields[0]        
        if cmd in self.cmds:
            print("Found command:", cmd, "->", self.cmds[cmd])
            cmd_file_path = self.cmds[cmd]
            try:
                result = subprocess.run([cmd_file_path, fields[1]], capture_output=True, text=True, timeout=CMD_TIMEOUT)
                if result.returncode != 0:
                    print("Command failed with return code:", result.returncode)
                    return []
                result_text = result.stdout.strip()
                print("Command output:", result_text)
                if len(result_text) == 0:
                    return []
                # data, text, icon, type (KRunner::QueryType), relevance (0-1), properties (subtext, category, multiline(bool) and urls)
                return [("cmd", result_text, "new-command-alarm", 100, 1.0, {})]
            except subprocess.TimeoutExpired:
                print("Command timed out")
                return []
        return []

    @dbus.service.method(IFACE, out_signature='a(sss)')
    def Actions(self):
        print("Actions:")
        # id, text, icon
        return []

    @dbus.service.method(IFACE, in_signature='ss')
    def Run(self, data: str, action_id: str):
        print("Run: data=", data, "action_id=", action_id)
        print(data, action_id)


runner = Runner()
loop = GLib.MainLoop()
loop.run()
