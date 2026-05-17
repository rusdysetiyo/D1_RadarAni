import math
import base64

def _mini_sakura(cx, cy, size=22, opacity=0.18, rotate_deg=0) -> str:
    petals = []
    for i in range(5):
        rd = rotate_deg + i * 72
        grad_id = f"mg{cx}{cy}{i}".replace(".","")
        petals.append(f'''
        <defs>
            <radialGradient id="{grad_id}" cx="50%" cy="70%" r="60%">
                <stop offset="0%"   stop-color="#FFCCD8"/>
                <stop offset="100%" stop-color="#E890A8"/>
            </radialGradient>
        </defs>
        <g transform="translate({cx},{cy}) rotate({rd})">
            <ellipse cx="0" cy="-{int(size*0.44)}" rx="{int(size*0.28)}" ry="{int(size*0.40)}"
                     fill="url(#{grad_id})" opacity="{opacity}"/>
        </g>''')
    r_center = int(size * 0.15)
    return ''.join(petals) + f'<circle cx="{cx}" cy="{cy}" r="{r_center}" fill="#F0B0C0" opacity="{opacity*0.8}"/>'

def get_sakura_svg(size=160) -> str:
    """Fungsi ini dipanggil buat ngambil gambar Base64 si Sakura"""
    cx, cy = size // 2, size // 2

    bg_flowers = ""
    organic_positions = [
        (40, 40, 24, 0.2, 15), (120, 38, 20, 0.18, -25), (135, 85, 25, 0.22, 45),
        (125, 125, 22, 0.19, -10), (45, 130, 26, 0.21, 60), (25, 85, 20, 0.17, -40),
        (80, 25, 22, 0.18, 5), (85, 135, 18, 0.16, 80), (60, 55, 14, 0.15, -15),
        (105, 100, 16, 0.14, 30), (100, 55, 12, 0.12, 75), (55, 105, 15, 0.15, -60)
    ]

    for (bx, by, bsz, bop, brot) in organic_positions:
        bg_flowers += _mini_sakura(bx, by, size=bsz, opacity=bop, rotate_deg=brot)

    petals = []
    for i in range(5):
        rd = i * 72
        grad_id = f"pg{i}"
        petal = f'''
        <defs>
            <radialGradient id="{grad_id}" cx="50%" cy="70%" r="60%">
                <stop offset="0%"   stop-color="#F9C0D0"/>
                <stop offset="50%"  stop-color="#E8809A"/>
                <stop offset="100%" stop-color="#CC5070"/>
            </radialGradient>
        </defs>
        <g transform="translate({cx},{cy}) rotate({rd})">
            <ellipse cx="0" cy="-28" rx="18" ry="26"
                     fill="url(#{grad_id})" opacity="0.95"/>
            <line x1="0"  y1="-6"  x2="0"   y2="-50"
                  stroke="#B43C5A" stroke-opacity="0.25" stroke-width="1.2"/>
            <line x1="0"  y1="-18" x2="-12" y2="-38"
                  stroke="#B43C5A" stroke-opacity="0.15" stroke-width="0.8"/>
            <line x1="0"  y1="-18" x2="12"  y2="-38"
                  stroke="#B43C5A" stroke-opacity="0.15" stroke-width="0.8"/>
            <ellipse cx="-4" cy="-36" rx="5" ry="8"
                     fill="white" opacity="0.2"
                     transform="rotate(-15,-4,-36)"/>
        </g>'''
        petals.append(petal)

    stamens = ""
    for i in range(14):
        a = math.radians(i * (360 / 14))
        tip = 14 + (i % 4) * 2
        x1 = cx + 8 * math.cos(a)
        y1 = cy + 8 * math.sin(a)
        x2 = cx + tip * math.cos(a)
        y2 = cy + tip * math.sin(a)
        stamens += (
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"'
            f' stroke="#C0506A" stroke-width="0.9" opacity="0.8"/>'
            f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="1.6" fill="#A03050" opacity="0.85"/>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <defs>
    <radialGradient id="centerGrad" cx="40%" cy="35%" r="60%">
      <stop offset="0%"   stop-color="#FFE0EA"/>
      <stop offset="60%"  stop-color="#F5C0D0"/>
      <stop offset="100%" stop-color="#E090A8"/>
    </radialGradient>
  </defs>
  {bg_flowers}
  {''.join(petals)}
  <circle cx="{cx}" cy="{cy}" r="16" fill="url(#centerGrad)"/>
  <circle cx="{cx}" cy="{cy}" r="14" fill="#FFF0F5" opacity="0.6"/>
  {stamens}
</svg>'''

    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()