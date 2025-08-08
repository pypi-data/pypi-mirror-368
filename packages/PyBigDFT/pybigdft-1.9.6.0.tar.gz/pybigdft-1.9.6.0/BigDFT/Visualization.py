"""
This module has the routines and data structures necessary to allow one to
generate visualizations of a atomic systems. We also include helper routines
for generating colors.
"""
from io import StringIO
from typing import Dict, List, Optional, Union

import BigDFT
import BigDFT.Systems

# Default colors for atoms taken from JMol
_atoms = {'H': '#FFFFFF', 'He': '#D9FFFF', 'Li': '#CC80FF', 'Be': '#C2FF00',
          'B': '#FFB5B5', 'C': '#909090', 'N': '#3050F8', 'O': '#FF0D0D',
          'F': '#90E050', 'Ne': '#B3E3F5', 'Na': '#AB5CF2', 'Mg': '#8AFF00',
          'Al': '#BFA6A6', 'Si': '#F0C8A0', 'P': '#FF8000', 'S': '#FFFF30',
          'Cl': '#1FF01F', 'Ar': '#80D1E3', 'K': '#8F40D4', 'Ca': '#3DFF00',
          'Sc': '#E6E6E6', 'Ti': '#BFC2C7', 'V': '#A6A6AB', 'Cr': '#8A99C7',
          'Mn': '#9C7AC7', 'Fe': '#E06633', 'Co': '#F090A0', 'Ni': '#50D050',
          'Cu': '#C88033', 'Zn': '#7D80B0', 'Ga': '#C28F8F', 'Ge': '#668F8F',
          'As': '#BD80E3', 'Se': '#FFA100', 'Br': '#A62929', 'Kr': '#5CB8D1',
          'Rb': '#702EB0', 'Sr': '#00FF00', 'Y': '#94FFFF', 'Zr': '#94E0E0',
          'Nb': '#73C2C9', 'Mo': '#54B5B5', 'Tc': '#3B9E9E', 'Ru': '#248F8F',
          'Rh': '#0A7D8C', 'Pd': '#006985', 'Ag': '#C0C0C0', 'Cd': '#FFD98F',
          'In': '#A67573', 'Sn': '#668080', 'Sb': '#9E63B5', 'Te': '#D47A00',
          'I': '#940094', 'Xe': '#429EB0', 'Cs': '#57178F', 'Ba': '#00C900',
          'La': '#70D4FF', 'Ce': '#FFFFC7', 'Pr': '#D9FFC7', 'Nd': '#C7FFC7',
          'Pm': '#A3FFC7', 'Sm': '#8FFFC7', 'Eu': '#61FFC7', 'Gd': '#45FFC7',
          'Tb': '#30FFC7', 'Dy': '#1FFFC7', 'Ho': '#00FF9C', 'Er': '#00E675',
          'Tm': '#00D452', 'Yb': '#00BF38', 'Lu': '#00AB24', 'Hf': '#4DC2FF',
          'Ta': '#4DA6FF', 'W': '#2194D6', 'Re': '#267DAB', 'Os': '#266696',
          'Ir': '#175487', 'Pt': '#D0D0E0', 'Au': '#FFD123', 'Hg': '#B8B8D0',
          'Tl': '#A6544D', 'Pb': '#575961', 'Bi': '#9E4FB5', 'Po': '#AB5C00',
          'At': '#754F45', 'Rn': '#428296', 'Fr': '#420066', 'Ra': '#007D00',
          'Ac': '#70ABFA', 'Th': '#00BAFF', 'Pa': '#00A1FF', 'U': '#008FFF',
          'Np': '#0080FF', 'Pu': '#006BFF', 'Am': '#545CF2', 'Cm': '#785CE3',
          'Bk': '#8A4FE3', 'Cf': '#A136D4', 'Es': '#B31FD4', 'Fm': '#B31FBA',
          'Md': '#B30DA6', 'No': '#BD0D87', 'Lr': '#C70066', 'Rf': '#CC0059',
          'Db': '#D1004F', 'Sg': '#D90045', 'Bh': '#E00038', 'Hs': '#E6002E',
          'Mt': '#EB0026'}


