#                                          ТЕСТУВАННЯ 2: ДЕБАГЕР
Всі команди дебагера прописані одразу при запуску програми. Команда складається з двох частин: <власне команда> та <аргументи> (якщо вони присутні).

Також, ми прописали автоматичну перевірку роботи дебагера, де прописані тести майже для кожного зі сценаріїв, що пролписані тут.

## Тест-кейси
Будемо йти поступово, перевіряючи роботу кожних команд



***ВАЖЛИВІ ПРИМІМТКИ!!*** 

1.1) Для того, щоб запускати автоматичні тести (опція2), розписані в файлі test_debugger.py, бажано використовувати команду `python -m unittest test_debugger.py` з папки **xvm**. Якщо хочемо запустити через `pytest` варто зробити декілька важливих змін:
- В терміналі вийти з папки xvm на папку **task0**;
- Прописати `from run import xvm_debug`;
- В функції `test_exec_stack_command` в змінній `commands` написати `"load xvm/debug_program1.txt"`.

1.2) Наш дебагер адаптований до ситуації виникнення помилки під час виконання програми (необроблений exception), а саме: він не дозволяє завантаженому коду виконуватись далі після помилки, можна лише переглянути код (командою list) для розуміння де саме виникла помилка.


## Завантаження файлу (команда `load`)
Для тестування (не автоматичного) були створені два окремі файли debug_program1.txt (більш простий з сумою двох чисел) та debug_program2.txt (більш громіздкий, з викликами функцій). Тут буде розписано здебільшого для простої програми, якщо не вказано інше.

### Позитивні сценарії:
1) Прямий виклик файлу: 
```bash 
load debug_program1.txt
```
*Важливо!* Для такого запуску, потрібно в терміналі знаходитись в папці, де лежить цей файл - інакше робити як в п. 2 та 3

1.1) Перевірка завантаження усіх змінних для роботи:
```bash 
list   # Очікування: показує інструкції з файлу (переконатися, що це не порожній список).
stack  # Очікування: порожній (бо відбувається обнулення стану після load)
memory # Очікування: порожній (бо відбувається обнулення стану після load)
```
***Очікування***: ip = 0, поточна стрілка біля першої інструкції, бо щойно завантажили

2) Виклик файлу за відносним шляхом: 
```bash 
load ./debug_program1.txt
```

3) Виклик файлу за абсолютним шляхом: 
```bash 
load "C:\...\debug_program.1txt"     # for Windows
load /home/user/project/debug_program1.txt   # for Linux/Mac
```

4) Виклик файлу за шляхом з пробілами, лапками: 
```bash 
load "test data/debug_program1.txt"
```

***Очікування***: `File load succesfully`


### Негативні сценарії:
 1)  Виклик неіснуючого файлу: 
```bash 
load not_exists.txt
```
***Очікування***: `File not found`

 2)  Виклик директорії замість файлу: 
```bash 
load task0
```
***Очікування***: `File not found`

 3)  Виклик порожнього файлу: 
 Можна видалити з файлу debug_program1 інструкції і перевірити чи не вилітає віртуальнa машинa
```bash 
load debug_program1.txt
```
***Очікування***: `File load succesfully` та при виконанні команди `list` віртуальнa машинa не "падає"

4) Виклик файлу з неправильним кодуванням:
Можна вставити наступний код (це кодування наших інструкцій у формат base64 на основі KOI8-R) в файл debug_program1.txt
```bash 
,ЮЭ#█I>RLДDЩPдЁ─П▌5$Уя$нDOу│D@
<Б
LЁ─У@Gн�?у─4⌠9?Tl╨bн�?у.≤ТH5
```

```bash 
load debug_program1.txt
```

***Очікування***: `Failed to parse: Invalid OpCode input: ...` та віртуальнa машинa не падає.

5) Виклик файлу з синтаксичною помилкою:
Можна вставити у файл debug_program1.txt команду `LOAD_CONST 5`
```bash 
load debug_program1.txt
```
***Очікування***: `Failed to parse: Invalid OpCode input: ...` та віртуальнa машинa не "падає".

6) Виклик команди без аргумента:
```bash 
load 
```

***Очікування***: `File  not found`


### Поведінкові сценарії:

