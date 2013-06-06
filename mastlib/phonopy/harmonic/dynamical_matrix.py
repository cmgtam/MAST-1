# Copyright (C) 2011 Atsushi Togo
# All rights reserved.
#
# This file is part of phonopy.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
# * Neither the name of the phonopy project nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import numpy as np
from phonopy.structure.cells import get_reduced_bases
DAMPING_FACTOR = 0.25

class DynamicalMatrix:
    """Dynamical matrix class
    
    When prmitive and supercell lattices are L_p and L_s, respectively,
    frame F is defined by
    L_p = dot(F, L_s), then L_s = dot(F^-1, L_p).
    where lattice matrix is defined by axies a,b,c in Cartesian:
        [ a1 a2 a3 ]
    L = [ b1 b2 b3 ]
        [ c1 c2 c3 ]
    
    Phase difference in primitive cell unit
    between atoms 1 and 2 in supercell is calculated by, e.g.,
    1j * dot((x_s(2) - x_s(1)), F^-1) * 2pi
    where x_s is reduced atomic coordinate in supercell unit.
    """

    def __init__(self,
                 supercell,
                 primitive,
                 force_constants,
                 symprec=1e-5):
        self._scell = supercell
        self._pcell = primitive
        self._p2s_map = primitive.get_primitive_to_supercell_map()
        self._s2p_map = primitive.get_supercell_to_primitive_map()
        self._p2p_map = primitive.get_primitive_to_primitive_map()
        self._force_constants = force_constants
        self._symprec = symprec
        self._smallest_vectors, self._multiplicity = \
            get_smallest_vectors(supercell, primitive, symprec)
        self._mass = self._pcell.get_masses()
        # Non analytical term correction
        self._nac = False

    def is_nac(self):
        return self._nac

    def get_dynamical_matrix(self):
        return self._dynamical_matrix

    def set_dynamical_matrix(self, q, verbose=False):
        try:
            import phonopy._phonopy as phonoc
            self._set_c_dynamical_matrix(q)
        except ImportError:
            self._set_py_dynamical_matrix(q, verbose=verbose)

    def _set_py_dynamical_matrix(self,
                                 q,
                                 verbose=False):
        pos = self._scell.get_scaled_positions()
        fc = self._force_constants
        vecs = self._smallest_vectors
        multiplicity = self._multiplicity
        num_atom = len(self._p2s_map)
        dm = np.zeros((3 * num_atom, 3 * num_atom), dtype=complex)

        for i, s_i in enumerate(self._p2s_map):
            for j, s_j in enumerate(self._p2s_map):
                mass = np.sqrt(self._mass[i] * self._mass[j])
                dm_local = np.zeros((3, 3), dtype=complex)
                # Sum in lattice points                
                for k in range(self._scell.get_number_of_atoms()): 
                    if s_j == self._s2p_map[k]:
                        multi = multiplicity[k][i]
                        phase = []
                        for l in range(multi):
                            vec = vecs[k][i][l]
                            phase.append(np.vdot(vec, q) * 2j * np.pi)
                        phase_factor = np.exp(phase).sum()
                        if verbose:
                            self._phase_log(s_i, k, l, vec, phase_factor * multi,
                                           np.linalg.norm(
                                    np.dot(vec, self._pcell.get_cell())))
                        dm_local += fc[s_i, k] * phase_factor / mass / multi

                dm[(i*3):(i*3+3), (j*3):(j*3+3)] += dm_local

        # Impose Hermisian condition
        self._dynamical_matrix = (dm + dm.conj().transpose()) / 2 

        if verbose:
            self._dynamical_matrix_log()

    def _phase_log(self, s_i, k, l, vec, exp_phase, distance):
        print "(%3d)-(%3d)  %1d" % (s_i+1, k+1, l+1)
        print "vector: ", "%10.5f"*3 % tuple(vec)
        print "phase:  ", "%10.5f"*2 % (exp_phase.real, exp_phase.imag)
        print "distance: ", distance

    def _dynamical_matrix_log(self):
        dm = self._dynamical_matrix
        for i in range(dm.shape[0]/3):
            for j in range(dm.shape[0]/3):
                dm_local = dm[(i*3):(i*3+3), (j*3):(j*3+3)]
                for vec in dm_local:
                    re = vec.real
                    im = vec.imag
                    print "dynamical matrix(%3d - %3d) " \
                        "%10.5f %10.5f %10.5f %10.5f %10.5f %10.5f" % \
                        (i+1, j+1, re[0], im[0], re[1], im[1], re[2], im[2])
                print

    def _smallest_vectors_log(self):
        r = self._smallest_vectors
        m = self._multiplicity

        print "#%4s %4s %4s %4s %4s %10s" % \
            ("p_i", "p_j", "s_i", "s_j", "mult", "dist")
        for p_i, s_i in enumerate(self._p2s_map): # run in primitive
            for s_j in range(r.shape[0]): # run in supercell
                for tmp_p_j, tmp_s_j in enumerate(self._p2s_map):
                    if self._s2p_map[ s_j ] == tmp_s_j:
                        p_j = tmp_p_j
                for k in range(m[s_j][p_i]):
                    print " %4d %4d %4d %4d %4d %10.5f" % \
                        (p_i+1, p_j+1, s_i+1, s_j+1, m[s_j][p_i],
                          np.linalg.norm(np.dot(r[s_j][p_i][k],
                                                self._pcell.get_cell())))

    def _set_c_dynamical_matrix(self, q):
        import phonopy._phonopy as phonoc

        fc = self._force_constants
        vectors = self._smallest_vectors
        mass = self._pcell.get_masses()
        multiplicity = self._multiplicity
        size_prim = len(mass)
        size_super = fc.shape[0]
        dynamical_matrix_real = np.zeros((size_prim * 3, size_prim * 3),
                                         dtype=float)
        dynamical_matrix_image = np.zeros((size_prim * 3, size_prim * 3),
                                          dtype=float)
        phonoc.dynamical_matrix(dynamical_matrix_real,
                                dynamical_matrix_image,
                                fc,
                                np.array(q, dtype=float),
                                vectors,
                                multiplicity,
                                mass,
                                np.array(self._s2p_map),
                                np.array(self._p2s_map))
        dm = dynamical_matrix_real + dynamical_matrix_image * 1j
        self._dynamical_matrix = (dm + dm.conj().transpose()) / 2



