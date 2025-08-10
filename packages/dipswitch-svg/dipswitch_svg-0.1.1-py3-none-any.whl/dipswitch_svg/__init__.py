__version__ = "0.1.1"

from typing import Iterable
def dipswitch(name: str, numbers: Iterable, value: int, invert: bool = False) -> str:
    """Returns the svg as string

    numbers: the numbers to display from left to right for bit 0..n
    
    example:  
    ```
    dipswitch("SW1", [1,2,3], 0x1)
    ```
    Makes an svg where the first (left) dipswitch is numbered 1 and is ON

    """
    width = 56 + len(numbers) * 32
    text = []
    text.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width+4}" height="124">')
    # Box with name
    text.append(f'<rect x="2" y="2" width="{width}" height="120" fill="rgb(255,255,255)" stroke="rgb(0,0,0)"/>')
    text.append(f'<text x="{width/2 + 2}" y="25" fill="rgb(0, 0, 0)" font-family="Helvetica" font-size="24px" text-anchor="middle" font-weight="bold">{name}</text>')
    # Seperator line
    text.append(f'<path d="M 2 34 L {width+2} 34" fill="none" stroke="rgb(0, 0, 0)"/>')
    # ON / OFF text
    text.append(f'<text x="40" y="58" fill="rgb(0, 0, 0)" font-family="Helvetica" font-size="16px" text-anchor="end">ON</text>')
    text.append(f'<text x="40" y="90" fill="rgb(0, 0, 0)" font-family="Helvetica" font-size="16px" text-anchor="end">OFF</text>')
    # dipswitches
    for i, n in enumerate(numbers):
        x = 46 + i * 32
        y = 76
        if ((value >> i) & 0x1) ^ invert:
            y -= 24
        text.append(f'<rect x="{x}" y="50" width="24" height="40" fill="rgb(255, 255, 255)" stroke="rgb(0,0,0)"/>')
        text.append(f'<rect x="{x + 2}" y="{y}" width="20" height="12" fill="#000000" stroke="none" />')
        text.append(f'<text x="{x + 12}" y="114" fill="rgb(0, 0, 0)" font-family="Helvetica" font-size="24px" text-anchor="middle" font-weight="bold">{n}</text>')
    text.append("</svg>")
    return "".join(text)