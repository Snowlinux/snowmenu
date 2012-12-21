#!/usr/bin/env python

import sys

try:
    import pygtk
    pygtk.require( "2.0" )
except:
    pass
try:
    import gtk
    import gtk.glade
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
from easygconf import EasyGConf

class snowMenuConfig( object ):

    def __init__( self ):

        self.path = os.path.abspath( os.path.dirname( sys.argv[0] ) )

        # Load glade file and extract widgets
        gladefile = os.path.join( self.path, "snowMenuConfig.glade" )
        wTree     = gtk.glade.XML( gladefile, "mainWindow" )
        self.mainWindow=wTree.get_widget("mainWindow")

        #i18n
        self.mainWindow.set_title(_("Menu preferences"))
        self.mainWindow.set_icon_from_file("/usr/lib/snowlinux/snowMenu/icon.svg")

        wTree.get_widget("showButtonIcon").set_label(_("Show button icon"))
        wTree.get_widget("showAppComments").set_label(_("Show application comments"))
        wTree.get_widget("showCategoryIcons").set_label(_("Show category icons"))
        wTree.get_widget("hover").set_label(_("Hover"))
        # wTree.get_widget("use_apt").set_label(_("Search for packages to install"))
        wTree.get_widget("buttonTextLabel").set_text(_("Button text:"))
        wTree.get_widget("label23").set_text(_("Applications"))
        wTree.get_widget("label3").set_text(_("Main button"))
        wTree.get_widget("themeLabel").set_text(_("Theme:"))
        wTree.get_widget("iconSizeLabel").set_text(_("Icon size:"))
        wTree.get_widget("iconSizeLabel2").set_text(_("Icon size:"))
        wTree.get_widget("hoverLabel").set_text(_("Hover delay (ms):"))
        wTree.get_widget("label4").set_text(_("Button icon:"))
        wTree.get_widget("label5").set_text(_("Search command:"))

        self.editPlaceDialogTitle = (_("Edit Place"))
        self.newPlaceDialogTitle = (_("New Place"))
        self.folderChooserDialogTitle = (_("Select a folder"))

        wTree.get_widget("hotkey_label").set_text(_("Keyboard shortcut:"))

        self.showAppComments = wTree.get_widget( "showAppComments" )
        # self.useAPT = wTree.get_widget( "use_apt" )
        self.showCategoryIcons = wTree.get_widget( "showCategoryIcons" )

        self.hover = wTree.get_widget( "hover" )
        self.hoverDelay = wTree.get_widget( "hoverDelay" )
        self.iconSize = wTree.get_widget( "iconSize" )
        self.favIconSize = wTree.get_widget( "favIconSize" )
        self.showButtonIcon = wTree.get_widget( "showButtonIcon" )
        self.buttonText = wTree.get_widget( "buttonText" )
        self.hotkeyText = wTree.get_widget( "hotkeyText" )
        self.buttonIcon = wTree.get_widget( "buttonIcon" )
        self.buttonIconChooser = wTree.get_widget( "button_icon_chooser" )
        self.image_filter = gtk.FileFilter()
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
        self.buttonIconImage = wTree.get_widget("image_button_icon")
        self.searchCommand = wTree.get_widget( "search_command" )

        wTree.get_widget( "closeButton" ).connect("clicked", gtk.main_quit )


        self.gconf = EasyGConf( "/apps/snowMenu/" )
        self.gconfApplications = EasyGConf( "/apps/snowMenu/plugins/applications/" )

        self.bindGconfValueToWidget( self.gconfApplications, "bool", "show_application_comments", self.showAppComments, "toggled", self.showAppComments.set_active, self.showAppComments.get_active )
        # self.bindGconfValueToWidget( self.gconfApplications, "bool", "use_apt", self.useAPT, "toggled", self.useAPT.set_active, self.useAPT.get_active )
        self.bindGconfValueToWidget( self.gconfApplications, "bool", "show_category_icons", self.showCategoryIcons, "toggled", self.showCategoryIcons.set_active, self.showCategoryIcons.get_active )
        self.bindGconfValueToWidget( self.gconfApplications, "bool", "categories_mouse_over", self.hover, "toggled", self.hover.set_active, self.hover.get_active )
        self.bindGconfValueToWidget( self.gconfApplications, "int", "category_hover_delay", self.hoverDelay, "value-changed", self.hoverDelay.set_value, self.hoverDelay.get_value )
        self.bindGconfValueToWidget( self.gconfApplications, "int", "icon_size", self.iconSize, "value-changed", self.iconSize.set_value, self.iconSize.get_value )
        self.bindGconfValueToWidget( self.gconfApplications, "int", "favicon_size", self.favIconSize, "value-changed", self.favIconSize.set_value, self.favIconSize.get_value )
        self.bindGconfValueToWidget( self.gconf, "bool", "hide_applet_icon", self.showButtonIcon, "toggled", self.setShowButtonIcon, self.getShowButtonIcon )
        self.bindGconfValueToWidget( self.gconf, "string", "applet_text", self.buttonText, "changed", self.buttonText.set_text, self.buttonText.get_text )
        self.bindGconfValueToWidget( self.gconf, "string", "hot_key", self.hotkeyText, "changed", self.hotkeyText.set_text, self.hotkeyText.get_text )
        self.bindGconfValueToWidget( self.gconf, "string", "applet_icon", self.buttonIconChooser, "file-set", self.setButtonIcon, self.buttonIconChooser.get_filename )
        self.bindGconfValueToWidget( self.gconfApplications, "string", "search_command", self.searchCommand, "changed", self.searchCommand.set_text, self.searchCommand.get_text )

        #Detect themes and show theme here
        theme_name = commands.getoutput("mateconftool-2 --get /apps/snowMenu/theme_name").strip()
        themes = commands.getoutput("find /usr/share/themes -name gtkrc")
        themes = themes.split("\n")
        model = gtk.ListStore(str, str)
        wTree.get_widget("themesCombo").set_model(model)
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
        wTree.get_widget("themesCombo").set_active_iter(selected_theme)
        wTree.get_widget("themesCombo").connect("changed", self.set_theme)
        self.mainWindow.present()

    def set_theme(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        theme_name = model.get_value(iter, 1)
        os.system("mateconftool-2 --type string --set /apps/snowMenu/theme_name \"%s\"" % theme_name)

    def setPluginsLayout (self, widget):
        visiblePlugins = 'applicatons,'
        os.system("mateconftool-2 --type list --list-type string --set /apps/snowMenu/plugins_list [%s]" % visiblePlugins)

    def setShowButtonIcon( self, value ):
        self.showButtonIcon.set_active(not value )

    def setButtonIcon( self, value ):
        self.buttonIconChooser.set_filename(value)
        self.buttonIconImage.set_from_file(value)

    def getShowButtonIcon( self ):
        return not self.showButtonIcon.get_active()

    def bindGconfValueToWidget( self, gconf, gconfType, gconfPath, widget, changeEvent, setter, getter ):
        widget.connect( changeEvent, lambda *args: self.callGetter( gconf, gconfType, gconfPath, getter ) )

        gconf.notifyAdd( gconfPath, self.callSetter, args = [ gconfType, setter ] )
        if gconfType == "color":
            setter( gtk.gdk.color_parse( gconf.get( gconfType, gconfPath ) ) )
        else:
            setter( gconf.get( gconfType, gconfPath ) )

    def callSetter( self, client, connection_id, entry, args ):
        if args[0] == "bool":
            args[1]( entry.get_value().get_bool() )
        elif args[0] == "string":
            args[1]( entry.get_value().get_string() )
        elif args[0] == "int":
            args[1]( entry.get_value().get_int() )
        elif args[0] == "color":
            args[1]( gtk.gdk.color_parse( entry.get_value().get_string() ) )

    def callGetter( self, gconf, gconfType, gconfPath, getter ):
        if (gconfType == "int"):
            gconf.set( gconfType, gconfPath, int(getter()))
        else:
            gconf.set( gconfType, gconfPath, getter())


window = snowMenuConfig()
gtk.main()