1) Перезавантаження файлів поверх існуючого:
Приклад послідовності виклику команд:
```bash 
load debug_program1.txt
exec LOAD_CONST 123
exec STORE_VAR a
memory           # a = 123
load debug_program.txt
memory           # Очікування: має бути порожньо, бо обнулення після завантаження
stack            # Очікування: має бути порожньо, бо обнулення після завантаження
list             # Очікування: ip вказує на першу інструкцію
```

2) Сумісність із подальшими командами:
Приклад послідовності виклику команд:
```bash 
load debug_program1.txt
list
step
next
run
```
***Очікування***: 
- Жодних трейсбеків/крешів від несумісності структури “завантаженого коду” з тим, що очікують list/step/next/run.
- Якщо є команда BREAKPOINT — коректна зупинка та вивід повідомлення.



## Перегляд інструкцій файлу (команда `list`)
Завдання передбачало за командою list - перегляд до 5 команд до і до 5 команд після нинішньої інструкції
### Позитивні сценарії:
1) Звичайний виклик команди (після завантаження файлу):
```bash 
load debug_program1.txt
list
```
***Очікування***: Вивід до 5 перших команд з файлу з стрілкою на першу команду
Для файла debug_program1.txt це буде:
```bash 
-> 0000: Op(OpCode.LOAD_CONST, 5)
   0001: Op(OpCode.STORE_VAR, 'x')
   0002: Op(OpCode.LOAD_CONST, 10)
   0003: Op(OpCode.STORE_VAR, 'y')
   0004: Op(OpCode.BREAKPOINT, )
   0005: Op(OpCode.BREAKPOINT, )
```

2) Виклик команди з аргументами
```bash 
list 23пк
```
***Очікування***: аргументи ігноруються та при завантаженні коректного файлу виводяться до 5 перших команд (див. попереднй пункт)


### Негативні сценарії:
1) Просто виклик команди (без завантаження файлу):
```bash 
list
```
***Очікування***: `No program loaded. Use: load <path>`

2) Виклик команди з пустим завантаженим файлом:
```bash 
load debug_program1.txt       # (зроблений за аналогією п.3 негативних сценаріїв для load)
list
```
***Очікування***: `No program loaded. Use: load <path>` та продовження роботи віртуальної машини

3) Виклик команди з завантаженим файлом у неправильному кодуванні:
```bash 
load debug_program1.txt       # (зроблений за аналогією п.4 негативних сценаріїв для load)
list
```
***Очікування***: `No program loaded. Use: load <path>` та продовження роботи віртуальної машини

3) Виклик команди з завантаженим файлом з синтаксичною помилкою:
```bash 
load debug_program1.txt       # (зроблений за аналогією п.5 негативних сценаріїв для load)
list
```
***Очікування***: `No program loaded. Use: load <path>` та продовження роботи віртуальної машини



### Поведінкові сценарії:
1) Працюючи з командою `step` / `next` має змінюватись ip і відповідно кількість виведених інструкцій буде змінюватись.

Приклад результату викликів команд у терміналі:
```bash 
xvm > load debug_program1.txt
File loaded succesfully
xvm > list
-> 0000: Op(OpCode.LOAD_CONST, 5)
   0001: Op(OpCode.STORE_VAR, 'x')
   0002: Op(OpCode.LOAD_CONST, 10)
   0003: Op(OpCode.STORE_VAR, 'y')
   0004: Op(OpCode.BREAKPOINT, )
   0005: Op(OpCode.BREAKPOINT, )
xvm > step
0000: Op(OpCode.LOAD_CONST, 5)
xvm > list
   0000: Op(OpCode.LOAD_CONST, 5)
-> 0001: Op(OpCode.STORE_VAR, 'x')
   0002: Op(OpCode.LOAD_CONST, 10)
   0003: Op(OpCode.STORE_VAR, 'y')
   0004: Op(OpCode.BREAKPOINT, )
   0005: Op(OpCode.BREAKPOINT, )
   0006: Op(OpCode.LOAD_VAR, 'x')
xvm > step
0001: Op(OpCode.STORE_VAR, 'x')
xvm > step
0002: Op(OpCode.LOAD_CONST, 10)
xvm > next
0003: Op(OpCode.STORE_VAR, 'y')
xvm > list
   0000: Op(OpCode.LOAD_CONST, 5)
   0001: Op(OpCode.STORE_VAR, 'x')
   0002: Op(OpCode.LOAD_CONST, 10)
   0003: Op(OpCode.STORE_VAR, 'y')
-> 0004: Op(OpCode.BREAKPOINT, )
   0005: Op(OpCode.BREAKPOINT, )
   0006: Op(OpCode.LOAD_VAR, 'x')
   0007: Op(OpCode.LOAD_VAR, 'y')
   0008: Op(OpCode.ADD, )
   0009: Op(OpCode.STORE_VAR, 'sum')
   0010: Op(OpCode.LOAD_VAR, 'sum')
xvm >
```

