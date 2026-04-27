#!/bin/bash
# Run weekly policy distillation - cards, signals, digest
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${REPO_ROOT}/.venv/bin/activate"

WEEK=$(date +%Y_W%V)
REPORT_DIR="${REPO_ROOT}/reports"
mkdir -p "${REPORT_DIR}"

python -c "
from china_policy_skill.distill.make_file_card import FileCardMaker
maker = FileCardMaker()
maker.process_all('${REPO_ROOT}/corpus/processed', '${REPO_ROOT}/distilled/file_cards')
"

python -c "
from china_policy_skill.distill.make_policy_signal_card import PolicySignalCardMaker
maker = PolicySignalCardMaker()
maker.process_all('${REPO_ROOT}/corpus/processed', '${REPO_ROOT}/distilled/policy_signal_cards')
"

python -c "
from china_policy_skill.distill.make_language_card import LanguageCardMaker
maker = LanguageCardMaker()
maker.process_all('${REPO_ROOT}/corpus/processed', '${REPO_ROOT}/distilled/language_cards')
"

python -c "
from china_policy_skill.distill.make_opportunity_card import OpportunityCardMaker
maker = OpportunityCardMaker()
maker.process_all('${REPO_ROOT}/corpus/processed', '${REPO_ROOT}/distilled/opportunity_cards')
"

python -c "
from china_policy_skill.report.weekly_digest import WeeklyDigestGenerator
import json, glob

docs = []
for f in sorted(glob.glob('${REPO_ROOT}/corpus/metadata/*.json')):
    with open(f) as fh:
        docs.append(json.load(fh))

signals = []
for f in sorted(glob.glob('${REPO_ROOT}/distilled/policy_signal_cards/*.md')):
    with open(f) as fh:
        signals.append(fh.read())

gen = WeeklyDigestGenerator()
digest = gen.generate(docs, signals)
with open('${REPO_ROOT}/reports/weekly_${WEEK}.md', 'w') as fh:
    fh.write(digest)
"

python -c "
from china_policy_skill.evaluate.run_eval import EvalRunner
runner = EvalRunner('${REPO_ROOT}/eval')
report = runner.run_all()
with open('${REPO_ROOT}/reports/eval_weekly_${WEEK}.json', 'w') as fh:
    fh.write(report.to_json())
print(f'Eval: passed={report.overall_passed}, score={report.overall_score:.3f}')
"

echo "Weekly distill complete. Report: ${REPORT_DIR}/weekly_${WEEK}.md"