# Non analytical term correction (NAC)
# Call this when NAC is required instead of DynamicalMatrix
class DynamicalMatrixNAC(DynamicalMatrix):
    def __init__(self,
                 supercell,
                 primitive,
                 force_constants,
                 nac_params=None,
                 method='wang',
                 symprec=1e-5):

        DynamicalMatrix.__init__(self,
                                 supercell,
                                 primitive,
                                 force_constants,
                                 symprec=1e-5)
        self._bare_force_constants = self._force_constants.copy()
        self._method = method
        self._nac_params = nac_params
        self._nac = True

    def set_nac_params(self, nac_params, method='wang'):
        self._nac_params = nac_params
        self._method = method

    def set_dynamical_matrix(self, q_red, q_direction=None, verbose=False):
        num_atom = self._pcell.get_number_of_atoms()
        nac_q = np.zeros((num_atom * 3, num_atom * 3), dtype=float)

        if q_direction==None:
            q = np.dot(q_red, np.linalg.inv(self._pcell.get_cell()).T)
        else:
            q = np.dot(q_direction, np.linalg.inv(self._pcell.get_cell()).T)

        if (q_direction==None and np.abs(q).sum() < self._symprec) or \
                ((not q_direction==None) and
                 np.abs(q_direction).sum() < self._symprec):
            self._force_constants = self._bare_force_constants.copy()
            DynamicalMatrix.set_dynamical_matrix(self, np.array(q_red), verbose)
            return False
    
        born = np.array(self._nac_params['born'])
        factor = self._nac_params['factor']
        if (isinstance(factor, list) or
            isinstance(factor, tuple)):
            unit_conversion = factor[0]
            damping_factor = factor[1]
        else:
            unit_conversion = factor
            damping_factor = DAMPING_FACTOR
            
        dielectric = np.array(self._nac_params['dielectric'])
        volume = self._pcell.get_volume()
        m = self._pcell.get_masses()
        constant = unit_conversion * 4.0 * np.pi / volume \
            / np.dot(q, np.dot(dielectric, q))
        charge_sum = self._get_charge_sum(num_atom, q, born)

        # Parlinski method
        if self._method=='parlinski':
            q_distance = np.array(q_red) - np.array(q_red).round()
            constant *= \
                np.exp(- np.dot(q_distance, q_distance) / damping_factor ** 2)
            for i in range(num_atom):
                for j in range(num_atom):
                    nac_q[ i*3:(i+1)*3, j*3:(j+1)*3 ] = \
                        charge_sum[ i, j ] * constant / np.sqrt(m[i] * m[j])

            DynamicalMatrix.set_dynamical_matrix(self, np.array(q_red), verbose)
            self._dynamical_matrix += nac_q

        # Wang method (J. Phys.: Condens. Matter 22 (2010) 202201)
        else:
            for i in range(num_atom):
                for j in range(num_atom):
                    nac_q[ i*3:(i+1)*3, j*3:(j+1)*3 ] = \
                        charge_sum[ i, j ] * constant
            self._set_NAC_force_constants(nac_q)
            DynamicalMatrix.set_dynamical_matrix(self, q_red, verbose)

    def _set_NAC_force_constants(self, nac_q):
        fc = self._bare_force_constants.copy()
        N = (self._scell.get_number_of_atoms() /
             self._pcell.get_number_of_atoms())
        for s1 in range(self._scell.get_number_of_atoms()):
            # This if-statement is the trick.
            # In contructing dynamical matrix in phonopy
            # fc of left indices with s1 == self._s2p_map[ s1 ] are
            # only used.
            if not (s1==self._s2p_map[ s1 ]):
                continue
            p1 = self._p2p_map[ self._s2p_map[ s1 ] ]
            for s2 in range(self._scell.get_number_of_atoms()):            
                p2 = self._p2p_map[ self._s2p_map[ s2 ] ]
                fc[ s1, s2 ] += nac_q[ p1*3:(p1+1)*3, p2*3:(p2+1)*3 ] / N
        self._force_constants = fc

    def _get_charge_sum(self, num_atom, q, born):
        charge_sum = np.zeros((num_atom, num_atom, 3, 3), dtype=float)
        for i in range(num_atom):
            for j in range(num_atom):
                for a in (0, 1, 2):
                    for b in (0, 1, 2):
                        charge_sum[ i, j, a, b ] = \
                            np.dot(q, born[i, :, a]) * np.dot(q, born[j, :, b])
        return charge_sum






