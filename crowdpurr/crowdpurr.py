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


import argparse
import pandas as pd
import seaborn as sns
import numpy as np
import PIL
import math
from io import BytesIO
from matplotlib import pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.platypus import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


#
# Main starts here
#
parser = argparse.ArgumentParser()
parser.add_argument('datafile', type=str, help="Specify the data file")
parser.add_argument('--nocharts', action='store_true', help="Disable chart generation")
args = parser.parse_args()

# Start by simply loading the data from CSV
df = pd.read_csv(args.datafile, true_values='Yes', false_values='No', na_values='-')

# Set PDF document parameters
pagex = 1800
pagey = 1013.4

# Loop through all the results, creating a box chart for each.
for i in df['Question Number'].unique():
    print("Processing question {}".format(i))
    q = df[df['Question Number'] == i][['Question Number', 'Vote Title', 'Question Title']]
    ylabel = "Q{}: {}".format(i, q['Question Title'][:1].values[0])

    # Calculate max/min/mean
    p = q['Vote Title']
    qmean = p.mean()
    qmax = p.max()
    qmin = p.min()

    # 10% trimmed series
    #after = trimval = max(math.floor(p.count()*.1), 1)
    #s = p.sort_values().reset_index(drop=True).truncate(trimval, p.count()-1-trimval)

    if args.nocharts is False:
        fig, ax = plt.subplots(figsize=(5.75, 8.75))
        sns.catplot(ax=ax, y="Vote Title", kind="swarm", data=q, alpha=0.5)
        plt.ylabel(ylabel)

        # OK, let's try a little PDF generation here...
        # Save the figure as a PNG so we can open it via PIL and convert it to a ReportLab flowable.
        filename = "figure-%02d.png" % i
        fig.savefig(filename, bbox_inches='tight')
        plt.close()
    else:
        filename = 'assets/blank-figure.png'

    # Convert the PNG image to a Reportlab Flowable object
    im = PIL.Image.open(filename)
    buf = BytesIO()
    im.save(buf, 'PNG')
    im = Image(buf)

    # Draw the PDF canvas using the Arial font in Slalom blue
    c = canvas.Canvas("question-%02d.pdf" % i, pagesize=(pagex, pagey))
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

    # The way Reportlabs processes RGB values is so strange... The value must
    # be between 0 and 1, so just take your RGB values and multiply them each
    # by (1/255).
    c.setFillColorRGB(0.17647059, 0.44705882, 0.75686275)
    c.setFont('Arial', 38)
    c.drawCentredString(pagex/2.0, pagey-100, ylabel)
    c.setFont('Arial', 20)
    c.drawString(100, 100, "Slalom")
    im.drawOn(c, 150, 150)

    c.setFillColorRGB(0.5254902, 0.5254902, 0.5254902)
    c.line(pagex/2.0, 200, pagex/2.0, pagey-200)
    c.setFont('Arial', 100)
    c.drawString((pagex/3.0)*2, (pagey/4.0)*3, str(math.floor(qmean)))

    # Build the PDF
    c.save()


