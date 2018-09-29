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
import json
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
parser.add_argument('--trim', default=0.0, type=float, help="Percentage (as a float value) of results to trim before calculating the mean")
args = parser.parse_args()

# Set PDF document parameters
pagex = 1800
pagey = 1013.4

# Load the data from CSV
df = pd.read_csv(args.datafile, true_values='Yes', false_values='No', na_values='-')

# Load the answers
qna = json.load(open('data/answers.json'))

# Loop through all the results, creating a box chart for each.
for i in df['Question Number'].unique():
    print("Processing question {}".format(i))
    q = df[df['Question Number'] == i][['Question Number', 'Vote Title', 'Question Title']]
    ylabel = "Q{}: {}".format(i, q['Question Title'][:1].values[0])

    # Trimmed series
    if args.trim > 0.0:
        q = q.dropna()
        after = trimval = max(math.floor(len(q)*args.trim), 1)
        before = len(q)-1-trimval
        q = q.sort_values('Vote Title').reset_index(drop=True).truncate(after, before)

    if args.nocharts is False:
        fig, ax = plt.subplots(figsize=(5.5, 8.25))
        sns.catplot(ax=ax, y="Vote Title", kind="swarm", data=q, alpha=0.5)
        plt.ylabel(ylabel)

        # OK, let's try a little PDF generation here...
        # Save the figure as a PNG so we can open it via PIL and convert it to a ReportLab flowable.
        filename = "figure-%02d.png" % i
        fig.savefig(filename, bbox_inches='tight')
        plt.close()
    else:
        filename = 'assets/blank-figure.png'

    # Calculate max/min/mean
    qmean = q['Vote Title'].mean()
    if math.isnan(qmean) is True:
        qmean = "NaN"
    else:
        qmean = math.floor(qmean)
        # Insert commas every three digits
        qmean = "{:,}".format(qmean)

    # Load the answer

    # Convert the PNG image to a Reportlab Flowable object
    im = PIL.Image.open(filename)
    buf = BytesIO()
    im.save(buf, 'PNG')
    im = Image(buf)

    # Draw the PDF canvas using the Arial font in Slalom blue
    c = canvas.Canvas("question-%02d.pdf" % i, pagesize=(pagex, pagey))
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial Bold', 'Arial Bold.ttf'))

    # Draw the titles
    # The way Reportlabs processes RGB values is so strange... The value must
    # be between 0 and 1, so just take your RGB values and multiply them each
    # by (1/255).
    c.setFillColorRGB(0.17647059, 0.44705882, 0.75686275)
    c.setFont('Arial', 58)
    c.drawCentredString(pagex/2.0, pagey-100, qna[str(i)]['q'])
    c.drawCentredString((pagex/8.0*6), (pagey/8.0)*5+60, "Wisdom of the Crowd")
    c.drawCentredString((pagex/8.0*6), (pagey/8.0)*3+25, "Actual Answer")

    # Draw the numbers
    c.setFillColorRGB(0.5254902, 0.5254902, 0.5254902)
    c.setFont('Arial Bold', 150)
    c.drawCentredString((pagex/8.0)*6, (pagey/32.0)*17, str(qmean))
    c.drawCentredString((pagex/8.0)*6, (pagey/4.0), qna[str(i)]['a'])

    # Draw the center line
    c.setStrokeColorRGB(0.7, 0.7, 0.7)
    c.line(pagex/2.0, 100, pagex/2.0, pagey-200)

    # Insert the chart
    im.drawOn(c, 200, 125)

    # Build the PDF
    c.save()


