"""A module to extend the output by dna_feature_viewer.

"""


def plot_field_vals(record, ax, xlim):
    """Plot all the field data available in the same axis."""
    ist = record.start_index
    for fv in record.field_vals:
        if fv['errors'] is not None:
            errors = fv['errors'][xlim[0]-ist:xlim[1]-ist]
        else:
            errors = None
        extra_range_kwargs = {k: v[xlim[0]-ist:xlim[1]-ist]
                              for k, v in fv.get('array_kwargs',
                                                 {}).items()}

        plot_one_field_vals(ax, range(*xlim),
                            fv['values'][xlim[0]-ist:xlim[1]-ist],
                            label=fv['label'], errors=errors,
                            **extra_range_kwargs, **fv['kwargs'])


def violinplot_color(violin):
    return violin["bodies"][0].get_facecolor().flatten()


def violinplot_label(violin, label):
    import matplotlib.patches as mpatches
    color = violinplot_color(violin)
    return (mpatches.Patch(color=color, label=label), label)


def add_patch(ax, patch):
    handles, labels = ax.get_legend_handles_labels()
    handle, label = patch
    handles.append(handle)
    labels.append(label)
    return dict(handles=handles, labels=labels)

def _spec_calls(obj, specs):
    for spec, args in specs.items():

        if spec == 'func':
            args(obj)
            continue

        rearg = args.copy()
        if 'args' in rearg:
            arg = rearg.pop('args')
        else:
            arg = []
        getattr(obj, spec)(*arg, **rearg)


def plot_one_field_vals(ax, xrange, field_vals, kind='bar', specs={},
                        errors=None, kind_specs={}, **kwargs):
    """Plot the data in the axis with their own specification."""
    import matplotlib.ticker as plticker
    from futile.Utils import kw_pop
    if kind in ['violinplot']:  # unsupported label keyword
        new_kw, tlb = kw_pop('label', None, **kwargs)
        vp = getattr(ax, kind)(list(field_vals), positions=xrange, **new_kw)
        _spec_calls(vp, kind_specs)

        ax.scatter(xrange, field_vals.mean(axis=1),
                   color=violinplot_color(vp), label=tlb, marker='_')
        # vpl = violinplot_label(vp, tlb)
        # specs.setdefault('legend', {}).update(add_patch(ax, vpl))
    else:
        kd = getattr(ax, kind)(xrange, field_vals, **kwargs)
        _spec_calls(kd, kind_specs)

    loc = plticker.MultipleLocator(base=5.0)

    if errors is not None:
        ax.errorbar(xrange, field_vals, errors, fmt='none',
                    elinewidth=0.5, ecolor='k')

    _spec_calls(ax, specs)

    ax.xaxis.tick_top()
    ax.xaxis.set_major_locator(loc)


def restrict_features(features, groups):
    """Crop the features in the provided groups."""
    from dna_features_viewer import GraphicFeature
    feature_per_group = {}
    for line, chunks in groups.items():
        feature_per_group[line] = []
        for istart, iend in chunks:
            feature_per_line = [[] for feat in features]
            for ifeat, feat in enumerate(features):
                lb = ''
                for label, ft in feat.items():
                    if lb is not None:
                        lb = label
                    for (start, end), color in ft.items():
                        if start >= iend or end < istart:
                            continue
                        gft = GraphicFeature(start=start, end=end, strand=0,
                                             color=color, thickness=10,
                                             label=lb)
                        lb = None
                        feature_per_line[ifeat].append(gft)
            feature_per_group[line].append(feature_per_line)
    return feature_per_group


