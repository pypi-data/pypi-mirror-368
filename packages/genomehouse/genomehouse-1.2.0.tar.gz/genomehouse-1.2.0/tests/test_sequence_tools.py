import unittest
from genomehouse import sequence_tools

class TestSequenceTools(unittest.TestCase):
    def test_reverse_complement_dna(self):
        self.assertEqual(sequence_tools.reverse_complement("ATGC"), "GCAT")
    def test_reverse_complement_rna(self):
        self.assertEqual(sequence_tools.reverse_complement("AUGC", seq_type="RNA"), "GCAU")
    def test_find_motif(self):
        self.assertEqual(sequence_tools.find_motif("ATGCGATG", "ATG"), [0, 5])
    def test_gc_content(self):
        self.assertAlmostEqual(sequence_tools.gc_content("GGCCAA"), 66.666666, places=4)
    def test_translate(self):
        self.assertEqual(sequence_tools.translate("ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG"), "MAIVMGR*KGAR*")

if __name__ == "__main__":
    unittest.main()
