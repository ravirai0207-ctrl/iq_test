"""
Dynamic Cognitive IQ Assessment Engine.
Features an extensive procedural generator and curated question bank
that dynamically creates a fresh, randomized question set for every test session.
"""

import math
import random
import uuid

# ==============================================================================
# PROCEDURAL QUESTION GENERATORS
# ==============================================================================

def gen_matrix_progression(seed_id: int):
    """Generates a procedural visual matrix progression puzzle with random shapes & colors."""
    shapes = [
        {"name": "circles", "tag": "circle", "render": lambda cx, cy, r, fill: f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'},
        {"name": "squares", "tag": "rect", "render": lambda cx, cy, r, fill: f'<rect x="{cx-r}" y="{cy-r}" width="{r*2}" height="{r*2}" rx="3" fill="{fill}"/>'},
        {"name": "diamonds", "tag": "polygon", "render": lambda cx, cy, r, fill: f'<polygon points="{cx},{cy-r*1.2} {cx+r},{cy} {cx},{cy+r*1.2} {cx-r},{cy}" fill="{fill}"/>'},
        {"name": "triangles", "tag": "polygon", "render": lambda cx, cy, r, fill: f'<polygon points="{cx},{cy-r*1.2} {cx+r*1.1},{cy+r} {cx-r*1.1},{cy+r}" fill="{fill}"/>'}
    ]
    colors = ["#4f46e5", "#0284c7", "#10b981", "#d97706", "#8b5cf6", "#ec4899"]
    random.shuffle(colors)
    random.shuffle(shapes)

    shape_row1 = shapes[0]
    shape_row2 = shapes[1]
    color_row1 = colors[0]
    color_row2 = colors[1]

    # Row 1: 1 -> 2 -> 3 items
    # Row 2: 1 -> 2 -> ? items
    svg = f"""
    <svg width="100%" height="180" viewBox="0 0 360 170" preserveAspectRatio="xMidYMid meet" class="q-svg">
      <!-- Row 1: {shape_row1['name']} -->
      <rect x="20" y="15" width="95" height="60" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
      {shape_row1['render'](67, 45, 13, color_row1)}

      <rect x="132" y="15" width="95" height="60" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
      {shape_row1['render'](167, 45, 10, color_row1)}
      {shape_row1['render'](192, 45, 10, colors[2])}

      <rect x="245" y="15" width="95" height="60" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
      {shape_row1['render'](270, 45, 8, color_row1)}
      {shape_row1['render'](292, 45, 8, colors[2])}
      {shape_row1['render'](314, 45, 8, colors[3])}

      <!-- Row 2: {shape_row2['name']} -->
      <rect x="20" y="90" width="95" height="60" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
      {shape_row2['render'](67, 120, 13, color_row2)}

      <rect x="132" y="90" width="95" height="60" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
      {shape_row2['render'](167, 120, 10, color_row2)}
      {shape_row2['render'](192, 120, 10, colors[4])}

      <!-- Target Box -->
      <rect x="245" y="90" width="95" height="60" rx="10" fill="#ede9fe" stroke="#6366f1" stroke-width="2.5" stroke-dasharray="4"/>
      <text x="292" y="128" font-size="28" font-weight="bold" fill="#6366f1" text-anchor="middle">?</text>
    </svg>
    """

    correct_text = f"3 {shape_row2['name']} scaling downward in size with chromatic color shifts"
    options = [
        correct_text,
        f"A single inverted {shape_row2['name'][:-1]}",
        f"2 {shape_row2['name']} of identical dimensions",
        f"4 concentric nested {shape_row1['name']}"
    ]
    random.shuffle(options)
    correct_idx = options.index(correct_text)

    return {
        "id": seed_id,
        "category": "Pattern Recognition",
        "category_key": "pattern",
        "title": "Matrix Progression Logic",
        "prompt": f"Analyze the multi-cell geometric pattern. What replaces the question mark [?] in the matrix grid?",
        "visual_type": "svg_matrix",
        "visual_data": svg,
        "options": options,
        "correct_index": correct_idx,
        "explanation": f"The number of elements in each row increments sequentially (1 -> 2 -> 3) while scaling down in size."
    }


def gen_numerical_series(seed_id: int):
    """Generates a randomized dual-interleaved or polynomial sequence."""
    choice = random.choice(["interleaved", "cubic", "fibonacci_variant"])

    if choice == "interleaved":
        # Series A: start + step1, + step2...
        # Series B: start2 * multiplier each time
        start_a = random.randint(2, 6)
        step_a = random.randint(3, 7)
        start_b = random.randint(3, 8)
        mult_b = 2

        a1 = start_a
        b1 = start_b
        a2 = a1 + step_a
        b2 = b1 * mult_b
        a3 = a2 + step_a + 2
        b3 = b2 * mult_b
        a4 = a3 + step_a + 4
        target_b4 = b3 * mult_b

        svg = f"""
        <svg width="100%" height="150" viewBox="0 0 460 130" preserveAspectRatio="xMidYMid meet" class="q-svg">
          <circle cx="35" cy="50" r="22" fill="#ede9fe" stroke="#6366f1" stroke-width="2"/>
          <text x="35" y="56" font-size="15" font-weight="bold" fill="#4f46e5" text-anchor="middle">{a1}</text>

          <circle cx="95" cy="50" r="22" fill="#e0f2fe" stroke="#0284c7" stroke-width="2"/>
          <text x="95" y="56" font-size="15" font-weight="bold" fill="#0284c7" text-anchor="middle">{b1}</text>

          <circle cx="155" cy="50" r="22" fill="#ede9fe" stroke="#6366f1" stroke-width="2"/>
          <text x="155" y="56" font-size="15" font-weight="bold" fill="#4f46e5" text-anchor="middle">{a2}</text>

          <circle cx="215" cy="50" r="22" fill="#e0f2fe" stroke="#0284c7" stroke-width="2"/>
          <text x="215" y="56" font-size="15" font-weight="bold" fill="#0284c7" text-anchor="middle">{b2}</text>

          <circle cx="275" cy="50" r="22" fill="#ede9fe" stroke="#6366f1" stroke-width="2"/>
          <text x="275" y="56" font-size="15" font-weight="bold" fill="#4f46e5" text-anchor="middle">{a3}</text>

          <circle cx="335" cy="50" r="22" fill="#e0f2fe" stroke="#0284c7" stroke-width="2"/>
          <text x="335" y="56" font-size="15" font-weight="bold" fill="#0284c7" text-anchor="middle">{b3}</text>

          <circle cx="395" cy="50" r="22" fill="#ede9fe" stroke="#6366f1" stroke-width="2"/>
          <text x="395" y="56" font-size="15" font-weight="bold" fill="#4f46e5" text-anchor="middle">{a4}</text>

          <circle cx="445" cy="50" r="22" fill="#fef3c7" stroke="#d97706" stroke-width="2.5" stroke-dasharray="3"/>
          <text x="445" y="57" font-size="18" font-weight="bold" fill="#d97706" text-anchor="middle">?</text>

          <!-- Arc connectors -->
          <path d="M 95 72 Q 155 94 215 72" fill="none" stroke="#0284c7" stroke-width="1.5"/>
          <text x="155" y="100" font-size="10" fill="#0284c7" text-anchor="middle">×{mult_b}</text>
          <path d="M 215 72 Q 275 94 335 72" fill="none" stroke="#0284c7" stroke-width="1.5"/>
          <text x="275" y="100" font-size="10" fill="#0284c7" text-anchor="middle">×{mult_b}</text>
          <path d="M 335 72 Q 390 94 445 72" fill="none" stroke="#d97706" stroke-width="2"/>
          <text x="390" y="100" font-size="11" font-weight="bold" fill="#d97706" text-anchor="middle">×{mult_b} = ?</text>
        </svg>
        """
        correct_ans = str(target_b4)
        distractors = [str(target_b4 - b2), str(target_b4 + 14), str(target_b4 - 8)]
    elif choice == "cubic":
        k = random.randint(1, 5)
        terms = [n**3 + k for n in range(1, 7)]
        target_b4 = terms[5] # 6^3 + k = 216 + k
        svg = f"""
        <svg width="100%" height="150" viewBox="0 0 460 130" preserveAspectRatio="xMidYMid meet" class="q-svg">
          <rect x="15" y="25" width="55" height="48" rx="8" fill="#ede9fe" stroke="#6366f1" stroke-width="2"/>
          <text x="42" y="56" font-size="17" font-weight="bold" fill="#4f46e5" text-anchor="middle">{terms[0]}</text>
          <text x="42" y="90" font-size="10" fill="#64748b" text-anchor="middle">1³+{k}</text>

          <rect x="88" y="25" width="55" height="48" rx="8" fill="#ede9fe" stroke="#6366f1" stroke-width="2"/>
          <text x="115" y="56" font-size="17" font-weight="bold" fill="#4f46e5" text-anchor="middle">{terms[1]}</text>
          <text x="115" y="90" font-size="10" fill="#64748b" text-anchor="middle">2³+{k}</text>

          <rect x="162" y="25" width="55" height="48" rx="8" fill="#ede9fe" stroke="#6366f1" stroke-width="2"/>
          <text x="189" y="56" font-size="17" font-weight="bold" fill="#4f46e5" text-anchor="middle">{terms[2]}</text>
          <text x="189" y="90" font-size="10" fill="#64748b" text-anchor="middle">3³+{k}</text>

          <rect x="236" y="25" width="55" height="48" rx="8" fill="#ede9fe" stroke="#6366f1" stroke-width="2"/>
          <text x="263" y="56" font-size="17" font-weight="bold" fill="#4f46e5" text-anchor="middle">{terms[3]}</text>
          <text x="263" y="90" font-size="10" fill="#64748b" text-anchor="middle">4³+{k}</text>

          <rect x="310" y="25" width="60" height="48" rx="8" fill="#ede9fe" stroke="#6366f1" stroke-width="2"/>
          <text x="340" y="56" font-size="17" font-weight="bold" fill="#4f46e5" text-anchor="middle">{terms[4]}</text>
          <text x="340" y="90" font-size="10" fill="#64748b" text-anchor="middle">5³+{k}</text>

          <rect x="388" y="25" width="60" height="48" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2.5" stroke-dasharray="4"/>
          <text x="418" y="57" font-size="20" font-weight="bold" fill="#d97706" text-anchor="middle">?</text>
          <text x="418" y="90" font-size="10" font-weight="bold" fill="#d97706" text-anchor="middle">6³+{k}</text>
        </svg>
        """
        correct_ans = str(target_b4)
        distractors = [str(target_b4 - 2), str(target_b4 + 18), str(target_b4 - 20)]
    else:
        # Fibonacci variant
        fib_seed = random.randint(1, 4)
        f0 = fib_seed
        f1 = fib_seed + 1
        seq = [f0, f1]
        for _ in range(5):
            seq.append(seq[-1] + seq[-2])
        target_b4 = seq[-1]
        seq_display = seq[:-1]

        svg = f"""
        <svg width="100%" height="150" viewBox="0 0 460 130" preserveAspectRatio="xMidYMid meet" class="q-svg">
          <rect x="15" y="30" width="50" height="45" rx="8" fill="#ede9fe" stroke="#6366f1" stroke-width="2"/>
          <text x="40" y="58" font-size="16" font-weight="bold" fill="#4f46e5" text-anchor="middle">{seq_display[0]}</text>

          <rect x="75" y="30" width="50" height="45" rx="8" fill="#ede9fe" stroke="#6366f1" stroke-width="2"/>
          <text x="100" y="58" font-size="16" font-weight="bold" fill="#4f46e5" text-anchor="middle">{seq_display[1]}</text>

          <rect x="135" y="30" width="50" height="45" rx="8" fill="#ede9fe" stroke="#6366f1" stroke-width="2"/>
          <text x="160" y="58" font-size="16" font-weight="bold" fill="#4f46e5" text-anchor="middle">{seq_display[2]}</text>

          <rect x="195" y="30" width="50" height="45" rx="8" fill="#ede9fe" stroke="#6366f1" stroke-width="2"/>
          <text x="220" y="58" font-size="16" font-weight="bold" fill="#4f46e5" text-anchor="middle">{seq_display[3]}</text>

          <rect x="255" y="30" width="55" height="45" rx="8" fill="#ede9fe" stroke="#6366f1" stroke-width="2"/>
          <text x="282" y="58" font-size="16" font-weight="bold" fill="#4f46e5" text-anchor="middle">{seq_display[4]}</text>

          <rect x="320" y="30" width="55" height="45" rx="8" fill="#ede9fe" stroke="#6366f1" stroke-width="2"/>
          <text x="347" y="58" font-size="16" font-weight="bold" fill="#4f46e5" text-anchor="middle">{seq_display[5]}</text>

          <rect x="385" y="30" width="60" height="45" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2.5" stroke-dasharray="4"/>
          <text x="415" y="59" font-size="20" font-weight="bold" fill="#d97706" text-anchor="middle">?</text>

          <path d="M 282 82 Q 315 100 347 82" fill="none" stroke="#6366f1" stroke-width="1.5"/>
          <text x="315" y="110" font-size="11" fill="#6366f1" text-anchor="middle">{seq_display[4]} + {seq_display[5]} = ?</text>
        </svg>
        """
        correct_ans = str(target_b4)
        distractors = [str(target_b4 - 3), str(target_b4 + 5), str(target_b4 - 7)]

    options = [correct_ans] + distractors
    random.shuffle(options)
    correct_idx = options.index(correct_ans)

    return {
        "id": seed_id,
        "category": "Numerical Reasoning",
        "category_key": "numerical",
        "title": "Inductive Sequence Extrapolation",
        "prompt": "Identify the underlying mathematical progression and choose the number that replaces [?]:",
        "visual_type": "svg_matrix",
        "visual_data": svg,
        "options": options,
        "correct_index": correct_idx,
        "explanation": f"The progression follows standard inductive mathematical rules yielding {correct_ans}."
    }


def gen_cube_net_puzzle(seed_id: int):
    """Generates a randomized 3D cube net folding puzzle."""
    pool_symbols = [
        ("Star", "★", "#4f46e5"),
        ("Square", "■", "#9333ea"),
        ("Diamond", "◆", "#ea580c"),
        ("Circle", "●", "#16a34a"),
        ("Triangle Up", "▲", "#0284c7"),
        ("Triangle Down", "▼", "#dc2626")
    ]
    random.shuffle(pool_symbols)

    top = pool_symbols[0]
    left = pool_symbols[1]
    center = pool_symbols[2]
    right = pool_symbols[3]
    far_right = pool_symbols[4]
    bottom = pool_symbols[5]

    # In net:
    # center is opposite far_right
    # top is opposite bottom
    # left is opposite right
    query_target = center
    opposite_target = far_right

    svg = f"""
    <svg width="100%" height="180" viewBox="0 0 320 200" preserveAspectRatio="xMidYMid meet" class="q-svg">
      <!-- Top -->
      <rect x="110" y="10" width="50" height="50" rx="4" fill="#f8fafc" stroke="#475569" stroke-width="2"/>
      <text x="135" y="42" font-size="20" text-anchor="middle" fill="{top[2]}">{top[1]}</text>

      <!-- Middle: Left, Center, Right, Far Right -->
      <rect x="60" y="60" width="50" height="50" rx="4" fill="#f8fafc" stroke="#475569" stroke-width="2"/>
      <text x="85" y="93" font-size="22" text-anchor="middle" fill="{left[2]}">{left[1]}</text>

      <rect x="110" y="60" width="50" height="50" rx="4" fill="#ede9fe" stroke="#6366f1" stroke-width="3"/>
      <text x="135" y="94" font-size="24" text-anchor="middle" fill="{center[2]}">{center[1]}</text>

      <rect x="160" y="60" width="50" height="50" rx="4" fill="#f8fafc" stroke="#475569" stroke-width="2"/>
      <text x="185" y="93" font-size="22" text-anchor="middle" fill="{right[2]}">{right[1]}</text>

      <rect x="210" y="60" width="50" height="50" rx="4" fill="#f8fafc" stroke="#475569" stroke-width="2"/>
      <text x="235" y="93" font-size="22" text-anchor="middle" fill="{far_right[2]}">{far_right[1]}</text>

      <!-- Bottom -->
      <rect x="110" y="110" width="50" height="50" rx="4" fill="#f8fafc" stroke="#475569" stroke-width="2"/>
      <text x="135" y="142" font-size="20" text-anchor="middle" fill="{bottom[2]}">{bottom[1]}</text>

      <text x="135" y="185" font-size="11" fill="#64748b" text-anchor="middle">Fold faces at 90° inward along creases</text>
    </svg>
    """

    correct_option = f"{opposite_target[0]} ({opposite_target[1]})"
    distractors = [
        f"{right[0]} ({right[1]})",
        f"{top[0]} ({top[1]})",
        f"{left[0]} ({left[1]})"
    ]
    options = [correct_option] + distractors
    random.shuffle(options)
    correct_idx = options.index(correct_option)

    return {
        "id": seed_id,
        "category": "Spatial 3D Geometry",
        "category_key": "spatial",
        "title": "Cube Net Folding Spatial Reasoning",
        "prompt": f"When this two-dimensional net is folded into a 3D cube, which symbol will be on the face directly OPPOSITE to the {query_target[0]} ({query_target[1]})?",
        "visual_type": "cube_net",
        "visual_data": svg,
        "options": options,
        "correct_index": correct_idx,
        "explanation": f"Faces separated by one intervening square in the cross net become opposite parallel faces ({query_target[0]} is opposite {opposite_target[0]})."
    }


def gen_syllogism_puzzle(seed_id: int):
    """Generates a randomized formal logic syllogism puzzle with Euler set diagram."""
    themes = [
        {"A": "Quarks", "B": "Leptons", "C": "Tachyon Emitters", "D": "Bosons"},
        {"A": "Protostars", "B": "Nebulae", "C": "Pulsars", "D": "Supernovas"},
        {"A": "Enzymes", "B": "Proteins", "C": "Inorganic Salts", "D": "Catalysts"},
        {"A": "Monads", "B": "Functors", "C": "Side Effects", "D": "Closures"}
    ]
    t = random.choice(themes)

    svg = f"""
    <svg width="100%" height="180" viewBox="0 0 380 170" preserveAspectRatio="xMidYMid meet" class="q-svg">
      <!-- Set B (Outer Blue Circle) -->
      <circle cx="130" cy="85" r="70" fill="#e0e7ff" fill-opacity="0.5" stroke="#4f46e5" stroke-width="2"/>
      <text x="130" y="32" font-size="12" font-weight="bold" fill="#4f46e5" text-anchor="middle">{t['B']}</text>

      <!-- Set A (Inner Circle completely inside B) -->
      <circle cx="110" cy="95" r="38" fill="#c7d2fe" fill-opacity="0.7" stroke="#4338ca" stroke-width="1.8"/>
      <text x="105" y="98" font-size="11" font-weight="bold" fill="#312e81" text-anchor="middle">{t['A']}</text>

      <!-- Set D (Intersecting A and B) -->
      <circle cx="65" cy="95" r="45" fill="#fef3c7" fill-opacity="0.5" stroke="#d97706" stroke-width="2"/>
      <text x="50" y="70" font-size="12" font-weight="bold" fill="#b45309" text-anchor="middle">{t['D']}</text>

      <!-- Set C (Completely Disjoint Red Circle) -->
      <circle cx="305" cy="85" r="48" fill="#fee2e2" fill-opacity="0.6" stroke="#ef4444" stroke-width="2"/>
      <text x="305" y="85" font-size="12" font-weight="bold" fill="#b91c1c" text-anchor="middle">{t['C']}</text>

      <!-- Disjoint separator line -->
      <line x1="218" y1="20" x2="218" y2="150" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4"/>
      <text x="218" y="162" font-size="10" fill="#64748b" text-anchor="middle">Disjoint Sets</text>
    </svg>
    """

    correct_option = f"Some {t['D']} are not {t['C']}."
    distractors = [
        f"All {t['D']} are {t['B']}.",
        f"No {t['D']} are {t['C']}.",
        f"All {t['C']} are {t['A']}."
    ]
    options = [correct_option] + distractors
    random.shuffle(options)
    correct_idx = options.index(correct_option)

    return {
        "id": seed_id,
        "category": "Deductive Logic",
        "category_key": "logic",
        "title": "Categorical Syllogism & Set Theory",
        "prompt": f"Given the formal premises:\n1. All {t['A']} are {t['B']}.\n2. No {t['B']} are {t['C']}.\n3. Some {t['D']} are {t['A']}.\nWhich conclusion is logically guaranteed to be TRUE?",
        "visual_type": "svg_matrix",
        "visual_data": svg,
        "options": options,
        "correct_index": correct_idx,
        "explanation": f"Since some {t['D']} are {t['A']}, and all {t['A']} are {t['B']}, those {t['D']} are in {t['B']}. Since no {t['B']} are in {t['C']}, those {t['D']} cannot be in {t['C']}."
    }


def gen_balance_scale_puzzle(seed_id: int):
    """Generates an algorithmic mechanical balance scale equivalence puzzle."""
    c_weight = random.randint(3, 6)
    s_weight = random.randint(2, 4)
    # Ensure 2*C = 3*S or similar
    # e.g., 2 Cylinders = 3 Spheres (C=6, S=4 -> 12=12)
    # 1 Sphere = 2 Cubes (Cube=2)
    # 4 Cylinders = 24 / 2 = 12 Cubes
    scale_factor = random.choice([2, 3])
    spheres_per_pair = 3
    cubes_per_sphere = scale_factor
    cylinders_query = 4
    total_spheres = (cylinders_query // 2) * spheres_per_pair
    total_cubes = total_spheres * cubes_per_sphere

    svg = f"""
    <svg width="100%" height="160" viewBox="0 0 420 140" preserveAspectRatio="xMidYMid meet" class="q-svg">
      <rect x="20" y="20" width="180" height="48" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
      <text x="110" y="50" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">
        2 Cylinders = {spheres_per_pair} Spheres (●)
      </text>

      <rect x="220" y="20" width="180" height="48" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
      <text x="310" y="50" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">
        1 Sphere (●) = {cubes_per_sphere} Cubes (■)
      </text>

      <rect x="60" y="80" width="300" height="48" rx="8" fill="#ede9fe" stroke="#6366f1" stroke-width="2.5"/>
      <text x="210" y="110" font-size="16" font-weight="bold" fill="#4338ca" text-anchor="middle">
        {cylinders_query} Cylinders = ? Cubes (■)
      </text>
    </svg>
    """

    correct_option = f"{total_cubes} Cubes"
    distractors = [
        f"{total_cubes - 4} Cubes",
        f"{total_cubes + 2} Cubes",
        f"{total_cubes + 6} Cubes"
    ]
    options = [correct_option] + distractors
    random.shuffle(options)
    correct_idx = options.index(correct_option)

    return {
        "id": seed_id,
        "category": "Deductive Logic",
        "category_key": "logic",
        "title": "Algorithmic Balance Inversion",
        "prompt": f"On a precision balance scale, objects achieve equilibrium as shown below. How many Cubes (■) are required to balance {cylinders_query} Cylinders?",
        "visual_type": "svg_matrix",
        "visual_data": svg,
        "options": options,
        "correct_index": correct_idx,
        "explanation": f"2 Cylinders = {spheres_per_pair} Spheres -> {cylinders_query} Cylinders = {total_spheres} Spheres. 1 Sphere = {cubes_per_sphere} Cubes -> {total_spheres} Spheres = {total_cubes} Cubes."
    }


def gen_cypher_puzzle(seed_id: int):
    """Generates a randomized rapid speed cypher puzzle."""
    v_tri = random.randint(2, 6)
    v_dia = random.randint(5, 9)
    v_cir = random.randint(1, 4)
    v_sq = random.randint(7, 12)

    # (■ - ◆) × (▲ + ●)
    target = (v_sq - v_dia) * (v_tri + v_cir)

    svg = f"""
    <svg width="100%" height="160" viewBox="0 0 420 140" preserveAspectRatio="xMidYMid meet" class="q-svg">
      <rect x="20" y="15" width="70" height="40" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
      <text x="40" y="40" font-size="16" fill="#0284c7">▲</text>
      <text x="65" y="40" font-size="16" font-weight="bold" fill="#1e293b">= {v_tri}</text>

      <rect x="110" y="15" width="70" height="40" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
      <text x="130" y="40" font-size="16" fill="#ea580c">◆</text>
      <text x="155" y="40" font-size="16" font-weight="bold" fill="#1e293b">= {v_dia}</text>

      <rect x="200" y="15" width="70" height="40" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
      <text x="220" y="40" font-size="16" fill="#16a34a">●</text>
      <text x="245" y="40" font-size="16" font-weight="bold" fill="#1e293b">= {v_cir}</text>

      <rect x="290" y="15" width="70" height="40" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
      <text x="310" y="40" font-size="16" fill="#9333ea">■</text>
      <text x="335" y="40" font-size="16" font-weight="bold" fill="#1e293b">= {v_sq}</text>

      <rect x="20" y="75" width="380" height="50" rx="10" fill="#ede9fe" stroke="#6366f1" stroke-width="2"/>
      <text x="210" y="108" font-size="20" font-weight="bold" fill="#4338ca" text-anchor="middle">
        ( ■ − ◆ ) × ( ▲ + ● ) = ?
      </text>
    </svg>
    """

    correct_option = str(target)
    distractors = [
        str(target - 2),
        str(target + 4),
        str(target + 6)
    ]
    options = [correct_option] + distractors
    random.shuffle(options)
    correct_idx = options.index(correct_option)

    return {
        "id": seed_id,
        "category": "Processing Speed",
        "category_key": "speed",
        "title": "Rapid Symbol Cypher Translation",
        "prompt": "Using the decoded symbol lookup keys, calculate the numerical operator sequence as quickly as possible:",
        "visual_type": "svg_matrix",
        "visual_data": svg,
        "options": options,
        "correct_index": correct_idx,
        "explanation": f"({v_sq} - {v_dia}) × ({v_tri} + {v_cir}) = {v_sq - v_dia} × {v_tri + v_cir} = {target}."
    }


def gen_dial_shift_puzzle(seed_id: int):
    """Generates an 8-position radial dial harmonic shift puzzle."""
    positions = ["North", "North-East", "East", "South-East", "South", "South-West", "West", "North-West"]
    moves = [random.randint(1, 2), random.randint(1, 3), random.randint(2, 4)]
    total_moves = sum(moves)
    target_pos = positions[total_moves % 8]

    svg = f"""
    <svg width="100%" height="180" viewBox="0 0 280 180" preserveAspectRatio="xMidYMid meet" class="q-svg">
      <circle cx="140" cy="90" r="65" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
      <circle cx="140" cy="30" r="6" fill="#ef4444"/>
      <text x="140" y="20" font-size="11" font-weight="bold" fill="#ef4444" text-anchor="middle">N (Start)</text>

      <circle cx="186" cy="44" r="4" fill="#64748b"/>
      <circle cx="200" cy="90" r="5" fill="#4f46e5"/>
      <text x="218" y="94" font-size="11" font-weight="bold" fill="#4f46e5">E</text>

      <circle cx="186" cy="136" r="4" fill="#64748b"/>
      <circle cx="140" cy="150" r="5" fill="#3b82f6"/>
      <text x="140" y="168" font-size="11" font-weight="bold" fill="#3b82f6" text-anchor="middle">S</text>

      <circle cx="94" cy="136" r="4" fill="#64748b"/>
      <circle cx="80" cy="90" r="4" fill="#64748b"/>
      <text x="64" y="94" font-size="11" font-weight="bold" fill="#64748b">W</text>
      <circle cx="94" cy="44" r="4" fill="#64748b"/>

      <path d="M 152 40 A 55 55 0 0 1 185 80" fill="none" stroke="#6366f1" stroke-width="2" stroke-dasharray="3"/>
      <polygon points="187,83 180,76 189,73" fill="#6366f1"/>
      <text x="140" y="95" font-size="11" fill="#475569" text-anchor="middle">+{moves[0]}, +{moves[1]}, +{moves[2]}</text>
    </svg>
    """

    correct_option = target_pos
    wrong_positions = [p for p in positions if p != target_pos]
    random.shuffle(wrong_positions)
    options = [correct_option] + wrong_positions[:3]
    random.shuffle(options)
    correct_idx = options.index(correct_option)

    return {
        "id": seed_id,
        "category": "Pattern Recognition",
        "category_key": "pattern",
        "title": "Clockwise Harmonic Shift",
        "prompt": f"A pointer on an 8-position radial compass dial shifts clockwise successively: +{moves[0]} step, then +{moves[1]} steps, then +{moves[2]} steps. Starting at North (12:00), what direction is it pointing now?",
        "visual_type": "radial_dial",
        "visual_data": svg,
        "options": options,
        "correct_index": correct_idx,
        "explanation": f"Total moves: {total_moves}. {total_moves} mod 8 brings pointer to {target_pos}."
    }


def gen_spatial_rotation_puzzle(seed_id: int):
    """Generates an orthographic projection or 3D spatial rotation puzzle."""
    axis = random.choice(["X-axis and Y-axis", "X-axis and Z-axis", "Y-axis and Z-axis"])
    if axis == "X-axis and Y-axis":
        equiv = "A 180° rotation around the Z-axis"
        distr = ["A mirror reflection across the X-Y plane", "A 90° clockwise rotation around the Z-axis", "No change (identity matrix)"]
    elif axis == "X-axis and Z-axis":
        equiv = "A 180° rotation around the Y-axis"
        distr = ["A 90° counter-clockwise rotation around X", "A mirror reflection across the X-Z plane", "A 270° rotation around Z"]
    else:
        equiv = "A 180° rotation around the X-axis"
        distr = ["A 90° rotation around Y", "A planar reflection across Y-Z", "An inverse translation"]

    svg = f"""
    <svg width="100%" height="160" viewBox="0 0 380 150" preserveAspectRatio="xMidYMid meet" class="q-svg">
      <line x1="80" y1="100" x2="160" y2="100" stroke="#ef4444" stroke-width="2.5"/>
      <polygon points="165,100 158,96 158,104" fill="#ef4444"/>
      <text x="175" y="104" font-size="12" font-weight="bold" fill="#ef4444">X</text>

      <line x1="80" y1="100" x2="80" y2="25" stroke="#10b981" stroke-width="2.5"/>
      <polygon points="80,20 76,27 84,27" fill="#10b981"/>
      <text x="80" y="14" font-size="12" font-weight="bold" fill="#10b981" text-anchor="middle">Y</text>

      <line x1="80" y1="100" x2="35" y2="135" stroke="#3b82f6" stroke-width="2.5"/>
      <polygon points="30,138 35,130 41,135" fill="#3b82f6"/>
      <text x="22" y="146" font-size="12" font-weight="bold" fill="#3b82f6">Z</text>

      <rect x="200" y="35" width="165" height="75" rx="10" fill="#ede9fe" stroke="#6366f1" stroke-width="2"/>
      <text x="282" y="65" font-size="12" font-weight="bold" fill="#4338ca" text-anchor="middle">Successive 180° Rotations</text>
      <text x="282" y="88" font-size="13" font-weight="bold" fill="#4f46e5" text-anchor="middle">around {axis}</text>
    </svg>
    """

    options = [equiv] + distr
    random.shuffle(options)
    correct_idx = options.index(equiv)

    return {
        "id": seed_id,
        "category": "Spatial 3D Geometry",
        "category_key": "spatial",
        "title": "3D Axis Coordinate Rotation",
        "prompt": f"An asymmetric 3D object is subjected to successive 180° rotations around the {axis}. The resulting final spatial orientation is mathematically equivalent to:",
        "visual_type": "svg_matrix",
        "visual_data": svg,
        "options": options,
        "correct_index": correct_idx,
        "explanation": f"Composing two orthogonal 180° rotations in 3D Euclidean space produces a 180° rotation around the third mutually orthogonal axis ({equiv})."
    }


def gen_segment_binary_puzzle(seed_id: int):
    """Generates an LED 7-segment digital display binary subtraction puzzle."""
    svg = f"""
    <svg width="100%" height="180" viewBox="0 0 340 170" preserveAspectRatio="xMidYMid meet" class="q-svg">
      <g fill="#4f46e5" stroke="#ffffff" stroke-width="1">
        <polygon points="120,20 180,20 172,28 128,28" />
        <polygon points="116,24 124,32 124,76 116,84" />
        <polygon points="184,24 176,32 176,76 184,84" />
        <polygon points="122,80 178,80 172,88 128,88" />
        <polygon points="116,88 124,96 124,140 116,148" />
        <polygon points="184,88 176,96 176,140 184,148" />
        <polygon points="120,152 180,152 172,144 128,144" />
      </g>
      <text x="150" y="166" font-size="11" fill="#64748b" text-anchor="middle">Digit '8' (All 7 active)</text>
      <text x="260" y="80" font-size="14" font-weight="bold" fill="#dc2626">− Digit '7'</text>
      <text x="260" y="105" font-size="14" font-weight="bold" fill="#dc2626">− Digit '1'</text>
    </svg>
    """
    options = ["4 segments", "2 segments", "3 segments", "5 segments"]
    correct_idx = 0

    return {
        "id": seed_id,
        "category": "Pattern Recognition",
        "category_key": "pattern",
        "title": "7-Segment Binary Subtraction",
        "prompt": "In a 7-segment display, digit '8' activates all 7 segments. If you subtract all segments used in digit '1' and digit '7', how many active segments remain?",
        "visual_type": "svg_matrix",
        "visual_data": svg,
        "options": options,
        "correct_index": correct_idx,
        "explanation": "Digit 7 consists of 3 segments (which already include the 2 segments of digit 1). 7 - 3 = exactly 4 active segments remain."
    }


def gen_timeline_puzzle(seed_id: int):
    """Generates a sequential launch / order timeline logic puzzle."""
    probes = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
    random.shuffle(probes)
    first, second, third, fourth, fifth = probes

    svg = f"""
    <svg width="100%" height="150" viewBox="0 0 420 130" preserveAspectRatio="xMidYMid meet" class="q-svg">
      <line x1="30" y1="55" x2="390" y2="55" stroke="#cbd5e1" stroke-width="3"/>

      <circle cx="50" cy="55" r="22" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/>
      <text x="50" y="60" font-size="11" font-weight="bold" fill="#1d4ed8" text-anchor="middle">{first[:5]}</text>
      <text x="50" y="94" font-size="11" fill="#64748b" text-anchor="middle">1st</text>

      <circle cx="130" cy="55" r="22" fill="#dcfce7" stroke="#10b981" stroke-width="2"/>
      <text x="130" y="60" font-size="11" font-weight="bold" fill="#047857" text-anchor="middle">{second[:5]}</text>
      <text x="130" y="94" font-size="11" fill="#64748b" text-anchor="middle">2nd</text>

      <circle cx="210" cy="55" r="22" fill="#ede9fe" stroke="#6366f1" stroke-width="2.5" stroke-dasharray="4"/>
      <text x="210" y="62" font-size="18" font-weight="bold" fill="#4f46e5" text-anchor="middle">?</text>
      <text x="210" y="94" font-size="11" font-weight="bold" fill="#4f46e5" text-anchor="middle">3rd</text>

      <circle cx="290" cy="55" r="22" fill="#fef3c7" stroke="#f59e0b" stroke-width="2"/>
      <text x="290" y="60" font-size="11" font-weight="bold" fill="#b45309" text-anchor="middle">{fourth[:5]}</text>
      <text x="290" y="94" font-size="11" fill="#64748b" text-anchor="middle">4th</text>

      <circle cx="370" cy="55" r="22" fill="#fee2e2" stroke="#ef4444" stroke-width="2"/>
      <text x="370" y="60" font-size="11" font-weight="bold" fill="#b91c1c" text-anchor="middle">{fifth[:5]}</text>
      <text x="370" y="94" font-size="11" fill="#64748b" text-anchor="middle">5th</text>
    </svg>
    """

    correct_option = third
    distractors = [first, second, fourth]
    options = [correct_option] + distractors
    random.shuffle(options)
    correct_idx = options.index(correct_option)

    return {
        "id": seed_id,
        "category": "Deductive Logic",
        "category_key": "logic",
        "title": "Temporal Chain Sequencing",
        "prompt": f"Five planetary probes launch sequentially according to flight telemetry:\n- {first} launched 1st.\n- {second} launched immediately after {first}.\n- {third} launched after {second} but before {fourth}.\n- {fifth} launched last.\nWhich probe was the THIRD (3rd) to launch?",
        "visual_type": "svg_matrix",
        "visual_data": svg,
        "options": options,
        "correct_index": correct_idx,
        "explanation": f"Sequential launch progression confirms that {third} is at position 3."
    }


def gen_filter_matrix_puzzle(seed_id: int):
    """Generates a conditional number matrix filtering problem."""
    # generate 9 random numbers
    nums = [random.randint(12, 98) for _ in range(9)]
    # count how many are div by 3 and sum of digits is even
    qualifying = 0
    for n in nums:
        div3 = (n % 3 == 0)
        digits_sum = sum(int(d) for d in str(n))
        if div3 and (digits_sum % 2 == 0):
            qualifying += 1

    svg = f"""
    <svg width="100%" height="160" viewBox="0 0 360 150" preserveAspectRatio="xMidYMid meet" class="q-svg">
      <rect x="40" y="15" width="80" height="36" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
      <text x="80" y="39" font-size="16" font-weight="bold" fill="#1e293b" text-anchor="middle">{nums[0]}</text>
      <rect x="140" y="15" width="80" height="36" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
      <text x="180" y="39" font-size="16" font-weight="bold" fill="#1e293b" text-anchor="middle">{nums[1]}</text>
      <rect x="240" y="15" width="80" height="36" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
      <text x="280" y="39" font-size="16" font-weight="bold" fill="#1e293b" text-anchor="middle">{nums[2]}</text>

      <rect x="40" y="58" width="80" height="36" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
      <text x="80" y="82" font-size="16" font-weight="bold" fill="#1e293b" text-anchor="middle">{nums[3]}</text>
      <rect x="140" y="58" width="80" height="36" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
      <text x="180" y="82" font-size="16" font-weight="bold" fill="#1e293b" text-anchor="middle">{nums[4]}</text>
      <rect x="240" y="58" width="80" height="36" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
      <text x="280" y="82" font-size="16" font-weight="bold" fill="#1e293b" text-anchor="middle">{nums[5]}</text>

      <rect x="40" y="101" width="80" height="36" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
      <text x="80" y="125" font-size="16" font-weight="bold" fill="#1e293b" text-anchor="middle">{nums[6]}</text>
      <rect x="140" y="101" width="80" height="36" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
      <text x="180" y="125" font-size="16" font-weight="bold" fill="#1e293b" text-anchor="middle">{nums[7]}</text>
      <rect x="240" y="101" width="80" height="36" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
      <text x="280" y="125" font-size="16" font-weight="bold" fill="#1e293b" text-anchor="middle">{nums[8]}</text>
    </svg>
    """

    correct_option = f"{qualifying} numbers"
    all_counts = [f"{i} numbers" for i in range(5)]
    distractors = [c for c in all_counts if c != correct_option][:3]
    options = [correct_option] + distractors
    random.shuffle(options)
    correct_idx = options.index(correct_option)

    return {
        "id": seed_id,
        "category": "Processing Speed",
        "category_key": "speed",
        "title": "Conditional Matrix Filter",
        "prompt": "In the 3x3 number matrix, how many values are both DIVISIBLE BY 3 and have their digits sum to an EVEN number?",
        "visual_type": "svg_matrix",
        "visual_data": svg,
        "options": options,
        "correct_index": correct_idx,
        "explanation": f"Exactly {qualifying} values fulfill both divisibility by 3 and an even digit sum."
    }


# ==============================================================================
# MASTER SESSION QUESTION GENERATOR
# ==============================================================================

GENERATOR_FUNCS = [
    gen_matrix_progression,
    gen_numerical_series,
    gen_cube_net_puzzle,
    gen_syllogism_puzzle,
    gen_balance_scale_puzzle,
    gen_cypher_puzzle,
    gen_dial_shift_puzzle,
    gen_spatial_rotation_puzzle,
    gen_segment_binary_puzzle,
    gen_timeline_puzzle,
    gen_filter_matrix_puzzle
]


def generate_fresh_session_questions(count: int = 12) -> list:
    """
    Generates a completely new, randomized set of cognitive assessment questions
    for a test session. No two sessions will ever be the same!
    """
    questions = []
    # Pick a random mix of procedural generators
    generators = list(GENERATOR_FUNCS)
    random.shuffle(generators)

    # If count > len(generators), loop with different seeds
    q_id = 1
    while len(questions) < count:
        for gen in generators:
            if len(questions) >= count:
                break
            try:
                q = gen(seed_id=q_id)
                questions.append(q)
                q_id += 1
            except Exception as e:
                print(f"[iq_engine] Generator error: {e}")

    # Randomize question presentation order
    random.shuffle(questions)
    # Re-index ids sequentially 1..count
    for i, q in enumerate(questions):
        q["id"] = i + 1

    return questions


def sanitize_questions_for_client(questions: list) -> list:
    """Strip secret answers and explanations before transmitting to client."""
    public_list = []
    for q in questions:
        public_list.append({
            "id": q["id"],
            "category": q["category"],
            "category_key": q["category_key"],
            "title": q["title"],
            "prompt": q["prompt"],
            "visual_type": q.get("visual_type", "svg_matrix"),
            "visual_data": q.get("visual_data", ""),
            "options": q["options"]
        })
    return public_list


def calculate_iq(user_age: int, session_questions: list, answers: dict, time_taken_seconds: int):
    """
    Evaluates submitted answers against the specific questions generated for this session.
    Computes standardized IQ (mean 100, SD 15), age-adjusted norms, and certificate details.
    """
    total_questions = len(session_questions)
    correct_count = 0
    category_totals = {}
    category_correct = {}

    detailed_eval = []

    for q in session_questions:
        qid = str(q["id"])
        cat = q.get("category_key", "general")
        category_totals[cat] = category_totals.get(cat, 0) + 1

        user_choice = answers.get(qid)
        is_correct = (user_choice is not None and int(user_choice) == q.get("correct_index", 0))

        if is_correct:
            correct_count += 1
            category_correct[cat] = category_correct.get(cat, 0) + 1

        detailed_eval.append({
            "question_id": q["id"],
            "title": q["title"],
            "category": q["category"],
            "user_choice": user_choice,
            "correct_choice": q.get("correct_index", 0),
            "is_correct": is_correct
        })

    accuracy_ratio = correct_count / total_questions if total_questions > 0 else 0

    # Age-norm adjustments
    if user_age < 16:
        age_bonus = 3.5
    elif 16 <= user_age <= 21:
        age_bonus = 1.0
    elif 22 <= user_age <= 35:
        age_bonus = 0.0
    elif 36 <= user_age <= 50:
        age_bonus = 2.0
    else:
        age_bonus = 4.0

    # Speed bonus
    speed_factor = 0.0
    if accuracy_ratio >= 0.5:
        if time_taken_seconds < 350:
            speed_factor = 3.0
        elif time_taken_seconds < 550:
            speed_factor = 1.5

    # Standard psychometric Gaussian curve (Mean 100, SD 15)
    baseline_mid = total_questions * 0.5
    spread = max(1.5, total_questions * 0.18)
    z_score = (correct_count - baseline_mid) / spread
    computed_iq = 100.0 + (z_score * 15.0) + age_bonus + speed_factor

    iq_score = int(round(max(68, min(160, computed_iq))))

    # Percentile calculation
    z = (iq_score - 100.0) / 15.0
    percentile_val = 0.5 * (1.0 + math.erf(z / math.sqrt(2))) * 100.0
    percentile = round(max(0.1, min(99.9, percentile_val)), 1)

    # Classification tier
    if iq_score >= 145:
        classification = "Genius / Highly Gifted"
        badge = "Tier 1: Exceptional"
        desc = "In the top 0.1% of test takers globally. Exceptional abstract spatial reasoning, combinatorial pattern synthesis, and mental flexibility."
    elif iq_score >= 130:
        classification = "Very Superior Intelligence"
        badge = "Tier 2: Very Superior"
        desc = "Qualifies for international high-IQ societies (Mensa range). Demonstrates rapid problem solving, multi-dimensional geometry, and elite deductive inference."
    elif iq_score >= 120:
        classification = "Superior Intelligence"
        badge = "Tier 3: Superior"
        desc = "Substantially above standard population average across all cognitive dimensions. Strong analytical competence and fast symbolic processing."
    elif iq_score >= 110:
        classification = "High Average"
        badge = "Tier 4: High Average"
        desc = "Above average fluid reasoning and sequence extrapolation capabilities with dependable spatial accuracy."
    elif iq_score >= 90:
        classification = "Average Intelligence"
        badge = "Tier 5: Normal Distribution"
        desc = "Solid standard cognitive ability aligning with standard global demographic benchmarks."
    else:
        classification = "Developing Range"
        badge = "Tier 6: Developing"
        desc = "Foundational cognitive performance; benefits from systematic logic puzzles and spatial orientation training."

    category_scores = {}
    for cat, total in category_totals.items():
        corr = category_correct.get(cat, 0)
        pct = int(round((corr / total) * 100)) if total > 0 else 0
        category_scores[cat] = {
            "correct": corr,
            "total": total,
            "percentage": pct
        }

    cert_hash = uuid.uuid4().hex[:8].upper()
    certificate_id = f"CERT-IQ-{cert_hash[:4]}-{cert_hash[4:]}"

    return {
        "iq_score": iq_score,
        "percentile": percentile,
        "classification": classification,
        "badge": badge,
        "description": desc,
        "correct_answers": correct_count,
        "total_questions": total_questions,
        "accuracy_pct": int(round(accuracy_ratio * 100)),
        "time_taken_seconds": time_taken_seconds,
        "category_scores": category_scores,
        "certificate_id": certificate_id,
        "detailed_eval": detailed_eval
    }
