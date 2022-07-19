module selector(nblocks, block_size, margin, left, right, back) {
    x0 = block_size * (nblocks / 2 - back);
    dx = block_size * back + margin;
    y0 = block_size * left;
    dy = block_size * (right - left);
    z0 = block_size * nblocks / 2;
    dz = margin;
    l = nblocks * block_size * 2;
    difference() {
        translate([x0, y0, z0]) cube([dx, dy, dz]);
        rotate([-90, 0, 45]) translate([-l / 2, -l / 2, 0]) cube([l, l, l / 2]);
        rotate([90, 0, -45]) translate([-l / 2, -l / 2, 0]) cube([l, l, l / 2]);
        rotate([0, 135, 0]) translate([-l / 2, -l / 2, 0]) cube([l, l, l / 2]);
    }
}
module center_selector(nblocks, block_size, margin, back) {
    dx = block_size * (nblocks - back * 2);
    z0 = nblocks * block_size / 2;
    translate([-dx / 2, -dx / 2, z0]) cube([dx, dx, margin]);
}

color("Red", 0.5) selector(3, 19, 0.5, 0.5, 2, 1);
color("Blue", 0.5) rotate([0, 0, 90]) selector(3, 19, 0.5, -2, -0.5, 1);
color("Blue", 0.5) selector(3, 19, 0.5, -0.5, 0.5, 1);
color("Green", 0.5) center_selector(3, 19, 0.5, 1);