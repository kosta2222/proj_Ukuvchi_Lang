(   Istore_name,  # 0
    Iload_const,  # 1
    Iadd,  # 2
    Imult,  # 3
    Idiv,  # 4
    Isub,  # 5
    Inop,  # 6
    # Irem,  # 7
    # Ipow,  # 8
    # BR,  # 9
    # BRT,  # 10
    # BRF,  # 11
    # ICONST,  # 12
    # LOAD,  # 13
    # GLOAD,  # 14
    Istop, #7
    Iload_name, # 8
    Iloadfield, # 9
    Iprint, # 10
    Iinvokenative,# 11
    Ibuild_list, # 12
    Ioaload, # 13 load object (as item in array) on stack (to print it ex)
    Ioastore, # 14
    Imake_function, # 15
    Ireturn_value, # 16
    Icall_function, # 17
    Iimport_module_bname #18 
    )=range(19)

# HAVE_ARGUMENT=0 # up to this bytecode, opcodes have argument 
WE_LOAD_CONSTS=1
WE_LOAD_NAME=8
WE_LOAD_NAME2=9
WE_LOAD_NAME3=11
WE_STORE_NAME=0
