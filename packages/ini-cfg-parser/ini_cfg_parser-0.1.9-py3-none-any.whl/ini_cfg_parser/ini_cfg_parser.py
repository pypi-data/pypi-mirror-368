# SPDX-License-Identifier: MIT
# Copyright (c) 2025 pukkunk
# coding: utf-8

import os
import sys
import re
import pprint
import copy
import csv
import io
import configparser
from enum import IntEnum,auto
from typing import Any, List, Tuple, Dict, Union, Optional, Callable, get_origin, get_args, TypedDict, Type, cast

class DieMode(IntEnum):
    nSysExit = auto()
    nTkInter = auto()
    nException = auto()
    nTkInterException = auto()

class IniParserError(Exception):
    pass

OK_VAL = 0
NG_VAL = 1

# 型エイリアスの定義
IniType = Union[Type[str], Type[int], Type[float], Type[bool], Type[List[str]], Type[List[int]], Type[List[float]], Type[List[bool]]]
IniValue = Union[str, int, float, bool, List[str], List[int], List[float], List[bool]]

# IniValue の型一覧を取得
IniValueTypes = get_args(IniValue)

# 各ini項目の型
class IniItem(TypedDict):
    type: IniType
    inf: IniValue

# セクションごとの構造
IniDict = Dict[str, Dict[str, IniItem]]

