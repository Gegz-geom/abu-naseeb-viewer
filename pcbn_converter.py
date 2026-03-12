"""
pcbn_converter.py
-----------------
Converts a Metashape Potree 1.7 export (cloud.js + data/r/*.bin)
into a single .pcbn binary file for use in the 3D web viewer.

Usage:
    python3 pcbn_converter.py <path_to_pointcloud_dir> <output.pcbn>

Example:
    python3 pcbn_converter.py ./pointcloud output.pcbn

The pointcloud directory should contain:
    cloud.js          -- Potree metadata
    data/r/           -- Binary node files (*.bin)
"""

import sys
import os
import json
import struct
import zipfile

STRIDE = 17  # int32 x3 (12B) + uint8 x4 RGBA (4B) + uint8 classification (1B)


def get_child_box(plx, ply, plz, psize, idx):
    """Compute child node bounding box origin using Potree 1.7 bit ordering.
    Bit ordering: x=bit2, y=bit1, z=bit0 (verified against all node data).
    """
    h = psize / 2
    ox = h if (idx >> 2 & 1) else 0
    oy = h if (idx >> 1 & 1) else 0
    oz = h if (idx >> 0 & 1) else 0
    return plx + ox, ply + oy, plz + oz, h


def path_to_origin(fname, obb_lx, obb_ly, obb_lz, obb_size):
    """Walk octree path string to find node's world-space bounding box origin."""
    lx, ly, lz = obb_lx, obb_ly, obb_lz
    size = obb_size
    node_name = os.path.splitext(os.path.basename(fname))[0]
    for ch in node_name[1:]:  # skip leading 'r'
        lx, ly, lz, size = get_child_box(lx, ly, lz, size, int(ch))
    return lx, ly, lz


def convert(input_dir, output_path):
    # Load metadata
    meta_path = os.path.join(input_dir, 'cloud.js')
    with open(meta_path) as f:
        meta = json.load(f)

    obb = meta['boundingBox']
    obb_size = obb['ux'] - obb['lx']
    scale = meta['scale']
    bb = meta['tightBoundingBox']

    rx = bb['ux'] - bb['lx']
    ry = bb['uy'] - bb['ly']
    rz = bb['uz'] - bb['lz']

    # Collect all .bin files
    data_dir = os.path.join(input_dir, 'data', 'r')
    bin_files = []
    for root, _, files in os.walk(data_dir):
        for f in files:
            if f.endswith('.bin'):
                bin_files.append(os.path.join(root, f))
    bin_files.sort()
    print(f"Found {len(bin_files)} bin files")

    points = []
    for i, bin_path in enumerate(bin_files):
        oblx, obly, oblz = path_to_origin(bin_path, obb['lx'], obb['ly'], obb['lz'], obb_size)
        with open(bin_path, 'rb') as f:
            data = f.read()
        n = len(data) // STRIDE
        for j in range(n):
            o = j * STRIDE
            wx = struct.unpack_from('<i', data, o)[0] * scale + oblx
            wy = struct.unpack_from('<i', data, o + 4)[0] * scale + obly
            wz = struct.unpack_from('<i', data, o + 8)[0] * scale + oblz
            # Filter to tightBB
            if not (bb['lx'] - 0.5 <= wx <= bb['ux'] + 0.5 and
                    bb['ly'] - 0.5 <= wy <= bb['uy'] + 0.5 and
                    bb['lz'] - 0.5 <= wz <= bb['uz'] + 0.5):
                continue
            qx = max(0, min(65535, int((wx - bb['lx']) / rx * 65535)))
            qy = max(0, min(65535, int((wy - bb['ly']) / ry * 65535)))
            qz = max(0, min(65535, int((wz - bb['lz']) / rz * 65535)))
            r, g, b = data[o + 12], data[o + 13], data[o + 14]
            points.append((qx, qy, qz, r, g, b))

        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(bin_files)} files, {len(points):,} points so far")

    print(f"Total valid points: {len(points):,}")
    print(f"Writing {output_path}...")

    with open(output_path, 'wb') as f:
        f.write(b'PCBN')
        f.write(struct.pack('<I', len(points)))
        f.write(struct.pack('<6f',
            bb['lx'], bb['ux'], bb['ly'], bb['uy'], bb['lz'], bb['uz']))
        for qx, qy, qz, r, g, b in points:
            f.write(struct.pack('<HHH', qx, qy, qz))
            f.write(bytes([r, g, b]))

    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"Done. Output: {output_path} ({size_mb:.1f} MB)")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
