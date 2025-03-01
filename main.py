# main.py
import objc
from AppKit import *
from WebKit import *
from PyObjCTools import AppHelper
import os
import shutil
import urllib.request

class GrokMini(NSApplication):
    def finishLaunching(self):
        # Download and set up icon if not present
        self.setupIcon()
        
        # Create status bar item
        self.statusItem = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSSquareStatusItemLength
        )
        
        # Set icon
        icon_path = os.path.expanduser("~/Library/Application Support/GrokMini/grok-icon.png")
        if os.path.exists(icon_path):
            image = NSImage.alloc().initWithContentsOfFile_(icon_path)
            image.setSize_(NSMakeSize(18, 18))  # Size for status bar
            self.statusItem.button().setImage_(image)
        
        # Create menu
        self.menu = NSMenu.alloc().init()
        self.statusItem.setMenu_(self.menu)
        
        # Add "Toggle Grok" menu item with Ctrl+Space
        toggleItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Toggle Grok", "toggleGrok:", " "
        )
        toggleItem.setKeyEquivalentModifierMask_(NSControlKeyMask)
        self.menu.addItem_(toggleItem)
        
        # Add "Move Behind" menu item
        behindItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Move Behind", "moveBehind:", ""
        )
        self.menu.addItem_(behindItem)
        
        # Add "Uninstall" menu item
        uninstallItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Uninstall", "uninstallApp:", ""
        )
        self.menu.addItem_(uninstallItem)
        
        # Add Quit menu item
        quitItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Quit", "terminate:", "q"
        )
        self.menu.addItem_(quitItem)
        
        # Initialize window (hidden initially)
        self.window = None
        self.forceOnTop = True
        
        # Set up auto-launch
        self.setupAutoLaunch()

    def setupIcon(self):
        app_support_dir = os.path.expanduser("~/Library/Application Support/GrokMini")
        if not os.path.exists(app_support_dir):
            os.makedirs(app_support_dir)
        icon_path = os.path.join(app_support_dir, "grok-icon.png")
        if not os.path.exists(icon_path):
            urllib.request.urlretrieve(
                "https://assets.eweek.com/uploads/2025/01/grok-icon.png",
                icon_path
            )

    def setupAutoLaunch(self):
        script_path = os.path.abspath(__file__)
        app_support_dir = os.path.expanduser("~/Library/Application Support/GrokMini")
        dest_path = os.path.join(app_support_dir, "main.py")
        if not os.path.exists(dest_path):
            shutil.copy(script_path, dest_path)

    def toggleGrok_(self, sender):
        if not self.window:
            # Create window at 600x500
            screenFrame = NSScreen.mainScreen().visibleFrame()
            windowSize = NSMakeSize(600, 500)
            windowPos = NSMakePoint(
                NSMidX(screenFrame) - windowSize.width/2,
                NSMidY(screenFrame) - windowSize.height/2
            )
            
            self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                NSMakeRect(windowPos.x, windowPos.y, windowSize.width, windowSize.height),
                NSTitledWindowMask | NSClosableWindowMask | NSMiniaturizableWindowMask | NSResizableWindowMask,
                NSBackingStoreBuffered,
                False
            )
            self.window.setTitle_("GrokMini")
            self.window.setLevel_(NSFloatingWindowLevel)
            
            # Create web view
            self.webView = WKWebView.alloc().initWithFrame_(
                NSMakeRect(0, 0, windowSize.width, windowSize.height)
            )
            self.window.contentView().addSubview_(self.webView)
            
            # Load grok.com
            url = NSURL.URLWithString_("https://grok.com")
            request = NSURLRequest.requestWithURL_(url)
            self.webView.loadRequest_(request)
            
            self.window.makeKeyAndOrderFront_(None)
            NSApp.activateIgnoringOtherApps_(True)
        else:
            if self.window.isVisible():
                self.window.orderOut_(None)
            else:
                self.window.makeKeyAndOrderFront_(None)
                if self.forceOnTop:
                    self.window.setLevel_(NSFloatingWindowLevel)
                NSApp.activateIgnoringOtherApps_(True)

    def moveBehind_(self, sender):
        if self.window:
            self.forceOnTop = False
            self.window.setLevel_(NSNormalWindowLevel)

    def uninstallApp_(self, sender):
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Uninstall GrokMini")
        alert.setInformativeText_("Are you sure you want to uninstall GrokMini?")
        alert.addButtonWithTitle_("Yes")
        alert.addButtonWithTitle_("No")
        
        response = alert.runModal()
        if response == NSAlertFirstButtonReturn:  # Yes
            app_support_dir = os.path.expanduser("~/Library/Application Support/GrokMini")
            if os.path.exists(app_support_dir):
                shutil.rmtree(app_support_dir)
            app_dir = os.path.expanduser("~/Applications/GrokMini.app")
            if os.path.exists(app_dir):
                shutil.rmtree(app_dir)
            NSApp.terminate_(self)

if __name__ == "__main__":
    # Create application bundle structure
    app_name = "GrokMini"
    app_dir = os.path.expanduser(f"~/Applications/{app_name}.app/Contents/MacOS")
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    script_path = os.path.abspath(__file__)
    shutil.copy(script_path, os.path.join(app_dir, app_name))

    # Set up the application
    app = GrokMini.sharedApplication()
    NSApplication.sharedApplication().setDelegate_(app)
    
    # Run the application
    AppHelper.runEventLoop()
