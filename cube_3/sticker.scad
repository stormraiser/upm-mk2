module sticker(size, corner_r) {
    linear_extrude(height = 0.1, center = true){
        minkowski() {
            square(size - corner_r * 2, center = true);
            circle(corner_r);
        }
    }
}
