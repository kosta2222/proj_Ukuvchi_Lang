Проект язык программирования Ukuvchi(узб.-ученик)
================================================

***08/12/2018***
Компилятор написан на Python3(тестировался на Python3.6.3)
исходный текст идет в lisp подобном синтаксисе,идет интерпритация
так называемых s(sybolic) выражений.Нет массивов,строк,структур и т.д.
Язык служит для демонстрационных целей,того как может работать компилятор
и интерпритатор байт-кода(виртуальная машина),котарая написана на С,
как расширение для Python3,библиотека с расширением pyd.

Тесты в папке tests_CompilAndIntpretBc

1. S_compiler.py - транслятор на Py, подгружает C Vm.
2. S_compiler_py - транслятор на Py вместе с Py Vm.

    Как запускать:
    <path>/python.exe S_compiler.py ./tests_CompilAndIntpretBc/code_Arifm.lisp

### Виртуальная машина на C:
[BSD license]
Copyright (c) 2014, Terence Parr
All rights reserved.

[Ученик-картинка](https://github.com/kosta2222/proj_Ukuvchi_Lang/ukuvchi_logo.png)

### Copyright (C) 2018 Muhamedjanov K.K
 
   Permission to use, copy, modify, and/or distribute this software for any
   purpose with or without fee is hereby granted, provided that the above
   copyright notice and this permission notice appear in all copies.
 
   THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
   WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
   MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
   ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
   WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
   ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
   OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 
 