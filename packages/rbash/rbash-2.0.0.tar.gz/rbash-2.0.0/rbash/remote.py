#!/usr/bin/env python3
"""
RemoteSession: use subprocess(ssh) to:
1) prepare(): create remote temp SSH key + workspace, hold pubkey
2) run(): add pubkey to LOCAL authorized_keys, open reverse tunnel, sshfs mount, bash
3) clean(): unmount + remove remote workspace and temp keys, and tidy keys (local + remote)
"""

import os
import shlex
import socket
import getpass
import random
import subprocess
from pathlib import Path


class RemoteSession:
    def __init__(self, host: str, local_path: str = ".", base_port: int = 2222, strict_host_check: bool = False):
        self.host = host
        self.local_path = os.path.abspath(local_path)
        self.local_user = getpass.getuser()
        self.base_port = base_port
        self.workspace = f"workspace{random.randint(10_000_000, 99_999_999)}"
        self.pubkey = ""                     # set by prepare()
        self.pubkey_tag = f"# rbash-temp-key-{self.workspace}"
        self.remote_port = None              # set in run()
        self.strict = strict_host_check

        # SSH options (suppress host prompts unless strict=True)
        self.ssh_opts = []
        if not self.strict:
            self.ssh_opts += ["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/tmp/knowshosts"]

        if not self._host_in_ssh_config():
            print(f"⚠️  SSH host '{host}' not found in ~/.ssh/config — proceeding anyway.")

        #print(f"✅ init: host={self.host}  local_user={self.local_user}  local_path={self.local_path}  ws=~/{self.workspace}")

    # ---------- helpers ----------
    @staticmethod
    def _find_free_local_port(start=2222, end=2300) -> int:
        for port in range(start, end):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("127.0.0.1", port))
                    return port
                except OSError:
                    continue
        raise RuntimeError("No available local port found in range.")

    def _host_in_ssh_config(self) -> bool:
        cfg = Path.home() / ".ssh" / "config"
        if not cfg.exists():
            return False
        with cfg.open() as f:
            for line in f:
                s = line.strip()
                if s.lower().startswith("host ") and not s.lower().startswith("host *"):
                    parts = s.split()
                    if len(parts) >= 2 and parts[1] == self.host:
                        return True
        return False

    def _ssh(self, remote_cmd: str, *, add_tty: bool = False, r_port: int | None = None, l_port: int | None = None, check: bool = True):
        cmd = ["ssh"]
        if add_tty:
            cmd.append("-t")
        cmd += self.ssh_opts
        if r_port and l_port:
            cmd += ["-R", f"{r_port}:localhost:{l_port}"]
        cmd += [self.host, remote_cmd]
        return subprocess.run(cmd, check=check)

    def _ssh_out(self, remote_cmd: str) -> str:
        cmd = ["ssh", *self.ssh_opts, self.host, remote_cmd]
        return subprocess.check_output(cmd, text=True)

    # ---------- public ops ----------
    def prepare(self):
        """
        Remote:
          - ensure ~/.ssh and ~/workspaceX
          - generate ~/.ssh/id_rbash
          - print id_rbash.pub (captured to self.pubkey)
        """
        #print("🔧 prepare(): creating remote key + workspace ...")
        remote_cmd = (
            f"mkdir -p ~/{self.workspace} ~/.ssh && "
            "chmod 700 ~/.ssh && "
            "rm -f ~/.ssh/id_rbash ~/.ssh/id_rbash.pub && "
            "ssh-keygen -t rsa -N '' -f ~/.ssh/id_rbash -q && "
            "cat ~/.ssh/id_rbash.pub"
        )
        try:
            self.pubkey = self._ssh_out(remote_cmd).strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"prepare() failed on {self.host}: {e}") from e
        if not self.pubkey.startswith("ssh-"):
            raise RuntimeError("prepare(): remote pubkey did not look like an SSH key")
        #print("🔑 remote pubkey acquired.")

    def run(self):
        """
        - Append remote pubkey (from prepare) into LOCAL authorized_keys (tagged)
        - Choose a free local port; open ssh with -R remote_port:localhost:22
        - On remote: ensure fuse/sshfs, sshfs mount using IdentityFile=~/.ssh/id_rbash, then interactive bash
        - On exit: remove pubkey from local authorized_keys
        """
        if not self.pubkey:
            raise RuntimeError("run(): no pubkey loaded. Call prepare() first.")

        # Add pubkey to LOCAL authorized_keys (so remote can SSH back to local via tunnel)
        ak = Path.home() / ".ssh" / "authorized_keys"
        ak.parent.mkdir(parents=True, exist_ok=True)
        current = ak.read_text() if ak.exists() else ""
        if self.pubkey not in current:
            with ak.open("a") as f:
                f.write(f"\n{self.pubkey} {self.pubkey_tag}\n")
            #print("➕ added remote pubkey to LOCAL authorized_keys")

        # choose reverse remote port (listens on remote, forwards to our local sshd on 127.0.0.1:22)
        self.remote_port = self._find_free_local_port(self.base_port, self.base_port + 1000)
        #print(f"🔁 reverse tunnel port: {self.remote_port}")

        remote_bash = (
            "set -euo pipefail; "
            # fuse load (with sudo fallback if present)
            "(modprobe fuse 2>/dev/null || (command -v sudo >/dev/null && sudo modprobe fuse) || true); "
            # require sshfs
            "if ! command -v sshfs >/dev/null; then echo '❌ sshfs not found on remote'; exit 1; fi; "
            f"mkdir -p ~/{self.workspace}; "
            f"sshfs -p {self.remote_port} "
            f"-o IdentityFile=~/.ssh/id_rbash "
            f"-o StrictHostKeyChecking=no -o UserKnownHostsFile=/tmp/knownhosts "
            f"{self.local_user}@localhost:{shlex.quote(self.local_path)} ~/{self.workspace} && "
            f"cd ~/{self.workspace} && exec bash || exec bash"
        )

        # Launch interactive ssh with reverse port
        cmd_preview = ["ssh", "-t", *self.ssh_opts, "-R", f"{self.remote_port}:localhost:22", self.host, remote_bash]
        #print("🚀 launching shell with reverse sshfs mount:\n   ", shlex.join(cmd_preview))
        try:
            subprocess.run(cmd_preview, check=False)
        finally:
            # always remove LOCAL pubkey entry after session
            try:
                if ak.exists():
                    cleaned = "\n".join(line for line in ak.read_text().splitlines() if self.pubkey_tag not in line)
                    if cleaned and not cleaned.endswith("\n"):
                        cleaned += "\n"
                    ak.write_text(cleaned)
                    #print("🗑️  removed remote pubkey from LOCAL authorized_keys")
            except Exception as e:
                print(f"⚠️ failed to tidy local authorized_keys: {e}")

    def clean(self):
        """
        Remote cleanup:
          - try to umount workspace (lazy if necessary)
          - remove workspace dir
          - remove id_rbash keys
          - remove our pubkey line from remote authorized_keys (best-effort)
        """
        #print("🧹 clean(): remote unmount + key cleanup ...")

        # unmount if mounted
        remote_unmount = (
            f"(mount | grep -q '/{self.workspace} ') && "
            f"(fusermount -uz ~/{self.workspace} 2>/dev/null || umount -l ~/{self.workspace} 2>/dev/null || true); true"
        )
        self._ssh(remote_unmount, check=False)

        # remove dir + temp keys
        remote_rm = (
            f"rm -rf ~/{self.workspace} 2>/dev/null || true; "
            "rm -f ~/.ssh/id_rbash ~/.ssh/id_rbash.pub 2>/dev/null || true"
        )
        self._ssh(remote_rm, check=False)

        # remove our pubkey from remote authorized_keys (not strictly required for reverse sshfs, but tidy)
        if self.pubkey:
            escaped = self.pubkey.replace("/", r"\/")
            rm_key = f"test -f ~/.ssh/authorized_keys && sed -i '/{escaped}/d' ~/.ssh/authorized_keys || true"
            self._ssh(rm_key, check=False)

        print("✅ clean(): done.")
