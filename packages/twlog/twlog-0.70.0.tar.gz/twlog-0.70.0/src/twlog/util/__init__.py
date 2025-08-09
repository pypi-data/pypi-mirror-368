#!/home/twinkle/venv/bin/python

import sys

######################################################################
# LIBS

from twlog.util.ANSIColor import ansi

######################################################################
# VARS

# {ansi.start}...m
first            = "🌠 \x1b[94;1m"
# ?{ansi.reset}
title_structure  = ":\x1b[0m"
# e.g. -> {ansi.start}{ansi.fore_light_red};{ansi.text_on_bold}m->{ansi.reset}
middle_structure = ""
split            = " "

######################################################################
# CLASS

######################################################################
# DEFS

# Print for as options pair values. You guys not yet see EBI 🍤🍤🍤🍤
def popts(b, *t):
    b = str(b)
    a = [""] * len(t) 
    for i in range(len(t)):
        a[i] = str(t[i])
    m = f"\x1b[1m{b}:\x1b[0m "
    m += ", ".join(a)
    print(f"{m}")

# Pront for solo value, not includes line break
def psolo(m):
    print(m, end='')

#=====================================================================
# Priny: 🌠 Free Style 自由形式
def priny(b, *t):
    b = str(b)
    a = [""] * len(t) 
    for i in range(len(t)):
        a[i] = str(t[i])
    m = f"{first}{b}{title_structure}{middle_structure} "
    m += f"{split}".join(a)
    print(m)

#=====================================================================
# Pixie: 🧚✨✨✨✨✨ たのしいデバッグ用
def pixie(b, *t):
    b = str(b)
    a = [""] * len(t) 
    for i in range(len(t)):
        a[i] = str(t[i])
    #m = f"🧚✨✨✨ {ansi.start}{ansi.fore_light_blue};{ansi.text_on_blink};{ansi.text_on_bold}m{b} {ansi.reset}✨✨ "
    m = f"🧚✨✨✨ \x1b[36;5;1m{b}\x1b[0m ✨✨ "
    m += ", ".join(a)
    print(m)

#=====================================================================
# Prain: 🌈 Rainbow 🌈
def prain(b, *t):
    b = str(b)
    a = [""] * len(t) 
    for i in range(len(t)):
        a[i] = str(t[i])
    #m = f"{ansi.start}{ansi.fore_light_yellow};{ansi.text_on_bold}m{b}:{ansi.reset} "
    m = f"\x1b[93;1m{b}:\x1b[0m "
    m += ", ".join(a)
    print(f"🌈 {m}")

#=====================================================================
# Paint: 🎨 Paint Brush 🖌️
def paint(b, *t):
    b = str(b)
    a = [""] * len(t) 
    for i in range(len(t)):
        a[i] = str(t[i])
    #m = f"{ansi.start}{ansi.fore_light_magenta};{ansi.text_on_bold}m{b}:{ansi.reset} "
    m = f"\x1b[95;1m{b}\x1b[0m 🖌️ "
    m += "\x20🖌️".join(a)
    print(f"🎨 {m}")

#=====================================================================
# Plume: 🌬️ふーっ🌬️
def plume(b, *t):
    b = str(b)
    a = [""] * len(t) 
    for i in range(len(t)):
        a[i] = str(t[i])
    #m = f"{ansi.start}{ansi.fore_white};{ansi.text_on_bold}m{b}{ansi.reset} 🌬️\x20\x20"
    m = f"\x1b[97;1m{b}\x1b[0m 🌬️ "
    n = " ".join(a)
    #print(f"{m} {ansi.start}{ansi.fore_light_cyan};{ansi.text_on_italic}m{n}{ansi.reset} ")
    print(f"🌬️\x20\x20{m} \x1b[96;3m{n}\x1b[0m")

