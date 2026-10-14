#!/usr/bin/env python3
"""Reproduce Bianca_spiel_v4.m's numeric loops with NumPy (not a MATLAB run).

Requires NumPy. The MATLAB source is read for its change tables. Preserves its
combination ordering, technology constraints, skip predicate and zero-filled
skipped output rows. Plotting and diagnostic message construction are omitted.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re
import numpy as np

ROOT = Path(__file__).resolve().parent.parent


def changes(source, name, shape):
    match = re.search(r'\b'+name+r'\s*=\s*\{\{(.*?)^\s*\};', source, re.S | re.M)
    if not match: raise ValueError(f'Missing table: {name}')
    text = re.sub(r'%[^\n]*','',match.group(0))
    values = [list(map(int,re.findall(r'-?\d+',cell)))
              for cell in re.findall(r'\{([^{}]+)\}',text)]
    data = np.array(values,dtype=np.int16)
    assert data.shape == (shape[0]*shape[1],3),(name,data.shape)
    return data.reshape(*shape,3)


def combinations():
    # Same construction as MATLAB, with zero-based choices; then sortrows.
    rows = np.arange(3,dtype=np.uint8).reshape(-1,1)
    options = [3,7,3,4,3,7,3,7,3,4,3,4]
    for col, count in enumerate(options[1:],1):
        if col in (9,11):
            previous_tech = 3 if col==9 else 9
            no_tech = rows[rows[:,previous_tech]==0]
            with_tech = rows[rows[:,previous_tech]>0]
            first = np.column_stack((no_tech,np.zeros(len(no_tech),dtype=np.uint8)))
            second = np.column_stack((np.tile(with_tech,(count,1)),
                                      np.repeat(np.arange(count,dtype=np.uint8),len(with_tech))))
            rows = np.vstack((first,second))
        else:
            rows = np.column_stack((np.tile(rows,(count,1)),
                                    np.repeat(np.arange(count,dtype=np.uint8),len(rows))))
    order = np.lexsort(tuple(rows[:,i] for i in range(11,-1,-1)))
    return rows[order]


def run(path, output):
    source = path.read_text(encoding='cp1252')
    policy = changes(source,'policies_changes',(6,3))
    event = changes(source,'event_changes',(3,7))
    tech = changes(source,'tech_changes',(3,4))
    rows = combinations(); n=len(rows)
    print(f'Generated and sorted {n:,} combinations.',flush=True)
    # MATLAB initial money: 5 minus all nonempty future technology choices.
    happy=np.full(n,5,dtype=np.int16)
    circle=np.zeros(n,dtype=np.int16)
    money=(5-np.count_nonzero(rows[:,[3,9,11]],axis=1)).astype(np.int16)
    failure_step=np.zeros(n,dtype=np.uint8)
    policy_i=event_i=tech_i=0
    for col in range(12):
        if col%2==0:
            table=policy[policy_i];policy_i+=1
        elif col in (1,5,7):
            table=event[event_i];event_i+=1
        else:
            table=tech[tech_i];tech_i+=1
        delta=table[rows[:,col]]
        happy+=delta[:,0]
        circle=np.maximum(0,circle+delta[:,1])
        money+=delta[:,2]
        fail=(failure_step==0)&((happy<1)|(money<1))
        failure_step[fail]=col+1
    print('Calculated resource outcomes for all combinations.',flush=True)
    # Locate contiguous runs with the same choice in each column. This preserves
    # the original skip condition, which checks only one column's value.
    changes_at=[np.flatnonzero(rows[1:,col]!=rows[:-1,col])+1 for col in range(12)]
    processed=np.zeros(n,dtype=bool)
    deaths=skipped=0;i=0
    while i<n:
        processed[i]=True
        step=int(failure_step[i])
        if step:
            deaths+=1
            column=step-1
            boundaries=changes_at[column]
            pos=np.searchsorted(boundaries,i,side='right')
            stop=int(boundaries[pos]) if pos<len(boundaries) else n
            skipped+=stop-i-1
            i=stop
        else:i+=1
    successful=processed&(failure_step==0)
    # Independently replay a prefix using the original loop and skip predicate.
    # This checks the vectorized resource calculations and accelerated skipping.
    death_step=None;last_value=None;policy_cols={0:0,2:1,4:2,6:3,8:4,10:5}
    event_cols={1:0,5:1,7:2};tech_cols={3:0,9:1,11:2}
    for index in range(min(20000,n)):
        choices=rows[index]
        if death_step is not None and int(choices[death_step])==last_value:
            assert not processed[index]
            continue
        assert processed[index]
        h,c,m=5,0,5-int(np.count_nonzero(choices[[3,9,11]]))
        first_failure=0
        for column,choice in enumerate(choices):
            table=(policy[policy_cols[column]] if column in policy_cols else
                   event[event_cols[column]] if column in event_cols else tech[tech_cols[column]])
            dh,dc,dm=map(int,table[choice]);h+=dh;c=max(0,c+dc);m+=dm
            if h<1 or m<1:
                death_step=column;last_value=int(choice);first_failure=column+1
                break
            death_step=None;last_value=None
        assert first_failure==failure_step[index]
        if not first_failure:assert (h,c,m)==(happy[index],circle[index],money[index])
    actual_successes=int(np.count_nonzero(successful))
    assert actual_successes==n-deaths-skipped
    # MATLAB leaves skipped vectors at their original zero values; processed
    # failures become NaN. Both the minimum and histogram therefore include zeros.
    scores=2.5*circle[successful]+1.5*happy[successful]+money[successful]
    exact_values,exact_counts=np.unique(scores,return_counts=True)
    exact_hist={float(k):int(v) for k,v in zip(exact_values,exact_counts)}
    script_hist=dict(exact_hist)
    if skipped:script_hist[0.0]=script_hist.get(0.0,0)+skipped
    integer_hist=integer_bins(script_hist)
    all_successful=failure_step==0
    all_success_scores=2.5*circle[all_successful]+1.5*happy[all_successful]+money[all_successful]
    values,counts=np.unique(all_success_scores,return_counts=True)
    corrected_hist={float(k):int(v) for k,v in zip(values,counts)}
    with (ROOT/'analysis/results/score-histogram.csv').open() as f:
        python_hist={float(r['score']):int(r['success']) for r in csv.DictReader(f) if int(r['success'])}
    assert corrected_hist==python_hist, 'Unfiltered MATLAB-table histogram differs from the story model'
    first_missed=int(np.flatnonzero((~processed)&all_successful)[0])
    earlier_processed=np.flatnonzero(processed[:first_missed])
    causing_failure=int(earlier_processed[-1])
    def choice_info(index):
        return {'row_1_based':index+1,'choices_1_based':(rows[index]+1).tolist(),
                'initial_research_payment':int(np.count_nonzero(rows[index,[3,9,11]])),
                'first_failure_step':int(failure_step[index]) or None}
    report={
        'execution':'Python/NumPy reproduction of numeric MATLAB logic; not native MATLAB execution',
        'source':str(path.relative_to(ROOT)),
        'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'theoretical_combinations':n,'early_terminations':deaths,
        'skipped_combinations':skipped,'lucky_playthroughs':actual_successes,
        'actual_successful_ranges':{
            'happy':[int(happy[successful].min()),int(happy[successful].max())],
            'circle':[int(circle[successful].min()),int(circle[successful].max())],
            'money':[int(money[successful].min()),int(money[successful].max())],
            'score':[float(scores.min()),float(scores.max())]},
        'script_printed_ranges_including_skipped_zeros':{
            'happy':[0 if skipped else int(happy[successful].min()),int(happy[successful].max())],
            'circle':[0 if skipped else int(circle[successful].min()),int(circle[successful].max())],
            'money':[0 if skipped else int(money[successful].min()),int(money[successful].max())],
            'score':[0.0 if skipped else float(scores.min()),float(scores.max())]},
        'script_histogram_entries':n-deaths,
        'spurious_zero_score_entries':skipped,
        'successful_combinations_before_original_skip_filter':int(np.count_nonzero(failure_step==0)),
        'valid_successes_skipped_by_original_filter':int(np.count_nonzero((~processed)&(failure_step==0))),
        'unfiltered_success_histogram_matches_story_python':True,
        'independent_original_loop_prefix_checked':min(20000,n),
        'first_valid_success_skipped':choice_info(first_missed),
        'preceding_failure_that_caused_skip':choice_info(causing_failure),
    }
    baseline=json.loads((ROOT/'analysis/results/summary.json').read_text())
    report['current_story_python_results']={k:{field:v[field] for field in ('paths','minimum_score','maximum_score')}
                                           for k,v in baseline['results'].items()}
    output.mkdir(parents=True,exist_ok=True)
    (output/'bianca-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    with (output/'bianca-score-histogram.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['score','successful_processed_combinations','original_script_histogram','success_without_skip_filter','story_python_success'])
        for score in sorted(set(script_hist)|set(corrected_hist)):
            writer.writerow([f'{score:g}',exact_hist.get(score,0),script_hist.get(score,0),corrected_hist.get(score,0),python_hist.get(score,0)])
    with (output/'bianca-integer-histogram.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['integer_bin_center','original_script_count'])
        for score in range(int(max(integer_hist))+1):writer.writerow([score,integer_hist.get(score,0)])
    print(json.dumps(report,indent=2),flush=True)


def integer_bins(histogram):
    # MATLAB BinMethod Integers: half-integer edges, integer centers.
    bins={}
    for score,count in histogram.items():
        center=int(np.floor(score+0.5))
        bins[center]=bins.get(center,0)+count
    return bins


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=ROOT/'analysis2/Bianca_spiel_v4.m')
    parser.add_argument('--output',type=Path,default=ROOT/'analysis2')
    args=parser.parse_args()
    run(args.source.resolve(),args.output)