class SequenceRecord():
    """Representation of a Sequence in term of a dna_feature_viewer record.

    Args:
        sequence (str): string to represent.
        start_index(int): integer indicating the residue id of
            the starting point.
        line_length (int): number of residues to be represented in the line
    """
    def __init__(self, sequence, start_index=1, line_length=None):
        self.sequence = sequence
        self.start_index = start_index
        self.features = []
        self.field_vals = []
        self.active_domain = [[start_index, start_index+len(sequence)]]
        linelen = line_length if line_length is not None else len(sequence)
        self.set_line_length(linelen)
        self.highlight_chunks = {}

    def append_feature(self, feature, label=''):
        """Insert a dictionary of colors.

        Args:

            features (dict): dictionary of features to be plotted.
               each dictionary key is the name of the features, and the values
               are a dictionary of the form {(start_index, end_index): color}
               where start and end indices are calculated taking into account
               the start_index.

            label(str): label of the feature
        """
        self.features.append({label: feature})

    def append_sequence_field(self, field_vals, label='', errors=None,
                              array_kwargs={}, **kwargs):
        """Introduce a sequence field to be plot.

        Args:
            field_vals (array-like): values to be represented, in the order of
                sequence residues.
            errors (array-like): errorbar on to be represented, in the order of
                sequence residues.
            label (str): label of the values, to be put in the legend.
            array_kwargs (dict): dictionary of kargs whose values are arrays of
                the same length of field_vals
            **kwargs: keyword arguments to be employed in the
                `plot_one_field_vals` function.

        """
        self.field_vals.append({'values': field_vals,
                                'label': label,
                                'errors': errors,
                                'array_kwargs': array_kwargs,
                                'kwargs': kwargs})

    def define_interesting_chunks(self, chunks):
        """Introduce the chunks to be plotted separately.

        Args:
            chunks (list): list of tuples (start,end) in the sequence
               reference. Start index is considered.
        """
        self.active_domain = chunks
        self.split_sequence_in_groups()

    def define_highlight_regions(self, regions):
        """Introduce chunks to be highlighted.

        Args:
            chunks (dict): tuples (start,end) as keys, and colors
                in the sequence reference. Start index is considered.
        """
        self.highlight_chunks = regions

    def split_sequence_in_groups(self):
        """Define the groups in which to split the sequence representation."""
        istop = self.start_index
        remaining_space = self.line_length
        groups = {}
        iline = 0
        for istart, iend in self.active_domain:
            icursor = istart
            while(istop < iend):
                istop = min(iend, icursor+remaining_space)
                groups.setdefault(iline, []).append((icursor, istop))
                remaining_space -= istop - icursor
                icursor = istop
                if remaining_space == 0:
                    remaining_space = self.line_length
                    iline += 1
        self.groups = groups
        self.get_nlines()

    def set_line_length(self, line_length):
        """Define the conditions associated to the limited length in plots."""
        self.line_length = line_length
        self.split_sequence_in_groups()

    def get_nlines(self):
        """Extract the number of lines of the figures."""
        nlines = len(self.groups)
        if len(self.field_vals) > 0:
            nlines *= 2
        self.nlines = nlines

    def get_stride(self):
        """Get the number of axis per line."""
        self.get_nlines()
        return 2 if self.nlines == 2*len(self.groups) else 1

    def define_axis_grids(self, **kwargs):
        """Define the axis on which to plot the groups.

        Args:
            **kwargs: arguments for `py:func:matplotlib.pyplot.figure` method.
        """
        from matplotlib.gridspec import GridSpec
        import matplotlib.pyplot as plt
        stride = self.get_stride()
        gs = GridSpec(ncols=self.line_length, nrows=self.nlines, wspace=2)
        axsd = {}
        fig = plt.figure(**kwargs)
        for line, chunks in self.groups.items():
            iline = stride*line
            reference = chunks[0][0]
            icursor = 0
            for istart, iend in chunks:
                jstart = istart - reference
                jend = iend - reference
                jstart = icursor
                jend = iend - istart + icursor
                axsd.setdefault(iline, []).append(fig.add_subplot(
                    gs[iline, jstart:jend]))
                if stride == 2:
                    axsd.setdefault(iline+1, []).append(fig.add_subplot(
                        gs[iline+1, jstart:jend]))
                icursor = jend
        # include the remaining space to combine with further plots
        if jend < self.line_length:
            # ax = fig.add_subplot(gs[iline:, jend:self.line_length])
            # ax.set_visible(False)
            ilast = len(axsd) - 1
            axsd.setdefault(ilast, []).append(
                gs[iline:, jend:self.line_length])
        self.fig = fig
        self.axsd = axsd

    def compose_record(self, **kwargs):
        """Create the record from the class.

        Args:
            **kwargs: keyword arguments for `GraphicRecord`.
        """
        from dna_features_viewer import GraphicRecord
        istart = self.active_domain[0][0]
        iend = self.active_domain[-1][-1] + 1
        sequence = self.sequence[istart-self.start_index:iend-self.start_index]
        record = GraphicRecord(sequence, first_index=istart, features=[],
                               ticks_resolution=5,
                               feature_level_height=self.level_height,
                               **kwargs)
        record.sequence = sequence
        record.sequence_length = len(sequence)
        self.record = record

    # Set the distance covered by one feature level
    level_height = 0.55*0.5

    # shrink of the space occupied by a sequence
    sequence_level_shrink = 0.7

    # lower bound of the y axis
    y_lower_bound = level_height/sequence_level_shrink

    # extra buffer in y
    y_extra_buffer = 1

    # total y buffer
    total_y_buffer = y_extra_buffer*level_height + y_lower_bound

    lb = 0.52
    rb = 1 - lb

    def height(self, ft):
        """Height of the axis for a given number of features. """
        return self.level_height*(ft+self.y_extra_buffer)

    def set_axis_height(self, ax, hgt):
        """ Impose the total height considering the space for the sequence."""
        # ax.set_ylim([-1.5*self.level_height, self.height(hgt)])
        ax.set_ylim([-self.y_lower_bound,
                     self.height(hgt)])

    def nft_to_height(self, nft):
        return self.height(nft) + self.total_y_buffer

    def total_height(self, buffer=True):
        """Total height of the axis, including (or not) the sequence space."""
        return self.height(len(self.features)) + \
            (self.total_y_buffer if buffer else 0)

    def display(self, total_height=None, level_offset=0, on_top_of=None):
        """ Represent record information.

        Args:
            total_height (float): size of the axis height.
            Useful when representing more than one record.
            level_offset (int): starting coordinate of the level.
            on_top_of (SequenceRecord): base record on top of which to plot
                the present data. Employ the groups of the base record.

        Returns:

            tuple: (fig, axsd) matplotlib figure and a dictionary of
                {line: axs}, where axs is a list of matplotlib axes employed
                in a given line.
        """
        if on_top_of is None:
            stride = self.get_stride()
        else:
            stride = on_top_of.get_stride()
        if total_height is None:
            total_height = self.total_height()
        if on_top_of is None:
            self.define_axis_grids(figsize=(15.0/80.0*self.line_length,
                                            self.nlines*total_height))
            fig = self.fig
            axsd = self.axsd
            groups = self.groups
            base = True
        else:
            fig = on_top_of.fig
            axsd = on_top_of.axsd
            groups = on_top_of.groups
            base = False
        self.compose_record()
        feature_per_group = restrict_features(self.features, groups)
        for line in range(len(groups)):
            for iline, (xlim, ax, fts) in enumerate(zip(
                    groups[line], axsd[stride*line], feature_per_group[line])):
                location = xlim
                if not base:
                    xlim_t = (self.start_index,
                              self.start_index+len(self.sequence))
                    location = (max(xlim[0], xlim_t[0]),
                                min(xlim[1], xlim_t[1]))
                record = self.record.crop(location)
                if base:
                    record.plot(ax=ax, plot_sequence=False,
                                with_ruler=stride == 1,
                                x_lim=(xlim[0]-self.lb, xlim[1]-self.rb),
                                annotate_inline=False)
                for ilevel, feats in enumerate(fts):
                    for gft in feats:
                        record.plot_feature(
                            ax, gft,
                            level=ilevel+level_offset)
                        if iline > 0:
                            continue
                        ax.text(xlim[0]-2*self.lb,
                                (ilevel+level_offset)*self.level_height,
                                gft.label, ha="right", va="center",
                                fontdict={'size': 11})
                record.plot_sequence(
                    ax, location=location,
                    y_offset=(1-level_offset)/self.sequence_level_shrink)
                if base:
                    self.set_axis_height(ax,
                                         total_height/self.level_height - 1.5)
                if stride == 1:
                    if base:
                        ax.set_xlim((xlim[0]-self.lb, xlim[1]-self.rb))
                    continue
                ax1 = axsd[stride*line+1][iline]
                # the get_shared_x_axes function returns a GrouperView
                # which is now immutable. To join new axis one has to create a
                # internal function to access the Grouper
                _join_x_axes(ax1, ax)
                plot_field_vals(self, ax1, location)
                if base:
                    ax1.set_xlim((xlim[0]-self.lb, xlim[1]-self.rb))
                    ax1.grid(True)
                if iline > 0:
                    ax1.set_yticklabels([])
                    ax1.set_ylabel('')
                    lg = ax1.get_legend()
                    if lg is not None:
                        lg.remove()
                    ax1.set_xlabel('')
        return fig, axsd


