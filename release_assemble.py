"""Reassemble verified release ZIPs from pinned upstream files and the release recipe."""
import argparse
import base64
import concurrent.futures
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import urllib.request
import zipfile
import zlib


def digest(data):
    return hashlib.sha256(data).hexdigest()


def index_archive(path, blobs):
    def add(stream):
        data=stream.read()
        blobs.setdefault(digest(data),data)
    if path.name.endswith(".gguf"):
        with path.open("rb") as source:add(source)
    elif path.suffix==".zip":
        with zipfile.ZipFile(path) as bundle:
            for item in bundle.infolist():
                if not item.is_dir():
                    with bundle.open(item) as src:add(src)
    else:
        with tarfile.open(path) as bundle:
            for item in bundle:
                if item.isfile():
                    with bundle.extractfile(item) as src:add(src)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("recipe",type=Path)
    parser.add_argument("output",type=Path)
    parser.add_argument("--cache",type=Path)
    parser.add_argument("--upload",action="store_true")
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(args.recipe) as bundle:
        plan=json.loads(bundle.read("recipe.json"))
        cache=args.cache or Path(tmp)
        def restore(item):
            key,spec=item
            path=cache/spec["url"].split("/")[-1]
            if not path.exists():
                subprocess.run(["curl","-fsSL","--retry","3","--max-time","180",spec["url"],"-o",str(path)],check=True)
            with path.open("rb") as src:
                if hashlib.file_digest(src,"sha256").hexdigest()!=spec["sha256"]:raise ValueError("Upstream checksum mismatch: "+key)
            return key,path
        with concurrent.futures.ThreadPoolExecutor(4) as pool:
            deps=dict(pool.map(restore,plan["inputs"].items()))
        raw={}
        for path in deps.values():index_archive(path,raw)
        packed={}
        for archive,meta in plan["archives"].items():
            if Path(archive).name!=archive or not archive.endswith(".zip"):raise ValueError("Invalid archive name")
            dest=args.output/archive
            with dest.open("wb") as out:
                for header,compressed,source in meta["entries"]:
                    out.write(base64.b64decode(header,validate=True))
                    if compressed not in packed:
                        if source:
                            compressor=zlib.compressobj(1,zlib.DEFLATED,-15)
                            data=compressor.compress(raw[source])+compressor.flush()
                        else:data=bundle.read("chunks/"+compressed)
                        if digest(data)!=compressed:raise ValueError("Compressed member checksum mismatch: "+compressed)
                        packed[compressed]=data
                    out.write(packed[compressed])
                out.write(base64.b64decode(meta["end"],validate=True))
            with dest.open("rb") as src:
                if hashlib.file_digest(src,"sha256").hexdigest()!=meta["sha256"]:raise ValueError("Release checksum mismatch: "+archive)
            print("Verified",archive,flush=True)
            if args.upload:
                subprocess.run(["gh","release","upload","v0.1.0",str(dest),"--repo","jonaskuusela393-ctrl/local-desk-portable","--clobber"],check=True)

if __name__=="__main__":main()