***Очікування***: 
- До та після поточної команди вказано до 5 інструкцій.
- Стрілка вказує на поточну інструкцію для виконання
- Не висвічується "сміття" у випадках, якщо інструкцій для виведення менше ніж 5


### Додатково 
Перевірити чи кожен рядок має формат `<marker> <index:04d>: <repr(op)>`, де 
- `marker` - `->` для поточного ip, інакше два пробіли;
- `index`: 4-значний з лідируючими нулями (0000, 0001, …);
- `repr(op)`: щось на кшталт `Op(opcode=..., args=[...])`.

Поганий результат: `<bad op>`




## Проходження коду до кінця/помилки (команда run)
За завданням команда має виконати або увесь завантажений код до кінця, або припинити виконання на інструкції BREAKPOINT або при досяганні реальної помилки в самому коді.

### Позитивні сценарії
1) Команда виконає завантажений код?, записаний у файлі debug_program2.txt (більш громіздкий код без інструкцій   `BREAKPOINT`) до кінця 
```bash 
load debug_program2.txt
run
```

***Очікування***: 
- Дебагер має виконати всі інструкції послідовно та після завершення програми має вивести повідомлення про кінець програми. 
- Стан пам'яті має відображати результат усіх обчислень.


2) Команда зупиниться при потраплянні на інструкцію `BREAKPOINT` 
```bash 
load debug_program1.txt
run
```

***Очікування***: 
- Номер інструкції, на якій зупинилось виконання програми: 
```bash 
Stopped at instruction 5 (BREAKPOINT)
```
- При виведенні пам'яті (команда memory) будуть лише два значення x i y, адже sum ще не повинна існувати, адже вона обчислюється після брейкпоінту:
```bash 
xvm > memory
Frame $entrypoint$ variables

  x = 5
  y = 10

```


3) Виклик команди з аргументами
```bash 
run 23пк
```
***Очікування***: аргументи ігноруються та при завантаженні коректного файлу програма виконується до кінця або до помилки (в т.ч. інструкції `BREAKPOINT`) (див. попередні пункти)



### Негативні сценарії
1) Виклик команди без завантаженого файлу:
```bash 
XVM Debugger. Type 'info' or 'exit'.
xvm > run
```
***Очікування***: `End of program reached.` та продовження роботи віртуальної машини



2) Виконання програми при досягненні помилки
Наприклад, використання неіснуючої зміннної.
Можемо поставити третьою інструкцію `LOAD_VAR "z"` в debug_program1.txt
```bash 
load debug_program1.txt
run
```

***Очікування***: Дебагер має перехопити помилку від віртуальної машини, повідомити про неї користувачеві `Runtime error: Variable 'z' not defined.` та зупинити виконання на проблемній інструкції. Віртуальна машина не має "вилетіти".



### Поведінкові сценарії
1) Продовження виконання з поточної позиції (з місця, де зупинився вказівник), а не з нуля
```bash 
XVM Debugger. Type 'info' or 'exit'.
xvm > load debug_program1.txt
File loaded succesfully
xvm > list
-> 0000: Op(OpCode.LOAD_CONST, 100)
   0001: Op(OpCode.LOAD_CONST, 5)
   0002: Op(OpCode.STORE_VAR, 'x')
   0003: Op(OpCode.LOAD_CONST, 10)
   0004: Op(OpCode.STORE_VAR, 'y')
   0005: Op(OpCode.BREAKPOINT, )
xvm > step
0000: Op(OpCode.LOAD_CONST, 100)
xvm > step
0001: Op(OpCode.LOAD_CONST, 5)
xvm > step
0002: Op(OpCode.STORE_VAR, 'x')
xvm > step
0003: Op(OpCode.LOAD_CONST, 10)
xvm > list
   0000: Op(OpCode.LOAD_CONST, 100)
   0001: Op(OpCode.LOAD_CONST, 5)
   0002: Op(OpCode.STORE_VAR, 'x')
   0003: Op(OpCode.LOAD_CONST, 10)
-> 0004: Op(OpCode.STORE_VAR, 'y')
   0005: Op(OpCode.BREAKPOINT, )
   0006: Op(OpCode.BREAKPOINT, )
   0007: Op(OpCode.LOAD_VAR, 'x')
   0008: Op(OpCode.LOAD_VAR, 'y')
   0009: Op(OpCode.ADD, )
xvm > run
Stopped at instruction 5 (BREAKPOINT)
xvm > step
0006: Op(OpCode.BREAKPOINT, )  # BREAKPOINT consumed
xvm > step
0007: Op(OpCode.LOAD_VAR, 'x')
xvm > run
15
```