def _join_x_axes(ax1, ax):
    view = ax1.get_shared_x_axes()
    if hasattr(view, 'join'):
        view.join(ax)
    else:
        ax1._shared_axes['x'].join(ax)


def colordict_to_feature(colordict, sequence_fragments, start_index=0,
                         unify_same_colors=False):
    """Create the feature data starting from a colordict.

    Useful for conversion between the native representation method and
    the sequence one. Merge together residues which ehibit the same color.

    Args:
        sequence_fragments (list): order of the fragments of the sequence.
        start_index (int): initial index of the sequence
        colordict (dict): dictionary of the feature colors
        unify_same_colors (bool): if true create a rectangle for contiguous
            residues having the same color. Ignore white colors.

    Returns:
        dict: feature dictionary to be passed into `append_feature`
    """
    from matplotlib.colors import same_color
    from numpy import nan
    istart = start_index
    feature = {}
    prev_cl = None
    jstart = istart
    iend = istart
    for ifrag, frag in enumerate(sequence_fragments):
        cl = colordict.get(frag, 'w')
        if unify_same_colors:
            if ifrag == 0 and not same_color(cl, 'w'):
                jstart -= 1
            if prev_cl is None:
                prev_cl = cl
                continue
            if cl != prev_cl or ifrag == len(sequence_fragments)-1:
                if not same_color(prev_cl, 'w'):
                    if ifrag == len(sequence_fragments)-1:
                        iend += 1
                    feature[(jstart+1, iend+1)] = prev_cl
                    if ifrag == len(sequence_fragments)-1:
                        iend -= 1
                elif ifrag == len(sequence_fragments)-1:
                    if not same_color(cl, 'w'):
                        feature[(istart+1, iend+1)] = cl

                jstart = iend
                prev_cl = cl
        else:
            feature[(istart, iend+1)] = cl
        istart += 1
        iend += 1
    return feature