class InlineVisualizer():
    """
    This class allows for a quick viewing of BigDFT systems using the
    py3Dmol package.

    https://pypi.org/project/py3Dmol/

    Attributes:
      xsize (int): the width of the picture in pixels.
      ysize (int): the height of the picture in pixels.
      nrow (int): if present, the number of rows for displaying a grid of
          structures.
      ncol (int): if present, the number of columns for displaying a grid of
          structures.
    """

    def __init__(self, xsize: int = 400, ysize: int = 300, nrow: int = 1, ncol: int = 1) -> None:
        from py3Dmol import view
        # set linked to False so that each structure can be rotated
        # independently
        self.xyzview = view(width=ncol*xsize, height=nrow*ysize,
                            viewergrid=(nrow, ncol), linked=False)

    def display_system(self, *syslist: List[BigDFT.Systems.System], **kwargs) -> None:
        """
        Display an animation of a sequence of systems. The colordict can be
        used to color each fragment. When only one system is passed it
        will remain still.

        Args:
          syslist (BigDFT.Systems.System): the systems to visualize.
          colordict (dict): a dictionary from fragment ids to hex colors,
             can also be a list of dicts (one for each system) if using a grid.
          field_vals(list): values of the field to decide colors of the keys
          cartoon (bool): set to True to use the cartoon view. This only works
            if atom names and residues are properly defined.
          gridlist (list): if present, defines the row and column indices for
            visualizing multiple systems on a grid.
          show (bool): you can explicitly defer showing.
        """
        from BigDFT.IO import write_pdb, reorder_fragments

        colordict = kwargs.get('colordict')
        field_vals = kwargs.get('field_vals')
        cartoon = kwargs.get('cartoon', False)
        gridlist = kwargs.get('gridlist', None)
        stick_radius = kwargs.get('stick_radius', 0.0)
        stick_color = kwargs.get('stick_color', 'black')
        zoom = kwargs.get('zoom', None)
        show = kwargs.get('show', True)

        # Set the default colors
        if colordict is None:
            keyset = []
            for system in syslist:
                keyset += list(system.keys())
            fv = {}
            for i, key in enumerate(keyset):
                if key not in fv:
                    fv[key] = i
            keyset = list(set(keyset))
            fvs = field_vals
            if fvs is not None:
                fvs = [field_vals[fv[key]] for key in keyset]
            colordict = get_colordict(keyset, field_vals=fvs)

        # Draw each system
        models = ""
        for s, system in enumerate(syslist):
            if type(colordict) is list:
                this_colordict = colordict[s]
            else:
                this_colordict = colordict

            if type(stick_color) is list:
                this_stick_color = stick_color[s]
            else:
                this_stick_color = stick_color

            model = ""
            sval = StringIO()
            write_pdb(system, sval)
            model += "MODEL " + str(s) + "\n"
            model += sval.getvalue()
            model += "ENDMDL\n"

            # in this case we have only one (combined) system to display
            if gridlist is None:
                models += model
            # in this case we just want to display this system at the moment
            else:
                models = model

            # If displaying on a grid, remove all existing models
            if gridlist is not None:
                gx = gridlist[s][0]
                gy = gridlist[s][1]
                viewer = (gx, gy)
                # print(viewer)
                self.xyzview.removeAllModels(viewer=viewer)
            else:
                viewer = (0, 0)

            # in the case of a grid we need to display at each iteration
            # otherwise we only display for the final iteration
            if (gridlist is not None) or (gridlist is None and
                                          s == len(syslist) - 1):
                i = 0
                for fragid in reorder_fragments(syslist[0]):
                    frag = syslist[0][fragid]
                reorder = reorder_fragments(syslist[0])
                for fragid in reorder:
                    frag = syslist[0][fragid]
                    if fragid in this_colordict:
                        color = this_colordict[fragid]
                    else:
                        color = 'black'

                    if not cartoon:
                        if stick_radius > 0.0:
                            self.xyzview.addModelsAsFrames(models, "pdb",
                                                           {"keepH": "true"},
                                                           viewer=viewer)
                            self.xyzview.setStyle({'model': -1},
                                                  {"stick":
                                                  {'radius': stick_radius,
                                                   'color': this_stick_color}},
                                                  viewer=viewer)
                        else:
                            self.xyzview.addModelsAsFrames(models, "pdb",
                                                           {"keepH": "true"},
                                                           viewer=viewer)
                            self.xyzview.setStyle({'model': -1},
                                                  {"line": {'color': 'black'}},
                                                  viewer=viewer)

                    for at in frag:
                        if cartoon:
                            self.xyzview.addModelsAsFrames(models,
                                                           viewer=viewer)
                            self.xyzview.setStyle({'model': -1,
                                                   'serial': i + 1},
                                                  {"cartoon":
                                                  {'color': color}},
                                                  viewer=viewer)
                        else:

                            self.xyzview.addModelsAsFrames(models, "pdb",
                                                           {"keepH": "true"},
                                                           viewer=viewer)
                            self.xyzview.setStyle({'model': -1, 'serial': i+1},
                                                  {"sphere": {'scale': 0.2,
                                                              'color': color}},
                                                  viewer=viewer)
                        i += 1

            if gridlist is not None:
                self.xyzview.render()
        self.display_cell(syslist[0].cell)

        # Finish Drawing
        if len(syslist) > 1 and gridlist is None:
            self.xyzview.animate({'loop': "forward", 'interval': 1000})
        self.xyzview.zoomTo()
        if zoom is not None:
            self.xyzview.zoom(zoom)

        if show:
            self.xyzview.show()

    def display_cell(self, cell) -> None:
        if cell is None:
            return
        self.xyzview.addUnitCell({"model": -1},
                                 {"box": {"color": "black"},
                                 "alabel": "", "blabel": "", "clabel": ""})


