"""
Minimal KSP ConfigNode / ModuleManager text parser - just enough structure for
the catalog scrapers to read upstream RO / RP-1 / ROEngines cfg files without a
regex per field.

    parse(text) -> [Node]      top-level nodes, in file order

A Node keeps its raw HEADER verbatim (e.g. `@PART[*]:HAS[#engineType[F1]]:FOR[X]`
or `@CONFIG[H-1-200K]` or `PROPELLANT`), its `key = value` pairs in order (keys
keep any MM operator prefix like `%` / `@`), and its child nodes. Nothing is
evaluated - no MM patch semantics, no `$var$` substitution; callers decide what a
header means. `//` comments are stripped; a value keeps everything after the
first `=` up to the comment, stripped.

Tolerates the formats seen in the wild: `{` on the header line or the next one,
one-line nodes (`%MODULE[ModuleTagList] { tag = Reentry }`), and `}` sharing a
line with a value.
"""
import re

_TOKEN_RE = re.compile(r"\{|\}|[^{}]+")


class Node:
    __slots__ = ("header", "values", "children")

    def __init__(self, header):
        self.header = header
        self.values = []      # [(key, value)]
        self.children = []    # [Node]

    # --- header helpers -------------------------------------------------
    @property
    def op(self):
        """MM operator prefix of the header ('' for a plain node)."""
        h = self.header
        return h[0] if h and h[0] in "@%+$!-&|#*" else ""

    @property
    def type_name(self):
        """Node type without operator / selector / pass: '@PART[x]:FOR[y]' -> 'PART'."""
        h = self.header.lstrip("@%+$!-&|#*")
        return re.split(r"[\[:,\s]", h, maxsplit=1)[0]

    @property
    def selector(self):
        """The first [...] after the type name, or None ('@PART[a|b]' -> 'a|b')."""
        h = self.header.lstrip("@%+$!-&|#*")
        rest = h[len(self.type_name):]
        if not rest.startswith("["):
            return None
        depth, out = 0, []
        for ch in rest:
            if ch == "[":
                depth += 1
                if depth == 1:
                    continue
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    break
            out.append(ch)
        return "".join(out)

    # --- value helpers --------------------------------------------------
    def get(self, key, default=None):
        """First value whose key, minus MM operator prefixes, equals `key`
        (case-insensitive)."""
        k = key.lower()
        for kk, v in self.values:
            if kk.lstrip("@%&|!*").lower() == k:
                return v
        return default

    def get_all(self, key):
        k = key.lower()
        return [v for kk, v in self.values if kk.lstrip("@%&|!*").lower() == k]

    def find(self, type_name):
        """Child nodes of the given type (operator/selector ignored)."""
        t = type_name.lower()
        return [c for c in self.children if c.type_name.lower() == t]

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()

    def __repr__(self):
        return f"Node({self.header!r}, {len(self.values)} values, {len(self.children)} children)"


def _strip_comments(text):
    out = []
    for line in text.splitlines():
        i = line.find("//")
        out.append(line if i < 0 else line[:i])
    return "\n".join(out)


def parse(text):
    """Parse cfg text into a list of top-level Nodes (best effort, never raises
    on unbalanced braces - an unclosed node is closed at EOF, a stray '}' is
    ignored)."""
    text = _strip_comments(text)
    root = Node("")
    stack = [root]
    pending = ""      # text since the last brace: values, then maybe a header
    for tok in _TOKEN_RE.findall(text):
        if tok == "{":
            lines = [ln.strip() for ln in pending.splitlines() if ln.strip()]
            header = lines.pop() if lines else ""
            _add_values(stack[-1], lines)
            node = Node(header)
            stack[-1].children.append(node)
            stack.append(node)
            pending = ""
        elif tok == "}":
            _add_values(stack[-1], [ln.strip() for ln in pending.splitlines() if ln.strip()])
            pending = ""
            if len(stack) > 1:
                stack.pop()
        else:
            pending += tok
    _add_values(stack[-1], [ln.strip() for ln in pending.splitlines() if ln.strip()])
    return root.children


def _add_values(node, lines):
    for ln in lines:
        if "=" not in ln:
            continue
        k, v = ln.split("=", 1)
        k = k.strip()
        if k:
            node.values.append((k, v.strip()))


def parse_file(path):
    with open(path, errors="replace") as f:
        return parse(f.read())


def first_number(value, default=None):
    """Leading float in a cfg value ('1.5 // x' or '0.0566') or `default`."""
    if value is None:
        return default
    m = re.match(r"\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)", value)
    return float(m.group(1)) if m else default


if __name__ == "__main__":
    sample = """
// comment
@PART[a|b]:HAS[#engineType[F1]]:FOR[RealismOverhaulEngines]
{
    %title = Thing // trailing
    @MODULE[ModuleEngineConfigs] { CONFIG { name = X
        maxThrust = 10 } }
    %MODULE[ModuleTagList] { tag = EngineLiquidTurbo }
}
ENTRYCOSTMODS { A-4 = 1 }
"""
    nodes = parse(sample)
    assert len(nodes) == 2, nodes
    p = nodes[0]
    assert p.type_name == "PART" and p.op == "@" and p.selector == "a|b", p.header
    assert p.get("title") == "Thing"
    cfg = p.find("MODULE")[0].find("CONFIG")[0]
    assert cfg.get("name") == "X" and first_number(cfg.get("maxThrust")) == 10.0
    assert p.find("MODULE")[1].get("tag") == "EngineLiquidTurbo"
    assert nodes[1].get("A-4") == "1"
    print("mmcfg.py self-checks: OK")
