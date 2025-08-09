#!/home/twinkle/venv/bin/python
# -*- encoding: utf-8 -*-

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk # GDK_SELECTION_CLIPBOARD
#from gi.repository import Pango

######################################################################
# VARS

MessageType = {
     'GTK_MESSAGE_INFO': 0,
  'GTK_MESSAGE_WARNING': 1,
 'GTK_MESSAGE_QUESTION': 2,
    'GTK_MESSAGE_ERROR': 3,
    'GTK_MESSAGE_OTHER': 4,
}

ButtonType = {
      'GTK_BUTTONS_NONE': 0,
        'GTK_BUTTONS_OK': 1,
     'GTK_BUTTONS_CLOSE': 2,
    'GTK_BUTTONS_CANCEL': 3,
    'GTK_BUTTONS_YES_NO': 4,
 'GTK_BUTTONS_OK_CANCEL': 5,
}

ResponseType = {
         'GTK_RESPONSE_NONE': -1,
       'GTK_RESPONSE_REJECT': -2,
       'GTK_RESPONSE_ACCEPT': -3,
 'GTK_RESPONSE_DELETE_EVENT': -4,
           'GTK_RESPONSE_OK': -5,
       'GTK_RESPONSE_CANCEL': -6,
        'GTK_RESPONSE_CLOSE': -7,
          'GTK_RESPONSE_YES': -8,
           'GTK_RESPONSE_NO': -9,
        'GTK_RESPONSE_APPLY': -10,
         'GTK_RESPONSE_HELP': -11,
}

# Message Type
GTK_MESSAGE_INFO = Gtk.MessageType.INFO                   # 0
GTK_MESSAGE_WARNING = Gtk.MessageType.WARNING             # 1
GTK_MESSAGE_QUESTION = Gtk.MessageType.QUESTION           # 2
GTK_MESSAGE_ERROR = Gtk.MessageType.ERROR                 # 3
GTK_MESSAGE_OTHER = Gtk.MessageType.OTHER                 # 4

# Button Type
GTK_BUTTONS_NONE = Gtk.ButtonsType.NONE                   # 0
GTK_BUTTONS_OK = Gtk.ButtonsType.OK                       # 1
GTK_BUTTONS_CLOSE = Gtk.ButtonsType.CLOSE                 # 2
GTK_BUTTONS_CANCEL = Gtk.ButtonsType.CANCEL               # 3
GTK_BUTTONS_YES_NO = Gtk.ButtonsType.YES_NO               # 4
GTK_BUTTONS_OK_CANCEL = Gtk.ButtonsType.OK_CANCEL         # 5

# Response Type
GTK_RESPONSE_NONE = Gtk.ResponseType.NONE                 # -1
GTK_RESPONSE_REJECT = Gtk.ResponseType.REJECT             # -2
GTK_RESPONSE_ACCEPT = Gtk.ResponseType.ACCEPT             # -3
GTK_RESPONSE_DELETE_EVENT = Gtk.ResponseType.DELETE_EVENT # -4
GTK_RESPONSE_OK = Gtk.ResponseType.OK                     # -5
GTK_RESPONSE_CANCEL = Gtk.ResponseType.CANCEL             # -6
GTK_RESPONSE_CLOSE = Gtk.ResponseType.CLOSE               # -7
GTK_RESPONSE_YES = Gtk.ResponseType.YES                   # -8
GTK_RESPONSE_NO = Gtk.ResponseType.NO                     # -9
GTK_RESPONSE_APPLY = Gtk.ResponseType.APPLY               # -10
GTK_RESPONSE_HELP = Gtk.ResponseType.HELP                 # -11

######################################################################
# CLASS

def gdialog(dtext='Nothing.', label='label', title='dialog', dtype=GTK_MESSAGE_INFO, btype=GTK_BUTTONS_OK, markup=True):

    if dtype == GTK_MESSAGE_ERROR:
        print(f"{__name__}: {dtext}\n")
    else:
        print(f"{__name__}: {dtext}\n")

    dialog = Gtk.MessageDialog(
                               transient_for=Gtk.Window(),
                               flags=Gtk.DialogFlags.MODAL,
                               message_type=dtype,
                               buttons=btype,
                               #message_format=label
                               #text=label
                               )

    dialog.set_default_size(320, 256)
    dialog.set_title(title)
    dialog.set_markup(label)
    dialog.set_skip_taskbar_hint(False);
    dialog.set_position(Gtk.WindowPosition.CENTER);

    if markup is True:
        dialog.format_secondary_markup(dtext);
    else:
        dialog.format_secondary_text(dtext);

    # メッセージエリア内のGtkLabelを取得し、選択可能にする
    # GtkMessageDialog.get_message_area() は GtkBox を返す
    # その GtkBox の子ウィジェットが GtkLabel
    message_area = dialog.get_message_area()
    # GtkMessageDialog のメッセージラベルは、通常、message_area の最初の子（主メッセージ）です
    for child in message_area.get_children():
        if isinstance(child, Gtk.Label):
            child.set_selectable(True)
            #break # 最初に見つかったGtkLabelだけを対象とする場合

    retv = dialog.run()

    # クリップボードオブジェクトを取得
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    # クリップボードの内容を永続化（ストア）
    # これにより、アプリケーションが終了してもクリップボードの内容が保持されます
    clipboard.store()

    dialog.destroy()
    # ^^;
    return retv

