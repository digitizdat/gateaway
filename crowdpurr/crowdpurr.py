#!/usr/bin/env python
# ---
# jupyter:
#   jupytext_format_version: '1.3'
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.5.6
# ---


import pandas as pd
import seaborn as sns
import numpy as np
import PIL
from io import BytesIO
from matplotlib import pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, Image

# Start by simply loading the data from CSV
df = pd.read_csv('CrowdActivityExport_09132018_03-15PM.csv', true_values='Yes', false_values='No', na_values='-')

# Loop through all the results, creating a box chart for each.
for i in df['Question Number'].unique():
    q = df[df['Question Number'] == i][['Question Number', 'Vote Title', 'Question Title']]
    fig = sns.catplot(y="Vote Title", kind="box", data=q)
    plt.ylabel(q['Question Title'][:1].values[0])

    # OK, let's try a little PDF generation here...
    # Save the figure as a PNG so we can open it via PIL and convert it to a ReportLab flowable.
    filename = "figure-{}.png".format(i)
    fig.savefig(filename)
    im = PIL.Image.open(filename)

    buf = BytesIO()
    im.save(buf, 'PNG')
    im = Image(buf)

    # Load the data to be displayed into a table and then build the PDF.
    tabledata = [np.array([im], dtype=object).tolist()]
    table = Table(tabledata)
    
    doc = SimpleDocTemplate("question-{}.pdf".format(i), pagesize=letter)
    doc.build([table])