# Helper methods
def get_equivalent_smallest_vectors(atom_number_supercell,
                                    atom_number_primitive,
                                    supercell,
                                    primitive_lattice,
                                    symprec):
    distances = []
    differences = []
    reduced_bases = get_reduced_bases(supercell.get_cell(), symprec)
    positions = np.dot(supercell.get_positions(),
                       np.linalg.inv(reduced_bases))

    # Atomic positions are confined into the lattice made of reduced bases.
    for pos in positions:
        pos -= pos.round()

    p_pos = positions[atom_number_primitive]
    s_pos = positions[atom_number_supercell]
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            for k in (-1, 0, 1):
                # The vector arrow is from the atom in primitive to
                # the atom in supercell cell plus a supercell lattice
                # point. This is related to determine the phase
                # convension when building dynamical matrix.
                diff = s_pos + np.array([i, j, k]) - p_pos
                differences.append(diff)
                vec = np.dot(diff, reduced_bases)
                distances.append(np.linalg.norm(vec))

    minimum = min(distances)
    smallest_vectors = []
    for i in range(27):
        if abs(minimum - distances[i]) < symprec:
            relative_scale = np.dot(reduced_bases,
                                    np.linalg.inv(primitive_lattice))
            smallest_vectors.append(np.dot(differences[i], relative_scale))
            
    return smallest_vectors

def get_smallest_vectors(supercell, primitive, symprec):
    p2s_map = primitive.get_primitive_to_supercell_map()
    size_super = supercell.get_number_of_atoms()
    size_prim = primitive.get_number_of_atoms()
    r = np.zeros((size_super, size_prim, 27, 3), dtype=float)
    multiplicity = np.zeros((size_super, size_prim), dtype=int)

    for i in range(size_super): # run in supercell
        for j, s_j in enumerate(p2s_map): # run in primitive
            vectors = get_equivalent_smallest_vectors(i,
                                                      s_j,
                                                      supercell, 
                                                      primitive.get_cell(),
                                                      symprec)
            multiplicity[i][j] = len(vectors)
            for k, elem in enumerate(vectors):
                r[i][j][k] = elem

    return r, multiplicity

