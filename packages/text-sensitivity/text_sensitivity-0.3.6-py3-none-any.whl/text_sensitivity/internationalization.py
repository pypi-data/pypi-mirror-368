"""Support for i18n internationalization, using text_explainability to globally set the languages.

Todo:
- Add ability to extend text_explainability vocab per language
"""

from text_explainability.internationalization import (get_locale, set_locale,
                                                      translate_list,
                                                      translate_string)

LOCALE_MAP = {'br': 'pt_BR',
              'cs': 'cs_CZ',
              'da': 'da_DK',
              'el': 'el_GR',
              'ph': 'fil_PH',
              'fr': 'fr_FR',
              'ga': 'ga_IE',
              'hi': 'hi_IN',
              'hr': 'hr_HR',
              'hu': 'hu_HU',
              'id': 'id_ID',
              'it': 'it_IT',
              'jp': 'ja_JP',
              'ka': 'ka_GE',
              'lt': 'lt_LT',
              'lv': 'lv_LV',
              'nl': 'nl_NL',
              'no': 'no_NO',
              'pl': 'pl_PL',
              'pt': 'pt_PT',
              'ro': 'ro_RO',
              'ru': 'ru_RU',
              'sk': 'sk_SK',
              'tr': 'tr_TR',
              'uk': 'uk_UA'}


__all__ = [translate_string, translate_list, set_locale, get_locale, LOCALE_MAP]
