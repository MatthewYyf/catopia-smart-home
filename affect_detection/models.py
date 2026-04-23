"""
Cat Vocalization Classifier — Class-Specific HMM
Replication of: Ntalampiras et al., Animals 2019, 9, 543

Preprocessing: v1 (librosa MFCC + energy-based silence removal)
Classifier:    Class-Specific HMM (best performing in practice)
"""

import os
import pickle
import warnings
import numpy as np
import librosa
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict

from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

from hmmlearn import hmm

warnings.filterwarnings('ignore')
np.random.seed(42)


# ============================================================
#  CONFIGURATION
# ============================================================

DATASET_PATH = "./dataset"
CLASSES      = ["food", "isolation", "brushing"]
SR           = 8000
N_MFCC       = 13
N_MELS       = 23
FRAME_LEN    = int(0.030 * SR)   # 30 ms
HOP_LEN      = int(0.010 * SR)   # 10 ms
N_FFT        = 512

HMM_N_STATES = 4
HMM_N_MIX    = 8
HMM_N_ITER   = 25
HMM_TOL      = 0.001

N_FOLDS      = 10
OUTPUT_PATH  = "cat_classifier.pkl"


# ============================================================
#  SILENCE REMOVAL
# ============================================================

def remove_silence(y, sr, top_db=20):
    y_trimmed, _ = librosa.effects.trim(y, top_db=top_db)
    return y_trimmed if len(y_trimmed) > sr * 0.05 else y


# ============================================================
#  MFCC EXTRACTION (v1 — librosa)
# ============================================================

def extract_mfcc(y, sr=SR):
    """
    13-dim MFCC (12 coefficients + log energy) + delta/delta-delta/delta-delta-delta
    = 52-dim per frame. Matches Section 3.1.1 of the paper.
    """
    mfcc = librosa.feature.mfcc(
        y=y, sr=sr,
        n_mfcc=N_MFCC - 1,
        n_mels=N_MELS,
        n_fft=N_FFT,
        hop_length=HOP_LEN,
        win_length=FRAME_LEN,
        window='hamming'
    )
    energy    = np.log(librosa.feature.rms(
        y=y, frame_length=FRAME_LEN, hop_length=HOP_LEN
    ) + 1e-10)
    mfcc_full = np.vstack([energy, mfcc]).T          # (T, 13)

    delta1    = librosa.feature.delta(mfcc_full.T, order=1).T
    delta2    = librosa.feature.delta(mfcc_full.T, order=2).T
    delta3    = librosa.feature.delta(mfcc_full.T, order=3).T

    mfcc_full = np.hstack([mfcc_full, delta1, delta2, delta3])  # (T, 52)

    # Z-score normalise per sequence
    mfcc_full = (mfcc_full - mfcc_full.mean(axis=0)) / (mfcc_full.std(axis=0) + 1e-10)

    return mfcc_full


# ============================================================
#  DATASET LOADING
# ============================================================

def load_dataset(dataset_path, classes, sr=SR):
    file_paths = []
    dataset_path = Path(dataset_path)
    for cls in classes:
        cls_dir = dataset_path / cls
        if not cls_dir.exists():
            print(f"  ⚠️  Not found: {cls_dir}")
            continue
        files = list(cls_dir.glob("*.wav")) + list(cls_dir.glob("*.WAV"))
        for f in files:
            file_paths.append((str(f), cls))
        print(f"  {cls:12s}: {len(files):4d} files")
    print(f"\n  Total: {len(file_paths)} files")
    return file_paths


def extract_all_features(file_paths, sr=SR):
    sequences, labels = [], []
    for fpath, label in tqdm(file_paths, desc="Extracting features"):
        try:
            y, _ = librosa.load(fpath, sr=sr)
            y    = remove_silence(y, sr)
            seq  = extract_mfcc(y, sr)
            if seq.shape[0] < 5:
                continue
            sequences.append(seq)
            labels.append(label)
        except Exception as e:
            print(f"  ⚠️  Skipping {fpath}: {e}")
    return sequences, labels


# ============================================================
#  HMM TRAINING & SCORING
# ============================================================

def train_hmm(sequences, n_states=HMM_N_STATES, n_mix=HMM_N_MIX):
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=RuntimeWarning)
        model = hmm.GMMHMM(
            n_components=n_states,
            n_mix=n_mix,
            covariance_type='diag',
            n_iter=HMM_N_ITER,
            tol=HMM_TOL,
            init_params='mcw',
            params='mcwt',
            min_covar=1e-3
        )
        X_concat = np.vstack(sequences)
        lengths  = [len(s) for s in sequences]
        try:
            model.fit(X_concat, lengths)
        except Exception:
            pass
    return model


