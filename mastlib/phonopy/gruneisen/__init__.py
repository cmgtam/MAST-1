# Copyright (C) 2012 Atsushi Togo
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
from phonopy.phonon.mesh import get_qpoints
from phonopy.phonon.band_structure import estimate_band_connection

def mesh_sampling(phonon,
                  phonon_plus,
                  phonon_minus,
                  mesh,
                  grid_shift=None,
                  is_gamma_center=False,
                  epsilon=1e-4,
                  matplot=None,
                  cutoff_frequency=None,
                  color_scheme=None,
                  marker='o',
                  markersize=None):
    factor = phonon.get_unit_conversion_factor(),
    primitive = phonon.get_primitive()
    gruneisen = Gruneisen(phonon.get_dynamical_matrix(),
                          phonon_plus.get_dynamical_matrix(),
                          phonon_minus.get_dynamical_matrix(),
                          primitive.get_volume(),
                          phonon_plus.get_primitive().get_volume(),
                          phonon_minus.get_primitive().get_volume())
    qpoints, weights = get_qpoints(mesh,
                                   primitive,
                                   grid_shift,
                                   is_gamma_center)
    gruneisen.set_qpoints(qpoints)
    gamma = gruneisen.get_gruneisen()
    eigenvalues = gruneisen.get_eigenvalues()
    frequencies = np.sqrt(abs(eigenvalues)) * np.sign(eigenvalues) * factor

    f = open("gruneisen.yaml", 'w')
    f.write("nqpoint: %d\n" % len(qpoints))
    f.write("phonon:\n")
    for q, w, gs, freqs in zip(qpoints, weights, gamma, frequencies):
        f.write("- q-position: [ %10.7f, %10.7f, %10.7f ]\n" % tuple(q))
        f.write("  multiplicity: %d\n" % w)
        f.write("  band:\n")
        for j, (g, freq) in enumerate(zip(gs, freqs)):
            f.write("  - # %d\n" % (j + 1))
            f.write("    gruneisen: %15.10f\n" % g)
            f.write("    frequency: %15.10f\n" % freq)
        f.write("\n")
    f.close()

    if matplot:
        for i, (g, freqs) in enumerate(zip(gamma.T, frequencies.T)):
            if cutoff_frequency:
                g = np.extract(freqs > cutoff_frequency, g)
                freqs = np.extract(freqs > cutoff_frequency, freqs)

            if color_scheme == 'RB':
                n = len(gamma.T) - 1
                color = (1. / n * i, 0, 1./ n * (n - i))
                if markersize:
                    matplot.plot(freqs, g, marker,
                                 color=color, markersize=markersize)
                else:
                    matplot.plot(freqs, g, marker, color=color)
            elif color_scheme == 'RG':
                n = len(gamma.T) - 1
                color = (1. / n * i, 1./ n * (n - i), 0)
                if markersize:
                    matplot.plot(freqs, g, marker,
                                 color=color, markersize=markersize)
                else:
                    matplot.plot(freqs, g, marker, color=color)
            elif color_scheme == 'RGB':
                n = len(gamma.T) - 1
                color = (max(2./ n * (i - n / 2.), 0),
                         min(2./ n * i, 2./ n * (n - i)),
                         max(2./ n * (n / 2. - i), 0))
                if markersize:
                    matplot.plot(freqs, g, marker,
                                 color=color, markersize=markersize)
                else:
                    matplot.plot(freqs, g, marker, color=color)
            else:
                if markersize:
                    matplot.plot(freqs, g, marker, markersize=markersize)
                else:
                    matplot.plot(freqs, g, marker)
                
    
def band_structure(phonon,
                   phonon_plus,
                   phonon_minus,
                   paths,
                   num_points,
                   epsilon=1e-4,
                   cutoff_frequency=None,
                   matplot=None):

    primitive = phonon.get_primitive()
    gruneisen = Gruneisen(phonon.get_dynamical_matrix(),
                          phonon_plus.get_dynamical_matrix(),
                          phonon_minus.get_dynamical_matrix(),
                          primitive.get_volume(),
                          phonon_plus.get_primitive().get_volume(),
                          phonon_minus.get_primitive().get_volume(),
                          is_band_connection=True)
    rec_vectors = np.linalg.inv(primitive.get_cell())
    factor = phonon.get_unit_conversion_factor(),
    distance_shift = 0.0
    
    f = open("gruneisen.yaml", 'w')

    f.write("path:\n\n")
    for path in paths:
        qpoints, distances = _get_band_qpoints(path[0],
                                               path[1],
                                               rec_vectors,
                                               num_points=num_points)
        gruneisen.set_qpoints(qpoints)
        gamma = gruneisen.get_gruneisen()
        eigenvalues = gruneisen.get_eigenvalues()
        frequencies = np.sqrt(abs(eigenvalues)) * np.sign(eigenvalues) * factor
        
        distances_with_shift = distances + distance_shift

        f.write("- nqpoint: %d\n" % num_points)
        f.write("  phonon:\n")
        for q, d, gs, freqs in zip(qpoints, distances, gamma, frequencies):
            f.write("  - q-position: [ %10.7f, %10.7f, %10.7f ]\n" % tuple(q))
            f.write("    distance: %10.7f\n" % d)
            f.write("    band:\n")
            for i, (g, freq) in enumerate(zip(gs, freqs)):
                f.write("    - # %d\n" % (i + 1))
                f.write("      gruneisen: %15.10f\n" % g)
                f.write("      frequency: %15.10f\n" % freq)
            f.write("\n")
                
        if matplot:
            _bandplot(matplot,
                      gamma,
                      frequencies,
                      qpoints,
                      distances_with_shift,
                      epsilon)

        distance_shift = distances_with_shift[-1]

    f.close()