class VSimVisualizer():
    def __init__(self, filename: str, xsize: int = 600, ysize: int = 600) -> None:
        from gi.repository import v_sim, GLib, Gtk
        self.win = v_sim.UiRenderingWindow.new(xsize, ysize, True, True)
        self.loop = GLib.MainLoop.new(None, False)
        self.win.connect_object('destroy', GLib.MainLoop.quit, self.loop)
        self.main = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        self.main.add(self.win)
        self.main.show_all()
        self._set_file(filename)

    def _set_file(self, filename: str) -> None:
        from gi.repository import v_sim
        self.data = v_sim.DataAtomic.new(filename, None)
        self.data.load(0, None)
        self.win.getGlScene().setData(self.data)
        # v_sim.basic_parseConfigFiles()

    def show(self) -> None:
        # from gi.repository import GLib
        self.loop.run()

    def colorize_by_fragments(self) -> None:
        from gi.repository import v_sim
        self._scene_colorizer(v_sim, self.data, self.win.getGlScene())

    def _scene_colorizer(self, v_sim, data, scene) -> None:
        nodes = scene.getNodes()
        frag = data.getNodeProperties("Fragment")
        c = v_sim.DataColorizerFragment.new()
        c.setNodeModel(frag)
        nodes.pushColorizer(c)
        c.setActive(True)

    def colorizer_script(self, filename: str) -> None:
        import inspect
        towrite = ['scene = ' +
                   'v_sim.UiMainClass.getDefaultRendering().getGlScene()',
                   'data = scene.getData()']
        for line in inspect.getsource(self._scene_colorizer).split('\n')[1:]:
            towrite.append(line.lstrip(' '))
        f = open(filename, 'w')
        for line in towrite:
            f.write(line + '\n')
        f.close()


class VMDGenerator():
    """
    This class contains the routines you would use for visualization of
    a system using the VMD program.

    Attributes:
      representation (str): the vmd representation to draw with.
        https://www.ks.uiuc.edu/Research/vmd/allversions/repimages/#representations
      color (int): the default color to draw with.
    """

    def __init__(self, representation: str = "CPK", color: int = 16):
        self.representation = representation
        self.color = color

    def visualize_fragments(
            self,
            system: BigDFT.Systems.System,
            scriptfile: str,
            geomfile: str,
            fragcolors: Optional[Dict[int, int]] = None
        ):
        """
        This generates a script for visualizing the fragmentation of a
        system using VMD.

        Args:
          system (BigDFT.Systems.System): the system to visualize.
          scriptfile (str): the name of the file to write the vmd script
            to (usually has extension .tcl)
          geomfile (str): the filename for where to write an xyz file
            of the system.
          fragcolors (dict): optionally, a dictionary from fragment ids to
            fragment colors. Colors are integers between 0 and 32.
        """
        from BigDFT.Fragments import Fragment
        from BigDFT.IO import XYZWriter

        # To create the XYZ file, we first make one big fragment.
        geomorder = Fragment()
        for fragid, frag in system.items():
            geomorder += frag

        # Then write it to file.
        with XYZWriter(geomfile, len(geomorder)) as ofile:
            for at in geomorder:
                ofile.write(at)

        # Get the matching so we can write the correct atom indices.
        matching = system.compute_matching(geomorder)

        # If fragcolors is not specified, we will generate it ourselves.
        if fragcolors is None:
            fragcolors = {}
            for i, s in enumerate(system):
                # 16 is black, which we will reserve.
                if i % 32 == 16:
                    c = str(32)
                else:
                    c = str(i % 32)
                fragcolors[s] = c

        # The header of the script file draws the whole system in black.
        outstr = self._get_default_header(geomfile)

        # This part colors individual fragments.
        modid = 1
        for fragid, frag in system.items():
            if fragid not in fragcolors:
                continue
            outstr += "mol addrep 0\n"
            outstr += """mol modselect """ + str(modid) + """ 0 index """
            outstr += " ".join([str(x) for x in matching[fragid]])
            outstr += "\n"
            outstr += """mol modcolor """
            outstr += str(modid) + """ 0 ColorID """ + \
                str(fragcolors[fragid]) + """\n"""
            modid += 1

        # Finally, write to file.
        with open(scriptfile, "w") as ofile:
            ofile.write(outstr)

    def _get_default_header(self, geomfile: str) -> str:
        outstr = """mol default style """+self.representation+"""\n"""
        outstr += """mol new """ + geomfile + "\n"
        outstr += """mol modcolor 0 0 ColorID """+str(self.color)+"""\n"""

        return outstr


