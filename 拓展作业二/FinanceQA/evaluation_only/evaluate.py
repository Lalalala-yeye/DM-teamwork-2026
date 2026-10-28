#!/usr/bin/env python3
"""Evaluate saved answers using the original DDR-Bench 10-K support prompt."""
import argparse
import json
import os
from pathlib import Path
import urllib.request

LABELS = ('CORRECT_INFO', 'INCORRECT_INFO', 'INSUFFICIENT_INFO')


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def load_array(path):
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, list):
        raise ValueError(f'Expected a JSON array: {path}')
    return data


def index_predictions(predictions, expected_ids):
    result = {}
    for item in predictions:
        if not isinstance(item, dict) or not isinstance(item.get('question_id'), str) or not isinstance(item.get('answer'), str):
            raise ValueError('Each prediction needs a string question_id and answer')
        qid = item['question_id']
        if qid not in expected_ids or qid in result:
            raise ValueError(f'Unknown or duplicate question_id: {qid}')
        result[qid] = item
    return result


def normalize_judgment(data):
    if not isinstance(data, dict) or data.get('context_quality') not in LABELS:
        raise ValueError('Judge must return an official context_quality label')
    if any(not isinstance(data.get(key), str) for key in ('evidence_text', 'reasoning')):
        raise ValueError('Judge must return evidence_text and reasoning strings')
    return {key: data[key] for key in ('context_quality', 'evidence_text', 'reasoning')}


def summarize(results, expected_count):
    if expected_count == 0 or len(results) != expected_count:
        raise ValueError('Summary denominator must include all expected questions')
    counts = {label: sum(r.get('context_quality') == label for r in results) for label in LABELS}
    failed = sum(r.get('context_quality') == 'API_FAILED' for r in results)
    pending = any(r.get('context_quality') not in (*LABELS, 'API_FAILED') for r in results)
    return {'expected_questions': expected_count,
            'missing_predictions': sum(r.get('status') == 'MISSING_PREDICTION' for r in results),
            'empty_answers': sum(r.get('status') == 'EMPTY_ANSWER' for r in results),
            'correct_info': counts['CORRECT_INFO'], 'incorrect_info': counts['INCORRECT_INFO'],
            'insufficient_info': counts['INSUFFICIENT_INFO'], 'api_failed': failed,
            'evaluation_complete': not pending and failed == 0,
            'support_percentage': None if pending else counts['CORRECT_INFO'] / expected_count * 100,
            'incorrect_percentage': None if pending else counts['INCORRECT_INFO'] / expected_count * 100,
            'insufficient_percentage': None if pending else counts['INSUFFICIENT_INFO'] / expected_count * 100,
            'api_failed_percentage': None if pending else failed / expected_count * 100}