def _get_band_qpoints(q_start, q_end, rec_lattice, num_points=51):
    qpoints = []
    distances = []
    distance = 0.0
    q_start_ = np.array(q_start)
    q_end_ = np.array(q_end)
    dq = (q_end_ - q_start_) / (num_points - 1)
    delta = np.linalg.norm(np.dot(rec_lattice, dq))
    
    for i in range(num_points):
        distances.append(distance)
        qpoints.append(q_start_+ dq * i)
        distance += delta
        
    return np.array(qpoints), np.array(distances)

def _bandplot(plt,
              gamma,
              freqencies,
              qpoints,
              distances_with_shift,
              epsilon=1e-4):
    plt.subplot(2, 1, 1)
    for curve in gamma.T.copy():
        if (abs(qpoints[0]) < epsilon).all():
            curve[0] = curve[1]   # To avoid divergence at Gamma
        if (abs(qpoints[-1]) < epsilon).all():
            curve[-1] = curve[-2] # To avoid divergence at Gamma
        plt.plot(distances_with_shift, curve)
    plt.xlim(0, distances_with_shift[-1])

    plt.subplot(2, 1, 2)
    for freqs in freqencies.T:
        plt.plot(distances_with_shift, freqs)
    plt.xlim(0, distances_with_shift[-1])


class Gruneisen:
    def __init__(self,
                 dynmat,
                 dynmat_plus,
                 dynmat_minus,
                 volume,
                 volume_plus,
                 volume_minus,
                 qpoints=None,
                 is_band_connection=False):
        self._dynmat = dynmat
        self._dynmat_plus = dynmat_plus
        self._dynmat_minus = dynmat_minus
        self._volume = volume
        self._dV = volume_plus - volume_minus
        self._is_band_connection = is_band_connection
        self._qpoints = qpoints

        self._gruneisen = None
        self._eigenvalues = None
        if qpoints:
            self._set_gruneisen()

    def set_qpoints(self, qpoints):
        self._qpoints = qpoints
        self._set_gruneisen()
        
    def get_gruneisen(self):
        return self._gruneisen

    def get_eigenvalues(self):
        return self._eigenvalues

    def _set_gruneisen(self):
        if self._is_band_connection:
            self._q_direction = self._qpoints[0] - self._qpoints[-1]
            prev_eigvecs = None
        dD = []
        eigvals = []
        for i, q in enumerate(self._qpoints):
            if (self._is_band_connection and
                self._dynmat.is_nac()):
                self._dynmat.set_dynamical_matrix(
                    q, q_direction=self._q_direction)
            else:
                self._dynmat.set_dynamical_matrix(q)

            dm = self._dynmat.get_dynamical_matrix()
            eigvals_at_q, eigvecs = np.linalg.eigh(dm)
            eigvals_at_q = eigvals_at_q.real
            dD_at_q = [np.vdot(eig, np.dot(self._get_dD(q), eig)).real
                       for eig in eigvecs.T]

            if self._is_band_connection:
                if i == 0:
                    band_order = range(len(eigvals_at_q))
                else:
                    band_order = estimate_band_connection(prev_eigvecs,
                                                          eigvecs,
                                                          band_order)
                eigvals.append([eigvals_at_q[b] for b in band_order])
                dD.append([dD_at_q[b] for b in band_order])
                prev_eigvecs = eigvecs
            else:
                eigvals.append(eigvals_at_q)
                dD.append(dD_at_q)

        dD = np.array(dD)
        eigvals = np.array(eigvals)
            
        self._gruneisen = -dD / eigvals * self._volume  / self._dV / 2
        self._eigenvalues = eigvals
                
    def _get_dD(self, q):
        if (self._is_band_connection and
            self._dynmat_plus.is_nac() and 
            self._dynmat_minus.is_nac()):
            self._dynmat_plus.set_dynamical_matrix(
                q, q_direction=self._q_direction)
            self._dynmat_minus.set_dynamical_matrix(
                q, q_direction=self._q_direction)
        else:
            self._dynmat_plus.set_dynamical_matrix(q)
            self._dynmat_minus.set_dynamical_matrix(q)
        dm_plus = self._dynmat_plus.get_dynamical_matrix()
        dm_minus = self._dynmat_minus.get_dynamical_matrix()
        return dm_plus - dm_minus
