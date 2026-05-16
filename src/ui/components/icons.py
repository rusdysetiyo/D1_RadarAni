import base64
import math


def _sakura_icon_svg(size=100) -> str:
    cx, cy = size // 2, size // 2

    petals = []
    for i in range(5):
        rd = i * 72
        petal = f'''
        <g transform="translate({cx},{cy}) rotate({rd})">
            <ellipse cx="0" cy="-22" rx="16" ry="26" fill="#E8708A" />
            <ellipse cx="0" cy="-18" rx="7" ry="18" fill="#F9C0D0" opacity="0.6" />
        </g>'''
        petals.append(petal)


    dots = ""
    for i in range(5):
        a = math.radians(i * 72 - 54)
        x = cx + 12 * math.cos(a)
        y = cy + 12 * math.sin(a)
        dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="#B43C5A" />'

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  {''.join(petals)}

  <circle cx="{cx}" cy="{cy}" r="14" fill="#FFF0F5" opacity="0.9" />
  {dots}
  <circle cx="{cx}" cy="{cy}" r="5" fill="#CC5070" />
</svg>'''

    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()