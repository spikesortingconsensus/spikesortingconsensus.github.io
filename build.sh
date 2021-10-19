#!/bin/bash
# So here's how this works.  You have to download the data from the Qualtrics
# survey.  This is on my (Max) Yale account, which Yale tells me I should have
# for life.  Google forms doesn't work because they don't have a way of
# automating the process of linking spreadsheet responses to the files.  (In the
# spreadsheet, it gives you a link to the page where you can download the file.
# It doesn't give you the filename for doing a separate download, and you can't
# download directly from the link, since it requires browser cookies and tries
# to open the Google viewer on the .tsv files.)  Pass the two files from
# Qualtrics (the zipped csv containing the responses, and the zip containing the
# downloaded files) as arguments to this script.  It will make sure the web page
# is up to date, process these files, and then add them and commit them to the
# git repo.  The git repo is owned by a custom organization which I made so that
# we can control the .github.io domain name.  Then the site should automatically
# update via github pages a minute or two after the commit.

# Images taken with "shutter -s 663,98,825,845 -e -n", saves as Selection_xxx.png
# Window masked through imagemagick script: "for f in Selection*.png; do convert $f mask.png -background black -gravity center -flatten out$f; done"
# Mass rename with "rename 's/outSelection_/eMouse_/' outSelection*.png" or "rename 's/outSelection_/miniDataset_/' outSelection*.png"

python3 make_html_from_template.py
python3 process_survey_response.py $1 $2
#git add -u
#git commit -m "$(date)"
#git push
