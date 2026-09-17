#!/usr/bin/env python3
"""Regression checks for advisory authority and unsafe observation examples.

These check published contracts, NOT arbitrary shell execution or model routing.
The two Ansible counterexamples run only on isolated localhost fixtures. Missing
Ansible is a visible skip; CI installs it so those examples must actually run.
"""
from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIZING = 'operation-registry/delivered/sizing.md'
TIERS = 'skills/_operation/SAFETY_TIERS.md'
CAPTURE = 'skills/operation-incident/reference/capture-commands.md'
TRAPS = 'skills/operation-incident/reference/observation-traps.md'
SKILLS = ('change', 'incident', 'oncall', 'readiness', 'runbook')
BOUNDARY = 'Advisory only. Humans execute system changes.'


def defects(root: Path) -> list[str]:
    out: list[str] = []
    def read(path: str) -> str:
        p = root / path
        if not p.is_file():
            out.append(f'missing: {path}')
            return ''
        return p.read_text(encoding='utf-8')
    sizing, tiers, capture, traps = map(read, (SIZING, TIERS, CAPTURE, TRAPS))
    if BOUNDARY not in sizing:
        out.append('A1: boundary missing from delivery source')
    for name in SKILLS:
        if BOUNDARY not in read(f'skills/operation-{name}/SKILL.md'):
            out.append(f'A1: boundary not delivered to {name}')
    if 'Human operator approval' not in tiers or re.search(r'\bautonomous\b', tiers, re.I):
        out.append('A2: autonomy is not separated from human approval')
    if 'This set never executes system mutations' not in tiers:
        out.append('A2: system mutation boundary missing')
    if 'execution: proposed' not in tiers or 'operator:' not in tiers:
        out.append('A3: proposed action lacks explicit actor or execution state')
    if 'No dry run or reversal is required for a read-only observation.' not in tiers:
        out.append('A4: observation requires fictitious dry-run or undo')
    rows = {t: next((l for l in tiers.splitlines() if l.startswith(f'| `{t}` |')), '')
            for t in ('T1', 'T2', 'T3', 'T4')}
    if 'Dry-run output logged' in rows['T1']:
        out.append('A4: unconditional T1 dry-run restored')
    if not all(s in rows['T2'] for s in ('preflight', 'rollback command', 'post-verify')):
        out.append('A5: T2 risk controls weakened')
    if 'Named approver + rollback rehearsed' not in rows['T3'] or 'two-person rule' not in rows['T4']:
        out.append('A5: T3/T4 approval controls weakened')
    if 'advisory-only boundary' not in read('operation-registry/delivered/values.md'):
        out.append('A6: escape hatch can suspend advisory boundary')
    if 'Everything here is read-only' in capture:
        out.append('A7: unsafe blanket observation claim')
    if any('check_mode: false' not in t or 'custom facts' not in t for t in (capture, traps)):
        out.append('A7: Ansible side-effect warning missing')
    for block in re.findall(r'```sh\n(.*?)```', capture, flags=re.S):
        for line in block.splitlines():
            if line.startswith('ansible-playbook ') or re.search(r'\b-m\s+setup\b', line):
                out.append('A8: unreviewed Ansible execution in capture commands')
            if line.startswith('aws ') and not all(f in line for f in ('--profile ', '--region ')):
                out.append('A9: ambient AWS observation')
            if line.startswith(('gcloud compute ', 'gcloud logging ')) and not all(
                    f in line for f in ('--project ', '--account ')):
                out.append('A9: ambient Google Cloud observation')
    return out


