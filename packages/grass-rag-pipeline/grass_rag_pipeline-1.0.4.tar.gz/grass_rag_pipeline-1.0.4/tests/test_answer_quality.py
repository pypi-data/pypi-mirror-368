from grass_rag.core.pipeline import OptimizedRAGPipeline

EVAL_CASES = {
    "calculate slope from dem": ["r.slope.aspect", "slope_output"],
    "generate aspect map": ["r.slope.aspect", "aspect_output"],
    "watershed delineation": ["r.watershed", "threshold"],
    "compute flow accumulation": ["r.watershed", "accumulation"],
    "create hillshade": ["r.relief", "hillshade"],
    "viewshed analysis": ["r.viewshed", "observer_elevation"],
    "shortest path routing": ["v.net.path", "cost"],
    "create buffer zones": ["v.buffer", "distance"],
    "cost surface model": ["r.cost", "start_coordinates"],
    "reclassify landcover": ["r.reclass", "rules"],
}

def completeness(answer: str, required: list[str]) -> float:
    found = sum(1 for kw in required if kw.lower() in answer.lower())
    return found / len(required)

def test_answer_completeness():
    pipe = OptimizedRAGPipeline()
    for query, req in EVAL_CASES.items():
        ans, src, met = pipe.query(query)
        score = completeness(ans, req)
        assert score >= 0.5, f"Answer for '{query}' missing required concepts: {req}\nGot: {ans}"
        assert met["quality_score"] >= 0.9 or met["method"] == "enhanced_fallback"
