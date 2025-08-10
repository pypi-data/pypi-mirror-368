import unittest
import numpy as np
from genomehouse import ml_models

class TestMLModels(unittest.TestCase):
    def test_extract_features(self):
        seqs = ["ATGCGA", "TTAGGC"]
        feats = ml_models.extract_features(seqs)
        self.assertEqual(feats.shape, (2, 2))
    def test_train_classifier(self):
        X = np.array([[0.5, 6], [0.33, 6]])
        y = np.array([1, 0])
        model, acc, report = ml_models.train_classifier(X, y)
        self.assertTrue(acc >= 0)
        self.assertIn("precision", report)
    def test_save_and_load_model(self):
        X = np.array([[0.5, 6], [0.33, 6]])
        y = np.array([1, 0])
        model, _, _ = ml_models.train_classifier(X, y)
        ml_models.save_model(model, "test_model.joblib")
        loaded = ml_models.load_model("test_model.joblib")
        self.assertIsNotNone(loaded)

if __name__ == "__main__":
    unittest.main()
