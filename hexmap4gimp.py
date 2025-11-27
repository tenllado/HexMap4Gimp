#!/usr/bin/env python3

# NAME 
#       HexMap4Gimp, Christian Tenllado
#
# VERSION 
#       0.0.1   2025/11/27
#
# DESCRIPTION
#
#       GIMP plugin for the creation of traditional RPG hexagonal maps. Based on
#       the code of the original scrift-fu plugin HexGimp, from isomage
#       DJMythal, that can be found in:
#          https://sites.google.com/view/ddhorizons/cartography/hexgimp
#
#       This plugin is a reimplementation in Python for GIMP 3.0, with some
#       additional modifications:
#       - user can choose the blank hex brush to use, opening the posibility to
#       use other brush sets. The plugin is not linked to a specific set of
#       brushses.
#       - an option is provided to draw an extra large grid layer, choosing the
#       center hex for that grid (atlas over region or region over county, and
#       so on).
#
# AUTHOR
#       - Referenced HexGimp script-fu plugin : isoimage/DJMythal
#       - Python rewrite: Christian Tenllado, ctenllado@gmail.com
#
# LICENSE: GPLv3
#
#       This program is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY, without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#       GNU General Public License for more details.
#
#       To view a copy of the GNU General Public License
#       visit: http://www.gnu.org/licenses/gpl.html
#
# DOCUMENTATION
#
#       orig    s          w = 2*s
#         ·  _______       h = sqrt(3) * s
#         | /      |\      distance origin - center = (w/2, h/2)
#         |/    .  | \_______
#         |\ center| /       \
#         | \______|/    .    \
#                   \         /
#                    \_______/
#
#       The hex grid is drawn using a blank hex that is a 1 pixel srinked
#       version of the rest of the hex brushes. The grid is formed puting the
#       centers of the hexes so that the normal hexes overlap one pixel on their
#       sides. The Terrain layer is drawn using the blank hex on those centers,
#       leaving a one pixel-wide epmty space on the layer between hexes. That
#       empty space is then selected and filled with a grey color on the grid
#       layer, which is set to multiply mode to darken the overlaping pixels
#       between adjacent hexes, which is seen as an hex grid. 
#
#       At the moment the code has been tested with brushes available from:
#       1. https://sites.google.com/view/ddhorizons/cartography/hexgimp
#       2. https://www.enworld.org/threads/making-hex-maps-with-the-gimp.238000/
#
#       You must install any of these brushes, or other brushes you may design. 
#       The user selects the blank hex brush to use in the input dialog.
#
#       The brushes from (1) are the brushes provided with the original HexGimp
#       script-fu plugin. These are the best supported. 
#
#       The brushes from (2) seem to be generated from the icons offered by
#       inkwellideas, who develop hexographer/worldographer. I tested them and
#       the code seems to work nicely with them, but you but you have to make a 
#       proper blank hex brush for this plugin (the Hex Blank brush provided in
#       this set does not have the properties expected by this plugin). To make
#       the brush just open the "Hex Blank" brush, included in the set, as an
#       image with gimp. Select the interior of the hex with the fuzzy select
#       tool and fill it with white. Then invert selection, erase what is
#       selected and crop the image to content. Export the transformed image as
#       a gimp brush. Select a name for the brush, which you would write on the
#       "Blank Hex Brush" selector when you start the plugin.

import gi, math
gi.require_version("Gimp", "3.0")
gi.require_version("GimpUi", "3.0")
from gi.repository import Gimp, Gegl, GimpUi, Gtk, Gdk, GLib, Babl, GObject
import sys

new_hexmap = "plug-in-hexgimp"