def get_distinct_colors(keys, name: str = "tab20", fuzz: bool = True) -> dict:
    """
    This generates a dictionary of distinct colors based on a matplotlib
    colormap.

    Args:
        keys (list): a list of keys.
        name (str): the name of the matplotlib colormap to use.
        fuzz (bool): some color maps (included tab20) only have a distinct
            set of colors. The fuzz option adds increased randomness to make
            up for this.

    Returns:
        (dict): a dictionary mapping matplotlib keys to RGB colors.
    """
    from matplotlib import pyplot as plt
    from numpy import linspace
    from random import sample, uniform

    def fuzz_fn(x):
        fuzzed = (x[i] + uniform(-0.1, 0.1) for i in range(3))
        return [max(0.0, min(y, 1.0)) for y in fuzzed]

    # Map using a color map
    cmap = plt.get_cmap(name)
    xvals = linspace(0, 1, len(keys))
    vals = {x: list(cmap(xvals[i])) for i, x in
            enumerate(sample(keys, len(keys)))}

    # Add some random fuzz
    if fuzz:
        vals = {x: fuzz_fn(y) for x, y in vals.items()}

    return vals


def truncate_colormap(
        cmap, 
        compressed_values: Optional[List[Union[int, float]]] = None, 
        vmin: Union[int, float] = 0.0, 
        vmax: Union[int, float] = 1.0, 
        N: int = -1
    ):
    """Truncate a colormap from a given cmap. Taken from
    https://stackoverflow.com/questions/40929467/
    how-to-use-and-plot-only-a-part-of-a-colorbar-in-matplotlib.
    """
    from matplotlib import colors
    from numpy import linspace
    if N == -1:
        N = cmap.N
    maxv = vmax
    minv = vmin
    if compressed_values is not None:
        maxv = max(compressed_values)
        minv = min(compressed_values)
    new_cmap = colors.LinearSegmentedColormap.from_list(
         'trunc({name},{a:.2f},{b:.2f})'.format(name=cmap.name,
                                                a=minv, b=maxv),
         cmap(linspace(minv, maxv, N)))
    return new_cmap


def get_atomic_colordict(sys: BigDFT.Systems.System) -> dict:
    """
    Builds a dictionary of colors for a system where each atom is its own
    fragment. This uses the built in colors of jmol.

    Args:
        sys (BigDFT.Systems.System): a system where each atom contains a
        single atom.

    Returns:
        dict: a dictionary mapping fragment ids to colors.
    """
    result = {}
    for fragid, frag in sys.items():
        if len(frag) != 1:
            raise ValueError("Fragment must be made up of exactly one atom")
        result[fragid] = _atoms[frag[0].sym]
    return result


