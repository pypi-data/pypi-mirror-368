#!/usr/bin/env python3
"""
rbash CLI — `rbash <host>` mounts your local folder to a remote server via reverse sshfs
and opens an interactive bash. If no <host> is provided, it lists hosts from ~/.ssh/config.
"""

import sys
import shutil
import argparse
from pathlib import Path

from .remote import RemoteSession


def _list_hosts():
    cfg = Path.home() / ".ssh" / "config"
    if not cfg.exists():
        print("No ~/.ssh/config found.")
        return
    print("📜 SSH hosts:")
    print(f"{'Name':<24} {'HostName':<24} {'Jump':<24}")
    print("-" * 72)
    current = {}
    rows = []
    with cfg.open() as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            low = s.lower()
            if low.startswith("host ") and not low.startswith("host *"):
                if current:
                    rows.append(current)
                    current = {}
                parts = s.split()
                if len(parts) >= 2:
                    current["Host"] = parts[1]
            elif low.startswith("hostname "):
                parts = s.split()
                if len(parts) >= 2:
                    current["HostName"] = parts[1]
            elif low.startswith("proxyjump "):
                parts = s.split()
                if len(parts) >= 2:
                    current["ProxyJump"] = parts[1]
        if current:
            rows.append(current)
    for e in rows:
        print(f"{e.get('Host',''):<24} {e.get('HostName',''):<24} {e.get('ProxyJump',''):<24}")


def _ensure_tools():
    missing = []
    for tool in ("ssh", "sshfs"):
        if shutil.which(tool) is None:
            missing.append(tool)
    if missing:
        print(f"❌ Missing required tools: {', '.join(missing)}", file=sys.stderr)
        print("   Please install them and try again.", file=sys.stderr)
        sys.exit(3)


def main():
    parser = argparse.ArgumentParser(
        prog="rbash",
        description="Mount your local folder to a remote server (reverse sshfs) and open an interactive bash."
    )
    parser.add_argument("host", nargs="?", help="SSH host alias or hostname/IP")
    parser.add_argument("--path", default=".", help="Local path to expose (default: current dir)")
    parser.add_argument("--port", type=int, default=2222, help="Base reverse port to try (default: 2222)")
    parser.add_argument("--strict", action="store_true", help="Enable strict host key checking")
    parser.add_argument("--no-clean", action="store_true", help="Skip remote cleanup (debug)")
    args = parser.parse_args()

    if not args.host:
        _list_hosts()
        return 0

    _ensure_tools()

    sess = RemoteSession(args.host, local_path=args.path, base_port=args.port, strict_host_check=args.strict)
    try:
        sess.prepare()
        sess.run()
    except KeyboardInterrupt:
        print("\n⛔ Interrupted by user.")
    except:
        print("\n⛔ the remote server is not well prepared")
        pass
    finally:
        if not args.no_clean:
            try:
                sess.clean()
            except Exception as e:
                print(f"⚠️ Cleanup encountered an issue: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
