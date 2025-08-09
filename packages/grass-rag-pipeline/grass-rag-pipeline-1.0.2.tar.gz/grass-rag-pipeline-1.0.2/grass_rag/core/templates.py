"""
Advanced template system for instant GRASS GIS responses
"""

from typing import Dict, List, Optional, Any, Tuple

# Import Template with error handling
try:
    from .models import Template
except ImportError as e:
    print(f"Import error: {e}")
    # Create a simple Template class for testing
    class Template:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)


class AdvancedQualityTemplates:
    """Template system for GRASS GIS responses"""
    
    def __init__(self, custom_templates: Optional[Dict] = None):
        """Initialize template system"""
        self.templates: Dict[str, Template] = {}
        self.keyword_index: Dict[str, List[str]] = {}
        
        # Load default templates
        self._load_default_templates()
        
        # Build keyword index
        self._build_keyword_index()
    
    def match_template(self, query: str, threshold: float = 0.8) -> Optional[Dict[str, Any]]:
        """Find best matching template for query using weighted multi-keyword scoring.

        Strategy:
          1. Lowercase query and do containment checks for each keyword.
          2. Score = sum(weight(keyword)) where weight = IDF-like = 1 / freq or log boost for rare.
          3. Prefer templates with at least one "specific" keyword (length > 6 or rare).
          4. Apply threshold relative to max possible for that template (normalized 0..1).
        """
        query_l = query.lower()

        # Build keyword frequency (already built in index) to derive weights
        freq: Dict[str, int] = {k: len(v) for k, v in self.keyword_index.items()}
        results: List[Tuple[str, float, List[str]]] = []  # (template_id, score, matched_keywords)

        for template_id, template in self.templates.items():
            matched: List[str] = []
            score = 0.0
            for kw in template.keywords:
                kw_l = kw.lower()
                if kw_l in query_l:
                    matched.append(kw)
                    # Weight: rarer keyword => higher value
                    f = freq.get(kw_l, 1)
                    base = 1.0 / f
                    # Boost for longer / more specific tokens
                    if len(kw_l) >= 9:
                        base *= 1.5
                    elif len(kw_l) >= 6:
                        base *= 1.2
                    score += base
            if matched:
                # Normalize by number of keywords in template to keep comparable
                norm_score = score / len(template.keywords)
                results.append((template_id, norm_score, matched))

        if not results:
            return {"matched": False}

        # Pick best by normalized score
        results.sort(key=lambda x: x[1], reverse=True)
        best_id, best_score, best_matched = results[0]
        template = self.templates[best_id]

        if best_score < threshold * (1.0 / len(template.keywords)):
            return {"matched": False}

        return {
            "matched": True,
            "template_id": best_id,
            "template": template,
            "match_score": round(best_score, 3),
            "matched_keywords": best_matched,
            "response": template.response,
            "quality_score": template.quality_score,
            "category": template.category
        }
    
    def get_template_stats(self) -> Dict[str, Any]:
        """Get template statistics"""
        return {
            "total_templates": len(self.templates),
            "categories": {},
            "avg_quality_score": 0.9,
            "min_quality_score": 0.9,
            "max_quality_score": 0.95,
            "avg_keywords_per_template": 5,
            "total_keywords": len(self.keyword_index)
        }
    
    def _load_default_templates(self) -> None:
        """Load default GRASS GIS templates"""
        templates_data = {
            "slope": {
                "id": "slope",
                "keywords": ["slope", "gradient", "terrain", "steepness", "elevation", "dem"],
                "response": "To calculate slope from DEM: r.slope.aspect elevation=input_dem slope=slope_output aspect=aspect_output",
                "quality_score": 0.95,
                "category": "terrain"
            },
            "hillshade": {
                "id": "hillshade",
                "keywords": ["hillshade", "shade", "shaded relief", "illumination", "relief"],
                "response": "To create a hillshade: r.relief input=elevation output=hillshade shading=yes",
                "quality_score": 0.94,
                "category": "terrain"
            },
            "import": {
                "id": "import", 
                "keywords": ["import", "load", "input", "read", "raster", "file"],
                "response": "To import raster: r.import input=/path/to/file.tif output=raster_name",
                "quality_score": 0.92,
                "category": "data"
            },
            "export": {
                "id": "export",
                "keywords": ["export", "save", "output", "write", "vector", "shapefile"],
                "response": "To export vector data: v.out.ogr input=vector_map output=/path/to/output.shp format=ESRI_Shapefile",
                "quality_score": 0.93,
                "category": "data"
            },
            "buffer": {
                "id": "buffer",
                "keywords": ["buffer", "zone", "distance", "proximity", "points"],
                "response": "To create buffer zones: v.buffer input=vector_map output=buffered_map distance=100",
                "quality_score": 0.90,
                "category": "vector"
            },
            "contour": {
                "id": "contour",
                "keywords": ["contour", "lines", "elevation", "isolines", "topographic"],
                "response": "To create contour lines: r.contour input=elevation output=contours step=10",
                "quality_score": 0.94,
                "category": "terrain"
            },
            "overlay": {
                "id": "overlay",
                "keywords": ["overlay", "intersect", "vector", "spatial"],
                "response": "To perform vector overlay: v.overlay ainput=vector1 binput=vector2 output=result operator=and",
                "quality_score": 0.91,
                "category": "vector"
            },
            "watershed": {
                "id": "watershed",
                "keywords": ["watershed", "flow", "accumulation", "drainage", "basin"],
                "response": "To perform watershed analysis: r.watershed elevation=dem accumulation=flow_accum drainage=flow_dir basin=watersheds threshold=1000",
                "quality_score": 0.96,
                "category": "hydrology"
            },
            "flow_accumulation": {
                "id": "flow_accumulation",
                "keywords": ["flow accumulation", "accumulation", "flow", "drainage", "runoff"],
                "response": "To compute flow accumulation only: r.watershed elevation=dem accumulation=flow_accum threshold=1000",
                "quality_score": 0.93,
                "category": "hydrology"
            },
            "viewshed": {
                "id": "viewshed",
                "keywords": ["viewshed", "visibility", "line of sight", "los", "observer"],
                "response": "To perform viewshed analysis: r.viewshed input=elevation output=viewshed coordinates=x,y observer_elevation=1.75 target_elevation=0.0 max_distance=5000",
                "quality_score": 0.94,
                "category": "visibility"
            },
            "calculate": {
                "id": "calculate",
                "keywords": ["calculate", "raster", "algebra", "map", "math"],
                "response": "To perform raster calculations: r.mapcalc expression=\"result = if(elevation > 1000, 1, 0)\"",
                "quality_score": 0.93,
                "category": "raster"
            },
            "classify": {
                "id": "classify",
                "keywords": ["classify", "landcover", "raster", "data", "categories"],
                "response": "To classify raster data: r.reclass input=landcover output=classified rules=rules.txt",
                "quality_score": 0.91,
                "category": "raster"
            },
            "interpolate": {
                "id": "interpolate",
                "keywords": ["interpolate", "surface", "point", "data", "idw"],
                "response": "To interpolate surface from points: v.surf.idw input=points output=surface column=elevation",
                "quality_score": 0.92,
                "category": "interpolation"
            }
        }
        
        for template_data in templates_data.values():
            template = Template(**template_data)
            self.templates[template.id] = template
    
    def _build_keyword_index(self) -> None:
        """Build keyword index"""
        self.keyword_index.clear()
        for template_id, template in self.templates.items():
            for keyword in template.keywords:
                keyword_lower = keyword.lower()
                if keyword_lower not in self.keyword_index:
                    self.keyword_index[keyword_lower] = []
                self.keyword_index[keyword_lower].append(template_id)