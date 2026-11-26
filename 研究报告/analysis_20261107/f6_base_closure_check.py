"""F6 deployment check (read-only): BASE must equal the F5 frozen source closure; after overlay, ROOT may differ
from it only in the frozen F6 overlay files.
Usage: python3 -I f6_base_closure_check.py <F5 prepared.json> <F6_delivery_manifest.json> <BASE> [<ROOT>]
Exit 0 = PASS, 1 = FAIL."""
import json, sys, hashlib, os
prep, man, base = sys.argv[1], sys.argv[2], sys.argv[3]
root = sys.argv[4] if len(sys.argv) > 4 else None
f5 = {r['relative_path']: r['sha256'] for r in json.load(open(prep))['files']}
ov = {r['relative_path']: r['sha256'] for r in json.load(open(man))['source_files']}
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.isfile(p) else None
fails = []
bad_base = [x for x, s in f5.items() if sha(os.path.join(base, x)) != s]
print('BASE vs F5 frozen closure: %d/%d match' % (len(f5) - len(bad_base), len(f5)))
fails += ['BASE ' + x for x in bad_base]
if root:
    bad_root = []
    for x, s in f5.items():
        want = ov.get(x, s)                      # overlay version for overlapping files, F5 version otherwise
        if sha(os.path.join(root, x)) != want: bad_root.append(x)
    bad_ov = [x for x, s in ov.items() if sha(os.path.join(root, x)) != s]
    changed = sorted(x for x in f5 if x in ov)
    print('ROOT vs F5 closure (overlay applied): %d/%d as expected; overlay files %d/%d byte-identical; '
          'F5 files replaced by overlay: %d' % (len(f5) - len(bad_root), len(f5), len(ov) - len(bad_ov), len(ov), len(changed)))
    fails += ['ROOT ' + x for x in bad_root] + ['OVERLAY ' + x for x in bad_ov]
print('PASS' if not fails else 'FAIL: ' + '; '.join(fails[:15]))
sys.exit(0 if not fails else 1)
