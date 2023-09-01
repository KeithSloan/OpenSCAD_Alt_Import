// Here's what code I do have, which was more or less a translation of some other code I had found in another programming language. I no longer remember where to find the original code. Some of the variable names were best guesses on my part.

include <BOSL2/std.scad>

function bspline(path, closed=false, splinesteps=8) =
    assert(is_path(path) && len(path)>3)
    assert(is_finite(splinesteps))
    assert(floor(ln(splinesteps)/ln(2)) == (ln(splinesteps)/ln(2)), "splinesteps must be an integer power of 2.")
    let(
        lev = max(0, ceil(ln(splinesteps) / ln(2)) ),
        path = closed? path :
            concat([path[0]], path, [last(path)])
    )
    _bspline_recurse(path, closed=closed, lev=lev);


function _bspline_recurse(path, closed=false, lev) =
    lev == 0 ? path :
    let(
        endknots = [
            [1.0, 0.0,  0.0,  0.0],
            [0.5, 0.5,  0.0,  0.0],
            [0.0, 0.75, 0.25, 0.0],
            [0.0, 0.1875, 0.6875, 0.125],
        ],
        midknots = [
            [0.5,   0.5,  0.0  ],
            [0.125, 0.75, 0.125],
        ],
        plen = len(path)
    )
    closed
      ? _bspline_recurse([for(i=idx(path), j=[0,1]) midknots[j] * select(path,i,i+2)], closed, lev=lev-1)
      : _bspline_recurse(
            [
                for(i=[0:1:min(3,plen-3)])   endknots[i] * select(path,0,3),
                for(i=[3:1:plen-4], j=[0,1]) midknots[j] * select(path,i-1,i+1),
                midknots[0] * select(path,-4,-2),
                for(i=[min(3,plen-2):-1:0])  endknots[i] * select(path,[-1:-1:-4]),
            ],
            closed,
            lev=lev-1
        );

function bspline_patch(patch, splinesteps=8, col_wrap=false, row_wrap=false) =
    let(
        bswall1 = [for (i = idx(patch[0])) bspline([for (row=patch) row[i]], closed=col_wrap, splinesteps=splinesteps)],
        bswall2 = [for (i = idx(bswall1[0])) bspline([for (row=bswall1) row[i]], closed=row_wrap, splinesteps=splinesteps)]
    )
    vnf_vertex_array(bswall2, col_wrap=col_wrap, row_wrap=row_wrap);


//p = star(r=50,n=5,step=2); closed=true;
//color("#f00") stroke(p, closed=closed, width=0.5, joints="dot");
//color("#00f") stroke(bspline(p, closed=closed), width=0.5, joints="dot");


rsteps = 96;
csteps = 48;
ssteps = 4;

patch = [
    for (u = [0:1/rsteps:1]) [
        for (v=[0:1/csteps:1])
        zrot(u*360, p=[50,0,0] + (20+sin(v*360*6)*sin(u*360*12)*4)*[cos(360*v),0,sin(360*v)])
    ]
];

//color("blue") move_copies(flatten(patch)) cube(1,center=true);
vnf = vnf_vertex_array(patch, style="quincunx", col_wrap=true, row_wrap=true);
vnfb = bspline_patch(patch, splinesteps=ssteps, col_wrap=true, row_wrap=true);
//vnf_polyhedron(vnf);
vnf_polyhedron(vnfb);
