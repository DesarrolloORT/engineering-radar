import pathlib

p = pathlib.Path(__file__).parent / "config.yaml"
t = p.read_text()
fixture = str((pathlib.Path(__file__).parent.parent / "tests" / "fixtures" / "documents.json").resolve())
fixture = fixture.replace("\\", "/")
t = t.replace("sources: []", "sources:\n  - type: static\n    params:\n      path: " + fixture)
p.write_text(t)
