# SEMarkup-2023 (Russian)

Соревнование по автоматической семантической разметке.

[Чат в телеграме](https://t.me/+58wXWNPgUt8yZDgy)

<a href="https://creativecommons.org/licenses/by-nc/4.0/"><img src="https://img.shields.io/static/v1?label=license&message=CC-BY-NC-4.0&color=green"/></a>

## Обзор

Соревнование содержит 2 дорожки:
- base ([Codalab](https://codalab.lisn.upsaclay.fr/competitions/10472)): создать решение, которое будет производить **семантическую разметку** с вершинами зависимостей (по возможности с использованием морфосинтаксической разметки).
- hard ([Codalab](https://codalab.lisn.upsaclay.fr/competitions/10471)): создать решение, которое будет производить **одновременно морфологическую, синтаксическую и семантическую** разметку.

Обе дорожки подразумевают в том числе решение задачи All-words WSD &ndash; разрешения омонимии для всех многозначных слов, так как участники должны приписать семантические классы всем словам.<br />
Наличие морфосинтаксической разметки в обучающем датасете позволит учитывать эти данные и в перспективе выяснить взаимосвязь разных уровней разметки.

## Цитирование
Ссылка на публикацию при использовании корпуса:
```
@inproceedings{Petrova2023,
  year = {2023},
  author = {Maria Petrova, Alexandra Ivoylova, Ilya Bayuk, Darya Dyachkova, Mariia Michurina},
  title = {The ICA Project: the Creation and Application of the full Morpho-Syntactic and Semantic Markup Standard},
  booktitle = {Computational Linguistics and Intellectual Technologies}
}
```

## Пример разметки

Разберем формат разметки base дорожки на примере предложения:
> Еду готовили на костре.

Разметка base дорожки состоит из 3-х типов тэгов: вершины зависимостей, глубинные позиции (ГП) и семантические классы (СК).
1) Вершины зависимостей: слова в предложении находятся в связи друг с другом, и как правило, одно слово является зависимым, а другое &ndash; его вершиной, т.е. каким-либо образом управляет им. Эта зависимость &ndash; синтаксическая и семантическая. Так, токен *еду* будет зависеть от токена *готовили*.
2) Глубинные позиции &ndash; это семантические роли, которые занимают конкретные слова в предложении, например, в нашем предложении *еда* &ndash; это объект готовки `(Object)`, а *костер* &ndash; место, где готовка происходила `(Locative)`.
3) Семантические классы &ndash; это смысловые категории, к которым относятся слова, конкретные толкования слов. Так, *еда* будет иметь сем. класс `FOOD`, а, например, *готовить* &ndash; `TO_PREPARE_FOOD_SUBSTANCE`.

Разметка на Base дорожке &ndash; это разметка этих трех видов тэгов:

```
# text = Еду готовили на костре.
@@ -31,9 +32,12 @@
4	костре _	_	_	_	2	_	Locative	OBJECT_BY_FUNCTION_AND_PROPERTY
5	.	_	_	_	_	2	_	_	_
```
Здесь трудность представляют токены-омонимы *еду* и *готовили*. Так, токен *еду*, кроме значения `Object FOOD`, может иметь значение `Predicate	TO_GO_AND_TRANSFER` (для глагола *ехать*), а токен готовили &ndash; `Predicate	READINESS`.

Разметка для Hard дорожки:

```
# text = Еду готовили на костре.
1	Еду	еда	NOUN	_	Animacy=Inan|Case=Acc|Gender=Fem|Number=Sing	2	obj	Object	FOOD	_
@@ -42,40 +46,49 @@
4	костре	костёр	NOUN	_	Animacy=Inan|Case=Loc|Gender=Masc|Number=Sing	2	obl	Locative	OBJECT_BY_FUNCTION_AND_PROPERTY	_
5	.	.	PUNCT	_	_	2	punct	_	punct	_
```
Помимо вершин зависимостей, ГП и СК, мы предлагаем участникам разметить леммы, части речи, грамматические категории (т.н. features) и синтаксические связи (по UD).

## Датасет

[Train dataset](train.conllu)

Для русского языка впервые создан и выложен в открытый доступ [корпус](https://github.com/compreno-semantics/compreno-corpus), который содержит разметку по 3 уровням языка:
- Морфология (UD)
- Синтаксис (UD)
- Семантика (Упрощенная разметка Compreno)

Мы считаем, что одновременная разметка сразу 3 уровней языка &ndash; это challenge для участников, еще более сложный, чем [соревнование GramEval-2020 (Диалог)](https://github.com/dialogue-evaluation/GramEval2020), где было 2 уровня языка &ndash; морфология и синтаксис.<br />
Подробную информацию о датасете можно прочесть в [его репозитории](https://github.com/compreno-semantics/compreno-corpus). 

## Важные ссылки

- [Codalab BASE track](https://codalab.lisn.upsaclay.fr/competitions/10472)
- [Codalab HARD track](https://codalab.lisn.upsaclay.fr/competitions/10471)

## Тагсеты и др. полезная информация

- [Semantic Slots](tagsets/semantic_slots.xlsx) – список используемых в разметке семантических отношений
- [Semantic Classes](tagsets/semantic_classes.csv) – список используемых в разметке семантических классов
- [UD Morphology tagset](https://github.com/dialogue-evaluation/GramEval2020/blob/master/UDtagset/UD-Russian_tagset.md) &ndash; Морфологический тагсет UD: части речи и грамматические категории (мы используем ссылку на тагсет, опубликованный на соревновании GramEval-2020)
- [UD Dependency relations (syntax)](tagsets/syntax.md) &ndash; синтаксические связи UD
- [Полное описание датасета и его формата]https://github.com/compreno-semantics
- [Acknowledgements](acknowledgements.md) – участники проекта

## Статья по корвертации
Ссылка на публикацию по конвертации корпуса:
```
@inproceedings{Ivoylova2023,
  year = {2023},
  author = {Alexandra Ivoylova, Darya Dyachkova, Maria Petrova, Mariia Michurina},
  title = {The problem of linguistic markup conversion: the transformation of the Compreno markup into the UD format},
  booktitle = {Computational Linguistics and Intellectual Technologies}
}
```

## График проведения соревнования:

- 20 января — публикация train и dev датасетов, тестовых данных;
- 31 января &ndash; публикация соревнования на CodaLab
- 20 марта — окончание соревнование, подведение результатов;
- 1 апреля — дедлайн для подачи статьи.

## Организаторы

- Мария Петрова (A4 Foundation)
- Александра Ивойлова (РГГУ)
- Илья Баюк (A4 Foundation)
- Мичурина Мария (РГГУ)
- Дарья Дьячкова (РГГУ)
- Анжела Шумилова (РГГУ)
