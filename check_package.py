"""Exercise the distributed package on the runner's real operating system."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import zipfile

tag=sys.argv[1];mobile=len(sys.argv)>2 and sys.argv[2]=="ios"
system={"win32":"windows","darwin":"darwin","linux":"linux"}[sys.platform]
arch={"amd64":"amd64","x86_64":"amd64","aarch64":"arm64","arm64":"arm64"}[platform.machine().lower()]
target=system+"-"+arch
archive="local-desk-"+("ios-source" if mobile else target)+".zip"
with tempfile.TemporaryDirectory(dir=Path.home()) as tmp:
    root=Path(tmp)
    subprocess.run(["gh","release","download",tag,"--repo","jonaskuusela393-ctrl/local-desk-portable","-p",archive,"-D",tmp],check=True)
    os.environ.pop("GH_TOKEN",None)
    expected = {'local-desk-android-arm64.zip': '7d9025e97f3b752b10192cbd68cd54c8db1220b1eab67df6dbe1dc24bf604e21', 'local-desk-darwin-amd64.zip': 'bf37cac8b8dc9c8b7de77109bb81d99d88e5d3858610a3c967e623a3de385e14', 'local-desk-darwin-arm64.zip': '5a130dac1ab45ca514d052180b74f9a0a7194308d2729748db1272d33de2c794', 'local-desk-ios-source.zip': 'ee021b9e2fdbed9ba64e3ff02405403904502b70aeea064cdc677c70ca0c97da', 'local-desk-linux-amd64.zip': '41ed33356e8e6362ab18fbd8cc70c345e5b82595ad5edebd35584c7b3abff6e8', 'local-desk-linux-arm64.zip': '4086250fa51e552e3c35be6f43d123d7c323943cc29f12846f55c73d8547e628', 'local-desk-windows-amd64.zip': '5266672735d125e841bdacb113a889412847a2e889b9da3c08d0637b8fb3b799', 'local-desk-windows-arm64.zip': 'f41ba4084aa48f7986a90e55f01f8b42e2e33099e7e8ee48eacf66983dd8e2ed'}
    with (root/archive).open("rb") as f:
        digest=hashlib.sha256()
        for block in iter(lambda: f.read(2**20), b""): digest.update(block)
        assert digest.hexdigest()==expected[archive], archive
    with zipfile.ZipFile(root/archive) as bundle:
        for entry in bundle.infolist():
            output=Path(bundle.extract(entry,root))
            if os.name!="nt":output.chmod(((entry.external_attr>>16)&0o777)|0o600)
    if mobile:
        folder=root/"Local Desk iOS"
        subprocess.run(["xcodebuild","-quiet","-project",str(folder/"llama.swiftui.xcodeproj"),"-target","llama.swiftui","-configuration","Release","-sdk","iphoneos","CODE_SIGNING_ALLOWED=NO","ARCHS=arm64","build"],check=True,cwd=folder)
        print("iOS device target compiled")
    else:
        cli=root/"Local Desk/bin"/("desk-"+target+(".exe" if os.name=="nt" else ""))
        env={**os.environ,"XDG_STATE_HOME":str(root/"state"),"XDG_CACHE_HOME":str(root/"cache"),"XDG_CONFIG_HOME":str(root/"config"),"PYTHONIOENCODING":"utf8","LOCAL_DESK_MODEL_HOME":str(root/"library")}
        project=root/"project";project.mkdir()
        (project/"sample.txt").write_text("release sample")
        def ask(*questions):
            res=subprocess.run([str(cli),"-C",str(project),*(item for question in questions for item in ("--ask",question))],env=env,capture_output=True,timeout=180)
            if res.returncode:raise RuntimeError(res.stderr.decode(errors="replace"))
            return res.stdout.decode(errors="replace")
        assert "release sample" in ask("/read sample.txt")
        assert "smol-360m" in ask("/models fit")
        assert "release sample" in ask("/resume latest") or "smol-360m" in ask("/resume latest")
        assert arch in ask("/mcp call desk system_info {}")
        reply=ask("/chat What is 2 plus 2? Reply with just the number.","/status")
        generation, marker, stats = reply.partition("Last generation ")
        assert generation.splitlines()[0].strip() and marker and "tokens/s" in stats, reply
        assert float(stats.split()[0]) > 0, stats
        print("Starter model arithmetic sample:",generation.splitlines()[0])
        print(target,"model, workspace, memory, MCP and catalog passed")
