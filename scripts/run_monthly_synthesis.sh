#!/bin/bash
# Run monthly synthesis and maintenance
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${REPO_ROOT}/.venv/bin/activate"

MONTH=$(date +%Y-%m)
REPORT_DIR="${REPO_ROOT}/reports"
mkdir -p "${REPORT_DIR}"

python -c "
from china_policy_skill.report.monthly_synthesis import MonthlySynthesisGenerator
import json, glob

monthly_data = {'month': '${MONTH}', 'documents': [], 'total_documents': 0, 'trending_topics': [], 'policy_signals': [], 'regional_breakdown': {}, 'sector_breakdown': {}}

for f in sorted(glob.glob('${REPO_ROOT}/corpus/metadata/*.json')):
    with open(f) as fh:
        monthly_data['documents'].append(json.load(fh))
monthly_data['total_documents'] = len(monthly_data['documents'])

for f in sorted(glob.glob('${REPO_ROOT}/distilled/policy_signal_cards/*.json')):
    with open(f) as fh:
        monthly_data['policy_signals'].append(json.load(fh))

gen = MonthlySynthesisGenerator()
report = gen.generate(monthly_data)
with open('${REPO_ROOT}/reports/monthly_${MONTH}.md', 'w') as fh:
    fh.write(report)
"

python -c "
import yaml, requests, sys
with open('${REPO_ROOT}/config/sources.yaml') as f:
    sources = yaml.safe_load(f)
broken = []
def check_urls(group):
    for src in group:
        url = src.get('url', '')
        if not url:
            continue
        try:
            r = requests.head(url, timeout=10, allow_redirects=True)
            if r.status_code >= 400:
                broken.append({'name': src.get('name', ''), 'url': url, 'status': r.status_code})
        except Exception as e:
            broken.append({'name': src.get('name', ''), 'url': url, 'error': str(e)})
for key, group in sources.items():
    if isinstance(group, list):
        check_urls(group)
if broken:
    print(f'WARNING: {len(broken)} sources have availability issues')
    for b in broken[:10]:
        print(f'  {b[\"name\"]}: {b.get(\"url\", \"\")} - {b.get(\"status\", b.get(\"error\", \"\"))}')
else:
    print('All source URLs accessible')
"

python -c "
import json, glob, os
from datetime import datetime

forecast_dir = '${REPO_ROOT}/distilled/policy_signal_forecast_log'
calibration = {'total': 0, 'calibrated': 0, 'overdue': 0}
for f in sorted(glob.glob(os.path.join(forecast_dir, '*.json'))):
    with open(f) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            calibration['total'] += 1
            if entry.get('resolved'):
                calibration['calibrated'] += 1
            elif entry.get('deadline') and entry['deadline'] < datetime.now().isoformat():
                calibration['overdue'] += 1
print(f'Forecast calibration: {calibration[\"calibrated\"]}/{calibration[\"total\"]} resolved, {calibration[\"overdue\"]} overdue')
"

echo "Monthly synthesis complete. Report: ${REPORT_DIR}/monthly_${MONTH}.md"