***Очікування***: після "проходження" інструкції `BREAKPOINT` за допомогою команди `step`, команда `run` продовжила з 7 інструкції і дійшла до кінця виконання та вивела результат додавання 15



## Покрокове проходження коду (команда `step`)
Ця команда має проходитись поступово по кожному рядочку нашого коду, виконати одну поточну інструкцію та перемістити вказівник (`ip`) на наступну. Це основний інструмент для детального, покрокового аналізу програми. Команда не приймає аргументів.

### Позитивні сценарії
1) Перший крок після завантаження програми
```bash 
load debug_program1.txt
step
```

***Очікування***: дебагер має виконати першу інструкцію (0000), вивести її в консоль, і перемістити вказівник на наступну (0001).

```bash 
xvm > list
   0000: Op(OpCode.LOAD_CONST, 100)
-> 0001: Op(OpCode.LOAD_CONST, 5)
   0002: Op(OpCode.STORE_VAR, 'x')
   0003: Op(OpCode.LOAD_CONST, 10)
   0004: Op(OpCode.STORE_VAR, 'y')
   0005: Op(OpCode.BREAKPOINT, )
   0006: Op(OpCode.BREAKPOINT, )
```


2) Послідовне виконання кількох кроків: Кожен виклик `step` має послідовно виконувати інструкції та змінювати стан віртуальної машини (ту ж пам'ять).
```bash 
load debug_program1.txt
step  # Команда LOAD_CONST 5
step  # Команда STORE_VAR 'x'
memory
```

***Очікування***: Після двох кроків змінна `x` повинна з'явитися в пам'яті зі значенням 5.
```bash 
xvm > memory
Frame $entrypoint$ variables

  x = 5

```

3) Виклик команди з аргументами
```bash 
step 23пк
```
***Очікування***: аргументи ігноруються та при завантаженні коректного файлу все працює належним чином (див. попередні пункти)


### Негативні сценарії
1) Виклик команди без завантаженого файлу:
```bash 
xvm > step
```
***Очікування***: Фраза `No program loaded. Use: load <path>` та продовження роботи дебагера.


2) Виклик команди на останній інструкції програми:
```bash 
# вище - виконання всіх інструкцій
step
```

***Очікування***: Дебагер має повідомити, що програма завершена - `End of program reached.` і немає чого виконувати.


3) Перехід на інструкцію, що викликає помилку:
Для тестування нам потрібно знову додати третьою інструкцією в debug_program1.txt - `LOAD_VAR "z"`
```bash 
# вище - виконання всіх інструкцій
step
```

***Очікування***: дебагер має перехопити помилку, вивести повідомлення про неї, але не переміщувати вказівник інструкції. 
- Також варто врахувати примітку 1.2, яка наголошує, що після досягнення помилки / екзепшена програма далі виконуватись не буде. Можна лише запустити команду list, щоб побачити в якому моменті знаходиться інструкція з помилкою. 
```bash 
xvm > step
0001: Op(OpCode.LOAD_VAR, 'z')
Runtime error at instruction 1: Op(OpCode.LOAD_VAR, 'z')
Error: Variable 'z' not defined.
xvm > step
XVM has crashed, instruction execution is forbidden. Please reload your program file.
xvm > list
   0000: Op(OpCode.LOAD_CONST, 100)
-> 0001: Op(OpCode.LOAD_VAR, 'z')
   0002: Op(OpCode.LOAD_CONST, 5)
   0003: Op(OpCode.STORE_VAR, 'x')
   0004: Op(OpCode.LOAD_CONST, 10)
   0005: Op(OpCode.STORE_VAR, 'y')
   0006: Op(OpCode.BREAKPOINT, )
xvm >
```


