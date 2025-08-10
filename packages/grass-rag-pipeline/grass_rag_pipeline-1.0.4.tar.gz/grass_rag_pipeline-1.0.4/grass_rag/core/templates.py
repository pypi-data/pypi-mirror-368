"""Advanced template system for instant GRASS GIS responses (single clean implementation)."""
from typing import Dict, List, Optional, Any, Tuple

try:  # Normal path
    from .models import Template
except Exception:  # Fallback for isolated import contexts
    class Template:  # type: ignore
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)


class AdvancedQualityTemplates:
    """Provides fast, high-quality, structured answers for common GRASS GIS tasks.

    Notes:
        This file previously contained duplicated method definitions causing the
        rich structured fields (command, steps, prerequisites, notes) to be lost.
        The implementation has been consolidated so only one set of methods
        remains and structured template content is preserved.
    """

    def __init__(self, custom_templates: Optional[Dict] = None):
        self.templates: Dict[str, Template] = {}
        self.keyword_index: Dict[str, List[str]] = {}
        self._load_default_templates()
        if custom_templates:
            for t in custom_templates.values():
                self.templates[t.id] = t
        self._build_keyword_index()

    # ------------------------------------------------------------------
    # Template Loading
    # ------------------------------------------------------------------
    def _load_default_templates(self) -> None:
        """Load default templates with structured answer components."""
        templates_data: Dict[str, Dict[str, Any]] = {
            "slope": {
                "id": "slope",
                "keywords": ["slope", "gradient", "terrain", "steepness", "elevation", "dem"],
                "response": "Calculate slope from a DEM using r.slope.aspect.",
                "command": "r.slope.aspect elevation=input_dem slope=slope_output aspect=aspect_output format=degrees",
                "prerequisites": [
                    "DEM imported (r.import)",
                    "Region set to DEM (g.region raster=input_dem)"
                ],
                "steps": [
                    "Import DEM if needed",
                    "Set computational region",
                    "Run r.slope.aspect",
                    "Inspect resulting slope and aspect maps"
                ],
                "notes": "Use format=percent for percent slope.",
                "quality_score": 0.95,
                "category": "terrain"
            },
            "aspect": {
                "id": "aspect",
                "keywords": ["aspect", "orientation", "exposure", "slope aspect", "aspect map"],
                "response": "Generate aspect map from DEM using r.slope.aspect.",
                "command": "r.slope.aspect elevation=input_dem aspect=aspect_output slope=slope_output",
                "steps": ["Ensure DEM available", "Run r.slope.aspect specifying aspect output"],
                "quality_score": 0.94,
                "category": "terrain"
            },
            "hillshade": {
                "id": "hillshade",
                "keywords": ["hillshade", "shade", "shaded relief", "illumination", "relief"],
                "response": "Create hillshade (shaded relief) using r.relief.",
                "command": "r.relief input=elevation output=hillshade",
                "steps": ["Import/prepare elevation raster", "Run r.relief", "Adjust color table if desired"],
                "quality_score": 0.94,
                "category": "terrain"
            },
            "import": {
                "id": "import",
                "keywords": ["import", "load", "input", "read", "raster", "file"],
                "response": "Import external raster with r.import.",
                "command": "r.import input=/path/to/file.tif output=raster_name",
                "steps": ["Run r.import", "Verify with r.info", "Set region: g.region raster=raster_name"],
                "quality_score": 0.92,
                "category": "data"
            },
            "export": {
                "id": "export",
                "keywords": ["export", "save", "output", "write", "vector", "shapefile"],
                "response": "Export vector to Shapefile using v.out.ogr.",
                "command": "v.out.ogr input=vector_map output=export_dir format=ESRI_Shapefile",
                "steps": ["Ensure vector map exists", "Run v.out.ogr", "Check output files"],
                "quality_score": 0.93,
                "category": "data"
            },
            "buffer": {
                "id": "buffer",
                "keywords": ["buffer", "zone", "distance", "proximity", "points"],
                "response": "Create buffer zones with v.buffer.",
                "command": "v.buffer input=vector_map output=buffered_map distance=100",
                "steps": ["Run v.buffer with distance parameter", "Visualize buffered output"],
                "quality_score": 0.90,
                "category": "vector"
            },
            "contour": {
                "id": "contour",
                "keywords": ["contour", "lines", "elevation", "isolines", "topographic"],
                "response": "Generate contour lines using r.contour.",
                "command": "r.contour input=elevation output=contours step=10",
                "steps": ["Set region to elevation raster", "Run r.contour with chosen step"],
                "quality_score": 0.94,
                "category": "terrain"
            },
            "overlay": {
                "id": "overlay",
                "keywords": ["overlay", "intersect", "vector", "spatial"],
                "response": "Vector overlay (intersection) with v.overlay.",
                "command": "v.overlay ainput=vector1 binput=vector2 output=result operator=and",
                "steps": ["Ensure both input vectors present", "Run v.overlay with operator=and"],
                "quality_score": 0.91,
                "category": "vector"
            },
            "watershed": {
                "id": "watershed",
                "keywords": ["watershed", "flow", "accumulation", "drainage", "basin"],
                "response": "Watershed delineation and flow accumulation via r.watershed.",
                "command": "r.watershed elevation=dem accumulation=flow_accum drainage=flow_dir basin=watersheds threshold=1000",
                "steps": [
                    "Set region to DEM",
                    "Run r.watershed with suitable threshold",
                    "Optionally vectorize basins (r.to.vect)"
                ],
                "quality_score": 0.96,
                "category": "hydrology"
            },
            "flow_accumulation": {
                "id": "flow_accumulation",
                "keywords": ["flow accumulation", "accumulation", "flow", "runoff"],
                "response": "Compute flow accumulation raster with r.watershed.",
                "command": "r.watershed elevation=dem accumulation=flow_accum threshold=1000",
                "steps": ["Run r.watershed focusing on accumulation output"],
                "quality_score": 0.93,
                "category": "hydrology"
            },
            "viewshed": {
                "id": "viewshed",
                "keywords": ["viewshed", "visibility", "line of sight", "observer"],
                "response": "Viewshed (line-of-sight) analysis using r.viewshed.",
                "command": "r.viewshed input=elevation output=viewshed coordinates=x,y observer_elevation=1.75 target_elevation=0.0 max_distance=5000",
                "steps": ["Prepare elevation raster", "Run r.viewshed with observer coordinates"],
                "quality_score": 0.94,
                "category": "visibility"
            },
            "calculate": {
                "id": "calculate",
                "keywords": ["calculate", "raster", "algebra", "map", "math"],
                "response": "Raster algebra with r.mapcalc.",
                "command": "r.mapcalc expression=\"result = if(elevation > 1000, 1, 0)\"",
                "steps": ["Decide logical expression", "Run r.mapcalc", "Inspect result"],
                "quality_score": 0.93,
                "category": "raster"
            },
            "classify": {
                "id": "classify",
                "keywords": ["classify", "classification", "landcover", "reclass"],
                "response": "Reclassify landcover raster with r.reclass.",
                "command": "r.reclass input=landcover output=classified rules=rules.txt",
                "steps": ["Prepare rules file", "Run r.reclass", "Verify categories"],
                "quality_score": 0.91,
                "category": "raster"
            },
            "interpolate": {
                "id": "interpolate",
                "keywords": ["interpolate", "interpolation", "surface", "idw", "points"],
                "response": "Inverse distance weighting interpolation via v.surf.idw.",
                "command": "v.surf.idw input=points output=surface column=elevation",
                "steps": ["Import point data", "Run v.surf.idw"] ,
                "quality_score": 0.92,
                "category": "interpolation"
            },
            "resample": {
                "id": "resample",
                "keywords": ["resample", "resolution", "scale", "r.resamp"],
                "response": "Resample raster resolution with r.resamp.interp (bilinear example).",
                "command": "r.resamp.interp input=src_raster output=dst_raster method=bilinear",
                "steps": ["Choose interpolation method", "Run r.resamp.interp"],
                "quality_score": 0.92,
                "category": "raster"
            },
            "network": {
                "id": "network",
                "keywords": ["network", "shortest path", "routing", "v.net", "path"],
                "response": "Compute shortest path using v.net.path after building network.",
                "command": "v.net.path input=roads output=shortest_path afcolumn=cost abcolumn=cost",
                "steps": ["Prepare network topology (v.net)", "Run v.net.path"],
                "quality_score": 0.93,
                "category": "network"
            },
            "cost_surface": {
                "id": "cost_surface",
                "keywords": ["cost surface", "least cost", "r.cost", "accumulative"],
                "response": "Create cost surface raster using r.cost.",
                "command": "r.cost input=elevation output=cost_surface start_coordinates=x,y",
                "steps": ["Set region", "Run r.cost with start coordinates"],
                "quality_score": 0.93,
                "category": "terrain"
            },
            "reproject": {
                "id": "reproject",
                "keywords": ["reproject", "projection", "r.proj"],
                "response": "Reproject raster using r.proj from another location.",
                "command": "r.proj location=src_location map=src_raster output=dst_raster",
                "steps": ["Set target location", "Run r.proj", "Verify with r.info"],
                "quality_score": 0.93,
                "category": "data"
            },
            "extract_values": {
                "id": "extract_values",
                "keywords": ["extract", "values", "v.what.rast", "raster", "sample"],
                "response": "Extract raster values at vector point locations using v.what.rast.",
                "command": "v.what.rast map=points raster=elevation column=elev_val",
                "steps": ["Ensure points map exists", "Run v.what.rast specifying output column"],
                "quality_score": 0.92,
                "category": "data"
            }
        }

        for data in templates_data.values():
            self.templates[data["id"]] = Template(**data)

    # ------------------------------------------------------------------
    def _build_keyword_index(self) -> None:
        self.keyword_index.clear()
        for tid, tpl in self.templates.items():
            for kw in tpl.keywords:
                self.keyword_index.setdefault(kw.lower(), []).append(tid)

    # ------------------------------------------------------------------
    def match_template(self, query: str, threshold: float = 0.8) -> Dict[str, Any]:
        """Match query to best template using weighted keyword scoring.

        Returns dict with keys: matched(bool), response(str) (enriched), template_id,
        quality_score, match_score, matched_keywords, category, alternative_id(optional).
        """
        ql = query.lower()
        # Build frequency for IDF-like weighting
        freq: Dict[str, int] = {}
        for tpl in self.templates.values():
            for kw in tpl.keywords:
                k = kw.lower()
                freq[k] = freq.get(k, 0) + 1

        scored: List[Tuple[str, float, List[str]]] = []
        for tid, tpl in self.templates.items():
            matched: List[str] = []
            score = 0.0
            for kw in tpl.keywords:
                kl = kw.lower()
                if kl in ql:
                    matched.append(kw)
                    base = 1.0 / max(freq.get(kl, 1), 1)
                    if len(kl) >= 9:
                        base *= 1.5
                    elif len(kl) >= 6:
                        base *= 1.2
                    score += base
            if matched:
                scored.append((tid, score / len(tpl.keywords), matched))

        if not scored:
            return {"matched": False}

        scored.sort(key=lambda x: x[1], reverse=True)
        best_id, best_score, matched = scored[0]
        best_tpl = self.templates[best_id]
        # Threshold relative to template keyword count
        if best_score < threshold * (1.0 / len(best_tpl.keywords)):
            return {"matched": False}

        alt_id = None
        if len(scored) > 1:
            sid, sscore, _ = scored[1]
            if sscore >= 0.9 * best_score and sid != best_id:
                alt_id = sid

        # Build enriched response
        enriched = best_tpl.response
        if getattr(best_tpl, 'command', ''):
            enriched += f"\nCommand: {best_tpl.command}"
        if getattr(best_tpl, 'prerequisites', []):
            enriched += "\nPrerequisites:\n" + "\n".join(f"- {p}" for p in best_tpl.prerequisites)
        if getattr(best_tpl, 'steps', []):
            enriched += "\nSteps:\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(best_tpl.steps))
        if getattr(best_tpl, 'notes', ''):
            enriched += f"\nNotes: {best_tpl.notes}"
        if alt_id:
            alt_tpl = self.templates[alt_id]
            enriched += f"\nAlternative: {alt_tpl.id}" + (f"\nAlt Command: {alt_tpl.command}" if getattr(alt_tpl, 'command', '') else '')

        return {
            "matched": True,
            "template_id": best_id,
            "response": enriched,
            "quality_score": best_tpl.quality_score,
            "match_score": round(best_score, 3),
            "matched_keywords": matched,
            "category": best_tpl.category,
            "alternative_id": alt_id
        }

    # ------------------------------------------------------------------
    def get_template_stats(self) -> Dict[str, Any]:
        categories: Dict[str, int] = {}
        for t in self.templates.values():  # count per category
            cat = getattr(t, 'category', 'uncategorized')
            categories[cat] = categories.get(cat, 0) + 1
        return {
            "total_templates": len(self.templates),
            "categories": categories,
            "avg_quality_score": round(sum(t.quality_score for t in self.templates.values()) / max(len(self.templates), 1), 3),
            "max_quality_score": max((t.quality_score for t in self.templates.values()), default=0),
            "min_quality_score": min((t.quality_score for t in self.templates.values()), default=0),
            "avg_keywords_per_template": round(sum(len(t.keywords) for t in self.templates.values()) / max(len(self.templates), 1), 2),
            "total_keywords": sum(len(t.keywords) for t in self.templates.values())
        }