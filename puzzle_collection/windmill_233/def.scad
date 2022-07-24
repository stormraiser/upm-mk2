inf = 200;

cube_l = 57;
cube_corner_r = 1;
sticker_margin = 1.5;
sticker_r = 1.5;

h = cube_l;
r = cube_corner_r;

function f0(x) = h*x^4 + 2*h*x^3 + (20*r-10*h)*x^2 + (8*r-2*h)*x + (h-4*r);
function df0(x) = 4*h*x^3 + 6*h*x^2 + (40*r-20*h)*x + (8*r-2*h);

x0 = 5 ^ 0.5 - 2;
x1 = x0 - f0(x0) / df0(x0);
x2 = x1 - f0(x1) / df0(x1);
x3 = x2 - f0(x2) / df0(x2);
x = x3;

theta = atan(x);

a = h / 2 + r * tan(theta * 2);
b = h / 2 / tan(theta * 2) + r;
hmid_h = (h / 2 - r) * sin(theta * 2) * 2;
echo(a / h);
echo(b / h);

module body(d = 0) {
    h2 = h + d * 2;
    h1 = h / 2 + d * 2;
    cube([h2, h2, h1], center = true);
}

module hmid_layer(d = 0) {
    h_t = hmid_h + d * 2;
    rotate([0, 0, theta * 2])
        cube([inf, h_t, inf], center = true);
}

module hright_layer(d = 0) {
    h_t = hmid_h / 2 - d;
    rotate([0, 0, theta * 2])
        translate([-inf / 2, h_t, -inf / 2])
            cube([inf, inf, inf]);
}

module center_block() {
    minkowski() {
        intersection() {
            body(-r);
            hmid_layer(-r);
            rotate([0, 0, -90]) hmid_layer(-r);
        }
        sphere(r, $fn = 24);
    }
}

module edge_block() {
    minkowski() {
        intersection() {
            body(-r);
            hright_layer(-r);
            rotate([0, 0, -90]) hmid_layer(-r);
        }
        sphere(r, $fn = 24);
    }
}

module corner_block() {
    minkowski() {
        intersection() {
            body(-r);
            hright_layer(-r);
            rotate([0, 0, -90]) hright_layer(-r);
        }
        sphere(r, $fn = 24);
    }
}

module center_sticker() {
    linear_extrude(0.1) {
        minkowski() {
            projection(true) {
                intersection() {
                    body(-sticker_margin - sticker_r);
                    hmid_layer(-sticker_margin - sticker_r);
                    rotate([0, 0, -90]) hmid_layer(-sticker_margin - sticker_r);
                }
            }
            circle(sticker_r, $fn = 24);
        }
    }
}

module edge_sticker() {
    linear_extrude(0.1) {
        minkowski() {
            projection(true) {
                intersection() {
                    body(-sticker_margin - sticker_r);
                    hright_layer(-sticker_margin - sticker_r);
                    rotate([0, 0, -90]) hmid_layer(-sticker_margin - sticker_r);
                }
            }
            circle(sticker_r, $fn = 24);
        }
    }
}

module corner_sticker() {
    linear_extrude(0.1) {
        minkowski() {
            projection(true) {
                intersection() {
                    body(-sticker_margin - sticker_r);
                    hright_layer(-sticker_margin - sticker_r);
                    rotate([0, 0, -90]) hright_layer(-sticker_margin - sticker_r);
                }
            }
            circle(sticker_r, $fn = 24);
        }
    }
}

module side_sticker() {
    side_lmargin = r / tan(theta) - (h / 2 - (h - r) * tan(theta * 2)) / tan(theta * 2);
    side_rmargin = r / tan(45 - theta) - r * tan(2 * theta);
    w = h / 2 - side_lmargin - side_rmargin + r * 2 - (sticker_margin + sticker_r) * 2;
    t = side_lmargin - r + sticker_margin + sticker_r;
    translate([0, h / 2, 0]) 
    rotate([90, 0, 0]) linear_extrude(0.1) minkowski() {
        translate([-h / 2 + t, -h / 4 + sticker_margin + sticker_r])
            square([w, h / 2 - (sticker_margin + sticker_r) * 2]);
        circle(sticker_r, $fn = 24);
    }
}

rotate([-90, -90, 0]) {
    //color("Gray") center_block();
    //color("Gray") edge_block();
    //color("Gray") corner_block();
    //center_sticker();
    //edge_sticker();
    //corner_sticker();
    side_sticker();
}
