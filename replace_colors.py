import re

filepath = '/home/coder/project/Pinarr/frontend/src/views/CaveView.vue'
with open(filepath, 'r') as f:
    content = f.read()

replacements = [
    ('bg-[#0d1117]', 'bg-gh-bg'),
    ('bg-[#161b22]', 'bg-gh-surface'),
    ('bg-[#21262d]', 'bg-gh-elevated'),
    ('border-[#30363d]', 'border-gh-border'),
    ('text-[#8b949e]', 'text-gh-text-secondary'),
    ('text-[#58a6ff]', 'text-gh-accent'),
    ('text-[#c9d1d9]', 'text-gh-text'),
    ('text-[#f85149]', 'text-gh-accent-red'),
    ('text-[#3fb950]', 'text-gh-accent-green-text'),
    ('bg-[#238636]', 'bg-gh-accent-green'),
    ('bg-[#2ea043]', 'bg-gh-accent-green-hover'),
    ('bg-[#f85149]', 'bg-gh-accent-red'),
    ('text-white', 'text-gh-text'),
    ('TEMP_BG_COLOR', 'bg-gh-accent-green'),
    ('TEMP_TEXT_COLOR', 'text-white'),
]

counts = {}
for old, new in replacements:
    c = content.count(old)
    content = content.replace(old, new)
    counts[old] = c

with open(filepath, 'w') as f:
    f.write(content)

total = sum(v for v in counts.values())
for old, c in counts.items():
    print(f"{old!r:30s} -> {c} replacé(s)")
print(f"Total: {total} remplacements")
