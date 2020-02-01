# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2019, GEM Foundation
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake.  If not, see <http://www.gnu.org/licenses/>.

import os
import unittest
import numpy
from openquake.hazardlib.contexts import Effect

from openquake.hazardlib.pmf import PMF

from openquake.hazardlib.const import TRT
from openquake.baselib.general import DictArray

from openquake.hazardlib.contexts_ne import ContextMaker

from openquake.hazardlib.tests.gsim.mgmpe.dummy import Dummy
from openquake.hazardlib.source import NonParametricSeismicSource

from openquake.hazardlib.gsim.boore_atkinson_2008 import BooreAtkinson2008

BASE_PATH = os.path.dirname(__file__)

dists = numpy.array([0, 10, 20, 30, 40, 50])
intensities = {
    '4.5': numpy.array([1.0, .95, .7, .6, .5, .3]),
    '5.0': numpy.array([1.2, 1.1, .7, .69, .6, .5]),
    '5.5': numpy.array([1.5, 1.2, .89, .85, .82, .6]),
    '6.0': numpy.array([2.0, 1.5, .9, .85, .81, .6])}

class InstantiateContextTest(unittest.TestCase):

    def setUp(self):
        self.trt = TRT.ACTIVE_SHALLOW_CRUST
        self.gsims = [BooreAtkinson2008()]

    def test01(self):
        cm = ContextMaker(self.trt, self.gsims)
        self.assertTrue(cm.filter_distance, 'rjb')


class GetPmapTest(unittest.TestCase):

    def setUp(self):
        self.trt = TRT.ACTIVE_SHALLOW_CRUST
        # Parameters
        self.param = {}
        imtls = DictArray({'PGA': [0.1, 0.2, 0.3, 0.4],
                           'SA(0.5)': [0.1, 0.2, 0.3, 0.4, 0.5]})
        self.param['imtls'] = imtls
        # Creating ruptures
        rup1 = Dummy.get_rupture(mag=5.5)
        pmf1 = PMF([(0.2, 0), (0.8, 1)])
        rup2 = Dummy.get_rupture(mag=6.0)
        pmf2 = PMF([(0.4, 0), (0.6, 1)])
        data = [(rup1, pmf1), (rup2, pmf2)]
        # Creating non-parametric source
        self.src = NonParametricSeismicSource('1', 'test', self.trt, data)
        # Creating the sites
        self.sitesc = Dummy.get_site_collection(2, hyp_lon=0.05, hyp_lat=0.25,
                                                vs30=500., vs30measured=True,
                                                z1pt0=50.)

    def test01(self):
        gsims = [BooreAtkinson2008()]
        # Context maker
        cm = ContextMaker(self.trt, gsims, param=self.param)
        # Computing probability map
        poemap = cm.get_pmap(self.src, self.sitesc)


class EffectTestCase(unittest.TestCase):
    def test_dist_by_mag(self):
        effect = Effect(intensities, dists)
        dist = list(effect.dist_by_mag().values())
        numpy.testing.assert_allclose(dist, [50, 50, 50, 50])

        dist = list(effect.dist_by_mag(.9).values())
        numpy.testing.assert_allclose(dist, [12, 15, 19.677419, 20])

        dist = list(effect.dist_by_mag(1.1).values())
        numpy.testing.assert_allclose(dist, [0, 10, 13.225806, 16.666667])
