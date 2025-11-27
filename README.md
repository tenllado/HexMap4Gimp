# HexMap4Gimp

This is a GIMP plugin for the creation of traditional RPG hexagonal maps. It was
derived from the code of the scrift-fu plugin from
[HexGimp](https://sites.google.com/view/ddhorizons/cartography/hexgimp).
HexMap4Gimp is a reimplementation of the former written is Python, specifically
for GIMP 3.0. I have no idea if it works on older versions of GIMP. The rewrite
was started because the original script-fu plugin was not working for me in GIMP
3.0, and because I also wanted to include some additional features using python
was more convenient for me, as I know it better than scheme.

The plugin is under GPLv3 license.

## Features

In its current state the plugin:
- Creates a multilayer image configured to draw a hexmap

- The user should use the pencil tool with some hex brushes to pait hexes on the
*Terrain* layer.

- Gimp's grid is configured for selected brush set, making it easy to correctly
  place your hexes by selecting the snap to grid option in the gimp's view menu.

- The *Terrain* layer is prefiled with blank hexes (1 pixel srinked version of
the regular hexes), showing you were to paint hexes. The hexes painted with the
hex brushes will overlap one pixel on the hex boundaries. These hex boundaries
are darkened by the hex grid drawn on the *Grid* layer.

- The user can optionally select number labels for the hexes, which are in the
format CCRR (column with two digits, row with two digits).

- The user can also optionally select a second larger grid, which will be
painted on the *LargeGrid* layer. Each of these large hexes will cover a number
of the regular hexes specified in the input dialog of the plugin. This allows
you to have atlas hexes over your regional hex map, regional hexes over your
county map, and so forth.

For the moment only flat top hex layout is supported.

## Install

To install the plugin you should:
1. Create a new directory named **hexmap4gimp** in the plugi-ins folder inside
   the gimp config directory. On Linux or other unix type system this is
generally ~/.config/GIMP/3.0/plug-ins/hexgimp. On windows this should be on the
%APPDATA% directory, namely *C:\Users\<YourUserName>\AppData\Roaming*.

2. Copy the hexmap4gimp.py file to the directory you just created.

You must also download at least one set of hex brushes, as explained in the next
section.

## Brushes

The HexMap4Gimp plugin is not linked to any set of hex brushes. The user must
choose in the input dialog window the blank hex brush to use to create the map.
This opens the posibility to use any brush set you have, or you may desing new
brushes to use with this plugin. 

The code has been tested with brushes available from the following links:

1. [HexGimp brush sets](https://sites.google.com/view/ddhorizons/cartography/hexgimp)
2. [Hex brushes derived from Inkwellideas icons](https://www.enworld.org/threads/making-hex-maps-with-the-gimp.238000/)

You must install any of these brush sets, or other brushes you may design or
find on the internet. Just create a subdirectory in the brushes folder inside
GIMP's configuration directory.

### Hexgimp brushes

The brushes from [HexGimp
(1)](https://sites.google.com/view/ddhorizons/cartography/hexgimp) are well
tested and supported, as they come from the reference script-fu implementation. 

### Hex brushes derived from Inkwellideas icons

The brushes [derived from Inkwellideas icons
(2)](https://www.enworld.org/threads/making-hex-maps-with-the-gimp.238000/)] are
less tested, but the code seems to work well with them. 

Apart from installing the brushes you have to make a proper blank hex brush for
HexMap4Gimp. The *Hex Blank* brush provided with this set does not have the
properties expected by the plugin. To make the brush:
1. Open the "Hex Blank" brush in GIMP as an image
2. Select the interior of the hex with the fuzzy select tool and fill it with
   white using the bucket fill tool.
3. Invert selection and erase what is selected
4. Crop the image to content.
5. Export the transformed image as a gimp brush, and don't forget to select a
   name for the brush.

You can use the brush with the plugin by writing its name in the *Blank Hex
Brush* selector from the input dialog, that opens when you start the plugin.

## Usage

Once installed, the File menu in Gimp will show a new HexMap4Gimp entry, that
offers you the option to create a *New Hex Map*. Click that option and a dialog
window will open where you can select the options for the map, namely:
- The blank hex brush to be used.
- The number of rows and columns you want on the map
- Labeling options, that is, whether you want to generate the labels, the column
  and row where numbering should start and end, and the number to assign to the
  first labeled row and column.
- Large grid options, allows you to activate the large grid option, the number of
  hexes that each large hex should cover (scale), and the row and column of the
  hex on which you want to center the map.

Press the *OK* button and the map will be created.

Once created, select snap on grid from the view menu. You can then use the
pencil tool with the hex brushes to draw hexes on the *Terrain* layer (you will
be covering the white hexes that help you center your colored hexes). You should
place the cities, towers or town icons on the *Cities* layer and use the
*Rivers* and *Roads* layers to draw this kind of elements using regular gimp
drawing tools. And that is it, you can use any gimp technique you know to
improve your hex map.

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
version of the hex brushes you plan to use, all in white. This brush is used to
paint white hexagons on the *Terrain* layer, putting the centers of the hexes so
that normal hexes drawn on top of these blank hexes would overlap one pixel on
their sides. This means that when the blank hexes are painted a 1 pixel empty
space is left between the hexes. That empty space is then selected and filled
with a grey color on the *Grid* layer, which is set to multiply mode to darken the
overlapping pixels between adjacent hexes, which is seen as a hex grid. 

Number labels and Large Hex Grid are optional features. When not selected in the
input dialog the corresponding layer is removed.

The plugin draws the Number labels as text layers on top of the *Numbers* layer,
and then it merges them down.

The large grid layer is drawn using the mathematical expressions for a hexagonal
grid, for a scaled up hex whose dimensions are computed from the blank hex
selected by the user. The dialog allows also to choose the column and row of the
small hex on which the large hex will be centered, as well as the scale (the
number of normal hexes covered by each large hex).

## Work for the future

- Test more hex brush sets if I can find more.
- Improve the number labeling, both in speed (if possible at all) and in
resolution.
- Add options to add labels and large grid on an already created image.
- Adding labels on the large hexes?

