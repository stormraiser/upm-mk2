use <cubelet.scad>
use <sticker.scad>
use <cube_selector.scad>
$fn = 48;

cube_l = 19;
cube_corner_r = 1;
sticker_margin = 1.5;
sticker_r = 1.5;

module make_cubelet() {
    cubelet(cube_l, cube_corner_r);
}

module make_sticker() {
    sticker(cube_l - sticker_margin * 2, sticker_r);
}

module assembly_test() {
    color("DimGray") translate([cube_l, cube_l, cube_l]) make_cubelet();
    color("DimGray") translate([0, cube_l, cube_l]) make_cubelet();
    color("DimGray") translate([0, 0, cube_l]) make_cubelet();
    color("White") translate([cube_l, cube_l, cube_l * 3 / 2]) make_sticker();
    color("White") translate([0, cube_l, cube_l * 3 / 2]) make_sticker();
    color("White") translate([0, 0, cube_l * 3 / 2]) make_sticker();
    color("Red", 0.5) selector(3, cube_l, 0.2, 0.5, 2, 1);
    color("Blue", 0.5) rotate([0, 0, 90]) selector(3, cube_l, 0.2, -2, -0.5, 1);
    color("Blue", 0.5) rotate([0, 0, 90]) selector(3, cube_l, 0.2, 0, 0.5, 1);
    color("Red", 0.5) rotate([0, 0, 90]) selector(3, cube_l, 0.2, -0.5, 0, 1);
    color("Green", 0.5) center_selector(3, 19, 0.2, 1);
}

assembly_test();

rotate([-90, -90, 0]) {
//    make_cubelet();
//    make_sticker();
//    selector(3, cube_l, 0.2, 0.5, 2, 1);
//    rotate([0, 0, 90]) selector(3, cube_l, 0.2, -2, -0.5, 1);
//    rotate([0, 0, 90]) selector(3, cube_l, 0.2, 0, 0.5, 1);
//    rotate([0, 0, 90]) selector(3, cube_l, 0.2, -0.5, 0, 1);
//    center_selector(3, 19, 0.2, 1);
}