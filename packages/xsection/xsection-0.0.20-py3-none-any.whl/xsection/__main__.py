from shps.frame.solvers import TriangleModel
from xsection.warping import WarpingSection


if __name__ == "__main__":
    import sys
    import json
    import veux
    file_name = sys.argv[1]
    with open(file_name, "r") as f:
        data = json.load(f)
    model = TriangleModel.from_xara(data)

    section = WarpingSection(model)

    print(section.summary())

    artist = veux.create_artist(section.model, ndf=1)
    w = section._analysis.solution()
    artist.draw_surfaces(field=w, state=w/w.max())
    artist.draw_outlines()
    veux.serve(artist)