def get_colordict(
        keys: list, 
        field_vals: Optional[list] = None, 
        vmin: Optional[float] = None, 
        vmax: Optional[float] = None, 
        colorcode: Optional[str] = None,
    ) -> dict:
    """
    Build a dictionary of colors for each of the keys.
    If the field_dict is provided, order the colors of the keys in terms
    of the sorting of the filed values

    Args:
        keys (list): keys of the color dictionary
        field_vals(list) : values of the field to decide the colors of the keys
        vmin (float): minimum value of the colors.
            Useful to extend the range below the minimum of field_vals.
        vmax (float): maximum value of the colors.
            Useful to extend the range below the maximum of field_vals.
        colorcode (str): the string of the colorcode.
             Default is 'rainbow' if no field_vals are present. If
             field_vals have negative data, default is seismic. Otherwise
             Reds.
    Returns:
        dict: the dictionary of the keys, and the corresponding colors.
            The dictionary contains also special keys arguments
            to be passed to the `colorbar` method of matplotlib:

               * '__mappable__', which
                 is associated the reference to the matplotlib.ScalarMappable
                 instance that is associated to the colordict. This instance
                 can be useful to draw colorbars associated to such a
                 colordict.

    """
    import numpy as np
    from matplotlib.pyplot import get_cmap
    from matplotlib.colors import Normalize
    from matplotlib.cm import ScalarMappable

    # Optional parameters
    if field_vals is None:
        field_vals = [float(x) for x in range(len(keys))]
        compressed_values = field_vals
        center_to_zero = False
        if colorcode is None:
            colorcode = "rainbow"
    else:
        compressed_values = np.array(
            [val for val in field_vals if not np.isnan(val)])
        center_to_zero = any(compressed_values < 0.0)
        if colorcode is None:
            if center_to_zero:
                colorcode = "seismic"
            else:
                colorcode = "Reds"

    # Normalize and center
    mx = np.max(compressed_values)
    if vmax is not None:
        mx = max(mx, vmax)
    mn = np.min(compressed_values)
    if vmin is not None:
        mn = min(mn, vmin)
    norm = Normalize(vmin=mn, vmax=mx)
    if center_to_zero:
        shift = min(mn, -mx)
        top = max(mx, -mn)
    else:
        shift = mn
        top = mx
    compressed_values -= shift
    if top > shift:
        compressed_values /= (top-shift)

    cmap = get_cmap(colorcode)
    cvals = []
    icv = 0
    for v in field_vals:
        if np.isnan(v):
            cvals.append('None')
        else:
            y = compressed_values[icv]
            cvals.append(_rgb_to_html(
                tuple(map(int, np.array(cmap(y)[0:3])*255))))
            icv += 1
    sm = ScalarMappable(norm=norm,
                        cmap=truncate_colormap(cmap, compressed_values))

    colordict = {x: y for x, y in zip(keys, cvals)}
    colordict['__mappable__'] = sm
    return colordict


def _rgb_to_html(rgb: List[int]) -> str:
    html = [0] * 6
    htmls = [0] * 6
    html[0] = int(rgb[0]/16)
    html[1] = (rgb[0] % 16)
    html[2] = int(rgb[1]/16)
    html[3] = (rgb[1] % 16)
    html[4] = int(rgb[2]/16)
    html[5] = (rgb[2] % 16)
    for j in range(6):
        if (html[j] == 10):
            htmls[j] = 'A'
        elif (html[j] == 11):
            htmls[j] = 'B'
        elif (html[j] == 12):
            htmls[j] = 'C'
        elif (html[j] == 13):
            htmls[j] = 'D'
        elif (html[j] == 14):
            htmls[j] = 'E'
        elif (html[j] == 15):
            htmls[j] = 'F'
        else:
            htmls[j] = html[j]
        html_string = '#'+str(htmls[0])+str(htmls[1]) + \
            str(htmls[2])+str(htmls[3])+str(htmls[4])+str(htmls[5])
    return html_string


def contrasting_text_color(hstr: str) -> str:
    """
    Input a string without hash sign of RGB hex digits to compute
    complementary contrasting color such as for fonts.
    Function borrowed from
    https://stackoverflow.com/questions/1855884/\
        determine-font-color-based-on-background-color

    Args:
        hstr (str): the color string, preferably in hex.
    Returns:
        str: string of the contrasting color, black or white.
    """
    from matplotlib.colors import to_hex
    hex_str = to_hex(hstr)
    (r, g, b) = (hex_str[1:3], hex_str[3:5], hex_str[5:])
    is_dark = (int(r, 16) * 0.299 + int(g, 16) * 0.587 + int(b, 16) * 0.114)
    return '#000000' if 1 - is_dark / 255 < 0.5 else '#ffffff'


def _example() -> None:
    """Visualization Example"""
    from BigDFT.Systems import System
    from BigDFT.Fragments import Fragment
    from BigDFT.IO import XYZReader

    # Read in a system.
    sys = System()
    with XYZReader("SiO") as ifile:
        for i, at in enumerate(ifile):
            sys["FRA:"+str(i)] = Fragment([at])

    # Display the system.
    viz = InlineVisualizer(400, 300)
    viz.display_system(sys)

    # Change the colors
    colordict = get_distinct_colors(list(sys))
    viz.display_system(sys, colordict=colordict)


if __name__ == "__main__":
    _example()
