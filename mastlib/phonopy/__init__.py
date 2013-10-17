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

import sys
import numpy as np
from phonopy.structure.atoms import Atoms
from phonopy.structure.symmetry import Symmetry
from phonopy.structure.cells import get_supercell, Primitive, print_cell
from phonopy.harmonic.displacement import get_least_displacements, print_displacements
from phonopy.harmonic.force_constants import get_force_constants, symmetrize_force_constants, rotational_invariance, cutoff_force_constants
from phonopy.harmonic.dynamical_matrix import DynamicalMatrix, DynamicalMatrixNAC
from phonopy.phonon.band_structure import BandStructure
from phonopy.phonon.thermal_properties import ThermalProperties
from phonopy.harmonic.forces import Forces
from phonopy.phonon.mesh import Mesh
from phonopy.units import VaspToTHz
from phonopy.phonon.dos import TotalDos, PartialDos
from phonopy.phonon.thermal_displacement import ThermalDisplacements, ThermalDistances
from phonopy.phonon.animation import Animation
from phonopy.phonon.modulation import Modulation
from phonopy.phonon.qpoints_mode import write_yaml as write_yaml_qpoints
from phonopy.phonon.character_table import CharacterTable

class Phonopy:
    def __init__(self,
                 unitcell,
                 supercell_matrix,
                 distance=0.01,
                 factor=VaspToTHz,
                 is_auto_displacements=True,
                 symprec=1e-5,
                 is_symmetry=True,
                 log_level=0):
        self._symprec = symprec
        self._unitcell = unitcell
        self._supercell_matrix = supercell_matrix
        self._factor = factor
        self._is_symmetry = is_symmetry
        self._log_level = log_level
        self._supercell = None
        self._set_supercell()
        self._symmetry = None
        self._set_symmetry()

        # set_displacements (used only in preprocess)
        self._displacements = None
        self._displacement_directions = None
        self._supercells_with_displacements = None
        if is_auto_displacements:
            self.generate_displacements(distance)

        # set_post_process
        self._primitive = None
        self._dynamical_matrix = None
        self._is_nac = False

        # set_force_constants or set_forces
        self._sets_of_forces = None
        self._force_constants = None

        # set_band_structure
        self._band_structure = None

        # set_mesh
        self._mesh = None

        # set_thermal_properties
        self._thermal_properties = None

        # set_thermal_displacements
        self._thermal_displacements = None

        # set_partial_DOS
        self._pdos = None

        # set_total_DOS
        self._total_dos = None

        # set_modulation
        self._modulation = None

        # set_character_table
        self._character_table = None
        
    def get_primitive(self):
        return self._primitive
    primitive = property(get_primitive)

    def set_primitive(self, primitive):
        self._primitive = primitive

    def get_unitcell(self):
        return self._unitcell
    unitcell = property(get_unitcell)

    def get_supercell(self):
        return self._supercell
    supercell = property(get_supercell)

    def set_supercell(self, supercell):
        self._supercell = supercell

    def get_symmetry(self):
        return self._symmetry
    symmetry = property(get_symmetry)

    def get_unit_conversion_factor(self):
        return self._factor
    unit_conversion_factor = property(get_unit_conversion_factor)
    
    def generate_displacements(self,
                               distance=0.01,
                               is_plusminus='auto',
                               is_diagonal=True,
                               is_trigonal=False):
        """Generate displacements automatically

        displacements:
          List of displacements in Cartesian coordinates.
          See 'set_displacements'
        
        displacement_directions:
          List of directions with respect to axes. This gives only the
          symmetrically non equivalent directions. The format is like:
             [[0, 1, 0, 0],
              [7, 1, 0, 1], ...]
          where each list is defined by:
             First value:      Atom index in supercell starting with 0
             Second to fourth: If the direction is displaced or not ( 1, 0, or -1 )
                               with respect to the axes.
                               
        """

        lattice = self._supercell.get_cell()
        self._displacements = []
        self._displacement_directions = \
            get_least_displacements(self._symmetry, 
                                    is_plusminus=is_plusminus,
                                    is_diagonal=is_diagonal,
                                    is_trigonal=is_trigonal,
                                    log_level=self._log_level)

        for disp in self._displacement_directions:
            atom_num = disp[0]
            disp_cartesian = np.dot(disp[1:], lattice)
            disp_cartesian *= distance / np.linalg.norm(disp_cartesian)
            self._displacements.append([atom_num,
                                       disp_cartesian[0],
                                       disp_cartesian[1],
                                       disp_cartesian[2]])

        self._set_supercells_with_displacements()

    def set_displacements(self, displacements):
        """Set displacements manually

        displacemsts: List of disctionaries
           [[0, 0.01, 0.00, 0.00], ...]
        where each set of elements is defined by:
           First value:      Atom index in supercell starting with 0
           Second to fourth: Displacement in Cartesian coordinates
           
        """

        self._displacements = displacements
        self._set_supercells_with_displacements()

    def get_displacements(self):
        return self._displacements
    displacements = property(get_displacements)

    def get_displacement_directions(self):
        return self._displacement_directions
    displacement_directions = property(get_displacement_directions)

    def print_displacements(self):
        print "Least displacements:"
        print " Atom       Displacement"
        print " ----------------------------"
        for disp in self._displacements:
            print " %4d  " % disp[0],
            print disp[1:4]

    def get_supercells_with_displacements(self):
        return self._supercells_with_displacements

    def set_post_process(self,
                         primitive_matrix=np.eye(3, dtype=float),
                         sets_of_forces=None,
                         force_constants=None,
                         is_nac=False,
                         calculate_full_force_constants=False,
                         force_constants_decimals=None):
        """
        Set forces to prepare phonon calculations. The order of
        'sets_of_forces' has to correspond to that of 'displacements'.

        primitive_matrix:
          Relative axes of primitive cell to the input unit cell.
          Relative axes to the supercell is calculated by:
             supercell_matrix^-1 * primitive_matrix
          Therefore primitive cell lattice is finally calculated by:
             (supercell_lattice * (supercell_matrix)^-1 * primitive_matrix)^T

        sets_of_forces:
           [[[f_1x, f_1y, f_1z], [f_2x, f_2y, f_2z], ...], # first supercell
             [[f_1x, f_1y, f_1z], [f_2x, f_2y, f_2z], ...], # second supercell
             ...                                                  ]
        """

        self._is_nac = is_nac

        # Primitive cell
        inv_supercell_matrix = np.linalg.inv(self._supercell_matrix)
        self._primitive = Primitive(
            self._supercell,
            np.dot(inv_supercell_matrix, primitive_matrix),
            self._symprec)

        # Force constants
        if self._force_constants==None:
            if force_constants == None:
                if self._sets_of_forces==None:
                    if not sets_of_forces == None:
                        self.set_forces(sets_of_forces)
                    else:
                        print "In set_post_process, sets_of_forces or force_constants"
                        print "has to be set."
                        return False

                if calculate_full_force_constants:
                    self.set_force_constants_from_forces(
                        distributed_atom_list=None,
                        force_constants_decimals=force_constants_decimals)
                else:
                    self.set_force_constants_from_forces(
                        distributed_atom_list=\
                            self._primitive.get_primitive_to_supercell_map(),
                        force_constants_decimals=force_constants_decimals)
            else:
                self.set_force_constants(force_constants)

        # Dynamical Matrix
        self.set_dynamical_matrix()

    def set_nac_params(self, nac_params, method='wang'):
        if self._is_nac:
            self._dynamical_matrix.set_nac_params(nac_params, method)

    def set_dynamical_matrix(self):
        if self._is_nac:
            self._dynamical_matrix = \
                DynamicalMatrixNAC(self._supercell,
                                   self._primitive,
                                   self._force_constants,
                                   symprec=self._symprec)
        else:
            self._dynamical_matrix = \
                DynamicalMatrix(self._supercell,
                                self._primitive,
                                self._force_constants,
                                symprec=self._symprec)

    def get_dynamical_matrix(self):
        return self._dynamical_matrix
    dynamical_matrix = property(get_dynamical_matrix)

    def set_forces(self, sets_of_forces):
        forces = []
        for i, disp in enumerate(self._displacements):
            forces.append(Forces(disp[0],
                                 disp[1:4],
                                 sets_of_forces[i]))
        self._sets_of_forces = forces

    def set_force_constants_from_forces(self,
                                        distributed_atom_list=None,
                                        force_constants_decimals=None):
        self._force_constants = get_force_constants(
            self._sets_of_forces,
            self._symmetry,
            self._supercell,
            atom_list=distributed_atom_list,
            decimals=force_constants_decimals)

    def set_force_constants_zero_with_radius(self,
                                             cutoff_radius):
        cutoff_force_constants(self._force_constants,
                               self._supercell,
                               cutoff_radius,
                               symprec=self._symprec)

    def set_force_constants(self, force_constants):
        self._force_constants = force_constants

    def symmetrize_force_constants(self, iteration=3):
        symmetrize_force_constants(self._force_constants, iteration)
        
    def get_force_constants(self):
        return self._force_constants
    force_constants = property(get_force_constants)

    def get_rotational_condition_of_fc(self):
        return rotational_invariance(self._force_constants,
                                     self._supercell,
                                     self._primitive,
                                     self._symprec)

    def get_dynamical_matrix_at_q(self, q):
        self._dynamical_matrix.set_dynamical_matrix(q)
        return self._dynamical_matrix.get_dynamical_matrix()

    # Frequency at a q-point
    def get_frequencies(self, q):
        """
        Calculate phonon frequencies at q
        
        q: q-vector in reduced coordinates of primitive cell
        """
        self._dynamical_matrix.set_dynamical_matrix(q)
        dm = self._dynamical_matrix.get_dynamical_matrix()
        frequencies = []
        for eig in np.linalg.eigvalsh(dm).real:
            if eig < 0:
                frequencies.append(-np.sqrt(-eig))
            else:
                frequencies.append(np.sqrt(eig))
            
        return np.array(frequencies) * self._factor

    # Frequency and eigenvector at a q-point
    def get_frequencies_with_eigenvectors(self, q):
        """
        Calculate phonon frequencies and eigenvectors at q
        
        q: q-vector in reduced coordinates of primitive cell
        """
        self._dynamical_matrix.set_dynamical_matrix(q)
        dm = self._dynamical_matrix.get_dynamical_matrix()
        frequencies = []
        eigvals, eigenvectors = np.linalg.eigh(dm)
        frequencies = []
        for eig in eigvals:
            if eig < 0:
                frequencies.append(-np.sqrt(-eig))
            else:
                frequencies.append(np.sqrt(eig))

        return np.array(frequencies) * self._factor, eigenvectors
                
        ## This expression may not be supported in old python versions.
        # frequencies = np.array(
        #     [np.sqrt(x) if x > 0 else -np.sqrt(-x) for x in eigvals])
        # return frequencies * self._factor, eigenvectors

    # Band structure
    def set_band_structure(self,
                           bands,
                           is_eigenvectors=False,
                           is_band_connection=False):

        self._band_structure = BandStructure(
            bands,
            self._dynamical_matrix,
            self._primitive,
            is_eigenvectors=is_eigenvectors,
            is_band_connection=is_band_connection,
            factor=self._factor)

    def get_band_structure(self):
        band = self._band_structure
        return (band.get_qpoints(),
                band.get_distances(),                
                band.get_frequencies(),
                band.get_eigenvectors())

    def plot_band_structure(self, symbols=None):
        return self._band_structure.plot_band(symbols)

    def write_yaml_band_structure(self):
        self._band_structure.write_yaml()

    # Mesh sampling
    def set_mesh(self,
                 mesh,
                 shift=None,
                 is_time_reversal=True,
                 is_symmetry=True,
                 is_eigenvectors=False,
                 is_gamma_center=False):

        self._mesh = Mesh(self._dynamical_matrix,
                          self._primitive,
                          mesh,
                          shift=shift,
                          is_time_reversal=is_time_reversal,
                          is_symmetry=is_symmetry,
                          is_eigenvectors=is_eigenvectors,
                          is_gamma_center=is_gamma_center,
                          factor=self._factor,
                          symprec=self._symprec)

    def get_mesh(self):
        return (self._mesh.get_qpoints(),
                self._mesh.get_weights(),
                self._mesh.get_frequencies(),
                self._mesh.get_eigenvectors())

    def write_yaml_mesh(self):
        self._mesh.write_yaml()

    # Thermal property
    def set_thermal_properties(self,
                               t_step=10,
                               t_max=1000,
                               t_min=0,
                               cutoff_frequency=None):
        if self._mesh==None:
            print "set_mesh has to be done before set_thermal_properties"
            sys.exit(1)

        tp = ThermalProperties(self._mesh.get_frequencies(),
                               weights=self._mesh.get_weights(),
                               cutoff_frequency=cutoff_frequency)
        tp.set_thermal_properties(t_step, t_max, t_min)
        self._thermal_properties = tp

    def get_thermal_properties(self):
        temps, fe, entropy, cv = \
            self._thermal_properties.get_thermal_properties()
        return temps, fe, entropy, cv

    def plot_thermal_properties(self):
        return self._thermal_properties.plot_thermal_properties()

    def write_yaml_thermal_properties(self):
        self._thermal_properties.write_yaml()

    # Partial DOS
    def set_partial_DOS(self,
                        sigma=None,
                        omega_min=None,
                        omega_max=None,
                        omega_pitch=None):

        if self._mesh==None:
            print "set_mesh has to be done before set_thermal_properties"
            sys.exit(1)
        if self._mesh.get_eigenvectors() == None:
            print "Eigenvectors have to be calculated."
            sys.exit(1)

        pdos = PartialDos(self._mesh.get_frequencies(),
                          self._mesh.get_weights(),
                          self._mesh.get_eigenvectors(),
                          sigma=sigma)
        pdos.set_draw_area(omega_min,
                           omega_max,
                           omega_pitch)
        pdos.calculate()
        self._pdos = pdos

    def get_partial_DOS(self):
        """
        Retern omegas and partial_dos.
        The first element is omegas and the second is partial_dos.
        
        omegas: [freq1, freq2, ...]
        partial_dos:
          [[elem1-freq1, elem1-freq2, ...],
           [elem2-freq1, elem2-freq2, ...],
           ...]

          where
           elem1: atom1-x compornent
           elem2: atom1-y compornent
           elem3: atom1-z compornent
           elem4: atom2-x compornent
           ...
        """
        return self._pdos.get_partial_dos()

    def plot_partial_DOS(self, pdos_indices=None, legend=None):
        return self._pdos.plot_pdos(indices=pdos_indices,
                                    legend=legend)

    def write_partial_DOS(self):
        self._pdos.write()

    # Total DOS
    def set_total_DOS(self,
                      sigma=None,
                      omega_min=None,
                      omega_max=None,
                      omega_pitch=None):

        if self._mesh==None:
            print "set_mesh has to be done before set_thermal_properties"
            sys.exit(1)

        total_dos = TotalDos(self._mesh.get_frequencies(),
                             self._mesh.get_weights(),
                             sigma=sigma)
        total_dos.set_draw_area(omega_min,
                                omega_max,
                                omega_pitch)
        total_dos.calculate()
        self._total_dos = total_dos

    def get_total_DOS(self):
        """
        Retern omegas and total dos.
        The first element is omegas and the second is total dos.
        
        omegas: [freq1, freq2, ...]
        total_dos: [dos1, dos2, ...]
        """
        return self._total_dos.get_dos()

    def set_Debye_frequency(self, freq_max_fit=None):
        self._total_dos.set_Debye_frequency(
            self._primitive.get_number_of_atoms(), freq_max_fit)

    def get_Debye_frequency(self):
        return self._total_dos.get_Debye_frequency()

    def plot_total_DOS(self):
        return self._total_dos.plot_dos()

    def write_total_DOS(self):
        self._total_dos.write()

    # Thermal displacement
    def set_thermal_displacements(self,
                                  t_step=10,
                                  t_max=1000,
                                  t_min=0,
                                  projector=None,
                                  cutoff_eigenvalue=None):
        """
        cutoff_eigenvalue:
          phonon modes that have frequencies below cutoff_eigenvalue
          are ignored.
          e.g. 0.1 (THz)
        """
        if self._mesh==None:
            print "set_mesh has to be done before set_thermal_properties"
            sys.exit(1)
        if self._mesh.get_eigenvectors() == None:
            print "Eigenvectors have to be calculated."
            sys.exit(1)

        td = ThermalDisplacements(self._mesh.get_eigenvalues(),
                                  self._mesh.get_eigenvectors(),
                                  self._mesh.get_weights(),
                                  self._primitive.get_masses(),
                                  factor=self._factor,
                                  cutoff_eigenvalue=cutoff_eigenvalue)
        td.set_temperature_range(t_min, t_max, t_step)
        if not projector==None:
            td.project_eigenvectors(projector, self._primitive.get_cell())
        td.set_thermal_displacements()
        
        self._thermal_displacements = td

    def plot_thermal_displacements(self, is_legend=False):
        return self._thermal_displacements.plot_thermal_displacements(is_legend)

    def write_yaml_thermal_displacements(self):
        self._thermal_displacements.write_yaml()

    # Thermal displacement
    def set_thermal_distances(self,
                              atom_pairs,
                              t_step=10,
                              t_max=1000,
                              t_min=0,
                              cutoff_eigenvalue=None):
        """
        atom_pairs: List of list
          Mean square distances are calculated for the atom_pairs
          e.g. [[1, 2], [1, 4]]

        cutoff_eigenvalue:
          phonon modes that have frequencies below cutoff_eigenvalue
          are ignored.
          e.g. 0.1 (THz)
        """

        td = ThermalDistances(self._mesh.get_eigenvalues(),
                              self._mesh.get_eigenvectors(),
                              self._mesh.get_weights(),
                              self._supercell,
                              self._primitive,
                              self._mesh.get_qpoints(),
                              symprec=self._symprec,
                              factor=self._factor,
                              cutoff_eigenvalue=cutoff_eigenvalue)
        td.set_temperature_range(t_min, t_max, t_step)
        td.set_thermal_distances(atom_pairs)

        self._thermal_distances = td

    def write_yaml_thermal_distances(self):
        self._thermal_distances.write_yaml()


    # Q-points mode
    def write_yaml_qpoints(self,
                           qpoints,
                           is_eigenvectors=False,
                           factor=VaspToTHz):
        
        write_yaml_qpoints(qpoints,
                           self._primitive,
                           self._dynamical_matrix,
                           is_eigenvectors=is_eigenvectors,
                           factor=self._factor)

    # Animation
    def write_animation(self,
                        qpoint=None,
                        anime_type='v_sim',
                        band_index=None,
                        amplitude=None,
                        num_div=None,
                        shift=None,
                        filename=None):
        if qpoint==None:
            animation = Animation([0, 0, 0],
                                  self._dynamical_matrix,
                                  self._primitive,
                                  shift=shift)
        else:
            animation = Animation(qpoint,
                                  self._dynamical_matrix,
                                  self._primitive,
                                  shift=shift)
        if anime_type=='v_sim':
            if amplitude:
                amplitude_ = amplitude
            else:
                amplitude_ = 1.0

            if filename:
                animation.write_v_sim(amplitude=amplitude_,
                                      factor=self._factor,
                                      filename=filename)
            else:
                animation.write_v_sim(amplitude=amplitude_,
                                      factor=self._factor)

            
        if (anime_type=='arc' or
            anime_type=='xyz' or
            anime_type=='jmol' or
            anime_type=='poscar'):
            if band_index==None or amplitude==None or num_div==None:
                print "Parameters are not correctly set for animation."
                sys.exit(1)

            if anime_type=='arc' or anime_type==None:
                if filename:
                    animation.write_arc(band_index,
                                        amplitude,
                                        num_div,
                                        filename=filename)
                else:
                    animation.write_arc(band_index,
                                        amplitude,
                                        num_div)
    
            if anime_type=='xyz':
                if filename:
                    animation.write_xyz(band_index,
                                        amplitude,
                                        num_div,
                                        self._factor,
                                        filename=filename)
                else:
                    animation.write_xyz(band_index,
                                        amplitude,
                                        num_div,
                                        self._factor)
    
            if anime_type=='jmol':
                if filename:
                    animation.write_xyz_jmol(amplitude=amplitude,
                                             factor=self._factor,
                                             filename=filename)
                else:
                    animation.write_xyz_jmol(amplitude=amplitude,
                                             factor=self._factor)
    
            if anime_type=='poscar':
                if filename:
                    animation.write_POSCAR(band_index,
                                           amplitude,
                                           num_div,
                                           filename=filename)
                else:
                    animation.write_POSCAR(band_index,
                                           amplitude,
                                           num_div)
                    

    # Modulation
    def set_modulations(self, dimension, phonon_modes):
        self._modulation = Modulation(self._dynamical_matrix,
                                      self._primitive,
                                      dimension=dimension,
                                      phonon_modes=phonon_modes,
                                      factor=self._factor)
                    
    def get_modulations(self):
        """Returns cells with modulations as Atoms objects"""
        return self._modulation.get_modulations()
                
    def get_delta_modulations(self):
        """Return modulations relative to equilibrium supercell

        (modulations, supercell)

        modulations: Atomic modulations of supercell in Cartesian coordinates
        supercell: Supercell as an Atoms object.
        
        """
        return self._modulation.get_delta_modulations()
                
    def write_modulations(self):
        """Create MPOSCAR's"""
        self._modulation.write()
                          
    def write_yaml_modulations(self):
        self._modulation.write_yaml()


    # Character table
    def set_character_table(self, q, degeneracy_tolerance):
        self._character_table = CharacterTable(
            self._dynamical_matrix,
            q,
            self._primitive,
            factor=self._factor,
            symprec=self._symprec,
            degeneracy_tolerance=degeneracy_tolerance,
            log_level=self._log_level)

    def get_character_table(self):
        return self._character_table
        
    def show_character_table(self, show_irreps=False):
        self._character_table.show(show_irreps=show_irreps)

    def write_yaml_character_table(self, show_irreps=False):
        self._character_table.write_yaml(show_irreps=show_irreps)

    def _set_supercell(self):
        self._supercell = get_supercell(self._unitcell,
                                        self._supercell_matrix,
                                        self._symprec)

    def _set_symmetry(self):
        self._symmetry = Symmetry(self._supercell,
                                  self._symprec,
                                  self._is_symmetry)

    def _set_supercells_with_displacements(self):
        supercells = []
        for disp in self._displacements:
            positions = self._supercell.get_positions()
            positions[disp[0]] += disp[1:4]
            supercells.append(Atoms(
                    numbers=self._supercell.get_atomic_numbers(),
                    masses=self._supercell.get_masses(),
                    magmoms=self._supercell.get_magnetic_moments(),
                    positions=positions,
                    cell=self._supercell.get_cell(),
                    pbc=True))

        self._supercells_with_displacements = supercells
                        
