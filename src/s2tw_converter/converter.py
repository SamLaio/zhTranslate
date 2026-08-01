from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from opencc import OpenCC
except Exception as exc:  # pragma: no cover - dependency is required at runtime
    OpenCC = None
    OPENCC_IMPORT_ERROR = exc
else:
    OPENCC_IMPORT_ERROR = None


PACKAGE_REPLACEMENTS = Path(__file__).with_name("custom_replacements.tsv")
DEFAULT_ENCODINGS = ("utf-8-sig", "utf-8", "gb18030", "big5")
DEFAULT_EXTENSIONS = (".txt", ".md")
OUTPUT_SUFFIX = "_zyTw"
WESTERN_TO_EAST_ASIAN_QUOTES = str.maketrans({
    "“": "「",
    "”": "」",
    "‘": "『",
    "’": "』",
})


def load_replacements(paths: Iterable[Path | str] | None = None) -> tuple[tuple[str, str], ...]:
    replacements: dict[str, str] = {}
    candidates = [PACKAGE_REPLACEMENTS]
    if paths:
        candidates.extend(Path(path) for path in paths)

    for path in candidates:
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#") or "\t" not in line:
                    continue
                source, target = line.split("\t", 1)
                source = source.strip()
                target = target.strip().split()[0] if target.strip() else ""
                if source and target:
                    replacements[source] = target
    return tuple(sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True))


@dataclass
class Converter:
    replacement_paths: tuple[Path, ...] = ()
    convert_quotes: bool = True

    def __post_init__(self) -> None:
        self._replacements = load_replacements(self.replacement_paths)
        self._converter = self._new_opencc()

    def convert(self, text: str | None) -> str | None:
        if not text:
            return text
        converted = self._apply_replacements(text)
        converted = self._converter.convert(converted)
        converted = self._apply_replacements(converted)
        if self.convert_quotes:
            converted = converted.translate(WESTERN_TO_EAST_ASIAN_QUOTES)
        return converted

    def _apply_replacements(self, text: str) -> str:
        for source, target in self._replacements:
            text = text.replace(source, target)
        return text

    @staticmethod
    def _new_opencc():
        if OpenCC is None:
            raise RuntimeError("無法載入 opencc-python-reimplemented") from OPENCC_IMPORT_ERROR
        return OpenCC("s2tw")


def output_path_with_suffix(path: Path) -> Path:
    return path.with_name(f"{path.stem}{OUTPUT_SUFFIX}{path.suffix}")


def convert_text(text: str | None, replacement_paths: Iterable[Path | str] | None = None, convert_quotes: bool = True) -> str | None:
    return Converter(tuple(Path(path) for path in replacement_paths or ()), convert_quotes=convert_quotes).convert(text)


def read_text_with_fallback(path: Path, encodings: Iterable[str] = DEFAULT_ENCODINGS) -> str:
    last_error: UnicodeDecodeError | None = None
    data = path.read_bytes()
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    for encoding in encodings:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error:
        raise last_error
    return data.decode("utf-8")


def convert_file(
    input_path: Path | str,
    output_path: Path | str,
    *,
    replacement_paths: Iterable[Path | str] | None = None,
    convert_quotes: bool = True,
    overwrite: bool = False,
) -> Path:
    source = Path(input_path)
    target = output_path_with_suffix(Path(output_path))
    if target.exists() and not overwrite:
        raise FileExistsError(f"輸出檔已存在：{target}")
    converter = Converter(tuple(Path(path) for path in replacement_paths or ()), convert_quotes=convert_quotes)
    converted = converter.convert(read_text_with_fallback(source)) or ""
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(converted, encoding="utf-8", newline="\n")
    return target


def convert_directory(
    input_dir: Path | str,
    output_dir: Path | str | None = None,
    *,
    replacement_paths: Iterable[Path | str] | None = None,
    convert_quotes: bool = True,
    extensions: Iterable[str] = DEFAULT_EXTENSIONS,
    in_place: bool = False,
    overwrite: bool = False,
) -> list[Path]:
    source_root = Path(input_dir)
    target_root = source_root if in_place else Path(output_dir) if output_dir else None
    if target_root is None:
        raise ValueError("非原地轉換時必須指定 output_dir")

    allowed = {ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in extensions}
    converted_paths: list[Path] = []
    excluded_root = None
    if not in_place:
        source_root_abs = source_root.resolve()
        target_root_abs = target_root.resolve()
        if target_root_abs == source_root_abs or target_root_abs.is_relative_to(source_root_abs):
            excluded_root = target_root_abs

    for source in list(source_root.rglob("*")):
        if excluded_root and source.resolve().is_relative_to(excluded_root):
            continue
        if not source.is_file() or source.suffix.lower() not in allowed:
            continue
        if source.stem.endswith(OUTPUT_SUFFIX):
            continue
        target = source if in_place else target_root / source.relative_to(source_root)
        converted_paths.append(
            convert_file(
                source,
                target,
                replacement_paths=replacement_paths,
                convert_quotes=convert_quotes,
                overwrite=overwrite or in_place,
            )
        )
    return converted_paths
