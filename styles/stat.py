from ..styler import new_style
dark_gray = ".15"
light_gray = ".8"


#
# rcparams axes.edgecolor -> spine.edgecolor
#  axes.facecolor -> axes.axi_bgcolor

new_style("stat",

    figure = dict( facecolor="white"),
    text = dict( color = dark_gray),
    ticks = dict( labelcolor = dark_gray, direction="out", color=dark_gray),
    legend = dict( frameon=False, numpoints=1, scatterpoints=1),
    axes = dict( axisbelow=True),
    grids = dict( linestyle="-", state=True),
    lines = dict( solid_capstyle="round")
    )

new_style("dark", 
          {
            "axes|axis_bgcolor": "#EAEAF2",
            "spines|color": "white",
            "spines|linewidth": 0,
            "grids|color": "white"}
          )
new_style("black", 
          {
            "axes|axis_bgcolor": "k",
            "spines|color": "white",
            "spines|linewidth": 1,
            "grids|color": "white"}
          )

new_style("white", 
          {          
            "axes|bgcolor": "white",
            "spines|color": dark_gray,
            "spines|linewidth": 1.25,
            "grids|color": light_gray
          }
          )

new_style("tick", 
          {
           "ticks.major|size": 6,           
           "ticks.minor|size": 3
          }
          )

new_style("notick", 
          {
           "ticks.major|size": 0,           
           "ticks.minor|size": 0
          }
          )
new_style("poster", {
          "axes.ticks":{"width":1.6, "length":8},
          "axes.ticks.labels":{"fontsize":14}, 
          "spines|linewidth":2, 
          "axes.labels|fontsize":18,
          "plot|markersize":12
          }
          )


