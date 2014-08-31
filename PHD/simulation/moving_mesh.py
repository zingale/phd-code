import h5py
import numpy as np
import simulation as sim
from static_mesh import StaticMesh
from PHD.fields import Fields
from PHD.mesh import VoronoiMesh
from PHD.riemann.riemann_base import RiemannBase
from PHD.boundary.boundary_base import BoundaryBase
from PHD.reconstruction.reconstruct_base import ReconstructBase


class MovingMesh(StaticMesh):
    """
    moving mesh simulation class
    """

    def __init__(self, gamma = 1.4, CFL = 0.5, max_steps=100, max_time=None, output_cycle = 100000,
            output_name="simulation_", regularization=True):

        super(MovingMesh, self).__init__(gamma, CFL, max_steps, max_time, output_cycle, output_name)

        # simulation parameters
        self.regularization = regularization


    def solve_one_step(self):
        """
        Evolve the simulation for one time step.
        """

        # generate ghost particles with links to original real particles 
        self.particles = self.fields.update_boundaries(self.particles, self.particles_index, self.neighbor_graph, self.neighbor_graph_sizes)

        # construct the new mesh 
        self.neighbor_graph, self.neighbor_graph_sizes, self.face_graph, self.face_graph_sizes, self.voronoi_vertices = self.mesh.tessellate(self.particles)

        # calculate volume and center of mass of real particles
        self.cell_info = self.mesh.volume_center_mass(self.particles, self.neighbor_graph, self.neighbor_graph_sizes, self.face_graph,
                self.voronoi_vertices, self.particles_index)

        # calculate primitive variables of real particles and pass to ghost particles with give boundary conditions
        self.fields.update_primitive(self.cell_info["volume"], self.particles, self.particles_index)

        # calculate global time step
        self.get_dt()

        # assign fluid velocities to particles, regularize if needed, and pass to ghost particles
        w = self.mesh.assign_particle_velocities(self.particles, self.fields.prim, self.particles_index, self.cell_info, self.gamma, self.regularization)

        # grab left and right states for each face
        faces_info = self.mesh.faces_for_flux(self.particles, self.fields.prim, w, self.particles_index, self.neighbor_graph,
                self.neighbor_graph_sizes, self.face_graph, self.voronoi_vertices)

        # calculate gradient for real particles and pass to ghost particles
        self.reconstruction.gradient(self.fields.prim, self.particles, self.particles_index, self.cell_info, self.neighbor_graph, self.neighbor_graph_sizes,
                self.face_graph, self.voronoi_vertices)

        # extrapolate state to face, apply frame transformations, solve riemann solver, and transform back
        fluxes = self.riemann_solver.fluxes(faces_info, self.gamma, self.dt, self.cell_info, self.particles_index)

        # update conserved variables
        self.update(self.fields, fluxes, faces_info)

        # update particle positions
        self.move_particles(w)


    def move_particles(self, w):
        """
        advance real particles positions for one time step
        """

        self.particles[:,self.particles_index["real"]] += self.dt*w[:, self.particles_index["real"]]
