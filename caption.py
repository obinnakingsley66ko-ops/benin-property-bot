"""
generate_caption() — Creates dynamic, attractive public channel captions.
NO price. NO phone. NO agent contact.
"""
import random
import re


SELLING_POINTS_BY_TYPE = {
    "mini flat": [
        "🛋 Cosy and well-finished interior",
        "💡 Constant electricity supply",
        "🚿 Neat private bathroom",
        "🔐 Secure and gated compound",
        "🌬 Good cross ventilation",
        "🛏 Comfortable bedroom space",
    ],
    "room and parlour": [
        "🛋 Spacious parlour area",
        "🔐 Secure environment",
        "💡 Regular power supply",
        "🚰 Good water supply",
        "🧹 Clean and well-maintained",
    ],
    "1 bedroom": [
        "🛋 Spacious sitting room",
        "🚿 Modern bathroom and toilet",
        "💡 Prepaid meter installed",
        "🔐 Safe and secured compound",
        "🌿 Serene neighbourhood",
    ],
    "2 bedroom": [
        "🛋 Generous living area",
        "🚿 Fitted bathroom and toilet",
        "💡 Prepaid electricity meter",
        "🚗 Parking space available",
        "🔐 Gated and secure compound",
        "🌿 Quiet residential area",
    ],
    "3 bedroom": [
        "🛋 Spacious rooms throughout",
        "🍳 Modern kitchen fittings",
        "🚿 En-suite master bedroom",
        "🚗 Ample parking space",
        "🔐 24/7 security",
        "🌿 Family-friendly neighbourhood",
    ],
    "4 bedroom": [
        "🏡 Large compound and garden",
        "🍳 Fully fitted kitchen",
        "🚿 Multiple bathrooms",
        "🚗 Spacious car park",
        "🔐 Top-notch security",
        "🌿 Prestigious location",
    ],
    "duplex": [
        "🏡 Elegant duplex design",
        "🍳 Modern kitchen fittings",
        "🚿 Multiple en-suite bathrooms",
        "🚗 Large parking area",
        "🔐 Secure estate",
        "🌿 Prime neighbourhood",
    ],
    "flat": [
        "🛋 Well-finished flat",
        "💡 Steady electricity",
        "🚿 Clean bathroom and toilet",
        "🔐 Secure compound",
        "🌬 Well-ventilated rooms",
    ],
    "bungalow": [
        "🏡 All on one floor — easy access",
        "🌿 Big compound with space to spare",
        "🚗 Parking within compound",
        "🔐 Safe and quiet area",
        "💡 Good power supply",
    ],
    "self-contain": [
        "🔑 Full self-contain with kitchen",
        "🚿 Private bathroom and toilet",
        "💡 Prepaid meter",
        "🔐 Secure environment",
        "🌬 Well ventilated",
    ],
    "office": [
        "💼 Professional office layout",
        "💡 Steady power supply",
        "🚗 Parking for clients and staff",
        "🔐 Secure business environment",
        "📶 Good internet connectivity",
    ],
    "shop": [
        "🏪 High foot traffic area",
        "💡 Power supply available",
        "🚗 Easy vehicle access",
        "🔐 Secure location",
        "📦 Good storage space",
    ],
    "default": [
        "🛋 Well-finished interior",
        "💡 Good electricity supply",
        "🚿 Clean bathroom and toilet",
        "🔐 Secure and gated compound",
        "🌿 Calm neighbourhood",
        "🚗 Accessible road",
        "🌬 Well ventilated",
        "🔑 Ready to move in",
    ],
}

URGENCY_LINES = [
    "🔥 Hot deal — don't miss out!",
    "⚡ Going fast — act now!",
    "🏃 Limited availability!",
    "🔥 High demand — contact today!",
    "⚡ Serious enquiries only",
    "🏃 Won't last long at this offer!",
    "🔥 Top pick of the week!",
    "⚡ Enquire before it's gone!",
]


def _extract_property_type(title: str) -> str:
    """Detect property type keyword from listing title."""
    title_lower = (title or "").lower()
    ordered = [
        "room and parlour", "mini flat", "self-contain",
        "1 bedroom", "2 bedroom", "3 bedroom", "4 bedroom",
        "duplex", "bungalow", "flat", "apartment",
        "office", "shop",
    ]
    for pt in ordered:
        if pt in title_lower:
            return pt
    return "default"


def _pick_selling_points(property_type: str, n: int = 3) -> list[str]:
    """Pick n random selling points appropriate for the property type."""
    pool = SELLING_POINTS_BY_TYPE.get(property_type) or SELLING_POINTS_BY_TYPE["default"]
    return random.sample(pool, min(n, len(pool)))


def generate_caption(listing: dict) -> str:
    """
    Build a dynamic, attractive public-facing caption for a Telegram channel post.

    Rules:
    - NO price
    - NO phone number
    - NO agent contact details (other than the DM call-to-action)
    - Varies each call via random selection
    """
    title = (listing.get("title") or "Property Available").strip()
    location = (listing.get("location") or "Benin City, Edo").strip()

    title_display = _title_case_property(title)

    prop_type = _extract_property_type(title)
    selling_points = _pick_selling_points(prop_type, n=3)
    urgency = random.choice(URGENCY_LINES)

    points_block = "\n".join(selling_points)

    caption = (
        f"🏠 *{title_display}*\n"
        f"\n"
        f"📍 {location}\n"
        f"\n"
        f"{points_block}\n"
        f"\n"
        f"{urgency}\n"
        f"\n"
        f"📲 DM @Kingsley0136 for price, details & inspection"
    )

    return caption


def _title_case_property(title: str) -> str:
    """Capitalise title nicely; avoid all-caps or all-lowercase."""
    words = title.split()
    minor = {"and", "or", "for", "in", "at", "of", "a", "an", "the", "with"}
    result = []
    for i, w in enumerate(words):
        if i == 0 or w.lower() not in minor:
            result.append(w.capitalize())
        else:
            result.append(w.lower())
    return " ".join(result)
