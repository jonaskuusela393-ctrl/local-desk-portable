"""Exercise the distributed package on the runner's real operating system."""
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
        def ask(text):
            res=subprocess.run([str(cli),"-C",str(project),"--ask",text],env=env,capture_output=True,timeout=180)
            if res.returncode:raise RuntimeError(res.stderr.decode(errors="replace"))
            return res.stdout.decode(errors="replace")
        assert "release sample" in ask("/read sample.txt")
        assert "smol-360m" in ask("/models fit")
        assert "release sample" in ask("/resume latest") or "smol-360m" in ask("/resume latest")
        assert arch in ask("/mcp call desk system_info {}")
        reply=ask("/chat What is 2 plus 2? Reply with just the number.")
        assert reply.strip() and ("4" in reply or "four" in reply.lower()),reply
        print(target,"model, workspace, memory, MCP and catalog passed")
