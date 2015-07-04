def learn(args):        
    from zope import component

    from pyzcasp import asp, potassco
    from caspo import core, learn
    
    if args.threads:
        learn.register_mt(args.threads, args.conf)

    sif = component.getUtility(core.IFileReader)
    sif.read(args.pkn)
    graph = core.IGraph(sif)
    
    reader = component.getUtility(core.ICsvReader)
    reader.read(args.midas)
    dataset = core.IDataset(reader)
    
    learner = learn.learner(graph, dataset, args.time, args.length, potassco.IClingo, args.discretization, args.factor)
    networks = learner.learn(args.fit, args.size)
    
    writer = core.ICsvWriter(networks)
    writer.write('networks.csv', args.outdir)
    
    return 0
    
def design(args):
    from itertools import combinations
    from zope import component

    from pyzcasp import asp, potassco
    from caspo import core, design

    if args.threads:
        design.register_mt(args.threads, args.conf)
    
    reader = component.getUtility(core.ICsvReader)
    reader.read(args.networks)
    networks = core.IBooleLogicNetworkSet(reader)
        
    reader.read(args.midas)
    dataset = core.IDataset(reader)
    
    clist = None
    if args.list:
        reader.read(args.list)
        clist = core.IClampingList(reader)
    
    designer = design.designer(networks, dataset.setup, clist, potassco.IClingo)
    exps = designer.design(max_stimuli=args.stimuli, max_inhibitors=args.inhibitors, 
                           max_experiments=args.experiments, relax=int(args.relax))
    
    if exps:
        for i,exp in enumerate(exps):
            writer = component.getMultiAdapter((exp, dataset.setup), core.ICsvWriter)
            writer.write('opt-design-%s.csv' % i, args.outdir)

            diffs = []
            readouts = dataset.setup.readouts
            for clamping in exp.clampings:                
                d = dict.fromkeys(readouts, 0)
                d['pairs'] = 0
                for m1,m2 in combinations(networks, 2):
                    cd = False
                    for r in readouts:
                        if m1.prediction(r,clamping) != m2.prediction(r,clamping):
                            d[r] += 1
                            cd = True
                    if cd:
                        d['pairs'] += 1
                
                diffs.append(d)

            writer = component.getUtility(core.ICsvWriter)
            writer.load(diffs, readouts + ['pairs'])
            writer.write('opt-design-%s-diffs.csv' % i, args.outdir)
            
    else:        
        printer = component.getUtility(core.IPrinter)
        printer.pprint("There is no solutions matching your experimental design criteria.")
        
    return 0

def control(args):    
    from zope import component

    from pyzcasp import potassco, asp
    from caspo import core, control
    
    if args.threads:
        control.register_mt(args.threads, args.conf)

    reader = component.getUtility(core.ICsvReader)
    
    reader.read(args.networks)
    networks = core.ILogicalNetworkSet(reader)
    
    reader.read(args.scenarios)
    multiscenario = control.IMultiScenario(reader)
    multiscenario.allow_constraints = args.iconstraints
    multiscenario.allow_goals = args.igoals
    
    controller = control.controller(networks, multiscenario, potassco.IClingo)
    strategies = controller.control(args.size)
    
    writer = core.ICsvWriter(strategies)
    writer.write('strategies.csv', args.outdir)
        
    return 0

