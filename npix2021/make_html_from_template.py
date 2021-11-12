# Since we want to build two HMTL files that are exactly the same except for a
# single file name, and we don't want any dynamic server-side scripts, we just
# replace the string %%%DSNAME%%% with the dataset name, and save it to the
# appropriate HTML file.

datasets = ["miniDataset", "eMouse"]
dataset_filenames = ["index.html", "emouse_dataset.html"]
with open("template.txt", "r") as f:
    text = f.read()

for ds,fn in zip(datasets, dataset_filenames):
    html = text.replace("%%%DSNAME%%%", ds)
    with open(fn, "w") as f:
        f.write(html)
