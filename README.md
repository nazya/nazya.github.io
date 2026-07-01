# nazariitupitsa.github.io

Personal static website for Nazarii Tupitsa.

## Design Approach

The site is intentionally simple: plain HTML, CSS, and small vanilla JavaScript helpers. Most visual decisions live in CSS custom properties at the top of `styles/global.css`, so the theme can be changed without hunting through page markup.

Palette values live once as `--light-*` and `--dark-*` variables. Public theme variables such as `--Canvas`, `--CanvasText`, and `--LinkText` map to those palette values, so changing a color only requires editing the palette block.

Other key variables control:

- layout: `--wrap`, `--gutter`, `--space`
- UI shape: `--radius`, `--radius-sm`, `--border`
- profile layout: `--profile-card-width`, `--profile-text-width`, `--profile-gap`, `--profile-card-padding`

Light, dark, and manual theme overrides reuse the same variable names. Components then reference those variables instead of hard-coded colors, which keeps changes local and predictable.

## Structure

- `index.html` - homepage/profile
- `papers/index.html` - publications
- `contact/index.html` - contact QR codes
- `styles/global.css` - shared design system and layout styles
- `scripts/` - theme, layout, and back-to-top helpers
- `assets/` - icons, theme icons, and QR SVGs

## Contact QR

The contact QR is generated from `contact/contact.vcf`, and the LinkedIn QR points to the LinkedIn profile URL. Both QR SVGs are used as CSS masks, so they inherit site colors through `--Canvas` and `--CanvasText`.

Regenerate QR assets with:

```sh
python3 scripts/generate-qr.py
```

The generator writes `contact/contact-qr.svg` and `contact/linkedin-qr.svg`. It uses QR byte mode with level-L Reed-Solomon error correction, a 4-module quiet zone, and SVG path output. The QR SVGs contain only dark modules; page CSS supplies the background and foreground theme colors.