### Поведінкові сценарії
1) Вхід у функцію:
`step` — це інструмент для глибокого аналізу. На відміну від `next`, коли `step` виконує інструкцію `CALL`, він має "зайти" всередину функції, а не виконати усі команди функції і вийти з результатом.
```bash 
XVM Debugger. Type 'info' or 'exit'.
xvm > load debug_program2.txt
File loaded succesfully
xvm > step
0000: Op(OpCode.INPUT_NUMBER, )
Input for INPUT_NUMBER (one arg):
12
xvm > step
0001: Op(OpCode.STORE_VAR, 'x')
xvm > 2
Unknown command: 2. Type 'info'.
xvm > step
0002: Op(OpCode.INPUT_NUMBER, )
Input for INPUT_NUMBER (one arg):
2
xvm > step
0003: Op(OpCode.STORE_VAR, 'n')
xvm > step
0004: Op(OpCode.LOAD_VAR, 'n')
xvm > next
0005: Op(OpCode.LOAD_VAR, 'x')
xvm > step
0006: Op(OpCode.LOAD_CONST, 'pow')
xvm > step
0007: Op(OpCode.CALL, )
xvm > step
0000: Op(OpCode.STORE_VAR, 'x')
xvm > step
0001: Op(OpCode.STORE_VAR, 'n')
xvm > list
   0000: Op(OpCode.STORE_VAR, 'x')
   0001: Op(OpCode.STORE_VAR, 'n')
-> 0002: Op(OpCode.LOAD_CONST, 0)
   0003: Op(OpCode.LOAD_VAR, 'n')
   0004: Op(OpCode.EQ, )
   0005: Op(OpCode.CJMP, 'Power 0')
   0006: Op(OpCode.LOAD_CONST, 2)
   0007: Op(OpCode.LOAD_VAR, 'n')
xvm > 
```

***Очікування***: після виконання команди `CALL` за допомогою `step`, вказівник (`ip`) має переміститися на першу інструкцію всередині викликаної функції, а поточний фрейм (`frame`) має змінитися на `pow`.
```bash 
xvm > frame
Active frame: pow
  x = 12
  n = 2
xvm >
```

2) Вихід з функції:
Коли `step` виконує останню інструкцію у функції (`RET`), він має повернути виконання до основної програми.
```bash 
xvm > step
0032: Op(OpCode.RET, )
xvm > step
0037: Op(OpCode.STORE_VAR, 'xn')
xvm > list
   0033: Op(OpCode.LOAD_VAR, 'd')
   0034: Op(OpCode.LOAD_VAR, 'x')
   0035: Op(OpCode.LOAD_CONST, 'pow')
   0036: Op(OpCode.CALL, )
   0037: Op(OpCode.STORE_VAR, 'xn')
-> 0038: Op(OpCode.LOAD_VAR, 'xn')
   0039: Op(OpCode.LOAD_VAR, 'xn')
   0040: Op(OpCode.MUL, )
   0041: Op(OpCode.RET, )
   0042: Op(OpCode.LOAD_CONST, "This func can't take power of 0.")
   0043: Op(OpCode.RET, )
```

***Очікування***: Після виконання `RET`, вказівник (`ip`) має повернутися на інструкцію, що йде одразу після вихідної інструкції `CALL`.
```bash
xvm > list
   0033: Op(OpCode.LOAD_VAR, 'd')
   0034: Op(OpCode.LOAD_VAR, 'x')
   0035: Op(OpCode.LOAD_CONST, 'pow')
   0036: Op(OpCode.CALL, )
   0037: Op(OpCode.STORE_VAR, 'xn')
-> 0038: Op(OpCode.LOAD_VAR, 'xn')
   0039: Op(OpCode.LOAD_VAR, 'xn')
   0040: Op(OpCode.MUL, )
   0041: Op(OpCode.RET, )
   0042: Op(OpCode.LOAD_CONST, "This func can't take power of 0.")
   0043: Op(OpCode.RET, )
xvm >
```



## Команда для перестрибування через функції (команда `next`)
Завдання команди `next` — виконати одну поточну інструкцію. Її ключова відмінність від `step` полягає в обробці інструкції `CALL`: next виконує всю викликану функцію за один крок ("перестрибує" через неї), зупиняючись на наступній інструкції після `CALL`. На всіх інших інструкціях `next` працює ідентично до `step`. Команда не приймає аргументів.

