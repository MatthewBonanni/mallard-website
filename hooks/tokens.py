"""MkDocs hook: design/tokens.json, the design tokens shared with Mallard's GUI, as CSS custom
properties (--m-*) in assets/tokens.css, which extra.css builds the theme on.

Lengths become rem of Material's 20 px root (so they follow its larger root on wide screens);
colors are set per Material scheme (default: light, slate: dark).
"""
import json
import os

ROOT_PX = 20


def rem(px):
    return f"{px / ROOT_PX:g}rem"


def css(tokens):
    font, out = tokens["font"], [":root {"]
    for name in ("sans", "mono"):
        out.append(f'  --m-font-{name}: "{font[name]["family"]}", {font[name]["fallback"]};')
    out.append(f"  --m-font-features: {font['features']};")
    out.append(f"  --m-numeric: {font['numeric']};")
    for name, t in tokens["type"].items():
        if name.startswith("$"):
            continue
        out += [f"  --m-type-{name}-size: {rem(t['size'])};", f"  --m-type-{name}-line: {t['line']};",
                f"  --m-type-{name}-weight: {t['weight']};", f"  --m-type-{name}-tracking: {t['tracking']};"]
    out += [f"  --m-space-{k}: {rem(v)};" for k, v in tokens["space"].items() if not k.startswith("$")]
    out += [f"  --m-radius-{k}: {rem(v) if v < 999 else '999px'};" for k, v in tokens["radius"].items()]
    out += [f"  --m-brand-{k}: {v};" for k, v in tokens["brand"].items() if not k.startswith("$")]
    out.append("}")
    for scheme, theme in (("default", "light"), ("slate", "dark")):
        out.append(f'[data-md-color-scheme="{scheme}"] {{')
        out += [f"  --m-{k}: {v};" for k, v in tokens["color"][theme].items()]
        out.append(f"  color-scheme: {theme};")
        out.append("}")
    return "\n".join(out) + "\n"


def on_post_build(config, **kwargs):
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(here, "design", "tokens.json")) as f:
        tokens = json.load(f)
    path = os.path.join(config["site_dir"], "assets", "tokens.css")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("/* Generated from design/tokens.json by hooks/tokens.py */\n" + css(tokens))
