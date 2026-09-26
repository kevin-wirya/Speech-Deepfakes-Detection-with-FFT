"""Evaluate the detector on a labeled directory and write interview-ready artifacts.

Example:
    python evaluate.py --data-dir ../../test --reference-stats reference_stats.json
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from detector import DeepfakeDetector


SUPPORTED_EXTENSIONS = {'.wav', '.mp3'}


def collect_samples(data_dir):
    samples = []
    for filepath in sorted(Path(data_dir).rglob('*')):
        if filepath.is_file() and filepath.suffix.lower() in SUPPORTED_EXTENSIONS:
            relative_parts = filepath.relative_to(data_dir).parts
            condition = relative_parts[0] if len(relative_parts) > 1 else 'default'
            is_human = condition.lower() == 'human'
            samples.append({
                'path': filepath,
                'label': 0 if is_human else 1,
                'condition': condition,
            })
    if not samples:
        raise ValueError(f'No WAV or MP3 files found in {data_dir}')
    return samples


def percentile(values, value):
    return round(float(np.percentile(values, value)), 2) if values else None


def evaluate_samples(detector, samples):
    y_true, y_pred, y_score = [], [], []
    rows = []
    for sample in samples:
        started_at = time.perf_counter()
        try:
            result = detector.predict(str(sample['path']))
            latency_ms = (time.perf_counter() - started_at) * 1000
            distance_total = result['distance_to_human'] + result['distance_to_ai']
            ai_score = result['distance_to_human'] / distance_total if distance_total else 0.5
            y_true.append(sample['label'])
            y_pred.append(1 if result['prediction'] == 'ai' else 0)
            y_score.append(ai_score)
            rows.append({
                'file': str(sample['path']),
                'condition': sample['condition'],
                'label': sample['label'],
                'prediction': y_pred[-1],
                'score_ai': round(float(ai_score), 6),
                'latency_ms': round(float(latency_ms), 2),
            })
        except Exception as error:
            rows.append({'file': str(sample['path']), 'error': str(error)})

    if not y_true:
        raise RuntimeError('No files could be evaluated successfully.')
    return y_true, y_pred, y_score, rows


def metrics_for(y_true, y_pred, y_score):
    matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = matrix.ravel()
    metrics = {
        'accuracy': float(accuracy_score(y_true, y_pred)),
        'precision': float(precision_score(y_true, y_pred, zero_division=0)),
        'recall': float(recall_score(y_true, y_pred, zero_division=0)),
        'f1': float(f1_score(y_true, y_pred, zero_division=0)),
        'false_positive_rate': float(fp / (fp + tn)) if fp + tn else None,
        'false_negative_rate': float(fn / (fn + tp)) if fn + tp else None,
        'confusion_matrix': {'true_negative': int(tn), 'false_positive': int(fp), 'false_negative': int(fn), 'true_positive': int(tp)},
    }
    if len(set(y_true)) == 2:
        metrics['roc_auc'] = float(roc_auc_score(y_true, y_score))
        metrics['pr_auc'] = float(average_precision_score(y_true, y_score))
    else:
        metrics['roc_auc'] = None
        metrics['pr_auc'] = None
    return metrics


def write_confusion_matrix(matrix, output_path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    figure, axis = plt.subplots(figsize=(5, 4))
    image = axis.imshow(matrix, cmap='Blues')
    axis.set(xticks=[0, 1], yticks=[0, 1], xticklabels=['Human', 'AI'], yticklabels=['Human', 'AI'],
             xlabel='Predicted label', ylabel='True label', title='FFT Detector Confusion Matrix')
    for row in range(2):
        for column in range(2):
            axis.text(column, row, matrix[row, column], ha='center', va='center', color='white' if matrix[row, column] > matrix.max() / 2 else 'black')
    figure.colorbar(image, ax=axis)
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)


def write_markdown(summary, output_path):
    metrics = summary['metrics']
    lines = [
        '# Detector Evaluation', '',
        f"- Evaluated files: {summary['evaluated_files']}",
        f"- Failed files: {summary['failed_files']}",
        f"- Note: {summary['evaluation_note']}",
        f"- Latency p50/p95: {summary['latency_ms']['p50']} / {summary['latency_ms']['p95']} ms", '',
        '| Metric | Value |', '| --- | ---: |',
    ]
    for key in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc', 'pr_auc', 'false_positive_rate', 'false_negative_rate']:
        value = metrics[key]
        lines.append(f'| {key} | {"n/a" if value is None else f"{value:.4f}"} |')
    lines.extend(['', '## Condition breakdown', '', '| Condition | Files | Accuracy | AI recall |', '| --- | ---: | ---: | ---: |'])
    for condition, values in summary['condition_metrics'].items():
        lines.append(f"| {condition} | {values['files']} | {values['accuracy']:.4f} | {values['recall_ai']:.4f} |")
    output_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, required=True)
    parser.add_argument('--reference-stats', type=Path, default=Path('reference_stats.json'))
    parser.add_argument('--output-dir', type=Path, default=Path('../../evaluation'))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    detector = DeepfakeDetector(str(args.reference_stats))
    samples = collect_samples(args.data_dir)
    y_true, y_pred, y_score, rows = evaluate_samples(detector, samples)
    successful_rows = [row for row in rows if 'error' not in row]
    summary = {
        'model_version': 'fft-geometry-v1',
        'data_dir': str(args.data_dir),
        'evaluation_note': 'Benchmark on the supplied test directory; not a speaker-disjoint or generator-disjoint production estimate.',
        'evaluated_files': len(y_true),
        'failed_files': len(rows) - len(successful_rows),
        'metrics': metrics_for(y_true, y_pred, y_score),
        'latency_ms': {
            'p50': percentile([row['latency_ms'] for row in successful_rows], 50),
            'p95': percentile([row['latency_ms'] for row in successful_rows], 95),
        },
        'condition_metrics': {},
        'files': rows,
    }
    for condition in sorted({sample['condition'] for sample in samples}):
        condition_rows = [row for row in successful_rows if row['condition'] == condition]
        if condition_rows:
            condition_true = [row['label'] for row in condition_rows]
            condition_pred = [row['prediction'] for row in condition_rows]
            condition_score = [row['score_ai'] for row in condition_rows]
            condition_result = metrics_for(condition_true, condition_pred, condition_score)
            summary['condition_metrics'][condition] = {
                'files': len(condition_rows),
                'accuracy': condition_result['accuracy'],
                'recall_ai': condition_result['recall'],
            }

    matrix = np.array([[summary['metrics']['confusion_matrix']['true_negative'], summary['metrics']['confusion_matrix']['false_positive']],
                       [summary['metrics']['confusion_matrix']['false_negative'], summary['metrics']['confusion_matrix']['true_positive']]])
    (args.output_dir / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    write_confusion_matrix(matrix, args.output_dir / 'confusion_matrix.png')
    write_markdown(summary, args.output_dir / 'summary.md')
    print(f"Evaluation written to {args.output_dir.resolve()}")


if __name__ == '__main__':
    main()