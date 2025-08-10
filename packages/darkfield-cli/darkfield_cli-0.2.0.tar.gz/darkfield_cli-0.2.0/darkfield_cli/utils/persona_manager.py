"""Persona management utilities for darkfield CLI

Provides:
- Local persona registry under ~/.darkfield/personas
- Active persona state under ~/.darkfield/state.json
- Composition of persona vectors from weighted trait reference vectors
- Envelope (system prompt + style markers) handling
"""
from __future__ import annotations

import os
import json
import math
import pathlib
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # Lazy error at runtime if used without install

from . import __init__  # noqa: F401  # ensure package context
from ..api_client import DarkfieldClient


PERSONAS_DIR = pathlib.Path.home() / ".darkfield" / "personas"
STATE_FILE = pathlib.Path.home() / ".darkfield" / "state.json"


@dataclass
class PersonaEnvelope:
    system_prompt: Optional[str] = None
    style_markers: Optional[List[str]] = None


@dataclass
class PersonaComposition:
    name: str
    model: str
    vector: List[float]
    norm: float
    dimension: int
    recommended_layer: Optional[int] = None
    recommended_coefficient: Optional[float] = None
    envelope: Optional[PersonaEnvelope] = None


def _ensure_dirs() -> None:
    PERSONAS_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