MUTATIONS = (
    ('A1', SIZING, BOUNDARY, 'Proceed autonomously.'),
    ('A2', TIERS, 'Human operator approval', 'Autonomy'),
    ('A2', TIERS, 'Existing change policy;', 'Autonomous with post-verify;'),
    ('A3', TIERS, 'execution: proposed', 'execution: executed'),
    ('A4', TIERS, 'No dry run or reversal is required for a read-only observation.',
     'Every observation requires a dry run and rollback.'),
    ('A5', TIERS, 'Meaningful preflight + rollback command stated', 'Command stated'),
    ('A5', TIERS, 'two-person rule', 'one-person rule'),
    ('A6', 'operation-registry/delivered/values.md', 'advisory-only boundary', 'formatting rule'),
    ('A7', CAPTURE, 'Only verified read-only observations may be executed by the agent.',
     'Everything here is read-only.'),
    ('A7', TRAPS, 'check_mode: false', 'check_mode: true'),
    ('A8', CAPTURE, 'ansible <pattern> -i <reviewed-static-inventory> --list-hosts',
     'ansible-playbook -i <inv> <play.yml> --check --diff'),
    ('A9', CAPTURE, '--profile <profile>', ''),
    ('A9', CAPTURE, '--project <project>', ''),
)


class ContractTests(unittest.TestCase):
    def test_current_contracts(self):
        self.assertEqual(defects(ROOT), [])

    def test_every_deliberate_regression_is_rejected(self):
        for code, path, old, new in MUTATIONS:
            with self.subTest(code=code, path=path), tempfile.TemporaryDirectory() as tmp:
                copy = Path(tmp) / 'repo'
                shutil.copytree(ROOT, copy, symlinks=True,
                                ignore=shutil.ignore_patterns('.git', '__pycache__'))
                p = copy / path
                text = p.read_text(encoding='utf-8')
                self.assertIn(old, text, 'negative test no longer reaches its target')
                p.write_text(text.replace(old, new, 1), encoding='utf-8')
                result = subprocess.run([sys.executable, __file__, '--check', str(copy)],
                                        capture_output=True, text=True, timeout=20)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(code + ':', result.stdout)
        print(f'{len(MUTATIONS)} deliberate advisory/observation regressions rejected')


@unittest.skipUnless(shutil.which('ansible-playbook'), 'SKIPPED: ansible-playbook not installed')
class AnsibleCounterexamples(unittest.TestCase):
    def run_local(self, tasks: str, d: Path) -> subprocess.CompletedProcess:
        inv = d / 'inventory'
        inv.write_text(f'localhost ansible_connection=local ansible_python_interpreter={sys.executable}\n')
        cfg = d / 'ansible.cfg'
        cfg.write_text('[defaults]\nretry_files_enabled = False\n')
        play = d / 'play.yml'
        play.write_text('- hosts: all\n  gather_facts: false\n  tasks:\n' + tasks)
        env = {'PATH': os.environ['PATH'], 'HOME': str(d), 'LANG': 'C.UTF-8',
               'ANSIBLE_CONFIG': str(cfg), 'ANSIBLE_LOCAL_TEMP': str(d / 'ansible-tmp')}
        result = subprocess.run(['ansible-playbook', '-i', str(inv), str(play), '--check'],
                                cwd=d, env=env, capture_output=True, text=True, timeout=45)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_check_mode_false_really_mutates(self):
        with tempfile.TemporaryDirectory(prefix='operation-advisory-') as tmp:
            d = Path(tmp)
            marker = d / 'changed-despite-check'
            self.run_local(f'    - ansible.builtin.file:\n        path: {marker}\n'
                           '        state: touch\n      check_mode: false\n', d)
            self.assertTrue(marker.is_file(), 'check_mode:false counterexample did not execute')

    def test_custom_facts_really_execute(self):
        with tempfile.TemporaryDirectory(prefix='operation-advisory-') as tmp:
            d = Path(tmp)
            facts = d / 'facts'
            facts.mkdir()
            marker = d / 'custom-fact-executed'
            fact = facts / 'probe.fact'
            fact.write_text('#!/bin/sh\n: > ' + shlex.quote(str(marker)) +
                            '\nprintf \'{"probe": "executed"}\\n\'\n')
            fact.chmod(0o700)
            self.run_local(f'    - ansible.builtin.setup:\n        fact_path: {facts}\n'
                           '        gather_subset: ["!all", "!min", "local"]\n', d)
            self.assertTrue(marker.is_file(), 'custom-facts counterexample did not execute')


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--check':
        errors = defects(Path(sys.argv[2]))
        print('\n'.join(errors) if errors else 'advisory contracts green')
        sys.exit(bool(errors))
    unittest.main(verbosity=2)
