#!/usr/bin/env python3
"""Find LLM call sites in a codebase and check their observability tags.

Heuristic, stdlib only. Prints a Markdown table (default) or JSON.

    python3 find_llm_calls.py [path] [--format md|json]

For each call site it reports the provider/SDK hint, whether the file already
uses OpenTelemetry, and which recommended tags appear in the file. Review
every hit: the patterns can match unrelated code, and they can't see calls made
through an internal gateway or a wrapper with a custom name.
"""
import argparse
import json
import os
import re
import sys

SKIP_DIRS = {
    ".git", "node_modules", "vendor", ".venv", "venv", "env", "__pycache__",
    "dist", "build", ".next", ".nuxt", "coverage", "storage", ".idea", ".vscode",
    "site-packages", ".mypy_cache", ".pytest_cache", ".tox",
}
EXTS = {".py", ".php", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"}
MAX_BYTES = 1_000_000

# (provider hint, regex). Matched per line.
CALL_PATTERNS = [
    ("openai", r"\.chat\.completions\.(create|parse|stream)\s*\("),
    ("openai", r"\.responses\.(create|parse|stream)\s*\("),
    ("openai", r"\.embeddings\.create\s*\("),
    ("openai (legacy)", r"\bopenai\.(ChatCompletion|Completion)\.create\s*\("),
    ("anthropic", r"\.messages\.(create|stream)\s*\("),
    ("google genai", r"\.generate_content(_async)?\s*\(|\.generateContent(Stream)?\s*\("),
    ("aws bedrock", r"\.(invoke_model|invoke_model_with_response_stream|converse|converse_stream)\s*\("),
    ("aws bedrock", r"new\s+(InvokeModel|Converse)(Stream)?Command\s*\("),
    ("litellm", r"\blitellm\.a?completion\s*\("),
    ("langchain", r"\b(ChatOpenAI|ChatAnthropic|ChatVertexAI|ChatGoogleGenerativeAI|AzureChatOpenAI|ChatBedrock|ChatOllama)\s*\("),
    ("ollama", r"\bollama\.(chat|generate)\s*\("),
    ("vercel ai sdk", r"\b(generateText|streamText|generateObject|streamObject)\s*\("),
    ("openai-php", r"OpenAI::(client|factory)\s*\(|->chat\(\)\s*->\s*create(Streamed)?\s*\(|->responses\(\)\s*->\s*create\s*\("),
    ("openai-php (laravel)", r"OpenAI::(chat|responses|completions|embeddings)\(\)\s*->\s*create(Streamed)?\s*\("),
    ("prism (laravel)", r"Prism::(text|structured|embeddings)\s*\("),
    ("raw http", r"api\.openai\.com|api\.anthropic\.com|generativelanguage\.googleapis\.com|openai\.azure\.com|bedrock-runtime\."),
]
CALL_RES = [(name, re.compile(rx)) for name, rx in CALL_PATTERNS]

# A match only counts in files that reference an LLM library or endpoint,
# which filters out unrelated `.messages.create(` or `generateText(` methods.
FILE_GATE = re.compile(
    r"openai|anthropic|google\.genai|google\.generativeai|@google/genai|vertexai|bedrock|litellm|"
    r"langchain|ollama|from\s+['\"]ai['\"]|require\(['\"]ai['\"]\)|@ai-sdk/|Prism\\|EchoLabs\\Prism|OpenAI\\|"
    r"api\.openai\.com|api\.anthropic\.com|generativelanguage\.googleapis\.com",
    re.I,
)
TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|spec|fixtures|mocks?)(/|$)|(_test|\.test|\.spec)\.\w+$|(^|/)test_[^/]*$", re.I)

OTEL = re.compile(r"opentelemetry|OpenTelemetry\\|@opentelemetry/", re.I)
TAGS = {
    "gen_ai.request.model": re.compile(r"gen_ai\.request\.model"),
    "gen_ai.provider.name/system": re.compile(r"gen_ai\.(provider\.name|system)"),
    "gen_ai.usage.*_tokens": re.compile(r"gen_ai\.usage\.(input|output)_tokens"),
    "app.feature": re.compile(r"app\.feature"),
    "app.tenant_id": re.compile(r"app\.tenant_id"),
    "app.prompt_version": re.compile(r"app\.prompt_version"),
}


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(filenames):
            if os.path.splitext(name)[1].lower() in EXTS:
                path = os.path.join(dirpath, name)
                try:
                    if os.path.getsize(path) <= MAX_BYTES:
                        yield path
                except OSError:
                    continue


def scan(root):
    sites = []
    files = {}
    for path in iter_files(root):
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        if not FILE_GATE.search(text):
            continue
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        hits = []
        for lineno, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith(("#", "//", "*", "/*")) and "http" not in stripped:
                continue
            for name, rx in CALL_RES:
                if rx.search(line):
                    hits.append({"file": rel, "line": lineno, "provider": name, "code": stripped[:120]})
                    break
        if not hits:
            continue
        info = {
            "otel": bool(OTEL.search(text)),
            "tags": [t for t, rx in TAGS.items() if rx.search(text)],
            "test_file": bool(TEST_PATH.search(rel)),
        }
        files[rel] = info
        for h in hits:
            h.update(info)
            sites.append(h)
    return sites, files


def to_md(sites, files, root):
    out = [f"# LLM call sites in `{root}`", ""]
    if not sites:
        out += ["No LLM call sites found with the built-in patterns.",
                "Search for provider hostnames and the project's own wrapper names before concluding there are none."]
        return "\n".join(out)
    prod = [s for s in sites if not s["test_file"]]
    out.append(f"**{len(prod)}** call sites in **{len({s['file'] for s in prod})}** files"
               f" (+{len(sites) - len(prod)} in test files). "
               f"Files with OpenTelemetry: **{sum(1 for f, i in files.items() if i['otel'] and not i['test_file'])}**.")
    out += ["", "| # | File:line | Provider hint | OTel in file | Span tags in file | Code |", "|---|---|---|---|---|---|"]
    for i, s in enumerate(sites, 1):
        tags = ", ".join(s["tags"]) or "none"
        mark = " (test)" if s["test_file"] else ""
        code = s["code"].replace("|", "\\|")
        out.append(f"| {i} | `{s['file']}:{s['line']}`{mark} | {s['provider']} | {'yes' if s['otel'] else 'no'} | {tags} | `{code}` |")
    out += ["", "Heuristic results: open each hit, drop false positives, and look for calls this scan can't see "
            "(internal gateways, raw HTTP built elsewhere, queue workers)."]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.path):
        print(f"not a directory: {args.path}", file=sys.stderr)
        return 2
    sites, files = scan(args.path)
    if args.format == "json":
        print(json.dumps({"call_sites": sites, "files": files}, indent=2))
    else:
        print(to_md(sites, files, args.path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
