# Мои решения задач с Codewars

В данном репозитории не размещается какой-то целый проект, но тут находятся мои решения некоторых задач с сайта **Codewars**.

# Решения задач

| Название задачи                                    | Сложность | Файл                           | Статус             | Ссылка                                                        |
|----------------------------------------------------|-----------|--------------------------------|--------------------|---------------------------------------------------------------|
| [Esolang Interpreters #4 - Boolfuck Interpreter](#esolang-interpreters-4---boolfuck-interpreter) | 3 kyu     | [Тык](boolfuck_interpreter.py) | Не решена до конца | [Тык](https://www.codewars.com/kata/5861487fdb20cff3ab000030) |
| [Rail Fence Cipher: Encoding and Decoding]         | 3 kyu     | [Тык](rail_fence_cipher.py)    | Решена             | [Тык](https://www.codewars.com/kata/58c5577d61aefcf3ff000081) |
| [Evaluate mathematical expressions]                | 2 kyu     | [Тык](eval_math_expression.py) | Решена             | [Тык](https://www.codewars.com/kata/52a78825cdfc2cfc87000005) |
| [Break the pieces]                                 | 2 kyu     | [Тык](break_the_pieces.py)     | Решена             | [Тык](https://www.codewars.com/kata/527fde8d24b9309d9b000c4e) |

# О каждой задаче

## Esolang Interpreters #4 - Boolfuck Interpreter
В целом код интерпретатора достаточно простой, больше всего сложностей вызвал побитовый ввод данных и морока с порядком байтов.
Программа в целом работает на простых примерах кода на Brainfuck, транслированного в Boolfuck, но с более сложными примерами с циклами возникают проблемы.
Надо закончить отладку.

#### Задача неплоха для 3 kyu, хотя алгоритмически довольно простая

## Rail Fence Cipher: Encoding and Decoding
Довольно интересная задача с интересным шифром для кодирования и декодирования.
Долго пытался придумать схему, которая на основе числа рельс (здесь и далее рельсами я называю горизонтальные строки) определяла бы номер рельсы каждого символа, но в итоге пришёл к решению другим путём.

На основе числа рельс генерирую шаги, которыми определяется расстояние между буквмаи на каждой рельсе.
При этом стоит учитывать, что для не-центральных и не-краевых рельс это расстояние не постоянно, чередуются два шага, названные "первым" и "вторым", которые применяются по очереди, в завимости от того, ближе мы сейчас следующему повороту забора или дальше.

Вспомогательная функция для прохода циклом по всем буквам используется в кодировщике и в декодировщике.
Чередование между шагами реализовано максимально наивно через флаг (можно лучше, например брать остаток от деления на 2 в качестве индекса в наборе из 2 шагов).

При этом кодировщик заполняет строку-результат значениями из исходной строки в соответствии с индексами "на заборе", а декодировщик - заполняет предвыделенный буфер (благо размеры строк на входе и выходе одинаковы) буквами из данной строки в соответствии с индексами "на заборе".

#### Задача простовата для 3 kyu      

## Evaluate mathematical expressions
                    
Задача классическая, требует написания несложного калькулятора математических выражений с поддержкой одного вида скобок и унарных операций.
Все операции определены как произвольные действия, имеющие доступ к стеку.
Само вычисление происходит не для инфиксной записи, а для обратной польской записи, преобразование к которой выполнено [алгоритмом сортировочной станции](https://ru.wikipedia.org/wiki/Алгоритм_сортировочной_станции) Дейкстры.

Единственная сложность - пришлось городить логику для считывания чисел из нескольких цифр, необходимо запоминать их и добавлять к концу результата, а потом преобразовывать все строки из цифр в нормальные числа.

#### Задача простовата для 2 kyu, думаю лучше подошло бы 3/4 kyu

## Break the pieces
Страшная задача, долго не мог подступиться.
В один момент пришло озарение и идея - выделить все области при помощи поиска в ширину и потом просто отрисоваь их, не забыв обрезать в пустых местах.

Но мне на момент решения задачи было дико лень писать всё это, поэтому задача решалась при помощи метода "попробуй заставить ChatGPT сделать то, что тебе нужно".
Спустя некоторое время, когда получилось раз двадцать обьяснить Великому ИИ, что он делает не так, результат был получен.
Дальше осталось допилить напильником кривые места и добавить стрёмные эвристики (строки 107-111) для определения внутренних и внешних углов.

Но оно того стоило! Классная задача на подумать и подебажить.

#### Хорошая задача для 2 kyu