def analyze(args):    
    from zope import component
    from pyzcasp import asp, potassco
    from caspo import core, analyze, learn, control
    
    clingo = component.getUtility(potassco.IClingo)
    reader = component.getUtility(core.ICsvReader)

    lines = []
    if args.networks:
        reader.read(args.networks)
        networks = core.IBooleLogicNetworkSet(reader)
        
        if args.netstats:
            stats = analyze.IStats(networks)
            writer = core.ICsvWriter(stats)
            writer.write('networks-stats.csv', args.outdir)
            
        lines.append("Total Boolean logic networks: %s" % len(networks))
        
        if args.midas:
            reader.read(args.midas[0])
            dataset = core.IDataset(reader)
            point = core.TimePoint(int(args.midas[1]))
            
            if args.netstats:
                writer = component.getMultiAdapter((networks, dataset, point), core.ICsvWriter)
                writer.write('networks-mse-len.csv', args.outdir)
            
            behaviors =  component.getMultiAdapter((networks, dataset, clingo), analyze.IBooleLogicBehaviorSet)
            multiwriter = component.getMultiAdapter((behaviors, point), core.IMultiFileWriter)
            multiwriter.write(['behaviors.csv', 'behaviors-mse-len.csv', 'variances.csv', 'core.csv'], args.outdir)
            
            lines.append("Total I/O Boolean logic behaviors: %s" % len(behaviors))
            lines.append("Weighted MSE: %.4f" % behaviors.mse(dataset, point.time))
            lines.append("Core predictions: %.2f%%" % ((100. * len(behaviors.core())) / 2**(len(behaviors.active_cues))))
    
    if args.strategies:
        reader.read(args.strategies)
        strategies = control.IStrategySet(reader)
        stats = analyze.IStats(strategies)
        writer = core.ICsvWriter(stats)
        writer.write('strategies-stats.csv', args.outdir)
        
        lines.append("Total intervention strategies: %s" % len(strategies))

    writer = component.getUtility(core.IFileWriter)
    writer.load(lines, "caspo analytics summary")
    writer.write('summary.txt', args.outdir)
    
    printer = component.getUtility(core.IPrinter)
    printer.pprint("\ncaspo analytics summary")
    printer.pprint("=======================")
    for line in lines:
        printer.pprint(line)
        
    return 0
    
def visualize(args):
    import os
    from zope import component
    from caspo import core, visualize, control, learn
    import random

    reader = component.getUtility(core.ICsvReader)
    printer = component.getUtility(core.IPrinter)
    if args.midas:
        reader.read(args.midas)
        dataset = core.IDataset(reader)
        
        if args.pkn:
            sif = component.getUtility(core.IFileReader)
            sif.read(args.pkn)
            graph = core.IGraph(sif)
            
            zipgraph = component.getMultiAdapter((graph, dataset.setup), core.IGraph)
        
            if zipgraph.nodes != graph.nodes:
                writer = component.getMultiAdapter((visualize.IMultiDiGraph(graph), dataset.setup), visualize.IDotWriter)
                writer.write('pkn-orig.dot', args.outdir)
            
                writer = component.getMultiAdapter((visualize.IMultiDiGraph(zipgraph), dataset.setup), visualize.IDotWriter)
                writer.write('pkn-zip.dot', args.outdir)
            else:
                writer = component.getMultiAdapter((visualize.IMultiDiGraph(graph), dataset.setup), visualize.IDotWriter)
                writer.write('pkn.dot', args.outdir)
    
        if args.networks:
            reader.read(args.networks)
            networks = core.IBooleLogicNetworkSet(reader)
            if args.sample:
                try:
                    sample = random.sample(networks, args.sample)
                except ValueError as e:
                    printer.pprint("Warning: %s, there are only %s logical networks." % (str(e), len(networks)))
                    sample = networks
            else:
                sample = networks
            
            printer = component.getUtility(core.IPrinter)
            for i, network in enumerate(sample):
                writer = component.getMultiAdapter((visualize.IMultiDiGraph(network), dataset.setup), visualize.IDotWriter)
                printer.quiet = True
                writer.write('network-%s.dot' % (i+1), args.outdir)
                printer.quiet = False
                printer.iprint("Wrote %s to %s" % (os.path.join(args.outdir, 'network-1.dot'), os.path.join(args.outdir, 'network-%s.dot' % (i+1))))
            
            printer.pprint("")                
            if args.union:
                writer = component.getMultiAdapter((visualize.IMultiDiGraph(networks), dataset.setup), visualize.IDotWriter)
                writer.write('networks-union.dot', args.outdir)
                    
    if args.strategies:
        reader.read(args.strategies)
        strategies = control.IStrategySet(reader)
        writer = visualize.IDotWriter(visualize.IDiGraph(strategies))
        writer.write('strategies.dot', args.outdir)
        
    return 0
