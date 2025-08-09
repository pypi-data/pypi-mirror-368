#!/home/twinkle/venv/bin/python

import re

######################################################################
# CLASS

class ansi:

    # start (0x1b), reset
    start = "\x1b["
    reset = "\x1b[0m"

    # ANSI Defaults
    a2h = [
        "#000000", "#800000", "#008000", "#808000", "#000080", "#800080", "#008080", "#c0c0c0",
        "#808080", "#ff0000", "#00ff00", "#ffff00", "#0000ff", "#ff00ff", "#00ffff", "#ffffff",
    ]
    # ANSI Debian
    d2h = [
        "#000000", "#aa0000", "#00aa00", "#aa5500", "#0000aa", "#aa00aa", "#00aaaa", "#aaaaaa",
        "#555555", "#ff5555", "#55ff55", "#ffff55", "#5555ff", "#ff55ff", "#55ffff", "#ffffff",
    ]
    # Complete 256
    e2h = [
        "#000000", "#800000", "#008000", "#808000", "#000080", "#800080", "#008080", "#c0c0c0",
        "#808080", "#ff0000", "#00ff00", "#ffff00", "#0000ff", "#ff00ff", "#00ffff", "#ffffff",
        "#000000", "#000033", "#000066", "#000099", "#0000cc", "#0000ff", "#003300", "#003333",
        "#003366", "#003399", "#0033cc", "#0033ff", "#006600", "#006633", "#006666", "#006699",
        "#0066cc", "#0066ff", "#009900", "#009933", "#009966", "#009999", "#0099cc", "#0099ff",
        "#00cc00", "#00cc33", "#00cc66", "#00cc99", "#00cccc", "#00ccff", "#00ff00", "#00ff33",
        "#00ff66", "#00ff99", "#00ffcc", "#00ffff", "#330000", "#330033", "#330066", "#330099",
        "#3300cc", "#3300ff", "#333300", "#333333", "#333366", "#333399", "#3333cc", "#3333ff",
        "#336600", "#336633", "#336666", "#336699", "#3366cc", "#3366ff", "#339900", "#339933",
        "#339966", "#339999", "#3399cc", "#3399ff", "#33cc00", "#33cc33", "#33cc66", "#33cc99",
        "#33cccc", "#33ccff", "#33ff00", "#33ff33", "#33ff66", "#33ff99", "#33ffcc", "#33ffff",
        "#660000", "#660033", "#660066", "#660099", "#6600cc", "#6600ff", "#663300", "#663333",
        "#663366", "#663399", "#6633cc", "#6633ff", "#666600", "#666633", "#666666", "#666699",
        "#6666cc", "#6666ff", "#669900", "#669933", "#669966", "#669999", "#6699cc", "#6699ff",
        "#66cc00", "#66cc33", "#66cc66", "#66cc99", "#66cccc", "#66ccff", "#66ff00", "#66ff33",
        "#66ff66", "#66ff99", "#66ffcc", "#66ffff", "#990000", "#990033", "#990066", "#990099",
        "#9900cc", "#9900ff", "#993300", "#993333", "#993366", "#993399", "#9933cc", "#9933ff",
        "#996600", "#996633", "#996666", "#996699", "#9966cc", "#9966ff", "#999900", "#999933",
        "#999966", "#999999", "#9999cc", "#9999ff", "#99cc00", "#99cc33", "#99cc66", "#99cc99",
        "#99cccc", "#99ccff", "#99ff00", "#99ff33", "#99ff66", "#99ff99", "#99ffcc", "#99ffff",
        "#cc0000", "#cc0033", "#cc0066", "#cc0099", "#cc00cc", "#cc00ff", "#cc3300", "#cc3333",
        "#cc3366", "#cc3399", "#cc33cc", "#cc33ff", "#cc6600", "#cc6633", "#cc6666", "#cc6699",
        "#cc66cc", "#cc66ff", "#cc9900", "#cc9933", "#cc9966", "#cc9999", "#cc99cc", "#cc99ff",
        "#cccc00", "#cccc33", "#cccc66", "#cccc99", "#cccccc", "#ccccff", "#ccff00", "#ccff33",
        "#ccff66", "#ccff99", "#ccffcc", "#ccffff", "#ff0000", "#ff0033", "#ff0066", "#ff0099",
        "#ff00cc", "#ff00ff", "#ff3300", "#ff3333", "#ff3366", "#ff3399", "#ff33cc", "#ff33ff",
        "#ff6600", "#ff6633", "#ff6666", "#ff6699", "#ff66cc", "#ff66ff", "#ff9900", "#ff9933",
        "#ff9966", "#ff9999", "#ff99cc", "#ff99ff", "#ffcc00", "#ffcc33", "#ffcc66", "#ffcc99",
        "#ffcccc", "#ffccff", "#ffff00", "#ffff33", "#ffff66", "#ffff99", "#ffffcc", "#ffffff",
        "#080808", "#121212", "#1c1c1c", "#262626", "#303030", "#3a3a3a", "#444444", "#4e4e4e",
        "#585858", "#626262", "#6c6c6c", "#767676", "#808080", "#8a8a8a", "#949494", "#9e9e9e",
        "#a8a8a8", "#b2b2b2", "#bcbcbc", "#c6c6c6", "#d0d0d0", "#dadada", "#e4e4e4", "#eeeeee",
    ]

    # ANSI Defaults
    h2a = {
        "#000000": "0", "#800000": "1", "#008000":  "2", "#808000":  "3", "#000080":  "4", "#800080":  "5", "#008080":  "6", "#c0c0c0":  "7",
        "#808080": "8", "#ff0000": "9", "#00ff00": "10", "#ffff00": "11", "#0000ff": "12", "#ff00ff": "13", "#00ffff": "14", "#ffffff": "15",
    }
    # ANSI Debian
    h2d = {
        "#000000": "0", "#aa0000": "1", "#00aa00":  "2", "#aa5500":  "3", "#0000aa":  "4", "#aa00aa":  "5", "#00aaaa":  "6",  "#aaaaaa":  "7",
        "#555555": "8", "#ff5555": "9", "#55ff55": "10", "#ffff55": "11", "#5555ff": "12", "#ff55ff": "13", "#55ffff": "14",  "#ffffff": "15",
    }
    # Complete 256
    h2e = {
        "#000000":   "0", "#800000":   "1", "#008000":   "2", "#808000":   "3", "#000080":   "4", "#800080":   "5", "#008080":   "6", "#c0c0c0":   "7",
        "#808080":   "8", "#ff0000":   "9", "#00ff00":  "10", "#ffff00":  "11", "#0000ff":  "12", "#ff00ff":  "13", "#00ffff":  "14", "#ffffff":  "15",
        "#000000":  "16", "#000033":  "17", "#000066":  "18", "#000099":  "19", "#0000cc":  "20", "#0000ff":  "21", "#003300":  "22", "#003333":  "23",
        "#003366":  "24", "#003399":  "25", "#0033cc":  "26", "#0033ff":  "27", "#006600":  "28", "#006633":  "29", "#006666":  "30", "#006699":  "31",
        "#0066cc":  "32", "#0066ff":  "33", "#009900":  "34", "#009933":  "35", "#009966":  "36", "#009999":  "37", "#0099cc":  "38", "#0099ff":  "39",
        "#00cc00":  "40", "#00cc33":  "41", "#00cc66":  "42", "#00cc99":  "43", "#00cccc":  "44", "#00ccff":  "45", "#00ff00":  "46", "#00ff33":  "47",
        "#00ff66":  "48", "#00ff99":  "49", "#00ffcc":  "50", "#00ffff":  "51", "#330000":  "52", "#330033":  "53", "#330066":  "54", "#330099":  "55",
        "#3300cc":  "56", "#3300ff":  "57", "#333300":  "58", "#333333":  "59", "#333366":  "60", "#333399":  "61", "#3333cc":  "62", "#3333ff":  "63",
        "#336600":  "64", "#336633":  "65", "#336666":  "66", "#336699":  "67", "#3366cc":  "68", "#3366ff":  "69", "#339900":  "70", "#339933":  "71",
        "#339966":  "72", "#339999":  "73", "#3399cc":  "74", "#3399ff":  "75", "#33cc00":  "76", "#33cc33":  "77", "#33cc66":  "78", "#33cc99":  "79",
        "#33cccc":  "80", "#33ccff":  "81", "#33ff00":  "82", "#33ff33":  "83", "#33ff66":  "84", "#33ff99":  "85", "#33ffcc":  "86", "#33ffff":  "87",
        "#660000":  "88", "#660033":  "89", "#660066":  "90", "#660099":  "91", "#6600cc":  "92", "#6600ff":  "93", "#663300":  "94", "#663333":  "95",
        "#663366":  "96", "#663399":  "97", "#6633cc":  "98", "#6633ff":  "99", "#666600": "100", "#666633": "101", "#666666": "102", "#666699": "103",
        "#6666cc": "104", "#6666ff": "105", "#669900": "106", "#669933": "107", "#669966": "108", "#669999": "109", "#6699cc": "110", "#6699ff": "111",
        "#66cc00": "112", "#66cc33": "113", "#66cc66": "114", "#66cc99": "115", "#66cccc": "116", "#66ccff": "117", "#66ff00": "118", "#66ff33": "119",
        "#66ff66": "120", "#66ff99": "121", "#66ffcc": "122", "#66ffff": "123", "#990000": "124", "#990033": "125", "#990066": "126", "#990099": "127",
        "#9900cc": "128", "#9900ff": "129", "#993300": "130", "#993333": "131", "#993366": "132", "#993399": "133", "#9933cc": "134", "#9933ff": "135",
        "#996600": "136", "#996633": "137", "#996666": "138", "#996699": "139", "#9966cc": "140", "#9966ff": "141", "#999900": "142", "#999933": "143",
        "#999966": "144", "#999999": "145", "#9999cc": "146", "#9999ff": "147", "#99cc00": "148", "#99cc33": "149", "#99cc66": "150", "#99cc99": "151",
        "#99cccc": "152", "#99ccff": "153", "#99ff00": "154", "#99ff33": "155", "#99ff66": "156", "#99ff99": "157", "#99ffcc": "158", "#99ffff": "159",
        "#cc0000": "160", "#cc0033": "161", "#cc0066": "162", "#cc0099": "163", "#cc00cc": "164", "#cc00ff": "165", "#cc3300": "166", "#cc3333": "167",
        "#cc3366": "168", "#cc3399": "169", "#cc33cc": "170", "#cc33ff": "171", "#cc6600": "172", "#cc6633": "173", "#cc6666": "174", "#cc6699": "175",
        "#cc66cc": "176", "#cc66ff": "177", "#cc9900": "178", "#cc9933": "179", "#cc9966": "180", "#cc9999": "181", "#cc99cc": "182", "#cc99ff": "183",
        "#cccc00": "184", "#cccc33": "185", "#cccc66": "186", "#cccc99": "187", "#cccccc": "188", "#ccccff": "189", "#ccff00": "190", "#ccff33": "191",
        "#ccff66": "192", "#ccff99": "193", "#ccffcc": "194", "#ccffff": "195", "#ff0000": "196", "#ff0033": "197", "#ff0066": "198", "#ff0099": "199",
        "#ff00cc": "200", "#ff00ff": "201", "#ff3300": "202", "#ff3333": "203", "#ff3366": "204", "#ff3399": "205", "#ff33cc": "206", "#ff33ff": "207",
        "#ff6600": "208", "#ff6633": "209", "#ff6666": "210", "#ff6699": "211", "#ff66cc": "212", "#ff66ff": "213", "#ff9900": "214", "#ff9933": "215",
        "#ff9966": "216", "#ff9999": "217", "#ff99cc": "218", "#ff99ff": "219", "#ffcc00": "220", "#ffcc33": "221", "#ffcc66": "222", "#ffcc99": "223",
        "#ffcccc": "224", "#ffccff": "225", "#ffff00": "226", "#ffff33": "227", "#ffff66": "228", "#ffff99": "229", "#ffffcc": "230", "#ffffff": "231",
        "#080808": "232", "#121212": "233", "#1c1c1c": "234", "#262626": "235", "#303030": "236", "#3a3a3a": "237", "#444444": "238", "#4e4e4e": "239",
        "#585858": "240", "#626262": "241", "#6c6c6c": "242", "#767676": "243", "#808080": "244", "#8a8a8a": "245", "#949494": "246", "#9e9e9e": "247",
        "#a8a8a8": "248", "#b2b2b2": "249", "#bcbcbc": "250", "#c6c6c6": "251", "#d0d0d0": "252", "#dadada": "253", "#e4e4e4": "254", "#eeeeee": "255",
    }

    # foreground color
    fore_black  = "30"
    fore_red    = "31"
    fore_green  = "32"
    fore_yellow = "33"
    fore_blue   = "34"
    fore_purple = "35"
    fore_cyan   = "36"
    fore_white  = "37"
    # foreground light color
    fore_light_gray    = "90"
    fore_light_red     = "91"
    fore_light_green   = "92"
    fore_light_yellow  = "93"
    fore_light_blue    = "94"
    fore_light_magenta = "95"
    fore_light_cyan    = "96"
    fore_light_white   = "97"
    # background color
    back_black  = "40"
    back_red    = "41"
    back_green  = "42"
    back_yellow = "43"
    back_blue   = "44"
    back_purple = "45"
    back_cyan   = "46"
    back_white  = "47"
    # background light color
    back_light_gray    = "100"
    back_light_red     = "101"
    back_light_green   = "102"
    back_light_yellow  = "103"
    back_light_blue    = "104"
    back_light_magenta = "105"
    back_light_cyan    = "106"
    back_light_white   = "107"
    # bold, italic, underline, blink, invert
    text_on_bold       = "1"
    text_on_faint      = "2"
    text_on_italic     = "3"
    text_on_underline  = "4"
    text_on_blink      = "5"
    text_on_rapid      = "6" # Rapid Blink
    text_on_reverse    = "7"
    text_on_conceal    = "8"
    text_on_strike     = "9"
    # bold, italic, underline, blink, invert
    text_on_doubled    = "21" # Not Bold or Doubled Underline
    text_off_bold      = "22" # Off to Bold or Faint
    text_off_italic    = "23"
    text_off_underline = "24"
    text_off_blink     = "25"
    text_roportional   = "26"
    text_off_reverse   = "28"
    text_off_strike    = "29"
    # Font
    font_primary       = "10"
    # 11 ... 19
    font_fraktur       = "20"
    # Underline
    foreground_rgb     = "38:2"
    background_rgb     = "48:2"
    underline_rgb      = "58:2"

    # foreground color
    frev_black  = "#000000"
    frev_red    = "#ff0000"
    frev_green  = "#00ff00"
    frev_yellow = "#ff5500"
    frev_blue   = "#0000ff"
    frev_purple = "#ff00ff"
    frev_cyan   = "#0000ff"
    frev_white  = "#ffffff"
    # foreground light color
    frev_light_gray    = "#999999"
    frev_light_red     = "#ff9999"
    frev_light_green   = "#99ff99"
    frev_light_yellow  = "#ffff99"
    frev_light_blue    = "#99ffff"
    frev_light_magenta = "#ff00ff"
    frev_light_cyan    = "#99ffff"
    frev_light_white   = "#ffffff"
    # background color
    brev_black  = "#000000"
    brev_red    = "#660000"
    brev_green  = "#006600"
    brev_yellow = "#666600"
    brev_blue   = "#000066"
    brev_purple = "#660066"
    brev_cyan   = "#006666"
    brev_white  = "#666666"
    # background light color
    brev_light_gray    = "#cccccc"
    brev_light_red     = "#cc6666"
    brev_light_green   = "#66cc66"
    brev_light_yellow  = "#cccc66"
    brev_light_blue    = "#6666cc"
    brev_light_magenta = "#cc66cc"
    brev_light_cyan    = "#66cccc"
    brev_light_white   = "#cccccc"
    # bold, italic, underline, blink, invert
    trev_on_bold       = "<b>{}</b>"
    trev_off_bold      = ""
    trev_on_italic     = "<i>{}</i>"
    trev_off_italic    = ""
    trev_on_underline  = "<u>{}</u>"
    trev_off_underline = ""
    trev_on_blink      = "<blink>{}</blink>"
    trev_off_blink     = ""
    trev_on_reverse    = "<span style=\x22transform: scaleX(-1);display: inline-block;\x22>{}</span>"
    trev_off_reverse   = ""

    # Color Code: Foreground, Background, Underline Color
    def frgb(self, c):
        d = int(c, base=16)
        return f"38;5;{d}"
    def brgb(self, c):
        d = int(c, base=16)
        return f"48;5;{d}"
    def urgb(self, c):
        d = int(c, base=16)
        return f"58;5;{d}"
    # RGB Color: Foreground, Background, Underline Color
    def grgb(self, r, g, b):
        x = int(r, base=16)
        y = int(g, base=16)
        z = int(b, base=16)
        return x, y, z
    # RGB Color: Foreground, Background, Underline Color
    def frgb(self, r, g, b):
        x = int(r, base=16)
        y = int(g, base=16)
        z = int(b, base=16)
        return f"38;2;{x};{y};{z}"
    def brgb(self, r, g, b):
        x = int(r, base=16)
        y = int(g, base=16)
        z = int(b, base=16)
        return f"48;2;{x};{y};{z}"
    def urgb(self, r, g, b):
        x = int(r, base=16)
        y = int(g, base=16)
        z = int(b, base=16)
        return f"58;2;{x};{y};{z}"

######################################################################
# DEFS

# Ignore ANSI Counter
def strlen(msg):
    slen = len(msg)
    mlen = ansilen(msg)
    return slen - mlen

# ANSI Counter
def ansilen(msg):
    mall = re.findall("\x1b\[[0-9;]*m", msg)
    if mall is None:
        return 0
    mstr = ''.join(mall)
    mlen = len(mstr)
    return mlen

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["ansi", "ansilen", "strlen"]

""" __DATA__

__END__ """
