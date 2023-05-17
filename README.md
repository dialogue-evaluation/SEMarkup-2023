# SEMarkup-2023

[Русский](README_RU.md)

A shared task devoted to the automatic semantic markup.

<a href="https://creativecommons.org/licenses/by-nc/4.0/"><img src="https://img.shields.io/static/v1?label=license&message=CC-BY-NC-4.0&color=green"/></a>

## Overview
The shared task contains 2 tracks:
- base ([Codalab](https://codalab.lisn.upsaclay.fr/competitions/10472)): create a solution that would produce a **semantic markup** with a dependency head (using the morphosyntactic markup, if possible).
- hard ([Codalab](https://codalab.lisn.upsaclay.fr/competitions/10471)): create a solution that would produce a **simultaneous morpho-, syntactic and semantic markup**.

Both tracks imply, among other things, the solution of the All-words WSD problem - disambiguation for all polysemous words (homonyms), as participants have to assign semantic classes to all words. <br />
The presence of morphosyntactic markup in the training dataset makes it possible to take these data into account and, in addition, to find out the connection between different levels of markup.

## Citing
Please refer to this paper if you use our dataset
```
@inproceedings{Petrova2023,
  year = {2023},
  author = {Maria Petrova, Alexandra Ivoylova, Ilya Bayuk, Darya Dyachkova, Mariia Michurina},
  title = {The ICA Project: the Creation and Application of the full Morpho-Syntactic and Semantic Markup Standard},
  booktitle = {Computational Linguistics and Intellectual Technologies}
}
```

## Markup example

Let us look at the markup using this example sentence:
> Еду готовили на костре. (The food was cooked on a fire.)

The markup of the base track consists of 3 types of tags: dependency heads, semantic slots and semantic classes.

1) Dependency heads: words in a sentence are related. Basically, one word is a dependent, and the other is its head, i.e. manages it in some way. This dependency is both semantic and syntactic. Thus, the token *еду (food)* depends on the token *готовили (was cooked)*.
2) Semantic slots (Глубинные позиции, ГП) - semantic roles that specific words occupy in a sentence. In the example sentence *еда (food)* is the `(Object)` of cooking, and *костер (fire)* is the place where cooking was located (`(Locative)`).
3) Semantic classes (семантические классы, СК) are semantic categories, particular interpretations of words. I.e., *еда (food)* would have a semantic class `FOOD`, as well as *готовить (was cooked)* `TO_PREPARE_FOOD_SUBSTANCE`.

The whole markup of this example for the BASE track sentence runs as follows:

```
# text = Еду готовили на костре.
1	Еду	_	_	_	_	2	_	Object	FOOD
2	готовили _	_	_	_	0	_	Predicate	TO_PREPARE_FOOD_SUBSTANCE
3	на	_	_	_	_	4	_	_	PREPOSITION
4	костре _	_	_	_	2	_	Locative	OBJECT_BY_FUNCTION_AND_PROPERTY
5	.	_	_	_	_	2	_	_	_
```

Here special attention should be paid to homonyms *еду (food)* and *готовили (was cooked)*. The token *еду*, apart from semantic tags `Object FOOD`, can be interpreted in a lexicon as `Predicate	TO_GO_AND_TRANSFER` (1 person sing. verb form of *ехать*), whereas *готовили* may also have tags `Predicate	READINESS`.


The markup of this example for the HARD track sentence runs as follows:

```
# text = Еду готовили на костре.
1	Еду	еда	NOUN	_	Animacy=Inan|Case=Acc|Gender=Fem|Number=Sing	2	obj	Object	FOOD	_
2	готовили	готовить	VERB	_	Aspect=Imp|Mood=Ind|Tense=Past|VerbForm=Fin|Voice=Act	0	root	Predicate	TO_PREPARE_FOOD_SUBSTANCE	_
3	на	на	ADP	_	_	4	case	_	PREPOSITION	_
4	костре	костёр	NOUN	_	Animacy=Inan|Case=Loc|Gender=Masc|Number=Sing	2	obl	Locative	OBJECT_BY_FUNCTION_AND_PROPERTY	_
5	.	.	PUNCT	_	_	2	punct	_	punct	_
```

Besides labelling dependency heads, semantic slots and classes, we suggest that the participants mark up lemmas, PoS tags, grammatical features and dependency relations according to UD (Universal Dependencies).

## Dataset

[Train dataset](train.conllu)

As the train dataset we suggest using the first open [corpus](https://github.com/compreno-semantics/compreno-corpus) for Russian which contains 3-level markup:

- Morphology (UD)
- Syntax (UD)
- Semantics (Simplified Compreno format)

We believe that simultaneous markup of these three language levels is a challenge even more complicated than [Dialogue GramEval-2020 competition](https://github.com/dialogue-evaluation/GramEval2020), where 2 language levels were introduced, morphology and syntax.
<br />
The details about the dataset and its creation can be read in the [corpus repository](https://github.com/compreno-semantics/compreno-corpus).

## Important links
- [Codalab BASE track](https://codalab.lisn.upsaclay.fr/competitions/10472)
- [Codalab HARD track](https://codalab.lisn.upsaclay.fr/competitions/10471)
- [Our telegram chat](https://t.me/+58wXWNPgUt8yZDgy)

## Tagsets and other useful information
- [Semantic Slots](tagsets/semantic_slots.xlsx) – a list of semantic slots with their unsimplified counterparts
- [Semantic Classes](tagsets/semantic_classes.csv) – a list of hyperonym semantic classes which were used in the simplified version of the format
- [UD Morphology tagset](https://github.com/dialogue-evaluation/GramEval2020/blob/master/UDtagset/UD-Russian_tagset.md) - UD morphological tagset: PoS-tags and grammatical features (the link is provided for the tagset published in GramEval-2020 competition) 
- [UD Dependency relations (syntax)](tagsets/syntax.md) - UD dependency relations
- [Full information about the dataset and its format](https://github.com/compreno-semantics)
- [Acknowledgements](acknowledgements.md) – project participants

## Conversion paper
Please refer to this paper if you use our conversion materials
```
@inproceedings{Petrova2023,
  year = {2023},
  author = {Alexandra Ivoylova, Darya Dyachkova, Maria Petrova, Mariia Michurina},
  title = {The problem of linguistic markup conversion: the transformation of the Compreno markup into the UD format},
  booktitle = {Computational Linguistics and Intellectual Technologies}
}
```

## Timeline:
- 20 January - train dataset is published;
- 6 February - test dataset and CodaLab is published;
- 28 March - shared task deadline, results publication;
- 1 April - paper submission deadline.

## Organizers
- Maria Petrova (A4 Foundation)
- Alexandra Ivoylova (RSUH)
- Ilya Bayuk (A4 Foundation)
- Darya Dyachkova (RSUH)
- Mariia Michurina (RSUH)
- Angela Shumilova (RSUH)
