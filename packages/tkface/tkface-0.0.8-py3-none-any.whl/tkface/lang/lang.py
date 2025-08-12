# lang/lang.py
import os
import tkinter as tk
from tkinter import TclError

class LanguageManager:
    def __init__(self):
        self.user_dicts = {}
        self.current_lang = 'en'
        self.msgcat_loaded = set()

    def register(self, lang_code, dictionary, root):
        if lang_code not in self.user_dicts:
            self.user_dicts[lang_code] = {}
        self.user_dicts[lang_code].update(dictionary)
        for key, value in dictionary.items():
            root.tk.call('msgcat::mcset', lang_code, key, value)

    def set(self, lang_code, root):
        if lang_code == 'auto':
            try:
                lang_code_full = root.tk.call('msgcat::mclocale').replace('-', '_')
                lang_code = lang_code_full
            except Exception:
                lang_code = 'en'
        self.current_lang = lang_code
        # Load tk standard msgcat file (optional, but keep for fallback)
        try:
            tk_library = str(root.tk.globalgetvar('tk_library'))
            msg_path_full = os.path.join(tk_library, 'msgs', f'{lang_code}.msg')
            msg_path_short = os.path.join(tk_library, 'msgs', f'{lang_code.split("_")[0]}.msg')
            loaded = False
            if os.path.exists(msg_path_full):
                root.tk.call('msgcat::mcload', msg_path_full)
                loaded = True
            elif os.path.exists(msg_path_short):
                root.tk.call('msgcat::mcload', msg_path_short)
                loaded = True
            if loaded:
                root.tk.call('msgcat::mclocale', lang_code)
                self.msgcat_loaded.add(lang_code)
        except Exception:
            pass
        # Load locales/xx_YY.msg or locales/xx.msg by parsing and mcset
        try:
            assets_path_full = os.path.join(os.path.dirname(__file__), '..', 'locales', f'{lang_code}.msg')
            assets_path_short = os.path.join(os.path.dirname(__file__), '..', 'locales', f'{lang_code.split("_")[0]}.msg')
            loaded = False
            if os.path.exists(assets_path_full):
                # Initialize user_dicts for this language
                if lang_code not in self.user_dicts:
                    self.user_dicts[lang_code] = {}
                
                with open(assets_path_full, encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if '{' in line and '}' in line:
                            key, val = line.split('{', 1)
                            key = key.strip()
                            val = val.rsplit('}', 1)[0].strip()
                            # Store in user_dicts
                            self.user_dicts[lang_code][key] = val
                            # Also set in msgcat
                            root.tk.call('msgcat::mcset', lang_code, key, val)
                root.tk.call('msgcat::mclocale', lang_code)
                self.msgcat_loaded.add(lang_code)
                loaded = True
            elif os.path.exists(assets_path_short):
                short_lang = lang_code.split('_')[0]
                # Initialize user_dicts for this language
                if short_lang not in self.user_dicts:
                    self.user_dicts[short_lang] = {}
                
                with open(assets_path_short, encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if '{' in line and '}' in line:
                            key, val = line.split('{', 1)
                            key = key.strip()
                            val = val.rsplit('}', 1)[0].strip()
                            # Store in user_dicts
                            self.user_dicts[short_lang][key] = val
                            # Also set in msgcat
                            root.tk.call('msgcat::mcset', short_lang, key, val)
                root.tk.call('msgcat::mclocale', short_lang)
                self.msgcat_loaded.add(short_lang)
                loaded = True
        except Exception:
            pass
        # Set locale!
        try:
            root.tk.call('msgcat::mclocale', lang_code)
        except Exception:
            pass

    def get(self, key, root=None, language=None):
        if root is None:
            import tkinter as tk
            root = getattr(tk, '_default_root', None)
            if root is None:
                raise RuntimeError("No Tk root window found. Please create a Tk instance or pass root explicitly.")
        lang_code = language or self.current_lang
        if lang_code in self.user_dicts and key in self.user_dicts[lang_code]:
            result = self.user_dicts[lang_code][key]
            return result
        try:
            orig_locale = root.tk.call('msgcat::mclocale')
            root.tk.call('msgcat::mclocale', lang_code)
            translated = root.tk.call('::msgcat::mc', key)
            root.tk.call('msgcat::mclocale', orig_locale)
            if translated != key:
                return translated
        except Exception:
            pass
        try:
            root.tk.call('msgcat::mclocale', 'en')
            translated = root.tk.call('::msgcat::mc', key)
            if translated != key:
                return translated
        except Exception:
            pass
        return key

    mc = get  # alias

    def available(self):
        """
        Return a sorted list of available language codes (user, msgcat, and 'en').
        """
        langs = set()
        if self.user_dicts:
            langs.update(self.user_dicts.keys())
        if self.msgcat_loaded:
            langs.update(self.msgcat_loaded)
        langs.add('en')
        return sorted(langs)

    def load_msg(self, lang_code, msg_path, root):
        """
        Load a .msg file into msgcat for the specified language code.
        """
        try:
            root.tk.call('msgcat::mcload', os.path.abspath(msg_path))
            self.msgcat_loaded.add(lang_code)
        except Exception:
            pass

    def clear(self, lang_code):
        """
        Remove the user dictionary for the specified language code.
        """
        if lang_code in self.user_dicts:
            del self.user_dicts[lang_code]

    def current(self):
        """
        Return the current language code in use.
        """
        return self.current_lang

    def get_dict(self, lang_code):
        """
        Return the user dictionary for the specified language code.
        """
        return self.user_dicts.get(lang_code, {})

__all__ = ['LanguageManager'] 