"""First-name-only helper display labels (warmth without roll-match identity)."""
from __future__ import annotations

# Curated, common given names used as *display* labels — not school admission names.
GIRL_NAMES = (
    'Amina', 'Wanjiru', 'Fatuma', 'Nyambura', 'Achieng', 'Njeri', 'Halima',
    'Wangari', 'Zawadi', 'Imani', 'Neema', 'Akinyi', 'Blessing', 'Mercy',
    'Faith', 'Grace', 'Sarah', 'Esther', 'Naomi', 'Mary',
)
BOY_NAMES = (
    'Kamau', 'Otieno', 'Juma', 'Kipchoge', 'Baraka', 'Mwangi', 'Odhiambo',
    'Kariuki', 'Jabari', 'Abdi', 'Kiptoo', 'Daniel', 'James', 'Brian',
    'Peter', 'Samuel', 'Joseph', 'David', 'Eric', 'Kevin',
)


def first_name_label(student_id: int, gender: str) -> str:
    """Stable first-name display for a student id (Girl/Boy)."""
    pool = GIRL_NAMES if str(gender).lower().startswith('g') else BOY_NAMES
    return pool[int(student_id) % len(pool)]