def get_chain_id(frags):
    """Commodity function to extract the chain id."""
    from BigDFT.BioQM import construct_frag_tuple
    ch, res, num = construct_frag_tuple(frags[0])
    return ch


def get_data_from_field_vals(sys, field_vals, lookup=None):
    """Extract the actual data from the field_vals keyword."""
    if isinstance(field_vals, dict):
        return get_values_and_errors(field_vals['data'], lookup)
    elif isinstance(field_vals, str):
        return get_values_and_errors(sys.fragment_values(field_vals), lookup)
    else:
        return get_values_and_errors(field_vals, lookup)


def get_values_and_errors(fv, lookup=None):
    """Discriminate between values and values with errors."""
    from numpy import array
    from BigDFT.BioQM import filter_field_vals
    if isinstance(fv, dict):
        fvt = array(fv['field_vals'])
        fve = fv.get('errors')
        if fve is not None:
            fve=filter_field_vals(array(fve), lookup)
            # if lookup is not None:
            #     fve = fve[lookup]
    else:
        fvt = array(fv)
        fve = None
    fvt = filter_field_vals(fvt, lookup)
    # if lookup is not None:
    #     fvt = fvt[lookup]
    return fvt, fve


def sys_into_records(sys, features={}, shift={}, chain_labels={},
                     line_length=80, restrict_to={}, field_vals={}):
    """Transform a `BigDFT.BioQM.BioSystem` into a list of `SequenceRecord`.

    Args:
        sys (bigDFT.BioQM.BioSystem): the system to be represented.
        features (dict): dictionary of the features to plot.
            the dictionary can be of the form: {label: feature}, where
            feature may be either a string to be passed to
            `py:func:~BigDFT.BioQM.BioSystem.fragment_values` method
            or alternatively a colordict. If label contains the keyword
            ``highlight`` then the unify_same_colors approach is applied to the
            feature.
        shift (dict): shift to be applied to each of the chain id.
        chain_labels (dict): label to be written in the figure title,
            per chain. A value `None` is interpreted by excluding the chain
            from the records.
        line_length (int): number of residues par line.
        restrict_to (dict): dictionary of chunks to be plot per chain id.
        field_vals (dict): {label: {``data``: field_vals, ``kwargs``: kwargs,
            ``specs``: specs}}
            dictionary. Accepts also the {`label`: field_vals}  format.
            In this latter case, the field vals value may also be a string
            which can be passed to
            `py:func:~BigDFT.BioQM.BioSystem.fragment_values` method.

    Returns:
        dict: dictionary of {label: `SequenceRecord`}, one per system sequence.
    """
    from numpy import nanmin, nanmax
    from BigDFT.BioQM import filter_field_vals, construct_frag_tuple
    yM = -1e100
    ym = 1e100
    for label, fv in field_vals.items():
        fvt, fve = get_data_from_field_vals(sys, fv)
        ym = min(ym, nanmin(fvt))
        yM = max(yM, nanmax(fvt))
    ylim = [ym, yM]
    records = {}
    for seq, frags in zip(sys.chains, sys.sequences_to_fragments):
        lu = [sys.fragment_names.index(f) if f in sys.fragment_names else None
              for f in frags]
        ch = get_chain_id(frags)
        title = chain_labels.get(ch, 'Chain: '+ch)
        if title is None:
            continue
        default_shift = construct_frag_tuple(frags[0]).id - 1
        start_index = shift.get(ch, 0) + default_shift + 1
        record = SequenceRecord(str(seq.sequence),
                                line_length=line_length,
                                start_index=start_index)
        chunks = restrict_to.get(ch)
        if chunks is not None:
            record.define_interesting_chunks(chunks)
        for label, feat in features.items():
            if not isinstance(feat, dict):
                cd = sys.colordict(color_by=feat)
            else:
                cd = feat
            feature = colordict_to_feature(
                cd, frags, start_index=start_index,
                unify_same_colors='highlight' in label)
            lb = label.lstrip('highlight') if 'highlight' in label else label
            record.append_feature(feature, label=lb)
        for label, fv in field_vals.items():
            fvt, fve = get_data_from_field_vals(sys, fv, lookup=lu)
            specs = {'tick_params': {'args': ['x'], 'top': True,
                                     'which': 'both', 'pad': 1},
                     'set_ylim': {'args': ylim},
                     'legend': {'loc': 'best'}}
            kwargs = {}  # 'label': label}
            array_kwargs = {}
            if isinstance(fv, dict):
                specs.update(fv.get('specs', {}))
                kwargs.update(fv.get('kwargs', {}))
                array_kwargs.update({k: filter_field_vals(v, lu)
                                     for k, v in fv.get('array_kwargs', {}).items()})
            record.append_sequence_field(field_vals=fvt, label=label,
                                         errors=fve, specs=specs,
                                         array_kwargs=array_kwargs,
                                         **kwargs)
        records[title] = record
    return records


