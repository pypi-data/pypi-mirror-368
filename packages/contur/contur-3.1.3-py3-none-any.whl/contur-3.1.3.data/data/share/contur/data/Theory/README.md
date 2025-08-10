 ##  SM theory predictions

To add new SM theory predictions to the contur release, you need to

   * Get them into YODA file format and put them in your local copy of this directory. The histogram path names should start with ``/THY/`` and otherwise
match the histograms they are intended to be compared to. 
   * The details of what the prediction is and where it comes from should then be added to the ``theory_predictions`` table in the analysis database [here](../DB/analyses.sql).
   * Any original data (e.g. CSV files from a theorist etc) should be archived in [``TheoryRaw`` directory](../TheoryRaw), and any code used to build the Theory.yoda file from these should be implemented in [``sm_theory_builders.py``](../../contur/data/sm_theory_builders.py) and hooked in to [``run_mkthy.py``](../../contur/run/run_mkthy.py) so that it can be redone if necessary using `contur-mkthy`.

There are lots of examples in [``sm_theory_builders.py``](../../contur/data/sm_theory_builders.py) of standard or semi-standard ways of building Theory yodas from various sources.

Several predictions for the same cross section may be stored here, but the one that is used is the one which has ID "A" in the table. In future
users will be able to select which predictions to use, probably with a config file, but at the moment the simplest way to do this is probably to either change
the ID in the DB and rebuild the DB, or else add a special conditional when `load_bg_data` is called in [``yoda_factory``](../../contur/factories/yoda_factories.py).

### Digitising SM predictions from plots in a paper

Unfortunately this is sometimes the only way.

These instructions, original version by Daniel Baig, use https://plotdigitizer.com/app to read data points from figures.

#### Uploading your image.

Firstly, your plot needs to be converted to an accessible format and uploaded to the application so you can work on it.

To obtain a plot from a paper, it is best to go to the source of the paper rather than the pdf and see if the image is already available in a high-quality format
alongside the pdf. However, often this is not the case. So the most reliable option is to go into the pdf and take a screenshot.

You want to ensure that the image is in as high quality as possible, so maximise the window with the pdf and click the ‘+’ to enlarge and the scroll bars to centre the
image so it takes up a considerable portion of the screen.

Press ‘Print Screen’ (you may need to hold down Fn while doing this) to save a .png image in your pictures folder.

Go to your pictures folder (get here from the ‘home’ folder on the desktop screen) and open the most recent .png screenshot.

Crop the image to only include the relevant plot, and be careful to not cut off the axes and their ticks.

If you cannot find a way to crop the image you may need to open the image in an alternative application. Right-click on the image and select ‘open with’ to do this.

I would recommend using ‘Gwenview’ to do this.
   * Go to Edit>Crop
   * Once cropped, left-click on ‘Crop’.
   * Then save the cropped image with an identifiable name in pictures.

Lastly, select ‘open file’ in the top left of the screen in PlotDigitize and navigate to your cropped image in pictures and select it.
You should see the image on the screen with four points on it (x1,x2,y1,y2).

Note: a significant portion of the image may be cut off, if you go to the full-screen icon in the top left corner this should make the image display normally
so you can access all parts of it.

Additionally, you may notice that the image can be rather blurry, this is an unfortunate consequence of using a screenshot and cropping it.
To reduce this blurring, you can repeat the above procedure and make sure that before the screenshot is taken the graph is as large as possible while making
sure to not cut any relevant data or axes off.

#### Selecting points

Before any points are chosen, the scales need to be set in terms of the pixels. Begin by choosing two locations on the x-axis and two on the y-axis and drag the given points to the chosen locations.

   * Recommendation: Choose spread-out major ticks. By choosing major ticks you can more easily put the point exactly on the value and get a more accurate scale.
   
Decide on what data point you are going to sample (if there are multiple) and try to select the centre of each data point along with the upper and lower uncertainties as accurately as you can using the zoomed version of the image in the top right.
Be sure to refer to the legend to ensure you are including the correct uncertainties.

Note: The order does not strictly matter however it will be more readable if you keep to a consistent system, e.g. centre, upper, lower, centre, upper, etc.
Note: additional information is available in the top right in the question mark symbol followed by ‘instructions’.
Uploading points to a Python file

Export the points to a CSV (comma-separated variable) file (the option to do this is in the top left of the app screen.

### Importing data from a CSV file

CSV files in the format obtained from the digitiser app as described above can be read in using a standard function - 'read_from_csv_files' -  found in [``sm_theory_builders.py``](../../contur/data/sm_theory_builders.py). 

To ensure the correct points apply to the correct graph, you need to go to [inspirehep.net](https://inspirehep.net) and enter the name of your paper, or the ID (which is the
number after the I in the rivet analysis name).

Go to datasets on the paper you are looking at to see entries for the different tables. You will find a column of tables with a short description of what they show.
Find the table that corresponds to the data you are taking from a plot.
In your Python function, entries will usually be of the form "dXX-xYY-yZZ", where XX, YY and ZZ are numbers with a preceding zero if only a single digit.

   * XX refers to the table number.
   * YY refers to the independent variable number (this will almost always be 01)
   * ZZ refers to the dependent variable number, i.e. the column number subtracted by YY.
   
Make a directory in contur/data/TheoryRaw with the full name of the relevant analysis, e.g. `mkdir ATLAS_2016_I1448301:LMODE=LL`.
Rename each of your CSV files so the name matches the table of the plot it belongs to, e.g. `dXX-xYY-yZZ.csv` and copy it into this new directory.

#### Adding and checking on a local branch

Now that the CSV file has been stored we need to add the code to convert it to a yoda file.

Navigate to your top-level contur environment in the terminal.
You can check what branch you would be working on by default with ‘git status’. You will see that you are on the main branch. You can see all active branches with ‘git branch -a’.

We want to test on a separate branch first so create a new branch with: `git checkout -b name_of_your_branch_here`

Note: to change between branches use: `git checkout`

Navigate to `analyses.sql` and open it for editing.

Add the relevant information for the new SM prediction as a "SPECIAL" entry in the theory_predictions table.

Return the the contur top directory and run `make` to add the new entry to the database

Navigate to `run_mkthy.py`, and open it for editing.

Add the new analysis and its histograms to the `histo_lists` python dictionary in this file.

In `data/Theory`, run `contur-mkthy --ana-match nameOfFunc`.

Return to the contur top directory and run: `make` and then `make check`.
If you run into an assertion error due to regression test, this means your new data have changed the results (which is good!) but you need to
rebuild the reference data for the regression tests. See [``these instructions``](../../tests/README.md)

Use `git add fileName` to add all the relevant new files you have created.

Remember to also add the new `.yoda` file that is in `contur/data/Theory`

Run ‘git commit -m “Title of your changes”’ to commit your changes to your branch.

Run `git push --set-upstream origin name_of_your_branch_here` from the top contur directory.

Finally, request to merge your branch with the main one.

Go to https://gitlab.com/hepcedar/contur/-/merge_requests

Select the merge request you just pushed.

Add a brief description and reviewers.

Merging with main

You will need to regularly pull changes to contur from gitlab.

Navigate to your contur directory.
Ensure you are on the main branch with `git status`. If not, run: `git checkout main`

Execute: `git pull`

Run `make` again.

#### Viewing your plots

If you run `contur-smtest --graphics True` you should get an html index file which you can browse and see your new SM comparison plots. Check by eye to see
they agree with what you expect! (You can select just your own analysis with the `--ana-match` option.)





