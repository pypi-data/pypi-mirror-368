def find_applications(prefix, pattern='*', exclude=None):
    apps = []
    for p in os.environ['PATH'].split(':'):
        apps += [p+"/"+x for x in glob.glob("%s-%s" % (prefix, pattern), root_dir=p)]

    result = {}
    for a in apps:
        name = os.path.basename(a).replace(prefix+'-', '')

        if name.split('-')[0] in (exclude or []):
            continue
        
        result[name] = a

    return result


def parse_me():
    ''' Returns the current application name compontens
    (e.g. ['camagic', 'source', 'epics'])
    '''
    return os.path.basename(sys.argv[0]).split('-')

    
def parse_apps():
    ''' Separates command line arguments in sub-applications.

    The idea is that the top-level camagick calls sub-applications which
    have a name that begins with 'camagick-'. There are 3 types of
    subapplications:
    
      - Data sources (begin with 'camagick-source-...'), which create
        datasets i.e. fill the stash, but don't consume

      - Data sinks (begin with 'camagick-display-...'), which don't
        create any datasets, just view/consume the stash non-destructively
        (i.e. don't remove data)

      - Filters; these may begin with any word ('camagick-...'), and they
        take the stash and modify it (i.e. add new datasets).

    To stay modular we don't know anything about the applications and their
    command lines, but we somehow still wish to separate command line parameters
    from one another. To do this, we move from subapplication word marker
    to word marker (i.e. all display and source applications we can find
    in $PATH, and then all filters we can find in $PATH).

    This function returns an ordered dictionary as
    `{'name': ('application', (parameters...)), ...}`
    '''
    
    me = parse_me()

    # There's a general pipe structure here, but the "source" and "display"
    # are special in the sense that they're starting points / end points of
    # the pipe and require specific kinds of synchronisation.
    filters  = find_applications(me[0], exclude=['source', 'display'])

    specials = {
        'source': find_applications('%s-source' % me[0]),
        'display': find_applications('%s-display' % me[0])
    
    
    if len(sys.argv) < 2:
        print("Usage:\n\n"
              "    %s source [source... [source...]]\n"\
              "            [filter [filter... [filter...]]]\n"\

        if len(specials['source']):
            print("Available sources ('%s source <name>' for help):\n\n" % me[0],
                  *['   %s\n' % s for s in specials['source']])

        if len(specials['display']):
            print("Available displays ('%s display <name>' for help):\n\n" % me[0],
                  *['   %s\n' % d for d in specials['display'])
            

        if len(filters):
            print("Available filters ('%s <name>' for help):\n\n" % me[0],
                  *['   %s\n'%c for c in apps])

    sub_command = None
    sub_params = []
    applications = OrderedDict()
    
    for arg in sys.argv[1:] + ['']:

        # Try to find argument in any of the sub-applications lists
        if arg in [k for k in specials] + [f for f in filters] + ['']:

            # Store the previous sub-command invocation
            if sub_command is not None:
                try:
                    # reconstruct <special>-<command> invocation
                    tmp = specials[sub_command]

                    try:
                        app = tmp[sub_params[0]]
                    except KeyError:
                        logging.error("Invalid %s: %s" % (sub_command, sub_params[0]))
                        return None
                    
                    sub_command += "-"+sub_params[0]
                    sub_params = sub_params[1:]
                    
                except KeyError as e:
                    # regular <filter> invocation
                    app = filters[sub_command]

                applications[sub_command] = (app, sub_params)
                applications.move_to_end(sub_command)

            sub_command = arg
            sub_params = []
        else:
            sub_params.append(arg)

    return applications
