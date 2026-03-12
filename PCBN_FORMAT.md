# .pcbn Binary Format Specification

The `.pcbn` format is a compact single-file point cloud format designed for
efficient delivery in web browsers. It was created as a replacement for
streaming 360 individual Potree `.bin` files.

## Motivation

Potree 1.7 exports produce hundreds of small `.bin` files (one per octree node).
Fetching these individually in a browser creates a large number of HTTP requests
and significant latency. This format pre-decodes all points and stores them in
a single binary file.

## Format

All values are little-endian.

### Header (32 bytes)

| Offset | Size | Type       | Description                     |
|--------|------|------------|---------------------------------|
| 0      | 4    | `char[4]`  | Magic number: `PCBN`            |
| 4      | 4    | `uint32`   | Total number of points          |
| 8      | 4    | `float32`  | Tight bounding box: `lx` (min X)|
| 12     | 4    | `float32`  | Tight bounding box: `ux` (max X)|
| 16     | 4    | `float32`  | Tight bounding box: `ly` (min Y)|
| 20     | 4    | `float32`  | Tight bounding box: `uy` (max Y)|
| 24     | 4    | `float32`  | Tight bounding box: `lz` (min Z)|
| 28     | 4    | `float32`  | Tight bounding box: `uz` (max Z)|

### Point Data (9 bytes × N points)

| Offset | Size | Type     | Description                              |
|--------|------|----------|------------------------------------------|
| 0      | 2    | `uint16` | X position, quantized (0–65535)          |
| 2      | 2    | `uint16` | Y position, quantized (0–65535)          |
| 4      | 2    | `uint16` | Z position, quantized (0–65535)          |
| 6      | 1    | `uint8`  | Red channel (0–255)                      |
| 7      | 1    | `uint8`  | Green channel (0–255)                    |
| 8      | 1    | `uint8`  | Blue channel (0–255)                     |

### Dequantization

To recover world-space coordinates from quantized values:

```
worldX = (qX / 65535) * (ux - lx) + lx
worldY = (qY / 65535) * (uy - ly) + ly
worldZ = (qZ / 65535) * (uz - lz) + lz
```

Spatial resolution at this quantization level is approximately **1.7mm**
for a 111m scene extent — more than sufficient for architectural documentation.

## Comparison

| Format           | Files | Size  | HTTP Requests | Browser Decode |
|------------------|-------|-------|---------------|----------------|
| Potree 1.7 raw   | 360   | 63 MB | 360           | Complex        |
| `.pcbn`          | 1     | 34 MB | 1             | Simple         |

## Coordinate System

Points are stored in the original Potree/Metashape coordinate system (Z-up).
The viewer converts to Three.js Y-up on decode:

```js
sceneX =  worldX - centreX
sceneY =  worldZ - centreZ   // Z becomes Y
sceneZ = -(worldY - centreY) // Y becomes -Z
```