def _read_yaml_or_json(path: pathlib.Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    # Try YAML first if available, then JSON
    if yaml is not None:
        try:
            data = yaml.safe_load(text)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    # Fallback to JSON
    try:
        return json.loads(text)
    except Exception as exc:
        raise ValueError(f"Unsupported persona file format for {path}: {exc}")


def _write_yaml(path: pathlib.Path, data: Dict[str, Any]) -> None:
    if yaml is None:
        # Fallback to JSON
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def list_personas() -> List[str]:
    _ensure_dirs()
    names: List[str] = []
    for file in PERSONAS_DIR.glob("*.y*ml"):
        names.append(file.stem)
    for file in PERSONAS_DIR.glob("*.json"):
        if file.stem not in names:
            names.append(file.stem)
    return sorted(names)


def get_persona_path(name: str) -> pathlib.Path:
    # Prefer YAML
    yaml_path = PERSONAS_DIR / f"{name}.yaml"
    if yaml_path.exists():
        return yaml_path
    yml_path = PERSONAS_DIR / f"{name}.yml"
    if yml_path.exists():
        return yml_path
    json_path = PERSONAS_DIR / f"{name}.json"
    return json_path


def load_persona(name_or_path: str) -> Dict[str, Any]:
    _ensure_dirs()
    path = pathlib.Path(name_or_path)
    if not path.exists():
        # Treat as name in registry
        path = get_persona_path(name_or_path)
    if not path.exists():
        raise FileNotFoundError(f"Persona not found: {name_or_path}")
    return _read_yaml_or_json(path)


def save_persona_from_file(file_path: str) -> str:
    _ensure_dirs()
    src = pathlib.Path(file_path)
    data = _read_yaml_or_json(src)
    name = data.get("name") or src.stem
    target = PERSONAS_DIR / f"{name}.yaml"
    _write_yaml(target, data)
    return name


def save_persona_inline(inline_spec: str, name: Optional[str] = None) -> str:
    """
    inline_spec example: 'name=helpful-honest; model=llama-3; traits=helpfulness:0.7,honesty:0.5,harmlessness:0.6'
    Minimal parser for quick creation.
    """
    _ensure_dirs()
    parts = [p.strip() for p in inline_spec.split(";") if p.strip()]
    kv: Dict[str, str] = {}
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            kv[k.strip()] = v.strip()
    if name is None:
        name = kv.get("name", "persona")
    model = kv.get("model", "llama-3")
    traits_str = kv.get("traits") or kv.get("weights") or ""
    traits: Dict[str, float] = {}
    for item in [s.strip() for s in traits_str.split(",") if s.strip()]:
        if ":" in item:
            t, w = item.split(":", 1)
            try:
                traits[t.strip()] = float(w)
            except ValueError:
                continue
    data: Dict[str, Any] = {
        "name": name,
        "model": model,
        "traits": traits,
    }
    target = PERSONAS_DIR / f"{name}.yaml"
    _write_yaml(target, data)
    return name


def delete_persona(name: str) -> bool:
    _ensure_dirs()
    for ext in ("yaml", "yml", "json"):
        p = PERSONAS_DIR / f"{name}.{ext}"
        if p.exists():
            p.unlink()
            return True
    return False


def set_active_persona(name: Optional[str]) -> None:
    _ensure_dirs()
    state = {}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
        except Exception:
            state = {}
    state["active_persona"] = name
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def get_active_persona() -> Optional[str]:
    if not STATE_FILE.exists():
        return None
    try:
        state = json.loads(STATE_FILE.read_text())
        return state.get("active_persona")
    except Exception:
        return None


def _normalize(vec: List[float]) -> Tuple[List[float], float]:
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0:
        return vec, 0.0
    return [x / norm for x in vec], norm


def compose_persona_vector(
    persona: Dict[str, Any],
    client: Optional[DarkfieldClient] = None,
    model: Optional[str] = None,
) -> PersonaComposition:
    """
    Compose a persona vector from weighted trait reference vectors.
    Persona format:
      name: str
      model: str
      traits: { trait_name: weight, ... }
      envelope: { system_prompt: str, style_markers: [..] }
      safety: { max_coefficient: float, disallow_traits: [..] }
    """
    if client is None:
        client = DarkfieldClient()

    name = persona.get("name", "persona")
    target_model = model or persona.get("model", "llama-3")
    traits: Dict[str, float] = persona.get("traits", {}) or {}

    if not traits:
        raise ValueError("Persona has no traits/weights defined")

    # Fetch reference trait vectors and accumulate weighted sum
    sum_vec: List[float] = []
    dim: Optional[int] = None

    # Reject disallowed traits if configured
    disallow_specs = persona.get("safety", {}).get("disallow_traits", [])
    disallow: Dict[str, float] = {}
    for spec in disallow_specs:
        # format: trait>threshold
        if ">" in spec:
            t, thr = spec.split(">", 1)
            try:
                disallow[t.strip()] = float(thr)
            except ValueError:
                pass
        else:
            disallow[spec.strip()] = 1e-9  # any weight disallowed

    for trait, weight in traits.items():
        # Safety: skip disallowed overweight traits
        if trait in disallow and weight > disallow[trait]:
            continue
        resp = client.get(f"/api/v1/vectors/reference/{trait}", params={"model_name": target_model})
        vec: List[float] = resp.get("vector") or resp.get("caa_vector", {}).get("vector")
        if vec is None:
            raise RuntimeError(f"Reference vector for trait '{trait}' not available")
        if dim is None:
            dim = len(vec)
            sum_vec = [0.0] * dim
        # Resize if needed (pad/truncate)
        if len(vec) != dim:
            if len(vec) < dim:
                vec = vec + [0.0] * (dim - len(vec))
            else:
                vec = vec[:dim]
        for i in range(dim):
            sum_vec[i] += weight * vec[i]

    if dim is None:
        raise RuntimeError("Failed to compose vector; no valid traits")

    normed, norm = _normalize(sum_vec)

    env = persona.get("envelope", {}) or {}
    envelope = PersonaEnvelope(
        system_prompt=env.get("system_prompt"),
        style_markers=env.get("style_markers"),
    )

    # Recommended coefficient and layer
    rec_coef = persona.get("safety", {}).get("max_coefficient")
    # pick default 1.5, capped by max
    default_coef = 1.5
    if isinstance(rec_coef, (float, int)):
        default_coef = min(default_coef, float(rec_coef))

    comp = PersonaComposition(
        name=name,
        model=target_model,
        vector=normed,
        norm=norm,
        dimension=dim,
        recommended_layer=None,  # can be filled by optimal layer search later
        recommended_coefficient=default_coef,
        envelope=envelope,
    )
    return comp


def apply_envelope_to_prompt(prompt: str, envelope: Optional[PersonaEnvelope]) -> str:
    if envelope is None:
        return prompt
    system = envelope.system_prompt or ""
    if not system.strip():
        return prompt
    # Simple concatenation: System preface then user prompt
    return f"System: {system}\n\nUser: {prompt}"