class IniParser:
    mode = DieMode.nException
    use_def_val: bool = False
    fallback_def_val: Optional[IniValue] = None
    # 0: 無効, 1: INFO, 2: DEBUG, 3: TRACEなど
    _DEBUG_MODE = 0  # クラス変数（全インスタンス共通）
    _DEBUG_STREAM = sys.stdout  # 出力先（デフォルトは標準出力）
    _DIEPRINT_STREAM = sys.stdout  # 出力先（デフォルトは標準出力）

    _sentinel = object()  # 特別なダミーオブジェクト

    def __init__(self, ini_path: str, get_ini_dict_val: IniDict, encoding: str):
        if not self._is_valid_ini_value(IniParser.fallback_def_val):
            msg = f"called def {sys._getframe().f_code.co_name}()\n"
            msg += f"Error detect. The type of fallback_def_val is invalid. Please specify a value of type IniValue or None.\n"
            msg += f"IniParser.fallback_def_val: {IniParser.fallback_def_val}\n"
            msg += f"Current type: {type(IniParser.fallback_def_val)}"
            IniParser.die_print(msg)
        if not isinstance(IniParser.use_def_val, bool):
            msg = f"called def {sys._getframe().f_code.co_name}()\n"
            msg += f"Error detect. The type of use_def_val is invalid. Please specify a value of type bool.\n"
            msg += f"IniParser.use_def_val: {IniParser.use_def_val}\n"
            msg += f"Current type: {type(IniParser.use_def_val)}"
            IniParser.die_print(msg)
        self.ini_path = ini_path
        self.config = configparser.ConfigParser(defaults=None, interpolation=None)
        if not isinstance(ini_path, str):
            msg = f"called def {sys._getframe().f_code.co_name}()\n"
            msg += f"Error detect. The type of ini_path is invalid. type is not 'str'\n"
            msg += f"ini_path: {ini_path}\n"
            msg += f"Current type: {type(ini_path)}"
            IniParser.die_print(msg)
        if not isinstance(encoding, str):
            msg = f"called def {sys._getframe().f_code.co_name}()\n"
            msg += f"Error detect. The type of encoding is invalid. type is not 'str'\n"
            msg += f"encoding: {encoding}\n"
            msg += f"Current type: {type(encoding)}"
            IniParser.die_print(msg)
        if(IniParser.is_valid_ini_dict(get_ini_dict_val) == False):
            msg = f"called def {sys._getframe().f_code.co_name}()\n"
            msg += f"Error detect. The type of get_ini_dict_val is invalid. type is not 'IniDict'\n"
            msg += pprint.pformat(get_ini_dict_val)
            IniParser.die_print(msg)
        self.encoding = encoding
        self.parsed_val: Dict[str, Dict[str, Any]] = {}

        self.ini_dict = get_ini_dict_val
        self.def_dict = self._merge_config_sections()

        try:
            self._validate_ini_dict_types()  # 型チェックを追加
        except IniParserError as e:
            IniParser.die_print(str(e))

        # default_dict を自動生成
        self.default_dict = self._generate_default_dict()

        if not os.path.isfile(self.ini_path):
            self._create_default_ini_file()
        else:
            self.read_inifile(self.ini_path, self.config)

        self._load_values_from_file()

    def items(self):
        for section in self.sections():
            yield section, dict(self[section].items())

    ##@fn _validate_ini_dict_types()
    # @brief        dict型変数self.ini_dictをチェックし、規定のdict型であるかを検証する。規定外の場合exception IniParserErrorを発生。
    # @param[in]    None            : 
    # @retval       None            : 
    def _validate_ini_dict_types(self):
        for section, params in self.ini_dict.items():
            for key, val_info in params.items():
                # key='type' または key='inf' が欠けている場合はエラー
                if 'type' not in val_info:
                    raise IniParserError(f"[MissingKeyError] {section}.{key} is missing required field 'type'.")
                if 'inf' not in val_info:
                    raise IniParserError(f"[MissingKeyError] {section}.{key} is missing required field 'inf'.")

                # 期待のtype情報を取得
                expected_type = val_info['type']
                # 実際の情報を取得
                actual_val = val_info['inf']

                # 実際の情報の型をチェックし、期待の型と一致していることを確認。
                if not self._is_instance_of_type(actual_val, expected_type):
                    msg = f"[TypeError] {section}.{key} has value {actual_val}, which is not of expected type {expected_type}."
                    raise IniParserError(msg)


    ##@fn _is_instance_of_type()
    # @brief        dict型変数self.valueをチェックし、規定の型であるかを検証する。規定外の場合exception IniParserErrorを発生。
    # @param[in]    value           : [type Any]
    # @retval       None            : 
    def _is_instance_of_type(self, value: Any, expected_type: Any) -> bool:
        # 型ヒントがジェネリック型（例：List[str] や Dict[str, int]）だった場合に True になります。
        origin = get_origin(expected_type)
        # リスト型（例：List[str]）の場合のみ処理します。
        if origin is not None:
            # ジェネリック（例：List[str]）
            if origin is list:
                if not isinstance(value, list):
                    return False
                item_type = get_args(expected_type)[0]
                # value のすべての要素が item_type に一致するかチェックします。1つでも違えば False になります。
                return all(isinstance(v, item_type) for v in value)
            # リスト以外のジェネリック型（Dict や Set など）は対応外なので False を返します。
            return False
        else:
            # ジェネリック型でなければ、通常の isinstance() チェックを行います。
            return isinstance(value, expected_type)

    ##@fn _generate_default_dict()
    # @brief        self.ini_dictを元にDEFAULTセクション用dictを生成（重複キーは最初の定義を優先）
    # @param[in]    None            : 
    # @retval       defaults        : [type dict]
    def _generate_default_dict(self) -> dict:
        # DEFAULTセクション用dictを生成（重複キーは最初の定義を優先）
        defaults = {}
        for section in self.ini_dict.values():
            for key, val in section.items():
                if key not in defaults:
                    defaults[key] = self._to_string(val['inf'])
        return defaults

    def _merge_config_sections(self) -> dict:
        """
        セクション"DEFAULT"のデータを優先。
        それ以外のセクションのデータでセクション"DEFAULT"に存在しないkeyがあればマージする。
        先に処理したkeyを優先。
        """
        merged = {}

        # 1. DEFAULT以外を処理：先に出たキーを優先する（上書きしない）
        for section, content in self.ini_dict.items():
            if section == 'DEFAULT':
                continue
            for key, value in content.items():
                if key not in merged:
                    merged[key] = value

        # 2. 最後にDEFAULTセクションで上書き（DEFAULTは常に優先）
        default_content = self.ini_dict.get('DEFAULT', {})
        for key, value in default_content.items():
            merged[key] = value  # 上書きOK

        return merged

    def _create_default_ini_file(self):
        # DEFAULT セクションの構築
        default_values = {}
        for section_dict in self.ini_dict.values():
            for key, val in section_dict.items():
                if key not in default_values:
                    default_values[key] = self._serialize(val['inf'])  # 最初の定義を優先

        self.config['DEFAULT'] = default_values

        # 各セクションの構築
        for section, items in self.ini_dict.items():
            self.config[section] = {}
            for key, val in items.items():
                self.config[section][key] = self._serialize(val['inf'])

        IniParser.write_inifile(self.ini_path, self.config, self.encoding)

    def _serialize(self, value: Any) -> str:
        if isinstance(value, list):
            return ",".join(map(str, value))
        elif isinstance(value, bool):
            return str(value).lower()
        else:
            return str(value)

    def _load_values_from_file(self):
        modified = False

        #ファイルが存在しない場合
        if not os.path.exists(self.ini_path):
            self.config = configparser.ConfigParser(defaults=None, interpolation=None)
            self.config._defaults.update(self.default_dict)
            modified = True  # 新規ファイル作成
        #ファイルが存在する場合
        else:
            #ファイルの情報を読み込む。
            self.config.read(self.ini_path, encoding=self.encoding)
            #対象keyが存在しない場合、セクションDEFAULTに値を設定する。
            for key, value in self.default_dict.items():
                if key not in self.config['DEFAULT']:
                    self.config['DEFAULT'][key] = value
                    modified = True

        for section, params in self.ini_dict.items():
            # 対象のsectionが存在しない場合、セクションを追加。書き込みflagをset
            if not self.config.has_section(section):
                if not section == 'DEFAULT':
                    self.config.add_section(section)
                modified = True
            if section not in self.parsed_val:
                self.parsed_val[section] = {}

            for key, val_info in params.items():
                # 期待のtype情報を取得
                expected_type = val_info['type']
                default_val = val_info['inf']
                try:
                    # 指定されたセクション (section) に、指定されたキー (key) が存在するか
                    if self.config.has_option(section, key):
                        self.debug_print(f"case1:section={section},key={key}", level=2)
                        raw_val = self.config.get(section, key)
                        val = self._cast_value(raw_val, expected_type)
                    # keyの情報がセクションDEFAULTにある場合
                    elif key in self.config.defaults():
                        self.debug_print(f"case2:section={section},key={key}", level=2)
                        raw_val = self.config.defaults()[key]
                        val = self._cast_value(raw_val, expected_type)
                    # 対象のsectionにkeyが存在しない場合、self.ini_dictから値を補完。書き込みflagはsetしない
                    else:
                        self.debug_print(f"case3:section={section},key={key}", level=2)
                        val = default_val
                        self.config.set(section, key, self._to_string(val))
                        #modified = True

                    self.parsed_val[section][key] = val
                except ValueError as e:
                    self.die_print(f"Detect error. ValueError. [{section}] {key}: {e}")
                except Exception as e:
                    self.die_print(f"Error parsing [{section}] {key}: {e}")

        if modified:
            #print(f"[INFO] iniファイルに不足キーやDEFAULTを追記保存します: {self.ini_path}")
            IniParser.write_inifile(self.ini_path, self.config, self.encoding) 

    ##@fn _cast_value()
    # @brief        引数valを引数typで指定した型にキャストする。
    # @param[in]    val             : value [type str]
    # @param[in]    typ             : type [type Any]
    # @retval                       : value [type str]
    def _cast_value(self, val: str, typ: Any) -> Any:
        try:
            if typ == bool:
                return val.lower() in ['true', '1', 'yes', 'on']
            elif typ == int:
                return int(val)
            elif typ == float:
                return float(val)
            elif typ == list or typ == List[str]:
                reader = csv.reader(io.StringIO(val), skipinitialspace=True)
                return [v.strip() for v in next(reader)] 
            elif typ == List[int]:
                reader = csv.reader(io.StringIO(val), skipinitialspace=True)
                lst_val = cast(List[str], next(reader))
                return cast(List[int], [int(v.strip()) for v in lst_val])
            elif typ == List[float]:
                reader = csv.reader(io.StringIO(val), skipinitialspace=True)
                lst_val = next(reader)
                return cast(List[float], [float(v.strip()) for v in lst_val])
            elif typ == List[bool]:
                reader = csv.reader(io.StringIO(val), skipinitialspace=True)
                lst_val = next(reader)
                truthy_values = {'true', '1', 'yes', 'on'}
                return cast(List[bool], [v.strip().lower() in truthy_values for v in lst_val])
            return val
        except Exception as e:
            raise ValueError(f"Failed to cast '{val}' to {typ}: {e}")

    ##@fn _to_string()
    # @brief        引数valの型がlistの場合、型変換でstrに変換後、","で連結する。
    # @param[in]    val             : value [type Any]
    # @retval                       : result value [type str]
    def _to_string(self, val: Any) -> str:
        if isinstance(val, list):
            return ', '.join(map(str, val))
        return str(val)

    ##@fn get()
    # @brief        ini情報を取得する。指定したsection,keyに対応した情報を取得。
    # @param[in]    section         : section name [type str]
    # @param[in]    key             : key name [type str]
    # @param[in]    fallback        : fallback value [type _sentinel]
    # @retval                       : result value [type Any]
    def get(self, section: str, key: str, fallback=_sentinel) -> Any:
        # parsed_val にすでに値があるならそれを使う
        if section in self.parsed_val and key in self.parsed_val[section]:
            return self.parsed_val[section][key]

        val = self._get_value(section, key, fallback)
        return val

    ##@fn _get_value()
    # @brief        ini情報を取得する。指定したsection,keyに対応した情報を取得。
    # @param[in]    section         : section name [type str]
    # @param[in]    key             : key name [type str]
    # @param[in]    fallback        : fallback value [type _sentinel]
    # @retval                       : result value [type Any]
    def _get_value(self, section: str, key: str, fallback: Any = _sentinel) -> Any:
        #引数fallback指定無し/指定有りを判定
        #引数fallback指定無し
        if fallback is self._sentinel:
            fallback_provided = False
            fallback_value = None
        #引数fallback指定有り
        else:
            fallback_provided = True
            fallback_value = fallback

        self.debug_print(f"---- section={section},key={key}", level=2)
        # type情報が無い場合
        if key not in self.def_dict or 'type' not in self.def_dict[key]:
            self.debug_print(f"detect keyerror. [self.def_dict] section={section},key={key}", level=2)
            # self.configにkeyが存在する場合
            if section in self.config and key in self.config[section]:
                valcfg = self.config[section][key]
                self.debug_print(f"case1:section={section},key={key},val={valcfg},type={type(valcfg)}", level=2)
                return valcfg
            # fallback指定なし and self.use_def_val = True
            elif not fallback_provided and self.use_def_val:
                self.debug_print(f"case2:section={section},key={key}", level=2)
                return self.fallback_def_val
            else:
                self.debug_print(f"case3:section={section},key={key}", level=2)
                return fallback_value
        expected_type = self.def_dict[key]['type']

        val = None
        try:
            # configに対象のsection,keyが存在することを判定
            if self.config.has_option(section, key):
                raw_val = self.config.get(section, key)
                self.debug_print(f"case4:section={section},key={key},val={raw_val},type={type(raw_val)}", level=2)
                val = self._cast_value(raw_val, expected_type)
            # 下記(1)and(2)がTrue
            # (1)引数get_ini_dict_valの指定セクション名が存在
            # (2)引数get_ini_dict_valの指定セクション名に対象のkeyが存在
            elif section in self.ini_dict and key in self.ini_dict[section]:
                self.debug_print(f"case5:section={section},key={key}", level=2)
                val = self.ini_dict[section][key]['inf']
            # configのセクション"DEFAULT"に対象のkeyが有ることを判定
            elif key in self.config.defaults():
                self.debug_print(f"case6:section={section},key={key}", level=2)
                raw_val = self.config.defaults()[key]
                val = self._cast_value(raw_val, expected_type)
            # 下記(1)and(2)がTrue
            # (1)引数get_ini_dict_valのセクション'DEFAULT'が存在
            # (2)引数get_ini_dict_valのセクション'DEFAULT'に対象のkeyが存在
            elif 'DEFAULT' in self.ini_dict and key in self.ini_dict['DEFAULT']:
                self.debug_print(f"case7:section={section},key={key}", level=2)
                val = self.ini_dict['DEFAULT'][key]['inf']
            # 下記(1)and(2)がTrue
            #(1)引数fallback指定無し
            #(2)option use_def_valで変数fallback_def_valを使用を指定
            #引数fallback指定無し
            elif not fallback_provided and self.use_def_val:
                self.debug_print(f"case8:section={section},key={key},fallback_provided={fallback_provided},use_def_val={self.use_def_val}", level=2)
                return self.fallback_def_val
            else:
                self.debug_print(f"case9:section={section},key={key},fallback_provided={fallback_provided},use_def_val={self.use_def_val}", level=2)
                return fallback_value
        except ValueError as e:
            self.debug_print(f"case10,Exception", level=2)
            self.die_print(f"Detect error. ValueError. [{section}] {key}: {e}")
        except Exception:
            self.debug_print(f"case11,Exception", level=2)
            val = fallback_value

        return val

    def add_section(self, section: str) -> None:
        """
        セクションを新規追加する関数。

        Parameters:
            section (str): 追加するセクション名
        """
        if section not in self.config:
            self.config.add_section(section)  # configparser.ConfigParserの add_section を使用
        if section not in self.ini_dict:
            self.ini_dict[section] = {}  # ini_dictにも空の辞書を登録する

    def add_ini_dict_keys(self, section: str, items: Dict[str, IniItem]) -> None:
        """
        ini_dict に指定セクションへ複数のキー情報を追加する。

        Parameters:
            section (str): 追加対象のセクション名
            items (Dict[str, Dict[str, Any]]): 追加するキーと型情報。例:
                {
                    'key1': {'type': int, 'inf': 123},
                    'key2': {'type': str, 'inf': 'abc'}
                }

        Raises:
            KeyError: 指定セクションが ini_dict に存在しない場合
            ValueError: アイテムの形式が正しくない場合
        """
        if section not in self.ini_dict:
            raise KeyError(f"Section '{section}' not found in ini_dict.")

        for key, meta in items.items():
            if not isinstance(meta, dict) or 'type' not in meta or 'inf' not in meta:
                raise ValueError(f"Invalid format for key '{key}'. Must include 'type' and 'inf'.")
            self.ini_dict[section][key] = meta  # 正しく ini_dict に追加
            #self.def_dictにkey情報が無い場合、self.def_dict[key]にmetaを代入。
            if key not in self.def_dict:
                self.def_dict[key] = copy.deepcopy(meta)

    def set(self, section: str, key: str, value: IniValue):
        # セクション／キーの存在チェック。self.ini_dictに存在しないセクション,キーの場合エラーとする。
        if section not in self.ini_dict:
            raise IniParserError(f"[SetError] Section '{section}' does not exist.")
        if key not in self.ini_dict[section]:
            raise IniParserError(f"[SetError] Key '{key}' not found in section '{section}'.")

        expected_type = self.ini_dict[section][key]['type']

        # 型チェック：型が一致しないなら例外を投げる
        if not self._is_instance_of_type(value, expected_type):
            raise IniParserError(
                f"[TypeError] Cannot set '{section}.{key}' to {value!r}: "
                f"expected type {expected_type}, got {type(value)}."
            )

        # 値を更新する
        self.ini_dict[section][key]['inf'] = value
        self.config.set(section, key, self._to_string(value))
        if section not in self.parsed_val:  # セクションが無い場合は作成
            self.parsed_val[section] = {}
        self.parsed_val[section][key] = value

    def save(self):
        IniParser.write_inifile(self.ini_path, self.config, self.encoding)

    def sections(self):
        return self.config.sections()

    def has_section(self, section: str) -> bool:
        return self.config.has_section(section)

    def has_option(self, section: str, option: str) -> bool:
        return self.config.has_option(section, option)

    def __getitem__(self, section: str):
        if not self.has_section(section) and section != 'DEFAULT':
            raise KeyError(f"Section '{section}' not found.")
        return self.SectionProxy(self, section)

    @staticmethod
    # 引数valが、None or 型IniValue(カスタム型)であるかをチェックする。
    # IniValue = Union[str, int, float, bool, List[str], List[int], List[float], List[bool]]
    def _is_valid_ini_value(val: Any) -> bool:
        if val is None:
            return True
        for t in IniValueTypes:
            origin = get_origin(t)  #型の元を取得
            args = get_args(t)      #ジェネリックの引数を取得
            if origin is list:      #List[...] 型のとき
                if isinstance(val, list) and all(isinstance(elem, args[0]) for elem in val):
                    return True
            else:
                if isinstance(val, t):  #通常の型(str, intなど)のチェック
                    return True
        return False

    @staticmethod
    def is_valid_ini_value(value) -> bool:
        for valid_type in IniValueTypes:
            if hasattr(valid_type, '__origin__') and valid_type.__origin__ == list:
                # List[...] の型の場合、中の要素もチェック
                if isinstance(value, list):
                    elem_type = valid_type.__args__[0]
                    if all(isinstance(elem, elem_type) for elem in value):
                        return True
            else:
                if isinstance(value, valid_type):
                    return True
        return False

    @staticmethod
    def is_valid_ini_dict(data: object) -> bool:
        if not isinstance(data, dict):
            return False
        for section_key, section_val in data.items():
            if not isinstance(section_key, str):
                return False
            if not isinstance(section_val, dict):
                return False
            for item_key, item_val in section_val.items():
                if not isinstance(item_key, str):
                    return False
                if not isinstance(item_val, dict):
                    return False
                if 'type' not in item_val or 'inf' not in item_val:
                    return False
                if(IniParser._is_valid_ini_value(item_val['inf']) == False):
                    return False
        return True

    @staticmethod
    def can_read(filename: str) -> bool:
        return os.access(filename, os.R_OK)

    @staticmethod
    def can_write(filename: str) -> bool:
        return os.access(filename, os.W_OK)

    @staticmethod
    def read_inifile(filename: str, config: configparser.ConfigParser) -> None:
        if not os.path.isfile(filename):
            IniParser.die_print(f"File not found: {filename}")
        if not IniParser.can_read(filename):
            IniParser.die_print(f"No read permission: {filename}")

        try:
            files_read = config.read(filename)
            if not files_read:
                IniParser.die_print(f"INI file could not be read. file={filename}")
        except configparser.MissingSectionHeaderError as e:
            IniParser.die_print(f"Missing section header in file {filename}: {e}")
        except configparser.ParsingError as e:
            IniParser.die_print(f"Parsing error in file {filename}: {e}")
        except Exception as e:
            IniParser.die_print(f"Unknown error reading file {filename}: {e}")

    @staticmethod
    def write_inifile(filename: str, config: configparser.ConfigParser, encoding: str) -> None:
        try:
            # 1. DEFAULTセクション情報を抽出
            defaults = config.defaults()
            default_items = dict(defaults)  # コピー

            # 2. DEFAULTセクションのキーを config から削除
            for key in list(defaults.keys()):
                config.remove_option('DEFAULT', key)

            # 3. DEFAULTを除いた内容を一時文字列に書き込み
            import io
            temp_io = io.StringIO()
            config.write(temp_io)
            other_sections_content = temp_io.getvalue()
            temp_io.close()

            # 4. ファイルに書き込み（DEFAULTセクションを先頭に書く）
            with open(filename, 'w', encoding=encoding) as f:
                if default_items:
                    f.write("[DEFAULT]\n")
                    for key, val in default_items.items():
                        f.write(f"{key} = {val}\n")
                    f.write("\n")  # セクション区切り改行

                # 5. DEFAULT以外のセクション内容を書き込む
                f.write(other_sections_content)

            # 6. configにDEFAULTセクションの値を戻す
            for key, value in default_items.items():
                config.set('DEFAULT', key, value)

        except Exception as e:
            IniParser.die_print(f"Error writing to file {filename}: {e}")

    ##@fn re_option_check()
    # @brief        ini情報を取得する。指定したsection,keyに対応した情報を取得。
    # @param[in]    str_opt         : option infomation [type str]
    # @retval       opt_re          : result value [type Union[int, re.RegexFlag]]
    @staticmethod
    def re_option_check(str_opt: str) -> Union[int, re.RegexFlag]:
        # 正規表現オプションのマップ(キーは小文字に統一)
        option_map = {
            "re.unicode": re.UNICODE,
            "re.ignorecase": re.IGNORECASE,
            "re.multiline": re.MULTILINE,
            "re.dotall": re.DOTALL,
        }

        res_flag = True
        invalid_tokens = []  #無効なオプションをためておくリスト
        opt_re = 0  # 初期値

        # 変数str_optが空文字列で無い時
        if str_opt.strip():
            # "|"で区切り、小文字に変換、前後の空白削除し、tokensとして取得。
            tokens = [token.strip().lower() for token in str_opt.split("|")]
            for token in tokens:
                if token in option_map:
                    opt_re |= option_map[token]
                else:
                    res_flag = False
                    invalid_tokens.append(token)

        msg = ""
        if not res_flag:
            func_name = sys._getframe().f_code.co_name
            msg = f"Error detect. def {func_name} \nInvalid option: {', '.join(invalid_tokens)}"
            IniParser.die_print(str(msg ))

        return opt_re

    @classmethod
    def set_use_def_val(cls, use_def_val: bool) -> None :
        if not isinstance(use_def_val, bool):
            msg = f"called def {sys._getframe().f_code.co_name}()\n"
            msg += f"Error detect. The type of mode is invalid. type is not bool\n"
            msg += f"use_def_val: {use_def_val}\n"
            msg += f"Current type: {type(use_def_val)}"
            IniParser.die_print(msg)
        cls.use_def_val = use_def_val

    @classmethod
    def get_use_def_val(cls) -> bool :
        return cls.use_def_val

    @classmethod
    def set_fallback_def_val(cls, fallback_def_val: Optional[IniValue] = None) -> None :
        if not IniParser._is_valid_ini_value(fallback_def_val):
            msg = f"called def {sys._getframe().f_code.co_name}()\n"
            msg += f"Error detect. The type of fallback_def_val is invalid. fallback_def_val must be None or IniValue.\n"
            msg += f"fallback_def_val: {fallback_def_val}\n"
            msg += f"Current type: {type(fallback_def_val)}"
            IniParser.die_print(msg)
        cls.fallback_def_val = fallback_def_val

    @classmethod
    def get_fallback_def_val(cls) -> Optional[IniValue] :
        return cls.fallback_def_val

    @classmethod
    def set_die_mode(cls, mode: DieMode) -> None :
        if not isinstance(mode, DieMode) or mode not in DieMode:
            msg = f"called def {sys._getframe().f_code.co_name}()\n"
            msg += f"Error detect. The type of mode is invalid. type is not DieMode"
            IniParser.die_print(msg)
        cls.mode = mode

    @classmethod
    def get_die_mode(cls) -> DieMode :
        return cls.mode

    ##@fn set_debug_mode()
    # @brief        debug_print制御用のdebug levelを設定する。
    # @param[in]    level           : debug level [type int]
    # @retval       None            : 
    @classmethod
    def set_debug_mode(cls, level: int) -> None :
        cls._DEBUG_MODE = int(level)

    ##@fn debug_print()
    # @brief        debug用print文
    # @param[in]    level           : debug level [type int]
    # @retval       None            : 
    @classmethod
    def debug_print(cls, msg: str, level=1, *args, **kwargs):
        """
        level: メッセージの重要度（1=INFO, 2=DEBUG, 3=TRACEなど）
        cls._DEBUG_MODE >= level のときに出力される
        """
        if cls._DEBUG_MODE >= level:
            print(f"[DEBUG{level}] {msg}", *args, file=cls._DEBUG_STREAM, **kwargs)

    @classmethod
    def set_debug_output(cls, stream_type: str = "stdout") -> None:
        """
        デバッグ出力の出力先を設定する。

        Parameters:
            stream_type (str): 'stdout' または 'stderr'
        """
        if stream_type == "stdout":
            cls._DEBUG_STREAM = sys.stdout
        elif stream_type == "stderr":
            cls._DEBUG_STREAM = sys.stderr
        else:
            raise ValueError("stream_type must be 'stdout' or 'stderr'")

    @classmethod
    def set_dieprint_output(cls, stream_type: str = "stdout") -> None:
        """
        die_print()のメッセージ出力先を設定する。

        Parameters:
            stream_type (str): 'stdout' または 'stderr'
        """
        if stream_type == "stdout":
            cls._DIEPRINT_STREAM = sys.stdout
        elif stream_type == "stderr":
            cls._DIEPRINT_STREAM = sys.stderr
        else:
            raise ValueError("stream_type must be 'stdout' or 'stderr'")

    @classmethod
    def die_print(cls, msg: str) -> None:
        if IniParser.mode in (DieMode.nTkInter, DieMode.nTkInterException):
            try:
                import tkinter as tk
                from tkinter import messagebox
                root = tk.Tk()
                root.withdraw()  # メインウィンドウを表示しない
                messagebox.showerror("Error", msg)
                root.destroy()  # 明示的に閉じる
                if IniParser.mode == DieMode.nTkInterException:
                    raise IniParserError(msg)
                else:
                    sys.exit(NG_VAL)
            except Exception as e:
                # 最終手段:printで通知(_DIEPRINT_STREAMを使用)
                print(f"GUIエラー: {e}", file=cls._DIEPRINT_STREAM)
                print(msg, file=cls._DIEPRINT_STREAM)
        elif IniParser.mode == DieMode.nSysExit:
            print(msg, file=cls._DIEPRINT_STREAM)
            sys.exit(NG_VAL)
        elif IniParser.mode == DieMode.nException:
            raise IniParserError(msg)

    class SectionProxy:
        def __init__(self, parser, section):
            self.parser = parser
            self.section = section

        def __getitem__(self, key):
            try:
                return self.parser.ini_dict[self.section][key]['inf']
            except KeyError:
                raise KeyError(f"Key '{key}' not found in section '{self.section}'.")

        _sentinel = object()  # 特別なダミーオブジェクト

        ##@fn get()
        # @brief        ini情報を取得する。指定したsection,keyに対応した情報を取得。
        # @param[in]    key             : key name [type str]
        # @param[in]    fallback        : fallback value [type _sentinel]
        # @retval                       : result value [type Any]
        def get(self, key, fallback=_sentinel):
            return self.parser._get_value(self.section, key, fallback)

        def items(self):
            try:
                ini_section = self.parser.ini_dict.get(self.section, {})  # ini_dict の section データ
                config_section = self.parser.config[self.section]         # config の section データ（DEFAULT 継承あり）

                # DEFAULT セクションのキーを除くために、明示的に DEFAULT のキーを取得
                default_keys = self.parser.config['DEFAULT'].keys() if 'DEFAULT' in self.parser.config else []

                seen_keys = set()

                # まず ini_dict にある key を優先して返却（value['inf']）
                for key, val in ini_section.items():
                    seen_keys.add(key)
                    yield (key, val['inf'])  # #修正

                # 次に config にある key のうち、DEFAULT に由来しない＆ini_dict にもない key を返却
                for key in config_section.keys():
                    if key not in seen_keys and key not in default_keys:
                        seen_keys.add(key)
                        yield (key, config_section[key])  # #修正

            except KeyError:
                return iter([])  # セクションが存在しない場合は空のイテレータを返す

        def keys(self):
            try:
                ini_section = self.parser.ini_dict.get(self.section, {})
                config_section = self.parser.config[self.section]

                # DEFAULT セクションのキーを取得（存在しない場合は空）
                default_keys = self.parser.config['DEFAULT'].keys() if 'DEFAULT' in self.parser.config else []

                # ini_dictのキーを優先
                seen_keys = set(ini_section.keys())

                # config のキーのうち、DEFAULT から継承されていないものを追加
                for key in config_section.keys():
                    if key not in seen_keys and key not in default_keys:
                        seen_keys.add(key)

                return seen_keys
            except KeyError:
                return []