#=====================================================================
# Prank: 🤡🎭
def prank(b, *t):
    b = str(b)
    a = [""] * len(t) 
    for i in range(len(t)):
        a[i] = str(t[i])
    #m = f"{ansi.start}{ansi.fore_light_green};{ansi.text_on_bold}m{b}{ansi.reset} {ansi.start}{ansi.fore_light_red};{ansi.text_on_bold}m->{ansi.reset} "
    m = f"\x1b[92;1m{b}\x1b[0m \x1b[91;1m->\x1b[0m "
    m += " ".join(a)
    print(f"🤡 {m}")

#=====================================================================
# Prown: 🦞えび🦞 🍤Fried Prown🍤
def prown(b, *t):
    b = str(b)
    a = [""] * len(t) 
    for i in range(len(t)):
        a[i] = str(t[i])
    #m = f"{ansi.start}{ansi.fore_light_red};{ansi.text_on_bold}m{b}:{ansi.reset} "
    m = f"\x1b[91;1m{b}:\x1b[0m "
    m += ", ".join(a)
    print(f"🍤 {m}")

#=====================================================================
# Pinok: 🍄きのこ🍄 🍄‍🟫生えた🍄‍🟫
def pinok(b, *t):
    b = str(b)
    a = [""] * len(t) 
    for i in range(len(t)):
        a[i] = str(t[i])
    #m = f"{ansi.start}{ansi.fore_light_red};{ansi.text_on_bold}m{b}:{ansi.reset} "
    m = f"\x1b[91;1m{b}:\x1b[0m "
    m += ", ".join(a)
    print(f"🍄 {m}")

#=====================================================================
# Peach: 🍑桃さんくださ〜い！
def peach(b, *t):
    b = str(b)
    a = [""] * len(t) 
    for i in range(len(t)):
        a[i] = str(t[i])
    #m = f"{ansi.start}{ansi.fore_light_red};{ansi.text_on_bold}m{b}:{ansi.reset} "
    m = f"\x1b[95;1m{b}:\x1b[0m "
    m += ", ".join(a)
    print(f"🍑 {m}")

#=====================================================================
# Prism: 三稜鏡 🔮💎🪩🎆🎇🪅🎊🎉🎑☄️✨🌌🌠🌫️🫧🌈🏜️🏞️🌅🌄
def prism(b, *t):
    b = str(b)
    a = [""] * len(t) 
    for i in range(len(t)):
        a[i] = str(t[i])
    #m = f"{ansi.start}{ansi.fore_cyan};{ansi.text_on_bold}m{b}:{ansi.reset}\n\t"
    m = f"\x1b[96;1m{b}:\x1b[0m\n\t"
    m += "\n\t".join(a)
    print(f"🪩 {m}")

#plume 🪶🌬️（羽根、風の流れ）
#pulse 💓🔄（脈拍、信号の変化）
#pivot 🔄🔀（回転、軸の切り替え）
#prank 🤡🎭（ちょっとした遊びやデバッグ用メッセージに）
#pixie 🧚✨（魔法っぽいエフェクト付きの情報表示）
#paint 🎨🖌️（色を表現するログ出力）

######################################################################
# CODE

def _get_caller_class_name():
    import inspect
    caller_frame = inspect.currentframe().f_back
    caller_class = caller_frame.f_locals.get('self', None).__class__
    return caller_class.__name__

def safedate(src: dict, dest: dict):
    for key in dest.keys():
        if key not in src:
            src[key] = dest[key]

def export_global_namespace(name=None):
    if name is not None:
        c = sys.modules.get(name)
        if c is None:
            c = sys.modules.get(_get_caller_class_name())
            if c is not None:
                # Update
                safedate(src=c.__dict__, dest=__all__)

def export_builtins_namespace():
    # Update
    safedate(src=__builtins__, dest=__all__)

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["psolo", "popts", "priny", "pixie", "prain", "paint", "plume", "prank", "prown", "pinok", "peach", "prism"]

""" __DATA__

__END__ """