def call_judge(url, model, messages):
    payload = json.dumps({'model': model, 'temperature': 0, 'messages': messages}).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    key = os.environ.get('LLM_API_KEY')
    if key:
        headers['Authorization'] = 'Bearer ' + key
    request = urllib.request.Request(url, data=payload, headers=headers, method='POST')
    with urllib.request.urlopen(request, timeout=60) as response:
        envelope = json.load(response)
    content = envelope['choices'][0]['message']['content']
    text = content.strip()
    if text.startswith('```') and text.endswith('```'):
        text = text.split('\n', 1)[1].rsplit('```', 1)[0].strip()
    return json.loads(text), content


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--split', choices=['train', 'test'], required=True)
    parser.add_argument('--predictions', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--limit', type=int, help='Optional positive train subset; test always uses all questions')
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--check-only', action='store_true', help='Check prediction format only; no model call')
    modes.add_argument('--export-requests', type=Path, help='Export judge requests without calling a model')
    modes.add_argument('--judge-url', help='Full /v1/chat/completions endpoint; only this mode calls a model')
    parser.add_argument('--model')
    args = parser.parse_args()
    if args.judge_url and not args.model:
        parser.error('--judge-url requires --model')
    if args.limit is not None and (args.split == 'test' or args.limit < 1):
        parser.error('--limit is only for positive train subsets')
    if args.output.exists() or (args.export_requests and args.export_requests.exists()):
        parser.error('Use new output paths; evaluation does not overwrite earlier results')
    if args.export_requests and args.output.resolve() == args.export_requests.resolve():
        parser.error('Output report and request export must use different paths')
    package = Path(__file__).resolve().parent.parent
    work = package / 'agent_workspace'
    questions = load_array(work / args.split / 'questions.json')
    source_count = len(questions)
    if args.limit:
        questions = questions[:args.limit]
    expected_ids = {q['question_id'] for q in questions}
    if not questions or len(expected_ids) != len(questions):
        raise ValueError('Question list must be non-empty with unique question IDs')
    predictions = index_predictions(load_array(args.predictions), expected_ids)
    refs, system, template = {}, '', ''
    if not args.check_only:
        reference_file = (work / 'train/reference_answers.json' if args.split == 'train'
                          else package / 'evaluation_only/test_reference_answers.json')
        rows = load_array(reference_file)
        refs = {r['question_id']: r for r in rows}
        if len(refs) != len(rows):
            raise ValueError('Reference answers have duplicate question IDs')
        system = (package / 'evaluation_only/evaluator_system.txt').read_text(encoding='utf-8')
        template = (package / 'evaluation_only/evaluator_user.txt').read_text(encoding='utf-8')
    results, requests, model_calls = [], [], 0
    for task in questions:
        qid = task['question_id']
        result = {'question_id': qid, 'company_cik': task['company_cik']}
        prediction = predictions.get(qid)
        if prediction is None or not prediction['answer'].strip():
            result.update(status='MISSING_PREDICTION' if prediction is None else 'EMPTY_ANSWER',
                          context_quality='INSUFFICIENT_INFO', evidence_text='', reasoning='No submitted answer.')
        elif args.check_only:
            result.update(status='CHECKED_ONLY', context_quality=None)
        else:
            reference = refs[qid]
            if reference['question'] != task['question']:
                raise ValueError('Question differs from original reference')
            prompt = template.format(context=prediction['answer'], question=task['question'], ground_truth=reference['answer'])
            messages = [{'role': 'system', 'content': system}, {'role': 'user', 'content': prompt}]
            if args.export_requests:
                requests.append({'question_id': qid, 'messages': messages})
                result.update(status='WAITING_FOR_JUDGE', context_quality=None)
            else:
                model_calls += 1
                try:
                    parsed, raw = call_judge(args.judge_url, args.model, messages)
                    result.update(status='SCORED', **normalize_judgment(parsed), raw_judge_response=raw)
                except Exception as exc:
                    result.update(status='JUDGE_ERROR', context_quality='API_FAILED', error=f'{type(exc).__name__}: {exc}')
        results.append(result)
    report = {'split': args.split, 'source_question_count': source_count,
              'subset_evaluation': len(questions) < source_count,
              'mode': 'check_only' if args.check_only else ('export_requests' if args.export_requests else 'judge_api'),
              'model_calls': model_calls, 'judge_model': args.model,
              **summarize(results, len(questions)), 'results': results}
    per_company = {}
    for cik in dict.fromkeys(q['company_cik'] for q in questions):
        rows = [r for r in results if r['company_cik'] == cik]
        per_company[cik] = summarize(rows, len(rows))
    report['per_company'] = per_company
    percentages = [s['support_percentage'] for s in per_company.values()]
    report['average_support_percentage'] = (sum(percentages) / len(percentages)
                                            if all(v is not None for v in percentages) else None)
    if args.check_only or args.export_requests:
        report.update(evaluation_complete=False, support_percentage=None, average_support_percentage=None,
                      incorrect_percentage=None, insufficient_percentage=None, api_failed_percentage=None)
        for stats in per_company.values():
            stats.update(evaluation_complete=False, support_percentage=None, incorrect_percentage=None,
                         insufficient_percentage=None, api_failed_percentage=None)
    if args.export_requests:
        write(args.export_requests, requests)
    write(args.output, report)
    print(json.dumps({k: report[k] for k in ('split', 'mode', 'expected_questions', 'evaluation_complete',
                                           'support_percentage', 'average_support_percentage', 'model_calls')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
