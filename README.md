### Reasoning on the response of logical signaling networks

The manual identification of logic rules underlying a biological system is
often hard, error-prone and time consuming. 
Further, it has been shown that, if the inherent experimental noise is considered, many different logical networks
can be compatible with a set of experimental observations. 
Thus, automated **inference of logical networks from experimental data** would allow for
identifying admissible large-scale logic models saving a lot of efforts and without any a priori bias. 
Next, once a family a logical networks has been identified, one can suggest or **design new experiments** in order to reduce the uncertainty provided by this family.
Finally, one can **look for intervention strategies** (i.e. inclusion minimal sets of knock-ins and knock-outs) that force
a set of target species or compounds into a desired steady state. 
Altogether, this constitutes a pipeline for automated reasoning on logical signaling networks. 
Hence, the aim of **caspo** is to implement such a pipeline providing a powerful and easy-to-use software tool for systems biologists.

### Installation

If you are already using [Python](https://www.python.org/download/releases/2.7.6) with [NumPy](http://www.numpy.org/), you should be able to install **caspo** from [pypi](https://pypi.python.org/pypi/caspo) simply by running:
```
$ pip install caspo
```
If you are not using Python and/or NumPy, please visit the [WIKI](https://github.com/bioasp/caspo/wiki) for detailed instructions.

### Usage
Ask for help by running:

```
$ caspo --help
usage: caspo [-h] [--quiet] [--out O] [--version]
             {control,visualize,design,learn,test,analyze} ...

Reasoning on the response of logical signaling networks with Answer Set Programming

optional arguments:
  -h, --help            show this help message and exit
  --quiet               do not print anything to standard output
  --out O               output directory path (Default to './out')
  --version             show program's version number and exit

caspo subcommands:
  for specific help on each subcommand use: caspo {cmd} --help

  {control,visualize,design,learn,test,analyze}```
```

### Samples

Sample files are included and available for [download](https://github.com/bioasp/caspo/tree/master/caspo/data)

### Related publications

* Minimal intervention strategies in logical signaling networks with ASP. (2013). Theory and Practice of Logic Programming. [DOI](http://dx.doi.org/10.1017/S1471068413000422)

* Exhaustively characterizing feasible logic models of a signaling network using Answer Set Programming. (2013). Bioinformatics. [DOI](http://dx.doi.org/10.1093/bioinformatics/btt393)

* Revisiting the Training of Logic Models of Protein Signaling Networks with a Formal Approach based on Answer Set Programming. (2012) The 10th Conference on Computational Methods in Systems Biology. [DOI](http://dx.doi.org/10.1007/978-3-642-33636-2_20)
