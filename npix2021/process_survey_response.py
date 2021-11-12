# This script takes two arguments.  The first is the zipped csv file downloaded
# from qualtrics.  The second is the zip file containing the files uploaded to
# qualtrics.

import sys
import zipfile
import tempfile
import glob
import pandas
import numpy as np

csvzip = sys.argv[1]
fileszip = sys.argv[2]

names = {"miniDataset": "miniDataset", "eMouse": "eMouse"}

ignore_ids = ['random test', 'max test', 'dummy', 'splitmergetest']

#csvzip = "/home/max/Downloads/Submit+manual+spike+sorting_October+16,+2021_07.34.zip"
#fileszip = "/home/max/Downloads/Submit+manual+spike+sorting_October+16,+2021_07.34(1).zip"

# csvzip = "/home/max/Downloads/Submit+manual+spike+sorting_October+14,+2021_09.29.zip"
# fileszip = "/home/max/Downloads/Submit+manual+spike+sorting_October+14,+2021_09.29(2).zip"
# d = "/home/max/Tmp/surveyextract/"

reference_clusters_files = {"miniDataset": "/home/max/Research_data/cortexlab/neuropixels_course/miniDataset/spike_templates.npy", "eMouse": "/home/max/Research_data/cortexlab/neuropixels_course/eMouse_dataset/spike_templates.npy"} # TODO change path
_referenceclusters = {"miniDataset": [], "eMouse": []}
for k in reference_clusters_files.keys():
    _s = np.load(reference_clusters_files[k]).flatten()
    _referenceclusters[k] = _s


with tempfile.TemporaryDirectory() as d:
    with zipfile.ZipFile(csvzip, 'r') as zip_ref:
        zip_ref.extractall(d)

    with zipfile.ZipFile(fileszip, 'r') as zip_ref:
        zip_ref.extractall(d)

    csvfile = glob.glob(d+"/*.csv")[0]
    df = pandas.read_csv(csvfile).iloc[2:]

    cluster_group_files = {"miniDataset": [], "eMouse": []}
    spike_clusters_files = {"miniDataset": [], "eMouse": []}
    anonymous_ids = {"miniDataset": [], "eMouse": []}
    for i,r in df.iterrows():
        aid = r['Q1']
        print(aid)
        if aid in ignore_ids: continue
        cluster_group_files[r['Q2']].append(glob.glob(d+"/Q3/"+r["ResponseId"]+"*.tsv")[0])
        spike_clusters_files[r['Q2']].append(glob.glob(d+"/Q4/"+r["ResponseId"]+"*.npy")[0])
        anonymous_ids[r['Q2']].append(aid)

    _spikeclusters = {"miniDataset": [], "eMouse": []}
    for k in spike_clusters_files.keys():
        if len(spike_clusters_files[k]) == 0: continue
        for fn,aid in zip(spike_clusters_files[k], anonymous_ids[k]):
            _s = np.load(fn).flatten()
            _spikeclusters[k].append((aid,_s))


    _groups = {"miniDataset": [], "eMouse": []}
    for k in cluster_group_files.keys():
        if len(cluster_group_files[k]) == 0: continue
        for fn,aid in zip(cluster_group_files[k], anonymous_ids[k]):
            _g = pandas.read_csv(fn, sep="\t")
            _g.columns = ["cell", aid]
            _g.set_index("cell", inplace=True)
            _groups[k].append(_g)

        groups = pandas.concat(_groups[k], axis=1)
        groups = groups[groups.index<=max(_referenceclusters[k])]
        json = "dat = "+str(groups.reset_index().T.reset_index().T.to_numpy(na_value="").tolist())
        with open(f"groups-{names[k]}.json", "w") as f:
            f.write(json)


for k in _spikeclusters.keys():
    splits = []
    merges = []
    for subj in range(0, len(_spikeclusters[k])):
        splits.append([])
        merges.append([])
        sc = _spikeclusters[k][subj][1]
        # Splits
        refinds = list(sorted(set(_referenceclusters[k])))
        for i in refinds:
            newlabels = set(sc[_referenceclusters[k]==i])
            if len(newlabels) > 1:
                splits[-1].append(i)
        # Merges
        userinds = list(sorted(set(sc)))
        for i in userinds:
            oldlabels = set(_referenceclusters[k][sc==i])
            if len(oldlabels) > 1 and list(sorted(oldlabels)) not in merges[-1]:
                merges[-1].append(list(sorted(oldlabels)))

    fulljson = "dat_splits = "+str(splits) + ";\ndat_merges = "+str(merges)+";"
    with open(f"splitsmerges-{names[k]}.json", "w") as f:
        f.write(fulljson)
