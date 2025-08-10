from feasytools import ArgChecker

def test_argcheck():
    args = ArgChecker('''--sdji="-dsf -sdf" -d 123 -e " -d 'hello   world'" -sdfsdf -v "-asdb" -g "-ff 'wqsfd  asdf' -sdf " --musd=-sdfi''',['g'])
    assert args.pop_int('d') == 123, "Expected integer value for argument 'd'."
    assert args.pop_str('e') == " -d 'hello   world'", "Expected string value for argument 'e'."
    assert args.pop_str('g') == "-ff 'wqsfd  asdf' -sdf ", "Expected string value for argument 'g'."
    assert args.pop_bool('asdb') == True
    assert args.pop_bool('sdfsdf') == True
    assert args.pop_str('musd') == '-sdfi', "Expected string value for argument 'musd'."
    assert args.pop_str('sdji') == '-dsf -sdf', "Expected string value for argument 'sdji'."

    eh_flag = False
    def eh(x:Exception):
        nonlocal eh_flag
        eh_flag = True
    ArgChecker.ErrorHandler = eh

    try:
        args.pop_int('f')
    except:
        pass
    assert eh_flag, "Expected error handler to be called for missing argument 'f'."