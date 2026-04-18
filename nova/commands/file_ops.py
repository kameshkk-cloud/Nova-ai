"""
NOVA Commands — File Operations
================================
Organise folders, summarise documents, find files.
"""

from __future__ import annotations

import os
import re
import shutil
from collections import Counter
from typing import Optional

from nova.commands.registry import CommandResult, command
from nova.config.settings import FILE_CATEGORIES
from nova.utils import logger as log


# ─── Internal helpers ────────────────────────────────────────────────────────

def _get_category(ext: str) -> Optional[str]:
    for cat, exts in FILE_CATEGORIES.items():
        if ext in exts:
            return cat
    return None


def _organize(folder_path: str) -> dict:
    if not os.path.isdir(folder_path):
        return {"error": f"Folder not found: {folder_path}"}
    moved: dict = {}
    skipped: list = []
    for fname in os.listdir(folder_path):
        fpath = os.path.join(folder_path, fname)
        if os.path.isdir(fpath):
            continue
        ext = os.path.splitext(fname)[1].lower()
        cat = _get_category(ext)
        if cat is None:
            skipped.append(fname)
            continue
        dest_dir = os.path.join(folder_path, cat)
        os.makedirs(dest_dir, exist_ok=True)
        try:
            shutil.move(fpath, os.path.join(dest_dir, fname))
        except Exception as exc:
            log.warn(f"Could not move {fname}: {exc}")
            skipped.append(fname)
            continue
        moved.setdefault(cat, []).append(fname)
    return {"moved": moved, "skipped": skipped}


_STOP_WORDS = {
    "the", "a", "an", "is", "in", "on", "at", "to", "for", "of",
    "and", "or", "but", "it", "this", "that", "with", "be", "as",
    "i", "you", "he", "she", "we", "they", "my", "your", "its",
    "are", "was", "were", "has", "have", "had", "will", "can",
    "not", "no", "if", "by", "from", "do", "did", "so", "then",
}


def _extract_keywords(text: str, top_n: int = 8) -> list:
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    filtered = [w for w in words if w not in _STOP_WORDS]
    return [w for w, _ in Counter(filtered).most_common(top_n)]


def _summarize(filepath: str) -> dict:
    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in (".txt", ".md", ".py", ".html", ".json", ".csv", ".log"):
        return {"error": f"Cannot summarize file type: {ext}"}
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
    except Exception as exc:
        return {"error": str(exc)}
    words = content.split()
    sentences = [s.strip() for s in re.split(r"[.!?]+", content) if len(s.strip()) > 10]
    word_count = len(words)
    avg_wl = sum(len(w) for w in words) / max(word_count, 1)
    complexity = "simple" if avg_wl < 4.5 else "moderate" if avg_wl < 6 else "complex"
    return {
        "file": os.path.basename(filepath), "word_count": word_count,
        "sentence_count": len(sentences), "keywords": _extract_keywords(content),
        "preview": ". ".join(sentences[:3]) + "..." if sentences else content[:200],
        "complexity": complexity,
    }


def _find(filename: str, search_dir: str = None) -> list:
    if search_dir is None:
        search_dir = os.path.expanduser("~")
    matches = []
    pattern = filename.lower()
    for root, _, files in os.walk(search_dir):
        for f in files:
            if pattern in f.lower():
                matches.append(os.path.join(root, f))
            if len(matches) >= 20:
                return matches
    return matches


# ─── Registered commands ─────────────────────────────────────────────────────

@command(intents=["organize_folder", "sort_files"], description="Organise files by type", category="files")
def cmd_organize(arg: Optional[str], memory) -> CommandResult:
    result = _organize(arg or ".")
    if "error" in result:
        return CommandResult(response=result["error"])
    total = sum(len(v) for v in result["moved"].values())
    cats = ", ".join(result["moved"].keys())
    return CommandResult(response=f"Organised {total} files into: {cats}.", data=result)


@command(intents=["summarize_file", "analyse_file"], description="Summarise a text file", category="files")
def cmd_summarize(arg: Optional[str], memory) -> CommandResult:
    if not arg:
        return CommandResult(response="Please specify a file path to summarize.")
    result = _summarize(arg)
    if "error" in result:
        return CommandResult(response=result["error"])
    return CommandResult(
        response=f"The file {result['file']} has {result['word_count']} words, "
                 f"{result['sentence_count']} sentences. Keywords: {', '.join(result['keywords'][:4])}. "
                 f"Complexity: {result['complexity']}.",
        data=result,
    )


@command(intents=["find_file", "search_file", "locate_file"], description="Search for a file", category="files")
def cmd_find_file(arg: Optional[str], memory) -> CommandResult:
    if not arg:
        return CommandResult(response="What file are you looking for?")
    matches = _find(arg)
    if not matches:
        return CommandResult(response=f"No files found matching '{arg}'.")
    return CommandResult(response=f"Found {len(matches)} files. First match: {matches[0]}", data={"matches": matches})