def display_records(records, *args, **kwargs):
    """Display a stack of records.

    Args:
        records(list): dictionary of `SequenceRecord` objects to be plot
            one after another.
        *args: further lists of objects that will be superimposed
            at the first argument. should have the same number of elements.
            Their labels are ignored in favour of the first.
        **kwargs:
            keyword arguments, like:

                records_lookup: list of lists indicating which
                    record of the first list should be associated to the
                    records of the others. Put `None` for records which
                    should not be considered in the comparison.
    Returns:
        list: list of (fig, axsd) tuples, containing the figure and
            the matplotlib axes dictionary employed per sequence.
    """
    figures_and_axes = []
    offsets = {}
    lookup = kwargs.get('records_lookup')
    if lookup is None:
        lookup = [list(range(len(newrec))) for newrec in args]
    for irec, (title, record) in enumerate(records.items()):
        offset = len(record.features) + 1.0/record.sequence_level_shrink
        for iarg, newrec in enumerate(args):
            for krec, (_, otherrec) in enumerate(newrec.items()):
                jrec = lookup[iarg][krec]
                if irec != jrec or jrec is None:
                    continue
                offsets.setdefault(iarg, {}).setdefault(irec, offset)
                offset += len(otherrec.features) + \
                    1.0/record.sequence_level_shrink
        fig, axsd = record.display(total_height=record.nft_to_height(offset))
        axsd[0][0].set_title(title, loc='left', y=0.8,
                             fontdict=dict(fontsize=14, fontweight='bold'))
        figures_and_axes.append((fig, axsd))
    for iarg, newrec in enumerate(args):
        for irec, (title, record) in enumerate(records.items()):
            for krec, (_, otherrec) in enumerate(newrec.items()):
                jrec = lookup[iarg][krec]
                found = jrec == irec
                if found:
                    break
            if not found:
                continue
            otherrec.display(on_top_of=record,
                             level_offset=offsets[iarg][irec])
    return figures_and_axes