def hmm_score(model, sequence):
    try:
        return model.score(sequence)
    except Exception:
        return -np.inf


def train_class_specific_hmm(sequences, labels, classes):
    """Train one HMM per class, return dict {class_idx: GMMHMM}."""
    models = {}
    for cls in classes:
        seqs_cls = [s for s, l in zip(sequences, labels) if l == cls]
        if seqs_cls:
            models[cls] = train_hmm(seqs_cls)
            print(f"    Trained HMM for class {cls} on {len(seqs_cls)} sequences")
    return models


def predict(hmm_models, sequences):
    preds = []
    for seq in sequences:
        scores = {cls: hmm_score(m, seq) for cls, m in hmm_models.items()}
        preds.append(max(scores, key=scores.get))
    return preds


# ============================================================
#  10-FOLD CROSS VALIDATION
# ============================================================

def cross_validate(sequences, labels, n_folds=N_FOLDS):
    labels     = np.array(labels)
    skf        = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    all_preds  = []
    all_true   = []
    classes    = np.unique(labels)

    for fold, (train_idx, test_idx) in enumerate(
        tqdm(skf.split(np.zeros(len(labels)), labels),
             total=n_folds, desc="10-fold CV")
    ):
        train_seqs = [sequences[i] for i in train_idx]
        test_seqs  = [sequences[i] for i in test_idx]
        train_y    = labels[train_idx]
        test_y     = labels[test_idx]

        models = train_class_specific_hmm(train_seqs, train_y, classes)
        preds  = predict(models, test_seqs)

        all_preds.extend(preds)
        all_true.extend(test_y)

    acc = accuracy_score(all_true, all_preds) * 100
    cm  = confusion_matrix(all_true, all_preds)
    return acc, cm, all_true, all_preds


# ============================================================
#  SAVE MODEL
# ============================================================

def save_model(hmm_models, le, output_path=OUTPUT_PATH):
    """
    Save raw GMMHMM dict directly — avoids custom class pickling issues.
    """
    payload = {
        'hmm_models': hmm_models,   # {class_idx: GMMHMM}
        'le':         le,
        'classes':    CLASSES,
        'SR':         SR,
        'N_FFT':      N_FFT,
        'HOP_LEN':    HOP_LEN,
        'FRAME_LEN':  FRAME_LEN,
    }
    with open(output_path, 'wb') as f:
        pickle.dump(payload, f)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"\n✅ Model saved to {output_path} ({size_kb:.1f} KB)")


# ============================================================
#  MAIN
# ============================================================

if __name__ == '__main__':

    print("=" * 55)
    print("  Cat Vocalization Classifier — Class-Specific HMM")
    print("=" * 55)

    # 1. Load dataset
    print("\n📁 Loading dataset...")
    file_paths = load_dataset(DATASET_PATH, CLASSES)

    # 2. Extract features
    print("\n🎵 Extracting features...")
    sequences, labels_raw = extract_all_features(file_paths)

    le     = LabelEncoder()
    labels = le.fit_transform(labels_raw)
    print(f"\n  Label encoding : {dict(zip(le.classes_, le.transform(le.classes_)))}")
    print(f"  Class counts   : {np.bincount(labels)}")
    print(f"  Feature shape  : {sequences[0].shape} per sequence")

    # 3. Cross-validate
    print("\n🔁 Running 10-fold cross-validation...")
    acc, cm, all_true, all_preds = cross_validate(sequences, labels)

    # 4. Results
    print("\n" + "=" * 55)
    print(f"  Overall accuracy : {acc:.2f}%  (paper: 80.95%)")
    print("=" * 55)
    print("\nPer-class accuracy:")
    for i, cls in enumerate(le.classes_):
        row_sum = cm[i].sum()
        if row_sum > 0:
            print(f"  {cls:12s}: {cm[i, i] / row_sum * 100:.2f}%")

    print("\nConfusion matrix:")
    print(cm)

    print("\nClassification report:")
    print(classification_report(all_true, all_preds, target_names=le.classes_))

    # 5. Train final model on full dataset and save
    print("\n💾 Training final model on full dataset...")
    classes    = np.unique(labels)
    hmm_models = train_class_specific_hmm(sequences, labels, classes)
    save_model(hmm_models, le)