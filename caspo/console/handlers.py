def learn(args):        
    from zope import component

    from pyzcasp import asp, potassco
    from caspo import core, learn

    clingo = potassco.Clingo(args.clingo)

    sif = component.getUtility(core.IFileReader)
    sif.read(args.pkn)
    graph = core.IGraph(sif)
    
    reader = component.getUtility(core.ICsvReader)
    reader.read(args.midas)
    dataset = core.IDataset(reader)
    
    point = core.TimePoint(args.time)
    
    discretize = component.createObject(args.discretization, args.factor)
    discreteDS = component.getMultiAdapter((dataset, discretize), learn.IDiscreteDataset)
    
    zipgraph = component.getMultiAdapter((graph, dataset.setup), core.IGraph)

    instance = component.getMultiAdapter((zipgraph, point, discreteDS), asp.ITermSet)

    learner = component.getMultiAdapter((instance, clingo), learn.ILearner)
    networks = learner.learn(args.fit, args.size)
    
    writer = core.ICsvWriter(networks)
    writer.write('networks.csv', args.outdir)
    
    return 0
    
def design(args):
    from zope import component

    from pyzcasp import asp, potassco
    from caspo import core, design
    
    clingo = potassco.Clingo(args.clingo)
    
    reader = component.getUtility(core.ICsvReader)
    reader.read(args.networks)
    networks = core.IBooleLogicNetworkSet(reader)
        
    reader.read(args.midas)
    dataset = core.IDataset(reader)
    
    instance = component.getMultiAdapter((networks, dataset.setup), asp.ITermSet)

    designer = component.getMultiAdapter((instance, clingo), design.IDesigner)
    exp = designer.design(max_stimuli=args.stimuli, max_inhibitors=args.inhibitors, max_experiments=args.experiments)
    
    if exp:
        writer = component.getMultiAdapter((exp, dataset.setup), core.ICsvWriter)
        writer.write('opt-design.csv', args.outdir)
    else:
        printer = component.getUtility(core.IPrinter)
        printer.pprint("There is no solutions matching your experimental design criteria.")
        
    return 0

def control(args):    
    from zope import component

    from pyzcasp import potassco, asp
    from caspo import core, control

    if args.gringo_series == 3:
        gringo = potassco.Gringo3(args.gringo)
    else:
        gringo = potassco.Gringo4(args.gringo)
    
    if args.solver == 'hclasp':
        clasp = potassco.ClaspHSolver(args.hclasp)
    else:
        clasp = potassco.ClaspDSolver(args.claspD)
    
    reader = component.getUtility(core.ICsvReader)
    
    reader.read(args.networks)
    networks = core.ILogicalNetworkSet(reader)
    
    reader.read(args.scenarios)
    multiscenario = control.IMultiScenario(reader)
    multiscenario.allow_constraints = args.iconstraints
    multiscenario.allow_goals = args.igoals
    
    instance = component.getMultiAdapter((networks, multiscenario), asp.ITermSet)

    controller = component.getMultiAdapter((instance, gringo, clasp), control.IController)
    strategies = controller.control(args.size)
    
    writer = core.ICsvWriter(strategies)
    writer.write('strategies.csv', args.outdir)
        
    return 0

def analyze(args):    
    from zope import component
    from pyzcasp import asp, potassco
    from caspo import core, analyze, learn, control
    
    clingo = potassco.Clingo(args.clingo)    
    reader = component.getUtility(core.ICsvReader)

    lines = []
    if args.networks:
        reader.read(args.networks)
        networks = core.IBooleLogicNetworkSet(reader)
        
        stats = analyze.IStats(networks)
        writer = core.ICsvWriter(stats)
        writer.write('networks-stats.csv', args.outdir)
        lines.append("Total Boolean logic networks: %s" % len(networks))
        
        if args.midas:
            reader.read(args.midas[0])
            dataset = core.IDataset(reader)
            point = core.TimePoint(int(args.midas[1]))
    
            writer = component.getMultiAdapter((networks, dataset, point), core.ICsvWriter)
            writer.write('networks-mse.csv', args.outdir)
    
            behaviors =  component.getMultiAdapter((networks, dataset, clingo), analyze.IBooleLogicBehaviorSet)
            multiwriter = component.getMultiAdapter((behaviors, point), core.IMultiFileWriter)
            multiwriter.write(['behaviors.csv', 'behaviors-mse-len.csv', 'variances.csv', 'core.csv'], args.outdir)
            
            lines.append("Total I/O Boolean logic behaviors: %s" % len(behaviors))
            lines.append("Weighted MSE: %.4f" % behaviors.mse(point.time))
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
