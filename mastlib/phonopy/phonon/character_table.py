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
from phonopy.structure.symmetry import Symmetry, get_pointgroup
from phonopy.harmonic.force_constants import similarity_transformation
from phonopy.units import VaspToTHz

# from Wikipedia http://en.wikipedia.org/wiki/List_of_character_tables_for_chemically_important_3D_point_groups
character_table = { '6/mmm':
                        { 'rotation_list':
                              [ 'E', 'C6', 'C3', 'C2', 'C2\'', 'C2\'\'',
                                'i', 'S3', 'S6', 'sgh', 'sgd', 'sgv' ],
                          'character_table':
                              { 'A1g': [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
                                'A2g': [ 1, 1, 1, 1,-1,-1, 1, 1, 1, 1,-1,-1 ],
                                'B1g': [ 1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1 ],
                                'B2g': [ 1,-1, 1,-1,-1, 1, 1,-1, 1,-1,-1, 1 ],
                                'E1g': [ 2, 1,-1,-2, 0, 0, 2, 1,-1,-2, 0, 0 ],
                                'E2g': [ 2,-1,-1, 2, 0, 0, 2,-1,-1, 2, 0, 0 ],
                                'A1u': [ 1, 1, 1, 1, 1, 1,-1,-1,-1,-1,-1,-1 ],
                                'A2u': [ 1, 1, 1, 1,-1,-1,-1,-1,-1,-1, 1, 1 ],
                                'B1u': [ 1,-1, 1,-1, 1,-1,-1, 1,-1, 1,-1, 1 ],
                                'B2u': [ 1,-1, 1,-1,-1, 1,-1, 1,-1, 1, 1,-1 ],
                                'E1u': [ 2, 1,-1,-2, 0, 0,-2,-1, 1, 2, 0, 0 ],
                                'E2u': [ 2,-1,-1, 2, 0, 0,-2, 1, 1,-2, 0, 0 ] },
                          'mapping_table': [
            { 'E'     : [ ( ( 1, 0, 0 ),
                            ( 0, 1, 0 ),
                            ( 0, 0, 1 ) ) ],
              'C6'    : [ ( ( 1,-1, 0 ),
                            ( 1, 0, 0 ),
                            ( 0, 0, 1 ) ),
                          ( ( 0, 1, 0 ),
                            (-1, 1, 0 ),
                            ( 0, 0, 1 ) ) ],
              'C3'    : [ ( ( 0,-1, 0 ),
                            ( 1,-1, 0 ),
                            ( 0, 0, 1 ) ),
                          ( (-1, 1, 0 ),
                            (-1, 0, 0 ),
                            ( 0, 0, 1 ) ) ],
              'C2'    : [ ( (-1, 0, 0 ),
                            ( 0,-1, 0 ),
                            ( 0, 0, 1 ) ) ],
              'C2\''  : [ ( ( 0,-1, 0 ),
                            (-1, 0, 0 ),
                            ( 0, 0,-1 ) ),
                          ( (-1, 1, 0 ),
                            ( 0, 1, 0 ),
                            ( 0, 0,-1 ) ),
                          ( ( 1, 0, 0 ),
                            ( 1,-1, 0 ),
                            ( 0, 0,-1 ) ) ],
              'C2\'\'': [ ( ( 0, 1, 0 ),
                            ( 1, 0, 0 ),
                            ( 0, 0,-1 ) ),
                          ( ( 1,-1, 0 ),
                            ( 0,-1, 0 ),
                            ( 0, 0,-1 ) ),
                          ( (-1, 0, 0 ),
                            (-1, 1, 0 ),
                            ( 0, 0,-1 ) ) ],
              'i'     : [ ( (-1, 0, 0 ),
                            ( 0,-1, 0 ),
                            ( 0, 0,-1 ) ) ],
              'S3'    : [ ( (-1, 1, 0 ),
                            (-1, 0, 0 ),
                            ( 0, 0,-1 ) ),
                          ( ( 0,-1, 0 ),
                            ( 1,-1, 0 ),
                            ( 0, 0,-1 ) ) ],
              'S6'    : [ ( ( 0, 1, 0 ),
                            (-1, 1, 0 ),
                            ( 0, 0,-1 ) ),
                          ( ( 1,-1, 0 ),
                            ( 1, 0, 0 ),
                            ( 0, 0,-1 ) ) ],
              'sgh'   : [ ( ( 1, 0, 0 ),
                            ( 0, 1, 0 ),
                            ( 0, 0,-1 ) ) ],
              'sgd'   : [ ( ( 0, 1, 0 ),
                            ( 1, 0, 0 ),
                            ( 0, 0, 1 ) ),
                          ( ( 1,-1, 0 ),
                            ( 0,-1, 0 ),
                            ( 0, 0, 1 ) ),
                          ( (-1, 0, 0 ),
                            (-1, 1, 0 ),
                            ( 0, 0, 1 ) ) ],             
              'sgv'   : [ ( ( 0,-1, 0 ),
                            (-1, 0, 0 ),
                            ( 0, 0, 1 ) ),
                          ( (-1, 1, 0 ),
                            ( 0, 1, 0 ),
                            ( 0, 0, 1 ) ),
                          ( ( 1, 0, 0 ),
                            ( 1,-1, 0 ),
                            ( 0, 0, 1 ) ) ] }
            ]
                          },

                    '6mm':
                        { 'rotation_list':
                              [ 'E', 'C6', 'C3', 'C2', 'sgv', 'sgd' ],
                          'character_table':
                              { 'A1': [ 1, 1, 1, 1, 1, 1],
                                'A2': [ 1, 1, 1, 1,-1,-1],
                                'B1': [ 1,-1, 1,-1, 1,-1],
                                'B2': [ 1,-1, 1,-1,-1, 1],
                                'E1': [ 2, 1,-1,-2, 0, 0],
                                'E2': [ 2,-1,-1, 2, 0, 0] },
                          'mapping_table': [
            { 'E'  : [ ( ( 1, 0, 0 ),
                         ( 0, 1, 0 ),
                         ( 0, 0, 1 ) ) ],
              'C6' : [ ( ( 1,-1, 0 ),
                         ( 1, 0, 0 ),
                         ( 0, 0, 1 ) ),
                       ( ( 0, 1, 0 ),
                         (-1, 1, 0 ),
                         ( 0, 0, 1 ) ) ],
              'C3' : [ ( ( 0,-1, 0 ),
                         ( 1,-1, 0 ),
                         ( 0, 0, 1 ) ),
                       ( (-1, 1, 0 ),
                         (-1, 0, 0 ),
                         ( 0, 0, 1 ) ) ],
              'C2' : [ ( (-1, 0, 0 ),
                         ( 0,-1, 0 ),
                         ( 0, 0, 1 ) ) ],
              'sgv': [ ( ( 0,-1, 0 ),
                         (-1, 0, 0 ),
                         ( 0, 0, 1 ) ),
                       ( (-1, 1, 0 ),
                         ( 0, 1, 0 ),
                         ( 0, 0, 1 ) ),
                       ( ( 1, 0, 0 ),
                         ( 1,-1, 0 ),
                         ( 0, 0, 1 ) ) ],
              'sgd': [ ( ( 0, 1, 0 ),
                         ( 1, 0, 0 ),
                         ( 0, 0, 1 ) ),
                       ( ( 1,-1, 0 ),
                         ( 0,-1, 0 ),
                         ( 0, 0, 1 ) ),
                       ( (-1, 0, 0 ),
                         (-1, 1, 0 ),
                         ( 0, 0, 1 ) ) ] }
            ]
                          },

                    '4/mmm':
                        { 'rotation_list':
                              [ 'E', 'C4', 'C2', 'C2\'', 'C2\'\'', 'i',
                                'S4', 'sgh', 'sgv', 'sgd' ],
                          'character_table':
                              { 'A1g': [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
                                'A2g': [ 1, 1, 1,-1,-1, 1, 1, 1,-1,-1 ],
                                'B1g': [ 1,-1, 1, 1,-1, 1,-1, 1, 1,-1 ],
                                'B2g': [ 1,-1, 1,-1, 1, 1,-1, 1,-1, 1 ],
                                'Eg' : [ 2, 0,-2, 0, 0, 2, 0,-2, 0, 0 ],
                                'A1u': [ 1, 1, 1, 1, 1,-1,-1,-1,-1,-1 ],
                                'A2u': [ 1, 1, 1,-1,-1,-1,-1,-1, 1, 1 ],
                                'B1u': [ 1,-1, 1, 1,-1,-1, 1,-1,-1, 1 ],
                                'B2u': [ 1,-1, 1,-1, 1,-1, 1,-1, 1,-1 ],
                                'Eu' : [ 2, 0,-2, 0, 0,-2, 0, 2, 0, 0 ] },
                          'mapping_table': [
            { 'E'     : [ ( ( 1, 0, 0 ),
                            ( 0, 1, 0 ),
                            ( 0, 0, 1 ) ) ],
              'C4'    : [ ( ( 0,-1, 0 ),
                            ( 1, 0, 0 ),
                            ( 0, 0, 1 ) ),
                          ( ( 0, 1, 0 ),
                            (-1, 0, 0 ),
                            ( 0, 0, 1 ) ) ],
              'C2'    : [ ( (-1, 0, 0 ),
                            ( 0,-1, 0 ),
                            ( 0, 0, 1 ) ) ],
              'C2\''  : [ ( ( 1, 0, 0 ),
                            ( 0,-1, 0 ),
                            ( 0, 0,-1 ) ),
                          ( (-1, 0, 0 ),
                            ( 0, 1, 0 ),
                            ( 0, 0,-1 ) ) ],
              'C2\'\'': [ ( ( 0, 1, 0 ),
                            ( 1, 0, 0 ),
                            ( 0, 0,-1 ) ),
                          ( ( 0,-1, 0 ),
                            (-1, 0, 0 ),
                            ( 0, 0,-1 ) ) ],
              'i'     : [ ( (-1, 0, 0 ),
                            ( 0,-1, 0 ),
                            ( 0, 0,-1 ) ) ],
              'S4'    : [ ( ( 0, 1, 0 ),
                            (-1, 0, 0 ),
                            ( 0, 0,-1 ) ),
                          ( ( 0,-1, 0 ),
                            ( 1, 0, 0 ),
                            ( 0, 0,-1 ) ) ],
              'sgh'   : [ ( ( 1, 0, 0 ),
                            ( 0, 1, 0 ),
                            ( 0, 0,-1 ) ) ],
              'sgv'   : [ ( (-1, 0, 0 ),
                            ( 0, 1, 0 ),
                            ( 0, 0, 1 ) ),
                          ( ( 1, 0, 0 ),
                            ( 0,-1, 0 ),
                            ( 0, 0, 1 ) ) ],
              'sgd'   : [ ( ( 0, 1, 0 ),
                            ( 1, 0, 0 ),
                            ( 0, 0, 1 ) ),
                          ( ( 0,-1, 0 ),
                            (-1, 0, 0 ),
                            ( 0, 0, 1 ) ) ] }
            ]
                          },
                    'mmm':
                        { 'rotation_list':
                              [ 'E', 'C2', 'C2x', 'C2y', 'i', 'sgxy',
                                'sgxz', 'sgyz' ],
                          'character_table':
                              { 'Ag' : [ 1, 1, 1, 1, 1, 1, 1, 1 ],
                                'B1g': [ 1, 1,-1,-1, 1, 1,-1,-1 ],
                                'B2g': [ 1,-1,-1, 1, 1,-1, 1,-1 ],
                                'B3g': [ 1,-1, 1,-1, 1,-1,-1, 1 ],
                                'Au' : [ 1, 1, 1, 1,-1,-1,-1,-1 ],
                                'B1u': [ 1, 1,-1,-1,-1,-1, 1, 1 ],
                                'B2u': [ 1,-1,-1, 1,-1, 1,-1, 1 ],
                                'B3u': [ 1,-1, 1,-1,-1, 1, 1,-1 ] },
                          'mapping_table': [
            { 'E'   : [ ( ( 1, 0, 0 ),
                          ( 0, 1, 0 ),
                          ( 0, 0, 1 ) ) ],
              'C2'  : [ ( (-1, 0, 0 ),
                          ( 0,-1, 0 ),
                          ( 0, 0, 1 ) ) ],
              'C2y' : [ ( (-1, 0, 0 ),
                          ( 0, 1, 0 ),
                          ( 0, 0,-1 ) ) ],
              'C2x' : [ ( ( 1, 0, 0 ),
                          ( 0,-1, 0 ),
                          ( 0, 0,-1 ) ) ],
              'i'   : [ ( (-1, 0, 0 ),
                          ( 0,-1, 0 ),
                          ( 0, 0,-1 ) ) ],
              'sgxy': [ ( ( 1, 0, 0 ),
                          ( 0, 1, 0 ),
                          ( 0, 0,-1 ) ) ],
              'sgxz': [ ( ( 1, 0, 0 ),
                          ( 0,-1, 0 ),
                          ( 0, 0, 1 ) ) ],
              'sgyz': [ ( (-1, 0, 0 ),
                          ( 0, 1, 0 ),
                          ( 0, 0, 1 ) ) ] }
            ]
                          },

                    'm-3m':
                        { 'rotation_list':
                              [ 'E', 'C3', 'C2', 'C4', 'C4^2', 'i',
                                'S4', 'S6', 'sgh', 'sgd' ],
                          'character_table':
                              { 'A1g': [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
                                'A2g': [ 1, 1,-1,-1, 1, 1,-1, 1, 1,-1 ],
                                'Eg' : [ 2,-1, 0, 0, 2, 2, 0,-1, 2, 0 ],
                                'T1g': [ 3, 0,-1, 1,-1, 3, 1, 0,-1,-1 ],
                                'T2g': [ 3, 0, 1,-1,-1, 3,-1, 0,-1, 1 ],
                                'A1u': [ 1, 1, 1, 1, 1,-1,-1,-1,-1,-1 ],
                                'A2u': [ 1, 1,-1,-1, 1,-1, 1,-1,-1, 1 ],
                                'Eu' : [ 2,-1, 0, 0, 2,-2, 0, 1,-2, 0 ],
                                'T1u': [ 3, 0,-1, 1,-1,-3,-1, 0, 1, 1 ],
                                'T2u': [ 3, 0, 1,-1,-1,-3, 1, 0, 1,-1 ] },
                          'mapping_table': [
            { 'E'   : [ ( ( 1, 0, 0 ),
                          ( 0, 1, 0 ),
                          ( 0, 0, 1 ) ) ],
              'C3'  : [ ( ( 0, 0, 1 ),
                          ( 1, 0, 0 ),
                          ( 0, 1, 0 ) ),
                        ( ( 0, 1, 0 ),
                          ( 0, 0, 1 ),
                          ( 1, 0, 0 ) ),
                        ( ( 0, 0,-1 ),
                          ( 1, 0, 0 ),
                          ( 0,-1, 0 ) ),
                        ( ( 0,-1, 0 ),
                          ( 0, 0,-1 ),
                          ( 1, 0, 0 ) ),
                        ( ( 0, 0,-1 ),
                          (-1, 0, 0 ),
                          ( 0, 1, 0 ) ),
                        ( ( 0, 1, 0 ),
                          ( 0, 0,-1 ),
                          (-1, 0, 0 ) ),
                        ( ( 0, 0, 1 ),
                          (-1, 0, 0 ),
                          ( 0,-1, 0 ) ),
                        ( ( 0,-1, 0 ),
                          ( 0, 0, 1 ),
                          (-1, 0, 0 ) ) ],
              'C2'  : [ ( ( 0, 1, 0 ),
                          ( 1, 0, 0 ),
                          ( 0, 0,-1 ) ),
                        ( (-1, 0, 0 ),
                          ( 0, 0, 1 ),
                          ( 0, 1, 0 ) ),
                        ( ( 0, 0, 1 ),
                          ( 0,-1, 0 ),
                          ( 1, 0, 0 ) ),
                        ( ( 0,-1, 0 ),
                          (-1, 0, 0 ),
                          ( 0, 0,-1 ) ),
                        ( (-1, 0, 0 ),
                          ( 0, 0,-1 ),
                          ( 0,-1, 0 ) ),
                        ( ( 0, 0,-1 ),
                          ( 0,-1, 0 ),
                          (-1, 0, 0 ) ) ],
              'C4'  : [ ( ( 0,-1, 0 ),
                          ( 1, 0, 0 ),
                          ( 0, 0, 1 ) ),
                        ( ( 0, 1, 0 ),
                          (-1, 0, 0 ),
                          ( 0, 0, 1 ) ),
                        ( ( 1, 0, 0 ),
                          ( 0, 0,-1 ),
                          ( 0, 1, 0 ) ),
                        ( ( 1, 0, 0 ),
                          ( 0, 0, 1 ),
                          ( 0,-1, 0 ) ),
                        ( ( 0, 0, 1 ),
                          ( 0, 1, 0 ),
                          (-1, 0, 0 ) ),
                        ( ( 0, 0,-1 ),
                          ( 0, 1, 0 ),
                          ( 1, 0, 0 ) ) ],
              'C4^2': [ ( (-1, 0, 0 ),
                          ( 0,-1, 0 ),
                          ( 0, 0, 1 ) ),
                        ( ( 1, 0, 0 ),
                          ( 0,-1, 0 ),
                          ( 0, 0,-1 ) ),
                        ( (-1, 0, 0 ),
                          ( 0, 1, 0 ),
                          ( 0, 0,-1 ) ) ],
              'i'   : [ ( (-1, 0, 0 ),
                          ( 0,-1, 0 ),
                          ( 0, 0,-1 ) ) ],
              'S4'  : [ ( ( 0, 1, 0 ),
                          (-1, 0, 0 ),
                          ( 0, 0,-1 ) ),
                        ( ( 0,-1, 0 ),
                          ( 1, 0, 0 ),
                          ( 0, 0,-1 ) ),
                        ( (-1, 0, 0 ),
                          ( 0, 0, 1 ),
                          ( 0,-1, 0 ) ),
                        ( (-1, 0, 0 ),
                          ( 0, 0,-1 ),
                          ( 0, 1, 0 ) ),
                        ( ( 0, 0,-1 ),
                          ( 0,-1, 0 ),
                          ( 1, 0, 0 ) ),
                        ( ( 0, 0, 1 ),
                          ( 0,-1, 0 ),
                          (-1, 0, 0 ) ) ],
              'S6'  : [ ( ( 0, 0,-1 ),
                          (-1, 0, 0 ),
                          ( 0,-1, 0 ) ),
                        ( ( 0,-1, 0 ),
                          ( 0, 0,-1 ),
                          (-1, 0, 0 ) ),
                        ( ( 0, 0, 1 ),
                          (-1, 0, 0 ),
                          ( 0, 1, 0 ) ),
                        ( ( 0, 1, 0 ),
                          ( 0, 0, 1 ),
                          (-1, 0, 0 ) ),
                        ( ( 0, 0, 1 ),
                          ( 1, 0, 0 ),
                          ( 0,-1, 0 ) ),
                        ( ( 0,-1, 0 ),
                          ( 0, 0, 1 ),
                          ( 1, 0, 0 ) ),
                        ( ( 0, 0,-1 ),
                          ( 1, 0, 0 ),
                          ( 0, 1, 0 ) ),
                        ( ( 0, 1, 0 ),
                          ( 0, 0,-1 ),
                          ( 1, 0, 0 ) ) ],
              'sgh' : [ ( ( 1, 0, 0 ),
                          ( 0, 1, 0 ),
                          ( 0, 0,-1 ) ),
                        ( (-1, 0, 0 ),
                          ( 0, 1, 0 ),
                          ( 0, 0, 1 ) ),
                        ( ( 1, 0, 0 ),
                          ( 0,-1, 0 ),
                          ( 0, 0, 1 ) ) ],
              'sgd' : [ ( ( 0,-1, 0 ),
                          (-1, 0, 0 ),
                          ( 0, 0, 1 ) ),
                        ( ( 1, 0, 0 ),
                          ( 0, 0,-1 ),
                          ( 0,-1, 0 ) ),
                        ( ( 0, 0,-1 ),
                          ( 0, 1, 0 ),
                          (-1, 0, 0 ) ),
                        ( ( 0, 1, 0 ),
                          ( 1, 0, 0 ),
                          ( 0, 0, 1 ) ),
                        ( ( 1, 0, 0 ),
                          ( 0, 0, 1 ),
                          ( 0, 1, 0 ) ),
                        ( ( 0, 0, 1 ),
                          ( 0, 1, 0 ),
                          ( 1, 0, 0 ) ) ]
              }
            ]
                          },

                    '-6m2':
                        { 'rotation_list':
                              [ 'E', 'C3', 'C2', 'sgh', 'S3', 'sgv' ],
                          'character_table':
                              { 'A1\''  : [ 1, 1, 1, 1, 1, 1 ],
                                'A2\''  : [ 1, 1,-1, 1, 1,-1 ],
                                'E\''   : [ 2,-1, 0, 2,-1, 0 ],
                                'A1\'\'': [ 1, 1, 1,-1,-1,-1 ],
                                'A2\'\'': [ 1, 1,-1,-1,-1, 1 ],
                                'E\'\'' : [ 2,-1, 0,-2, 1, 0 ] },
                          'mapping_table': [
            { 'E'   : [ ( ( 1, 0, 0 ),
                          ( 0, 1, 0 ),
                          ( 0, 0, 1 ) ) ],
              'C3' : [ ( ( 0,-1, 0 ),
                         ( 1,-1, 0 ),
                         ( 0, 0, 1 ) ),
                       ( (-1, 1, 0 ),
                         (-1, 0, 0 ),
                         ( 0, 0, 1 ) ) ],
              'C2' : [ ( ( 0, 1, 0 ),
                         ( 1, 0, 0 ),
                         ( 0, 0,-1 ) ),
                       ( ( 1,-1, 0 ),
                         ( 0,-1, 0 ),
                         ( 0, 0,-1 ) ),
                       ( (-1, 0, 0 ),
                         (-1, 1, 0 ),
                         ( 0, 0,-1 ) ) ],
              'sgh': [ ( ( 1, 0, 0 ),
                         ( 0, 1, 0 ),
                         ( 0, 0,-1 ) ) ],
              'S3' : [ ( ( 0,-1, 0 ),
                         ( 1,-1, 0 ),
                         ( 0, 0,-1 ) ),
                       ( (-1, 1, 0 ),
                         (-1, 0, 0 ),
                         ( 0, 0,-1 ) ) ],
              'sgv': [ ( ( 0, 1, 0 ),
                         ( 1, 0, 0 ),
                         ( 0, 0, 1 ) ),
                       ( ( 1,-1, 0 ),
                         ( 0,-1, 0 ),
                         ( 0, 0, 1 ) ),
                       ( (-1, 0, 0 ),
                         (-1, 1, 0 ),
                         ( 0, 0, 1 ) ) ]
              }
            ]
                          },
                    
                    '-3m':
                        { 'rotation_list':
                              [ 'E', 'C3', 'C2', 'i', 'S6', 'sgd' ],
                          'character_table':
                              { 'A1g': [ 1, 1, 1, 1, 1, 1 ],
                                'A2g': [ 1, 1,-1, 1, 1,-1 ],
                                'Eg' : [ 2,-1, 0, 2,-1, 0 ],
                                'A1u': [ 1, 1, 1,-1,-1,-1 ],
                                'A2u': [ 1, 1,-1,-1,-1, 1 ],
                                'Eu' : [ 2,-1, 0,-2, 1, 0 ] },
                          'mapping_table': [
            { 'E'  : [ ( ( 1, 0, 0 ),
                         ( 0, 1, 0 ),
                         ( 0, 0, 1 ) ) ],
              'C3' : [ ( ( 0,-1, 0 ),
                         ( 1,-1, 0 ),
                         ( 0, 0, 1 ) ),
                       ( (-1, 1, 0 ),
                         (-1, 0, 0 ),
                         ( 0, 0, 1 ) ) ],
              'C2' : [ ( ( 0,-1, 0 ),
                         (-1, 0, 0 ),
                         ( 0, 0,-1 ) ),
                       ( (-1, 1, 0 ),
                         ( 0, 1, 0 ),
                         ( 0, 0,-1 ) ),
                       ( ( 1, 0, 0 ),
                         ( 1,-1, 0 ),
                         ( 0, 0,-1 ) ) ],
              'i'  : [ ( (-1, 0, 0 ),
                         ( 0,-1, 0 ),
                         ( 0, 0,-1 ) ) ],
              'S6' : [ ( ( 0, 1, 0 ),
                         (-1, 1, 0 ),
                         ( 0, 0,-1 ) ),
                       ( ( 1,-1, 0 ),
                         ( 1, 0, 0 ),
                         ( 0, 0,-1 ) ) ],
              'sgd': [ ( ( 0, 1, 0 ),
                         ( 1, 0, 0 ),
                         ( 0, 0, 1 ) ),
                       ( ( 1,-1, 0 ),
                         ( 0,-1, 0 ),
                         ( 0, 0, 1 ) ),
                       ( (-1, 0, 0 ),
                         (-1, 1, 0 ),
                         ( 0, 0, 1 ) ) ]
              },
            { 'E'  : [ ( ( 1, 0, 0 ),
                         ( 0, 1, 0 ),
                         ( 0, 0, 1 ) ) ],
              'C3' : [ ( ( 0,-1, 0 ),
                         ( 1,-1, 0 ),
                         ( 0, 0, 1 ) ),
                       ( (-1, 1, 0 ),
                         (-1, 0, 0 ),
                         ( 0, 0, 1 ) ) ],
              'C2' : [ ( ( 0, 1, 0 ),
                         ( 1, 0, 0 ),
                         ( 0, 0,-1 ) ),
                       ( ( 1,-1, 0 ),
                         ( 0,-1, 0 ),
                         ( 0, 0,-1 ) ),
                       ( (-1, 0, 0 ),
                         (-1, 1, 0 ),
                         ( 0, 0,-1 ) ) ],
              'i'  : [ ( (-1, 0, 0 ),
                         ( 0,-1, 0 ),
                         ( 0, 0,-1 ) ) ],
              'S6' : [ ( ( 0, 1, 0 ),
                         (-1, 1, 0 ),
                         ( 0, 0,-1 ) ),
                       ( ( 1,-1, 0 ),
                         ( 1, 0, 0 ),
                         ( 0, 0,-1 ) ) ],
              'sgd': [ ( ( 0,-1, 0 ),
                         (-1, 0, 0 ),
                         ( 0, 0, 1 ) ),
                       ( (-1, 1, 0 ),
                         ( 0, 1, 0 ),
                         ( 0, 0, 1 ) ),
                       ( ( 1, 0, 0 ),
                         ( 1,-1, 0 ),
                         ( 0, 0, 1 ) ) ]
              }
            ]
                          },
                    '32':
                        { 'rotation_list':
                              [ 'E', 'C3', 'C2\'' ],
                          'character_table':
                              { 'A1': [ 1, 1, 1 ],
                                'A2': [ 1, 1,-1 ],
                                'E' : [ 2,-1, 0 ] },
                          'mapping_table': [
            { 'E'  : [ ( ( 1, 0, 0 ),
                         ( 0, 1, 0 ),
                         ( 0, 0, 1 ) ) ],
              'C3' : [ ( ( 0,-1, 0 ),
                         ( 1,-1, 0 ),
                         ( 0, 0, 1 ) ),
                       ( (-1, 1, 0 ),
                         (-1, 0, 0 ),
                         ( 0, 0, 1 ) ) ],
              'C2\'' : [ ( ( 0,-1, 0 ),
                           (-1, 0, 0 ),
                           ( 0, 0,-1 ) ),
                         ( (-1, 1, 0 ),
                           ( 0, 1, 0 ),
                           ( 0, 0,-1 ) ),
                         ( ( 1, 0, 0 ),
                           ( 1,-1, 0 ),
                           ( 0, 0,-1 ) ) ]
              }
            ]
                          }
                    }


r2h_observe_R3 = [[-1, 1, 1],
                  [ 0,-1, 1],
                  [ 1, 0, 1]]
r2h_reverse_R3 = [[ 1,-1, 1],
                  [ 0, 1, 1],
                  [-1, 0, 1]]
r2h = r2h_observe_R3

class CharacterTable:
    def __init__(self,
                 dynamical_matrix,
                 q,
                 primitive,
                 factor=VaspToTHz,
                 symprec=1e-5,
                 degeneracy_tolerance=1e-5,
                 log_level=0):
        self._factor = factor
        self._log_level = log_level

        self._q = np.array(q)
        self._degeneracy_tolerance = degeneracy_tolerance
        self._symprec = symprec
        self._primitive = primitive


        self._eigvecs, self._freqs = self._get_eigenvectors(dynamical_matrix)
        self._symmetry_dataset = Symmetry(self._primitive,
                                          self._symprec).get_dataset()

        (self._rotations_at_q,
         self._translations_at_q,
         self._q_rotations) = self._get_rotations_at_q()

        self._g = len(self._rotations_at_q)

        (self._pointgroup_symbol,
         self._transformation_matrix,
         self._conventional_rotations) = self._get_conventional_rotations()

        self._matrices = self._get_mapping_matrix()
        self._degenerate_sets = self._get_degenerate_sets()
        self._irreps = self._get_ir_representations()
        self._characters, self._irrep_dims = self._get_characters()

        self._ir_labels = None
        if self._pointgroup_symbol in character_table.keys():
            self._rotation_symbols = self._get_rotation_symbols()
            if (abs(self._q) < self._symprec).all() and self._rotation_symbols:
                self._ir_labels = self._get_ir_labels()
            else:
                print "Database for this point group is not preprared."
        else:
            self._rotation_symbols = None

    def get_matrices(self):
        return self._matrices

    def get_eigenvectors(self):
        return self._eigvecs

    def get_ir_representations(self):
        return self._irreps

    def get_rotation_symbols(self):
        return self._rotation_symbols

    def get_projection_operators(self, idx_irrep, i=None, j=None):
        if i == None or j == None:
            return self._get_character_projection_operators(idx_irrep)
        else:
            return self._get_projection_operators(idx_irrep, i, j)

    def show(self, show_irreps=False):
        self._show(show_irreps)

    def write_yaml(self, show_irreps=False):
        self._write_yaml(show_irreps)

    def _get_eigenvectors(self, dm):
        dm.set_dynamical_matrix(self._q)
        eigvals, eigvecs = np.linalg.eigh(dm.get_dynamical_matrix())
        freqs = np.sqrt(abs(eigvals)) * np.sign(eigvals) * self._factor
        return eigvecs, freqs

    def _get_rotations_at_q(self):
        rotations_at_q = []
        trans_at_q = []
        q_rotations = []
        lat = self._primitive.get_cell().T
        metric = np.dot(lat.T, lat)
        
        for r, t in zip(self._symmetry_dataset['rotations'],
                        self._symmetry_dataset['translations']):
            r_q = similarity_transformation(metric, r)
            diff = np.dot(r_q, self._q) - self._q
            if (abs(diff - diff.round()) < self._symprec).all():
                rotations_at_q.append(r)
                trans_at_q.append(t)
                q_rotations.append(r_q)

        return (np.array(rotations_at_q),
                np.array(trans_at_q),
                np.array(q_rotations))

    def _get_conventional_rotations(self):
        spacegroup_symbol = self._symmetry_dataset['international'][0]
        rotations = self._rotations_at_q.copy()
        pointgroup = get_pointgroup(rotations)
        pointgroup_symbol = pointgroup[0]
        transformation_matrix = pointgroup[1]

        # Set transfomration matrix pR --> hR
        if spacegroup_symbol == 'R':
            transformation_matrix = np.dot(transformation_matrix, r2h)

        # Rotation matrices for the conventional lattice vectors
        conventional_rotations = self._transform_rotations(
            transformation_matrix, rotations)

        return (pointgroup_symbol,
                transformation_matrix,
                conventional_rotations)

    def _transform_rotations(self, tmat, rotations):
        trans_rots = []

        for r in rotations:
            r_conv = similarity_transformation(np.linalg.inv(tmat), r)
            trans_rots.append(r_conv.round().astype(int))

        return np.array(trans_rots)

    def _get_mapping_matrix(self):
        matrices = []
        
        for (r, t, r_q) in zip(self._rotations_at_q,
                               self._translations_at_q,
                               self._q_rotations):
    
            lat = self._primitive.get_cell().T
            r_cart = similarity_transformation(lat, r)
    
            perm_mat = self._get_modified_permutation_matrix(r, t, r_q)
            matrices.append(np.kron(perm_mat, r_cart))

        return np.array(matrices)

    def _get_characters(self):
        import sys
        characters = []
        irrep_dims = []
        for irrep_Rs in self._irreps:
            characters.append([np.trace(rep) for rep in irrep_Rs])
            irrep_dims.append(len(irrep_Rs[0]))
        return np.array(characters), np.array(irrep_dims)

    def _get_modified_permutation_matrix(self, r, t, r_q):
        num_atom = self._primitive.get_number_of_atoms()
        pos = self._primitive.get_scaled_positions()
        matrix = np.zeros((num_atom, num_atom), dtype=complex)
        for i, p1 in enumerate(pos):
            p_rot = np.dot(r, p1) + t
            for j, p2 in enumerate(pos):
                diff = p_rot - p2
                if (abs(diff - diff.round()) < self._symprec).all():
                    phase_factor = np.dot(p1 - p_rot, self._q)
                    matrix[j, i] = np.exp(2j * np.pi * phase_factor)

        return matrix
    
    def _get_degenerate_sets(self):
        degenerates = []
        indices_done = []
        for i, f1 in enumerate(self._freqs):
            if i in indices_done:
                continue
            deg_set = []
            for j, f2 in enumerate(self._freqs):
                if abs(f2 - f1) < self._degeneracy_tolerance:
                    deg_set.append(j)
                    indices_done.append(j)
            degenerates.append(deg_set)

        return degenerates

    def _get_ir_representations(self):
        eigvecs = self._eigvecs.T
        irrep = []
        for band_indices in self._degenerate_sets:
            irrep_Rs = []
            for mat in self._matrices:
                l = len(band_indices)

                if l == 1:
                    vec = eigvecs[band_indices[0]]
                    irrep_Rs.append([[np.vdot(vec, np.dot(mat, vec))]])
                    continue
                
                irrep_R = np.zeros((l, l), dtype=complex)
                for i, b_i in enumerate(band_indices):
                    vec_i = eigvecs[b_i]
                    for j, b_j in enumerate(band_indices):
                        vec_j = eigvecs[b_j]
                        irrep_R[i, j] = np.vdot(vec_i, np.dot(mat, vec_j))
                irrep_Rs.append(irrep_R)

            irrep.append(irrep_Rs)

        return irrep

    def _get_character_projection_operators(self, idx_irrep):
        dim = self._irrep_dims[idx_irrep]
        chars = self._characters[idx_irrep]
        return np.sum([mat * char.conj() for mat, char
                       in zip(self._matrices, chars)], axis=0) * dim / self._g

    def _get_projection_operators(self, idx_irrep, i, j):
        dim = self._irrep_dims[idx_irrep]
        return np.sum([mat * r[i, j].conj() for mat, r
                       in zip(self._matrices, self._irreps[idx_irrep])],
                      axis=0) * dim / self._g
    
    def _get_rotation_symbols(self):
        ptg = self._pointgroup_symbol
        for mapping_table in character_table[ptg]['mapping_table']:
            rotation_symbols = []
            for r in self._conventional_rotations:
                symbol = get_rotation_symbol(r, mapping_table)
                rotation_symbols.append(symbol)

            if not False in rotation_symbols:
                break

        if False in rotation_symbols:
            return None
        else:
            return rotation_symbols

    def _get_ir_labels(self):
        ir_labels = []
        rot_list = character_table[self._pointgroup_symbol]['rotation_list']
        char_table = character_table[self._pointgroup_symbol]['character_table']
        for chars, deg_set in zip(self._characters, self._degenerate_sets):
            chars_ordered = np.zeros(len(rot_list), dtype=complex)
            for rs, ch in zip(self._rotation_symbols, chars):
                chars_ordered[rot_list.index(rs)] += ch

            for i, rl in enumerate(rot_list):
                chars_ordered[i] /= len(
                    character_table[self._pointgroup_symbol]['mapping_table'][0][rl])

            found = False
            for ct_label in char_table.keys():
                if (abs(chars_ordered - np.array(char_table[ct_label])) <
                    self._symprec).all():
                    ir_labels.append(ct_label)
                    found = True
                    break
                
            if not found:
                ir_labels.append(None)

            if self._log_level > 1:
                for v in chars_ordered:
                    print "%5.2f" % v,
                if found:
                    print ct_label
                else:
                    print "Not found"
                
        return ir_labels

    def _show(self, show_irreps):
        print
        print "-----------------"
        print " Character table"
        print "-----------------"
        print "q-point:", self._q
        print "Point group:", self._pointgroup_symbol
        print
        print "Original rotation matrices:"
        print
        print_rotations(self._rotations_at_q)

        print "Transformation matrix:"
        print
        for v in self._transformation_matrix:
            print "%6.3f %6.3f %6.3f" % tuple(v)
        print
        print "Rotation matrices by transformation matrix:"
        print
        print_rotations(self._conventional_rotations,
                        self._rotation_symbols)
        print "Character table:"
        print
        for i, deg_set in enumerate(self._degenerate_sets):
            print "%3d (%8.3f):" % (deg_set[0] + 1, self._freqs[deg_set[0]]),
            if self._ir_labels==None:
                print
            else:
                print self._ir_labels[i]
            print_characters(self._characters[i])

            print

        if show_irreps:
            self._show_irreps()
    
    def _show_irreps(self):
        print "IR representations:"
        print
        
        for i, (deg_set, irrep_Rs) in enumerate(zip(self._degenerate_sets,
                                                    self._irreps)):
            print "%3d (%8.3f):" % (deg_set[0] + 1, self._freqs[deg_set[0]])
            print
            for j, irrep_R in enumerate(irrep_Rs):
                for k in range(len(irrep_R)):
                    print "    ",
                    for l in range(len(irrep_R)):
                        if irrep_R[k][l].real > 0:
                            sign_r = " "
                        else:
                            sign_r = "-"
                        
                        if irrep_R[k][l].imag > 0:
                            sign_i = "+"
                        else:
                            sign_i = "-"

                        if k == 0:
                            str_index = "%2d" % (j + 1)
                        else:
                            str_index = "  "
                            
                        if l > 0:
                            str_index = ''

                        print "%s (%s%5.3f %s%5.3fi)" % (
                            str_index,
                            sign_r, abs(irrep_R[k][l].real),
                            sign_i, abs(irrep_R[k][l].imag)),
                    print
                if len(irrep_R) > 1:
                    print
            if len(irrep_R) == 1:
                print

    def _write_yaml(self, show_irreps):
        f = open("character_table.yaml", 'w')
        f.write("q-position: [ %12.7f, %12.7f, %12.7f ]\n" % tuple(self._q))
        f.write("point_group: %s\n" % self._pointgroup_symbol)
        f.write("transformation_matrix:\n")
        for v in self._transformation_matrix:
            f.write("- [ %10.7f, %10.7f, %10.7f ]\n" % tuple(v))
        f.write("rotations:\n")
        for i, r in enumerate(self._conventional_rotations):
            if self._rotation_symbols:
                f.write("- symbol: %s\n" % self._rotation_symbols[i])
            f.write("  representation:\n")
            for v in r:
                f.write("  - [ %2d, %2d, %2d ]\n" % tuple(v))
        f.write("\n")
        f.write("character_table:\n")
        for i, deg_set in enumerate(self._degenerate_sets):
            f.write("- frequency: %-15.10f\n" % self._freqs[deg_set[0]])
            if self._ir_labels:
                f.write("  ir_label: %s\n" % self._ir_labels[i])
            f.write("  characters: [ ")
            chars = self._characters[i]
            for chi in chars[:-1]:
                f.write("%2.0f, " % chi.real)
            f.write("%2.0f ]\n" % chars[-1].real)

        if show_irreps:
            self._write_yaml_irreps(f)
            
        f.close()

    def _write_yaml_irreps(self, file_pointer):
        f = file_pointer
        if not self._irreps:
            self._irrep = self._get_ir_representations()

        f.write("\n")
        f.write("irreps:\n")
        for i, (deg_set, irrep_Rs) in enumerate(
            zip(self._degenerate_sets, self._irreps)):
            f.write("- # %d\n" % (i + 1))
            for j, irrep_R in enumerate(irrep_Rs):
                if self._rotation_symbols:
                    symbol = self._rotation_symbols[j]
                else:
                    symbol = ''
                if len(deg_set) > 1:
                    f.write("  - # %d %s\n" % (j + 1, symbol))
                    for k, v in enumerate(irrep_R):
                        f.write("    - [ ")
                        for x in v[:-1]:
                            f.write("%10.7f, %10.7f,   " % (x.real, x.imag))
                        f.write("%10.7f, %10.7f ] # (" %
                                (v[-1].real, v[-1].imag))
                        
                        f.write(("%5.0f" * len(v)) %
                                tuple((np.angle(v) / np.pi * 180) % 360))
                        f.write(")\n")
                else:
                    x = irrep_R[0][0]
                    f.write("  - [ [ %10.7f, %10.7f ] ] # (%3.0f) %d %s\n" %
                            (x.real, x.imag,
                             (np.angle(x) / np.pi * 180) % 360, j + 1, symbol))
                
        pass
                
def get_rotation_symbol(rotation, mapping_table):
    for k, v in mapping_table.iteritems():
        for r in v:
            if (r == rotation).all():
                return k
    return False

def print_characters(characters, width=8):
    print "   ",
    for i, c in enumerate(characters):
        print "%6.3f" % c.real,
        if (i + 1) % width == 0 and i + 1 < len(characters):
            print
            print "   ",
    print

def print_rotations(rotations, rotation_symbols=None, width=6):
    for i in range(len(rotations) // width):
        if rotation_symbols == None:
            print ("    %2d    " * width) % \
                tuple(np.arange(i * width, (i + 1) * width) + 1)
        else:
            for k in range(width):
                rot_symbol = rotation_symbols[i * width + k]
                if len(rot_symbol) < 3:
                    print "    %2s   " % rot_symbol,
                else:
                    print "   %4s  " % rot_symbol,
            print
        print " -------- " * width
        for j in range(3):
            for k in range(width):
                print (" %2d %2d %2d") % tuple(rotations[i * width + k][j]),
            print
        print
    
    num_rest = len(rotations) % width
    if num_rest > 0:
        i = len(rotations) // width
        if rotation_symbols == None:
            print ("    %2d    " * num_rest) % \
                tuple(np.arange(i * width, i * width + num_rest) + 1)
        else:
            for k in range(num_rest):
                rot_symbol = rotation_symbols[i * width + k]
                if len(rot_symbol) < 3:
                    print "    %2s   " % rot_symbol,
                else:
                    print "   %4s  " % rot_symbol,
            print
        print " -------- " * num_rest
        for j in range(3):
            for k in range(num_rest):
                print (" %2d %2d %2d") % tuple(rotations[i * width + k][j]),
            print
        print

