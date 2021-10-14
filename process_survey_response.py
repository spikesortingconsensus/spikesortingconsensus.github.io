# This script takes two arguments.  The first is the zipped csv file downloaded
# from qualtrics.  The second is the zip file containing the files uploaded to
# qualtrics.

import sys
import zipfile
import tempfile
import glob
import pandas

csvzip = sys.argv[1]
fileszip = sys.argv[2]

names = {"miniDataset": "miniDataset", "optionalDataset": "bigDataset"}

ignore_ids = ['random test']

# csvzip = "/home/max/Downloads/Submit+manual+spike+sorting_October+14,+2021_09.29.zip"
# fileszip = "/home/max/Downloads/Submit+manual+spike+sorting_October+14,+2021_09.29(1).zip"
# d = "/home/max/Tmp/surveyextract/"

with tempfile.TemporaryDirectory() as d:
    with zipfile.ZipFile(csvzip, 'r') as zip_ref:
        zip_ref.extractall(d)

    with zipfile.ZipFile(fileszip, 'r') as zip_ref:
        zip_ref.extractall(d)

    csvfile = glob.glob(d+"/*.csv")[0]
    df = pandas.read_csv(csvfile).iloc[2:]

    cluster_group_files = {"miniDataset": [], "optionalDataset": []}
    spike_clusters_files = {"miniDataset": [], "optionalDataset": []}
    anonymous_ids = {"miniDataset": [], "optionalDataset": []}
    for i,r in df.iterrows():
        aid = r['Q1']
        if aid in ignore_ids: continue
        cluster_group_files[r['Q2']].append(glob.glob(d+"/Q3/"+r["ResponseId"]+"*.tsv")[0])
        spike_clusters_files[r['Q2']].append(glob.glob(d+"/Q4/"+r["ResponseId"]+"*.npy")[0])
        anonymous_ids[r['Q2']].append(aid)


    _groups = {"miniDataset": [], "optionalDataset": []}
    for k in cluster_group_files.keys():
        if len(cluster_group_files[k]) == 0: continue
        for fn,aid in zip(cluster_group_files[k], anonymous_ids[k]):
            _g = pandas.read_csv(fn, sep="\t")
            _g.columns = ["cell", aid]
            _g.set_index("cell", inplace=True)
            _groups[k].append(_g)

        groups = pandas.concat(_groups[k], axis=1)
        json = "dat = "+str(groups.reset_index().T.reset_index().T.to_numpy(na_value="").tolist())
        with open(f"groups-{names[k]}.json", "w") as f:
            f.write(json)
