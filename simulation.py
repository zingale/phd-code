import PHD.riemann as riemann
import PHD.boundary as boundary
import PHD.simulation as simulation
import PHD.reconstruction as reconstruction
import PHD.test_problems.sedov as sedov

# parameters and initial state of the simulation
parameters, data, particles, particles_index = sedov.simulation()

# create boundary and riemann objects
boundary_condition = boundary.Reflect2D(0.,1.,0.,1.)
#reconstruction = reconstruction.PiecewiseConstant(boundary_condition)
reconstruction = reconstruction.PiecewiseLinear(boundary_condition)
riemann_solver = riemann.Exact(reconstruction)
#riemann_solver = riemann.Hllc(reconstruction)
#riemann_solver = riemann.Hll(reconstruction)

# setup the moving mesh simulation
simulation = simulation.MovingMesh()
#simulation = simulation.StaticMesh()

for key, value in parameters.iteritems():
    simulation.set_parameter(key, value)

# set the boundary, riemann solver, and initial state of the simulation 
simulation.set_boundary_condition(boundary_condition)
simulation.set_reconstruction(reconstruction)
simulation.set_riemann_solver(riemann_solver)
simulation.set_initial_state(particles, data, particles_index)

# run the simulation
simulation.solve()
