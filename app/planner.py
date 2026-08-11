from __future__ import annotations
from typing import Dict, List

DEFAULT_STYLE = (
    "premium cinematic 3D product-film aesthetic, graphite and deep-navy modular architecture, "
    "soft volumetric lighting, restrained cyan energy accents, physically believable materials, "
    "high contrast, sophisticated industrial motion design, no UI text inside generated scenes"
)


def _scene_prompt(scene: Dict, prev_state: str) -> str:
    return (
        f"Create a seamless cinematic shot for: {scene['purpose']}. "
        f"Visual action: {scene['visual']}. Camera: {scene['camera']}. "
        "Persistent object: luminous cyan catalyst remains visible and causally drives the transformation. "
        f"Continuity inherited from previous scene: {prev_state}. "
        f"Style: {DEFAULT_STYLE}. "
        "Maintain exact material family, lighting direction, world scale and forward camera flow. "
        "No logos, letters, interface text, title cards or scene resets. End on a composition that can naturally continue forward."
    )


def make_plan(idea: str, duration: int = 30) -> Dict:
    scene_count = 6 if duration <= 35 else 8
    beats = [
        ("Hook", "A fractured product world reveals visible symptoms while deeper structural faults pulse beneath the surface.", "slow forward dolly, subtle parallax"),
        ("Diagnosis", "The cyan catalyst dives below the interface layer and exposes trust, value, activation and strategy as connected mechanical layers.", "continuous push-in through nested layers"),
        ("Research", "Signals, user behavior and business constraints organize into a coherent evidence field around the catalyst.", "orbital drift resolving into forward motion"),
        ("Strategy", "Scattered modules align into a clear product direction while unnecessary structures retract.", "controlled crane-forward move"),
        ("Experience", "The architecture becomes simpler, faster and more legible as pathways connect without visual discontinuity.", "smooth track through the newly aligned system"),
        ("Resolution", "The complete product architecture locks together into one confident system, with the catalyst settling at its core.", "hero push-in, elegant deceleration"),
        ("Impact", "The resolved system activates with a calm pulse showing clarity, trust and momentum instead of superficial decoration.", "wide-to-medium cinematic glide"),
        ("End Frame", "The environment resolves into a minimal brand-ready final composition with negative space for later typography in editing.", "slow settle, no cut"),
    ][:scene_count]
    seconds = max(4, duration // scene_count)
    scenes: List[Dict] = []
    prev_state = "same graphite/deep-navy world, forward-moving camera, cyan catalyst centered in the causal chain"
    for i, (purpose, visual, camera) in enumerate(beats, start=1):
        scene = {"id": i, "purpose": purpose, "duration": seconds, "visual": visual, "camera": camera}
        scene["prompt"] = _scene_prompt(scene, prev_state)
        scene["transition"] = "Use the final frame as the visual reference or starting frame for the next scene."
        prev_state = f"scene {i} end-frame geometry, same lighting, same catalyst position and same camera travel direction"
        scenes.append(scene)
    return {
        "title": "Solvent Studio Reel",
        "hook": "Your UX might not be the real problem.",
        "narration": "Your UX might not be the real problem. Sometimes the interface is only where a deeper business problem becomes visible. Low conversion can mean unclear value. Drop-offs can mean missing trust. Weak activation can mean value takes too long to reach. Great product design looks beneath the screen, connects evidence to strategy, and resolves the system, not just the surface.",
        "idea": idea,
        "duration": duration,
        "aspect_ratio": "9:16",
        "continuity_rules": ["One uninterrupted spatial world", "Persistent luminous cyan catalyst", "Forward camera direction", "Previous final frame becomes next scene reference", "No text baked into generated clips", "Same material family, scale and lighting across all shots"],
        "scenes": scenes,
    }
