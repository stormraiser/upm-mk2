module cubelet(size, corner_r) {
    minkowski() {
        cube(size - corner_r * 2, center = true);
        sphere(corner_r);
    }
}
