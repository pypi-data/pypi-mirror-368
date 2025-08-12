import unittest
import numpy as np

import sponfiss.snsfpy as sf


class TestZaidToSymbol(unittest.TestCase):
    def test_basic_zaid(self):
        # 92238 → Z=92 (U), A=238
        self.assertEqual(sf.zaid_to_symbol(92238), "U238")
        self.assertEqual(sf.zaid_to_symbol("1001"), "H1")

    def test_unknown_Z(self):
        # If Z not in periodic_table, should return "Z<Z><A>"
        self.assertEqual(sf.zaid_to_symbol(999123), "Z999123"[:len("Z999") + 3])  # interprets Z=999, A=123


class TestDecayConst(unittest.TestCase):
    def test_seconds_unit(self):
        lam = sf.decayConst(hl=10, unit="s")
        expected = np.log(2) / 10
        self.assertAlmostEqual(lam, expected, places=12)

    def test_hours_unit(self):
        lam = sf.decayConst(hl=2, unit="h")
        expected = np.log(2) / (2 * 3600)
        self.assertAlmostEqual(lam, expected, places=12)

    def test_days_years_units(self):
        lam_d = sf.decayConst(hl=1, unit="d")
        self.assertAlmostEqual(lam_d, np.log(2) / (86400), places=12)

        lam_y = sf.decayConst(hl=1, unit="y")
        self.assertAlmostEqual(lam_y, np.log(2) / (365.25 * 86400), places=12)

    def test_invalid_unit(self):
        with self.assertRaises(ValueError):
            sf.decayConst(hl=1, unit="minute")


class TestMaterialBasics(unittest.TestCase):
    def setUp(self):
        # fresh material for each test
        self.mat = sf.material(name="TestMat", density=5.0, volume=2.0)

    def test_add_and_remove_data(self):
        self.mat.addtodata("Xx123", halflife=100, BR=50, molar_mass=123.45)
        self.assertIn("Xx123", self.mat.nuclides)
        self.assertEqual(self.mat.nuclides["Xx123"]["BR"], 50)

        # remove existing
        self.mat.removedata("Xx123")
        self.assertNotIn("Xx123", self.mat.nuclides)

        # removing non-existent should KeyError
        with self.assertRaises(KeyError):
            self.mat.removedata("NoSuchNuclide")

    def test_addnuclei_formats(self):
        # atom fraction format
        self.mat.addnuclei("U235", frac=0.7, Format="nuclide")
        self.assertIn("U235", self.mat.composition)
        self.assertEqual(self.mat.composition["U235"], 0.7)

        # ZAID format
        self.mat.addnuclei(92238, frac=0.3, Format="ZAID")
        self.assertIn("U238", self.mat.composition)
        self.assertEqual(self.mat.composition["U238"], 0.3)

        # invalid format
        with self.assertRaises(ValueError):
            self.mat.addnuclei("U235", frac=1.0, Format="foo")


class TestSpontaneousFission(unittest.TestCase):
    def test_sponfiss_atomfrac_no_volume(self):
        m = sf.material(name="Simple", density=10.0, volume=None)
        
        m.addnuclei("Cf252", frac=1.0, Format="nuclide")
        
        hl = m.nuclides["Cf252"]["half_life"]
        BR = m.nuclides["Cf252"]["BR"] / 1000.0
        var1 = (m.density * 1.0 * 6.02214076e23) / m.nuclides["Cf252"]["molar_mass"]
        expected = sf.decayConst(hl, unit="s") * BR * var1

        result = m.sponfiss(unit="AtomFrac")
        self.assertAlmostEqual(result, expected, places=6)

    def test_sponfiss_with_volume(self):
        m = sf.material(name="VolMat", density=1.0, volume=0.5)
        m.addnuclei("U238", frac=1.0, Format="nuclide")
        hl = m.nuclides["U238"]["half_life"]
        BR = m.nuclides["U238"]["BR"] / 1000.0
        var1 = (m.density * 1.0 * 6.02214076e23) / m.nuclides["U238"]["molar_mass"]
        base_rate = sf.decayConst(hl) * BR * var1
        expected = base_rate * 0.5

        result = m.sponfiss(unit="AtomFrac")
        self.assertAlmostEqual(result, expected, places=6)

    def test_invalid_sponfiss_unit(self):
        m = sf.material()
        with self.assertRaises(ValueError):
            m.sponfiss(unit="weird")

if __name__ == "__main__":
    unittest.main()
