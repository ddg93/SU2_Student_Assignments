import gmsh
import sys

# Parameters
R_jet = 0.005 
Y_max = 10.0 * R_jet  
X_max = 60.0 * R_jet
L_wall = 0.05 * X_max  

# Resolution
nx_wall = 25   
nx_far = 175
ny_gas = 20    
ny_air = 20

gmsh.initialize()
gmsh.model.add("JetMesh")

# set the points: domain bounds, inlet-outlet separation and wall
p1 = gmsh.model.geo.addPoint(0, 0, 0)
p2 = gmsh.model.geo.addPoint(L_wall, 0, 0)
p3 = gmsh.model.geo.addPoint(X_max, 0, 0)
p4 = gmsh.model.geo.addPoint(X_max, R_jet, 0)
p5 = gmsh.model.geo.addPoint(X_max, Y_max, 0)
p6 = gmsh.model.geo.addPoint(L_wall, Y_max, 0)
p7 = gmsh.model.geo.addPoint(0, Y_max, 0)
p8 = gmsh.model.geo.addPoint(0, R_jet, 0)
p9 = gmsh.model.geo.addPoint(L_wall, R_jet, 0)

# generate the lines
l_inlet_gas = gmsh.model.geo.addLine(p8, p1)
l_axis_1 = gmsh.model.geo.addLine(p1, p2)
l_axis_2 = gmsh.model.geo.addLine(p2, p3)
l_out_gas = gmsh.model.geo.addLine(p3, p4)
l_out_air = gmsh.model.geo.addLine(p4, p5)
l_top_2 = gmsh.model.geo.addLine(p5, p6)
l_top_1 = gmsh.model.geo.addLine(p6, p7)
l_inlet_air = gmsh.model.geo.addLine(p7, p8)
l_wall = gmsh.model.geo.addLine(p8, p9)        # no-slip BC wall to prevent discontinuity
l_mid_horiz = gmsh.model.geo.addLine(p9, p4)   # virtual continuation
l_mid_vert_dn = gmsh.model.geo.addLine(p2, p9) # internal split
l_mid_vert_up = gmsh.model.geo.addLine(p9, p6) # internal split

# Generate the surfaces
# fast gas inlet - lower left
cl1 = gmsh.model.geo.addCurveLoop([l_inlet_gas, l_axis_1, l_mid_vert_dn, -l_wall])
s1 = gmsh.model.geo.addPlaneSurface([cl1])

# slow gas inlet - upper left
cl2 = gmsh.model.geo.addCurveLoop([l_wall, l_mid_vert_up, l_top_1, l_inlet_air])
s2 = gmsh.model.geo.addPlaneSurface([cl2])

# downstream gas - lower right
cl3 = gmsh.model.geo.addCurveLoop([l_mid_vert_dn, l_mid_horiz, -l_out_gas, -l_axis_2])
s3 = gmsh.model.geo.addPlaneSurface([cl3])

# downstream gas - upper right
cl4 = gmsh.model.geo.addCurveLoop([l_mid_vert_up, -l_top_2, -l_out_air, -l_mid_horiz])
s4 = gmsh.model.geo.addPlaneSurface([cl4])

# set transfinite surfaces and mesh with quadrilaterals
for s in [s1, s2, s3, s4]:
    gmsh.model.geo.mesh.setTransfiniteSurface(s)
    gmsh.model.geo.mesh.setRecombine(2, s)

# transfinite curves and distribution of points along curves
gmsh.model.geo.mesh.setTransfiniteCurve(l_wall, nx_wall)
gmsh.model.geo.mesh.setTransfiniteCurve(l_axis_1, nx_wall)
gmsh.model.geo.mesh.setTransfiniteCurve(l_top_1, nx_wall)
gmsh.model.geo.mesh.setTransfiniteCurve(l_mid_horiz, nx_far)
gmsh.model.geo.mesh.setTransfiniteCurve(l_axis_2, nx_far)
gmsh.model.geo.mesh.setTransfiniteCurve(l_top_2, nx_far)
gmsh.model.geo.mesh.setTransfiniteCurve(l_inlet_gas, ny_gas)
gmsh.model.geo.mesh.setTransfiniteCurve(l_mid_vert_dn, ny_gas)
gmsh.model.geo.mesh.setTransfiniteCurve(l_out_gas, ny_gas)
gmsh.model.geo.mesh.setTransfiniteCurve(l_inlet_air, ny_air)
gmsh.model.geo.mesh.setTransfiniteCurve(l_mid_vert_up, ny_air)
gmsh.model.geo.mesh.setTransfiniteCurve(l_out_air, ny_air)
# synch - redundant (?)
gmsh.model.geo.synchronize()

# set physical Groups
gmsh.model.addPhysicalGroup(1, [l_axis_1, l_axis_2], name="axis")
gmsh.model.addPhysicalGroup(1, [l_out_gas, l_out_air], name="outlet")
gmsh.model.addPhysicalGroup(1, [l_top_1, l_top_2], name="farfield")
gmsh.model.addPhysicalGroup(1, [l_inlet_air], name="inlet_air") #inlet of the slow surrounding fluid
gmsh.model.addPhysicalGroup(1, [l_inlet_gas], name="inlet_gas") #inlet of the fast jet
gmsh.model.addPhysicalGroup(1, [l_wall], name="wall") #no-slip BC to prevent discontinuity
gmsh.model.addPhysicalGroup(2, [s1, s2, s3, s4], name="fluid") #merge into fluid

# generate the mesh
gmsh.model.mesh.generate(2)
gmsh.write("axisymmetric_steady_jet.su2")
gmsh.finalize()