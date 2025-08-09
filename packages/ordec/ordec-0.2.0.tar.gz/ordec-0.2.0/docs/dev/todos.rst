Todos
=====

ORDB
----

- Add tree() method to Cursor that descends using NPath
- Implement subgraph directory index + Cursor.iterdir()
- External references:

  - add some kind of index to detect DanglingExternalRefs either on adding the ExternalRef or when updating the subgraph reference Attr.
  - do we need any other indices for external references?

- Cursor deletion:
  
  - delete path + node + "dependent" nodes?
  - Stuff that gets added together (MultiInserter) should also be deleted together?
  - complex example: PolyVec2R

- Test indices
  
  - in some limited testcases with updates and removals that affect indices
  - flag in SubgraphUpdater to track index changes (?)
  - check whether rebuilding subgraph from node list leds to identical index

- Branching and merging of Subgraphs
- SimHierarchy: do not duplicates the nets of Schematics and Symbols
- Profiling

SVG Renderer
------------

- understand how to properly compute the scaling factor for text instead of just guessing a value (0.045).
- in the medium term, make the symbols more compact overall and put params outside symbol. then, we can also drop the condensed font hack.
- can we deliver the font to the browser so that the user does not need to have inconsolate installed and the svg does not need to embed the font (some sort of browser font inheritance from the html page to the svg context)?
- firefox and cairosvg render fonts slightly differently (baseline). figure out whether an alternative dominant-baseline setting could fix this.

base.Dockerfile
---------------

Big dependencies (look into these to shrink base image further):

- scipy
- numpy
- ace-builds
