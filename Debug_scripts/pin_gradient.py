import random

# SITE selects which die's gradient to use: "bottom" or "top"
SITE = "bottom"

# Base fail probability per pin for each site (0.0–1.0)
# pin: (name, bottom_fail_prob, top_fail_prob)
_pins_both = {
    1:  ("JSOURCE_SENSE",  0.65, 0.24),
    2:  ("PINTVCC",        0.72, 0.31),
    3:  ("INTVCC",         0.78, 0.37),
    4:  ("AGND",           0.82, 0.41),
    5:  ("PGND",           0.86, 0.45),
    6:  ("VIN",            1.00, 0.58),
    7:  ("IN",             0.96, 0.58),
    8:  ("RSLEW",          0.92, 0.58),
    9:  ("OCP",            0.88, 0.57),
    10: ("TEMPOUT_READY",  0.84, 0.55),
    11: ("READY",          0.82, 0.50),
    12: ("JGATE_1",        0.32, 0.01),
    13: ("PGND_1",         0.02, 0.00),
    14: ("PGND_8",         0.23, 0.13),
    15: ("PGND_14",        0.44, 0.31),
    16: ("PGND_21",        0.65, 0.46),
    17: ("JSOURCE_1",      0.00, 0.00),
    18: ("JSOURCE_9",      0.24, 0.00),
    19: ("JSOURCE_16",     0.43, 0.14),
    20: ("JSOURCE_24",     0.62, 0.26),
}

# Flatten to single-site view: pin -> (name, fail_prob)
_site_index = 1 if SITE == "bottom" else 2
pins = {pin: (vals[0], vals[_site_index]) for pin, vals in _pins_both.items()}


def run_loop():
    """Returns pass/fail result for every pin in one loop. True = FAIL."""
    return {pin: random.random() < fail_prob for pin, (_, fail_prob) in pins.items()}


# --- Simulate N loops and accumulate ---
N_LOOPS = 1000
fail_counts = {pin: 0 for pin in pins}

for _ in range(N_LOOPS):
    for pin, failed in run_loop().items():
        if failed:
            fail_counts[pin] += 1

# --- Report empirical vs expected ---
print(f"Site: {SITE.upper()}  ({N_LOOPS} loops)\n")
print(f"{'Pin':<4} {'Name':<20} {'Expected':>9} {'Actual':>9}")
print("-" * 46)
for pin, (name, fail_prob) in pins.items():
    actual = fail_counts[pin] / N_LOOPS * 100
    print(f"{pin:<4} {name:<20} {fail_prob*100:>8.0f}% {actual:>8.1f}%")
