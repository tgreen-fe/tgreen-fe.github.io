# tgreen-fe.github.io

Personal portfolio. Plain static HTML and CSS, no build step. Published with
GitHub Pages from the `main` branch root.

```
index.html            landing page and project grid
<project>.html        one page per case study
style.css             single stylesheet
assets/fig/           SVG figures and schematics
assets/img/           raster imagery (WebP)
assets/video/         compressed demo loops
assets/               CV PDF
figures/              scripts that regenerate assets/fig
```

## Regenerating the figures

The pedal-actuation plots are generated from the raw bench data in
[automotive-driving-robot](https://github.com/tgreen-fe/automotive-driving-robot).
The schematics are hand-built SVG.

```sh
pip install matplotlib pandas
python figures/pedal.py        # needs the data repo cloned alongside
python figures/diagrams.py
```

## Adding a video

Compress to a short muted loop and drop it in `assets/video/`, then replace the
placeholder comment in the relevant project page:

```sh
ffmpeg -i source.MP4 -ss 00:00:04 -t 22 -vf "scale=1280:-2,fps=30" \
       -c:v libx264 -crf 28 -preset slow -movflags +faststart -an \
       assets/video/name.mp4
ffmpeg -i assets/video/name.mp4 -frames:v 1 -q:v 4 assets/video/name.jpg
```
