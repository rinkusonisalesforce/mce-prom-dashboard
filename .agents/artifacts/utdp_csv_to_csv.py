#!/usr/bin/env python3
"""Convert raw UTDP Jobs CSV exports (Job Name,Alert Type,Enabled,Last Exec)
into the dashboard NA_<date>.csv / EU_<date>.csv format.

Groups enabled jobs by (Customer_Name, EID) and counts them — identical
rules to pdf_to_csv.py (shared parse_job logic, no PDF dependency)."""
import csv, re, sys
from collections import Counter


def parse_job(jobname):
    m = re.search(r'([EeMm])(\d{4,})', jobname)
    if m:
        eid_out = ('M' if m.group(1) in 'Mm' else 'E') + m.group(2)
    else:
        m = re.search(r'(?<!\d)(\d{5,})', jobname)
        if not m:
            return None, None
        eid_out = 'E' + m.group(1)
    name_part = jobname[:m.start()].rstrip('_ ').strip()
    if name_part.startswith('ProM_MC_'):
        name = name_part[len('ProM_MC_'):]
    elif name_part.startswith('PLAT_MC_'):
        name = name_part[len('PLAT_'):]
    elif name_part.startswith('PLAT_'):
        stripped = name_part[len('PLAT_'):]
        name = stripped if stripped else name_part.rstrip('_')
    else:
        name = name_part
    name = name.strip().strip('_').strip()
    if not name:
        name = name_part.strip('_').strip() or 'UNKNOWN'
    return name, eid_out


def q(s):
    s = str(s)
    return '"' + s + '"' if re.search(r'[^A-Za-z0-9]', s) else s


def build(src, out, label):
    groups = Counter(); skips = []; n = 0
    with open(src, newline='') as f:
        reader = csv.DictReader(f)
        # Job-name column is usually 'Job Name' but exports sometimes label it
        # 'Job Name1' etc. — match any header that starts with 'Job Name'.
        job_col = next((c for c in (reader.fieldnames or []) if c and
                        c.strip().lower().startswith('job name')), 'Job Name')
        for r in reader:
            if (r.get('Enabled') or '').strip().upper() != 'TRUE':
                continue
            n += 1
            cust, eid = parse_job((r.get(job_col) or '').strip())
            if not eid:
                skips.append(r.get('Job Name')); continue
            groups[(cust, eid)] += 1
    rows = sorted(groups.items(), key=lambda kv: (-kv[1], kv[0][0].lower()))
    with open(out, 'w', newline='') as fh:
        fh.write(f'{q("Customer_Name")},{q("EID")},{q("Total_Monitors_Enabled")}\n')
        for (c, e), cnt in rows:
            fh.write(f'{q(c)},{q(e)},{cnt}\n')
    print(f"{label}: {n} enabled jobs -> {len(rows)} tenants, "
          f"{sum(groups.values())} monitors, {len(skips)} skipped")
    for s in skips:
        print("   SKIP:", s)
    print("   ->", out)


if __name__ == '__main__':
    na_src, eu_src, out_dir, date = sys.argv[1:5]
    build(na_src, f"{out_dir}/NA_{date}.csv", "NA")
    build(eu_src, f"{out_dir}/EU_{date}.csv", "EU")
