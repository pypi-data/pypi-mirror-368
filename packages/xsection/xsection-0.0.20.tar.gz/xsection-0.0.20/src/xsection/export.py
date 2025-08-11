import textwrap

def export_fedeas(shape, type, name=None, material=None):
    if name is None:
        name = "SecData"

    if type == "Elastic":
        # Export elastic properties
        pass

    elif type == "General":
        s = f"""
        {name} = struct();
        """
        for i,fiber in enumerate(shape.create_fibers()):
            s += f"""
            {name}.Fibers{{{i+1}}}.r    = [0 {fiber['y']}, {fiber['z']}];
            {name}.Fibers{{{i+1}}}.Area = {fiber['area']};
            {name}.Fibers{{{i+1}}}.Warp = [
                {float(fiber['warp'][0][0])}, {float(fiber['warp'][0][1])}, {float(fiber['warp'][0][2])};
                {float(fiber['warp'][1][0])}, {float(fiber['warp'][1][1])}, {float(fiber['warp'][1][2])};
                {float(fiber['warp'][2][0])}, {float(fiber['warp'][2][1])}, {float(fiber['warp'][2][2])}
            ]
            """
        return textwrap.dedent(s)
    else:
        raise ValueError(f"Unknown export type: {type}")
