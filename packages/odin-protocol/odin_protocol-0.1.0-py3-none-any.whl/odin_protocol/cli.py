import json, sys, pathlib, typer
from .odin_file import (
    create_odin_file, pack_odin, unpack_odin, sign_odin, verify_odin,
    encrypt_odin, decrypt_odin, write_chain, read_chain
)

app = typer.Typer(help="ODIN v1.0 CLI")

@app.command()
def pack(state: str, meta: str, out: str):
    """Pack JSON state and metadata into an ODIN file."""
    od = create_odin_file("application/json", json.loads(pathlib.Path(state).read_text()))
    # meta can be extended later; keeping minimal for v1 quickstart
    b = pack_odin(od)
    pathlib.Path(out).write_bytes(b)
    typer.echo(f"wrote {out} ({len(b)} bytes)")

@app.command()
def unpack(inp: str, state_out: str, meta_out: str = "meta.json"):
    """Unpack an ODIN file into separate state and metadata files."""
    od = unpack_odin(pathlib.Path(inp).read_bytes())
    pathlib.Path(state_out).write_text(json.dumps(od.state.data, indent=2))
    pathlib.Path(meta_out).write_text(json.dumps(od.meta.model_dump(), indent=2))
    typer.echo(f"unpacked -> {state_out}, {meta_out}")

@app.command()
def sign(inp: str, sk_pem: str, out: str):
    """Sign an ODIN file with a private key."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    key = serialization.load_pem_private_key(pathlib.Path(sk_pem).read_bytes(), password=None)
    b = pack_odin(unpack_odin(pathlib.Path(inp).read_bytes()))  # normalize
    sig = sign_odin(b, key)
    # attach signature (your SDK already supports)
    od = unpack_odin(b); od.sig = sig
    pathlib.Path(out).write_bytes(pack_odin(od))
    typer.echo(f"signed -> {out}")

@app.command()
def verify(inp: str):
    """Verify the signature of an ODIN file."""
    od = unpack_odin(pathlib.Path(inp).read_bytes())
    ok = verify_odin(pack_odin(od), od.sig) if od.sig else False
    typer.echo("valid" if ok else "invalid"); raise typer.Exit(code=0 if ok else 1)

@app.command()
def chain(out: str, inputs: list[str] = typer.Argument(...)):
    """Create a chain file from multiple ODIN files."""
    bufs = [pathlib.Path(p).read_bytes() for p in inputs]
    with open(out, "wb") as f:
        write_chain(bufs, f)
    typer.echo(f"chain -> {out}")

if __name__ == "__main__":
    app()