def gtxview(dtext='Nothing.', label='label', title='dialog', dtype=GTK_MESSAGE_INFO, btype=GTK_BUTTONS_OK, markup=True):

    def on_close(fixed, widget):
        widget.close()

    if dtype == GTK_MESSAGE_ERROR:
        print(f"{__name__}: {dtext}\n")
    else:
        print(f"{__name__}: {dtext}\n")

    gwin = Gtk.Window()

    dialog = Gtk.Dialog(
               title=title,
               transient_for=gwin,
               flags=Gtk.DialogFlags.MODAL,
               )

    dialog.set_default_size(384, 512)
    dialog.set_skip_taskbar_hint(False);
    dialog.set_position(Gtk.WindowPosition.CENTER);
    dialog.set_title(title)

    box = dialog.get_content_area()

    #attr = Pango.AttrList()
    #attr.insert(Pango.attr_foreground_new(65535, 0, 0))
    #attr.insert(Pango.attr_size_new(Pango.SCALE * 48))
    #attr.insert(Pango.attr_family_new('Serif'))

    #lbl1 = Gtk.Label(label, attr)
    lbl1 = Gtk.Label(label)
    lbl1.set_markup(f"<big><b>{label}</b></big>")
    lbl1.set_margin_top(6)
    lbl1.set_margin_bottom(6)
    box.add(lbl1)

    # GtkTextView を作成し、テキストをセット
    textview = Gtk.TextView()
    textbuffer = textview.get_buffer()
    textbuffer.set_text(dtext)

    # 読み取り専用にする
    textview.set_editable(True)
    textview.set_wrap_mode(True)
    textview.set_cursor_visible(True) # カーソルを非表示に
    textview.set_left_margin(4)
    textview.set_right_margin(4)
    textview.set_top_margin(4)
    textview.set_bottom_margin(4)

    # スクロール可能にするために GtkScrolledWindow に入れる
    scrolled_window = Gtk.ScrolledWindow()
    scrolled_window.set_vexpand(True)
    scrolled_window.set_hexpand(False)
    scrolled_window.add(textview)

    box.pack_start(scrolled_window, True, True, 2)

    btn1 = Gtk.Button("CLOSE")
    btn1.connect("clicked", on_close, dialog)
    box.add(btn1)
    dialog.show_all()

    retv = dialog.run()

    # クリップボードオブジェクトを取得
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    # クリップボードの内容を永続化（ストア）
    # これにより、アプリケーションが終了してもクリップボードの内容が保持されます
    clipboard.store()

    dialog.destroy()
    # ^^;
    return retv

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = [
    "gdialog", "gtxview", "MessageType", "ButtonType", "ResponseType", "GTK_MESSAGE_INFO", "GTK_MESSAGE_WARNING", "GTK_MESSAGE_QUESTION", "GTK_MESSAGE_ERROR", "GTK_MESSAGE_OTHER",
    "GTK_BUTTONS_NONE", "GTK_BUTTONS_OK", "GTK_BUTTONS_CLOSE", "GTK_BUTTONS_CANCEL", "GTK_BUTTONS_YES_NO", "GTK_BUTTONS_OK_CANCEL",
    "GTK_RESPONSE_NONE", "GTK_RESPONSE_REJECT", "GTK_RESPONSE_ACCEPT", "GTK_RESPONSE_DELETE_EVENT", "GTK_RESPONSE_OK", "GTK_RESPONSE_CANCEL", "GTK_RESPONSE_CLOSE", "GTK_RESPONSE_YES", "GTK_RESPONSE_NO", "GTK_RESPONSE_APPLY", "GTK_RESPONSE_HELP",
]

""" __DATA__

__END__ """
