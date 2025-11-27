# HexMap4Gimp

This is a GIMP plugin for the creation of traditional RPG hexagonal maps. It was
derived from the code of the scrift-fu plugin from
[HexGimp](https://sites.google.com/view/ddhorizons/cartography/hexgimp).
HexMap4Gimp is a reimplementation of the former written is Python, specifacally
for GIMP 3.0. I have no idea if it works on older versions of GIMP. The rewrite
was started because the original script-fu plugin was not working for me in GIMP
3.0, and because I also wanted to include some additional features using python
was more convenient for me, as I know it better than scheme.

The plugin is under GPLv3 license.

## Features

In its current state the plugin can be used to:
- Create a multilayer image configured to draw an hexmap

- You can use the pencil tool with hex brushes to pait hexes on the *Terrain*
layer.

- Gimp's grid is configured for selected brush set, making it easy to correctly
  paint your hexes by selecting snap to grid.

- The *Terrain* layer is prefiled with blank hexes (1 pixel srinked version of
the regular hexes), showing you were to paint hexes. Regular hexex overlap one
pixel on the hex boundaries which are darkened by the hex grid drawn on the Grid
Layer.

- The user can optionally select number labels for the hexes, which are in the
format CCRR (column with two digits, row with two digits).

- The user can alos optionally select a second grid layer, called LargeGrid, on
which a second grid is drawn in which each grid covers a number of regular
hexes. This allows you to have atlas grid over your regional map or regional
grid over your county map, and so forth.

- The user has to select the blank hex brush to use, more on this bellow.

For the moment only flat top hex layout is supported.

## Brushes

The plugin is not linked to any set of hex brushes. The user must choose the
blank hex brush to use to create the map. This opens the posibility to
use any brush set you have or you may desing new brushes to use with this
plugin. 

At the moment the code has been tested with brushes available from:

1. [HexGimp brush sets](https://sites.google.com/view/ddhorizons/cartography/hexgimp)
2. [Hex brushes derived from Inkwellideas icons](https://www.enworld.org/threads/making-hex-maps-with-the-gimp.238000/)

You must install any of these brush sets, or other brushes you may design or
find on the internet. The user selects the blank hex brush to use in the input
dialog of the plugin.

The brushes from [HexGimp
(1)](https://sites.google.com/view/ddhorizons/cartography/hexgimp) are well
tested and supported, as they come from the reference script-fu implementation. 

The brushes [derived from Inkwellideas icons
(2)](https://www.enworld.org/threads/making-hex-maps-with-the-gimp.238000/)] are
less tested, but the code seems to work well with them. Howeve, to use them you
have to make a proper blank hex brush. The *Hex Blank* brush provided in this
set does not have the properties expected by this plugin. To make the brush just
open the "Hex Blank" brush in GIMP as an image. Select the interior of the hex
with the fuzzy select tool and fill it with white. Then invert selection, erase
what is selected and crop the image to content. Export the transformed image as
a gimp brush. Select a name for the brush, which you would write on the "Blank
Hex Brush" selector when you start the plugin.

## How it works

An image is created with the following layers:

- *Numbers*
- *Borders*
- *LargeGrid*
- *Grid*
- *Cities*
- *Roads*
- *Rivers*
- *Terrain*

The hex grid is drawn using a blank hex brush, which must be a 1-pixel-srinked
version of the hex brushes you plan to use. This brush is used to paint white
hexagons on the *Terrain* layer, puting the centers of the hexes so that normal
hexes drawn on top of these blank hexes would overlap one pixel on their
sides. This means that when the blank hexes are painted a 1 pixel empty space is
left between the hexes. That empty space is then selected and filled with a
grey color on the grid layer, which is set to multiply mode to darken the
overlaping pixels between adjacent hexes, which is seen as a hex grid. 

Numer labels and Large Grid are optional features. When not selected in the
input dialog the correspondig layer is removed.

The plugin draws the Number labels as text layers on top ot the *Numbers* layer,
and then it merges them down.

The large grid layer is drawn using the mathematical expresions for a scaled up
hex, whose dimensions are computed from the blank hex selected by the user; who
can also select the column and row of the hex on which the large hex will be
centered as well as the scale (the number of normal hexes covered by each large
hex).

## Work for the future

- Test more hex brush sets if I can find more.
- Improve the number labeling, both in speed (if possible at all) and in
resolution.
- Add options to add labels and large grid on an already created image.
- Adding labels on the large hexes?


