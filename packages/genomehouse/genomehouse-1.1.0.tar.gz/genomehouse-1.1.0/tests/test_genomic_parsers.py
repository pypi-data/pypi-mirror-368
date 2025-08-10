import unittest
import tempfile
import os
from genomehouse import genomic_parsers

class TestGenomicParsers(unittest.TestCase):
    def setUp(self):
        self.fasta = tempfile.NamedTemporaryFile(delete=False, mode='w+')
        self.fasta.write(">seq1\nATGCGA\n>seq2\nTTAGGC\n")
        self.fasta.close()
        self.fastq = tempfile.NamedTemporaryFile(delete=False, mode='w+')
        self.fastq.write("@id1\nATGCGA\n+\nIIIIII\n@id2\nTTAGGC\n+\nIIIIII\n")
        self.fastq.close()
        self.vcf = tempfile.NamedTemporaryFile(delete=False, mode='w+')
        self.vcf.write("##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\nchr1\t123\trs1\tA\tG\t99\tPASS\tDP=100\n")
        self.vcf.close()
        self.gff = tempfile.NamedTemporaryFile(delete=False, mode='w+')
        self.gff.write("chr1\tsource\tgene\t1\t1000\t.\t+\t.\tID=gene1\n")
        self.gff.close()
    def tearDown(self):
        os.unlink(self.fasta.name)
        os.unlink(self.fastq.name)
        os.unlink(self.vcf.name)
        os.unlink(self.gff.name)
    def test_parse_fasta(self):
        records = list(genomic_parsers.parse_fasta(self.fasta.name))
        self.assertEqual(records, [("seq1", "ATGCGA"), ("seq2", "TTAGGC")])
    def test_parse_fastq(self):
        records = list(genomic_parsers.parse_fastq(self.fastq.name))
        self.assertEqual(records[0]['id'], "id1")
        self.assertEqual(records[1]['seq'], "TTAGGC")
    def test_parse_vcf(self):
        records = list(genomic_parsers.parse_vcf(self.vcf.name))
        self.assertEqual(records[0]['CHROM'], "chr1")
        self.assertEqual(records[0]['ID'], "rs1")
    def test_parse_gff(self):
        records = list(genomic_parsers.parse_gff(self.gff.name))
        self.assertEqual(records[0]['seqid'], "chr1")
        self.assertEqual(records[0]['attributes'], "ID=gene1")

if __name__ == "__main__":
    unittest.main()
