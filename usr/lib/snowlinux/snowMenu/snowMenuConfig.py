#!/usr/bin/env python

import sys

import gi
gi.require_version("Gtk", "2.0")
from gi.repository import Gtk, Gdk
try:
    import gettext
    import os
    import commands
except Exception, e:
    print e
    sys.exit( 1 )

PATH = os.path.abspath( os.path.dirname( sys.argv[0] ) )

sys.path.append( os.path.join( PATH , "plugins") )

# i18n
gettext.install("snowmenu", "/usr/share/snowlinux/locale")

from easybuttons import iconManager
from easygsettings import EasyGSettings

class snowMenuConfig( object ):

    def __init__( self ):

        self.path = os.path.abspath( os.path.dirname( sys.argv[0] ) )

        # Load glade file and extract widgets
        self.builder = Gtk.Builder()
        self.builder.add_from_file (os.path.join(self.path, "mintMenuConfig.glade" ))
        self.mainWindow=self.builder.get_object("mainWindow")

        #i18n
        self.mainWindow.set_title(_("Menu preferences"))
        self.mainWindow.set_icon_from_file("/usr/lib/snowlinux/snowMenu/icon.svg")

        self.builder.get_object("showButtonIcon").set_label(_("Show button icon"))
        self.builder.get_object("showAppComments").set_label(_("Show application comments"))
        self.builder.get_object("showCategoryIcons").set_label(_("Show category icons"))
        self.builder.get_object("hover").set_label(_("Hover"))
        # self.builder.get_object("use_apt").set_label(_("Search for packages to install"))
        self.builder.get_object("buttonTextLabel").set_text(_("Button text:"))
        self.builder.get_object("label23").set_text(_("Applications"))
        self.builder.get_object("label3").set_text(_("Main button"))
        self.builder.get_object("themeLabel").set_text(_("Theme:"))
        self.builder.get_object("iconSizeLabel").set_text(_("Icon size:"))
        self.builder.get_object("iconSizeLabel2").set_text(_("Icon size:"))
        self.builder.get_object("hoverLabel").set_text(_("Hover delay (ms):"))
        self.builder.get_object("label4").set_text(_("Button icon:"))
        self.builder.get_object("label5").set_text(_("Search command:"))

        self.editPlaceDialogTitle = (_("Edit Place"))
        self.newPlaceDialogTitle = (_("New Place"))
        self.folderChooserDialogTitle = (_("Select a folder"))

        self.builder.get_object("hotkey_label").set_text(_("Keyboard shortcut:"))

        self.showAppComments = self.builder.get_object( "showAppComments" )
        # self.useAPT = self.builder.get_object( "use_apt" )
        self.showCategoryIcons = self.builder.get_object( "showCategoryIcons" )

        self.hover = self.builder.get_object( "hover" )
        self.hoverDelay = self.builder.get_object( "hoverDelay" )
        self.iconSize = self.builder.get_object( "iconSize" )
        self.favIconSize = self.builder.get_object( "favIconSize" )
        self.showButtonIcon = self.builder.get_object( "showButtonIcon" )
        self.buttonText = self.builder.get_object( "buttonText" )
        self.hotkeyText = self.builder.get_object( "hotkeyText" )
        self.buttonIcon = self.builder.get_object( "buttonIcon" )
        self.buttonIconChooser = self.builder.get_object( "button_icon_chooser" )
        self.image_filter = Gtk.FileFilter()
        self.image_filter.set_name(_("Images"))
        self.image_filter.add_pattern("*.png")
        self.image_filter.add_pattern("*.jpg")
        self.image_filter.add_pattern("*.jpeg")
        self.image_filter.add_pattern("*.bmp")
        self.image_filter.add_pattern("*.ico")
        self.image_filter.add_pattern("*.xpm")
        self.image_filter.add_pattern("*.svg")
        self.buttonIconChooser.add_filter(self.image_filter)
        self.buttonIconChooser.set_filter(self.image_filter)
        self.buttonIconImage = self.builder.get_object("image_button_icon")
        self.searchCommand = self.builder.get_object( "search_command" )

        self.builder.get_object( "closeButton" ).connect("clicked", Gtk.main_quit )


        self.settings = EasyGSettings( "com.snowlinux.snowmenu" )
        self.settingsApplications = EasyGSettings( "com.snowlinux.snowmenu.plugins.applications" )

        self.bindGSettingsValueToWidget( self.settingsApplications, "bool", "show-application-comments", self.showAppComments, "toggled", self.showAppComments.set_active, self.showAppComments.get_active )
        # self.bindGSettingsValueToWidget( self.settingsApplications, "bool", "use-apt", self.useAPT, "toggled", self.useAPT.set_active, self.useAPT.get_active )
        self.bindGSettingsValueToWidget( self.settingsApplications, "bool", "show-category-icons", self.showCategoryIcons, "toggled", self.showCategoryIcons.set_active, self.showCategoryIcons.get_active )
        self.bindGSettingsValueToWidget( self.settingsApplications, "bool", "categories-mouse-over", self.hover, "toggled", self.hover.set_active, self.hover.get_active )
        self.bindGSettingsValueToWidget( self.settingsApplications, "int", "category-hover-delay", self.hoverDelay, "value-changed", self.hoverDelay.set_value, self.hoverDelay.get_value )
        self.bindGSettingsValueToWidget( self.settingsApplications, "int", "icon-size", self.iconSize, "value-changed", self.iconSize.set_value, self.iconSize.get_value )
        self.bindGSettingsValueToWidget( self.settingsApplications, "int", "favicon-size", self.favIconSize, "value-changed", self.favIconSize.set_value, self.favIconSize.get_value )
        self.bindGSettingsValueToWidget( self.settings, "bool", "hide-applet-icon", self.showButtonIcon, "toggled", self.setShowButtonIcon, self.getShowButtonIcon )
        self.bindGSettingsValueToWidget( self.settings, "string", "applet-text", self.buttonText, "changed", self.buttonText.set_text, self.buttonText.get_text )
        self.bindGSettingsValueToWidget( self.settings, "string", "hot-key", self.hotkeyText, "changed", self.hotkeyText.set_text, self.hotkeyText.get_text )
        self.bindGSettingsValueToWidget( self.settings, "string", "applet-icon", self.buttonIconChooser, "file-set", self.setButtonIcon, self.buttonIconChooser.get_filename )
        self.bindGSettingsValueToWidget( self.settingsApplications, "string", "search-command", self.searchCommand, "changed", self.searchCommand.set_text, self.searchCommand.get_text )

        #Detect themes and show theme here
        theme_name = self.settings.get ("string", "theme-name")
        themes = commands.getoutput("find /usr/share/themes -name gtkrc")
        themes = themes.split("\n")
        model = Gtk.ListStore(str, str)
        self.builder.get_object("themesCombo").set_model(model)
        selected_theme = model.append([_("Desktop theme"), "default"])
        for theme in themes:
            if theme.startswith("/usr/share/themes") and theme.endswith("/gtk-2.0/gtkrc"):
                theme = theme.replace("/usr/share/themes/", "")
                theme = theme.replace("gtk-2.0", "")
                theme = theme.replace("gtkrc", "")
                theme = theme.replace("/", "")
                theme = theme.strip()
                iter = model.append([theme, theme])
                if theme == theme_name:
                    selected_theme = iter
        self.builder.get_object("themesCombo").set_active_iter(selected_theme)
        self.builder.get_object("themesCombo").connect("changed", self.set_theme)
        self.mainWindow.present()

    def set_theme(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        theme_name = model.get_value(iter, 1)
        self.settings.set( "string", "theme-name", theme_name)

    def setPluginsLayout (self, widget):
        visiblePlugins = 'applicatons,'
        self.settings.set ("list-string", "plugins-list", visiblePlugins)

    def setShowButtonIcon( self, value ):
        self.showButtonIcon.set_active(not value )

    def setButtonIcon( self, value ):
        self.buttonIconChooser.set_filename(value)
        self.buttonIconImage.set_from_file(value)

    def getShowButtonIcon( self ):
        return not self.showButtonIcon.get_active()

    def bindGSettingsValueToWidget( self, settings, setting_type, key, widget, changeEvent, setter, getter ):
        widget.connect( changeEvent, lambda *args: self.callGetter( settings, setting_type, key, getter ) )

        settings.notifyAdd( key, self.callSetter, args = [ setting_type, setter ] )
        if setting_type == "color":
            setter( Gdk.color_parse( settings.get( setting_type, key ) ) )
        else:
            setter( settings.get( setting_type, key ) )

    def callSetter( self, settings, key, args ):
        if args[0] == "bool":
            args[1]( settings.get_boolean(key) )
        elif args[0] == "string":
            args[1]( settings.get_string(key) )
        elif args[0] == "int":
            args[1]( settings.get_int(key) )
        elif args[0] == "color":
            args[1]( Gdk.color_parse( settings.get_string(key) ) )

    def callGetter( self, settings, setting_type, key, getter ):
        if (setting_type == "int"):
            settings.set( setting_type, key, int(getter()))
        else:
            settings.set( setting_type, key, getter())


window = snowMenuConfig()
Gtk.main()
