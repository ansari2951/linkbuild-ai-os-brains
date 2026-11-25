import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "private" / "niches"
DATA_DIR.mkdir(parents=True, exist_ok=True)

NICHE_FILE = DATA_DIR / "niche_database.json"


DEFAULT_NICHES = {
    "Technology": [
        "Software",
        "Artificial Intelligence",
        "Cybersecurity",
        "Cloud Computing",
        "Gadgets",
        "Mobile Technology",
        "Web Development"
    ],
    "Business": [
        "Entrepreneurship",
        "Startups",
        "Management",
        "Small Business",
        "Leadership",
        "Business Strategy"
    ],
    "Marketing": [
        "Digital Marketing",
        "SEO",
        "Link Building",
        "Content Marketing",
        "Social Media Marketing",
        "Email Marketing"
    ],
    "Finance": [
        "Personal Finance",
        "Investing",
        "Banking",
        "Insurance",
        "Accounting",
        "Fintech"
    ],
    "Health": [
        "Healthcare",
        "Fitness",
        "Nutrition",
        "Mental Wellness",
        "Medical Technology"
    ],
    "Lifestyle": [
        "Home Improvement",
        "Fashion",
        "Beauty",
        "Food",
        "Parenting",
        "Relationships"
    ],
    "Travel": [
        "Tourism",
        "Hotels",
        "Travel Guides",
        "Adventure Travel",
        "Luxury Travel"
    ],
    "Education": [
        "Online Learning",
        "Higher Education",
        "Career Development",
        "EdTech",
        "Student Resources"
    ],
    "Real Estate": [
        "Property Investment",
        "Residential Real Estate",
        "Commercial Real Estate",
        "Property Management"
    ],
    "Automotive": [
        "Cars",
        "Electric Vehicles",
        "Auto Repair",
        "Car Accessories"
    ]
}


class NicheIntelligence:

    def __init__(self):
        self.niches = self._load()

    def _load(self):
        if NICHE_FILE.exists():
            try:
                with open(NICHE_FILE, "r", encoding="utf-8") as file:
                    return json.load(file)
            except (json.JSONDecodeError, OSError):
                pass

        self.niches = DEFAULT_NICHES.copy()
        self._save()
        return self.niches

    def _save(self, data=None):
        payload = data if data is not None else self.niches
        with open(NICHE_FILE, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=4)

    def get_all_niches(self):
        return self.niches

    def get_categories(self):
        return list(self.niches.keys())

    def get_subniches(self, category):
        return self.niches.get(category, [])

    def add_category(self, category):
        if category not in self.niches:
            self.niches[category] = []
            self._save()

    def add_subniche(self, category, subniche):
        self.add_category(category)

        if subniche not in self.niches[category]:
            self.niches[category].append(subniche)
            self._save()

    def search_niche(self, keyword):
        keyword = keyword.lower()
        results = []

        for category, subniches in self.niches.items():
            if keyword in category.lower():
                results.append(category)

            for subniche in subniches:
                if keyword in subniche.lower():
                    results.append({
                        "category": category,
                        "subniche": subniche
                    })

        return results