// One-shot PWA icon generator
// Usage (from frontend/): npx --yes sharp@0.33.5 ./scripts/generate-pwa-icons.mjs
// Or: npm i -D sharp && node scripts/generate-pwa-icons.mjs
import sharp from "sharp";
import { readFile } from "node:fs/promises";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PUBLIC = resolve(__dirname, "..", "public");

const targets = [
  { src: "icon.svg",          out: "icon-192.png",         size: 192 },
  { src: "icon.svg",          out: "icon-512.png",         size: 512 },
  { src: "icon.svg",          out: "apple-touch-icon.png", size: 180 },
  { src: "icon-maskable.svg", out: "icon-maskable-512.png", size: 512 },
];

for (const t of targets) {
  const inPath = resolve(PUBLIC, t.src);
  const outPath = resolve(PUBLIC, t.out);
  const svg = await readFile(inPath);
  await sharp(svg, { density: 384 })
    .resize(t.size, t.size, { fit: "contain", background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .png({ compressionLevel: 9 })
    .toFile(outPath);
  console.log(`✓ ${t.out} (${t.size}×${t.size})`);
}