### Позитивні сценарії
1) Використання на простій інструкції (не `CALL`):
на будь-якій інструкції, крім `CALL`, next має поводитися точно так само, як step.
```bash
load debug_program1.txt
next
```

***Очікування***: Дебагер виконає першу інструкцію (0000), виведе її в консоль, і перемістить вказівник на наступну (0001). Результат ідентичний до `step`.
```bash
   0000: Op(OpCode.LOAD_CONST, 100)
-> 0001: Op(OpCode.LOAD_CONST, 5)
   0002: Op(OpCode.STORE_VAR, 'x')
   0003: Op(OpCode.LOAD_CONST, 10)
   0004: Op(OpCode.STORE_VAR, 'y')
   0005: Op(OpCode.BREAKPOINT, )
   0006: Op(OpCode.BREAKPOINT, )
xvm >
```


2) "Перестрибування" через виклик функції (`CALL`): Це головна перевірка для `next`. Коли вказівник стоїть на інструкції `CALL`, `next` має виконати всю функцію за лаштунками і зупинитися на наступному рядку.
```bash
load debug_program2.txt
# ... робимо кроки до інструкції CALL ...
next
```

***Очікування***: дебагер виконає інструкцію `CALL` та весь код всередині викликаної функції. Вказівник `->` зупиниться на інструкції, що йде одразу після `CALL`. При цьому стан пам'яті має змінитися згідно з тим, що зробила функція (наприклад, з'явиться нова змінна):
```bash
xvm > step
0007: Op(OpCode.CALL, )
xvm > list
-> 0000: Op(OpCode.STORE_VAR, 'x')
   0001: Op(OpCode.STORE_VAR, 'n')
   0002: Op(OpCode.LOAD_CONST, 0)
   0003: Op(OpCode.LOAD_VAR, 'n')
   0004: Op(OpCode.EQ, )
   0005: Op(OpCode.CJMP, 'Power 0')
xvm > next
0000: Op(OpCode.STORE_VAR, 'x')
xvm > list
   0000: Op(OpCode.STORE_VAR, 'x')
-> 0001: Op(OpCode.STORE_VAR, 'n')
   0002: Op(OpCode.LOAD_CONST, 0)
   0003: Op(OpCode.LOAD_VAR, 'n')
   0004: Op(OpCode.EQ, )
   0005: Op(OpCode.CJMP, 'Power 0')
   0006: Op(OpCode.LOAD_CONST, 2)
xvm >
```

3) Виклик команди з аргументами
```bash 
next 23пк
```
***Очікування***: аргументи ігноруються та при завантаженні коректного файлу все працює належним чином (див. попередні пункти)


### Негативні сценарії
1) Виклик команди без завантаженого файлу:
```bash 
next
```

***Очікування***: дебагер має повідомити, що жодна програма не завантажена (`No program loaded. Use: load <path>`), і не повинен "впасти".

2) Виклик команди в кінці програми
```bash 
# (після виконання всіх інструкцій)
next
```

***Очікування***: дебагер має повідомити, що програма завершена (`IP at end; nothing to execute.`) і немає чого виконувати.


3) Помилка в самій функцій, через яку ми перестрибуємо:

Якщо функція, яку `next` виконує "за лаштунками", містить помилку (наприклад, `LOAD_VAR` неіснуючої змінної)
```bash 
load program_with_failing_function.txt
# ... підводимо ip до CALL ...
next
```

***Очікування***: `next` має перервати виконання, повідомити про помилку ( наприклад `Runtime error: Variable 'z' not defined.`), що сталася всередині функції, і зупинити дебагер. Вказівник `ip` має залишитись на інструкції `CALL`, яка спричинила проблему.



### Поведінкові сценарії
1) Виконання інструкцій переходу (`JMP`, `CJMP`): 
на інструкціях, що змінюють потік виконання, next має поводитися так само, як `step`, тобто виконувати перехід
```bash 
# ... ip стоїть на інструкції JMP end_label ...
next
```

***Очікування***: Вказівник `->` переміститься на інструкцію, що йде після мітки `end_label`, пропустивши проміжний код.




## Команда `exec`
Завдання команди `exec` — виконати одну інструкцію "на льоту", не рухаючи основний вказівник програми (`ip`): можна покласти щось на стек, змінити змінну або виконати обчислення. 

**Важливо**: команда exec не має і не буде виконуватись без завантаження файлу 

