 ($
 (// Пример if c else )  
 (if(< (arif 20) (arif 10))
   ($(set! x (arif 100)) (// Последовательность True ветки)
   (print x))
 ($(set! x (arif 200)) (// Последовательность False ветки)
 (print x)             (// Ожидается 200)))
  )