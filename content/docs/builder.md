---
title: Input builder
description: "Build a Mallard input file step by step, or check one, against the keys Mallard's setup reads: types, defaults and accepted values."
hide:
  - toc
---

# Input builder

Build an input file step by step, or paste one to check it. Everything here comes from the
[key catalog](https://github.com/MatthewBonanni/mallard/blob/main/docs/input-keys.json) that
Mallard's setup records as it reads the examples and tutorials: each key's type, default and accepted
values. Each key links to its row of the [input reference](input.md). The page runs in your browser
and sends nothing anywhere.

For a ready-made case with its mesh, run and post-processing scripts, start from a template instead:
`Mallard new --list`. `Mallard --check input.toml` checks what this page cannot: mesh files, zone
names, the time step, memory and cost.

<div id="mallard-builder" class="mallard-builder" markdown="0">
<p class="mallard-builder__loading">Loading the key catalog…</p>
<noscript>The input builder needs JavaScript; the <a href="../input/">input reference</a> lists every key.</noscript>
</div>
