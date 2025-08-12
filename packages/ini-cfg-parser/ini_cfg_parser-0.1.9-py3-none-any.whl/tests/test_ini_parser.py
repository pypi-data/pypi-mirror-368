# tests/test_ini_parser.py

import os
import re
import sys
import stat
import textwrap
import tempfile
import configparser
import ini_cfg_parser as ini
from typing import List

OK_VAL = 0
NG_VAL = 1

try:
    import pytest
except ImportError as e:
    msg = f"The 'ini_parser' module is required but not installed.\n"
    msg += f"You can install it with: pip install pytest\n"
    msg += f"Details: {e}"
    print(msg)
    raise SystemExit(NG_VAL)

@pytest.fixture
def locked_file(tmp_path):
    f = tmp_path / "locked_file.txt"
    f.write_text("lock test")

    # Windowsでは共有ロックで書き込みモードで開く
    if sys.platform.startswith("win"):
        import msvcrt
        fp = open(f, "r+")
        msvcrt.locking(fp.fileno(), msvcrt.LK_NBLCK, 1)
        yield f, fp
        msvcrt.locking(fp.fileno(), msvcrt.LK_UNLCK, 1)
        fp.close()
    else:
        # Unixはfcntlロックを使う
        import fcntl
        fp = open(f, "r+")
        fcntl.flock(fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield f, fp
        fcntl.flock(fp.fileno(), fcntl.LOCK_UN)
        fp.close()

def test_set_debug_output_stdout(capsys):
    ini.IniParser.set_debug_mode(1)
    ini.IniParser.set_debug_output("stdout")

    ini.IniParser.debug_print("hello world", level=1)
    captured = capsys.readouterr()  # 出力をキャプチャ
    assert "[DEBUG1] hello world" in captured.out  # stdoutにあるかチェック
    assert captured.err == ""  # stderrは空のはず

def test_set_debug_output_stderr(capsys):
    ini.IniParser.set_debug_mode(1)
    ini.IniParser.set_debug_output("stderr")

    ini.IniParser.debug_print("hello world", level=1)

    captured = capsys.readouterr()
    assert "[DEBUG1] hello world" in captured.err
    assert captured.out == ""

def get_ini_dict_val() -> ini.IniDict:
    '''
    ini fileのsection="DEFAULT"に設定したい情報をdict形式で設定
    '''
    return {
        'Callback': {
            'backup': {'type': bool, 'inf': False},
            'zip': {'type': bool, 'inf': False},
            'repall': {'type': bool, 'inf': False},
            'original': {'type': bool, 'inf': False},
            'ignorecase': {'type': bool, 'inf': False},
            'multiline': {'type': bool, 'inf': False},
            'dotall': {'type': bool, 'inf': False},
            'fullmatch': {'type': bool, 'inf': False},
            'notregex': {'type': bool, 'inf': False},
            'lst_int': {'type': List[int], 'inf': [999]},
            'lst_float': {'type': List[float], 'inf': [3.14, 1.23]},
            'lst_bool': {'type': List[bool], 'inf': [False, True]},
            'ext': {'type': List[str], 'inf': ['.txt', '.py' , '.pl', '.vhd', '.c']},
            'resultdir': {'type': str, 'inf': 'Result'},
            'in_file': {'type': str, 'inf': 'hoge.bat'},
            'level': {'type': int, 'inf': 100},
            'pi': {'type': float, 'inf': 3.14},
        }
    }

def get_ini_dict_val2() -> ini.IniDict:
    '''
    ini fileのsection="DEFAULT"に設定したい情報をdict形式で設定
    '''
    return {
        'sandbox': {
            'user': {'type': str, 'inf': 'root'},
            'password': {'type': str, 'inf': 'hogeroot'},
            'host': {'type': str, 'inf': '192.168.0.23'},
        },
        'user1': {
            'user': {'type': str, 'inf': 'user1'},
            'password': {'type': str, 'inf': 'hogepass1'},
            'host': {'type': str, 'inf': '172.31.2.190'},
        },
        'user2': {
            'user': {'type': str, 'inf': 'user2'},
            'password': {'type': str, 'inf': 'hogepass2'},
            'host': {'type': str, 'inf': '172.31.2.191'},
        },
        'user3': {
            'user': {'type': str, 'inf': 'user3'},
            'password': {'type': str, 'inf': 'hogepass3'},
            'host': {'type': str, 'inf': '172.31.2.193'},
        },
        'user4': {
        },
    }


def get_ini_dict_val3() -> ini.IniDict:
    '''
    ini fileのsection="DEFAULT"に設定したい情報をdict形式で設定
    '''
    return {
        'Callback': {
            'in_file': {'type': str, 'inf': 'hoge.bat'},
        },
        'user1': {
            'user': {'type': str, 'inf': 'user1'},
            'password': {'type': str, 'inf': 'hogepass1'},
            'host': {'type': str, 'inf': '172.31.2.190'},
        },
    }
def test_read_set_write_config_value():
    ini_file = "config.ini"
    if os.path.isfile(ini_file):
        os.remove(ini_file)

    encoding = "utf8"
    default_ini = get_ini_dict_val()
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    try:
        ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    except ini.IniParserError as e:
        print(e)
        sys.exit(1)

    # ファイルの存在を確認
    assert os.path.exists(ini_file)

    # テスト実行
    assert ini_parser.get('Callback', 'backup') == False
    assert ini_parser.get('Callback', 'zip') == False
    assert ini_parser.get('Callback', 'backup') == False
    assert ini_parser.get('Callback', 'zip') == False
    assert ini_parser.get('Callback', 'repall') == False
    assert ini_parser.get('Callback', 'original') == False
    assert ini_parser.get('Callback', 'ignorecase') == False
    assert ini_parser.get('Callback', 'multiline') == False
    assert ini_parser.get('Callback', 'dotall') == False
    assert ini_parser.get('Callback', 'fullmatch') == False
    assert ini_parser.get('Callback', 'notregex') == False
    assert ini_parser.get('Callback', 'lst_int') == [999]
    assert ini_parser.get('Callback', 'lst_float') == [3.14, 1.23]
    assert ini_parser.get('Callback', 'lst_bool') == [False, True]
    assert ini_parser.get('Callback', 'ext') == ['.txt', '.py' , '.pl', '.vhd', '.c']
    assert ini_parser.get('Callback', 'resultdir') == 'Result'
    assert ini_parser.get('Callback', 'in_file') == 'hoge.bat'
    assert ini_parser['Callback'].get('in_file') == 'hoge.bat'

    # 値を設定
    ini_parser.set('Callback', 'ext', ['.c', '.cpp' , '.c', '.h'])
    assert ini_parser.get('Callback', 'ext') == ['.c', '.cpp' , '.c', '.h']
    ini_parser.save()
    #ini.IniParser.set_debug_mode(2)

def test_missing_key():
    ini_file = "config.ini"
    encoding = "utf8"
    default_ini = get_ini_dict_val()
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    try:
        ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    except ini.IniParserError as e:
        print(e)

    assert ini_parser.get('Callback', 'ext') == ['.c', '.cpp' , '.c', '.h']

    with pytest.raises(ini.IniParserError):
        # 値を設定
        ini_parser.set('Callback', 'ext', False)

def test_missing_key2():
    ini_file = "config2.ini"
    encoding = "utf8"
    if os.path.isfile(ini_file):
        os.remove(ini_file)

    fixed_text = textwrap.dedent("""\
        [DEFAULT]
        user = default
        password = defpasswd
        host = 172.31.2.99
        [sandbox]
        user = root
        password = hogeroot
        host = 192.168.0.23
        [user1]
        user = user1
        password = hogepass1
        host = 172.31.2.190
        [user2]
        user = user2
        password = hogepass2
        host = 172.31.2.191
        [user3]
        user = user3
        password = hogepass3
        host = 172.31.2.193
        [user4]
    """)
    with open(ini_file, 'w', encoding=encoding) as f:
        f.write(fixed_text)
    default_ini = get_ini_dict_val2()
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    try:
        ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    except ini.IniParserError as e:
        print(e)
        sys.exit(1)

    # ファイルの存在を確認
    assert os.path.exists(ini_file)

    # テスト実行
    assert ini_parser.get('sandbox', 'user') == 'root'
    assert ini_parser.get('sandbox', 'password') == 'hogeroot'
    assert ini_parser.get('sandbox', 'host') == '192.168.0.23'

    assert ini_parser.get('user1', 'user') == 'user1'
    assert ini_parser.get('user1', 'password') == 'hogepass1'
    assert ini_parser.get('user1', 'host') == '172.31.2.190'

    assert ini_parser.get('user2', 'user') == 'user2'
    assert ini_parser.get('user2', 'password') == 'hogepass2'
    assert ini_parser.get('user2', 'host') == '172.31.2.191'

    assert ini_parser.get('user3', 'user') == 'user3'
    assert ini_parser.get('user3', 'password') == 'hogepass3'
    assert ini_parser.get('user3', 'host') == '172.31.2.193'

    assert ini_parser.get('user4', 'user') == 'default'
    assert ini_parser.get('user4', 'password') == 'defpasswd'
    assert ini_parser.get('user4', 'host') == '172.31.2.99'

def test_no_val():
    ini_file = "config2.ini"
    encoding = "utf8"
    if os.path.isfile(ini_file):
       os.remove(ini_file)
    default_ini = get_ini_dict_val2()
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    try:
        ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    except ini.IniParserError as e:
        print(e)
        sys.exit(1)

    assert ini_parser.get('user5', 'user_dbg', fallback="user5") == 'user5'
    assert ini_parser.get('user5', 'password_dbg', fallback="xyz12345") == 'xyz12345'
    assert ini_parser.get('user5', 'host_dbg', fallback="172.31.2.123") == '172.31.2.123'

    ini.IniParser.use_def_val = True
    ini.IniParser.fallback_def_val = "user6"
    assert ini_parser.get('user6', 'user_deb') == 'user6'
    ini.IniParser.fallback_def_val = "abc123456"
    assert ini_parser.get('user6', 'password_deb') == 'abc123456'
    ini.IniParser.fallback_def_val = "172.31.2.111"
    assert ini_parser.get('user6', 'host_deb') == '172.31.2.111'

def test_type_err():
    ini_file = "config.ini"
    encoding = "utf8"
    if os.path.isfile(ini_file):
        os.remove(ini_file)
    default_ini = get_ini_dict_val()
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    try:
        ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    except ini.IniParserError as e:
        print(e)
        sys.exit(1)

    with pytest.raises(ini.IniParserError):
        ini_parser.set('Callback', 'lst_int', [18,1, 24.3])

    with pytest.raises(ini.IniParserError):
        ini_parser.set('Callback', 'lst_float', ['kobe', 'yokohama', 'hakodate'])

    with pytest.raises(ini.IniParserError):
        ini_parser.set('Callback', 'lst_bool', [777, 999])

    with pytest.raises(ini.IniParserError):
        ini_parser.set('Callback', 'ext', [False, True])


def test_die_mode():
    assert ini.IniParser.get_die_mode() == ini.DieMode.nException
    ini.IniParser.set_die_mode(ini.DieMode.nSysExit)
    assert ini.IniParser.get_die_mode() == ini.DieMode.nSysExit
    ini.IniParser.set_die_mode(ini.DieMode.nTkInter)
    assert ini.IniParser.get_die_mode() == ini.DieMode.nTkInter
    ini.IniParser.set_die_mode(ini.DieMode.nTkInterException)
    assert ini.IniParser.get_die_mode() == ini.DieMode.nTkInterException
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    assert ini.IniParser.get_die_mode() == ini.DieMode.nException

def test_invalid_get_ini_dict_val():
    ini_file = "config.ini"
    encoding = "utf8"
    if os.path.isfile(ini_file):
        os.remove(ini_file)
    default_ini = {
        'config': {
            'backup': {'type': dict, 'inf': {'user': 'user1', 'password': 'hogehoge'},},
        }
    }
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    with pytest.raises(ini.IniParserError):
       ini_parser = ini.IniParser(ini_file, default_ini, encoding)

    default_ini = {
        'config': {
            'backup': {'type': str, 'inf': False},
        }
    }
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    with pytest.raises(ini.IniParserError):
       ini_parser = ini.IniParser(ini_file, default_ini, encoding)

    default_ini = {
        'config': {
            'backup': {'type': List[str], 'inf': [1, 2, 3]},
        }
    }
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    with pytest.raises(ini.IniParserError):
       ini_parser = ini.IniParser(ini_file, default_ini, encoding)

    default_ini = {
        'config': {
            'backup': {'type': bool},
        }
    }
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    with pytest.raises(ini.IniParserError):
       ini_parser = ini.IniParser(ini_file, default_ini, encoding)

    default_ini = {
        'config': {
            'backup': {'inf': False},
        }
    }
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    with pytest.raises(ini.IniParserError):
       ini_parser = ini.IniParser(ini_file, default_ini, encoding)

def test_invalid_fallback_def_val():
    ini.IniParser.fallback_def_val = [10,"100"]
    ini_file = "config.ini"
    encoding = "utf8"
    if os.path.isfile(ini_file):
        os.remove(ini_file)
    default_ini = get_ini_dict_val()
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    with pytest.raises(ini.IniParserError):
       ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    #元の設定に戻す
    ini.IniParser.fallback_def_val = None

def test_invalid_use_def_val():
    ini.IniParser.use_def_val = "hogehoge"
    ini_file = "config.ini"
    encoding = "utf8"
    if os.path.isfile(ini_file):
        os.remove(ini_file)
    default_ini = get_ini_dict_val()
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    with pytest.raises(ini.IniParserError):
       ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    #元の設定に戻す
    ini.IniParser.use_def_val = False

def test_invalid_ini_file():
    ini_file = ["config.ini", "config2.ini"]
    encoding = "utf8"
    default_ini = get_ini_dict_val()
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    with pytest.raises(ini.IniParserError):
       ini_parser = ini.IniParser(ini_file, default_ini, encoding)

def test_invalid_encoding():
    ini_file = "config.ini"
    encoding = ["utf8"]
    default_ini = get_ini_dict_val()
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    with pytest.raises(ini.IniParserError):
       ini_parser = ini.IniParser(ini_file, default_ini, encoding)

def test_func_has():
    ini_file = "config.ini"
    encoding = "utf8"
    default_ini = get_ini_dict_val()
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    try:
        ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    except ini.IniParserError as e:
        print(e)
        sys.exit(1)
    assert ini_parser.sections() == ['Callback']
    assert ini_parser.has_section('Callback') == True
    assert ini_parser.has_section('hogehoge') == False
    assert ini_parser.has_option('Callback', 'backup') == True
    assert ini_parser.has_option('Callback', 'hogehoge') == False
    
def test_missing_inifile(locked_file):
    ini_file = "config.ini"
    if os.path.isfile(ini_file):
        os.remove(ini_file)

    encoding = "utf8"
    config = configparser.ConfigParser()
    with pytest.raises(ini.IniParserError):
        ini.IniParser.read_inifile(ini_file, config)

    ini_file = "config.ini"
    encoding = "utf8"
    default_ini = get_ini_dict_val()
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    try:
        ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    except ini.IniParserError as e:
        print(e)
        sys.exit(1)

    # get st_mode
    original_mode = os.stat(ini_file).st_mode
    assert (original_mode & stat.S_IRUSR)
    assert ini.IniParser.can_write(ini_file) == True

    f, fp = locked_file
    with pytest.raises(ini.IniParserError):
        ini.IniParser.read_inifile(f, config)

    config.add_section("settings")
    config.set('settings', 'username', 'user123')
    os.chmod(ini_file, stat.S_IRUSR)	# can't write
    assert ini.IniParser.can_write(ini_file) == False
    with pytest.raises(ini.IniParserError):
        ini.IniParser.write_inifile(ini_file, config, encoding)
    # revert
    os.chmod(ini_file, original_mode)	

def test_opt_replace():
    ini_file = "config.ini"
    if os.path.isfile(ini_file):
        os.remove(ini_file)
    encoding = "utf8"
    default_ini = {
        'opt_replace': {
            'str_search': {'type': str, 'inf': 'search word'},
            'str_replace': {'type': str, 'inf': 'replace word'},
            'opt_re': {'type': str, 'inf': 're.UNICODE | re.IGNORECASE | re.MULTILINE | re.DOTALL'},
        }
    }

    ini.IniParser.set_die_mode(ini.DieMode.nException)
    try:
        ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    except ini.IniParserError as e:
        print(e)
        sys.exit(1)

    opt_re = None
    section = 'opt_replace'
    key = 'opt_re'
    str_val = ini_parser.get(section, key)
    assert str_val == 're.UNICODE | re.IGNORECASE | re.MULTILINE | re.DOTALL'
    try:
        opt_re = ini.IniParser.re_option_check(str_val)
    except ini.IniParserError as e:
        print(e)
    assert opt_re == re.IGNORECASE|re.UNICODE|re.MULTILINE|re.DOTALL

    opt_re = None
    key = 'str_replace'
    str_val = ini_parser.get(section, key)
    assert str_val == 'replace word'
    with pytest.raises(ini.IniParserError):
        opt_re = ini.IniParser.re_option_check(str_val)

def test_fallback_def_val_use_def_val():
    ini_file = "config.ini"
    if os.path.isfile(ini_file):
        os.remove(ini_file)

    encoding = "utf8"
    default_ini = {
        'config': {
            'backup': {'type': bool, 'inf': False},
        }
    }
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    try:
        ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    except ini.IniParserError as e:
        print(e)
        sys.exit(1)
    section = 'config'
    key = 'backup'
    inf = ini_parser.get(section, key)
    assert inf == False
    
    # when ini.IniParser.set_use_def_val(False) and 
    # when no fallback is specified.
    section = 'config'
    key = 'lst_bool'
    inf = ini_parser.get(section, key)
    assert inf == None

    # when ini.IniParser.set_use_def_val(True) and 
    # when fallback_def_val is set
    ini.IniParser.set_use_def_val(True)
    lst_bool = None
    ini.IniParser.set_fallback_def_val([False, True])
    assert ini.IniParser.get_use_def_val() == True
    assert ini.IniParser.get_fallback_def_val() == [False, True]
    lst_bool = ini_parser.get(section, key)
    assert lst_bool == [False, True]

def test_def_items():
    ini_file = "config.ini"
    if os.path.isfile(ini_file):
        os.remove(ini_file)

    encoding = "utf8"
    default_ini = {
        'Callback': {
            'backup': {'type': bool, 'inf': False},
            'zip': {'type': bool, 'inf': False},
            'repall': {'type': bool, 'inf': False},
            'original': {'type': bool, 'inf': False},
            'ignorecase': {'type': bool, 'inf': False},
            'multiline': {'type': bool, 'inf': False},
            'dotall': {'type': bool, 'inf': False},
            'fullmatch': {'type': bool, 'inf': False},
            'notregex': {'type': bool, 'inf': False},
            'lst_int': {'type': List[int], 'inf': [999]},
            'lst_float': {'type': List[float], 'inf': [3.14, 1.23]},
            'lst_bool': {'type': List[bool], 'inf': [False, True]},
            'ext': {'type': List[str], 'inf': ['.txt', '.py' , '.pl', '.vhd', '.c']},
            'resultdir': {'type': str, 'inf': 'Result'},
            'in_file': {'type': str, 'inf': 'hoge.bat'},
            'level': {'type': int, 'inf': 100},
            'pi': {'type': float, 'inf': 3.14},
        },
        'user1': {
            'user': {'type': str, 'inf': 'user1'},
            'password': {'type': str, 'inf': 'hogepass1'},
            'host': {'type': str, 'inf': '172.31.2.190'},
        },
    }

    ini.IniParser.set_die_mode(ini.DieMode.nException)
    try:
        ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    except ini.IniParserError as e:
        print(e)
        sys.exit(1)
    expected = {
        'Callback': {
            'backup': False,
            'zip': False,
            'repall': False,
            'original': False,
            'ignorecase': False,
            'multiline': False,
            'dotall': False,
            'fullmatch': False,
            'notregex': False,
            'lst_int': [999],
            'lst_float': [3.14, 1.23],
            'lst_bool': [False, True],
            'ext': ['.txt', '.py', '.pl', '.vhd', '.c'],
            'resultdir': 'Result',
            'in_file': 'hoge.bat',
            'level': 100,
            'pi': 3.14,
        },
        'user1': {
            'user': 'user1',
            'password': 'hogepass1',
            'host': '172.31.2.190',
        },
    }

    # チェック対象のセクションとキー/値を1つの辞書に格納
    actual = {}
    for section_name in ini_parser.sections():
        actual[section_name] = dict(ini_parser[section_name].items())
    # 値も含めて完全一致しているか確認
    assert actual == expected, f"Mismatch in ini content.\nExpected:\n{expected}\nActual:\n{actual}"

    actual = {}
    for section_name,items in ini_parser.items():
        actual[section_name] = items
    # 値も含めて完全一致しているか確認
    assert actual == expected, f"Mismatch in ini content.\nExpected:\n{expected}\nActual:\n{actual}"


def test_def_keys():
    ini_file = "config.ini"
    if os.path.isfile(ini_file):
        os.remove(ini_file)

    encoding = "utf8"
    default_ini = {
        'Callback': {
            'backup': {'type': bool, 'inf': False},
            'zip': {'type': bool, 'inf': False},
            'repall': {'type': bool, 'inf': False},
            'original': {'type': bool, 'inf': False},
            'ignorecase': {'type': bool, 'inf': False},
            'multiline': {'type': bool, 'inf': False},
            'dotall': {'type': bool, 'inf': False},
            'fullmatch': {'type': bool, 'inf': False},
            'notregex': {'type': bool, 'inf': False},
            'lst_int': {'type': List[int], 'inf': [999]},
            'lst_float': {'type': List[float], 'inf': [3.14, 1.23]},
            'lst_bool': {'type': List[bool], 'inf': [False, True]},
            'ext': {'type': List[str], 'inf': ['.txt', '.py', '.pl', '.vhd', '.c']},
            'resultdir': {'type': str, 'inf': 'Result'},
            'in_file': {'type': str, 'inf': 'hoge.bat'},
            'level': {'type': int, 'inf': 100},
            'pi': {'type': float, 'inf': 3.14},
        },
        'user1': {
            'user': {'type': str, 'inf': 'user1'},
            'password': {'type': str, 'inf': 'hogepass1'},
            'host': {'type': str, 'inf': '172.31.2.190'},
        },
    }

    ini.IniParser.set_die_mode(ini.DieMode.nException)
    try:
        ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    except ini.IniParserError as e:
        print(e)
        sys.exit(1)

    expected = {
        'Callback': sorted([
            'backup', 'zip', 'repall', 'original', 'ignorecase', 'multiline',
            'dotall', 'fullmatch', 'notregex', 'lst_int', 'lst_float', 'lst_bool',
            'ext', 'resultdir', 'in_file', 'level', 'pi'
        ]),
        'user1': sorted(['user', 'password', 'host']),
    }

    actual = {}
    for section_name in ini_parser.sections():
        actual[section_name] = sorted(list(ini_parser[section_name].keys()))

    assert actual == expected, f"Mismatch in section keys.\nExpected:\n{expected}\nActual:\n{actual}"

def test_nosection_set():
    ini_file = "config2.ini"
    encoding = "utf8"
    if os.path.isfile(ini_file):
        os.remove(ini_file)
    assert not os.path.exists(ini_file)

    default_ini = get_ini_dict_val3()
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    try:
        ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    except ini.IniParserError as e:
        print(e)
        sys.exit(1)

    # when no section
    with pytest.raises(ini.IniParserError):
        ini_parser.set('user4', 'user','user_4')

    ini_parser.add_section("user4")  # 先にセクションを追加
    # ini_dictに追加設定
    ini_parser.add_ini_dict_keys("user4", {
        "user": {"type": str, "inf": "user_4"},
        "password": {"type": str, "inf": "pass1234"},
        "host": {"type": str, "inf": "172.31.2.199"}
    })

    # 対象のkey情報が無いため、セクションDEFAULTに定義されている情報を取得。
    assert ini_parser.get('user4', 'user') == 'user1'
    assert ini_parser.get('user4', 'password') == 'hogepass1'
    assert ini_parser.get('user4', 'host') == '172.31.2.190'

    ini_parser.set('user4', 'user','user_4x')
    ini_parser.set('user4', 'password', 'pass1234x')
    ini_parser.set('user4', 'host', '172.31.2.99')

    assert ini_parser.get('user4', 'user') == 'user_4x'
    assert ini_parser.get('user4', 'password') == 'pass1234x'
    assert ini_parser.get('user4', 'host') == '172.31.2.99'

    ini_parser.set('user1', 'user','user-1x')
    ini_parser.set('user1', 'password', 'pass1234-x')
    ini_parser.set('user1', 'host', '172.31.102.99')
    # テスト実行
    assert ini_parser.get('user1', 'user') == 'user-1x'
    assert ini_parser.get('user1', 'password') == 'pass1234-x'
    assert ini_parser.get('user1', 'host') == '172.31.102.99'

    # 対象のkey情報が無いため、セクションDEFAULTに定義されている情報を取得。
    assert ini_parser.get('user2', 'user') == 'user1'
    assert ini_parser.get('user2', 'password') == 'hogepass1'
    assert ini_parser.get('user2', 'host') == '172.31.2.190'

    assert ini_parser.get('user3', 'user') == 'user1'
    assert ini_parser.get('user3', 'password') == 'hogepass1'
    assert ini_parser.get('user3', 'host') == '172.31.2.190'

    assert ini_parser.get('sandbox', 'user') == 'user1'
    assert ini_parser.get('sandbox', 'password') == 'hogepass1'
    assert ini_parser.get('sandbox', 'host') == '172.31.2.190'

def test_no_inidict():
    ini_file = "config2.ini"
    encoding = "utf8"
    if os.path.isfile(ini_file):
        os.remove(ini_file)
    assert not os.path.exists(ini_file)

    fixed_text = textwrap.dedent("""\
        [user2]
        user = user2
        password = hogepass2
        host = 172.31.2.191
        port = 40
    """)
    with open(ini_file, 'w', encoding=encoding) as f:
        f.write(fixed_text)
    default_ini = get_ini_dict_val3()
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    try:
        ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    except ini.IniParserError as e:
        print(e)
        sys.exit(1)

    # ini_dictに情報なし。iniファイルに情報ありの場合
    assert ini_parser.get('user2', 'user') == 'user2'
    assert ini_parser.get('user2', 'password') == 'hogepass2'
    assert ini_parser.get('user2', 'host') == '172.31.2.191'
    assert ini_parser.get('user2', 'port') == '40'

def test_is_valid_ini_dict():
    default_ini = get_ini_dict_val()
    assert ini.IniParser.is_valid_ini_dict(default_ini) == True
    default_ini = get_ini_dict_val2()
    assert ini.IniParser.is_valid_ini_dict(default_ini) == True
    default_ini = {
        'Callback': {
            'backup': False,
        }
    }
    assert ini.IniParser.is_valid_ini_dict(default_ini) == False
    default_ini = "hogehoge"
    assert ini.IniParser.is_valid_ini_dict(default_ini) == False
    default_ini = {
        'Callback': {
            1: False,
            2: True,
        }
    }
    assert ini.IniParser.is_valid_ini_dict(default_ini) == False
    default_ini = {
        100: {
            'backup': False,
        }
    }
    assert ini.IniParser.is_valid_ini_dict(default_ini) == False
    default_ini = {
        'Callback': 'backup',
    }
    assert ini.IniParser.is_valid_ini_dict(default_ini) == False

def test_is_valid_ini_value():
    assert ini.IniParser.is_valid_ini_value('string') == True
    assert ini.IniParser.is_valid_ini_value([1, 2, 3]) == True
    assert ini.IniParser.is_valid_ini_value([1.1, 2.1, 3.1]) == True
    assert ini.IniParser.is_valid_ini_value([True, False]) == True
    assert ini.IniParser.is_valid_ini_value(['hello', 'world']) == True
    default_ini = get_ini_dict_val()
    assert ini.IniParser.is_valid_ini_value(default_ini) == False

def test_set_use_def_val():
    ini.IniParser.set_use_def_val(True)
    with pytest.raises(ini.IniParserError):
        ini.IniParser.set_use_def_val('hogehoge')

def test_set_fallback_def_val():
    ini.IniParser.set_fallback_def_val('string')
    ini.IniParser.set_fallback_def_val([1, 2, 3])
    ini.IniParser.set_fallback_def_val([1.1, 2.1, 3.1])
    ini.IniParser.set_fallback_def_val([True, False])
    ini.IniParser.set_fallback_def_val(['hello', 'world'])
    default_ini = get_ini_dict_val()
    with pytest.raises(ini.IniParserError):
        ini.IniParser.set_fallback_def_val(default_ini)

def test_die_print(capsys):
    ini.IniParser.set_dieprint_output("stdout")
    ini.IniParser.set_die_mode(ini.DieMode.nSysExit)
    msg = "hello world"
    with pytest.raises(SystemExit) as exc_info:
        ini.IniParser.die_print(msg)

    # sys.exit(1) が呼ばれたことを確認
    assert exc_info.type == SystemExit
    assert exc_info.value.code == 1

    # printされた出力を確認
    captured = capsys.readouterr()
    assert msg in captured.out

    #-----
    ini.IniParser.set_dieprint_output("stderr")
    ini.IniParser.set_die_mode(ini.DieMode.nSysExit)
    msg = "hello world"
    with pytest.raises(SystemExit) as exc_info:
        ini.IniParser.die_print(msg)

    # sys.exit(1) が呼ばれたことを確認
    assert exc_info.type == SystemExit
    assert exc_info.value.code == 1

    # printされた出力を確認
    captured = capsys.readouterr()
    assert "" == captured.out
    assert msg in captured.err

    #-----
    ini.IniParser.set_dieprint_output("stdout")
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    msg = "hello world"
    with pytest.raises(ini.IniParserError) as exc_info:
        ini.IniParser.die_print(msg)
    assert exc_info.type == ini.IniParserError

    # 例外メッセージに msg が含まれていることを確認
    assert msg in str(exc_info.value)

def test_ini_setting_csvfmt(capsys):
    ini_file = "config.ini"
    encoding = "utf8"
    if os.path.isfile(ini_file):
        os.remove(ini_file)
    assert not os.path.exists(ini_file)

    fixed_text = textwrap.dedent("""\
        [config]
        lst_inf = "abc,def","hello, world","My name is Yamada."
        lst_inf2 = "1,234","5,678","This is, indeed, a test."
        lst_int = "1" ,  2 ,  4, 8, 16, 32, 64 , "128"
        lst_float = 1.1 , 2.1 , 4.0 , 8.3 , 16.1 , 32.1 , 64.1 , 128.1
        lst_bool = True, False, yes, no, 1, 0
        ext = .c , .cpp, .h
        ext2 = ".txt", ".py", ".pl"
    """)
    with open(ini_file, 'w', encoding=encoding) as f:
        f.write(fixed_text)
    default_ini = {
            'config': {
            'lst_int': {'type': List[int], 'inf': [999]},
            'lst_float': {'type': List[float], 'inf': [3.14, 1.23]},
            'lst_bool': {'type': List[bool], 'inf': [False, True]},
            'ext': {'type': List[str], 'inf': ['.txt', '.py' , '.pl', '.vhd', '.c']},
            'ext': {'type': List[str], 'inf': ['.txt']},
            'ext2': {'type': List[str], 'inf': ['.vhd']},
            'lst_inf': {'type': List[str], 'inf': ['hello world']},
            'lst_inf2': {'type': List[str], 'inf': ['hogehoge']},
        },
    }
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    try:
        ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    except ini.IniParserError as e:
        print(e)
        sys.exit(1)
    section = 'config'
    key = 'ext'
    assert [".c", ".cpp", ".h"] == ini_parser.get(section, key)
    key = 'ext2'
    assert [".txt", ".py", ".pl"] == ini_parser.get(section, key)
    key = 'lst_inf'
    assert ["abc,def", "hello, world", "My name is Yamada."] == ini_parser.get(section, key)
    key = 'lst_inf2'
    assert ["1,234", "5,678", "This is, indeed, a test."] == ini_parser.get(section, key)
    key = 'lst_int'
    assert [1, 2, 4, 8, 16, 32, 64 ,128] == ini_parser.get(section, key)
    key = 'lst_float'
    assert [1.1, 2.1, 4.0, 8.3, 16.1, 32.1, 64.1 ,128.1] == ini_parser.get(section, key)
    key = 'lst_bool'
    assert [True, False, True, False, True, False] == ini_parser.get(section, key)

def test_parsed_val(capsys):
    ini_file = "config.ini"
    if os.path.isfile(ini_file):
        os.remove(ini_file)

    encoding = "utf8"
    default_ini = {
        'Callback': {
            'backup': {'type': bool, 'inf': False},
            'zip': {'type': bool, 'inf': False},
            'repall': {'type': bool, 'inf': False},
            'original': {'type': bool, 'inf': False},
            'ignorecase': {'type': bool, 'inf': False},
            'multiline': {'type': bool, 'inf': False},
            'dotall': {'type': bool, 'inf': False},
            'fullmatch': {'type': bool, 'inf': False},
            'notregex': {'type': bool, 'inf': False},
            'lst_int': {'type': List[int], 'inf': [999]},
            'lst_float': {'type': List[float], 'inf': [3.14, 1.23]},
            'lst_bool': {'type': List[bool], 'inf': [False, True]},
            'ext': {'type': List[str], 'inf': ['.txt', '.py' , '.pl', '.vhd', '.c']},
            'resultdir': {'type': str, 'inf': 'Result'},
            'in_file': {'type': str, 'inf': 'hoge.bat'},
            'level': {'type': int, 'inf': 100},
            'pi': {'type': float, 'inf': 3.14},
        },
        'user1': {
            'user': {'type': str, 'inf': 'user1'},
            'password': {'type': str, 'inf': 'hogepass1'},
            'host': {'type': str, 'inf': '172.31.2.190'},
        },
    }
    ini.IniParser.set_die_mode(ini.DieMode.nException)
    try:
        ini_parser = ini.IniParser(ini_file, default_ini, encoding)
    except ini.IniParserError as e:
        print(e)
        sys.exit(1)
    expected = {
        'Callback': {
            'backup': False,
            'zip': False,
            'repall': False,
            'original': False,
            'ignorecase': False,
            'multiline': False,
            'dotall': False,
            'fullmatch': False,
            'notregex': False,
            'lst_int': [999],
            'lst_float': [3.14, 1.23],
            'lst_bool': [False, True],
            'ext': ['.txt', '.py', '.pl', '.vhd', '.c'],
            'resultdir': 'Result',
            'in_file': 'hoge.bat',
            'level': 100,
            'pi': 3.14,
        },
        'user1': {
            'user': 'user1',
            'password': 'hogepass1',
            'host': '172.31.2.190',
        },
    }

    assert ini_parser.parsed_val == expected
