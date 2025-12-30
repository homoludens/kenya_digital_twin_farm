"""Fertilizer scenario configuration data."""

DEFAULT_FERT_SCENARIOS = {
    "none": {
        "name": "No Fertilizer",
        "total_n": 0,
        "applications": [],
        "description": "Baseline - soil N only",
        "enabled": True,
    },
    "low": {
        "name": "Low (25 kg N/ha)",
        "total_n": 25,
        "applications": [(0, 15, 0.7), (30, 10, 0.6)],
        "description": "Typical smallholder",
        "enabled": True,
    },
    "medium": {
        "name": "Medium (50 kg N/ha)",
        "total_n": 50,
        "applications": [(0, 20, 0.7), (30, 15, 0.65), (50, 15, 0.6)],
        "description": "Improved smallholder",
        "enabled": True,
    },
    "recommended": {
        "name": "Recommended (75 kg N/ha)",
        "total_n": 75,
        "applications": [(0, 25, 0.7), (30, 25, 0.65), (50, 25, 0.6)],
        "description": "Extension recommendation",
        "enabled": True,
    },
    "high": {
        "name": "High (100 kg N/ha)",
        "total_n": 100,
        "applications": [(0, 30, 0.7), (25, 35, 0.65), (50, 35, 0.6)],
        "description": "Commercial/intensive",
        "enabled": True,
    },
}
