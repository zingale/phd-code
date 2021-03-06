cimport numpy as np
from libcpp.list cimport list as cpplist

from ..domain.domain_manager cimport DomainManager
from ..containers.containers cimport CarrayContainer
from ..domain.domain_manager cimport FlagParticle, BoundaryParticle#, particle_flag_deref

cdef extern from "particle.h":
    FlagParticle* particle_flag_deref(cpplist[FlagParticle].iterator &it)

cdef enum:
    REFLECTIVE = 0x01
    PERIODIC   = 0x02

cdef inline bint intersect_bounds(double x[3], double r, np.float64_t bounds[2][3], int dim)

cdef class BoundaryConditionBase:
    cdef void create_ghost_particle(self, cpplist[FlagParticle] &flagged_particles,
                                    DomainManager domain_manager)
    cdef void create_ghost_particle_serial(self, cpplist[FlagParticle] &flagged_particles,
                                           DomainManager domain_manager)
    cdef void create_ghost_particle_parallel(self, cpplist[FlagParticle] &flagged_particles,
                                             DomainManager domain_manager)
    cdef void migrate_particles(self, CarrayContainer particles, DomainManager domain_manager)
    cdef void update_gradients(self, CarrayContainer particles, CarrayContainer gradients,
                               DomainManager domain_manager)
    cpdef update_fields(self, CarrayContainer particles, DomainManager domain_manager)

cdef class Reflective(BoundaryConditionBase):
    pass

cdef class Periodic(BoundaryConditionBase):
    pass
