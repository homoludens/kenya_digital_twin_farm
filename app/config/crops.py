"""Crop configuration data."""

CROP_OPTIONS = {
    "barley": {
        "variety": "Spring_barley_301",
        "kenya_relevance": "Highland areas, similar N response to maize",
        "planting_month": 3,
        "planting_day": 15,
        "season_days": 120,
        "n_demand": "medium",
    },
    "wheat": {
        "variety": "Winter_wheat_101",
        "kenya_relevance": "Narok, Nakuru wheat belt",
        "planting_month": 6,
        "planting_day": 1,
        "season_days": 150,
        "n_demand": "medium-high",
        "needs_vern_override": True,
    },
    "potato": {
        "variety": "Potato_701",
        "kenya_relevance": "Central highlands (Nyandarua, Meru)",
        "planting_month": 3,
        "planting_day": 15,
        "season_days": 120,
        "n_demand": "high",
    },
    "cassava": {
        "variety": "Cassava_VanHeemst_1988",
        "kenya_relevance": "Coast, Western Kenya",
        "planting_month": 3,
        "planting_day": 15,
        "season_days": 300,
        "n_demand": "low",
    },
    "sweetpotato": {
        "variety": "Sweetpotato_VanHeemst_1988",
        "kenya_relevance": "Food security crop, Western Kenya",
        "planting_month": 3,
        "planting_day": 15,
        "season_days": 150,
        "n_demand": "low",
    },
}

# Phenophase definitions for GDD visualization (fraction of total GDD)
PHENOPHASES = {
    "barley": {
        "name": "Barley",
        "total_gdd": 1550,
        "phases": [
            ("Germination", 0, 0.07, "#8B4513"),
            ("Tillering", 0.07, 0.25, "#228B22"),
            ("Stem Extension", 0.25, 0.45, "#32CD32"),
            ("Heading", 0.45, 0.55, "#FFD700"),
            ("Flowering", 0.55, 0.65, "#FF8C00"),
            ("Grain Fill", 0.65, 0.90, "#DAA520"),
            ("Maturity", 0.90, 1.0, "#8B0000"),
        ],
    },
    "wheat": {
        "name": "Wheat",
        "total_gdd": 1800,
        "phases": [
            ("Germination", 0, 0.06, "#8B4513"),
            ("Tillering", 0.06, 0.22, "#228B22"),
            ("Stem Extension", 0.22, 0.42, "#32CD32"),
            ("Heading", 0.42, 0.52, "#FFD700"),
            ("Flowering", 0.52, 0.62, "#FF8C00"),
            ("Grain Fill", 0.62, 0.88, "#DAA520"),
            ("Maturity", 0.88, 1.0, "#8B0000"),
        ],
    },
    "rice": {
        "name": "Rice",
        "total_gdd": 2100,
        "phases": [
            ("Germination", 0, 0.05, "#8B4513"),
            ("Seedling", 0.05, 0.15, "#90EE90"),
            ("Tillering", 0.15, 0.35, "#228B22"),
            ("Stem Extension", 0.35, 0.50, "#32CD32"),
            ("Heading", 0.50, 0.60, "#FFD700"),
            ("Flowering", 0.60, 0.70, "#FF8C00"),
            ("Grain Fill", 0.70, 0.92, "#DAA520"),
            ("Maturity", 0.92, 1.0, "#8B0000"),
        ],
    },
    "potato": {
        "name": "Potato",
        "total_gdd": 1500,
        "phases": [
            ("Sprouting", 0, 0.10, "#8B4513"),
            ("Vegetative", 0.10, 0.35, "#228B22"),
            ("Tuber Init.", 0.35, 0.50, "#32CD32"),
            ("Tuber Bulk", 0.50, 0.85, "#DAA520"),
            ("Maturity", 0.85, 1.0, "#8B0000"),
        ],
    },
    "soybean": {
        "name": "Soybean",
        "total_gdd": 1400,
        "phases": [
            ("Germination", 0, 0.08, "#8B4513"),
            ("Vegetative", 0.08, 0.40, "#228B22"),
            ("Flowering", 0.40, 0.55, "#FF8C00"),
            ("Pod Dev.", 0.55, 0.75, "#FFD700"),
            ("Seed Fill", 0.75, 0.92, "#DAA520"),
            ("Maturity", 0.92, 1.0, "#8B0000"),
        ],
    },
    "cowpea": {
        "name": "Cowpea",
        "total_gdd": 1100,
        "phases": [
            ("Germination", 0, 0.08, "#8B4513"),
            ("Vegetative", 0.08, 0.45, "#228B22"),
            ("Flowering", 0.45, 0.60, "#FF8C00"),
            ("Pod Fill", 0.60, 0.90, "#DAA520"),
            ("Maturity", 0.90, 1.0, "#8B0000"),
        ],
    },
    "groundnut": {
        "name": "Groundnut",
        "total_gdd": 1500,
        "phases": [
            ("Germination", 0, 0.07, "#8B4513"),
            ("Vegetative", 0.07, 0.35, "#228B22"),
            ("Flowering", 0.35, 0.50, "#FF8C00"),
            ("Pegging", 0.50, 0.65, "#FFD700"),
            ("Pod Fill", 0.65, 0.90, "#DAA520"),
            ("Maturity", 0.90, 1.0, "#8B0000"),
        ],
    },
    "cassava": {
        "name": "Cassava",
        "total_gdd": 4500,
        "phases": [
            ("Sprouting", 0, 0.05, "#8B4513"),
            ("Leaf Dev.", 0.05, 0.20, "#90EE90"),
            ("Vegetative", 0.20, 0.50, "#228B22"),
            ("Root Bulk", 0.50, 0.90, "#DAA520"),
            ("Maturity", 0.90, 1.0, "#8B0000"),
        ],
    },
    "sweetpotato": {
        "name": "Sweet Potato",
        "total_gdd": 2200,
        "phases": [
            ("Establishment", 0, 0.10, "#8B4513"),
            ("Vine Dev.", 0.10, 0.35, "#228B22"),
            ("Root Init.", 0.35, 0.50, "#32CD32"),
            ("Root Bulk", 0.50, 0.90, "#DAA520"),
            ("Maturity", 0.90, 1.0, "#8B0000"),
        ],
    },
}