## Позитивні сценарії
1) Виконання простої інструкції з аргументом:
```bash 
load debug_program1.txt
exec LOAD_CONST 123
stack
```

***Очікування***: iнструкція має виконатися, і число 123 з'явиться на вершині стеку. Команда `stack` повинна це підтвердити.
```bash 
xvm > exec LOAD_CONST 123
Executing: Op(OpCode.LOAD_CONST, 123)
xvm > stack
Stack (top is [0]):
[0] 123
xvm >
```


2) Виконання інструкції, що змінює пам'ять:
```bash 
exec LOAD_CONST 55
exec STORE_VAR "my_var"
memory
```

***Очікування***: після виконання двох команд у пам'яті дебагера має з'явитися змінна `my_var` зі значенням 55.
```bash 
xvm > memory
Frame $entrypoint$ variables

  "my_var" = 55


xvm >
```


3) Виконання обчислювальної інструкції (без аргументів):
```bash 
exec LOAD_CONST 10
exec LOAD_CONST 20
exec ADD
stack
```

***Очікування***: Команда `ADD` має взяти два числа зі стеку (10 і 20), додати їх і покласти результат (30) назад на стек.
```bash 
xvm > stack
Stack (top is [0]):
[0] 30
[1] 123
xvm >
```



### Негативні сценарії:
1) Виклик команди exec без аргументів:
```bash 
exec 
```

***Очікування***: дебагер має вивести інструкцію з правильного використання команди: `Usage: exec <OPCODE> <arg1, arg2, ..., argN>`


2) Виконання неіснуючого методу:
```bash 
exec JUMP_AROUND
```

***Очікування***: дебагер повинен повідомити, що такий опкод невідомий (`Unknown opcode: JUMP_AROUND`), і не має "падати"


3) Виконання інструкції з неправильною кількістю аргументів:
```bash 
exec LOAD_CONST
```

***Очікування***: дебагер має перехопити помилку від віртуальної машини та повідомити, що інструкція вимагає аргумент: `VM error: LOAD_CONST takes one argument. Got: ()`


4) Виконання інструкції, що спричиняє помилку в VM: 
Якщо стек порожній, спроба виконати `ADD` має спричинити помилку
```bash 
# (стек порожній)
exec ADD
```

***Очікування***: дебагер має коректно обробити помилку часу виконання (`runtime error`) від віртуальної машини (наприклад, спробу взяти елемент з порожнього стеку) і повідомити про неї: `VM error: pop from empty list`



### Поведінкові сценарії
1) `exec` не впливає на вказівник інструкції (`ip`): 

Це ключова перевірка. Команда exec виконується "окремо" від основної програми і не повинна змінювати її потік виконання. 

Приклад сесії:
```bash 
xvm > load debug_program1.txt 
File loaded succesfully
xvm > exec ADD
Executing: Op(OpCode.ADD, )
VM error: pop from empty list
xvm > list
-> 0000: Op(OpCode.LOAD_CONST, 100)
   0001: Op(OpCode.LOAD_CONST, 5)
   0002: Op(OpCode.STORE_VAR, 'x')
   0003: Op(OpCode.LOAD_CONST, 10)
   0004: Op(OpCode.STORE_VAR, 'y')
   0005: Op(OpCode.BREAKPOINT, )
xvm > exec LOAD_CONST 999
Executing: Op(OpCode.LOAD_CONST, 999)
xvm > list
-> 0000: Op(OpCode.LOAD_CONST, 100)
   0001: Op(OpCode.LOAD_CONST, 5)
   0002: Op(OpCode.STORE_VAR, 'x')
   0003: Op(OpCode.LOAD_CONST, 10)
   0004: Op(OpCode.STORE_VAR, 'y')
   0005: Op(OpCode.BREAKPOINT, )
xvm >
```

***Очікування***: після виконання будь-якої команди `exec` вказівник `->` має залишатися на тій самій інструкції, де він був до цього. Це доводить, що `exec` не є аналогом `step`


4) Виконання з аргументом-рядком, що містить пробіли:
```bash 
exec LOAD_CONST "hello beautiful world"
stack
```

***Очікування***: парсер команди `exec` має коректно обробити рядок у лапках як один цілісний аргумент. На стеку має з'явитися рядок "hello beautiful world":
`VM error: LOAD_CONST takes one argument. Got: ('"hello', 'beautiful', 'world"')`.