class HexGrid:
    def __init__(self, blank_hex_brush):
        # These expressions where derived from the original hexgimp scheme code
        # and work fine for hexgimp's brushes, where:
        #
        # hex_w = 36 -- width of the blank hex       --> even and multiple of 4
        # hex_h = 31 -- height of the blank hex      --> odd
        # dx    = 28 -- distance between hex columns
        # dy    = 15 -- distance between hex rows
        #
        # The code might need to be addapted to work with other brushes,
        # probably making adjustments in cases where hex_w is odd and/or hex_h
        # even.
        self.blank_hex_brush = blank_hex_brush
        ok, hex_w, hex_h, mask_bpp, color_bpp = blank_hex_brush.get_info()
        self.hex_w = hex_w
        self.hex_h = hex_h
        self.dx = (hex_w + 2) * 3 // 4 + 1
        self.dy = hex_h + 1
        self.odd_col_offset = hex_h // 2 + 1
        self.origin_center_dx = 1 + hex_w // 2
        self.origin_center_dy = 1 + hex_h // 2
        self.gimp_grid_x = self.dx
        self.gimp_grid_y = self.odd_col_offset

    def hex_center(self, c, r):
        x0 = c * self.dx
        y0 = r * self.dy
        if c % 2 != 0:
            y0 += self.odd_col_offset 
        return x0 + self.origin_center_dx, y0 + self.origin_center_dy

    def set_dims(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.img_w = self.dx * cols + (self.hex_w + 2) // 4
        self.img_h = self.dy * rows + 1 + self.odd_col_offset
        return self.img_w, self.img_h 

    def draw(self, img):
        prev_brush = Gimp.context_get_brush()
        Gimp.context_set_brush(self.blank_hex_brush)
        terrain_layer = img.get_layer_by_name("Terrain")
        for r in range(self.rows):
            for c in range(self.cols):
                x, y = self.hex_center(c, r)
                Gimp.pencil(terrain_layer, [x, y])

        prev_fcolor = Gimp.context_get_foreground()
        grid_color = Gegl.Color.new("#969696")
        Gimp.context_set_foreground(grid_color)
        terrain_blank_color = Gegl.Color.new("#ffffff")
        img.select_color(Gimp.ChannelOps.REPLACE,
                         terrain_layer,
                         terrain_blank_color)
        Gimp.Selection.invert(img)
        grid_layer = img.get_layer_by_name("Grid")
        grid_layer.set_mode(Gimp.LayerMode.MULTIPLY)
        grid_layer.set_opacity(75)
        grid_layer.edit_fill(Gimp.FillType.FOREGROUND)
        Gimp.context_set_foreground(prev_fcolor)
        Gimp.Selection.none(img)
        if (prev_brush != None):
            Gimp.context_set_brush(prev_brush)

    def draw_labels(self, img, x0, y0, x1, y1, ix, iy, separator):
        def make_label(coord_separator, x, y):
            return f"{x:02d}{coord_separator}{y:02d}"

        font = Gimp.Font.get_by_name("Sans-serif")
        font_size = 7
        foreground_color = Gimp.context_get_foreground()
        labels_color = Gegl.Color.new("#646464")
        Gimp.context_set_foreground(labels_color) # for 100, 100, 100
        for r in range(y0, y1 + 1):
            for c in range(x0, x1 + 1):
                cx, cy = self.hex_center(c, r)
                label = make_label(separator, ix + (c - x0), iy + (r - y0))
                text_layer = Gimp.TextLayer.new(img,
                                                label,
                                                font,
                                                font_size,
                                                Gimp.Unit.pixel())
                img.insert_layer(text_layer, None, 0)
                ycoord = cy - self.hex_h // 2 - 1
                text_layer.set_offsets(cx - text_layer.get_width() // 2, ycoord)
                img.merge_down(text_layer, Gimp.MergeType.EXPAND_AS_NECESSARY)
        Gimp.context_set_foreground(foreground_color)

    def set_gimp_grid(self, img):
        img.grid_set_spacing(self.dx, self.dy)
        img.grid_set_offset(self.origin_center_dx, 0)
        img.grid_set_style(Gimp.GridStyle.DOTS)

    def draw_large_grid(self, img, scale, ccol, crow):
        hex_h = (self.hex_h + 1) * scale
        hex_w = (self.hex_w + 2) * scale + scale / 2
        hex_s = hex_w / 2

        def draw_hex(layer, cx, cy):
            # hex vertices, anti clock wise, from bottom left
            verts = [
                (cx - hex_s/2, cy - hex_h/2),
                (cx + hex_s/2, cy - hex_h/2),
                (cx + hex_s  , cy            ),
                (cx + hex_s/2, cy + hex_h/2),
                (cx - hex_s/2, cy + hex_h/2),
                (cx - hex_s  , cy            ),
            ]

            # Draw sides
            for i in range(6):
                v1 = verts[i]
                v2 = verts[(i + 1) % 6]
                side = [v1[0], v1[1], v2[0], v2[1]]
                Gimp.pencil(layer, side)

        def hex_center(c, r):
            hex_c = ccol +  c*scale
            hex_r = crow + r*scale
            if c % 2 != 0:
                hex_r = hex_r + scale // 2
            return self.hex_center(hex_c, hex_r)

        prev_brush = Gimp.context_get_brush()
        prev_brush_size = Gimp.context_get_brush_size()

        pixel_brush = Gimp.Brush.get_by_name("1. Pixel")
        Gimp.context_set_brush(pixel_brush)
        Gimp.context_set_brush_size(1)
        prev_fcolor = Gimp.context_get_foreground()
        grid_color = Gegl.Color.new("#969696")
        Gimp.context_set_foreground(grid_color)
        layer = img.get_layer_by_name("LargeGrid")
        layer.set_mode(Gimp.LayerMode.MULTIPLY)
        layer.set_opacity(75)

        # Draw the grid, centered on column ccol and row crow
        rows = 2 + max(crow // scale , (self.rows - crow) // scale)
        cols = 2 + max(ccol // scale , (self.cols - ccol) // scale)
        for r in range(-rows, rows):
            for c in range(-cols, cols):
                cx, cy = hex_center(c, r)
                draw_hex(layer, cx, cy)
        Gimp.context_set_brush_size(prev_brush_size)
        Gimp.context_set_foreground(prev_fcolor)
        if (prev_brush != None):
            Gimp.context_set_brush(prev_brush)

class HexMapDialog(Gtk.Window):
    def __init__(self, title):
        super().__init__(title=title)

        self.response = Gtk.ResponseType.CANCEL
        self.set_modal(True)
        self.set_default_size(300, 300)
        self.set_resizable(False)
        self.get_style_context().add_class("gimp-dialog")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.set_margin_top(6)
        vbox.set_margin_bottom(6)
        vbox.set_margin_start(6)
        vbox.set_margin_end(6)
        self.add(vbox)

        # Grid for widgets
        self.grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        vbox.pack_start(self.grid, True, True, 0)
        self.widget_row = 0

        # Button box (OK / Cancel)
        action_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
            halign=Gtk.Align.END
        )

        cancel_btn = Gtk.Button.new_from_icon_name("gtk-cancel", Gtk.IconSize.BUTTON)
        ok_btn     = Gtk.Button.new_from_icon_name("gtk-ok", Gtk.IconSize.BUTTON)
        ok_btn.set_sensitive(True)
        self.ok_button = ok_btn

        cancel_btn.set_label("Cancel")
        ok_btn.set_label("OK")

        cancel_btn.connect("clicked", self.on_cancel)
        ok_btn.connect("clicked", self.on_ok)

        action_box.pack_start(cancel_btn, False, False, 0)
        action_box.pack_start(ok_btn, False, False, 0)

        vbox.pack_end(action_box, False, False, 0)

        # Build the widget UI
        self.add_widgets()

    def run_dialog(self):
        self.show_all()
        Gtk.main()           # block until OK/Cancel
        return self.response

    def on_ok(self, widget):
        self.response = Gtk.ResponseType.OK
        self.close()
        Gtk.main_quit()

    def on_cancel(self, widget):
        self.response = Gtk.ResponseType.CANCEL
        self.close()
        Gtk.main_quit()

    # -------------------------------------------------------
    # Widget helper methods
    # -------------------------------------------------------
    def push_widget_unlabeled(self, widget):
        self.grid.attach(widget, 0, self.widget_row, 2, 1)
        self.widget_row += 1

    def push_widget_labeled(self, label, widget):
        self.grid.attach(label,  0, self.widget_row, 1, 1)
        self.grid.attach(widget, 1, self.widget_row, 1, 1)
        self.widget_row += 1

    def add_spin(self, label, name, value, lower, upper, step_inc, page_inc):
        gtklabel = Gtk.Label(label=label)
        gtklabel.set_halign(Gtk.Align.START)
        adjustment = Gtk.Adjustment(
            value=value,
            lower=lower,
            upper=upper,
            step_increment=step_inc,
            page_increment=page_inc
        )
        spin_button = Gtk.SpinButton(adjustment=adjustment)
        self.push_widget_labeled(gtklabel, spin_button)
        setattr(self, name, spin_button)

    def add_spin_rows(self):
        self.add_spin("Rows:", "spin_rows", 16, 1, 1000, 1, 10)

    def add_spin_cols(self):
        self.add_spin("Columns:", "spin_cols", 16, 1, 1000, 1, 10)

    def add_numbering(self):
        self.numbering = Gtk.CheckButton(label="Hex numbering (CCRR)")
        self.push_widget_unlabeled(self.numbering)

    def add_spin_x0(self):
        self.add_spin("starting column:", "spin_x0", 0, 0, 15, 1, 5)

    def add_spin_y0(self):
        self.add_spin("starting row:", "spin_y0", 0, 0, 15, 1, 5)

    def add_spin_x1(self):
        self.add_spin("ending column:", "spin_x1", 15, 0, 15, 1, 5)

    def add_spin_y1(self):
        self.add_spin("ending row:", "spin_y1", 15, 0, 15, 1, 5)

    def add_spin_ix(self):
        self.add_spin("start column label:", "spin_ix", 0, 0, 99, 1, 10)

    def add_spin_iy(self):
        self.add_spin("start row label:", "spin_iy", 0, 0, 99, 1, 10)

    def add_coord_separator(self):
        label = Gtk.Label(label="Coordinate separator")
        label.set_halign(Gtk.Align.START)
        self.coord_separator = Gtk.Entry()
        self.coord_separator.set_text("")
        self.coord_separator.set_hexpand(True)
        self.push_widget_labeled(label, self.coord_separator)

    def add_large_grid(self):
        self.large_grid = Gtk.CheckButton(label="Additional large grid")
        self.push_widget_unlabeled(self.large_grid)

    def add_spin_scale(self):
        self.add_spin("Large Grid Scale:", "spin_scale", 4, 2, 10, 1, 2)

    def add_spin_lgrid_ccol(self):
        self.add_spin("Center column:", "spin_lgrid_ccol", 8, 0, 1000, 1, 10)

    def add_spin_lgrid_crow(self):
        self.add_spin("Center row:", "spin_lgrid_crow", 8, 0, 1000, 1, 10)

    # def add_brush_picker(self):
    #     # This brush picker is not working, at least with wayland on linux, the
    #     # code crashes when the button is pushed. I leave the code here for
    #     # future review
    #     label = Gtk.Label(label="Blank hex brush:")
    #     label.set_halign(Gtk.Align.START)
    #
    #     # Get the default brush (fallback if not found)
    #     default_brush = Gimp.Brush.get_by_name("hex blank")
    #     if default_brush is None:
    #         all_brushes = Gimp.brushes_get_list("")
    #         default_brush = all_brushes[0] if all_brushes else None
    #
    #     self.brush_picker = GimpUi.BrushChooser.new(
    #         None,                      # parent window, None is fine
    #         "Choose brush",            # dialog title if it opens a popup
    #         default_brush              # initial brush
    #     )
    #
    #     self.brush_picker.set_hexpand(True)
    #
    #     def get_active_text():
    #         brush = self.brush_picker.get_brush()
    #         return brush.get_name() if brush else None
    #
    #     self.brush_picker.get_active_text = get_active_text
    #     self.push_widget_labeled(label, self.brush_picker)

    def add_brush_entry(self):
        label = Gtk.Label(label="Blank hex brush:")
        label.set_halign(Gtk.Align.START)

        self.brush_entry = Gtk.Entry()
        self.brush_entry.set_hexpand(True)
        self.brush_entry.set_text("hex blank")  # default

        # A small label to show error on non exiting brush
        self.brush_error = Gtk.Label()
        self.brush_error.set_halign(Gtk.Align.START)
        self.brush_error.get_style_context().add_class("error")
        self.brush_error.set_no_show_all(True)

        def validate_brush_name(entry):
            name = entry.get_text().strip()
            brush = Gimp.Brush.get_by_name(name)

            if brush is None:
                entry.get_style_context().add_class("error")
                self.brush_error.set_text("Brush does not exist")
                self.brush_error.show()
                self.ok_button.set_sensitive(False)
            else:
                entry.get_style_context().remove_class("error")
                self.brush_error.hide()
                self.ok_button.set_sensitive(True)

        self.push_widget_labeled(label, self.brush_entry)
        self.push_widget_unlabeled(self.brush_error)
        self.brush_entry.connect("changed", validate_brush_name)
        validate_brush_name(self.brush_entry)

    def add_widgets(self):
        self.add_brush_entry()
        self.add_spin_rows()
        self.add_spin_cols()
        self.add_numbering()
        self.add_spin_x0()
        self.add_spin_y0()
        self.add_spin_x1()
        self.add_spin_y1()

        def adjust_spin(master_spin, slave_spin):
            value = master_spin.get_value_as_int()
            adj = slave_spin.get_adjustment()
            adj.set_upper(value - 1)
            if slave_spin.get_value() >= value:
                slave_spin.set_value(value - 1)

        self.spin_cols.connect("value-changed",
                               lambda x: adjust_spin(x, self.spin_x0))
        self.spin_cols.connect("value-changed",
                               lambda x: adjust_spin(x, self.spin_x1))
        self.spin_rows.connect("value-changed",
                               lambda x: adjust_spin(x, self.spin_y0))
        self.spin_rows.connect("value-changed",
                               lambda x: adjust_spin(x, self.spin_y1))

        self.add_spin_ix()
        self.add_spin_iy()
        self.add_coord_separator()

        def update_numbering_widgets(check):
            st = check.get_active()
            self.spin_x0.set_sensitive(st)
            self.spin_y0.set_sensitive(st)
            self.spin_x1.set_sensitive(st)
            self.spin_y1.set_sensitive(st)
            self.spin_ix.set_sensitive(st)
            self.spin_iy.set_sensitive(st)
            self.coord_separator.set_sensitive(st)

        self.numbering.connect("toggled", update_numbering_widgets)
        update_numbering_widgets(self.numbering)

        self.add_large_grid()
        self.add_spin_scale()
        self.add_spin_lgrid_ccol()
        self.add_spin_lgrid_crow()

        def update_large_grid_scale(check):
            st = check.get_active()
            self.spin_scale.set_sensitive(st)
            self.spin_lgrid_crow.set_sensitive(st)
            self.spin_lgrid_ccol.set_sensitive(st)

        def adjust_lgrid_spin(master_spin, slave_spin):
            value = master_spin.get_value_as_int()
            adj = slave_spin.get_adjustment()
            adj.set_value(value // 2)
            adj.set_upper(value - 1)

        self.large_grid.connect("toggled", update_large_grid_scale)
        update_large_grid_scale(self.large_grid)
        self.spin_rows.connect(
            "value-changed",
            lambda x: adjust_lgrid_spin(x, self.spin_lgrid_crow))
        self.spin_cols.connect(
            "value-changed",
            lambda x: adjust_lgrid_spin(x, self.spin_lgrid_ccol))
        adjust_lgrid_spin(self.spin_cols, self.spin_lgrid_ccol)
        adjust_lgrid_spin(self.spin_rows, self.spin_lgrid_crow)


class HexMap4Gimp(Gimp.PlugIn):
    def do_set_i18n(self, proc_name):
        return (False, None, None)

    def do_query_procedures(self):
        return [new_hexmap]

    def do_create_procedure(self, name):
        if name != new_hexmap:
            return None

        proc = Gimp.ImageProcedure.new(
            self,
            name,
            Gimp.PDBProcType.PLUGIN,
            self.new_hex_map,
            None
        )

        proc.set_menu_label("New Hex Map")
        proc.add_menu_path("<Image>/File/HexMap4Gimp")
        proc.set_documentation(
            "New Hex Map",
            "Creates a new image with layers for a hex map.",
            ""
        )
        proc.set_attribution("Christian", "Christian Tenllado. Based on the scheme code from DJ Mythal", "2025")
        proc.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.ALWAYS)
        return proc

    def new_hex_map(self, procedure, run_mode, image, drawable, args, data):
        GimpUi.init("hex-map-gimp")
        Gegl.init(None)
        dialog = HexMapDialog(title="HexMap Properties")

        response = dialog.run_dialog()

        if response != Gtk.ResponseType.OK:
            dialog.destroy()
            return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)

        brush_name = dialog.brush_entry.get_text().strip()
        hex_brush = Gimp.Brush.get_by_name(brush_name)
        hexgrid = HexGrid(hex_brush)

        rows = dialog.spin_rows.get_value_as_int()
        cols = dialog.spin_cols.get_value_as_int()
        img_w, img_h = hexgrid.set_dims(rows, cols)
        img = Gimp.Image.new(img_w, img_h, Gimp.ImageBaseType.RGB)

        layer_names=["Terrain","Rivers","Roads","Cities", "Grid",
                     "LargeGrid", "Borders","Numbers"]
        layers = {}
        for name in layer_names:
            layer = Gimp.Layer.new(
                img, name, img_w, img_h, Gimp.ImageType.RGBA_IMAGE, 100,
                Gimp.LayerMode.NORMAL 
            )
            img.insert_layer(layer, None, 0)
            layer.fill(0)
            layer.edit_clear()
            layers[name] = layer


        hexgrid.draw(img)

        numbering = dialog.numbering.get_active()
        if numbering:
            x0 = dialog.spin_x0.get_value_as_int()
            y0 = dialog.spin_y0.get_value_as_int()
            x1 = dialog.spin_x1.get_value_as_int()
            y1 = dialog.spin_y1.get_value_as_int()
            ix = dialog.spin_ix.get_value_as_int()
            iy = dialog.spin_iy.get_value_as_int()
            separator = dialog.coord_separator.get_text()
            hexgrid.draw_labels(img, x0, y0, x1, y1, ix, iy, separator)
        else:
            img.remove_layer(layers["Numbers"])

        large_grid = dialog.large_grid.get_active()
        if large_grid:
            lgrid_crow = dialog.spin_lgrid_crow.get_value_as_int()
            lgrid_ccol = dialog.spin_lgrid_ccol.get_value_as_int()
            lgrid_scale = dialog.spin_scale.get_value_as_int()
            hexgrid.draw_large_grid(img, lgrid_scale, lgrid_ccol, lgrid_crow)
        else:
            img.remove_layer(layers["LargeGrid"])

        hexgrid.set_gimp_grid(img)
        img.set_selected_layers([layers["Terrain"]])

        dialog.destroy()
        Gimp.Display.new(img)
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

Gimp.main(HexMap4Gimp.__gtype__, sys.argv)
